from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseAIService(ABC):
    @abstractmethod
    def extract_declarations(self, raw_html: str) -> List[Dict[str, Any]]:
        """Extract mandatory legal metrology declarations from product HTML."""
        pass

    @abstractmethod
    def classify_category(self, title: str, html_text: str, categories: List[str]) -> str:
        """Classify product into one of the available categories using NLP/LLM."""
        pass

    @abstractmethod
    def evaluate_rule_compliance(self, rule_name: str, expected_fields: str, declarations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare extracted declarations against a mandatory legal rule."""
        pass

    @abstractmethod
    def generate_explanation(self, product_title: str, category: str, passed_rules: List[str], failed_rules: List[str]) -> str:
        """Generate human-readable explainable AI summary rationale for compliance audit report."""
        pass
