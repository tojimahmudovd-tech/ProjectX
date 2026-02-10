"""
AutomationExercise API automated tests (Python)

Covers 10+ API checks based on the published API list:
https://automationexercise.com/api_list

Run:
  python src/api_test_runner.py

This script:
- Creates a unique test user (createAccount)
- Verifies login (valid + invalid + missing params)
- Gets products list, brands list
- Runs negative method checks (405) for endpoints
- Searches products (with and without parameter)
- Gets user detail by email
- Updates account (PUT)
- Deletes account (cleanup)
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional

import requests


BASE_URL = "https://automationexercise.com"
API = f"{BASE_URL}/api"

TIMEOUT = 20


@dataclass
class TestResult:
    name: str
    passed: bool
    details: str = ""


def log(msg: str, fp):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    fp.write(line + "\n")
    fp.flush()


def assert_true(condition: bool, ok: str, fail: str) -> (bool, str):
    return (True, ok) if condition else (False, fail)


def safe_json(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"_raw": resp.text}


def run_test(results: list[TestResult], name: str, fn, fp):
    try:
        passed, details = fn()
        results.append(TestResult(name=name, passed=passed, details=details))
        status = "PASS" if passed else "FAIL"
        log(f"{status} - {name} - {details}", fp)
    except Exception as e:
        results.append(TestResult(name=name, passed=False, details=str(e)))
        log(f"FAIL - {name} - Exception: {e}", fp)


def main():
    os.makedirs("reports", exist_ok=True)
    log_path = os.path.join("reports", f"api_test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    results: list[TestResult] = []

    # Create a unique user for the run
    uniq = uuid.uuid4().hex[:8]
    email = f"fazli_test_{uniq}@example.com"
    password = f"TestPwd_{uniq}!"
    user_payload = {
        "name": "Fazli Test",
        "email": email,
        "password": password,
        "title": "Mr",
        "birth_date": "12",
        "birth_month": "01",
        "birth_year": "2005",
        "firstname": "Fazli",
        "lastname": "Usmonov",
        "company": "BTEC",
        "address1": "Tashkent",
        "address2": "N/A",
        "country": "Uzbekistan",
        "zipcode": "100000",
        "state": "Tashkent",
        "city": "Tashkent",
        "mobile_number": "+998900000000",
    }

    with open(log_path, "w", encoding="utf-8") as fp:
        log("=== AutomationExercise API Testing (Python) ===", fp)
        log(f"Base URL: {BASE_URL}", fp)
        log(f"Test user: {email}", fp)

        session = requests.Session()
        session.headers.update({"User-Agent": "BTEC-API-Tests/1.0"})

        def t01_get_products_list():
            r = session.get(f"{API}/productsList", timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code == 200, "200 OK", f"Expected 200, got {r.status_code}")
            ok2, d2 = assert_true(isinstance(data.get("products"), list), "products[] present", f"products[] missing, keys={list(data.keys())}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t02_products_list_post_not_supported():
            r = session.post(f"{API}/productsList", timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code in (405, 200), f"Status {r.status_code}", f"Unexpected status {r.status_code}")
            # API list states 405 for POST
            ok2, d2 = assert_true(data.get("responseCode") == 405 or "not supported" in str(data).lower(),
                                  "405 not supported", f"Expected not supported, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t03_get_brands_list():
            r = session.get(f"{API}/brandsList", timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code == 200, "200 OK", f"Expected 200, got {r.status_code}")
            ok2, d2 = assert_true(isinstance(data.get("brands"), list), "brands[] present", f"brands[] missing, keys={list(data.keys())}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t04_brands_list_put_not_supported():
            r = session.put(f"{API}/brandsList", timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code in (405, 200), f"Status {r.status_code}", f"Unexpected status {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 405 or "not supported" in str(data).lower(),
                                  "405 not supported", f"Expected not supported, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t05_search_product_valid():
            r = session.post(f"{API}/searchProduct", data={"search_product": "top"}, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code == 200, "200 OK", f"Expected 200, got {r.status_code}")
            ok2, d2 = assert_true(isinstance(data.get("products"), list), "products[] present", f"products[] missing, keys={list(data.keys())}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t06_search_product_missing_param():
            r = session.post(f"{API}/searchProduct", data={}, timeout=TIMEOUT)
            data = safe_json(r)
            # API list expects 400 responseCode
            ok1, d1 = assert_true(r.status_code in (200, 400), f"HTTP {r.status_code}", f"Unexpected http {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 400 or "missing" in str(data).lower(),
                                  "400 missing param", f"Expected missing param error, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t07_create_account():
            r = session.post(f"{API}/createAccount", data=user_payload, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code in (201, 200), f"HTTP {r.status_code}", f"Expected 201/200, got {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") in (201, 200) or "created" in str(data).lower(),
                                  "User created", f"Expected created, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t08_verify_login_valid():
            r = session.post(f"{API}/verifyLogin", data={"email": email, "password": password}, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code == 200, "200 OK", f"Expected 200, got {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 200 or "exists" in str(data).lower(),
                                  "User exists", f"Expected user exists, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t09_verify_login_invalid():
            r = session.post(f"{API}/verifyLogin", data={"email": email, "password": "wrong_password"}, timeout=TIMEOUT)
            data = safe_json(r)
            # API list expects responseCode 404
            ok1, d1 = assert_true(r.status_code in (200, 404), f"HTTP {r.status_code}", f"Unexpected http {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 404 or "not found" in str(data).lower(),
                                  "User not found", f"Expected user not found, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t10_verify_login_missing_email():
            r = session.post(f"{API}/verifyLogin", data={"password": password}, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code in (200, 400), f"HTTP {r.status_code}", f"Unexpected http {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 400 or "missing" in str(data).lower(),
                                  "400 missing param", f"Expected missing param error, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t11_verify_login_delete_not_supported():
            r = session.delete(f"{API}/verifyLogin", timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code in (200, 405), f"HTTP {r.status_code}", f"Unexpected http {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 405 or "not supported" in str(data).lower(),
                                  "405 not supported", f"Expected not supported, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t12_get_user_detail_by_email():
            r = session.get(f"{API}/getUserDetailByEmail", params={"email": email}, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code == 200, "200 OK", f"Expected 200, got {r.status_code}")
            # Response has user details JSON; structure may vary. We'll check responseCode and user
            ok2, d2 = assert_true(data.get("responseCode") == 200 or "user" in data or "email" in str(data).lower(),
                                  "User detail present", f"Expected user detail, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def t13_update_account_put():
            # Update a field to prove PUT works
            updated = dict(user_payload)
            updated["company"] = "BTEC_UPDATED"
            r = session.put(f"{API}/updateAccount", data=updated, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code in (200, 201), f"HTTP {r.status_code}", f"Expected 200, got {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 200 or "updated" in str(data).lower(),
                                  "User updated", f"Expected updated, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        def cleanup_delete_account():
            r = session.delete(f"{API}/deleteAccount", data={"email": email, "password": password}, timeout=TIMEOUT)
            data = safe_json(r)
            ok1, d1 = assert_true(r.status_code == 200, "200 OK", f"Expected 200, got {r.status_code}")
            ok2, d2 = assert_true(data.get("responseCode") == 200 or "deleted" in str(data).lower(),
                                  "Account deleted", f"Expected deleted, got {data}")
            return (ok1 and ok2, f"{d1}; {d2}")

        # Execute tests
        run_test(results, "API 1 - GET /api/productsList returns products", t01_get_products_list, fp)
        run_test(results, "API 2 - POST /api/productsList not supported (negative)", t02_products_list_post_not_supported, fp)
        run_test(results, "API 3 - GET /api/brandsList returns brands", t03_get_brands_list, fp)
        run_test(results, "API 4 - PUT /api/brandsList not supported (negative)", t04_brands_list_put_not_supported, fp)
        run_test(results, "API 5 - POST /api/searchProduct with parameter returns results", t05_search_product_valid, fp)
        run_test(results, "API 6 - POST /api/searchProduct without parameter returns error (negative)", t06_search_product_missing_param, fp)

        run_test(results, "API 11 - POST /api/createAccount creates user", t07_create_account, fp)
        run_test(results, "API 7 - POST /api/verifyLogin valid credentials", t08_verify_login_valid, fp)
        run_test(results, "API 10 - POST /api/verifyLogin invalid credentials (negative)", t09_verify_login_invalid, fp)
        run_test(results, "API 8 - POST /api/verifyLogin missing email (negative)", t10_verify_login_missing_email, fp)
        run_test(results, "API 9 - DELETE /api/verifyLogin not supported (negative)", t11_verify_login_delete_not_supported, fp)
        run_test(results, "API 14 - GET /api/getUserDetailByEmail returns details", t12_get_user_detail_by_email, fp)
        run_test(results, "API 13 - PUT /api/updateAccount updates user", t13_update_account_put, fp)

        # Cleanup
        run_test(results, "API 12 - DELETE /api/deleteAccount deletes user (cleanup)", cleanup_delete_account, fp)

        # Summary
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        log("=== SUMMARY ===", fp)
        log(f"Total: {total} | Passed: {passed} | Failed: {total - passed}", fp)

        # Non-zero exit code if any failed (useful for CI / easy grading)
        if passed != total:
            log("Some tests failed. Check details above.", fp)
            sys.exit(1)

        log("All tests passed ✅", fp)
        sys.exit(0)


if __name__ == "__main__":
    main()
