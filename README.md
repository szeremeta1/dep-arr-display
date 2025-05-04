# KBLM Flight Board

This project displays a departures and arrivals board for any airport of your choosing using flight data from the FlightRadar24 API.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python src/app.py
   ```

3. Access the board in your browser at `http://localhost:5000`

## Configuration
Edit `config.json` to set the airport code, API URL, and refresh interval.