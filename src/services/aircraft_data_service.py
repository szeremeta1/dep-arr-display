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
        - Remove manufacturer (first word) except for Gulfstream
        - Keep manufacturer for Cessna models that are just numbers/letters+numbers
        """
        if not name or ' ' not in name:
            return name
            
        parts = name.split(' ')
        manufacturer = parts[0]
        
        # Always keep Gulfstream
        if manufacturer.lower() == 'gulfstream':
            return name
            
        # Keep "Cessna" for simple model names (C172, 172, etc.)
        if manufacturer.lower() == 'cessna':
            remainder = ' '.join(parts[1:])
            # Check if the remainder is just numbers or 1-2 letters + numbers
            if re.match(r'^[A-Z]{0,2}\d+$', remainder.replace(' ', '')):
                return name
        
        # For all other cases, remove the manufacturer
        return ' '.join(parts[1:])
        
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