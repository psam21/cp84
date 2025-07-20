#!/usr/bin/env python3
"""
Transaction Fee API Test Script

Tests all the transaction fee APIs listed in docs/transaction_fee_apis.md
to verify they're working and returning valid data.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

def test_bitcoin_fees() -> Dict[str, Any]:
    """Test Bitcoin fee estimation from mempool.space"""
    print("🔍 Testing Bitcoin (BTC) Fee API...")
    
    try:
        url = "https://mempool.space/api/v1/fees/recommended"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BTC API Success: {response.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            # Validate expected fields
            required_fields = ['fastestFee', 'halfHourFee', 'hourFee', 'economyFee', 'minimumFee']
            missing_fields = [field for field in required_fields if field not in data]
            
            if missing_fields:
                print(f"⚠️  Missing fields: {missing_fields}")
                return {"status": "partial", "data": data, "missing_fields": missing_fields}
            
            # Validate data types and ranges
            for field in required_fields:
                if not isinstance(data[field], (int, float)) or data[field] < 0:
                    print(f"⚠️  Invalid {field}: {data[field]}")
                    return {"status": "invalid", "data": data, "invalid_field": field}
            
            print(f"   Fastest Fee: {data['fastestFee']} sats/vB")
            print(f"   Half Hour Fee: {data['halfHourFee']} sats/vB")
            print(f"   Hour Fee: {data['hourFee']} sats/vB")
            print(f"   Economy Fee: {data['economyFee']} sats/vB")
            
            return {"status": "success", "data": data}
        else:
            print(f"❌ BTC API Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"status": "failed", "status_code": response.status_code, "error": response.text}
            
    except requests.RequestException as e:
        print(f"❌ BTC API Error: {str(e)}")
        return {"status": "error", "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"❌ BTC API JSON Error: {str(e)}")
        return {"status": "json_error", "error": str(e)}

def test_ethereum_gas() -> Dict[str, Any]:
    """Test Ethereum gas price from Etherscan"""
    print("\n🔍 Testing Ethereum (ETH) Gas API...")
    
    try:
        url = "https://api.etherscan.io/api?module=gastracker&action=gasoracle"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ ETH API Success: {response.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            # Check for successful response
            if data.get("status") == "1" and "result" in data:
                result = data["result"]
                required_fields = ['SafeGasPrice', 'ProposeGasPrice', 'FastGasPrice']
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"⚠️  Missing fields: {missing_fields}")
                    return {"status": "partial", "data": data, "missing_fields": missing_fields}
                
                print(f"   Safe Gas Price: {result['SafeGasPrice']} Gwei")
                print(f"   Propose Gas Price: {result['ProposeGasPrice']} Gwei")
                print(f"   Fast Gas Price: {result['FastGasPrice']} Gwei")
                
                return {"status": "success", "data": data}
            else:
                print(f"⚠️  API returned error status: {data}")
                return {"status": "api_error", "data": data}
        else:
            print(f"❌ ETH API Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"status": "failed", "status_code": response.status_code, "error": response.text}
            
    except requests.RequestException as e:
        print(f"❌ ETH API Error: {str(e)}")
        return {"status": "error", "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"❌ ETH API JSON Error: {str(e)}")
        return {"status": "json_error", "error": str(e)}

def test_bnb_gas_price(endpoint: str) -> Dict[str, Any]:
    """Test BNB Smart Chain gas price via JSON-RPC"""
    print(f"\n🔍 Testing BNB Smart Chain Gas API ({endpoint})...")
    
    try:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_gasPrice",
            "params": []
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ BNB API Success: {response.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            if "result" in data and data["result"]:
                gas_price_wei = data["result"]
                # Convert from Wei to Gwei (1 Gwei = 10^9 Wei)
                gas_price_gwei = int(gas_price_wei, 16) / 1e9
                
                print(f"   Gas Price: {gas_price_wei} Wei")
                print(f"   Gas Price: {gas_price_gwei:.2f} Gwei")
                
                return {"status": "success", "data": data, "gas_price_gwei": gas_price_gwei}
            else:
                print(f"⚠️  No result in response: {data}")
                return {"status": "no_result", "data": data}
        else:
            print(f"❌ BNB API Failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return {"status": "failed", "status_code": response.status_code, "error": response.text}
            
    except requests.RequestException as e:
        print(f"❌ BNB API Error: {str(e)}")
        return {"status": "error", "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"❌ BNB API JSON Error: {str(e)}")
        return {"status": "json_error", "error": str(e)}
    except ValueError as e:
        print(f"❌ BNB API Value Error: {str(e)}")
        return {"status": "value_error", "error": str(e)}

def test_all_apis() -> Dict[str, Any]:
    """Test all transaction fee APIs and return comprehensive results"""
    print("🚀 Starting Transaction Fee API Tests...\n")
    
    start_time = time.time()
    results = {}
    
    # Test Bitcoin fees
    results["bitcoin"] = test_bitcoin_fees()
    
    # Test Ethereum gas
    results["ethereum"] = test_ethereum_gas()
    
    # Test BNB gas - primary endpoint
    results["bnb_binance"] = test_bnb_gas_price("https://bsc-dataseed.binance.org")
    
    # Test BNB gas - alternative endpoint
    results["bnb_drpc"] = test_bnb_gas_price("https://bsc.drpc.org")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Summary
    print(f"\n📊 Test Summary (completed in {total_time:.2f}s)")
    print("=" * 50)
    
    successful_tests = 0
    total_tests = len(results)
    
    for api_name, result in results.items():
        status = result.get("status", "unknown")
        if status == "success":
            print(f"✅ {api_name.upper()}: Working")
            successful_tests += 1
        elif status == "partial":
            print(f"⚠️  {api_name.upper()}: Partial (missing fields)")
        elif status == "api_error":
            print(f"⚠️  {api_name.upper()}: API Error")
        else:
            print(f"❌ {api_name.upper()}: Failed ({status})")
    
    print(f"\nSuccess Rate: {successful_tests}/{total_tests} ({(successful_tests/total_tests)*100:.1f}%)")
    
    results["summary"] = {
        "total_tests": total_tests,
        "successful_tests": successful_tests,
        "success_rate": (successful_tests/total_tests)*100,
        "total_time": total_time
    }
    
    return results

def main():
    """Main function to run all tests"""
    try:
        results = test_all_apis()
        
        # Optional: Save results to file
        with open("transaction_fee_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\n💾 Results saved to: transaction_fee_test_results.json")
        
        # Return appropriate exit code
        summary = results.get("summary", {})
        if summary.get("success_rate", 0) == 100:
            print("🎉 All APIs are working perfectly!")
            return 0
        elif summary.get("success_rate", 0) >= 75:
            print("⚠️  Most APIs are working (some issues detected)")
            return 1
        else:
            print("❌ Multiple API failures detected")
            return 2
            
    except Exception as e:
        print(f"💥 Unexpected error: {str(e)}")
        return 3

if __name__ == "__main__":
    exit(main())
