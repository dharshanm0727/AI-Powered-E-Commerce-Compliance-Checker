import json
from typing import Dict, Any, List
import openai

from app.core.config import settings
from app.services.ai.base import BaseAIService
from app.services.ai.providers.mock_provider import MockAIProvider

class OpenAIProvider(BaseAIService):
    def __init__(self):
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.active = True
        else:
            self.active = False
            self.fallback = MockAIProvider()

    def extract_declarations(self, raw_html: str) -> List[Dict[str, Any]]:
        if not self.active:
            return self.fallback.extract_declarations(raw_html)

        prompt = f"Extract Legal Metrology declarations from this HTML as JSON array of objects with key_name, raw_value, normalized_value, confidence_score:\n{raw_html[:5000]}"
        try:
            res = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(res.choices[0].message.content)
        except Exception:
            return self.fallback.extract_declarations(raw_html)

    def classify_category(self, title: str, html_text: str, categories: List[str]) -> str:
        if not self.active:
            return self.fallback.classify_category(title, html_text, categories)

        prompt = f"Classify this product into one of: {json.dumps(categories)}. Title: {title}. Text: {html_text[:1500]}. Respond with category name only."
        try:
            res = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            cat = res.choices[0].message.content.strip()
            return cat if cat in categories else self.fallback.classify_category(title, html_text, categories)
        except Exception:
            return self.fallback.classify_category(title, html_text, categories)

    def evaluate_rule_compliance(self, rule_name: str, expected_fields: str, declarations: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not self.active:
            return self.fallback.evaluate_rule_compliance(rule_name, expected_fields, declarations)

        prompt = f"Evaluate rule '{rule_name}' with fields '{expected_fields}' against declarations: {json.dumps(declarations)}. Return JSON with status, actual_found, confidence, ai_reasoning."
        try:
            res = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return json.loads(res.choices[0].message.content)
        except Exception:
            return self.fallback.evaluate_rule_compliance(rule_name, expected_fields, declarations)

    def generate_explanation(self, product_title: str, category: str, passed_rules: List[str], failed_rules: List[str]) -> str:
        if not self.active:
            return self.fallback.generate_explanation(product_title, category, passed_rules, failed_rules)

        prompt = f"Generate audit summary for product '{product_title}' under '{category}'. Passed: {json.dumps(passed_rules)}, Failed: {json.dumps(failed_rules)} under India's Legal Metrology Rules."
        try:
            res = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return res.choices[0].message.content.strip()
        except Exception:
            return self.fallback.generate_explanation(product_title, category, passed_rules, failed_rules)
