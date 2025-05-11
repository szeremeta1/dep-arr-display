# Departure/Arrival Display
![image](https://github.com/user-attachments/assets/f4cca52e-d8c8-4d1e-a452-2f264c24e246)
This project displays a departures and arrivals board for any airport using live flight data from the FlightRadar24 API. It also shows full aircraft model names and registration numbers using a local CSV lookup. The design is minimalist and optimized for FBO lobbies, pilot lounges, and small airports.

---

## Background

Originally developed for [KBLM (Monmouth Executive Airport)](https://fids.monmouthpilot.com), this board is intentionally simple: no gate, terminal, or baggage info—just scheduled/estimated times, flight numbers, aircraft types, and carriers. The design is responsive and suitable for TVs, tablets, and mobile devices.

---

## Features

- **Live Departures and Arrivals:** Fetches and displays up-to-date flight information for the configured airport.
- **Full Aircraft Model Names:** Uses a local CSV to display the full aircraft model name and N-number.
- **Real-Time Weather Widget:** Displays current temperature and conditions for the airport location.
- **Digital Clock:** Shows current time with blinking separators for at-a-glance time reference.
- **Minimalist Display:** No gates, terminals, or baggage info—just the essentials for a small airport.
- **Carrier Logos:** Displays carrier logos when available.
- **Flight Status Indicators:** Color-coded status indicators for scheduled, estimated, delayed, and early flights.
- **Automatic Refresh:** The board refreshes automatically every 60 seconds (customizable).
- **Error Handling:** Displays error messages if data cannot be fetched.
- **Easy Customization:** Change the airport or display settings via `config.json`.
- **Local Caching:** Aircraft type lookups are cached locally to minimize repeated lookups.
- **Responsive Design:** Optimized for display on TVs, tablets, and mobile devices.
- **Last Update Indicator:** Shows when the flight data was last refreshed.
- **Custom Airport Branding:** Easily customizable with your own airport/FBO logo.

---

## Setup

### 1. Get API Key

- **FlightRadar24:**  
  Sign up for the FlightRadar24 API [here]([https://www.flightradar24.com/premium/](https://fr24api.flightradar24.com)) (the Explorer plan at $9/month is sufficient).

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Aircraft Data CSV

The system requires a CSV file containing aircraft type codes and their full names:

- The default file should be placed at `src/static/aircraft_data.csv`
- The CSV must have at least two columns named `ICAO_Code` and `Model_FAA`
- You can use publicly available aircraft type databases or create your own

Example CSV format:
```
ICAO_Code,Model_FAA,Manufacturer
C172,Cessna 172 Skyhawk,Cessna
PC12,Pilatus PC-12,Pilatus
CL35,Challenger 350,Bombardier
```

### 4. Configure API Key and Settings

Edit `config.json` and add your API key and airport details:

```json
{
  "airport_code": "KBLM",
  "airport_coordinates": {
    "latitude": 40.1865,
    "longitude": -74.1258,
    "radius": 25
  },
  "api_url": "https://api.flightradar24.com/common/v1/airport.json",
  "refresh_interval": 60,
  "fr24_api_key": "YOUR_FLIGHTRADAR24_API_KEY",
  "username": "",
  "password": ""
}
```

- Change `"airport_code"` to any ICAO airport code
- Update `"airport_coordinates"` to match your airport's location
  - You can find these coordinates from various aviation resources or Google Maps
  - The `"radius"` defines how far from the airport (in km) to include flights
- Set `"refresh_interval"` to your preferred update frequency (in seconds)
- Add your FlightRadar24 API key to `"fr24_api_key"`

### 5. Add Your Airport/FBO Logo

- Replace `src/static/images/monmouth-jet-center-logo.png` with your own logo
- For best results, use a transparent PNG with a height of 120-200px

### 6. Carrier Logos (Optional)

- Add airline/operator logos to `src/static/images/` as PNG files
- Update the carrier mapping in `src/app.py` as needed:
  ```python
  mapping = {
      'NetJets': 'netjets.png',
      'Vista America': 'vistajet.png',
      # Add your own mappings here
  }
  ```

### 7. Run the application

```bash
python src/app.py
```

### 8. Access the board in your browser

Open [http://localhost:5000](http://localhost:5000) in your browser.

### 9. Production Deployment (Optional)

For a production setup, consider using:
- Gunicorn or uWSGI as the WSGI server
- Nginx as a reverse proxy
- Supervisor to manage the process
- SSL certificate for HTTPS

---

## How It Works

- **Flight Data:**  
  Flight information is fetched from the FlightRadar24 API.
- **Aircraft Type Lookup:**  
  The aircraft code (e.g., "CL35") is looked up in a local CSV (`src/static/aircraft_data.csv`), which returns the full model name (e.g., "Challenger 350"). Results are cached in `data/aircraft_cache.json` for efficiency.
- **Weather Data:**  
  Real-time weather is fetched from the Open-Meteo API based on the airport coordinates.
- **Display:**  
  The board shows scheduled and estimated times, flight numbers, full aircraft model names, registration numbers, and carrier logos (if available).

---

## Project Structure

- [`src/app.py`](src/app.py): Main Flask application.
- [`src/services/flight_data_fetcher.py`](src/services/flight_data_fetcher.py): Fetches and parses flight data from FlightRadar24.
- [`src/services/aircraft_data_service.py`](src/services/aircraft_data_service.py): Loads aircraft model names from a local CSV.
- [`src/templates/index.html`](src/templates/index.html): Jinja2 template for the flight board display.
- [`src/static/`](src/static/): Static assets (CSS, JS, images).
  - [`src/static/css/styles.css`](src/static/css/styles.css): Main stylesheet for the board.
  - [`src/static/images/`](src/static/images/): Carrier and airport logos.
  - [`src/static/aircraft_data.csv`](src/static/aircraft_data.csv): Local CSV for aircraft type lookups.
- [`config.json`](config.json): Configuration file for airport and API settings.
- [`data/aircraft_cache.json`](data/aircraft_cache.json): Local cache for aircraft type lookups (created automatically).

---

## Customization

- **Airport:**  
  Change the `"airport_code"` and coordinates in `config.json` to any ICAO code supported by FlightRadar24.
- **Logos:**  
  Add carrier logos as PNG files to `src/static/images/` and update the carrier mapping in `src/app.py` if needed.
- **Refresh Rate:**  
  Adjust `"refresh_interval"` in `config.json` (in seconds).
- **Weather Widget:**  
  The weather widget uses airport coordinates from `config.json` automatically.
- **Color Scheme:**  
  Edit `src/static/css/styles.css` to change colors and appearance.
- **Layout:**  
  Modify `src/templates/index.html` for major layout changes or to add new widgets.

---

## Notes

- Designed for small airports and FBOs, but can be adapted for any airport supported by FlightRadar24.
- Carrier logos are matched by name and must be present in `src/static/images/` to display.
- All flight data is obtained from the FlightRadar24 API.
- Weather data is obtained from the free Open-Meteo API.
- Aircraft type lookups are cached locally to reduce repeated lookups and speed up display.
- The board is intended for informational use only and is not an official source of flight information.
- The default setup refreshes the webpage every 60 seconds which is suitable for a display-only kiosk.

---

## Troubleshooting

- **No aircraft model name shown:**  
  Make sure the aircraft code exists in `src/static/aircraft_data.csv`. The system will fall back to showing just the code if not found.
- **No flight data:**  
  Ensure your FlightRadar24 API key is correct and your subscription is active. Check console logs for specific error messages.
- **Carrier logo missing:**  
  Add the logo PNG to `src/static/images/` and/or update the mapping in `src/app.py`.
- **Weather widget not showing:**  
  Verify your airport coordinates are correct in `config.json`.
- **App not starting:**  
  Check that all dependencies are installed and your Python version is compatible (Python 3.7+ recommended).
- **Changes to code not appearing:**  
  If running in debug mode, try hard-refreshing your browser (Ctrl+F5 or Cmd+Shift+R).

---

## License

This project is licensed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for details.

---

## Credits

Made by Alexander Szeremeta — All Data Courtesy of FlightRadar24.
