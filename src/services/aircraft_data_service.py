import os
import csv
import re

class AircraftDataService:
    def __init__(self, config=None):
        # config is kept for potential future use
        self.config = config or {}
        
        # Updated path to the CSV file in the static directory
        csv_filename = 'aircraft_data.csv'
        # Navigate up from services to src, then into static
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', csv_filename)
        
        # Load aircraft data from CSV
        self.aircraft_data = self._load_aircraft_data()
        print(f"Initialized AircraftDataService with {len(self.aircraft_data)} aircraft mappings from CSV.")
        
    def _load_aircraft_data(self):
        """Load aircraft data from CSV file."""
        aircraft_dict = {}
        try:
            # Check if file exists
            if not os.path.isfile(self.csv_path):
                print(f"Warning: CSV file not found at {self.csv_path}")
                return {}
                
            with open(self.csv_path, 'r') as csvfile:
                # Create a CSV reader
                reader = csv.reader(csvfile)
                
                # Read headers
                headers = next(reader)
                
                # Find indices for ICAO_Code and Model_FAA
                try:
                    icao_idx = headers.index('ICAO_Code')
                    model_idx = headers.index('Model_FAA')
                except ValueError as e:
                    print(f"Error: Required column not found in CSV: {e}")
                    return {}
                
                # Process each row
                for row in reader:
                    if len(row) > max(icao_idx, model_idx):
                        icao_code = row[icao_idx].strip()
                        model_name = row[model_idx].strip()
                        if icao_code and model_name:
                            aircraft_dict[icao_code] = model_name
            
            return aircraft_dict
        except Exception as e:
            print(f"Error loading aircraft data from CSV: {e}")
            # Return an empty dictionary on error
            return {}
    
    def _format_aircraft_name(self, name):
        """Format aircraft name according to rules:
        - Keep the full name by default
        - Remove any text after a slash (/) character
        - Only remove the first word (manufacturer) if the full name exceeds 20 characters
        """
        if not name:
            return name
            
        # First, handle slash removal - keep only text before slash
        if '/' in name:
            name = name.split('/')[0].strip()
            
        # If the name is shorter than or equal to 20 characters, return as-is
        if len(name) <= 20:
            return name
        
        # If longer than 20 chars, remove the first word (assumed to be manufacturer)
        parts = name.split(' ')
        if len(parts) > 1:
            return ' '.join(parts[1:])
            
        # If there's only one word, return as is
        return name
        
    def get_aircraft_name(self, code):
        """Get full aircraft name from ICAO code using the loaded CSV data."""
        if not code or code == 'N/A':
            return 'Unknown'
            
        # Normalize the code
        code = code.strip().upper()
        
        # Look up in the CSV-loaded dictionary
        name = self.aircraft_data.get(code)
        
        if name:
            # Format the name according to our rules before returning
            return self._format_aircraft_name(name)
        else:
            # If code not found in our dictionary, return the code itself
            print(f"Aircraft code '{code}' not found in CSV data. Returning code.")
            return code