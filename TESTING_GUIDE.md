# Concurrency Testing Guide

This guide explains how to test the concurrent JSON updates functionality using the provided Python test scripts.

## Prerequisites

### 1. .NET Core API Setup
First, ensure the .NET Core API is running:

```bash
# Navigate to the project directory
cd /path/to/your/project

# Build and run the API
dotnet build
dotnet run
```

The API should be available at `https://localhost:7000` (or the port specified in your configuration).

### 2. Python Dependencies

#### For Simple Testing (Minimal Dependencies)
```bash
pip install requests
```

#### For Advanced Testing (Full Features)
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install requests aiohttp matplotlib pandas asyncio
```

## Test Scripts Overview

### 1. `simple_concurrency_test.py` - Lightweight Testing
- **Purpose**: Basic concurrency testing with minimal dependencies
- **Requirements**: Only `requests` library
- **Best for**: Quick validation and CI/CD pipelines

### 2. `test_concurrency.py` - Comprehensive Testing
- **Purpose**: Advanced concurrency testing with detailed analytics
- **Requirements**: Multiple libraries (requests, aiohttp, matplotlib, pandas)
- **Best for**: Detailed performance analysis and visualization

## Running the Tests

### Quick Start - Simple Testing

```bash
# Make sure the .NET API is running first
dotnet run

# In another terminal, run the simple test
python simple_concurrency_test.py
```

### Advanced Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run comprehensive tests
python test_concurrency.py
```

## Test Scenarios Covered

### 1. Concurrent Single Updates
- **What it tests**: Multiple threads updating different stages simultaneously
- **Validates**: Optimistic concurrency control, version conflicts, thread safety
- **Example**: 10 workers each making 5 updates concurrently

### 2. Concurrent Batch Updates
- **What it tests**: Multiple threads performing batch updates simultaneously
- **Validates**: Atomic batch operations, lock contention handling
- **Example**: 8 workers each updating 3 stages in a single batch

### 3. Mixed Operations
- **What it tests**: Combination of single and batch updates running concurrently
- **Validates**: System behavior under varied load patterns
- **Example**: Random mix of single and batch operations over 10 seconds

### 4. Stress Testing
- **What it tests**: High-load scenarios with varying concurrency levels
- **Validates**: System stability under sustained load
- **Example**: Variable load (5-20 concurrent operations) for 30 seconds

### 5. Built-in Simulation
- **What it tests**: The API's own concurrent update simulation endpoint
- **Validates**: Internal retry logic and conflict resolution
- **Example**: API internally creates 15 concurrent update tasks

## Understanding Test Results

### Success Metrics
- **Success Rate**: Percentage of operations that completed successfully
- **Conflict Rate**: Percentage of operations that encountered version conflicts
- **Throughput**: Operations per second
- **Response Times**: Min, max, mean, median response times

### What Good Results Look Like
```
✅ Success Rate: 85-100%
✅ Conflict Rate: 0-20% (conflicts are expected and handled)
✅ Throughput: Varies by system, but should be consistent
✅ No unhandled errors or exceptions
```

### Common Issues and Solutions

#### High Failure Rate (>15%)
- **Possible Causes**: API not running, network issues, configuration problems
- **Solutions**: Check API status, verify URL configuration, check logs

#### High Conflict Rate (>30%)
- **Possible Causes**: Very high contention, insufficient retry logic
- **Solutions**: This is often expected under high load; check retry mechanisms

#### Low Throughput
- **Possible Causes**: Resource constraints, inefficient locking
- **Solutions**: Monitor system resources, consider scaling

## Customizing Tests

### Modifying Test Parameters

#### Simple Test Script
```python
# Edit these parameters in simple_concurrency_test.py
BASE_URL = "https://localhost:7000/api/stagedata"  # Change port if needed
TEST_ID = "your-custom-test-id"

# In main() function, adjust:
single_results = tester.test_concurrent_single_updates(
    num_workers=15,        # Increase for more concurrency
    updates_per_worker=8   # More updates per worker
)
```

#### Advanced Test Script
```python
# Edit these parameters in test_concurrency.py
MAX_CONCURRENT_REQUESTS = 100  # Maximum concurrent requests
TEST_DURATION_SECONDS = 60     # Longer stress test duration
```

### Adding Custom Tests

You can extend either script with custom test scenarios:

```python
def custom_high_contention_test(self):
    """Test high contention on a single stage"""
    def update_same_stage(worker_id):
        return self.single_update_test("shared_stage", f"worker_{worker_id}")
    
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(update_same_stage, i) for i in range(20)]
        results = [future.result() for future in as_completed(futures)]
    
    return results
```

## Interpreting Visualizations (Advanced Script Only)

The advanced script generates `concurrency_test_results.png` with four charts:

### 1. Success Rate by Test Type
- Shows success percentage for each test scenario
- Higher bars indicate better performance

### 2. Response Time Distribution
- Histogram showing distribution of response times
- Look for consistent, low response times

### 3. Status Code Distribution
- Pie chart showing HTTP status codes
- Mostly 200 (success) and some 409 (conflicts) is normal

### 4. Response Time by Test Type (Box Plot)
- Shows response time ranges for each test type
- Lower, more consistent times indicate better performance

## Continuous Integration

### Basic CI Test
```bash
#!/bin/bash
# ci-test.sh

# Start the API in background
dotnet run &
API_PID=$!

# Wait for API to start
sleep 10

# Run simple concurrency test
python simple_concurrency_test.py

# Capture exit code
TEST_RESULT=$?

# Stop the API
kill $API_PID

# Exit with test result
exit $TEST_RESULT
```

### GitHub Actions Example
```yaml
name: Concurrency Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup .NET
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '8.0.x'
    
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install Python dependencies
      run: pip install requests
    
    - name: Build .NET API
      run: dotnet build
    
    - name: Start API
      run: dotnet run &
      
    - name: Wait for API
      run: sleep 15
    
    - name: Run concurrency tests
      run: python simple_concurrency_test.py
```

## Troubleshooting

### Common Issues

#### "Connection refused" errors
```bash
# Check if API is running
curl -k https://localhost:7000/api/stagedata
```

#### SSL certificate errors
- The scripts disable SSL verification for localhost testing
- For production testing, set `verify_ssl=True` and ensure proper certificates

#### Port conflicts
- Change the port in both the .NET API configuration and test scripts
- Update `BASE_URL` in the Python scripts

#### Memory issues during stress testing
- Reduce concurrent workers or test duration
- Monitor system resources during testing

### Debug Mode

Enable debug output in the test scripts:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Add debug prints
print(f"Making request to: {url}")
print(f"Request data: {json.dumps(data, indent=2)}")
```

## Performance Benchmarking

### Baseline Measurements
Run tests multiple times to establish baseline performance:

```bash
# Run 5 iterations and average results
for i in {1..5}; do
    echo "Run $i:"
    python simple_concurrency_test.py
    sleep 5
done
```

### Load Testing
For production load testing, consider using dedicated tools:
- **Artillery.io**: For HTTP load testing
- **Apache JMeter**: For comprehensive load testing
- **k6**: For developer-friendly load testing

The Python scripts are designed for functional concurrency testing rather than high-volume load testing.

## Best Practices

1. **Always test locally first** before running in CI/CD
2. **Monitor system resources** during testing
3. **Run tests multiple times** to identify inconsistent behavior
4. **Start with simple tests** before moving to advanced scenarios
5. **Keep test data isolated** using unique test IDs
6. **Clean up test data** after each run
7. **Document any custom modifications** to the test scripts

This testing framework helps ensure your concurrent JSON update implementation is robust, performant, and handles edge cases gracefully.