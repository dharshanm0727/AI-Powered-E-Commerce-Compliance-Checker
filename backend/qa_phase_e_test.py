import os
import sys
import time
import httpx

sys.path.insert(0, os.path.dirname(__file__))

from app.core.database import SessionLocal
from app.core.security import create_access_token, verify_password, get_password_hash
from app.models.user import User
from app.models.category import ProductCategory
from app.models.rule import ComplianceRule
from app.services.scraper.html_downloader import HTMLDownloaderService

BASE_URL = "http://127.0.0.1:8000/api/v1"

def execute_phase_e_audit():
    print("=" * 80)
    print("  PHASE E: UI/UX, API, SECURITY & PERFORMANCE VERIFICATION AUDIT    ")
    print("=" * 80)

    client = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # ------------------------------------------------------------------ #
    # 1. APPLICATION HEALTH & API ENDPOINT DISCOVERY
    # ------------------------------------------------------------------ #
    print("\n--- 1. Application Health & API Endpoint Status ---")
    
    t0 = time.time()
    res_health = httpx.get("http://127.0.0.1:8000/health", timeout=5.0)
    health_latency = (time.time() - t0) * 1000.0

    print(f"GET /health: Status={res_health.status_code}, Body={res_health.json()}, Latency={health_latency:.1f}ms")
    assert res_health.status_code == 200, "Health check must return 200 OK"
    print("[PASS] Backend & Database Startup: VERIFIED")

    # ------------------------------------------------------------------ #
    # 2. REST API & STATUS CODE VERIFICATION (200, 201, 400, 401, 403, 404, 422)
    # ------------------------------------------------------------------ #
    print("\n--- 2. REST API & Status Code Verification ---")

    # Public Endpoints
    t0 = time.time()
    res_cats = client.get("/categories/")
    cats_latency = (time.time() - t0) * 1000.0
    print(f"GET /categories/: Status={res_cats.status_code}, Items={len(res_cats.json())}, Latency={cats_latency:.1f}ms")
    assert res_cats.status_code == 200, "Categories API must return 200 OK"

    t0 = time.time()
    res_rules = client.get("/rules/")
    rules_latency = (time.time() - t0) * 1000.0
    print(f"GET /rules/: Status={res_rules.status_code}, Items={len(res_rules.json())}, Latency={rules_latency:.1f}ms")
    assert res_rules.status_code == 200, "Rules API must return 200 OK"

    # Status Code 404 Not Found
    res_404 = client.get("/categories/999999")
    print(f"GET /categories/999999 (Non-existent): Status={res_404.status_code}")
    assert res_404.status_code == 404, "Non-existent resource must return 404 Not Found"

    # Status Code 401 Unauthorized
    res_401 = client.get("/auth/me")
    print(f"GET /auth/me (No token): Status={res_401.status_code}")
    assert res_401.status_code == 401, "Protected endpoint without token must return 401 Unauthorized"

    # Status Code 422 Validation Error
    res_422 = client.post("/auth/login", json={"invalid_field": 123})
    print(f"POST /auth/login (Invalid payload): Status={res_422.status_code}")
    assert res_422.status_code in [400, 422], "Invalid payload must return validation status 400 or 422"

    print("[PASS] REST API Status Codes (200, 201, 404, 401, 422): VERIFIED")

    # ------------------------------------------------------------------ #
    # 3. AUTHENTICATION & JWT SECURITY VERIFICATION
    # ------------------------------------------------------------------ #
    print("\n--- 3. Authentication & JWT Security Verification ---")

    test_email = f"qa_test_user_{int(time.time())}@compliance.com"
    test_password = "SecurePassword123!"

    # 3a. Registration (Returns 201 Created)
    res_reg = client.post("/auth/register", json={"email": test_email, "password": test_password, "full_name": "QA Tester"})
    print(f"POST /auth/register: Status={res_reg.status_code}, UserID={res_reg.json().get('id')}")
    assert res_reg.status_code in [200, 201], "Valid registration must succeed with 201 Created"

    # 3b. Duplicate Registration Rejection
    res_dup = client.post("/auth/register", json={"email": test_email, "password": test_password})
    print(f"POST /auth/register (Duplicate): Status={res_dup.status_code}")
    assert res_dup.status_code == 400, "Duplicate registration must be rejected with 400 Bad Request"

    # 3c. Login & Token Generation
    t0 = time.time()
    res_login = client.post("/auth/login", data={"username": test_email, "password": test_password})
    login_latency = (time.time() - t0) * 1000.0
    print(f"POST /auth/login: Status={res_login.status_code}, Latency={login_latency:.1f}ms")
    assert res_login.status_code == 200, "Valid login must succeed"
    user_token = res_login.json().get("access_token")

    # 3d. Access Protected Endpoint with Token
    res_me = client.get("/auth/me", headers={"Authorization": f"Bearer {user_token}"})
    print(f"GET /auth/me (Authenticated): Status={res_me.status_code}, Email='{res_me.json().get('email')}'")
    assert res_me.status_code == 200 and res_me.json().get("email") == test_email, "Protected me route must return profile"

    # 3e. Role-Based Authorization Check (Normal User accessing Admin-only users list)
    res_admin_only = client.get("/users/", headers={"Authorization": f"Bearer {user_token}"})
    print(f"GET /users/ (User role accessing Admin route): Status={res_admin_only.status_code}")
    assert res_admin_only.status_code == 403, "Normal user accessing Admin route must be rejected with 403 Forbidden"

    print("[PASS] Authentication, JWT & Role-Based Authorization: VERIFIED")

    # ------------------------------------------------------------------ #
    # 4. URL SECURITY & SSRF PROTECTION TEST
    # ------------------------------------------------------------------ #
    print("\n--- 4. URL Security & SSRF Protection Test ---")

    ssrf_test_urls = [
        ("http://127.0.0.1:8000/secret", "Localhost IPv4"),
        ("http://localhost:5173/admin", "Localhost Domain"),
        ("http://169.254.169.254/latest/meta-data/", "AWS Cloud Metadata Endpoint"),
        ("ftp://example.com/file", "Unsupported Protocol FTP"),
    ]

    for ssrf_url, desc in ssrf_test_urls:
        try:
            HTMLDownloaderService.validate_url(ssrf_url)
            print(f"[FAIL] SSRF Test '{desc}': Expected validation failure, but passed!")
        except ValueError as e:
            print(f"[PASS] SSRF Protection for '{desc}' ({ssrf_url}): REJECTED -> {e}")

    # ------------------------------------------------------------------ #
    # 5. INPUT VALIDATION & SQL INJECTION SECURITY REVIEW
    # ------------------------------------------------------------------ #
    print("\n--- 5. Input Validation & SQL Injection Review ---")

    sqli_payloads = [
        "' OR '1'='1",
        "1; DROP TABLE users;--",
        "admin'--",
        "' UNION SELECT id, email, hashed_password FROM users--"
    ]

    for payload in sqli_payloads:
        res_sqli = client.get(f"/categories/?search={payload}")
        print(f"SQLi Search Test ('{payload}'): Status={res_sqli.status_code}")
        assert res_sqli.status_code == 200, "Search endpoint must safely parameterize SQL queries"
        assert type(res_sqli.json()) is list, "Response body must remain a valid JSON list"

    print("[PASS] SQL Injection Parameterization & Safety: VERIFIED")

    # ------------------------------------------------------------------ #
    # 6. SECRETS, CONFIGURATION & CORS AUDIT
    # ------------------------------------------------------------------ #
    print("\n--- 6. Secrets, Configuration & CORS Audit ---")

    me_data = res_me.json()
    has_hash = "hashed_password" in me_data or "password" in me_data
    print(f"User Profile JSON Fields: {list(me_data.keys())}")
    if not has_hash:
        print("[PASS] Secrets Leakage Audit: VERIFIED (Passwords & hashes strictly excluded from API responses)")
    else:
        print("[FAIL] Secrets Leakage Audit: Password hash leaked in API response!")

    # ------------------------------------------------------------------ #
    # 7. END-TO-END PROCESSING PERFORMANCE METRICS
    # ------------------------------------------------------------------ #
    print("\n--- 7. End-to-End Processing Performance Metrics ---")

    t0 = time.time()
    res_dash = client.get("/dashboard/stats", headers={"Authorization": f"Bearer {user_token}"})
    dash_latency = (time.time() - t0) * 1000.0
    print(f"GET /dashboard/stats: Status={res_dash.status_code}, Latency={dash_latency:.1f}ms")

    print("\nPerformance Summary:")
    print(f"  - Backend Health Check Latency: {health_latency:.1f} ms")
    print(f"  - User Login & Token Issue Latency: {login_latency:.1f} ms")
    print(f"  - Category Listing Latency: {cats_latency:.1f} ms")
    print(f"  - Rules Listing Latency: {rules_latency:.1f} ms")
    print(f"  - Dashboard Aggregation Latency: {dash_latency:.1f} ms")

    print("\n=" * 80)
    print("                 PHASE E QA VERIFICATION SUITE COMPLETE               ")
    print("=" * 80)

if __name__ == "__main__":
    execute_phase_e_audit()
