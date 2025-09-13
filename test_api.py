#!/usr/bin/env python3
"""
API Test Script for Bulk Pickup Service
Tests all major API endpoints to ensure functionality
"""

import requests
import json
import sys
from datetime import datetime, date, timedelta

BASE_URL = "http://localhost:5000/api"

def test_endpoint(method, endpoint, data=None, params=None, expected_status=200):
    """Test a single API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, params=params)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, params=params)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, params=params)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, params=params)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        if response.status_code == expected_status:
            print(f"✅ {method} {endpoint} - Status: {response.status_code}")
            try:
                response_data = response.json()
                if response_data.get('success'):
                    print(f"   Response: Success")
                else:
                    print(f"   Response: {response_data.get('error', {}).get('message', 'Unknown error')}")
            except:
                print(f"   Response: Non-JSON response")
            return True
        else:
            print(f"❌ {method} {endpoint} - Expected: {expected_status}, Got: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            except:
                print(f"   Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {method} {endpoint} - Connection failed (server not running?)")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint} - Exception: {str(e)}")
        return False

def run_tests():
    """Run all API tests"""
    print("🚀 Starting API Tests for Bulk Pickup Service")
    print("=" * 50)
    
    tests_passed = 0
    tests_total = 0
    
    # Test Schedule API
    print("\n📅 Testing Schedule API")
    print("-" * 30)
    
    tests_total += 1
    if test_endpoint('GET', '/schedules/lookup', params={'zipCode': '62701'}):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('GET', '/schedules/schedule_123/events', params={'limit': 5}):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('GET', '/schedules'):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('POST', '/schedules/subscriptions', data={
        'scheduleId': 'schedule_123',
        'addressId': 'addr_123',
        'notificationPreferences': {
            'email': True,
            'push': True,
            'sms': False,
            'advance_days': [1, 7]
        }
    }, expected_status=201):
        tests_passed += 1
    
    # Test Business API
    print("\n🏢 Testing Business API")
    print("-" * 30)
    
    tests_total += 1
    if test_endpoint('GET', '/businesses/search', params={
        'lat': 39.7817,
        'lng': -89.6501,
        'radius': 10
    }):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('GET', '/businesses/business_123'):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('POST', '/businesses/profile', data={
        'businessName': 'Test Cleanup Service',
        'businessType': 'junk_removal',
        'description': 'Test business for API testing',
        'serviceRadiusMiles': 25
    }):
        tests_passed += 1
    
    # Test Booking API
    print("\n📋 Testing Booking API")
    print("-" * 30)
    
    tests_total += 1
    if test_endpoint('POST', '/bookings/requests', data={
        'addressId': 'addr_123',
        'serviceCategory': 'junk_removal',
        'description': 'Need to remove old furniture',
        'preferredDate': (date.today() + timedelta(days=7)).isoformat(),
        'preferredTimeStart': '10:00',
        'estimatedBudget': 200.00
    }, expected_status=201):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('GET', '/bookings/requests/request_123/quotes'):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('GET', '/bookings/history', params={'limit': 10}):
        tests_passed += 1
    
    tests_total += 1
    if test_endpoint('GET', '/bookings/booking_123'):
        tests_passed += 1
    
    # Test User API (from template)
    print("\n👤 Testing User API")
    print("-" * 30)
    
    tests_total += 1
    if test_endpoint('GET', '/users'):
        tests_passed += 1
    
    # Print results
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{tests_total} tests passed")
    
    if tests_passed == tests_total:
        print("🎉 All tests passed! API is working correctly.")
        return True
    else:
        print(f"⚠️  {tests_total - tests_passed} tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

