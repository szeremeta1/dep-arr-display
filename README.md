# KBLM Flight Board

This project displays a departures and arrivals board for any airport of your choosing using live flight data from the FlightRadar24 API.

## Background

This project was originally developed for KBLM (Monmouth Executive Airport), a popular jet center in the northeast United States. KBLM is a smaller general aviation airport, primarily serving private and charter jets, so the board is intentionally simple: there is no gate, terminal, or baggage information, and the focus is on scheduled and estimated times, flight numbers, aircraft types, and carriers. The design is optimized for FBO lobbies and pilot lounges, where concise, real-time information is most useful.

## Features

- **Live Departures and Arrivals:** Fetches and displays up-to-date flight information for the configured airport.
- **Minimalist Display:** No gates, terminals, or baggage info—just the essentials for a small airport.
- **Carrier Logos:** Displays carrier logos when available.
- **Automatic Refresh:** The board refreshes automatically every 60 seconds.
- **Error Handling:** Displays error messages if data cannot be fetched.
- **Easy Customization:** Change the airport or display settings via `config.json`.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   python src/app.py
   ```

3. **Access the board in your browser:**
   ```
   http://localhost:5000
   ```

## Configuration

Edit [`config.json`](config.json) to set the airport code, API URL, refresh interval, and other options. By default, it is set up for KBLM.

Example:
```json
{
  "airport_code": "KBLM",
  "refresh_interval": 60,
  "fr24_api_key": "YOUR_API_KEY_HERE"
}
```

## Project Structure

- [`src/app.py`](src/app.py): Main Flask application.
- [`src/services/flight_data_fetcher.py`](src/services/flight_data_fetcher.py): Fetches and parses flight data from FlightRadar24.
- [`src/templates/index.html`](src/templates/index.html): Jinja2 template for the flight board display.
- [`src/static/`](src/static/): Static assets (CSS, JS, images).
- [`config.json`](config.json): Configuration file for airport and API settings.

## Notes

- This project is designed for small airports and FBOs, but can be adapted for any airport supported by FlightRadar24.
- Carrier logos are matched by name and must be present in `src/static/images/` to display.
- All data is obtained from the FlightRadar24 API. Personally, I have the cheapest ($9/month "Explorer") plan.

## License

This project is licensed under the GNU General Public License v3.0. See [`LICENSE`](LICENSE) for details.