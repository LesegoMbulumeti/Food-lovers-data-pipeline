import re
from typing import Dict, Optional

class AddressParser:
    """Parse South African addresses to extract components"""
    
    PROVINCES = {
        'Gauteng': ['gauteng', 'gp', 'johannesburg', 'pretoria', 'centurion', 'midrand'],
        'Western Cape': ['western cape', 'wc', 'cape town', 'stellenbosch', 'paarl'],
        'KwaZulu-Natal': ['kzn', 'kwazulu', 'natal', 'durban', 'pietermaritzburg'],
        'Eastern Cape': ['eastern cape', 'ec', 'port elizabeth', 'east london'],
        'Mpumalanga': ['mpumalanga', 'nelspruit', 'mbombela'],
        'Limpopo': ['limpopo', 'polokwane'],
        'North West': ['north west', 'rustenburg', 'mahikeng'],
        'Free State': ['free state', 'bloemfontein'],
        'Northern Cape': ['northern cape', 'kimberley']
    }
    
    @staticmethod
    def parse(address_text: str) -> Dict[str, str]:
        """Parse address into components"""
        result = {
            'address_line': address_text.strip(),
            'city': '',
            'province': '',
            'postal_code': ''
        }
        
        if not address_text:
            return result
            
        # Extract postal code (4 digits)
        postal_match = re.search(r'\b(\d{4})\b', address_text)
        if postal_match:
            result['postal_code'] = postal_match.group(1)
            result['address_line'] = address_text.replace(postal_match.group(0), '').strip()
        
        # Extract province
        address_lower = address_text.lower()
        for province, keywords in AddressParser.PROVINCES.items():
            for keyword in keywords:
                if keyword in address_lower:
                    result['province'] = province
                    break
            if result['province']:
                break
        
        return result
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Validate GPS coordinates"""
        return -90 <= lat <= 90 and -180 <= lon <= 180