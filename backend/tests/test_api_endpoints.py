import pytest
from fastapi import status
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule
from app.models.product import Product
from app.models.report import ComplianceReport


def test_categories_api(client, admin_token_headers):
    res_create = client.post("/api/v1/categories/", headers=admin_token_headers, json={
        "name": "Kitchen Appliances",
        "description": "Electrical items for home kitchen"
    })
    assert res_create.status_code == status.HTTP_201_CREATED
    cat_id = res_create.json()["id"]

    res_list = client.get("/api/v1/categories/")
    assert res_list.status_code == status.HTTP_200_OK
    assert len(res_list.json()) >= 1

    res_get = client.get(f"/api/v1/categories/{cat_id}")
    assert res_get.status_code == status.HTTP_200_OK
    assert res_get.json()["name"] == "Kitchen Appliances"

    res_del = client.delete(f"/api/v1/categories/{cat_id}", headers=admin_token_headers)
    assert res_del.status_code == status.HTTP_204_NO_CONTENT


def test_rules_api(client, admin_token_headers):
    res_create = client.post("/api/v1/rules/", headers=admin_token_headers, json={
        "rule_code": "LM-TEST-01",
        "declaration_name": "Country of Origin",
        "mandatory_fields": "Country of Origin, Made in",
        "enforcement_level": "strict"
    })
    assert res_create.status_code == status.HTTP_201_CREATED
    rule_id = res_create.json()["id"]

    res_list = client.get("/api/v1/rules/")
    assert res_list.status_code == status.HTTP_200_OK

    res_del = client.delete(f"/api/v1/rules/{rule_id}", headers=admin_token_headers)
    assert res_del.status_code == status.HTTP_204_NO_CONTENT


def test_compliance_check_api(client, user_token_headers):
    response = client.post("/api/v1/compliance/check", headers=user_token_headers, json={
        "url": "https://www.example.com/item-test-api"
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "id" in data
    assert "overall_status" in data
    assert data["step_reached"] == 10


def test_dashboard_stats_api(client, user_token_headers):
    response = client.get("/api/v1/dashboard/stats", headers=user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_products_scanned" in data
    assert "compliance_rate" in data
    assert "recent_reports" in data


def test_dashboard_audit_logs_admin_only(client, admin_token_headers, user_token_headers):
    res_forbidden = client.get("/api/v1/dashboard/audit-logs", headers=user_token_headers)
    assert res_forbidden.status_code == status.HTTP_403_FORBIDDEN

    res_admin = client.get("/api/v1/dashboard/audit-logs", headers=admin_token_headers)
    assert res_admin.status_code == status.HTTP_200_OK


def test_pdf_and_excel_export_api(client, user_token_headers, sample_product, test_user, db):
    report = ComplianceReport(
        product_id=sample_product.id,
        user_id=test_user.id,
        overall_status="COMPLIANT",
        overall_score=100.0
    )
    db.add(report)
    db.commit()

    res_pdf = client.get(f"/api/v1/reports/{report.id}/export/pdf", headers=user_token_headers)
    assert res_pdf.status_code == status.HTTP_200_OK
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert len(res_pdf.content) > 0

    res_excel = client.get(f"/api/v1/reports/{report.id}/export/excel", headers=user_token_headers)
    assert res_excel.status_code == status.HTTP_200_OK
    assert "spreadsheet" in res_excel.headers["content-type"]
    assert len(res_excel.content) > 0
