# EXPLAINER.md — Playto KYC Pipeline Technical Deep Dive

## 1. State Machine — Code & Explanation

**File:** `backend/kyc/services/state_machine.py`

### Design

The state machine is implemented as a single class `KYCStateMachine` with a static transition map:

```python
TRANSITIONS = {
    'draft': ['submitted'],
    'submitted': ['under_review'],
    'under_review': ['approved', 'rejected', 'more_info_requested'],
    'more_info_requested': ['submitted'],
}
```

### How It Works

1. **Transition map** — a dict where keys are current states and values are lists of valid next states.
2. **`transition(submission, new_status)`** — the ONLY way to change a submission's status:
   - Looks up `submission.status` in the transition map
   - Checks if `new_status` is in the allowed list
   - If not → raises `InvalidTransitionError` with a descriptive message
   - If yes → updates `status` and `updated_at`, saves, and returns the submission
3. **Terminal states** (`approved`, `rejected`) have no entries in TRANSITIONS, so any transition from them fails automatically.

### Why This Design?

- **Single source of truth** — no other file touches `submission.status` directly
- **Declarative** — the transition map is readable by non-engineers
- **Testable** — unit tests cover all 6 valid and 6 invalid transitions
- **No external dependencies** — pure Python, no state machine libraries needed

---

## 2. File Validation Logic

**File:** `backend/kyc/services/file_validator.py`

### Three Layers of Validation

```
Layer 1: Extension Check
  → Extract extension from filename
  → Compare against whitelist: {.pdf, .jpg, .jpeg, .png}
  → Reject immediately if not in whitelist

Layer 2: Size Check
  → Compare uploaded_file.size against MAX_FILE_SIZE (5MB = 5,242,880 bytes)
  → Reject if exceeds limit

Layer 3: MIME Type Sniffing (when python-magic is available)
  → Read first 2048 bytes of file content
  → Use libmagic to detect actual MIME type
  → Compare against whitelist: {application/pdf, image/jpeg, image/png}
  → Reset file pointer after reading
  → Graceful fallback if python-magic not installed
```

### Why MIME Sniffing?

Extension-only validation is trivially bypassable (rename `malware.exe` → `malware.pdf`). MIME sniffing reads the file's magic bytes to determine actual content type, preventing malicious uploads regardless of extension.

---

## 3. Queue Query Logic

**File:** `backend/kyc/services/queue_service.py`

### Queue Query

```python
KYCSubmission.objects.filter(status='submitted').order_by('updated_at')
```

- Filters to only `submitted` status (waiting for a reviewer to pick up)
- Orders by `updated_at` ascending → oldest first (FIFO)
- Uses `select_related('merchant')` to avoid N+1 queries

### Statistics Computation

```python
queue_count = queue.count()
avg_time = sum(now - sub.updated_at for sub in queue) / queue_count
approval_rate = approved_last_7d / total_resolved_last_7d * 100
```

- **Queue count** — simple COUNT query
- **Average time** — computed in Python (not SQL) since we iterate the queue anyway for SLA enrichment
- **Approval rate** — filters resolved submissions (approved + rejected) in last 7 days, computes percentage

---

## 4. Auth Enforcement Logic

### Architecture

```
Request → TokenAuthentication → Permission Class → View → Service
```

### Permission Classes (`backend/users/permissions.py`)

```python
class IsMerchant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'merchant'

class IsReviewer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'reviewer'
```

### Data Isolation (Merchant)

Merchant views filter queries to own data only:

```python
# In merchant views — ALWAYS filter by request.user
KYCSubmission.objects.filter(merchant=request.user)
```

A merchant can NEVER see or modify another merchant's submissions because:
1. List queries are filtered by `merchant=request.user`
2. Detail queries use `KYCSubmission.objects.get(id=id, merchant=user)` — returns 404 if not owned

### Reviewer Access

Reviewer views have no ownership filter — they can access ALL submissions:
```python
# In reviewer views — no merchant filter
KYCSubmission.objects.get(id=submission_id)
```

---

## 5. AI Bug Example & Fix

### The Bug: Race Condition in State Transitions

An AI code generator might produce this view code:

```python
# ❌ BUGGY CODE
@api_view(['POST'])
def approve_submission(request, submission_id):
    submission = KYCSubmission.objects.get(id=submission_id)

    # Bug: directly setting status without state machine validation
    submission.status = 'approved'
    submission.save()

    return Response({'status': 'approved'})
```

### Why This Is Wrong

1. **No state machine validation** — bypasses the transition map entirely
2. **Allows invalid transitions** — could approve a `draft` or `rejected` submission
3. **No atomicity** — between the `get()` and `save()`, another request could change the status
4. **No notification logging** — skips the notification service
5. **Business logic in views** — violates the service layer pattern

### The Fix

```python
# ✅ CORRECT CODE
@api_view(['POST'])
def approve_submission(request, submission_id):
    try:
        submission = KYCSubmission.objects.get(id=submission_id)
    except KYCSubmission.DoesNotExist:
        return Response({'error': 'Submission not found.'}, status=404)

    try:
        # State machine validates the transition
        KYCStateMachine.transition(submission, 'approved')
    except InvalidTransitionError as e:
        return Response({'error': str(e)}, status=400)

    # Log the event via notification service
    NotificationService.log_approval(submission)

    data = KYCSubmissionDetailSerializer(submission).data
    return Response(data)
```

### What The Fix Does

1. **State machine gate** — `KYCStateMachine.transition()` validates the transition is allowed before applying it
2. **Clear error handling** — `InvalidTransitionError` caught and returned as `{"error": "..."}` with HTTP 400
3. **Notification logging** — events are logged for audit trail
4. **Service layer pattern** — view is thin, business logic is in services
5. **Consistent error format** — all errors follow `{"error": "message"}` contract
