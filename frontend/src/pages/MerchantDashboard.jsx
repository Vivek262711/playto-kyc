import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { merchantAPI } from '../api/client';
import StatusBadge from '../components/StatusBadge';
import SLAIndicator from '../components/SLAIndicator';

export default function MerchantDashboard() {
  const [submissions, setSubmissions] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('submissions');

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [subRes, notifRes] = await Promise.all([
        merchantAPI.listSubmissions(),
        merchantAPI.getNotifications(),
      ]);
      setSubmissions(subRes.data);
      setNotifications(notifRes.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load data.');
    } finally { setLoading(false); }
  };

  const statusCounts = submissions.reduce((acc, s) => {
    acc[s.status] = (acc[s.status] || 0) + 1; return acc;
  }, {});

  if (loading) return <div className="flex items-center justify-center h-64"><div className="spinner w-8 h-8" /></div>;

  return (
    <div className="max-w-6xl mx-auto px-4 animate-fade-in">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Merchant Dashboard</h1>
          <p className="text-gray-400 mt-1">Manage your KYC submissions</p>
        </div>
        <Link to="/kyc/new" id="new-kyc-btn" className="btn-primary flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" /></svg>
          New KYC Submission
        </Link>
      </div>

      {error && <div className="mb-6 p-4 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-sm">{error}</div>}

      <div className="grid grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
        {['draft','submitted','under_review','approved','rejected','more_info_requested'].map(s=>(
          <div key={s} className="glass-card p-4 text-center">
            <p className="text-2xl font-bold text-white">{statusCounts[s]||0}</p>
            <StatusBadge status={s} />
          </div>
        ))}
      </div>

      <div className="flex gap-1 mb-6 p-1 glass-card w-fit">
        {['submissions','notifications'].map(tab=>(
          <button key={tab} onClick={()=>setActiveTab(tab)} className={`px-4 py-2 rounded-xl text-sm font-medium transition-all capitalize ${activeTab===tab?'bg-brand-600 text-white':'text-gray-400 hover:text-white'}`}>
            {tab} {tab==='notifications'&&notifications.length>0&&<span className="ml-1 px-1.5 py-0.5 rounded-full text-xs bg-brand-500/30">{notifications.length}</span>}
          </button>
        ))}
      </div>

      {activeTab==='submissions' && (
        <div className="glass-card overflow-hidden animate-slide-up">
          {submissions.length===0 ? (
            <div className="p-12 text-center"><p className="text-gray-400 text-lg">No submissions yet.</p></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead><tr className="border-b border-white/10">
                  {['ID','Status','SLA','Docs','Created',''].map(h=><th key={h} className="text-left px-6 py-4 text-xs font-medium text-gray-400 uppercase tracking-wider">{h}</th>)}
                </tr></thead>
                <tbody className="divide-y divide-white/5">
                  {submissions.map(sub=>(
                    <tr key={sub.id} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 text-sm font-mono text-gray-300">#{sub.id}</td>
                      <td className="px-6 py-4"><StatusBadge status={sub.status}/></td>
                      <td className="px-6 py-4"><SLAIndicator atRisk={sub.at_risk} timeInQueueHours={sub.time_in_queue_hours}/></td>
                      <td className="px-6 py-4 text-sm text-gray-400">{sub.document_count} files</td>
                      <td className="px-6 py-4 text-sm text-gray-400">{new Date(sub.created_at).toLocaleDateString()}</td>
                      <td className="px-6 py-4 text-right">
                        <Link to={`/submissions/${sub.id}`} className="text-sm text-brand-400 hover:text-brand-300 font-medium">View →</Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {activeTab==='notifications' && (
        <div className="space-y-3 animate-slide-up">
          {notifications.length===0 ? <div className="glass-card p-12 text-center"><p className="text-gray-400">No notifications yet.</p></div> :
            notifications.map(n=>(
              <div key={n.id} className="glass-card-hover p-4 flex items-start gap-4">
                <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${n.event_type==='approved'?'bg-emerald-400':n.event_type==='rejected'?'bg-red-400':n.event_type==='more_info_requested'?'bg-orange-400':'bg-blue-400'}`}/>
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-white">{n.payload?.message||n.event_type}</p>
                  <p className="text-xs text-gray-500 mt-1">{new Date(n.timestamp).toLocaleString()}</p>
                </div>
                <StatusBadge status={n.event_type}/>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
}
