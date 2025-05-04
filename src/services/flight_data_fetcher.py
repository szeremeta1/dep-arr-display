import requests # type: ignore
import time
import json
from datetime import datetime
import os

def fetch_flight_data(airport_code, config):
    """Fetch ONLY real FlightRadar24 data for the specified airport"""
    print(f"Fetching FlightRadar24 data for {airport_code}")
    
    # FlightRadar24 internal API endpoints
    base_url = "https://api.flightradar24.com/common/v1/airport.json"
    
    # Custom headers to mimic browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.flightradar24.com',
        'Referer': f'https://www.flightradar24.com/data/airports/{airport_code.lower()}'
    }
    
    # Initialize result structures
    departures = []
    arrivals = []
    
    try:
        # Fetch arrivals
        print("Fetching arrivals data from FlightRadar24...")
        arrivals_params = {
            'code': airport_code,
            'plugin[]': 'schedule',
            'plugin-setting[schedule][mode]': 'arrivals',
            'plugin-setting[schedule][timestamp]': int(time.time()),
            'page': 1,
            'limit': 100,
            'token': config.get('fr24_api_key', '')
        }
        
        arrival_response = requests.get(
            base_url, 
            params=arrivals_params,
            headers=headers,
            timeout=20
        )
        
        print(f"Arrivals API response status: {arrival_response.status_code}")
        if arrival_response.status_code != 200:
            print(f"Failed to fetch arrivals: {arrival_response.text}")
        else:
            # Debug: Save raw response
            with open('/tmp/fr24_arrivals_response.json', 'w') as f:
                f.write(arrival_response.text)
                
            arrival_data = arrival_response.json()
            
            # Process arrival data - using .get() for safer access
            arrival_schedule = arrival_data.get('result', {}).get('response', {}).get('airport', {}).get('pluginData', {}).get('schedule', {})
            
            if arrival_schedule and 'arrivals' in arrival_schedule:
                arrival_dict = arrival_schedule['arrivals']
                print(f"Found arrivals data with {len(arrival_dict)} keys")
                # The actual flights are in arrival_dict['data'], which is a list
                arrival_list = arrival_dict.get('data', [])
                print(f"Found {len(arrival_list)} arrival flights")
                for flight_data in arrival_list:
                    try:
                        print("DEBUG ARRIVAL FLIGHT DATA:", json.dumps(flight_data, indent=2))
                        f = flight_data.get("flight", {})
                        arrival = {
                            'time': (
                                f.get('time', {}).get('scheduled', {}).get('arrival') and
                                datetime.fromtimestamp(f['time']['scheduled']['arrival']).strftime('%H:%M')
                            ) or 'N/A',
                            'flight': f.get('identification', {}).get('callsign')
                                      or f.get('identification', {}).get('number', {}).get('default', 'N/A'),
                            'aircraft': f.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
                            'origin': {
                                'code': f.get('airport', {}).get('origin', {}).get('code', {}).get('iata', 'N/A'),
                                'name': f.get('airport', {}).get('origin', {}).get('name', 'Unknown')
                            },
                            'status': f.get('status', {}).get('text', 'N/A')
                        }
                        arrivals.append(arrival)
                    except Exception as e:
                        print(f"Error parsing arrival flight: {str(e)}")
            else:
                print("No arrivals data found in response")
            
        # Fetch departures
        print("Fetching departures data from FlightRadar24...")
        departures_params = {
            'code': airport_code,
            'plugin[]': 'schedule',
            'plugin-setting[schedule][mode]': 'departures',
            'plugin-setting[schedule][timestamp]': int(time.time()),
            'page': 1,
            'limit': 100,
            'token': config.get('fr24_api_key', '')
        }
        
        departure_response = requests.get(
            base_url, 
            params=departures_params,
            headers=headers,
            timeout=20
        )
        
        print(f"Departures API response status: {departure_response.status_code}")
        if departure_response.status_code != 200:
            print(f"Failed to fetch departures: {departure_response.text}")
        else:
            # Debug: Save raw response
            with open('/tmp/fr24_departures_response.json', 'w') as f:
                f.write(departure_response.text)
                
            departure_data = departure_response.json()
            
            # Process departure data - using .get() for safer access
            departure_schedule = departure_data.get('result', {}).get('response', {}).get('airport', {}).get('pluginData', {}).get('schedule', {})
            
            if departure_schedule and 'departures' in departure_schedule:
                departure_dict = departure_schedule['departures']
                print(f"Found departures data with {len(departure_dict)} keys")
                departure_list = departure_dict.get('data', [])
                print(f"Found {len(departure_list)} departure flights")
                for flight_data in departure_list:
                    try:
                        print("DEBUG DEPARTURE FLIGHT DATA:", json.dumps(flight_data, indent=2))
                        f = flight_data.get("flight", {})
                        departure = {
                            'time': (
                                f.get('time', {}).get('scheduled', {}).get('departure') and
                                datetime.fromtimestamp(f['time']['scheduled']['departure']).strftime('%H:%M')
                            ) or 'N/A',
                            'flight': f.get('identification', {}).get('callsign')
                                      or f.get('identification', {}).get('number', {}).get('default', 'N/A'),
                            'aircraft': f.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
                            'destination': {
                                'code': f.get('airport', {}).get('destination', {}).get('code', {}).get('iata', 'N/A'),
                                'name': f.get('airport', {}).get('destination', {}).get('name', 'Unknown')
                            },
                            'status': f.get('status', {}).get('text', 'N/A')
                        }
                        departures.append(departure)
                    except Exception as e:
                        print(f"Error parsing departure flight: {str(e)}")
            else:
                print("No departures data found in response")
        
        # If we got any data, return it
        result = {
            'departures': departures,
            'arrivals': arrivals
        }
        
        if len(departures) > 0 or len(arrivals) > 0:
            print(f"Returning real FlightRadar24 data: {len(departures)} departures, {len(arrivals)} arrivals")
            # Add debug info to see what's in the data
            for i, arrival in enumerate(arrivals):
                print(f"Arrival {i+1}: {arrival}")
            for i, departure in enumerate(departures):
                print(f"Departure {i+1}: {departure}")
            return result
        
        # If we get here, we failed to get any data
        print("CRITICAL: Failed to get ANY data from FlightRadar24")
        raise Exception("No data available from FlightRadar24")
        
    except Exception as e:
        print(f"ERROR: Could not fetch FlightRadar24 data: {str(e)}")
        raise Exception(f"Failed to fetch FlightRadar24 data: {str(e)}")