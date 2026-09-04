import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import API from '../services/api';
import { Link2, Sparkles, CheckCircle2 } from 'lucide-react';

const SubmitUrl = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await API.post('/compliance/check', { url });
      navigate(`/reports/${res.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to submit URL for analysis');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Audit Product Page</h1>
        <p className="text-xs text-slate-400">
          Enter an e-commerce product URL to inspect mandatory Legal Metrology packaged commodity declarations.
        </p>
      </div>

      <div className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
        {error && (
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2">E-Commerce Product URL</label>
            <div className="relative">
              <Link2 className="w-4 h-4 text-slate-400 absolute left-3 top-3.5" />
              <input
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://www.amazon.in/dp/B08X123456 or https://www.flipkart.com/..."
                className="w-full pl-9 pr-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold text-sm hover:from-cyan-400 hover:to-blue-500 transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            {loading ? 'Initiating Compliance Scanner...' : 'Start AI Compliance Audit'}
          </button>
        </form>

        <div className="pt-4 border-t border-slate-800/60 space-y-2">
          <h3 className="text-xs font-semibold text-slate-300">Automated Legal Metrology Workflow Steps:</h3>
          <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-slate-400">
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> 1. HTML Scraping & LLM Declaration Extraction
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> 2. AI Product Category Classification
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> 3. Dynamic Legal Metrology Rule Matching
            </li>
            <li className="flex items-center gap-2">
              <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" /> 4. OCR Image Fallback & Explainable Audit
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SubmitUrl;
