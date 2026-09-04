import json
from typing import Dict, Any, List
import google.generativeai as genai

from app.core.config import settings
from app.services.ai.base import BaseAIService
from app.services.ai.providers.mock_provider import MockAIProvider

class GeminiAIProvider(BaseAIService):
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(settings.LLM_MODEL or "gemini-1.5-pro")
            self.active = True
        else:
            self.active = False
            self.fallback = MockAIProvider()

    def extract_declarations(self, raw_html: str) -> List[Dict[str, Any]]:
        if not self.active:
            return self.fallback.extract_declarations(raw_html)
        
        prompt = f"""
        Analyze the following e-commerce product HTML text and extract ONLY mandatory Legal Metrology packaged commodity declarations (e.g., MRP, Net Quantity, Manufacturer Details, Country of Origin, Date of Manufacture, Expiry Date, FSSAI Number, Customer Care Details).
        Ignore marketing fluff. Return a strict JSON array of objects with fields:
        "key_name", "raw_value", "normalized_value", "confidence_score" (float 0-1).

        HTML snippet:
        {raw_html[:6000]}
        """
        try:
            res = self.model.generate_content(prompt)
            clean_json = res.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_json)
        except Exception:
            return self.fallback.extract_declarations(raw_html)

    def classify_category(self, title: str, html_text: str, categories: List[str]) -> str:
        if not self.active:
            return self.fallback.classify_category(title, html_text, categories)

        prompt = f"""
        Classify this e-commerce product into EXACTLY ONE of the following allowed categories:
        {json.dumps(categories)}

        Title: {title}
        Snippet: {html_text[:2000]}

        Return ONLY the category name.
        """
        try:
            res = self.model.generate_content(prompt)
            cat = res.text.strip()
            if cat in categories:
                return cat
            return self.fallback.classify_category(title, html_text, categories)
        except Exception:
            return self.fallback.classify_category(title, html_text, categories)

    def evaluate_rule_compliance(self, rule_name: str, expected_fields: str, declarations: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.active:
            return self.fallback.evaluate_rule_compliance(rule_name, expected_fields, declarations)

        prompt = f"""
        Evaluate if the product satisfies the Legal Metrology rule: "{rule_name}" requiring field(s) "{expected_fields}".
        
        Extracted Declarations:
        {json.dumps(declarations)}

        Return a JSON object with:
        "status": "PASSED" or "FAILED",
        "actual_found": string,
        "confidence": float,
        "ai_reasoning": string
        """
        try:
            res = self.model.generate_content(prompt)
            clean_json = res.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_json)
        except Exception:
            return self.fallback.evaluate_rule_compliance(rule_name, expected_fields, declarations)

    def generate_explanation(self, product_title: str, category: str, passed_rules: List[str], failed_rules: List[str]) -> str:
        if not self.active:
            return self.fallback.generate_explanation(product_title, category, passed_rules, failed_rules)

        prompt = f"""
        Generate a concise, professional audit summary report for product "{product_title}" categorized under "{category}".
        Satisfied Rules ({len(passed_rules)}): {json.dumps(passed_rules)}
        Violated Rules ({len(failed_rules)}): {json.dumps(failed_rules)}

        Explain clearly why the product passes, partially passes, or fails under India's Legal Metrology (Packaged Commodities) Rules, 2011.
        """
        try:
            res = self.model.generate_content(prompt)
            return res.text.strip()
        except Exception:
            return self.fallback.generate_explanation(product_title, category, passed_rules, failed_rules)
