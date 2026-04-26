export default function SLAIndicator({ atRisk, timeInQueueHours }) {
  if (!atRisk && !timeInQueueHours) return null;

  const hours = timeInQueueHours || 0;
  const displayTime =
    hours < 1
      ? `${Math.round(hours * 60)}m`
      : `${hours.toFixed(1)}h`;

  return (
    <div className="flex items-center gap-2">
      {atRisk ? (
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-red-500/15 border border-red-500/30">
          <div className="w-2 h-2 rounded-full bg-red-400 animate-pulse" />
          <span className="text-xs font-medium text-red-300">
            SLA At Risk — {displayTime}
          </span>
        </div>
      ) : (
        <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-emerald-500/15 border border-emerald-500/30">
          <div className="w-2 h-2 rounded-full bg-emerald-400" />
          <span className="text-xs font-medium text-emerald-300">
            On Track — {displayTime}
          </span>
        </div>
      )}
    </div>
  );
}
