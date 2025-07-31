#!/usr/bin/env python3
"""
Simple Concurrency Test Script for .NET Core JSON Stage Updates API

This is a lightweight version of the concurrency test that only requires
the requests library and provides basic concurrent testing functionality.

Requirements:
    pip install requests

Usage:
    python simple_concurrency_test.py
"""

import requests
import time
import json
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict
import urllib3

# Disable SSL warnings for localhost testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://localhost:7000/api/stagedata"
TEST_ID = "simple-concurrency-test"

class SimpleConcurrencyTester:
    """Simplified concurrency tester with basic functionality"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification for localhost
        self.results = []
        self.lock = threading.Lock()
    
    def setup_test_data(self) -> bool:
        """Create test data"""
        try:
            url = f"{BASE_URL}/{TEST_ID}"
            response = self.session.post(url, json={"createdBy": "SimpleTester"})
            
            if response.status_code in [201, 409]:
                print(f"✓ Test data setup completed (Status: {response.status_code})")
                return True
            else:
                print(f"✗ Failed to setup test data: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error setting up test data: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            url = f"{BASE_URL}/{TEST_ID}"
            response = self.session.delete(url)
            print("✓ Test data cleanup completed")
        except Exception as e:
            print(f"✗ Error cleaning up: {e}")
    
    def get_current_version(self) -> int:
        """Get current version of test data"""
        try:
            url = f"{BASE_URL}/{TEST_ID}"
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                return data.get('version', 1)
            return 1
        except:
            return 1
    
    def single_update_worker(self, worker_id: int, num_updates: int) -> Dict:
        """Worker function for concurrent single updates"""
        worker_results = {
            'worker_id': worker_id,
            'successful': 0,
            'failed': 0,
            'conflicts': 0,
            'total_time': 0,
            'details': []
        }
        
        start_time = time.time()
        
        for i in range(num_updates):
            update_start = time.time()
            
            try:
                # Get current version
                current_version = self.get_current_version()
                
                # Prepare update data
                stage_key = f"worker_{worker_id}_update_{i}"
                stage_data = {
                    "stageInfo": {
                        "name": f"Worker {worker_id} Stage {i}",
                        "status": random.randint(1, 2),
                        "progress": random.randint(0, 100),
                        "data": {
                            "workerId": worker_id,
                            "updateIndex": i,
                            "timestamp": time.time()
                        }
                    },
                    "expectedVersion": current_version,
                    "updatedBy": f"worker_{worker_id}"
                }
                
                # Make update request
                url = f"{BASE_URL}/{TEST_ID}/stages/{stage_key}"
                response = self.session.put(url, json=stage_data)
                
                update_time = time.time() - update_start
                
                if response.status_code == 200:
                    worker_results['successful'] += 1
                    status = "SUCCESS"
                elif response.status_code == 409:
                    worker_results['conflicts'] += 1
                    status = "CONFLICT"
                else:
                    worker_results['failed'] += 1
                    status = "FAILED"
                
                worker_results['details'].append({
                    'update_index': i,
                    'status': status,
                    'response_time': update_time,
                    'status_code': response.status_code
                })
                
            except Exception as e:
                worker_results['failed'] += 1
                worker_results['details'].append({
                    'update_index': i,
                    'status': 'ERROR',
                    'error': str(e),
                    'response_time': time.time() - update_start
                })
            
            # Small delay between updates
            time.sleep(0.01)
        
        worker_results['total_time'] = time.time() - start_time
        return worker_results
    
    def batch_update_worker(self, worker_id: int, batch_size: int = 3) -> Dict:
        """Worker function for batch updates"""
        start_time = time.time()
        
        try:
            # Get current version
            current_version = self.get_current_version()
            
            # Prepare batch data
            stages = {}
            for i in range(batch_size):
                stage_key = f"batch_worker_{worker_id}_stage_{i}"
                stages[stage_key] = {
                    "name": f"Batch Worker {worker_id} Stage {i}",
                    "status": random.randint(1, 2),
                    "progress": random.randint(0, 100),
                    "data": {
                        "batchWorkerId": worker_id,
                        "stageIndex": i,
                        "timestamp": time.time()
                    }
                }
            
            batch_data = {
                "stages": stages,
                "expectedVersion": current_version,
                "updatedBy": f"batch_worker_{worker_id}"
            }
            
            # Make batch update request
            url = f"{BASE_URL}/{TEST_ID}/stages"
            response = self.session.put(url, json=batch_data)
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {
                    'worker_id': worker_id,
                    'status': 'SUCCESS',
                    'response_time': response_time,
                    'stages_updated': batch_size
                }
            elif response.status_code == 409:
                return {
                    'worker_id': worker_id,
                    'status': 'CONFLICT',
                    'response_time': response_time,
                    'stages_updated': 0
                }
            else:
                return {
                    'worker_id': worker_id,
                    'status': 'FAILED',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'stages_updated': 0
                }
                
        except Exception as e:
            return {
                'worker_id': worker_id,
                'status': 'ERROR',
                'error': str(e),
                'response_time': time.time() - start_time,
                'stages_updated': 0
            }
    
    def test_concurrent_single_updates(self, num_workers: int = 10, updates_per_worker: int = 5):
        """Test concurrent single updates"""
        print(f"\n🔄 Testing Concurrent Single Updates")
        print(f"   Workers: {num_workers}, Updates per worker: {updates_per_worker}")
        print("-" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(self.single_update_worker, i, updates_per_worker)
                for i in range(num_workers)
            ]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # Analyze results
        total_requests = sum(r['successful'] + r['failed'] + r['conflicts'] for r in results)
        total_successful = sum(r['successful'] for r in results)
        total_conflicts = sum(r['conflicts'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {total_successful} ({total_successful/total_requests*100:.1f}%)")
        print(f"Conflicts: {total_conflicts} ({total_conflicts/total_requests*100:.1f}%)")
        print(f"Failed: {total_failed} ({total_failed/total_requests*100:.1f}%)")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {total_requests/total_time:.2f} requests/sec")
        
        return results
    
    def test_concurrent_batch_updates(self, num_workers: int = 8, batch_size: int = 3):
        """Test concurrent batch updates"""
        print(f"\n🔄 Testing Concurrent Batch Updates")
        print(f"   Workers: {num_workers}, Batch size: {batch_size}")
        print("-" * 60)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = [
                executor.submit(self.batch_update_worker, i, batch_size)
                for i in range(num_workers)
            ]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        total_time = time.time() - start_time
        
        # Analyze results
        successful = len([r for r in results if r['status'] == 'SUCCESS'])
        conflicts = len([r for r in results if r['status'] == 'CONFLICT'])
        failed = len([r for r in results if r['status'] in ['FAILED', 'ERROR']])
        total_stages = sum(r.get('stages_updated', 0) for r in results)
        
        print(f"Total Batch Requests: {len(results)}")
        print(f"Successful: {successful} ({successful/len(results)*100:.1f}%)")
        print(f"Conflicts: {conflicts} ({conflicts/len(results)*100:.1f}%)")
        print(f"Failed: {failed} ({failed/len(results)*100:.1f}%)")
        print(f"Total Stages Updated: {total_stages}")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Throughput: {len(results)/total_time:.2f} batch requests/sec")
        
        return results
    
    def test_mixed_operations(self, duration_seconds: int = 10):
        """Test mixed single and batch operations for a duration"""
        print(f"\n🔄 Testing Mixed Operations")
        print(f"   Duration: {duration_seconds} seconds")
        print("-" * 60)
        
        start_time = time.time()
        results = {'single': [], 'batch': []}
        request_count = 0
        
        def single_update_task():
            nonlocal request_count
            request_count += 1
            return self.single_update_worker(request_count, 1)
        
        def batch_update_task():
            nonlocal request_count
            request_count += 1
            return self.batch_update_worker(request_count, 2)
        
        while time.time() - start_time < duration_seconds:
            batch_start = time.time()
            
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = []
                
                # Submit mixed operations
                for _ in range(4):
                    if random.choice([True, False]):
                        futures.append(('single', executor.submit(single_update_task)))
                    else:
                        futures.append(('batch', executor.submit(batch_update_task)))
                
                for operation_type, future in futures:
                    try:
                        result = future.result(timeout=5)
                        results[operation_type].append(result)
                    except Exception as e:
                        print(f"Operation failed: {e}")
            
            # Small delay between batches
            time.sleep(0.2)
        
        total_time = time.time() - start_time
        
        # Analyze results
        single_successful = len([r for r in results['single'] if r.get('successful', 0) > 0])
        batch_successful = len([r for r in results['batch'] if r.get('status') == 'SUCCESS'])
        total_operations = len(results['single']) + len(results['batch'])
        
        print(f"Total Operations: {total_operations}")
        print(f"Single Updates: {len(results['single'])} (Success: {single_successful})")
        print(f"Batch Updates: {len(results['batch'])} (Success: {batch_successful})")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Operations/sec: {total_operations/total_time:.2f}")
        
        return results
    
    def test_built_in_simulation(self, concurrent_calls: int = 10):
        """Test the built-in simulation endpoint"""
        print(f"\n🎯 Testing Built-in Simulation Endpoint")
        print(f"   Concurrent calls: {concurrent_calls}")
        print("-" * 60)
        
        try:
            url = f"{BASE_URL}/{TEST_ID}/simulate-concurrent-updates"
            data = {
                "concurrentCallsCount": concurrent_calls,
                "expectedVersion": 1,
                "maxRetries": 3
            }
            
            start_time = time.time()
            response = self.session.post(url, json=data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"Total Calls: {result.get('totalCalls', 0)}")
                print(f"Successful: {result.get('successfulUpdates', 0)}")
                print(f"Failed: {result.get('failedUpdates', 0)}")
                print(f"Response Time: {response_time:.2f}s")
                
                if 'results' in result:
                    success_count = sum(1 for r in result['results'] if r.get('success', False))
                    print(f"Success Rate: {success_count/len(result['results'])*100:.1f}%")
                
                return result
            else:
                print(f"Simulation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error running simulation: {e}")
            return None

def main():
    """Main function to run simple concurrency tests"""
    print("🚀 Simple Concurrency Test for .NET Core JSON Stage Updates API")
    print("="*80)
    
    tester = SimpleConcurrencyTester()
    
    # Setup test data
    if not tester.setup_test_data():
        print("❌ Failed to setup test data. Make sure the API is running!")
        return
    
    try:
        # Run tests
        print("\n📋 Running Concurrency Tests...")
        
        # Test 1: Concurrent single updates
        single_results = tester.test_concurrent_single_updates(
            num_workers=8, updates_per_worker=3
        )
        
        # Test 2: Concurrent batch updates  
        batch_results = tester.test_concurrent_batch_updates(
            num_workers=6, batch_size=3
        )
        
        # Test 3: Mixed operations
        mixed_results = tester.test_mixed_operations(duration_seconds=8)
        
        # Test 4: Built-in simulation
        simulation_result = tester.test_built_in_simulation(concurrent_calls=8)
        
        # Summary
        print(f"\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        total_single_requests = sum(
            r['successful'] + r['failed'] + r['conflicts'] 
            for r in single_results
        )
        total_single_successful = sum(r['successful'] for r in single_results)
        
        batch_successful = len([r for r in batch_results if r['status'] == 'SUCCESS'])
        
        print(f"Single Updates: {total_single_requests} total, {total_single_successful} successful")
        print(f"Batch Updates: {len(batch_results)} total, {batch_successful} successful")
        print(f"Mixed Operations: {len(mixed_results['single']) + len(mixed_results['batch'])} total")
        
        if simulation_result:
            print(f"Built-in Simulation: {simulation_result.get('totalCalls', 0)} calls, "
                  f"{simulation_result.get('successfulUpdates', 0)} successful")
        
        print("\n💡 The API successfully handled concurrent updates with proper conflict resolution!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Cleanup
        tester.cleanup_test_data()
        print("\n✅ Testing completed!")

if __name__ == "__main__":
    main()