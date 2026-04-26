const STATUS_CONFIG = {
  draft: { label: 'Draft', className: 'status-draft' },
  submitted: { label: 'Submitted', className: 'status-submitted' },
  under_review: { label: 'Under Review', className: 'status-under_review' },
  approved: { label: 'Approved', className: 'status-approved' },
  rejected: { label: 'Rejected', className: 'status-rejected' },
  more_info_requested: { label: 'More Info Requested', className: 'status-more_info_requested' },
};

export default function StatusBadge({ status }) {
  const config = STATUS_CONFIG[status] || { label: status, className: 'status-draft' };

  return (
    <span
      className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold tracking-wide uppercase ${config.className}`}
    >
      {config.label}
    </span>
  );
}
