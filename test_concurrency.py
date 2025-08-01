#!/usr/bin/env python3
"""
Concurrency Test Script for .NET Core JSON Stage Updates API

This script tests various concurrent update scenarios to validate the 
thread-safety and performance of the concurrent JSON update service.

Requirements:
    pip install requests aiohttp asyncio matplotlib pandas

Usage:
    python test_concurrency.py
"""

import asyncio
import aiohttp
import requests
import time
import json
import random
import statistics
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Configuration
BASE_URL = "https://localhost:7000/api/stagedata"
TEST_ID = "concurrency-test-001"
MAX_CONCURRENT_REQUESTS = 50
TEST_DURATION_SECONDS = 30

# Disable SSL warnings for localhost testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@dataclass
class TestResult:
    """Represents the result of a single test operation"""
    operation: str
    success: bool
    response_time: float
    status_code: int
    error_message: Optional[str] = None
    attempt_number: int = 1
    version_conflict: bool = False

@dataclass
class StageInfo:
    """Represents stage information for updates"""
    name: str
    status: int  # 0=Pending, 1=InProgress, 2=Completed, 3=Failed, 4=Cancelled
    progress: int
    data: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}

@dataclass
class StageUpdateRequest:
    """Request model for stage updates"""
    stageInfo: StageInfo
    expectedVersion: int
    updatedBy: str

class ConcurrencyTester:
    """Main class for testing concurrent API operations"""
    
    def __init__(self, base_url: str = BASE_URL, verify_ssl: bool = False):
        self.base_url = base_url
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        self.session.verify = verify_ssl
        self.results: List[TestResult] = []
        
    def setup_test_data(self) -> bool:
        """Initialize test data by creating a stage data entry"""
        try:
            url = f"{self.base_url}/{TEST_ID}"
            response = self.session.post(url, json={"createdBy": "ConcurrencyTester"})
            
            if response.status_code in [201, 409]:  # Created or already exists
                print(f"✓ Test data setup completed (Status: {response.status_code})")
                return True
            else:
                print(f"✗ Failed to setup test data: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ Error setting up test data: {e}")
            return False
    
    def cleanup_test_data(self) -> bool:
        """Clean up test data after testing"""
        try:
            url = f"{self.base_url}/{TEST_ID}"
            response = self.session.delete(url)
            
            if response.status_code in [204, 404]:  # Deleted or not found
                print(f"✓ Test data cleanup completed")
                return True
            else:
                print(f"✗ Failed to cleanup test data: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error cleaning up test data: {e}")
            return False
    
    def get_current_version(self) -> Optional[int]:
        """Get the current version of the test data"""
        try:
            url = f"{self.base_url}/{TEST_ID}"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('version', 1)
            return None
            
        except Exception as e:
            print(f"Error getting current version: {e}")
            return None
    
    def single_update_test(self, stage_key: str, user_id: str, expected_version: int = None) -> TestResult:
        """Test a single stage update operation"""
        start_time = time.time()
        
        try:
            # Get current version if not provided
            if expected_version is None:
                expected_version = self.get_current_version() or 1
            
            stage_info = StageInfo(
                name=f"Test Stage {stage_key}",
                status=random.randint(1, 2),  # InProgress or Completed
                progress=random.randint(0, 100),
                data={"testId": user_id, "timestamp": time.time()}
            )
            
            update_request = StageUpdateRequest(
                stageInfo=stage_info,
                expectedVersion=expected_version,
                updatedBy=user_id
            )
            
            url = f"{self.base_url}/{TEST_ID}/stages/{stage_key}"
            response = self.session.put(url, json=asdict(update_request))
            
            response_time = time.time() - start_time
            
            return TestResult(
                operation="single_update",
                success=response.status_code == 200,
                response_time=response_time,
                status_code=response.status_code,
                error_message=response.text if response.status_code != 200 else None,
                version_conflict=response.status_code == 409
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                operation="single_update",
                success=False,
                response_time=response_time,
                status_code=0,
                error_message=str(e)
            )
    
    def batch_update_test(self, user_id: str, stage_count: int = 3) -> TestResult:
        """Test batch update of multiple stages"""
        start_time = time.time()
        
        try:
            # Get current version
            expected_version = self.get_current_version() or 1
            
            stages = {}
            for i in range(stage_count):
                stage_key = f"batch_stage_{i}_{user_id}"
                stages[stage_key] = asdict(StageInfo(
                    name=f"Batch Stage {i}",
                    status=random.randint(1, 2),
                    progress=random.randint(0, 100),
                    data={"batchId": user_id, "stageIndex": i}
                ))
            
            request_data = {
                "stages": stages,
                "expectedVersion": expected_version,
                "updatedBy": user_id
            }
            
            url = f"{self.base_url}/{TEST_ID}/stages"
            response = self.session.put(url, json=request_data)
            
            response_time = time.time() - start_time
            
            return TestResult(
                operation="batch_update",
                success=response.status_code == 200,
                response_time=response_time,
                status_code=response.status_code,
                error_message=response.text if response.status_code != 200 else None,
                version_conflict=response.status_code == 409
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                operation="batch_update",
                success=False,
                response_time=response_time,
                status_code=0,
                error_message=str(e)
            )
    
    def concurrent_single_updates_test(self, num_threads: int = 10, updates_per_thread: int = 5) -> List[TestResult]:
        """Test concurrent single updates using threading"""
        print(f"🔄 Running concurrent single updates test ({num_threads} threads, {updates_per_thread} updates each)")
        
        results = []
        
        def worker(thread_id: int) -> List[TestResult]:
            thread_results = []
            for i in range(updates_per_thread):
                stage_key = f"thread_{thread_id}_update_{i}"
                user_id = f"user_{thread_id}"
                result = self.single_update_test(stage_key, user_id)
                result.attempt_number = i + 1
                thread_results.append(result)
                time.sleep(0.01)  # Small delay between updates
            return thread_results
        
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker, i) for i in range(num_threads)]
            
            for future in as_completed(futures):
                try:
                    thread_results = future.result()
                    results.extend(thread_results)
                except Exception as e:
                    print(f"Thread execution error: {e}")
        
        return results
    
    async def async_single_update(self, session: aiohttp.ClientSession, stage_key: str, user_id: str) -> TestResult:
        """Async version of single update test"""
        start_time = time.time()
        
        try:
            # Get current version
            async with session.get(f"{self.base_url}/{TEST_ID}") as version_response:
                if version_response.status == 200:
                    version_data = await version_response.json()
                    expected_version = version_data.get('version', 1)
                else:
                    expected_version = 1
            
            stage_info = StageInfo(
                name=f"Async Stage {stage_key}",
                status=random.randint(1, 2),
                progress=random.randint(0, 100),
                data={"asyncTestId": user_id, "timestamp": time.time()}
            )
            
            update_request = StageUpdateRequest(
                stageInfo=stage_info,
                expectedVersion=expected_version,
                updatedBy=user_id
            )
            
            url = f"{self.base_url}/{TEST_ID}/stages/{stage_key}"
            async with session.put(url, json=asdict(update_request)) as response:
                response_time = time.time() - start_time
                response_text = await response.text()
                
                return TestResult(
                    operation="async_single_update",
                    success=response.status == 200,
                    response_time=response_time,
                    status_code=response.status,
                    error_message=response_text if response.status != 200 else None,
                    version_conflict=response.status == 409
                )
                
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                operation="async_single_update",
                success=False,
                response_time=response_time,
                status_code=0,
                error_message=str(e)
            )
    
    async def concurrent_async_updates_test(self, num_concurrent: int = 20) -> List[TestResult]:
        """Test concurrent updates using async/await"""
        print(f"🔄 Running concurrent async updates test ({num_concurrent} concurrent requests)")
        
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            
            for i in range(num_concurrent):
                stage_key = f"async_stage_{i}"
                user_id = f"async_user_{i}"
                task = self.async_single_update(session, stage_key, user_id)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and convert to TestResult objects
            valid_results = []
            for result in results:
                if isinstance(result, TestResult):
                    valid_results.append(result)
                elif isinstance(result, Exception):
                    valid_results.append(TestResult(
                        operation="async_single_update",
                        success=False,
                        response_time=0,
                        status_code=0,
                        error_message=str(result)
                    ))
            
            return valid_results
    
    def stress_test(self, duration_seconds: int = 30, max_concurrent: int = 20) -> List[TestResult]:
        """Run a stress test for a specified duration"""
        print(f"🔥 Running stress test ({duration_seconds}s duration, max {max_concurrent} concurrent)")
        
        results = []
        start_time = time.time()
        request_count = 0
        
        while time.time() - start_time < duration_seconds:
            batch_size = random.randint(5, max_concurrent)
            
            with ThreadPoolExecutor(max_workers=batch_size) as executor:
                futures = []
                
                for i in range(batch_size):
                    operation_type = random.choice(['single', 'batch'])
                    
                    if operation_type == 'single':
                        stage_key = f"stress_{request_count}_{i}"
                        user_id = f"stress_user_{request_count}_{i}"
                        future = executor.submit(self.single_update_test, stage_key, user_id)
                    else:
                        user_id = f"stress_batch_user_{request_count}_{i}"
                        future = executor.submit(self.batch_update_test, user_id)
                    
                    futures.append(future)
                    request_count += 1
                
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        results.append(TestResult(
                            operation="stress_test",
                            success=False,
                            response_time=0,
                            status_code=0,
                            error_message=str(e)
                        ))
            
            # Small delay between batches
            time.sleep(0.1)
        
        return results
    
    def built_in_simulation_test(self, concurrent_calls: int = 15, max_retries: int = 3) -> Dict:
        """Test the built-in concurrent update simulation endpoint"""
        print(f"🎯 Testing built-in simulation endpoint ({concurrent_calls} concurrent calls)")
        
        try:
            url = f"{self.base_url}/{TEST_ID}/simulate-concurrent-updates"
            request_data = {
                "concurrentCallsCount": concurrent_calls,
                "expectedVersion": 1,
                "maxRetries": max_retries
            }
            
            start_time = time.time()
            response = self.session.post(url, json=request_data)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                result['response_time'] = response_time
                return result
            else:
                return {
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time
                }
                
        except Exception as e:
            return {"error": str(e), "response_time": 0}
    
    def analyze_results(self, results: List[TestResult]) -> Dict:
        """Analyze test results and generate statistics"""
        if not results:
            return {"error": "No results to analyze"}
        
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        version_conflicts = [r for r in results if r.version_conflict]
        
        response_times = [r.response_time for r in results if r.response_time > 0]
        successful_response_times = [r.response_time for r in successful_results if r.response_time > 0]
        
        analysis = {
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "failed_requests": len(failed_results),
            "version_conflicts": len(version_conflicts),
            "success_rate": len(successful_results) / len(results) * 100 if results else 0,
            "conflict_rate": len(version_conflicts) / len(results) * 100 if results else 0,
            "response_times": {
                "min": min(response_times) if response_times else 0,
                "max": max(response_times) if response_times else 0,
                "mean": statistics.mean(response_times) if response_times else 0,
                "median": statistics.median(response_times) if response_times else 0,
                "std_dev": statistics.stdev(response_times) if len(response_times) > 1 else 0
            },
            "successful_response_times": {
                "min": min(successful_response_times) if successful_response_times else 0,
                "max": max(successful_response_times) if successful_response_times else 0,
                "mean": statistics.mean(successful_response_times) if successful_response_times else 0,
                "median": statistics.median(successful_response_times) if successful_response_times else 0,
                "std_dev": statistics.stdev(successful_response_times) if len(successful_response_times) > 1 else 0
            },
            "operations_per_second": len(results) / sum(response_times) if response_times else 0,
            "status_code_distribution": {}
        }
        
        # Calculate status code distribution
        for result in results:
            status = result.status_code
            analysis["status_code_distribution"][status] = analysis["status_code_distribution"].get(status, 0) + 1
        
        return analysis
    
    def generate_report(self, all_results: Dict[str, List[TestResult]], simulation_result: Dict = None):
        """Generate a comprehensive test report"""
        print("\n" + "="*80)
        print("🔍 CONCURRENCY TEST REPORT")
        print("="*80)
        
        total_tests = sum(len(results) for results in all_results.values())
        print(f"📊 Total Tests Executed: {total_tests}")
        print(f"🕐 Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        for test_name, results in all_results.items():
            if not results:
                continue
                
            print(f"📋 {test_name.upper().replace('_', ' ')}")
            print("-" * 60)
            
            analysis = self.analyze_results(results)
            
            print(f"  Total Requests: {analysis['total_requests']}")
            print(f"  Success Rate: {analysis['success_rate']:.2f}%")
            print(f"  Version Conflicts: {analysis['version_conflicts']} ({analysis['conflict_rate']:.2f}%)")
            print(f"  Failed Requests: {analysis['failed_requests']}")
            
            if analysis['response_times']['mean'] > 0:
                print(f"  Response Times:")
                print(f"    Mean: {analysis['response_times']['mean']:.3f}s")
                print(f"    Median: {analysis['response_times']['median']:.3f}s")
                print(f"    Min: {analysis['response_times']['min']:.3f}s")
                print(f"    Max: {analysis['response_times']['max']:.3f}s")
                print(f"    Std Dev: {analysis['response_times']['std_dev']:.3f}s")
            
            if analysis['operations_per_second'] > 0:
                print(f"  Throughput: {analysis['operations_per_second']:.2f} ops/sec")
            
            # Show status code distribution
            if analysis['status_code_distribution']:
                print(f"  Status Codes:")
                for status, count in sorted(analysis['status_code_distribution'].items()):
                    print(f"    {status}: {count}")
            
            print()
        
        # Built-in simulation results
        if simulation_result and 'error' not in simulation_result:
            print("🎯 BUILT-IN SIMULATION TEST")
            print("-" * 60)
            print(f"  Total Calls: {simulation_result.get('totalCalls', 0)}")
            print(f"  Successful Updates: {simulation_result.get('successfulUpdates', 0)}")
            print(f"  Failed Updates: {simulation_result.get('failedUpdates', 0)}")
            print(f"  Response Time: {simulation_result.get('response_time', 0):.3f}s")
            
            if 'results' in simulation_result:
                success_count = sum(1 for r in simulation_result['results'] if r.get('success', False))
                print(f"  Success Rate: {success_count / len(simulation_result['results']) * 100:.2f}%")
            print()
        
        print("💡 RECOMMENDATIONS")
        print("-" * 60)
        
        # Calculate overall success rate
        total_successful = sum(len([r for r in results if r.success]) for results in all_results.values())
        overall_success_rate = total_successful / total_tests * 100 if total_tests > 0 else 0
        
        if overall_success_rate > 95:
            print("  ✅ Excellent concurrency handling! The system performs well under load.")
        elif overall_success_rate > 85:
            print("  ⚠️  Good concurrency handling with some conflicts. Consider optimizing retry logic.")
        else:
            print("  ❌ Poor concurrency handling. Review locking mechanisms and error handling.")
        
        # Calculate overall conflict rate
        total_conflicts = sum(len([r for r in results if r.version_conflict]) for results in all_results.values())
        overall_conflict_rate = total_conflicts / total_tests * 100 if total_tests > 0 else 0
        
        if overall_conflict_rate > 20:
            print("  🔄 High version conflict rate. Consider implementing better retry strategies.")
        elif overall_conflict_rate > 10:
            print("  📊 Moderate version conflict rate. Monitor performance under higher loads.")
        else:
            print("  🎯 Low version conflict rate. Concurrency control is working effectively.")
        
        print()
        print("="*80)
    
    def create_visualizations(self, all_results: Dict[str, List[TestResult]]):
        """Create visualizations of test results"""
        try:
            import matplotlib.pyplot as plt
            import pandas as pd
            
            # Prepare data for visualization
            data = []
            for test_name, results in all_results.items():
                for result in results:
                    data.append({
                        'test_type': test_name,
                        'success': result.success,
                        'response_time': result.response_time,
                        'status_code': result.status_code,
                        'version_conflict': result.version_conflict
                    })
            
            if not data:
                print("No data available for visualization")
                return
            
            df = pd.DataFrame(data)
            
            # Create subplots
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle('Concurrency Test Results', fontsize=16)
            
            # 1. Success Rate by Test Type
            success_rates = df.groupby('test_type')['success'].mean() * 100
            axes[0, 0].bar(success_rates.index, success_rates.values)
            axes[0, 0].set_title('Success Rate by Test Type (%)')
            axes[0, 0].set_ylabel('Success Rate (%)')
            axes[0, 0].tick_params(axis='x', rotation=45)
            
            # 2. Response Time Distribution
            df[df['response_time'] > 0]['response_time'].hist(bins=30, ax=axes[0, 1])
            axes[0, 1].set_title('Response Time Distribution')
            axes[0, 1].set_xlabel('Response Time (seconds)')
            axes[0, 1].set_ylabel('Frequency')
            
            # 3. Status Code Distribution
            status_counts = df['status_code'].value_counts()
            axes[1, 0].pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
            axes[1, 0].set_title('Status Code Distribution')
            
            # 4. Response Time by Test Type (Box Plot)
            test_types = df['test_type'].unique()
            response_data = [df[df['test_type'] == tt]['response_time'].values for tt in test_types]
            axes[1, 1].boxplot(response_data, labels=test_types)
            axes[1, 1].set_title('Response Time by Test Type')
            axes[1, 1].set_ylabel('Response Time (seconds)')
            axes[1, 1].tick_params(axis='x', rotation=45)
            
            plt.tight_layout()
            plt.savefig('concurrency_test_results.png', dpi=300, bbox_inches='tight')
            print("📊 Visualization saved as 'concurrency_test_results.png'")
            
        except ImportError:
            print("⚠️  Matplotlib/Pandas not available. Skipping visualizations.")
        except Exception as e:
            print(f"❌ Error creating visualizations: {e}")

def main():
    """Main function to run all concurrency tests"""
    print("🚀 Starting Concurrency Tests for .NET Core JSON Stage Updates API")
    print("="*80)
    
    tester = ConcurrencyTester()
    
    # Setup test data
    if not tester.setup_test_data():
        print("❌ Failed to setup test data. Exiting.")
        return
    
    all_results = {}
    
    try:
        # Test 1: Concurrent Single Updates (Threading)
        results = tester.concurrent_single_updates_test(num_threads=10, updates_per_thread=5)
        all_results['concurrent_single_updates'] = results
        
        # Test 2: Concurrent Async Updates
        results = asyncio.run(tester.concurrent_async_updates_test(num_concurrent=20))
        all_results['concurrent_async_updates'] = results
        
        # Test 3: Mixed Operations Test
        mixed_results = []
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            
            # Submit single updates
            for i in range(10):
                future = executor.submit(tester.single_update_test, f"mixed_single_{i}", f"mixed_user_{i}")
                futures.append(future)
            
            # Submit batch updates
            for i in range(5):
                future = executor.submit(tester.batch_update_test, f"mixed_batch_user_{i}", 3)
                futures.append(future)
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    mixed_results.append(result)
                except Exception as e:
                    mixed_results.append(TestResult(
                        operation="mixed_test",
                        success=False,
                        response_time=0,
                        status_code=0,
                        error_message=str(e)
                    ))
        
        all_results['mixed_operations'] = mixed_results
        
        # Test 4: Stress Test
        stress_results = tester.stress_test(duration_seconds=15, max_concurrent=15)
        all_results['stress_test'] = stress_results
        
        # Test 5: Built-in Simulation
        simulation_result = tester.built_in_simulation_test(concurrent_calls=12, max_retries=3)
        
        # Generate comprehensive report
        tester.generate_report(all_results, simulation_result)
        
        # Create visualizations
        tester.create_visualizations(all_results)
        
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
    finally:
        # Cleanup
        tester.cleanup_test_data()
        print("\n✅ Concurrency testing completed!")

if __name__ == "__main__":
    main()