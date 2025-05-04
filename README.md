# Departure/Arrival Display

This project displays a departures and arrivals board for any airport of your choosing using live flight data from the FlightRadar24 API. It also shows full aircraft model names and registration numbers using the AviationStack API.

---

## Background

This project was originally developed for KBLM (Monmouth Executive Airport), a popular jet center in the northeast United States. KBLM is a smaller general aviation airport, primarily serving private and charter jets, so the board is intentionally simple: there is no gate, terminal, or baggage information, and the focus is on scheduled and estimated times, flight numbers, aircraft types, and carriers. The design is optimized for FBO lobbies and pilot lounges, where concise, real-time information is most useful.

---

## Features

- **Live Departures and Arrivals:** Fetches and displays up-to-date flight information for the configured airport.
- **Full Aircraft Model Names:** Uses the AviationStack API to display the full aircraft model name and N-number.
- **Minimalist Display:** No gates, terminals, or baggage info—just the essentials for a small airport.
- **Carrier Logos:** Displays carrier logos when available.
- **Automatic Refresh:** The board refreshes automatically every 60 seconds.
- **Error Handling:** Displays error messages if data cannot be fetched.
- **Easy Customization:** Change the airport or display settings via `config.json`.
- **Local Caching:** Aircraft type lookups are cached locally to minimize API calls.

---

## Setup

### 1. Get API Keys

- **FlightRadar24:**  
  Sign up for a FlightRadar24 subscription [here](https://www.flightradar24.com/premium/) (the Explorer plan at $9/month is sufficient).
- **AviationStack:**  
  Sign up for a free AviationStack account [here](https://aviationstack.com/) to get an API key for aircraft type lookups.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure API Keys

Edit [`config.json`](config.json) and add your API keys:

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
  "aviationstack_key": "YOUR_AVIATIONSTACK_API_KEY",
  "username": "",
  "password": ""
}
```

### 4. Run the application

```bash
python src/app.py
```

### 5. Access the board in your browser

```
http://localhost:5000
```

---

## How It Works

- **Flight Data:**  
  Flight information is fetched from the FlightRadar24 API.
- **Aircraft Type Lookup:**  
  The aircraft code (e.g., "CL35") is sent to the AviationStack API, which returns the full model name (e.g., "Challenger 350"). Results are cached in `data/aircraft_cache.json` for efficiency.
- **Display:**  
  The board shows scheduled and estimated times, flight numbers, full aircraft model names, registration numbers, and carrier logos (if available).

---

## Project Structure

- [`src/app.py`](src/app.py): Main Flask application.
- [`src/services/flight_data_fetcher.py`](src/services/flight_data_fetcher.py): Fetches and parses flight data from FlightRadar24.
- [`src/services/aviation_stack_service.py`](src/services/aviation_stack_service.py): Looks up full aircraft model names using AviationStack and caches results.
- [`src/templates/index.html`](src/templates/index.html): Jinja2 template for the flight board display.
- [`src/static/`](src/static/): Static assets (CSS, JS, images).
- [`config.json`](config.json): Configuration file for airport and API settings.
- [`data/aircraft_cache.json`](data/aircraft_cache.json): Local cache for aircraft type lookups (created automatically).

---

## Customization

- **Airport:**  
  Change the `"airport_code"` in `config.json` to any ICAO code supported by FlightRadar24.
- **Logos:**  
  Add carrier logos as PNG files to `src/static/images/` and update the carrier mapping in `app.py` if needed.
- **Refresh Rate:**  
  Adjust `"refresh_interval"` in `config.json` (in seconds).

---

## Notes

- This project is designed for small airports and FBOs, but can be adapted for any airport supported by FlightRadar24.
- Carrier logos are matched by name and must be present in `src/static/images/` to display.
- All data is obtained from the FlightRadar24 and AviationStack APIs.
- Aircraft type lookups are cached locally to reduce API usage and speed up display.

---

## Troubleshooting

- **No aircraft model name shown:**  
  Make sure your AviationStack API key is valid and you have internet access. The cache will fall back to the code if the API is unavailable.
- **No flight data:**  
  Ensure your FlightRadar24 API key is correct and your subscription is active.
- **Carrier logo missing:**  
  Add the logo PNG to `src/static/images/` and/or update the mapping in `app.py`.

---

## License

This project is licensed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for details.

---

## Credits

Made by Alexander Szeremeta — All Data Courtesy of FlightRadar24 and AviationStack.
