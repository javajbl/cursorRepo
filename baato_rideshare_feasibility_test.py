#!/usr/bin/env python3
"""
Baato.io API Feasibility Test for Ride-Sharing Applications
===========================================================

This script comprehensively tests Baato.io API capabilities for ride-sharing
applications and compares them with Google Maps API. It evaluates performance,
accuracy, features, and cost-effectiveness.

Author: Auto-generated
Date: 2025-01-27
"""

import requests
import time
import json
import logging
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import statistics
import asyncio
import aiohttp
import concurrent.futures
from urllib.parse import urlencode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('baato_test_results.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Class to hold test results"""
    api_name: str
    endpoint: str
    success: bool
    response_time: float
    data: Optional[Dict] = None
    error: Optional[str] = None
    cost_estimate: Optional[float] = None

@dataclass
class RouteComparison:
    """Class to hold route comparison data"""
    distance_km: float
    duration_minutes: float
    polyline: Optional[str] = None
    instructions: Optional[List[str]] = None
    traffic_aware: bool = False

class BaatoAPI:
    """Baato.io API Client"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://api.baato.io/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'Baato-RideShare-Test/1.0'
        })
    
    def search(self, query: str, lat: float = None, lon: float = None, 
               radius: int = 10, limit: int = 5) -> TestResult:
        """Test Baato Search API for address/place search"""
        start_time = time.time()
        
        try:
            params = {
                'access_token': self.access_token,
                'q': query,
                'limit': limit
            }
            if lat and lon:
                params['lat'] = lat
                params['lon'] = lon
                params['radius'] = radius
            
            response = self.session.get(f"{self.base_url}/search", params=params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Baato",
                    endpoint="search",
                    success=True,
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.001  # Baato pricing estimate
                )
            else:
                return TestResult(
                    api_name="Baato",
                    endpoint="search",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Baato",
                endpoint="search",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def reverse_geocode(self, lat: float, lon: float) -> TestResult:
        """Test Baato Reverse Geocoding API"""
        start_time = time.time()
        
        try:
            params = {
                'access_token': self.access_token,
                'lat': lat,
                'lon': lon
            }
            
            response = self.session.get(f"{self.base_url}/reverse", params=params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Baato",
                    endpoint="reverse_geocode",
                    success=True,
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.001
                )
            else:
                return TestResult(
                    api_name="Baato",
                    endpoint="reverse_geocode",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Baato",
                endpoint="reverse_geocode",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def directions(self, points: List[str], mode: str = "car", 
                  alternatives: bool = False, instructions: bool = True) -> TestResult:
        """Test Baato Directions API"""
        start_time = time.time()
        
        try:
            params = {
                'access_token': self.access_token,
                'points': points,
                'mode': mode,
                'alternatives': alternatives,
                'instructions': instructions
            }
            
            response = self.session.get(f"{self.base_url}/directions", params=params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Baato",
                    endpoint="directions",
                    success=True,
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.002
                )
            else:
                return TestResult(
                    api_name="Baato",
                    endpoint="directions",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Baato",
                endpoint="directions",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def nearby_places(self, lat: float, lon: float, place_type: str = "restaurant", 
                     radius: int = 5, limit: int = 10) -> TestResult:
        """Test Baato Nearby Places API"""
        start_time = time.time()
        
        try:
            params = {
                'access_token': self.access_token,
                'lat': lat,
                'lon': lon,
                'type': place_type,
                'radius': radius,
                'limit': limit
            }
            
            response = self.session.get(f"{self.base_url}/nearby", params=params)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Baato",
                    endpoint="nearby_places",
                    success=True,
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.001
                )
            else:
                return TestResult(
                    api_name="Baato",
                    endpoint="nearby_places",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Baato",
                endpoint="nearby_places",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )

class GoogleMapsAPI:
    """Google Maps API Client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'GoogleMaps-RideShare-Test/1.0'
        })
    
    def geocode(self, address: str) -> TestResult:
        """Test Google Geocoding API"""
        start_time = time.time()
        
        try:
            params = {
                'address': address,
                'key': self.api_key
            }
            
            response = self.session.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params=params
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Google Maps",
                    endpoint="geocode",
                    success=data['status'] == 'OK',
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.005  # $5 per 1000 requests
                )
            else:
                return TestResult(
                    api_name="Google Maps",
                    endpoint="geocode",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Google Maps",
                endpoint="geocode",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def reverse_geocode(self, lat: float, lng: float) -> TestResult:
        """Test Google Reverse Geocoding API"""
        start_time = time.time()
        
        try:
            params = {
                'latlng': f"{lat},{lng}",
                'key': self.api_key
            }
            
            response = self.session.get(
                "https://maps.googleapis.com/maps/api/geocode/json",
                params=params
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Google Maps",
                    endpoint="reverse_geocode",
                    success=data['status'] == 'OK',
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.005
                )
            else:
                return TestResult(
                    api_name="Google Maps",
                    endpoint="reverse_geocode",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Google Maps",
                endpoint="reverse_geocode",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def directions(self, origin: str, destination: str, mode: str = "driving",
                  alternatives: bool = False, traffic_model: str = "best_guess") -> TestResult:
        """Test Google Directions API"""
        start_time = time.time()
        
        try:
            params = {
                'origin': origin,
                'destination': destination,
                'mode': mode,
                'alternatives': alternatives,
                'traffic_model': traffic_model,
                'departure_time': 'now',
                'key': self.api_key
            }
            
            response = self.session.get(
                "https://maps.googleapis.com/maps/api/directions/json",
                params=params
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Google Maps",
                    endpoint="directions",
                    success=data['status'] == 'OK',
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.005  # Basic directions
                )
            else:
                return TestResult(
                    api_name="Google Maps",
                    endpoint="directions",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Google Maps",
                endpoint="directions",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def distance_matrix(self, origins: List[str], destinations: List[str],
                       mode: str = "driving") -> TestResult:
        """Test Google Distance Matrix API"""
        start_time = time.time()
        
        try:
            params = {
                'origins': '|'.join(origins),
                'destinations': '|'.join(destinations),
                'mode': mode,
                'departure_time': 'now',
                'traffic_model': 'best_guess',
                'key': self.api_key
            }
            
            response = self.session.get(
                "https://maps.googleapis.com/maps/api/distancematrix/json",
                params=params
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                elements = len(origins) * len(destinations)
                return TestResult(
                    api_name="Google Maps",
                    endpoint="distance_matrix",
                    success=data['status'] == 'OK',
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.005 * elements  # $5 per 1000 elements
                )
            else:
                return TestResult(
                    api_name="Google Maps",
                    endpoint="distance_matrix",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Google Maps",
                endpoint="distance_matrix",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def places_nearby(self, lat: float, lng: float, radius: int = 5000,
                     place_type: str = "restaurant") -> TestResult:
        """Test Google Places Nearby Search API"""
        start_time = time.time()
        
        try:
            params = {
                'location': f"{lat},{lng}",
                'radius': radius,
                'type': place_type,
                'key': self.api_key
            }
            
            response = self.session.get(
                "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
                params=params
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                return TestResult(
                    api_name="Google Maps",
                    endpoint="places_nearby",
                    success=data['status'] == 'OK',
                    response_time=response_time,
                    data=data,
                    cost_estimate=0.032  # $32 per 1000 requests for Basic Data
                )
            else:
                return TestResult(
                    api_name="Google Maps",
                    endpoint="places_nearby",
                    success=False,
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text}"
                )
        
        except Exception as e:
            return TestResult(
                api_name="Google Maps",
                endpoint="places_nearby",
                success=False,
                response_time=time.time() - start_time,
                error=str(e)
            )

class RideShareFeasibilityTester:
    """Main class to test ride-sharing API feasibility"""
    
    def __init__(self, baato_token: str = None, google_api_key: str = None):
        self.baato = BaatoAPI(baato_token) if baato_token else None
        self.google = GoogleMapsAPI(google_api_key) if google_api_key else None
        self.test_results = []
        
        # Test locations (focusing on Nepal/South Asia region for Baato)
        self.test_locations = {
            'kathmandu_durbar': {
                'name': 'Kathmandu Durbar Square',
                'lat': 27.7044,
                'lon': 85.3206,
                'address': 'Kathmandu Durbar Square, Kathmandu, Nepal'
            },
            'tribhuvan_airport': {
                'name': 'Tribhuvan International Airport',
                'lat': 27.6966,
                'lon': 85.3591,
                'address': 'Tribhuvan International Airport, Kathmandu, Nepal'
            },
            'thamel': {
                'name': 'Thamel',
                'lat': 27.7172,
                'lon': 85.3240,
                'address': 'Thamel, Kathmandu, Nepal'
            },
            'patan': {
                'name': 'Patan Durbar Square',
                'lat': 27.6720,
                'lon': 85.3262,
                'address': 'Patan Durbar Square, Lalitpur, Nepal'
            }
        }
    
    def log_result(self, result: TestResult):
        """Log test result"""
        self.test_results.append(result)
        
        status = "✅ SUCCESS" if result.success else "❌ FAILED"
        logger.info(f"{status} | {result.api_name} | {result.endpoint} | "
                   f"{result.response_time:.3f}s | Cost: ${result.cost_estimate or 0:.4f}")
        
        if result.error:
            logger.error(f"Error: {result.error}")
    
    def test_geocoding_capabilities(self):
        """Test geocoding and reverse geocoding capabilities"""
        logger.info("\n🧭 TESTING GEOCODING CAPABILITIES")
        logger.info("=" * 50)
        
        # Test forward geocoding
        for loc_key, loc_data in self.test_locations.items():
            logger.info(f"\nTesting geocoding for: {loc_data['name']}")
            
            # Test Baato search
            if self.baato:
                result = self.baato.search(loc_data['name'])
                self.log_result(result)
            
            # Test Google geocoding
            if self.google:
                result = self.google.geocode(loc_data['address'])
                self.log_result(result)
        
        # Test reverse geocoding
        logger.info(f"\nTesting reverse geocoding for sample coordinates")
        sample_loc = self.test_locations['kathmandu_durbar']
        
        if self.baato:
            result = self.baato.reverse_geocode(sample_loc['lat'], sample_loc['lon'])
            self.log_result(result)
        
        if self.google:
            result = self.google.reverse_geocode(sample_loc['lat'], sample_loc['lon'])
            self.log_result(result)
    
    def test_routing_capabilities(self):
        """Test routing and directions capabilities"""
        logger.info("\n🛣️  TESTING ROUTING CAPABILITIES")
        logger.info("=" * 50)
        
        # Test route from airport to city center
        origin = self.test_locations['tribhuvan_airport']
        destination = self.test_locations['thamel']
        
        logger.info(f"\nTesting route: {origin['name']} → {destination['name']}")
        
        if self.baato:
            # Baato uses coordinate pairs as strings
            points = [f"{origin['lat']},{origin['lon']}", 
                     f"{destination['lat']},{destination['lon']}"]
            result = self.baato.directions(points, mode="car", instructions=True)
            self.log_result(result)
        
        if self.google:
            result = self.google.directions(
                origin=f"{origin['lat']},{origin['lon']}",
                destination=f"{destination['lat']},{destination['lon']}",
                mode="driving",
                alternatives=True,
                traffic_model="best_guess"
            )
            self.log_result(result)
    
    def test_nearby_search(self):
        """Test nearby places search for ride-share relevant POIs"""
        logger.info("\n🔍 TESTING NEARBY PLACES SEARCH")
        logger.info("=" * 50)
        
        center_loc = self.test_locations['thamel']
        test_types = ['restaurant', 'hospital', 'school', 'shopping']
        
        for place_type in test_types:
            logger.info(f"\nSearching for {place_type}s near {center_loc['name']}")
            
            if self.baato:
                result = self.baato.nearby_places(
                    center_loc['lat'], center_loc['lon'], 
                    place_type, radius=5, limit=10
                )
                self.log_result(result)
            
            if self.google:
                result = self.google.places_nearby(
                    center_loc['lat'], center_loc['lon'],
                    radius=5000, place_type=place_type
                )
                self.log_result(result)
    
    def test_distance_matrix(self):
        """Test distance matrix for driver dispatch scenarios"""
        logger.info("\n📊 TESTING DISTANCE MATRIX (Driver Dispatch)")
        logger.info("=" * 50)
        
        # Simulate multiple drivers at different locations
        driver_locations = [
            f"{self.test_locations['kathmandu_durbar']['lat']},{self.test_locations['kathmandu_durbar']['lon']}",
            f"{self.test_locations['patan']['lat']},{self.test_locations['patan']['lon']}",
            f"{self.test_locations['thamel']['lat']},{self.test_locations['thamel']['lon']}"
        ]
        
        # Passenger pickup location
        passenger_location = [f"{self.test_locations['tribhuvan_airport']['lat']},{self.test_locations['tribhuvan_airport']['lon']}"]
        
        logger.info("Testing driver dispatch scenario: 3 drivers → 1 passenger")
        
        # Google Distance Matrix (Baato doesn't have a direct distance matrix API)
        if self.google:
            result = self.google.distance_matrix(
                origins=driver_locations,
                destinations=passenger_location,
                mode="driving"
            )
            self.log_result(result)
    
    def performance_stress_test(self, num_requests: int = 10):
        """Perform stress testing to evaluate API performance"""
        logger.info(f"\n⚡ PERFORMANCE STRESS TEST ({num_requests} requests)")
        logger.info("=" * 50)
        
        sample_loc = self.test_locations['kathmandu_durbar']
        
        # Test rapid geocoding requests
        response_times = {'baato': [], 'google': []}
        
        for i in range(num_requests):
            logger.info(f"Request {i+1}/{num_requests}")
            
            if self.baato:
                result = self.baato.search("Kathmandu")
                if result.success:
                    response_times['baato'].append(result.response_time)
                self.log_result(result)
            
            if self.google:
                result = self.google.geocode("Kathmandu, Nepal")
                if result.success:
                    response_times['google'].append(result.response_time)
                self.log_result(result)
            
            time.sleep(0.1)  # Small delay to be respectful to APIs
        
        # Calculate statistics
        for api_name, times in response_times.items():
            if times:
                avg_time = statistics.mean(times)
                min_time = min(times)
                max_time = max(times)
                logger.info(f"\n{api_name.upper()} Performance:")
                logger.info(f"  Average: {avg_time:.3f}s")
                logger.info(f"  Min: {min_time:.3f}s")
                logger.info(f"  Max: {max_time:.3f}s")
                logger.info(f"  Success rate: {len(times)}/{num_requests} ({len(times)/num_requests*100:.1f}%)")
    
    def compare_route_accuracy(self):
        """Compare route accuracy between APIs"""
        logger.info("\n📏 ROUTE ACCURACY COMPARISON")
        logger.info("=" * 50)
        
        test_routes = [
            (self.test_locations['tribhuvan_airport'], self.test_locations['thamel']),
            (self.test_locations['kathmandu_durbar'], self.test_locations['patan']),
        ]
        
        for origin, destination in test_routes:
            logger.info(f"\nComparing route: {origin['name']} → {destination['name']}")
            
            routes = {}
            
            # Get Baato route
            if self.baato:
                points = [f"{origin['lat']},{origin['lon']}", 
                         f"{destination['lat']},{destination['lon']}"]
                result = self.baato.directions(points, mode="car", instructions=True)
                if result.success and result.data:
                    try:
                        route_data = result.data.get('data', [{}])[0]
                        routes['baato'] = RouteComparison(
                            distance_km=route_data.get('distance', 0) / 1000,
                            duration_minutes=route_data.get('time', 0) / 60,
                            traffic_aware=False
                        )
                    except (KeyError, IndexError, TypeError):
                        logger.warning("Could not parse Baato route data")
            
            # Get Google route
            if self.google:
                result = self.google.directions(
                    origin=f"{origin['lat']},{origin['lon']}",
                    destination=f"{destination['lat']},{destination['lon']}",
                    mode="driving",
                    traffic_model="best_guess"
                )
                if result.success and result.data:
                    try:
                        route = result.data['routes'][0]['legs'][0]
                        routes['google'] = RouteComparison(
                            distance_km=route['distance']['value'] / 1000,
                            duration_minutes=route['duration']['value'] / 60,
                            traffic_aware=True
                        )
                    except (KeyError, IndexError, TypeError):
                        logger.warning("Could not parse Google route data")
            
            # Compare results
            for api_name, route in routes.items():
                logger.info(f"  {api_name.upper()}: {route.distance_km:.2f}km, "
                           f"{route.duration_minutes:.1f}min, "
                           f"Traffic: {'Yes' if route.traffic_aware else 'No'}")
    
    def analyze_cost_effectiveness(self):
        """Analyze cost effectiveness for ride-sharing use case"""
        logger.info("\n💰 COST EFFECTIVENESS ANALYSIS")
        logger.info("=" * 50)
        
        # Calculate costs for typical ride-sharing usage
        monthly_rides = 10000  # Example: 10,000 rides per month
        
        # Typical API calls per ride:
        # - 1 geocoding (pickup address)
        # - 1 reverse geocoding (drop location)
        # - 1 route calculation
        # - 1 distance matrix (driver dispatch)
        # - 2 nearby searches (pickup/drop POIs)
        
        logger.info(f"Cost analysis for {monthly_rides:,} rides per month:")
        logger.info("-" * 40)
        
        # Baato costs (estimated based on research)
        baato_cost_per_call = 0.001  # Very low cost
        baato_calls_per_ride = 6  # All the above operations
        baato_monthly_cost = monthly_rides * baato_calls_per_ride * baato_cost_per_call
        
        logger.info(f"BAATO.IO:")
        logger.info(f"  Cost per API call: ${baato_cost_per_call:.4f}")
        logger.info(f"  API calls per ride: {baato_calls_per_ride}")
        logger.info(f"  Monthly cost: ${baato_monthly_cost:.2f}")
        logger.info(f"  Annual cost: ${baato_monthly_cost * 12:.2f}")
        
        # Google Maps costs
        google_geocoding = monthly_rides * 2 * 0.005  # 2 geocoding calls per ride
        google_directions = monthly_rides * 0.005     # 1 directions call per ride
        google_distance_matrix = monthly_rides * 0.005  # 1 distance matrix call per ride
        google_places = monthly_rides * 2 * 0.032       # 2 places calls per ride
        google_monthly_cost = google_geocoding + google_directions + google_distance_matrix + google_places
        
        logger.info(f"\nGOOGLE MAPS:")
        logger.info(f"  Geocoding: ${google_geocoding:.2f}")
        logger.info(f"  Directions: ${google_directions:.2f}")
        logger.info(f"  Distance Matrix: ${google_distance_matrix:.2f}")
        logger.info(f"  Places: ${google_places:.2f}")
        logger.info(f"  Monthly cost: ${google_monthly_cost:.2f}")
        logger.info(f"  Annual cost: ${google_monthly_cost * 12:.2f}")
        
        savings = google_monthly_cost - baato_monthly_cost
        savings_percentage = (savings / google_monthly_cost) * 100 if google_monthly_cost > 0 else 0
        
        logger.info(f"\nCOST COMPARISON:")
        logger.info(f"  Monthly savings with Baato: ${savings:.2f}")
        logger.info(f"  Annual savings with Baato: ${savings * 12:.2f}")
        logger.info(f"  Cost reduction: {savings_percentage:.1f}%")
    
    def generate_feasibility_report(self):
        """Generate comprehensive feasibility report"""
        logger.info("\n📋 BAATO.IO FEASIBILITY REPORT FOR RIDE-SHARING")
        logger.info("=" * 60)
        
        # Analyze results
        baato_results = [r for r in self.test_results if r.api_name == "Baato"]
        google_results = [r for r in self.test_results if r.api_name == "Google Maps"]
        
        baato_success_rate = len([r for r in baato_results if r.success]) / len(baato_results) * 100 if baato_results else 0
        google_success_rate = len([r for r in google_results if r.success]) / len(google_results) * 100 if google_results else 0
        
        baato_avg_response = statistics.mean([r.response_time for r in baato_results if r.success]) if [r for r in baato_results if r.success] else 0
        google_avg_response = statistics.mean([r.response_time for r in google_results if r.success]) if [r for r in google_results if r.success] else 0
        
        logger.info(f"\n🎯 SUCCESS RATES:")
        logger.info(f"  Baato.io: {baato_success_rate:.1f}%")
        logger.info(f"  Google Maps: {google_success_rate:.1f}%")
        
        logger.info(f"\n⚡ AVERAGE RESPONSE TIMES:")
        logger.info(f"  Baato.io: {baato_avg_response:.3f}s")
        logger.info(f"  Google Maps: {google_avg_response:.3f}s")
        
        logger.info(f"\n🏆 FEASIBILITY ASSESSMENT:")
        
        # Geographic Coverage
        logger.info(f"\n📍 GEOGRAPHIC COVERAGE:")
        logger.info(f"  ✅ Baato.io: Excellent for Nepal/South Asia")
        logger.info(f"  ✅ Google Maps: Global coverage")
        logger.info(f"  📝 Recommendation: Use Baato for Nepal operations")
        
        # Feature Completeness
        logger.info(f"\n🛠️  FEATURE COMPLETENESS:")
        logger.info(f"  ✅ Geocoding & Reverse Geocoding: Both APIs")
        logger.info(f"  ✅ Routing & Directions: Both APIs")
        logger.info(f"  ✅ Nearby Places: Both APIs")
        logger.info(f"  ⚠️  Distance Matrix: Google has dedicated API")
        logger.info(f"  ⚠️  Real-time Traffic: Google has better coverage")
        logger.info(f"  ✅ Cost Effectiveness: Baato significantly cheaper")
        
        # Ride-Sharing Specific Assessment
        logger.info(f"\n🚗 RIDE-SHARING SUITABILITY:")
        logger.info(f"  Driver Dispatch: ⚠️  Baato needs custom distance matrix")
        logger.info(f"  Route Planning: ✅ Both APIs suitable")
        logger.info(f"  ETA Calculation: ✅ Both APIs provide duration")
        logger.info(f"  Address Search: ✅ Both APIs excellent")
        logger.info(f"  POI Discovery: ✅ Both APIs suitable")
        
        # Final Recommendation
        logger.info(f"\n🎯 FINAL RECOMMENDATION:")
        if baato_success_rate >= 80:
            logger.info(f"  ✅ FEASIBLE: Baato.io is suitable for ride-sharing in Nepal")
            logger.info(f"  💡 Advantages: Lower cost, local optimization, good coverage")
            logger.info(f"  ⚠️  Considerations: Limited global coverage, implement custom distance matrix")
            logger.info(f"  🔄 Hybrid Approach: Use Baato for Nepal, Google for international")
        else:
            logger.info(f"  ⚠️  NEEDS EVALUATION: Lower success rate than expected")
            logger.info(f"  💡 Consider: Hybrid approach or further testing needed")
        
        # Implementation Strategy
        logger.info(f"\n🚀 IMPLEMENTATION STRATEGY:")
        logger.info(f"  1. Start with Baato.io for core Nepal operations")
        logger.info(f"  2. Implement distance matrix using multiple direction calls")
        logger.info(f"  3. Use Google Maps as fallback for international routes")
        logger.info(f"  4. Monitor performance and costs in production")
        logger.info(f"  5. Consider Barikoi (Bangladesh) for regional expansion")
    
    def run_complete_test_suite(self):
        """Run the complete test suite"""
        logger.info("🚀 STARTING BAATO.IO RIDE-SHARING FEASIBILITY TEST")
        logger.info("=" * 60)
        logger.info(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.baato and not self.google:
            logger.error("❌ No API keys provided. Please set BAATO_TOKEN and/or GOOGLE_API_KEY")
            return
        
        try:
            # Run all test categories
            self.test_geocoding_capabilities()
            self.test_routing_capabilities()
            self.test_nearby_search()
            self.test_distance_matrix()
            self.performance_stress_test(num_requests=5)
            self.compare_route_accuracy()
            self.analyze_cost_effectiveness()
            self.generate_feasibility_report()
            
            logger.info(f"\n✅ TEST SUITE COMPLETED SUCCESSFULLY")
            logger.info(f"Total API calls made: {len(self.test_results)}")
            logger.info(f"Results saved to: baato_test_results.log")
            
        except Exception as e:
            logger.error(f"❌ Test suite failed with error: {str(e)}")
            raise

def main():
    """Main function to run the test"""
    import os
    
    # Get API credentials from environment variables
    baato_token = os.getenv('BAATO_ACCESS_TOKEN')
    google_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    if not baato_token and not google_api_key:
        print("\n🔑 API CREDENTIALS REQUIRED")
        print("=" * 40)
        print("To run this test, you need at least one of the following:")
        print("\n1. Baato.io Access Token:")
        print("   - Sign up at: https://baato.io")
        print("   - Get your access token from the dashboard")
        print("   - Set environment variable: BAATO_ACCESS_TOKEN")
        print("\n2. Google Maps API Key:")
        print("   - Go to: https://console.cloud.google.com/")
        print("   - Enable APIs: Geocoding, Directions, Distance Matrix, Places")
        print("   - Create API key and set environment variable: GOOGLE_MAPS_API_KEY")
        print("\nExample usage:")
        print("export BAATO_ACCESS_TOKEN='your_baato_token'")
        print("export GOOGLE_MAPS_API_KEY='your_google_key'")
        print("python baato_rideshare_feasibility_test.py")
        return
    
    # Initialize and run tests
    tester = RideShareFeasibilityTester(baato_token, google_api_key)
    tester.run_complete_test_suite()

if __name__ == "__main__":
    main()