import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import API from '../services/api';
import StatusBadge from '../components/StatusBadge';
import OCRImageViewer from '../components/OCRImageViewer';
import { Download, FileSpreadsheet, Sparkles, RefreshCw, AlertCircle } from 'lucide-react';

const ReportDetail = () => {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [ocrDecls, setOcrDecls] = useState([]);
  const [declarations, setDeclarations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);
  const [downloadingExcel, setDownloadingExcel] = useState(false);

  const fetchReportData = async () => {
    try {
      const res = await API.get(`/reports/${id}`);
      setReport(res.data);
      if (res.data.product_id) {
        const dRes = await API.get(`/products/${res.data.product_id}/declarations`);
        setDeclarations(dRes.data);
        const oRes = await API.get(`/ocr/declarations/${res.data.product_id}`);
        setOcrDecls(oRes.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch compliance report');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReportData();
  }, [id]);

  useEffect(() => {
    if (!report || report.overall_status !== 'PENDING') return;
    const interval = setInterval(() => {
      API.get(`/compliance/status/${id}`).then((statusRes) => {
        if (statusRes.data.overall_status !== 'PENDING') {
          fetchReportData();
        } else {
          setReport((prev) => prev ? { ...prev, ...statusRes.data } : prev);
        }
      });
    }, 2000);
    return () => clearInterval(interval);
  }, [id, report?.overall_status]);

  const handleRecheck = async () => {
    setLoading(true);
    try {
      const res = await API.post(`/compliance/recheck/${id}`);
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to re-run audit check');
    } finally {
      setLoading(false);
    }
  };

  const handleExportPdf = async () => {
    setDownloadingPdf(true);
    try {
      const response = await API.get(`/reports/${id}/export/pdf`, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `compliance_report_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download PDF report');
    } finally {
      setDownloadingPdf(false);
    }
  };

  const handleExportExcel = async () => {
    setDownloadingExcel(true);
    try {
      const response = await API.get(`/reports/${id}/export/excel`, { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `compliance_report_${id}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to download Excel report');
    } finally {
      setDownloadingExcel(false);
    }
  };

  if (loading && !report) {
    return (
      <div className="p-12 text-center text-slate-400 flex flex-col items-center gap-3">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <span className="text-sm font-semibold">Loading Compliance Audit Report...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="p-8 text-center glass-card rounded-2xl border border-rose-500/20 text-rose-400 space-y-3">
        <AlertCircle className="w-8 h-8 mx-auto" />
        <h2 className="text-lg font-bold">{error || 'Compliance Report Not Found'}</h2>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Actions */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-extrabold text-slate-100">Report #{report.id}</h1>
            <StatusBadge status={report.overall_status} />
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Product: <a href={report.product?.url} target="_blank" rel="noreferrer" className="text-cyan-400 hover:underline">{report.product?.title || report.product?.url}</a>
          </p>
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={handleRecheck}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5 text-blue-400" /> Re-Run Audit
          </button>
          <button
            onClick={handleExportPdf}
            disabled={downloadingPdf}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors disabled:opacity-50"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" /> {downloadingPdf ? 'Exporting...' : 'PDF Report'}
          </button>
          <button
            onClick={handleExportExcel}
            disabled={downloadingExcel}
            className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 border border-slate-700 transition-colors disabled:opacity-50"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" /> {downloadingExcel ? 'Exporting...' : 'Excel Sheet'}
          </button>
        </div>
      </div>

      {/* Real-time Progress Bar */}
      {report.overall_status === 'PENDING' && (
        <div className="glass-card p-4 rounded-xl space-y-3 border border-cyan-500/30 glow-blue">
          <div className="flex items-center justify-between text-xs text-cyan-400 font-semibold">
            <span className="flex items-center gap-2">
              <RefreshCw className="w-4 h-4 animate-spin" /> Live Pipeline Execution: Step {report.step_reached} of 10...
            </span>
            <span>{report.step_reached * 10}%</span>
          </div>
          <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
            <div className="h-full bg-cyan-400 rounded-full transition-all duration-500" style={{ width: `${report.step_reached * 10}%` }} />
          </div>
          <p className="text-xs text-slate-300 italic">{report.reasoning_summary || 'Executing HTML extraction, classification, and OCR audit...'}</p>
        </div>
      )}

      {/* Metric Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase">Legal Metrology Category</span>
          <p className="text-base font-bold text-slate-100 mt-1">{report.category?.name || 'Packaged Commodities'}</p>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase">Compliance Score</span>
          <p className="text-base font-bold text-cyan-400 mt-1">{report.overall_score}%</p>
        </div>

        <div className="glass-card p-5 rounded-xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-400 uppercase">OCR Fallback Status</span>
          <p className="text-base font-bold text-slate-100 mt-1">{report.ocr_checked ? 'Executed (Step 8 Image OCR)' : 'HTML Declarations Sufficient'}</p>
        </div>
      </div>

      {/* AI Rationale */}
      {report.reasoning_summary && (
        <div className="glass-card p-4 rounded-xl border border-slate-800 flex items-start gap-3">
          <Sparkles className="w-5 h-5 text-cyan-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-xs font-bold text-slate-200">Explainable AI Audit Rationale</h4>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">{report.reasoning_summary}</p>
          </div>
        </div>
      )}

      {/* Evaluation Details */}
      <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
        <h3 className="text-sm font-bold text-slate-100">Legal Metrology Declarations Evaluation</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                <th className="pb-3 px-3">Rule Code</th>
                <th className="pb-3 px-3">Mandatory Declaration</th>
                <th className="pb-3 px-3">Status</th>
                <th className="pb-3 px-3">Extracted Found Value</th>
                <th className="pb-3 px-3">AI Reasoning</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {report.violations && report.violations.length > 0 ? (
                report.violations.map((v) => (
                  <tr key={v.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-cyan-400">{v.rule?.rule_code || 'LM-RULE'}</td>
                    <td className="py-3 px-3 text-slate-200 font-medium">{v.field_name}</td>
                    <td className="py-3 px-3">
                      <StatusBadge status={v.status} />
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-300 max-w-xs truncate">{v.actual_found || 'Not Found'}</td>
                    <td className="py-3 px-3 text-slate-400 max-w-xs">{v.ai_reasoning}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center py-6 text-slate-500">
                    No violations found or evaluation pending.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* OCR Multi-Image Viewer */}
      {report.product?.image_urls && report.product.image_urls.length > 0 && (
        <OCRImageViewer images={report.product.image_urls} ocrDeclarations={ocrDecls} />
      )}
    </div>
  );
};

export default ReportDetail;
