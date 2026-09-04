import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, Clock, MinusCircle, AlertCircle, HelpCircle } from 'lucide-react';

const StatusBadge = ({ status }) => {
  switch (status) {
    case 'COMPLIANT':
    case 'PASSED':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Compliant
        </span>
      );
    case 'NOT_APPLICABLE':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/20">
          <MinusCircle className="w-3.5 h-3.5" />
          Not Applicable
        </span>
      );
    case 'REVIEW':
    case 'REVIEW_REQUIRED':
    case 'OCR_REQUIRED':
    case 'MISSING_FROM_HTML':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
          <AlertCircle className="w-3.5 h-3.5" />
          Review / OCR Pending
        </span>
      );
    case 'INSUFFICIENT_EVIDENCE':
    case 'AMBIGUOUS':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <HelpCircle className="w-3.5 h-3.5" />
          Insufficient Evidence
        </span>
      );
    case 'WARNING':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
          <AlertTriangle className="w-3.5 h-3.5" />
          Warning
        </span>
      );
    case 'NON_COMPLIANT':
    case 'FAILED':
    case 'MISSING':
    case 'INVALID':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
          <XCircle className="w-3.5 h-3.5" />
          Non-Compliant
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse">
          <Clock className="w-3.5 h-3.5 animate-spin" />
          Processing...
        </span>
      );
  }
};

export default StatusBadge;
