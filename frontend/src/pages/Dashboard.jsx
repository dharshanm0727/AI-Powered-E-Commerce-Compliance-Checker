import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import API from '../services/api';
import StatusBadge from '../components/StatusBadge';
import { ShieldCheck, CheckCircle, AlertOctagon, AlertTriangle, ArrowRight, Activity } from 'lucide-react';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get('/dashboard/stats')
      .then((res) => setStats(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center text-slate-400">Loading Dashboard Statistics...</div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Compliance Dashboard</h1>
        <p className="text-xs text-slate-400">Legal Metrology Packaged Commodity Audit Statistics</p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card p-5 rounded-xl space-y-2 border-l-4 border-l-cyan-500">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-semibold uppercase">Total Scanned</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold text-slate-100">{stats?.total_products_scanned || 0}</p>
        </div>

        <div className="glass-card p-5 rounded-xl space-y-2 border-l-4 border-l-emerald-500">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-semibold uppercase">Compliant</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold text-emerald-400">{stats?.compliant_count || 0}</p>
        </div>

        <div className="glass-card p-5 rounded-xl space-y-2 border-l-4 border-l-amber-500">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-semibold uppercase">Warnings</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <p className="text-3xl font-extrabold text-amber-400">{stats?.warning_count || 0}</p>
        </div>

        <div className="glass-card p-5 rounded-xl space-y-2 border-l-4 border-l-rose-500">
          <div className="flex justify-between items-center text-slate-400">
            <span className="text-xs font-semibold uppercase">Non-Compliant</span>
            <AlertOctagon className="w-4 h-4 text-rose-400" />
          </div>
          <p className="text-3xl font-extrabold text-rose-400">{stats?.non_compliant_count || 0}</p>
        </div>
      </div>

      {/* Compliance Rate Bar */}
      <div className="glass-card p-5 rounded-xl space-y-3">
        <div className="flex justify-between items-center">
          <span className="text-sm font-semibold text-slate-200">Overall Compliance Rate</span>
          <span className="text-sm font-bold text-cyan-400">{stats?.compliance_rate || 100}%</span>
        </div>
        <div className="w-full h-3 bg-slate-900 rounded-full overflow-hidden p-0.5 border border-slate-800">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full transition-all duration-500"
            style={{ width: `${stats?.compliance_rate || 100}%` }}
          />
        </div>
      </div>

      {/* Recent Audit Reports Table */}
      <div className="glass-card rounded-xl p-5 space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-base font-bold text-slate-100">Recent Product Compliance Reports</h2>
          <Link to="/history" className="text-xs font-semibold text-cyan-400 hover:underline flex items-center gap-1">
            View All <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                <th className="pb-3 px-3">Report ID</th>
                <th className="pb-3 px-3">Product Title</th>
                <th className="pb-3 px-3">Category</th>
                <th className="pb-3 px-3">Status</th>
                <th className="pb-3 px-3">Score</th>
                <th className="pb-3 px-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {stats?.recent_reports && stats.recent_reports.length > 0 ? (
                stats.recent_reports.map((report) => (
                  <tr key={report.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-3 font-mono font-bold text-slate-300">#{report.id}</td>
                    <td className="py-3.5 px-3 max-w-xs truncate text-slate-200 font-medium">
                      {report.product?.title || report.product?.url}
                    </td>
                    <td className="py-3.5 px-3 text-slate-400">{report.category?.name || 'Detecting...'}</td>
                    <td className="py-3.5 px-3">
                      <StatusBadge status={report.overall_status} />
                    </td>
                    <td className="py-3.5 px-3 font-bold text-slate-200">{report.overall_score}%</td>
                    <td className="py-3.5 px-3">
                      <Link
                        to={`/reports/${report.id}`}
                        className="text-cyan-400 font-semibold hover:underline"
                      >
                        Details
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="text-center py-6 text-slate-500">
                    No compliance scans performed yet. Submit a product URL to begin!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
