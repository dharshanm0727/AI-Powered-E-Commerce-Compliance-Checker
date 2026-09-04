import re
from typing import List, Dict, Any

class OCRTextNormalizer:
    """
    Normalizes extracted OCR text, eliminates duplicate declarations,
    and returns parsed declarations with confidence scores.
    """

    @staticmethod
    def deduplicate_and_clean(raw_texts: List[str]) -> str:
        """Remove duplicate text lines, trim noise, and normalize spaces."""
        seen = set()
        cleaned_lines = []

        for text in raw_texts:
            line = text.strip()
            if not line or len(line) < 2:
                continue

            line_normalized = re.sub(r'\s+', ' ', line)
            line_lower = line_normalized.lower()

            if line_lower not in seen:
                seen.add(line_lower)
                cleaned_lines.append(line_normalized)

        return "\n".join(cleaned_lines)

    @classmethod
    def remove_duplicate_declarations(cls, declarations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate extracted declaration objects by normalized key and value."""
        unique_declarations = []
        seen_keys = set()

        for decl in declarations:
            key_id = f"{decl.get('key_name', '').lower()}:{decl.get('normalized_value', '').lower()}"
            if key_id not in seen_keys:
                seen_keys.add(key_id)
                unique_declarations.append(decl)

        return unique_declarations

    @classmethod
    def extract_ocr_declarations(cls, full_text: str, default_confidence: float = 0.88) -> List[Dict[str, Any]]:
        """Parse key legal metrology declarations from OCR text stream with confidence scoring."""
        declarations = []

        # 1. MRP (M.R.P. / MRP / Price / Maximum Retail Price / Rs / ₹)
        mrp = re.search(r'(?:M\.?R\.?P\.?|Maximum Retail Price|Price|Rs\.?|₹)\s*[:\-]?\s*(?:Rs\.?|₹)?\s*([0-9.,]+)', full_text, re.IGNORECASE)
        if mrp:
            declarations.append({
                "key_name": "MRP (OCR)",
                "raw_value": mrp.group(0),
                "normalized_value": f"Rs. {mrp.group(1)}",
                "confidence_score": round(min(1.0, max(0.0, default_confidence)), 2),
                "source": "ocr"
            })

        # 2. Net Quantity (Net / Nett / Weight / Vol / Wt / Qty / Volume)
        net_qty = re.search(r'(?:Nett?\s*(?:Qty|Weight|Wt\.?|Vol|Volume|Quantity)|Net\s*Wt\.?)\s*[:\-]?\s*([0-9.]+\s*(?:g|kg|ml|l|grm|pcs|unit|units|n))', full_text, re.IGNORECASE)
        if not net_qty:
            net_qty = re.search(r'(?:Net\s*Qty|Net\s*Quantity|Net\s*Weight|Net\s*Vol)\s*[:\-]?\s*([0-9.]+\s*(?:g|kg|ml|l|grm|pcs|unit|units|n))', full_text, re.IGNORECASE)

        if net_qty:
            declarations.append({
                "key_name": "Net Quantity (OCR)",
                "raw_value": net_qty.group(0),
                "normalized_value": net_qty.group(1),
                "confidence_score": round(min(1.0, max(0.0, default_confidence - 0.03)), 2),
                "source": "ocr"
            })

        # 3. Date of Manufacture / Packing
        mfg = re.search(r'(?:Date of Manufacture|Date of Packing|Pkd Date|Mfg Date|MFD|MFG)\s*(?:by|at|on)?\s*[:\-]?\s*([A-Za-z0-9/\- ]+)', full_text, re.IGNORECASE)
        if mfg:
            declarations.append({
                "key_name": "Date of Manufacture (OCR)",
                "raw_value": mfg.group(0),
                "normalized_value": mfg.group(1).strip(),
                "confidence_score": round(min(1.0, max(0.0, default_confidence - 0.05)), 2),
                "source": "ocr"
            })

        # 4. Best Before / Expiry Date
        exp = re.search(r'(?:Best Before|Expiry Date|Exp Date|Use By|Use Before)\s*[:\-]?\s*([A-Za-z0-9/\- ]+)', full_text, re.IGNORECASE)
        if exp:
            declarations.append({
                "key_name": "Expiry Date (OCR)",
                "raw_value": exp.group(0),
                "normalized_value": exp.group(1).strip(),
                "confidence_score": round(min(1.0, max(0.0, default_confidence - 0.04)), 2),
                "source": "ocr"
            })

        # 5. FSSAI License Number
        fssai = re.search(r'(?:FSSAI|Lic\.?\s*No\.?)\s*[:\-]?\s*([0-9]{14})', full_text, re.IGNORECASE)
        if fssai:
            declarations.append({
                "key_name": "FSSAI License (OCR)",
                "raw_value": fssai.group(0),
                "normalized_value": fssai.group(1).strip(),
                "confidence_score": round(min(1.0, max(0.0, default_confidence + 0.05)), 2),
                "source": "ocr"
            })

        # 6. Country of Origin
        coo = re.search(r'(?:Country of Origin|Made in|Origin)\s*[:\-]?\s*([A-Za-z]+)', full_text, re.IGNORECASE)
        if coo:
            declarations.append({
                "key_name": "Country of Origin (OCR)",
                "raw_value": coo.group(0),
                "normalized_value": coo.group(1).strip(),
                "confidence_score": round(min(1.0, max(0.0, default_confidence + 0.05)), 2),
                "source": "ocr"
            })

        # 7. Customer / Consumer Care Details
        care = re.search(r'(?:Customer Care|Consumer Care|Helpline|Toll Free|Consumer Helpline)\s*[:\-]?\s*([^.\n]+)', full_text, re.IGNORECASE)
        if care:
            declarations.append({
                "key_name": "Consumer Care (OCR)",
                "raw_value": care.group(0),
                "normalized_value": care.group(1).strip(),
                "confidence_score": round(min(1.0, max(0.0, default_confidence - 0.02)), 2),
                "source": "ocr"
            })

        # 8. Part / Model Number
        pn = re.search(r'(?:Part Number|Part No|P/N|Model Number|Model No)\s*[:\-]?\s*([A-Za-z0-9\-]+)', full_text, re.IGNORECASE)
        if pn:
            declarations.append({
                "key_name": "Part / Model Number (OCR)",
                "raw_value": pn.group(0),
                "normalized_value": pn.group(1).strip(),
                "confidence_score": round(min(1.0, max(0.0, default_confidence)), 2),
                "source": "ocr"
            })

        return cls.remove_duplicate_declarations(declarations)
