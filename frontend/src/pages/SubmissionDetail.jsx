import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { merchantAPI, reviewerAPI } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import SLAIndicator from '../components/SLAIndicator';

export default function SubmissionDetail({ reviewer = false }) {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [submission, setSubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState('');
  const [error, setError] = useState('');
  const [reason, setReason] = useState('');

  const isReviewer = reviewer || user?.role === 'reviewer';

  useEffect(() => { fetchSubmission(); }, [id]);

  const fetchSubmission = async () => {
    try {
      setLoading(true);
      const res = isReviewer ? await reviewerAPI.getSubmission(id) : await merchantAPI.getSubmission(id);
      setSubmission(res.data);
    } catch (err) { setError(err.response?.data?.error || 'Failed to load.'); }
    finally { setLoading(false); }
  };

  const handleAction = async (action) => {
    setActionLoading(action); setError('');
    try {
      switch (action) {
        case 'pick': await reviewerAPI.pickSubmission(id); break;
        case 'approve': await reviewerAPI.approveSubmission(id); break;
        case 'reject': await reviewerAPI.rejectSubmission(id, { reason }); break;
        case 'request-info': await reviewerAPI.requestInfo(id, { reason }); break;
        case 'resubmit': await merchantAPI.resubmitSubmission(id); break;
      }
      fetchSubmission();
      setReason('');
    } catch (err) { setError(err.response?.data?.error || 'Action failed.'); }
    finally { setActionLoading(''); }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="spinner w-8 h-8" /></div>;
  if (!submission) return <div className="max-w-4xl mx-auto px-4"><div className="glass-card p-8 text-center text-gray-400">Submission not found.</div></div>;

  const s = submission;

  return (
    <div className="max-w-4xl mx-auto px-4 animate-fade-in">
      <button onClick={() => navigate(-1)} className="text-sm text-gray-400 hover:text-white mb-4 flex items-center gap-1">← Back</button>

      {/* Header */}
      <div className="glass-card p-6 mb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-white">Submission #{s.id}</h1>
            <p className="text-gray-400 text-sm mt-1">by {s.merchant_info?.name || 'Unknown'} • {new Date(s.created_at).toLocaleDateString()}</p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={s.status} />
            <SLAIndicator atRisk={s.at_risk} timeInQueueHours={s.time_in_queue_hours} />
          </div>
        </div>
      </div>

      {error && <div className="mb-4 p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-sm animate-fade-in">{error}</div>}

      {/* Details */}
      <div className="grid md:grid-cols-2 gap-6 mb-6">
        <div className="glass-card p-6">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">Personal Details</h2>
          {s.personal_details && Object.entries(s.personal_details).map(([k,v])=>(
            <div key={k} className="flex justify-between py-2 border-b border-white/5 last:border-0">
              <span className="text-sm text-gray-500 capitalize">{k.replace(/_/g,' ')}</span>
              <span className="text-sm text-white">{v || '—'}</span>
            </div>
          ))}
        </div>
        <div className="glass-card p-6">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">Business Details</h2>
          {s.business_details && Object.entries(s.business_details).map(([k,v])=>(
            <div key={k} className="flex justify-between py-2 border-b border-white/5 last:border-0">
              <span className="text-sm text-gray-500 capitalize">{k.replace(/_/g,' ')}</span>
              <span className="text-sm text-white">{v || '—'}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Documents */}
      <div className="glass-card p-6 mb-6">
        <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">Documents ({s.documents?.length || 0})</h2>
        {(!s.documents || s.documents.length === 0) ? <p className="text-sm text-gray-500">No documents uploaded.</p> : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {s.documents.map(d=>(
              <div key={d.id} className="flex items-center gap-3 p-3 rounded-xl bg-white/5 border border-white/10">
                <span className="text-xl">{d.type==='PAN'?'🪪':d.type==='Aadhaar'?'🆔':'🏦'}</span>
                <div><p className="text-sm text-white font-medium">{d.type}</p><p className="text-xs text-gray-500">{new Date(d.uploaded_at).toLocaleString()}</p></div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Reviewer Actions */}
      {isReviewer && s.status === 'under_review' && (
        <div className="glass-card p-6 mb-6">
          <h2 className="text-sm font-medium text-gray-400 uppercase tracking-wider mb-4">Reviewer Actions</h2>
          <div className="mb-4">
            <label className="block text-sm text-gray-300 mb-1.5">Reason (for reject / request info)</label>
            <textarea value={reason} onChange={e=>setReason(e.target.value)} className="input-field h-24 resize-none" placeholder="Optional reason..." />
          </div>
          <div className="flex flex-wrap gap-3">
            <button onClick={()=>handleAction('approve')} disabled={!!actionLoading} className="btn-success flex items-center gap-2">
              {actionLoading==='approve'&&<div className="spinner"/>} ✓ Approve
            </button>
            <button onClick={()=>handleAction('reject')} disabled={!!actionLoading} className="btn-danger flex items-center gap-2">
              {actionLoading==='reject'&&<div className="spinner"/>} ✗ Reject
            </button>
            <button onClick={()=>handleAction('request-info')} disabled={!!actionLoading} className="btn-warning flex items-center gap-2">
              {actionLoading==='request-info'&&<div className="spinner"/>} ⓘ Request Info
            </button>
          </div>
        </div>
      )}

      {isReviewer && s.status === 'submitted' && (
        <div className="glass-card p-6 mb-6">
          <button onClick={()=>handleAction('pick')} disabled={!!actionLoading} className="btn-primary flex items-center gap-2">
            {actionLoading==='pick'&&<div className="spinner"/>} Pick Up for Review
          </button>
        </div>
      )}

      {/* Merchant resubmit */}
      {!isReviewer && s.status === 'more_info_requested' && (
        <div className="glass-card p-6 mb-6">
          <p className="text-sm text-orange-300 mb-4">More information has been requested. Update your submission and resubmit.</p>
          <div className="flex gap-3">
            <button onClick={()=>navigate(`/kyc/${s.id}/edit`)} className="btn-secondary">Edit Submission</button>
            <button onClick={()=>handleAction('resubmit')} disabled={!!actionLoading} className="btn-primary flex items-center gap-2">
              {actionLoading==='resubmit'&&<div className="spinner"/>} Resubmit
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
