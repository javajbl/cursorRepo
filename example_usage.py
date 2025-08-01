#!/usr/bin/env python3
"""
Example Usage of Baato.io Ride-Sharing Feasibility Test
======================================================

This script demonstrates different ways to use the Baato.io test suite
for evaluating API feasibility in ride-sharing applications.
"""

import sys
import json
from baato_rideshare_feasibility_test import BaatoRideShareTester

def example_basic_test():
    """Run a basic test with default configuration."""
    print("🚀 Running Basic Baato.io Feasibility Test")
    print("=" * 50)
    
    # Initialize tester with API keys from config
    with open('config.json') as f:
        config = json.load(f)
    
    tester = BaatoRideShareTester(
        baato_api_key=config['api_keys']['baato'],
        google_api_key=config['api_keys']['google']
    )
    
    # Run basic test suite
    results = tester.run_basic_tests()
    
    print(f"✅ Basic tests completed!")
    print(f"📊 Success rate: {results['overall_success_rate']:.2%}")
    print(f"⏱️ Average response time: {results['avg_response_time']:.2f}ms")
    
    return results

def example_custom_scenarios():
    """Run tests with custom ride-sharing scenarios."""
    print("\n🎯 Running Custom Ride-Sharing Scenarios")
    print("=" * 50)
    
    # Load configuration
    with open('config.json') as f:
        config = json.load(f)
    
    tester = BaatoRideShareTester(
        baato_api_key=config['api_keys']['baato'],
        google_api_key=config['api_keys']['google']
    )
    
    # Define custom scenarios
    custom_scenarios = [
        {
            "name": "Airport to Hotel",
            "origin": [27.6966, 85.3591],  # Tribhuvan Airport
            "destination": [27.7172, 85.3240],  # Kathmandu Durbar Square
            "description": "Tourist arriving at airport"
        },
        {
            "name": "Business District Route",
            "origin": [27.7172, 85.3240],  # Kathmandu center
            "destination": [27.7199, 85.3371],  # Business area
            "description": "Business commute"
        }
    ]
    
    # Run custom scenarios
    results = tester.run_custom_scenarios(custom_scenarios)
    
    for scenario, result in results.items():
        print(f"📍 {scenario}: {result['status']}")
        if result['status'] == 'success':
            print(f"   ⏱️ Time: {result['duration']:.2f}s")
            print(f"   📏 Distance: {result['distance']:.2f}km")
    
    return results

def example_performance_comparison():
    """Compare performance between Baato.io and Google Maps."""
    print("\n⚡ Performance Comparison Test")
    print("=" * 50)
    
    # Load configuration  
    with open('config.json') as f:
        config = json.load(f)
    
    tester = BaatoRideShareTester(
        baato_api_key=config['api_keys']['baato'],
        google_api_key=config['api_keys']['google']
    )
    
    # Run performance comparison
    comparison = tester.compare_performance()
    
    print(f"🔍 Baato.io vs Google Maps Performance:")
    print(f"   Baato Response Time: {comparison['baato']['avg_response_time']:.2f}ms")
    print(f"   Google Response Time: {comparison['google']['avg_response_time']:.2f}ms")
    print(f"   Winner: {comparison['performance_winner']}")
    
    return comparison

def example_cost_analysis():
    """Analyze cost implications for ride-sharing usage."""
    print("\n💰 Cost Analysis for Ride-Sharing App")
    print("=" * 50)
    
    # Load configuration
    with open('config.json') as f:
        config = json.load(f)
    
    tester = BaatoRideShareTester(
        baato_api_key=config['api_keys']['baato'],
        google_api_key=config['api_keys']['google']
    )
    
    # Define usage projections
    monthly_usage = {
        'geocoding_requests': 10000,
        'routing_requests': 5000,
        'places_requests': 2000,
        'distance_matrix_requests': 3000
    }
    
    # Calculate costs
    cost_analysis = tester.analyze_costs(monthly_usage)
    
    print(f"💵 Monthly Cost Projection:")
    print(f"   Baato.io: ${cost_analysis['baato']['total_cost']:.2f}")
    print(f"   Google Maps: ${cost_analysis['google']['total_cost']:.2f}")
    print(f"   Savings with Baato: ${cost_analysis['savings']:.2f}")
    print(f"   Cost Efficiency: {cost_analysis['efficiency_ratio']:.1f}x")
    
    return cost_analysis

def example_comprehensive_report():
    """Generate a comprehensive feasibility report."""
    print("\n📊 Comprehensive Feasibility Report")
    print("=" * 50)
    
    # Load configuration
    with open('config.json') as f:
        config = json.load(f)
    
    tester = BaatoRideShareTester(
        baato_api_key=config['api_keys']['baato'],
        google_api_key=config['api_keys']['google']
    )
    
    # Generate comprehensive report
    report = tester.generate_comprehensive_report()
    
    print(f"📈 Overall Feasibility Score: {report['feasibility_score']}/100")
    print(f"🏆 Recommendation: {report['recommendation']}")
    
    print(f"\n📋 Key Findings:")
    for finding in report['key_findings']:
        print(f"   • {finding}")
    
    print(f"\n⚠️ Considerations:")
    for consideration in report['considerations']:
        print(f"   • {consideration}")
    
    # Save detailed report
    with open('baato_feasibility_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Detailed report saved to 'baato_feasibility_report.json'")
    
    return report

def main():
    """Run example usage scenarios."""
    print("🗺️ Baato.io Ride-Sharing API Feasibility Test Examples")
    print("=" * 60)
    
    try:
        # Check if config file exists
        with open('config.json') as f:
            config = json.load(f)
        
        # Verify API keys are configured
        if config['api_keys']['baato'] == 'YOUR_BAATO_API_KEY_HERE':
            print("❌ Please configure your Baato.io API key in config.json")
            return
        
        if config['api_keys']['google'] == 'YOUR_GOOGLE_MAPS_API_KEY_HERE':
            print("❌ Please configure your Google Maps API key in config.json")
            return
        
        # Run example tests
        basic_results = example_basic_test()
        custom_results = example_custom_scenarios()
        performance_results = example_performance_comparison()
        cost_results = example_cost_analysis()
        comprehensive_results = example_comprehensive_report()
        
        print(f"\n🎉 All example tests completed successfully!")
        print(f"📁 Check the generated reports for detailed analysis.")
        
    except FileNotFoundError:
        print("❌ Config file not found. Please ensure config.json exists.")
        print("💡 Copy config.json.example to config.json and add your API keys.")
    except Exception as e:
        print(f"❌ Error running examples: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())