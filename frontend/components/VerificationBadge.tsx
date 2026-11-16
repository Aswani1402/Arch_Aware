import React from 'react';
import { CheckCircle2, Eye, HelpCircle, AlertCircle } from 'lucide-react';

interface VerificationBadgeProps {
  status?: string | null;
  isPotential?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const VerificationBadge: React.FC<VerificationBadgeProps> = ({
  status,
  isPotential = false,
  className = "",
  size = "md"
}) => {
  const s = (status || '').toUpperCase().trim();
  const sizePad = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';

  if (isPotential || s === "POTENTIAL" || s === "POTENTIAL_GOOGLE_PLACE") {
    return (
      <span
        data-verification-state="POTENTIAL"
        className={`inline-flex items-center gap-1.5 ${sizePad} rounded-full font-medium bg-amber-50 text-amber-900 border border-amber-300 ${className}`}
        title="Discovered via business listing - contact supplier to confirm stock"
      >
        <AlertCircle className="w-3.5 h-3.5 text-amber-600 shrink-0" />
        <span>Potential Supplier — Contact to Confirm</span>
      </span>
    );
  }

  if (s === "VERIFIED_EXACT" || s === "MANUFACTURER_CONFIRMED" || s === "SUPPLIER_CONFIRMED" || s === "VERIFIED") {
    return (
      <span
        data-verification-state="VERIFIED"
        className={`inline-flex items-center gap-1.5 ${sizePad} rounded-full font-medium bg-emerald-50 text-emerald-900 border border-emerald-300 ${className}`}
        title="Confirmed with manufacturer catalog specifications"
      >
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
        <span>{s === "VERIFIED" ? "Verified" : "Manufacturer Confirmed"}</span>
      </span>
    );
  }

  if (s === "VISUALLY_SIMILAR") {
    return (
      <span
        data-verification-state="VISUALLY_SIMILAR"
        className={`inline-flex items-center gap-1.5 ${sizePad} rounded-full font-medium bg-blue-50 text-blue-900 border border-blue-200 ${className}`}
        title="Visual similarity to reference - review technical specs"
      >
        <Eye className="w-3.5 h-3.5 text-blue-600 shrink-0" />
        <span>Visually Similar Product</span>
      </span>
    );
  }

  if (s === "ALTERNATIVE_REVIEW") {
    return (
      <span
        data-verification-state="ALTERNATIVE_REVIEW"
        className={`inline-flex items-center gap-1.5 ${sizePad} rounded-full font-medium bg-stone-100 text-stone-800 border border-stone-300 ${className}`}
        title="Alternative material option requiring architect review"
      >
        <HelpCircle className="w-3.5 h-3.5 text-stone-600 shrink-0" />
        <span>Alternative Requiring Review</span>
      </span>
    );
  }

  if (s === "UNVERIFIED") {
    return (
      <span
        data-verification-state="UNVERIFIED"
        className={`inline-flex items-center gap-1.5 ${sizePad} rounded-full font-medium bg-stone-100 text-stone-700 border border-stone-300 ${className}`}
        title="Source provenance only; entity verification pending"
      >
        <HelpCircle className="w-3.5 h-3.5 text-stone-500 shrink-0" />
        <span>Source Unverified</span>
      </span>
    );
  }

  return (
    <span
      data-verification-state="UNKNOWN"
      className={`inline-flex items-center gap-1.5 ${sizePad} rounded-full font-medium bg-slate-50 text-slate-600 border border-slate-200 ${className}`}
      title="Verification status unavailable"
    >
      <HelpCircle className="w-3.5 h-3.5 text-slate-400 shrink-0" />
      <span>Verification Unknown</span>
    </span>
  );
};
