import React, { useState, useEffect } from 'react';
import API from '../services/api';
import { BookOpen, Tag } from 'lucide-react';

const RuleExplorer = () => {
  const [categories, setCategories] = useState([]);
  const [selectedCat, setSelectedCat] = useState('');
  const [mappings, setMappings] = useState([]);
  const [rules, setRules] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get('/categories')
      .then((res) => {
        setCategories(res.data);
        if (res.data.length > 0) setSelectedCat(res.data[0].id);
      })
      .catch((err) => console.error(err));

    API.get('/rules')
      .then((res) => setRules(res.data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (selectedCat) {
      API.get(`/rule-mappings?category_id=${selectedCat}`)
        .then((res) => setMappings(res.data))
        .catch((err) => console.error(err));
    }
  }, [selectedCat]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-100 tracking-tight">Legal Metrology Rule Explorer</h1>
        <p className="text-xs text-slate-400">
          Browse mandatory declaration rules dynamically configured per product category in PostgreSQL.
        </p>
      </div>

      <div className="flex items-center gap-3">
        <label className="text-xs font-semibold text-slate-300">Select Category:</label>
        <select
          value={selectedCat}
          onChange={(e) => setSelectedCat(e.target.value)}
          className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
        >
          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Category Mapped Rules */}
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <Tag className="w-4 h-4 text-cyan-400" />
            Applicable Mandatory Rules for Category
          </h3>
          <div className="space-y-2">
            {mappings.length > 0 ? (
              mappings.map((m) => (
                <div key={m.id} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-cyan-400 font-mono">{m.rule?.rule_code}</span>
                    <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      {m.rule?.enforcement_level}
                    </span>
                  </div>
                  <h4 className="font-semibold text-slate-200">{m.rule?.declaration_name}</h4>
                  <p className="text-slate-400 text-[11px]">Required tokens: {m.rule?.mandatory_fields}</p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500 italic py-4 text-center">No specific rules mapped to this category.</p>
            )}
          </div>
        </div>

        {/* Global Rules Database */}
        <div className="glass-card rounded-xl p-5 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-emerald-400" />
            Complete Legal Metrology Rules Registry
          </h3>
          <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
            {rules.map((r) => (
              <div key={r.id} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-emerald-400 font-mono">{r.rule_code}</span>
                  <span className="text-slate-400 text-[10px] uppercase">{r.enforcement_level}</span>
                </div>
                <h4 className="font-semibold text-slate-200">{r.declaration_name}</h4>
                <p className="text-slate-400 text-[11px]">Tokens: {r.mandatory_fields}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RuleExplorer;
