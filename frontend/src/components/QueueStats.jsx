export default function QueueStats({ stats }) {
  if (!stats) return null;

  const statCards = [
    {
      label: 'In Queue',
      value: stats.queue_count,
      icon: '📋',
      color: 'from-blue-500/20 to-blue-600/10',
      border: 'border-blue-500/20',
    },
    {
      label: 'Avg Wait',
      value: `${stats.avg_time_in_queue_hours}h`,
      icon: '⏱',
      color: 'from-yellow-500/20 to-yellow-600/10',
      border: 'border-yellow-500/20',
    },
    {
      label: 'Approval Rate (7d)',
      value: `${stats.approval_rate_7d}%`,
      icon: '✅',
      color: 'from-emerald-500/20 to-emerald-600/10',
      border: 'border-emerald-500/20',
    },
    {
      label: 'Resolved (7d)',
      value: stats.total_resolved_7d,
      icon: '📊',
      color: 'from-purple-500/20 to-purple-600/10',
      border: 'border-purple-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((card) => (
        <div
          key={card.label}
          className={`glass-card bg-gradient-to-br ${card.color} ${card.border} p-5 animate-slide-up`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-2xl">{card.icon}</span>
          </div>
          <p className="text-2xl font-bold text-white">{card.value}</p>
          <p className="text-sm text-gray-400 mt-1">{card.label}</p>
        </div>
      ))}
    </div>
  );
}
