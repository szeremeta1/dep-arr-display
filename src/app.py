from flask import Flask, render_template, jsonify # type: ignore
from services.flight_data_fetcher import fetch_flight_data
import threading
import time
import json
import os
import sys
import traceback
from datetime import datetime
import pytz # type: ignore

app = Flask(__name__)

# Get the absolute path to the project directory
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(project_dir, 'config.json')

try:
    with open(config_path) as config_file:
        config = json.load(config_file)
    print(f"Successfully loaded config from {config_path}")
    print(f"Config contents: {config}")
except Exception as e:
    print(f"Error loading config from {config_path}: {e}")
    sys.exit(1)

flight_data = {"departures": [], "arrivals": []}
last_successful_update = None
error_message = None

def update_flight_data():
    global flight_data, last_successful_update, error_message
    while True:
        try:
            print("Fetching flight data...")
            new_data = fetch_flight_data(config["airport_code"], config)
            flight_data = new_data
            
            # Get current time in EDT timezone
            eastern = pytz.timezone('America/New_York')
            now = datetime.now(eastern)
            last_successful_update = now.strftime("%-I:%M %p")  # No leading zeros
            
            error_message = None
            print(f"Updated flight data: {len(flight_data['departures'])} departures, {len(flight_data['arrivals'])} arrivals")
        except Exception as e:
            print(f"ERROR updating flight data: {str(e)}")
            error_message = str(e)
            traceback.print_exc()
        
        # Sleep for the configured interval
        time.sleep(config.get("refresh_interval", 60))

# Register the filter using the decorator approach
@app.template_filter('carrier_logo')
def carrier_logo_filename(carrier):
    """Find logo for carrier if it exists, otherwise return empty string"""
    if not carrier:
        return ''
    
    # Map common carriers to their logo filenames
    mapping = {
        'NetJets': 'netjets.png',
        'Vista America': 'vistajet.png',
        'Flexjet': 'flexjet.png',
        'flyExclusive': 'flyexclusive.png',
        'Red Wing Aviation': 'redwingaviation.png',
        'Wheels Up': 'wheelsup.png',
        'Silver Air': 'silverair.png',
        'XOJET': 'xojet.png',
        'Baker Aviation': 'bakeraviation.png',
        'PlaneSense': 'planesense.png',
        'Ventura': 'ventura.png',
        'Pacific Coast Jet': 'pacificcoastjet.png',
        'Global Air Charters': 'globalaircharters.png',
        'Private Jet Center': 'privatejetcenter.png',
        'Executive Fliteways': 'executivefliteways.png',
        'Tradewind Aviation': 'tradewindaviation.png',
        'Aero-Tech Services': 'aerotechservices.png',
        'Shoreline Aviation': 'shorelineaviation.png',
        'Northern Jet Management': 'northernjetmanagement.png',
        'Aircraft Management Group': 'aircraftmanagementgroup.png',
        'Fly Alliance': 'flyalliance.png',
        'Air Methods': 'airmethods.png',
        'Mountain Aviation': 'mountainaviation.png',
        'Jet Linx Aviation': 'jetlinxaviation.png',
        'Thrive': 'thrive.png',
        'Jet Aviation Flight Services': 'jetaviation.png',
        'Fltplan': 'fltplan.png',
        # Add more mappings as needed
    }
    
    # Look for the carrier in our mapping
    filename = mapping.get(carrier, carrier.lower().replace(' ', '') + '.png')
    
    # Check if file exists in static directory
    static_path = os.path.join(project_dir, 'src', 'static', 'images', filename)
    if os.path.exists(static_path):
        return filename
        
    # If no logo found, return empty string but don't filter out the flight
    print(f"No logo found for carrier: {carrier}")
    return ''

@app.route('/')
def index():
    # Get current time in EDT timezone
    eastern = pytz.timezone('America/New_York')
    now = datetime.now(eastern)
    current_time = now.strftime("%-I:%M %p")  # No leading zeros
    
    return render_template('index.html', 
                          flights=flight_data, 
                          airport_code=config.get("airport_code", "KBLM"),
                          last_update=last_successful_update or current_time,
                          error=error_message)

@app.route('/preview-image')
def preview_image():
    """Generate a preview image for social sharing"""
    from flask import send_file # type: ignore
    from PIL import Image, ImageDraw, ImageFont # type: ignore
    import io
    
    # Create a new image with your site's appearance
    width, height = 1200, 630  # Standard OG image size
    img = Image.new('RGB', (width, height), color=(26, 26, 26))
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts (fallback to default if not available)
    try:
        title_font = ImageFont.truetype('Arial.ttf', 60)
        subtitle_font = ImageFont.truetype('Arial.ttf', 40)
    except IOError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Add text
    draw.text((60, 180), 'KBLM - Monmouth Executive Airport', fill=(82, 107, 132), font=title_font)
    draw.text((60, 280), 'Flight Board', fill=(255, 255, 255), font=title_font)
    
    # Try to add logo
    try:
        logo = Image.open(os.path.join(project_dir, 'src', 'static', 'images', 'monmouth-jet-center-logo.png'))
        logo = logo.resize((200, 200))
        img.paste(logo, (width - 280, 60), logo if logo.mode == 'RGBA' else None)
    except Exception as e:
        print(f"Could not add logo to preview: {e}")
    
    # Save to bytes
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    return send_file(img_io, mimetype='image/png')

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'ok' if error_message is None else 'error',
        'last_update': last_successful_update,
        'error': error_message,
        'count': {
            'departures': len(flight_data['departures']),
            'arrivals': len(flight_data['arrivals'])
        }
    })

if __name__ == '__main__':
    # Start the background thread for fetching data
    data_thread = threading.Thread(target=update_flight_data, daemon=True)
    data_thread.start()
    
    # Run the Flask application
    app.run(debug=True, host='0.0.0.0')