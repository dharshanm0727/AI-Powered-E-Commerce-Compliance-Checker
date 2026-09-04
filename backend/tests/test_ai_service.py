import pytest
from app.services.ai.factory import get_ai_service
from app.services.ai.providers.mock_provider import MockAIProvider
from app.services.ai.providers.gemini_provider import GeminiAIProvider
from app.services.ai.providers.openai_provider import OpenAIProvider


def test_ai_factory_default():
    service = get_ai_service()
    assert service is not None


def test_mock_ai_service_extract_declarations():
    service = MockAIProvider()
    html_sample = """
    <div>
        <h1>Samsung Galaxy S24 Ultra</h1>
        <p>Manufacturer: Samsung Electronics India Pvt Ltd</p>
        <p>Country of Origin: India</p>
        <p>MRP: Rs. 1,29,999 (Inclusive of all taxes)</p>
        <p>Net Quantity: 1 Unit</p>
        <p>Part Number: SM-S928BZKGINU</p>
    </div>
    """
    declarations = service.extract_declarations(html_sample)
    assert isinstance(declarations, list)
    assert len(declarations) > 0

    key_names = [d["key_name"].lower() for d in declarations]
    assert any("mrp" in k or "price" in k for k in key_names)
    assert any("manufacturer" in k for k in key_names)


def test_mock_ai_service_classify_category():
    service = MockAIProvider()
    categories = ["Electronics", "Food Products", "Cosmetics", "Clothing"]

    cat1 = service.classify_category("Samsung 55 Inch 4K Smart TV", "Electrical appliance", categories)
    assert cat1 in categories

    cat2 = service.classify_category("Basmati Rice 5kg Pack", "Food grain", categories)
    assert cat2 in categories


def test_mock_ai_service_evaluate_rule():
    service = MockAIProvider()
    declarations = [
        {"key_name": "Part Number", "normalized_value": "P/N 12345", "confidence_score": 0.95},
        {"key_name": "MRP", "normalized_value": "Rs. 499", "confidence_score": 0.9}
    ]

    eval_pass = service.evaluate_rule_compliance(
        rule_name="Part Number",
        expected_fields="Part Number, Part No, P/N",
        declarations=declarations
    )
    assert eval_pass["status"] in ["PASSED", "FAILED"]
    assert "actual_found" in eval_pass


def test_mock_ai_service_generate_explanation():
    service = MockAIProvider()
    summary = service.generate_explanation(
        product_title="Sony Wireless Headphones",
        category="Electronics",
        passed_rules=["Part Number", "Manufacturer", "MRP"],
        failed_rules=["Consumer Care"]
    )
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert "Sony Wireless Headphones" in summary
