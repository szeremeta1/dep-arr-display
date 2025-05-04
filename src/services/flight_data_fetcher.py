import requests # type: ignore
import time
import json
from datetime import datetime, timezone, timedelta
import os
import pytz # type: ignore

def fetch_flight_data(airport_code, config):
    """Fetch ALL FlightRadar24 data for the specified airport, including flights with no carrier or logo."""
    print(f"Fetching FlightRadar24 data for {airport_code}")
    
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
        if arrival_response.status_code == 200:
            arrival_data = arrival_response.json()
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
                        if times.get('scheduled', {}).get('arrival'):
                            utc_time = datetime.fromtimestamp(times['scheduled']['arrival'], timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            scheduled_time = local_time.strftime('%-I:%M %p')
                        if times.get('estimated', {}).get('arrival'):
                            utc_time = datetime.fromtimestamp(times['estimated']['arrival'], timezone.utc)
                            local_time = utc_time.astimezone(local_tz)
                            estimated_time = local_time.strftime('%-I:%M %p')
                        elif times.get('real', {}).get('arrival'):
                            utc_time = datetime.fromtimestamp(times['real']['arrival'], timezone.utc)
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
                        arrivals.append({
                            'scheduled_time': scheduled_time or 'N/A',
                            'estimated_time': estimated_time or 'N/A',
                            'delay_status': delay_status,
                            'flight': f.get('identification', {}).get('callsign')
                                      or f.get('identification', {}).get('number', {}).get('default', 'N/A'),
                            'aircraft': f.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
                            'origin': {
                                'code': f.get('airport', {}).get('origin', {}).get('code', {}).get('iata', 'N/A'),
                                'name': f.get('airport', {}).get('origin', {}).get('name', 'Unknown')
                            },
                            'status': f.get('status', {}).get('text', 'N/A'),
                            'carrier': f.get('airline', {}).get('name', '') if f.get('airline') else ''
                        })
                    except Exception as e:
                        print(f"Error parsing arrival flight: {str(e)}")
            else:
                print("No arrivals data found in response")
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
        if departure_response.status_code == 200:
            departure_data = departure_response.json()
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
                            'estimated_time': estimated_time or 'N/A',
                            'delay_status': delay_status,
                            'flight': f.get('identification', {}).get('callsign')
                                      or f.get('identification', {}).get('number', {}).get('default', 'N/A'),
                            'aircraft': f.get('aircraft', {}).get('model', {}).get('code', 'N/A'),
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
        else:
            print(f"Failed to fetch departures: {departure_response.text}")

        # Sort by scheduled time (including flights with no carrier/logo)
        departures.sort(key=lambda x: x.get('scheduled_time', ''))
        arrivals.sort(key=lambda x: x.get('scheduled_time', ''))

        result = {
            'departures': departures,
            'arrivals': arrivals
        }
        if len(departures) > 0 or len(arrivals) > 0:
            print(f"Returning all FlightRadar24 data: {len(departures)} departures, {len(arrivals)} arrivals")
            return result
        print("CRITICAL: Failed to get ANY data from FlightRadar24")
        raise Exception("No data available from FlightRadar24")
    except Exception as e:
        print(f"ERROR: Could not fetch FlightRadar24 data: {str(e)}")
        raise Exception(f"Failed to fetch FlightRadar24 data: {str(e)}")