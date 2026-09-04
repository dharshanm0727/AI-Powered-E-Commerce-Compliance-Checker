import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import API from '../services/api';
import StatusBadge from '../components/StatusBadge';
import { Search, Filter } from 'lucide-react';

const History = () => {
  const [reports, setReports] = useState([]);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let url = '/reports?limit=100';
    if (statusFilter) url += `&status=${statusFilter}`;

    API.get(url)
      .then((res) => setReports(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [statusFilter]);

  const filtered = reports.filter((r) => {
    const title = r.product?.title || r.product?.url || '';
    return title.toLowerCase().includes(search.toLowerCase());
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Compliance Audit History</h1>
        <p className="text-xs text-slate-400">Search and filter previous product scan reports</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by product title or URL..."
            className="w-full pl-9 pr-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="COMPLIANT">Compliant</option>
            <option value="WARNING">Warning</option>
            <option value="NON_COMPLIANT">Non-Compliant</option>
          </select>
        </div>
      </div>

      <div className="glass-card rounded-xl p-5 border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                <th className="pb-3 px-3">Report ID</th>
                <th className="pb-3 px-3">Date</th>
                <th className="pb-3 px-3">Product Title</th>
                <th className="pb-3 px-3">Category</th>
                <th className="pb-3 px-3">Status</th>
                <th className="pb-3 px-3">Score</th>
                <th className="pb-3 px-3">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-6 text-slate-500">Loading audit history...</td>
                </tr>
              ) : filtered.length > 0 ? (
                filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3 px-3 font-mono font-bold text-slate-300">#{r.id}</td>
                    <td className="py-3 px-3 text-slate-400">{new Date(r.created_at).toLocaleDateString()}</td>
                    <td className="py-3 px-3 max-w-xs truncate text-slate-200 font-medium">
                      {r.product?.title || r.product?.url}
                    </td>
                    <td className="py-3 px-3 text-slate-400">{r.category?.name || 'Packaged Commodities'}</td>
                    <td className="py-3 px-3">
                      <StatusBadge status={r.overall_status} />
                    </td>
                    <td className="py-3 px-3 font-bold text-slate-200">{r.overall_score}%</td>
                    <td className="py-3 px-3">
                      <Link to={`/reports/${r.id}`} className="text-cyan-400 font-semibold hover:underline">
                        View
                      </Link>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="7" className="text-center py-6 text-slate-500">No matching reports found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default History;
