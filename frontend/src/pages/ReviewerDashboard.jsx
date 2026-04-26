import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { reviewerAPI } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import SLAIndicator from '../components/SLAIndicator';
import QueueStats from '../components/QueueStats';

export default function ReviewerDashboard() {
  const [queue, setQueue] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { fetchQueue(); }, []);

  const fetchQueue = async () => {
    try {
      setLoading(true);
      const res = await reviewerAPI.getQueue();
      setQueue(res.data.submissions);
      setStats(res.data.stats);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load queue.');
    } finally { setLoading(false); }
  };

  const handlePick = async (id) => {
    try {
      await reviewerAPI.pickSubmission(id);
      fetchQueue();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to pick submission.');
    }
  };

  if (loading) return <div className="flex items-center justify-center h-64"><div className="spinner w-8 h-8" /></div>;

  return (
    <div className="max-w-6xl mx-auto px-4 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">Reviewer Dashboard</h1>
        <p className="text-gray-400 mt-1">Review and process KYC submissions</p>
      </div>

      {error && <div className="mb-6 p-4 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-sm">{error}</div>}

      <div className="mb-8">
        <QueueStats stats={stats} />
      </div>

      <div className="glass-card overflow-hidden">
        <div className="px-6 py-4 border-b border-white/10">
          <h2 className="text-lg font-semibold text-white">Review Queue</h2>
          <p className="text-sm text-gray-400">Submissions awaiting review, sorted by oldest first</p>
        </div>

        {queue.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-400 text-lg">🎉 Queue is empty!</p>
            <p className="text-gray-500 mt-2">All submissions have been processed.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead><tr className="border-b border-white/10">
                {['ID','Merchant','Status','SLA','Submitted','Action'].map(h=>(
                  <th key={h} className="text-left px-6 py-4 text-xs font-medium text-gray-400 uppercase tracking-wider">{h}</th>
                ))}
              </tr></thead>
              <tbody className="divide-y divide-white/5">
                {queue.map(sub=>(
                  <tr key={sub.id} className="hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 text-sm font-mono text-gray-300">#{sub.id}</td>
                    <td className="px-6 py-4 text-sm text-white">{sub.merchant_name}</td>
                    <td className="px-6 py-4"><StatusBadge status={sub.status}/></td>
                    <td className="px-6 py-4"><SLAIndicator atRisk={sub.at_risk} timeInQueueHours={sub.time_in_queue_hours}/></td>
                    <td className="px-6 py-4 text-sm text-gray-400">{new Date(sub.updated_at).toLocaleString()}</td>
                    <td className="px-6 py-4">
                      <div className="flex gap-2">
                        <button onClick={()=>handlePick(sub.id)} className="btn-primary text-xs px-3 py-1.5">Pick Up</button>
                        <Link to={`/reviewer/submissions/${sub.id}`} className="btn-secondary text-xs px-3 py-1.5">View</Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
