import requests # type: ignore
import time
import json
from datetime import datetime, timezone, timedelta
import os
import pytz # type: ignore

# Global dict to track diverted/cancelled flights with their timestamp
# Structure: {flight_id: {'status': status, 'timestamp': timestamp, 'diverted_to': airport_code}}
cancelled_flights = {}

# Global dict to track landed flights with their timestamp
landed_flights = {}

# Helper function to clean out old cancelled/diverted flights
def clean_cancelled_flights():
    current_time = time.time()
    # Remove flights that have been cancelled/diverted for more than 30 minutes
    to_remove = []
    for flight_id, data in cancelled_flights.items():
        if current_time - data['timestamp'] > 1800:  # 1800 seconds = 30 minutes
            to_remove.append(flight_id)
    
    for flight_id in to_remove:
        del cancelled_flights[flight_id]

# Helper function to clean out old landed flights
def clean_landed_flights():
    current_time = time.time()
    # Remove flights that have been landed for more than 10 minutes
    to_remove = []
    for flight_id, data in landed_flights.items():
        if current_time - data['timestamp'] > 600:  # 600 seconds = 10 minutes
            to_remove.append(flight_id)
    
    for flight_id in to_remove:
        del landed_flights[flight_id]

def fetch_flight_data(airport_code, config):
    """Fetch ALL FlightRadar24 data for the specified airport, including flights with no carrier or logo."""
    print(f"Fetching FlightRadar24 data for {airport_code}")
    
    # Clean old cancelled/diverted flights first
    clean_cancelled_flights()
    
    # Clean old landed flights
    clean_landed_flights()
    
    base_url = "https://api.flightradar24.com/common/v1/airport.json"
    local_tz = pytz.timezone('America/New_York')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Origin': 'https://www.flightradar24.com',
        'Referer': f'https://www.flightradar24.com/data/airports/{airport_code.lower()}'
    }
    departures = []
    arrivals = []
    
    # Get current timestamp for comparing with estimated arrival times
    current_time = int(time.time())
    
    try:
        # Arrivals
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
        arrivals_data_debug = None
        if arrival_response.status_code == 200:
            arrival_data = arrival_response.json()
            arrivals_data_debug = arrival_data  # Save for debug if needed
            arrival_schedule = arrival_data.get('result', {}).get('response', {}).get('airport', {}).get('pluginData', {}).get('schedule', {})
            if arrival_schedule and 'arrivals' in arrival_schedule:
                arrival_dict = arrival_schedule['arrivals']
                arrival_list = arrival_dict.get('data', [])
                for flight_data in arrival_list:
                    try:
                        f = flight_data.get("flight", {})
                        times = f.get('time', {})
                        scheduled_time = None
                        estimated_time = None
                        estimated_timestamp = None
                        
                        if times.get('scheduled', {}).get('arrival'):
                            utc_time = datetime.fromtimestamp(times['scheduled']['arrival'], timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            scheduled_time = local_time.strftime('%-I:%M %p')
                        
                        if times.get('estimated', {}).get('arrival'):
                            estimated_timestamp = times['estimated']['arrival']
                            utc_time = datetime.fromtimestamp(estimated_timestamp, timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            estimated_time = local_time.strftime('%-I:%M %p')
                        elif times.get('real', {}).get('arrival'):
                            estimated_timestamp = times['real']['arrival']
                            utc_time = datetime.fromtimestamp(estimated_timestamp, timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            estimated_time = local_time.strftime('%-I:%M %p')
                        
                        delay_status = "on-time"
                        if times.get('scheduled', {}).get('arrival') and (times.get('estimated', {}).get('arrival') or times.get('real', {}).get('arrival')):
                            scheduled_ts = times['scheduled']['arrival']
                            actual_ts = times.get('estimated', {}).get('arrival') or times.get('real', {}).get('arrival')
                            if actual_ts and scheduled_ts:
                                delay_mins = (actual_ts - scheduled_ts) // 60
                                if delay_mins > 5:
                                    delay_status = "delayed"
                                elif delay_mins < -5:
                                    delay_status = "early"
                        
                        status_text = f.get('status', {}).get('text', 'N/A')
                        flight_id = f.get('identification', {}).get('id', '') or f.get('identification', {}).get('callsign', '')
                        
                        # Check if flight is diverted or cancelled
                        is_special_status = False
                        diverted_to = None
                        
                        # Check if status text indicates diversion
                        if "divert" in status_text.lower():
                            # Extract diversion airport if possible
                            # Assuming format like "Diverted to TTN"
                            parts = status_text.lower().split("to ")
                            if len(parts) > 1:
                                diverted_to = parts[1].strip().upper()
                            
                            # Track this diverted flight
                            cancelled_flights[flight_id] = {
                                'status': 'diverted',
                                'timestamp': time.time(),
                                'diverted_to': diverted_to
                            }
                            is_special_status = True
                            status_class = "cancelled"
                        
                        elif "cancel" in status_text.lower():
                            # Track this cancelled flight
                            cancelled_flights[flight_id] = {
                                'status': 'cancelled',
                                'timestamp': time.time()
                            }
                            is_special_status = True
                            status_class = "cancelled"
                        
                        # Check if it's a previously stored diverted/cancelled flight
                        elif flight_id in cancelled_flights:
                            is_special_status = True
                            if cancelled_flights[flight_id]['status'] == 'diverted':
                                diverted_to = cancelled_flights[flight_id].get('diverted_to')
                                status_text = f"Diverted to {diverted_to}" if diverted_to else "Diverted"
                            status_class = "cancelled"
                        
                        # Check if flight has landed status from API
                        elif status_text.lower() == "landed":
                            landed_flights[flight_id] = {
                                'status': 'landed',
                                'timestamp': time.time()
                            }
                            status_class = "landed"
                            is_special_status = True
                            status_text = "Landed"
                        
                        # Check if flight is already in our landed_flights dictionary
                        elif flight_id in landed_flights:
                            status_class = "landed"
                            is_special_status = True
                            status_text = "Landed"
                            
                        # NEW LOGIC: Check if estimated arrival time is in the past
                        elif estimated_timestamp and estimated_timestamp <= current_time:
                            # If estimated arrival time is now or in the past, mark as landed
                            landed_flights[flight_id] = {
                                'status': 'landed',
                                'timestamp': time.time()
                            }
                            status_class = "landed"
                            is_special_status = True
                            status_text = "Landed"
                        
                        arrivals.append({
                            'scheduled_time': scheduled_time or 'N/A',
                            'scheduled_timestamp': times.get('scheduled', {}).get('arrival', 0),
                            'estimated_time': estimated_time or 'N/A',
                            'delay_status': delay_status,
                            'flight': f.get('identification', {}).get('callsign')
                                      or f.get('identification', {}).get('number', {}).get('default', 'N/A'),
                            'aircraft': f.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
                            'registration': f.get('aircraft', {}).get('registration', 'N/A'),
                            'origin': {
                                'code': f.get('airport', {}).get('origin', {}).get('code', {}).get('iata', 'N/A'),
                                'name': f.get('airport', {}).get('origin', {}).get('name', 'Unknown')
                            },
                            'status': status_text,
                            'status_class': status_class if is_special_status else delay_status,
                            'is_special_status': is_special_status,
                            'carrier': f.get('airline', {}).get('name', '') if f.get('airline') else ''
                        })
                    except Exception as e:
                        print(f"Error parsing arrival flight: {str(e)}")
            else:
                print("No arrivals data found in response")
                print("DEBUG: arrival_data =", json.dumps(arrivals_data_debug, indent=2)[:2000])  # Print first 2000 chars for debug
        else:
            print(f"Failed to fetch arrivals: {arrival_response.text}")

        # Departures
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
        departures_data_debug = None
        if departure_response.status_code == 200:
            departure_data = departure_response.json()
            departures_data_debug = departure_data  # Save for debug if needed
            departure_schedule = departure_data.get('result', {}).get('response', {}).get('airport', {}).get('pluginData', {}).get('schedule', {})
            if departure_schedule and 'departures' in departure_schedule:
                departure_dict = departure_schedule['departures']
                departure_list = departure_dict.get('data', [])
                for flight_data in departure_list:
                    try:
                        f = flight_data.get("flight", {})
                        times = f.get('time', {})
                        scheduled_time = None
                        estimated_time = None
                        if times.get('scheduled', {}).get('departure'):
                            utc_time = datetime.fromtimestamp(times['scheduled']['departure'], timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            scheduled_time = local_time.strftime('%-I:%M %p')
                        if times.get('estimated', {}).get('departure'):
                            utc_time = datetime.fromtimestamp(times['estimated']['departure'], timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            estimated_time = local_time.strftime('%-I:%M %p')
                        elif times.get('real', {}).get('departure'):
                            utc_time = datetime.fromtimestamp(times['real']['departure'], timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            estimated_time = local_time.strftime('%-I:%M %p')
                        delay_status = "on-time"
                        if times.get('scheduled', {}).get('departure') and (times.get('estimated', {}).get('departure') or times.get('real', {}).get('departure')):
                            scheduled_ts = times['scheduled']['departure']
                            actual_ts = times.get('estimated', {}).get('departure') or times.get('real', {}).get('departure')
                            if actual_ts and scheduled_ts:
                                delay_mins = (actual_ts - scheduled_ts) // 60
                                if delay_mins > 5:
                                    delay_status = "delayed"
                                elif delay_mins < -5:
                                    delay_status = "early"
                        departures.append({
                            'scheduled_time': scheduled_time or 'N/A',
                            'scheduled_timestamp': times.get('scheduled', {}).get('departure', 0),
                            'estimated_time': estimated_time or 'N/A',
                            'delay_status': delay_status,
                            'flight': f.get('identification', {}).get('callsign')
                                      or f.get('identification', {}).get('number', {}).get('default', 'N/A'),
                            'aircraft': f.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
                            'registration': f.get('aircraft', {}).get('registration', 'N/A'),
                            'destination': {
                                'code': f.get('airport', {}).get('destination', {}).get('code', {}).get('iata', 'N/A'),
                                'name': f.get('airport', {}).get('destination', {}).get('name', 'Unknown')
                            },
                            'status': f.get('status', {}).get('text', 'N/A'),
                            'carrier': f.get('airline', {}).get('name', '') if f.get('airline') else ''
                        })
                    except Exception as e:
                        print(f"Error parsing departure flight: {str(e)}")
            else:
                print("No departures data found in response")
                print("DEBUG: departure_data =", json.dumps(departures_data_debug, indent=2)[:2000])  # Print first 2000 chars for debug
        else:
            print(f"Failed to fetch departures: {departure_response.text}")

        # Sort arrivals: landed flights at the top, then by scheduled timestamp
        arrivals.sort(key=lambda x: (x['status_class'] != 'landed', x.get('scheduled_timestamp', 0)))

        # Sort by scheduled timestamp (including flights with no carrier/logo)
        departures.sort(key=lambda x: x.get('scheduled_timestamp', 0))

        result = {
            'departures': departures,
            'arrivals': arrivals
        }
        # Only raise if BOTH API requests failed (not just empty lists)
        if (arrival_response.status_code != 200) and (departure_response.status_code != 200):
            print("CRITICAL: Failed to get ANY data from FlightRadar24 (HTTP error)")
            raise Exception("No data available from FlightRadar24")
        # If both lists are empty but HTTP was 200, just return empty lists (board will show 'No arrivals/departures')
        print(f"Returning FlightRadar24 data: {len(departures)} departures, {len(arrivals)} arrivals")
        return result
    except Exception as e:
        print(f"ERROR: Could not fetch FlightRadar24 data: {str(e)}")
        raise Exception(f"Failed to fetch FlightRadar24 data: {str(e)}")