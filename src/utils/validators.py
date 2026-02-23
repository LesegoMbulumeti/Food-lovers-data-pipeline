import re
from typing import Any, Dict, List

class DataValidator:
    """Validate store data"""
    
    @staticmethod
    def validate_store(store: Dict[str, Any]) -> List[str]:
        """Validate a store record, return list of errors"""
        errors = []
        
        # Required fields
        required_fields = ['store_name', 'address_line']
        for field in required_fields:
            if not store.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Branch ID format
        branch_id = store.get('branch_id', '')
        if branch_id and not re.match(r'^[A-Za-z0-9_]+$', branch_id):
            errors.append(f"Invalid branch_id format: {branch_id}")
        
        # Coordinates
        lat = store.get('latitude')
        lon = store.get('longitude')
        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    errors.append(f"Invalid coordinates: {lat}, {lon}")
            except (ValueError, TypeError):
                errors.append(f"Non-numeric coordinates: {lat}, {lon}")
        
        return errors