import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { merchantAPI } from '../api/client';

const STEPS = ['Personal Details', 'Business Details', 'Documents', 'Review & Submit'];

export default function KYCForm() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [submissionId, setSubmissionId] = useState(id || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [documents, setDocuments] = useState([]);
  const [uploadLoading, setUploadLoading] = useState(false);

  const [personal, setPersonal] = useState({ full_name: '', dob: '', address: '', phone: '' });
  const [business, setBusiness] = useState({ business_name: '', business_type: '', gstin: '', registered_address: '' });
  const [docFile, setDocFile] = useState(null);
  const [docType, setDocType] = useState('PAN');

  useEffect(() => {
    if (id) loadSubmission(id);
  }, [id]);

  const loadSubmission = async (sid) => {
    try {
      const res = await merchantAPI.getSubmission(sid);
      const d = res.data;
      setPersonal(d.personal_details || { full_name:'',dob:'',address:'',phone:'' });
      setBusiness(d.business_details || { business_name:'',business_type:'',gstin:'',registered_address:'' });
      setDocuments(d.documents || []);
      setSubmissionId(d.id);
    } catch (err) { setError(err.response?.data?.error || 'Failed to load submission.'); }
  };

  const saveProgress = async () => {
    setLoading(true); setError('');
    try {
      if (submissionId) {
        await merchantAPI.updateSubmission(submissionId, { personal_details: personal, business_details: business });
        setSuccess('Progress saved!');
      } else {
        const res = await merchantAPI.createSubmission({ personal_details: personal, business_details: business });
        setSubmissionId(res.data.id);
        setSuccess('Draft created!');
      }
    } catch (err) { setError(err.response?.data?.error || 'Failed to save.'); }
    finally { setLoading(false); setTimeout(() => setSuccess(''), 3000); }
  };

  const handleUpload = async () => {
    if (!docFile || !submissionId) return;
    setUploadLoading(true); setError('');
    try {
      const fd = new FormData();
      fd.append('file', docFile);
      fd.append('type', docType);
      await merchantAPI.uploadDocument(submissionId, fd);
      const res = await merchantAPI.listDocuments(submissionId);
      setDocuments(res.data);
      setDocFile(null);
      setSuccess('Document uploaded!');
    } catch (err) { setError(err.response?.data?.error || 'Upload failed.'); }
    finally { setUploadLoading(false); setTimeout(() => setSuccess(''), 3000); }
  };

  const handleSubmit = async () => {
    setLoading(true); setError('');
    try {
      await saveProgress();
      await merchantAPI.submitSubmission(submissionId);
      navigate('/');
    } catch (err) { setError(err.response?.data?.error || 'Submission failed.'); setLoading(false); }
  };

  const handleResubmit = async () => {
    setLoading(true); setError('');
    try {
      await merchantAPI.resubmitSubmission(submissionId);
      navigate('/');
    } catch (err) { setError(err.response?.data?.error || 'Resubmission failed.'); setLoading(false); }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 animate-fade-in">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-white">{id ? 'Edit KYC Submission' : 'New KYC Submission'}</h1>
        <p className="text-gray-400 mt-1">Complete all steps to submit your KYC application</p>
      </div>

      {/* Step indicator */}
      <div className="glass-card p-4 mb-6">
        <div className="flex items-center justify-between">
          {STEPS.map((s, i) => (
            <div key={s} className="flex items-center gap-2">
              <button onClick={() => setStep(i)} className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${i === step ? 'bg-brand-600 text-white' : i < step ? 'bg-emerald-600 text-white' : 'bg-white/10 text-gray-500'}`}>
                {i < step ? '✓' : i + 1}
              </button>
              <span className={`hidden sm:inline text-xs ${i === step ? 'text-white' : 'text-gray-500'}`}>{s}</span>
              {i < STEPS.length - 1 && <div className={`hidden sm:block w-8 h-px ${i < step ? 'bg-emerald-500' : 'bg-white/10'}`} />}
            </div>
          ))}
        </div>
      </div>

      {error && <div className="mb-4 p-3 rounded-xl bg-red-500/15 border border-red-500/30 text-red-300 text-sm animate-fade-in">{error}</div>}
      {success && <div className="mb-4 p-3 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-sm animate-fade-in">{success}</div>}

      <div className="glass-card p-6 animate-slide-up">
        {/* Step 0: Personal */}
        {step === 0 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white mb-4">Personal Details</h2>
            {[{l:'Full Name',k:'full_name',t:'text',p:'John Doe'},{l:'Date of Birth',k:'dob',t:'date',p:''},{l:'Address',k:'address',t:'text',p:'123 Main St'},{l:'Phone',k:'phone',t:'tel',p:'+91-9876543210'}].map(f=>(
              <div key={f.k}><label className="block text-sm font-medium text-gray-300 mb-1.5">{f.l}</label>
              <input type={f.t} value={personal[f.k]} onChange={e=>setPersonal({...personal,[f.k]:e.target.value})} className="input-field" placeholder={f.p}/></div>
            ))}
          </div>
        )}

        {/* Step 1: Business */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white mb-4">Business Details</h2>
            {[{l:'Business Name',k:'business_name',p:'Acme Corp'},{l:'Business Type',k:'business_type',p:'Sole Proprietorship'},{l:'GSTIN',k:'gstin',p:'27AAPFU0939F1ZV'},{l:'Registered Address',k:'registered_address',p:'456 Commercial St'}].map(f=>(
              <div key={f.k}><label className="block text-sm font-medium text-gray-300 mb-1.5">{f.l}</label>
              <input type="text" value={business[f.k]} onChange={e=>setBusiness({...business,[f.k]:e.target.value})} className="input-field" placeholder={f.p}/></div>
            ))}
          </div>
        )}

        {/* Step 2: Documents */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold text-white mb-4">Upload Documents</h2>
            {!submissionId && <p className="text-yellow-300 text-sm">Save your submission first (go back and click Save).</p>}
            {submissionId && (
              <>
                <div className="flex flex-col sm:flex-row gap-3">
                  <select value={docType} onChange={e=>setDocType(e.target.value)} className="input-field sm:w-40">
                    <option value="PAN">PAN Card</option><option value="Aadhaar">Aadhaar Card</option><option value="Bank">Bank Statement</option>
                  </select>
                  <input type="file" accept=".pdf,.jpg,.jpeg,.png" onChange={e=>setDocFile(e.target.files[0])} className="input-field flex-1 file:mr-4 file:py-1 file:px-3 file:rounded-lg file:border-0 file:text-sm file:bg-brand-600 file:text-white"/>
                  <button onClick={handleUpload} disabled={!docFile||uploadLoading} className="btn-primary whitespace-nowrap">
                    {uploadLoading ? <div className="spinner"/> : 'Upload'}
                  </button>
                </div>
                <p className="text-xs text-gray-500">Accepted: PDF, JPG, PNG. Max 5MB.</p>
                {documents.length > 0 && (
                  <div className="mt-4 space-y-2">
                    <p className="text-sm font-medium text-gray-300">Uploaded Documents:</p>
                    {documents.map(d=>(
                      <div key={d.id} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/10">
                        <div className="flex items-center gap-3">
                          <span className="text-lg">{d.type==='PAN'?'🪪':d.type==='Aadhaar'?'🆔':'🏦'}</span>
                          <div><p className="text-sm text-white">{d.type}</p><p className="text-xs text-gray-500">{new Date(d.uploaded_at).toLocaleString()}</p></div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {/* Step 3: Review */}
        {step === 3 && (
          <div className="space-y-6">
            <h2 className="text-lg font-semibold text-white">Review & Submit</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-sm font-medium text-gray-400 mb-3">Personal Details</h3>
                {Object.entries(personal).map(([k,v])=><p key={k} className="text-sm text-white mb-1"><span className="text-gray-500 capitalize">{k.replace('_',' ')}: </span>{v||'—'}</p>)}
              </div>
              <div className="p-4 rounded-xl bg-white/5 border border-white/10">
                <h3 className="text-sm font-medium text-gray-400 mb-3">Business Details</h3>
                {Object.entries(business).map(([k,v])=><p key={k} className="text-sm text-white mb-1"><span className="text-gray-500 capitalize">{k.replace('_',' ')}: </span>{v||'—'}</p>)}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10">
              <h3 className="text-sm font-medium text-gray-400 mb-2">Documents ({documents.length})</h3>
              {documents.length === 0 ? <p className="text-sm text-yellow-300">No documents uploaded.</p> :
                documents.map(d=><span key={d.id} className="inline-block mr-2 mb-1 px-3 py-1 rounded-lg bg-brand-500/20 text-brand-300 text-xs">{d.type}</span>)
              }
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between mt-8 pt-6 border-t border-white/10">
          <button onClick={() => setStep(Math.max(0, step - 1))} disabled={step === 0} className="btn-secondary disabled:opacity-30">← Back</button>
          <div className="flex gap-3">
            {step < 3 && <button onClick={saveProgress} disabled={loading} className="btn-secondary">{loading ? <div className="spinner" /> : 'Save Draft'}</button>}
            {step < 3 ? (
              <button onClick={() => { if (!submissionId) saveProgress().then(()=>setStep(step+1)); else setStep(step+1); }} className="btn-primary">Next →</button>
            ) : (
              <button onClick={handleSubmit} disabled={loading} className="btn-success flex items-center gap-2">{loading && <div className="spinner"/>} Submit KYC</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
