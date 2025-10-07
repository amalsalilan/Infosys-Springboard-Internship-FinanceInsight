#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to verify Unicode character handling in the extraction system.
Tests special characters like ✓, ✗, emojis, non-Latin scripts, smart quotes, etc.
"""

import requests
import json

# Test text with various Unicode characters
test_texts = {
    "special_symbols": {
        "text": "Agreement ✓ approved. Payment: $2,500,000 ✗ pending. Status: 🟢 active.",
        "description": "Extract status markers and payment info with special symbols"
    },
    "smart_quotes": {
        "text": ""Alpha Finance Corp." enters into agreement with 'Beta Holdings' for €2,500,000.",
        "description": "Extract entities with smart quotes and Euro symbol"
    },
    "mixed_scripts": {
        "text": "Contract between 中国银行 (Bank of China) and Deutsche Bank for ¥5,000,000.",
        "description": "Extract entities with Chinese characters and Yen symbol"
    },
    "emojis": {
        "text": "Q4 results 📊: Revenue ⬆️ 25%, Profit 💰 $1.2M, Rating ⭐⭐⭐⭐⭐",
        "description": "Extract financial metrics with emojis"
    },
    "math_symbols": {
        "text": "Investment formula: ROI = (Profit − Cost) × 100 ÷ Cost. Target ≥ 15%.",
        "description": "Extract formula with mathematical symbols"
    },
    "accented_characters": {
        "text": "François Müller from São Paulo invested €100,000 in Zürich.",
        "description": "Extract names and locations with accented characters"
    }
}

# LangExtract service URL
LANGEXTRACT_URL = "http://localhost:8003/extract"

def test_unicode_extraction(test_name, test_data):
    """Test Unicode handling for a specific test case"""
    print(f"\n{'='*60}")
    print(f"Testing: {test_name}")
    print(f"Text: {test_data['text']}")
    print(f"{'='*60}")

    # Prepare request payload
    payload = {
        "text": test_data["text"],
        "prompt_description": test_data["description"],
        "examples": [
            {
                "text": "Alpha Finance Corp. enters into agreement for $2,500,000.",
                "extractions": [
                    {
                        "extraction_class": "party",
                        "extraction_text": "Alpha Finance Corp.",
                        "attributes": {"role": "provider"}
                    },
                    {
                        "extraction_class": "amount",
                        "extraction_text": "$2,500,000",
                        "attributes": {"currency": "USD"}
                    }
                ]
            }
        ],
        "model_id": "gemini-2.0-flash-exp"
    }

    try:
        # Send request
        response = requests.post(
            LANGEXTRACT_URL,
            json=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: {len(result.get('extractions', []))} extractions found")

            for i, extraction in enumerate(result.get('extractions', []), 1):
                print(f"\n  Extraction {i}:")
                print(f"    Class: {extraction['extraction_class']}")
                print(f"    Text: {extraction['extraction_text']}")
                print(f"    Attributes: {extraction.get('attributes', {})}")

            return True
        else:
            print(f"❌ FAILED: HTTP {response.status_code}")
            print(f"Error: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {str(e)}")
        return False


def main():
    """Run all Unicode tests"""
    print("="*60)
    print("Unicode Character Handling Test Suite")
    print("="*60)
    print("\nThis script tests the LangExtract service's ability to handle:")
    print("  • Special symbols (✓, ✗, 🟢)")
    print("  • Smart quotes (" " ' ')")
    print("  • Non-Latin scripts (中文, العربية, etc.)")
    print("  • Emojis (📊, 💰, ⭐)")
    print("  • Mathematical symbols (×, ÷, ≥)")
    print("  • Accented characters (é, ü, ã)")
    print("\nMake sure the LangExtract service is running on port 8003!")
    print("="*60)

    # Test health endpoint first
    print("\n🔍 Checking service health...")
    try:
        health_response = requests.get("http://localhost:8003/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Service is healthy and ready")
        else:
            print(f"⚠️  Service returned: {health_response.status_code}")
    except requests.exceptions.RequestException:
        print("❌ ERROR: Cannot connect to LangExtract service on port 8003")
        print("   Please start the service with: python langextract_service.py")
        return

    # Run all tests
    results = {}
    for test_name, test_data in test_texts.items():
        results[test_name] = test_unicode_extraction(test_name, test_data)

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status}: {test_name}")

    if passed == total:
        print(f"\n🎉 All tests passed! Unicode handling is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the errors above.")


if __name__ == "__main__":
    main()
