import React, { useState, useEffect } from 'react';
import API from '../services/api';
import { Plus, Trash2, Edit, Shield } from 'lucide-react';

const AdminPanel = () => {
  const [categories, setCategories] = useState([]);
  const [rules, setRules] = useState([]);
  const [newCatName, setNewCatName] = useState('');
  const [newRuleCode, setNewRuleCode] = useState('');
  const [newRuleDecl, setNewRuleDecl] = useState('');
  const [newRuleTokens, setNewRuleTokens] = useState('');
  const [activeTab, setActiveTab] = useState('categories');

  const loadData = () => {
    API.get('/categories').then((res) => setCategories(res.data));
    API.get('/rules').then((res) => setRules(res.data));
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddCategory = async (e) => {
    e.preventDefault();
    if (!newCatName) return;
    await API.post('/categories', { name: newCatName, description: 'User added category' });
    setNewCatName('');
    loadData();
  };

  const handleDeleteCategory = async (id) => {
    if (window.confirm('Delete this category?')) {
      await API.delete(`/categories/${id}`);
      loadData();
    }
  };

  const handleAddRule = async (e) => {
    e.preventDefault();
    if (!newRuleCode || !newRuleDecl) return;
    await API.post('/rules', {
      rule_code: newRuleCode,
      declaration_name: newRuleDecl,
      mandatory_fields: newRuleTokens,
      enforcement_level: 'strict'
    });
    setNewRuleCode('');
    setNewRuleDecl('');
    setNewRuleTokens('');
    loadData();
  };

  const handleDeleteRule = async (id) => {
    if (window.confirm('Delete this rule?')) {
      await API.delete(`/rules/${id}`);
      loadData();
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center">
          <Shield className="w-5 h-5 text-cyan-400" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Admin Management Panel</h1>
          <p className="text-xs text-slate-400">Configure legal metrology rules and categories without changing source code</p>
        </div>
      </div>

      <div className="flex border-b border-slate-800 gap-4">
        <button
          onClick={() => setActiveTab('categories')}
          className={`pb-3 text-xs font-semibold border-b-2 transition-colors ${
            activeTab === 'categories' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Product Categories ({categories.length})
        </button>
        <button
          onClick={() => setActiveTab('rules')}
          className={`pb-3 text-xs font-semibold border-b-2 transition-colors ${
            activeTab === 'rules' ? 'border-cyan-400 text-cyan-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Compliance Rules ({rules.length})
        </button>
      </div>

      {activeTab === 'categories' && (
        <div className="space-y-6">
          <form onSubmit={handleAddCategory} className="glass-card p-4 rounded-xl border border-slate-800 flex gap-3">
            <input
              type="text"
              required
              value={newCatName}
              onChange={(e) => setNewCatName(e.target.value)}
              placeholder="Add New Product Category (e.g., Smart Watch)..."
              className="flex-1 px-4 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-cyan-500 text-white font-semibold text-xs hover:bg-cyan-400 transition-colors flex items-center gap-1.5"
            >
              <Plus className="w-4 h-4" /> Add Category
            </button>
          </form>

          <div className="glass-card rounded-xl p-5 border border-slate-800">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
              {categories.map((c) => (
                <div key={c.id} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 flex justify-between items-center text-xs">
                  <span className="font-semibold text-slate-200">{c.name}</span>
                  <button onClick={() => handleDeleteCategory(c.id)} className="text-rose-400 hover:text-rose-300">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'rules' && (
        <div className="space-y-6">
          <form onSubmit={handleAddRule} className="glass-card p-4 rounded-xl border border-slate-800 grid grid-cols-1 md:grid-cols-4 gap-3">
            <input
              type="text"
              required
              value={newRuleCode}
              onChange={(e) => setNewRuleCode(e.target.value)}
              placeholder="Rule Code (e.g., LM-NEW-01)"
              className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <input
              type="text"
              required
              value={newRuleDecl}
              onChange={(e) => setNewRuleDecl(e.target.value)}
              placeholder="Declaration Name"
              className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <input
              type="text"
              required
              value={newRuleTokens}
              onChange={(e) => setNewRuleTokens(e.target.value)}
              placeholder="Comma Tokens (e.g. Price, MRP)"
              className="px-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="submit"
              className="px-4 py-2 rounded-lg bg-cyan-500 text-white font-semibold text-xs hover:bg-cyan-400 transition-colors flex items-center justify-center gap-1.5"
            >
              <Plus className="w-4 h-4" /> Save Rule
            </button>
          </form>

          <div className="glass-card rounded-xl p-5 border border-slate-800">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                    <th className="pb-3 px-3">Rule Code</th>
                    <th className="pb-3 px-3">Declaration</th>
                    <th className="pb-3 px-3">Mandatory Tokens</th>
                    <th className="pb-3 px-3">Level</th>
                    <th className="pb-3 px-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/50">
                  {rules.map((r) => (
                    <tr key={r.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-3 font-mono font-bold text-cyan-400">{r.rule_code}</td>
                      <td className="py-3 px-3 text-slate-200 font-medium">{r.declaration_name}</td>
                      <td className="py-3 px-3 text-slate-400">{r.mandatory_fields}</td>
                      <td className="py-3 px-3 text-slate-400 uppercase">{r.enforcement_level}</td>
                      <td className="py-3 px-3">
                        <button onClick={() => handleDeleteRule(r.id)} className="text-rose-400 hover:text-rose-300">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminPanel;
