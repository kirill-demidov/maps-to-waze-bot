#!/usr/bin/env python3
"""
Crash Test Script for Google Maps to Waze Bot
Tests various input types and edge cases
"""

import requests
import time
import json
from typing import List, Dict, Tuple

# Bot configuration
BOT_TOKEN = "7980465326:AAGazpPHHvTB8ArTGRovbA49NgHqqFNErbw"
BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Test cases
TEST_CASES = [
    # Valid Google Maps URLs
    {
        "name": "Short Google Maps URL",
        "input": "https://maps.app.goo.gl/Rr1YmBwYZn1c1rUc6",
        "expected": "coordinates_found"
    },
    {
        "name": "Standard Google Maps URL with coordinates",
        "input": "https://www.google.com/maps?q=40.7128,-74.0060",
        "expected": "coordinates_found"
    },
    {
        "name": "Google Maps URL with @ coordinates",
        "input": "https://www.google.com/maps/@40.7128,-74.0060,15z",
        "expected": "coordinates_found"
    },
    {
        "name": "Google Maps place URL",
        "input": "https://www.google.com/maps/place/Times+Square/@40.7580,-73.9855,17z",
        "expected": "coordinates_found"
    },
    
    # Direct coordinates
    {
        "name": "Simple coordinates",
        "input": "40.7128, -74.0060",
        "expected": "coordinates_found"
    },
    {
        "name": "Coordinates without spaces",
        "input": "40.7128,-74.0060",
        "expected": "coordinates_found"
    },
    {
        "name": "DMS coordinates",
        "input": "40°42'46.8\"N 74°00'21.6\"W",
        "expected": "coordinates_found"
    },
    
    # Edge cases
    {
        "name": "Empty string",
        "input": "",
        "expected": "error"
    },
    {
        "name": "Random text",
        "input": "hello world",
        "expected": "error"
    },
    {
        "name": "Invalid coordinates",
        "input": "999,999",
        "expected": "error"
    },
    {
        "name": "Partial coordinates",
        "input": "40.7128",
        "expected": "error"
    },
    {
        "name": "Very long text",
        "input": "a" * 1000,
        "expected": "error"
    },
    {
        "name": "Special characters",
        "input": "!@#$%^&*()",
        "expected": "error"
    },
    {
        "name": "HTML tags",
        "input": "<script>alert('test')</script>",
        "expected": "error"
    },
    
    # Different URL formats
    {
        "name": "HTTP Google Maps URL",
        "input": "http://maps.google.com/maps?q=40.7128,-74.0060",
        "expected": "coordinates_found"
    },
    {
        "name": "Google Maps with zoom",
        "input": "https://www.google.com/maps/@40.7128,-74.0060,15z/data=!4m2!3m1!1s0x0:0x0",
        "expected": "coordinates_found"
    },
    {
        "name": "Invalid URL",
        "input": "https://invalid-url-test.com",
        "expected": "error"
    },
    
    # Bot commands
    {
        "name": "/start command",
        "input": "/start",
        "expected": "command_response"
    },
    {
        "name": "/help command",
        "input": "/help",
        "expected": "command_response"
    },
    {
        "name": "/menu command",
        "input": "/menu",
        "expected": "command_response"
    },
    {
        "name": "/language command",
        "input": "/language",
        "expected": "command_response"
    },
    {
        "name": "/myid command",
        "input": "/myid",
        "expected": "command_response"
    }
]

def send_message_to_bot(message: str, chat_id: str = "110319269") -> Dict:
    """Send message to bot and get response"""
    try:
        url = f"{BOT_API_URL}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }
        response = requests.post(url, json=data, timeout=30)
        return {
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else None,
            "error": None
        }
    except Exception as e:
        return {
            "status_code": None,
            "response": None,
            "error": str(e)
        }

def analyze_response(response: Dict, test_case: Dict) -> Dict:
    """Analyze bot response and determine if test passed"""
    result = {
        "test_name": test_case["name"],
        "input": test_case["input"],
        "expected": test_case["expected"],
        "actual_result": "unknown",
        "passed": False,
        "response_time": None,
        "error": None,
        "response_text": None
    }
    
    if response["error"]:
        result["error"] = response["error"]
        result["actual_result"] = "error"
        return result
    
    if response["status_code"] != 200:
        result["actual_result"] = "error"
        result["error"] = f"HTTP {response['status_code']}"
        return result
    
    # Check if response contains expected content
    if response["response"] and "text" in response["response"]:
        text = response["response"]["text"]
        result["response_text"] = text
        text_lower = text.lower()
        
        if test_case["expected"] == "coordinates_found":
            if any(keyword in text_lower for keyword in ["координаты", "coordinates", "waze", "✅", "link successfully processed"]):
                result["actual_result"] = "coordinates_found"
                result["passed"] = True
            elif any(keyword in text_lower for keyword in ["❌", "error", "ошибка", "не удалось", "failed"]):
                result["actual_result"] = "error"
            else:
                result["actual_result"] = "unknown"
                
        elif test_case["expected"] == "command_response":
            if any(keyword in text_lower for keyword in ["меню", "menu", "язык", "language", "помощь", "help", "welcome", "добро пожаловать"]):
                result["actual_result"] = "command_response"
                result["passed"] = True
            else:
                result["actual_result"] = "unknown"
                
        elif test_case["expected"] == "error":
            if any(keyword in text_lower for keyword in ["❌", "error", "ошибка", "не удалось", "failed"]):
                result["actual_result"] = "error"
                result["passed"] = True
            else:
                result["actual_result"] = "unknown"
    
    return result

def run_crash_test():
    """Run comprehensive crash test"""
    print("🚀 Starting Crash Test for Google Maps to Waze Bot")
    print("=" * 60)
    
    results = []
    total_tests = len(TEST_CASES)
    passed_tests = 0
    failed_tests = 0
    error_tests = 0
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n[{i}/{total_tests}] Testing: {test_case['name']}")
        print(f"Input: {test_case['input']}")
        
        # Send message to bot
        start_time = time.time()
        response = send_message_to_bot(test_case["input"])
        response_time = time.time() - start_time
        
        # Analyze response
        result = analyze_response(response, test_case)
        result["response_time"] = response_time
        
        # Update counters
        if result["passed"]:
            passed_tests += 1
            status = "✅ PASS"
        elif result["error"]:
            error_tests += 1
            status = "❌ ERROR"
        else:
            failed_tests += 1
            status = "⚠️ FAIL"
        
        print(f"Status: {status}")
        print(f"Response Time: {response_time:.2f}s")
        print(f"Expected: {test_case['expected']}, Actual: {result['actual_result']}")
        
        if result["response_text"]:
            print(f"Bot Response: {result['response_text'][:100]}...")
        
        if result["error"]:
            print(f"Error: {result['error']}")
        
        results.append(result)
        
        # Small delay between tests
        time.sleep(1)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 CRASH TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"⚠️ Failed: {failed_tests}")
    print(f"❌ Errors: {error_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    print("-" * 60)
    
    for result in results:
        status = "✅" if result["passed"] else "❌" if result["error"] else "⚠️"
        print(f"{status} {result['test_name']}")
        print(f"   Input: {result['input']}")
        print(f"   Expected: {result['expected']}, Actual: {result['actual_result']}")
        print(f"   Response Time: {result['response_time']:.2f}s")
        if result["error"]:
            print(f"   Error: {result['error']}")
        print()
    
    # Save results to file
    with open("crash_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": results
        }, f, indent=2, ensure_ascii=False)
    
    print(f"📄 Results saved to: crash_test_results.json")
    
    return results

if __name__ == "__main__":
    run_crash_test() 