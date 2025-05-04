import requests # type: ignore
import json
import os
import time
from functools import lru_cache

class AviationStackService:
    def __init__(self, config=None):
        self.config = config or {}
        self.api_key = config.get('aviationstack_key', '')
        self.base_url = "https://api.aviationstack.com/v1"
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
        self.cache_file = os.path.join(self.cache_dir, 'aircraft_cache.json')
        self.cache = self._load_cache()
        self._ensure_cache_dir()
        
    def _ensure_cache_dir(self):
        """Create the cache directory if it doesn't exist"""
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir)
            except Exception as e:
                print(f"Error creating cache directory: {e}")
    
    def _load_cache(self):
        """Load aircraft data from local cache file"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading aircraft cache: {e}")
        return {}
        
    def _save_cache(self):
        """Save aircraft data to local cache file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            print(f"Error saving aircraft cache: {e}")
    
    @lru_cache(maxsize=100)
    def get_aircraft_name(self, code):
        """Get full aircraft name from ICAO code"""
        if not code or code == 'N/A':
            return 'Unknown'
            
        # Check cache first
        if code in self.cache:
            return self.cache[code]
        
        # If no API key or not a valid code format, fall back to just showing the code
        if not self.api_key or not code.strip():
            return code
            
        try:
            # Call the AviationStack API for aircraft types
            response = requests.get(
                f"{self.base_url}/aircraft_types",
                params={
                    "access_key": self.api_key,
                    "iata_code": code  # AviationStack uses IATA code in the search
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data') and len(data['data']) > 0:
                    for aircraft in data['data']:
                        if aircraft.get('iata_code') == code:
                            name = aircraft.get('aircraft_name')
                            if name:
                                self.cache[code] = name
                                self._save_cache()
                                return name
                
                # If we got a response but didn't find a match, add to cache as the code itself
                self.cache[code] = code
                self._save_cache()
            
            # Fallback for common codes that might not be in AviationStack
            fallback_map = {
                # NetJets Fleet
                'E55P': 'Phenom 300',
                'C56X': 'Citation Excel/XLS',
                'C68A': 'Citation Latitude',
                'C700': 'Citation Longitude',
                'GL5T': 'Global 5000/6000',
                'GLF5': 'Gulfstream G550',
                'GLF6': 'Gulfstream G650',
                'H25B': 'Hawker 800/850XP',
                
                # Flexjet Fleet
                'CL35': 'Challenger 350',
                'CL30': 'Challenger 300',
                # Add other common mappings as needed
            }
            
            if code in fallback_map:
                self.cache[code] = fallback_map[code]
                self._save_cache()
                return fallback_map[code]
                
        except Exception as e:
            print(f"Error fetching aircraft data for {code}: {e}")
        
        # If all attempts fail, return the code itself
        return code