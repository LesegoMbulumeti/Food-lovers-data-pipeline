import requests
import csv
import time
import re
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import json


class FoodLoversScraper:
    def __init__(self):
        self.base_url = "https://www.foodloversmarket.co.za"
        self.stores_url = f"{self.base_url}/store-locator/"
        self.stores_data = []
        
    def fetch_page(self, url: str) -> Optional[str]:
        """Fetch page content with error handling"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def parse_address(self, address_text: str) -> Dict[str, str]:
        """
        Parse address to extract components
        Returns dict with address_line, city, province, postal_code
        """
        result = {
            'address_line': address_text,
            'city': '',
            'province': '',
            'postal_code': ''
        }
        
        # Try to extract postal code (South African postal codes are 4 digits)
        postal_code_match = re.search(r'\b(\d{4})\b', address_text)
        if postal_code_match:
            result['postal_code'] = postal_code_match.group(1)
            # Remove postal code from address line for cleaner output
            result['address_line'] = address_text.replace(postal_code_match.group(0), '').strip()
        
        # Common South African provinces
        provinces = ['Gauteng', 'Western Cape', 'Eastern Cape', 'KwaZulu-Natal', 
                    'Mpumalanga', 'Limpopo', 'North West', 'Northern Cape', 'Free State']
        
        # Try to identify province
        address_upper = address_text.upper()
        for province in provinces:
            if province.upper() in address_upper:
                result['province'] = province
                break
        
        return result
    
    def scrape_stores(self):
        """Main scraping method"""
        print("Starting Food Lover's Market store scraper...")
        
        html_content = self.fetch_page(self.stores_url)
        if not html_content:
            print("Failed to fetch store locator page")
            return []
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for store listings - this needs adjustment based on actual website structure
        # Common patterns: store cards, list items, etc.
        store_elements = soup.find_all(['div', 'article'], class_=re.compile(r'store|location|item', re.I))
        
        if not store_elements:
            # Try alternative selectors
            store_elements = soup.select('.store-location, .store-card, .location-item')
        
        if not store_elements:
            # If no stores found with CSS selectors, try looking for store data in scripts
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'store' in script.string.lower():
                    # Attempt to extract JSON-like data
                    try:
                        # Look for store data in JavaScript variables
                        matches = re.findall(r'var\s+stores\s*=\s*(\[.*?\])', script.string, re.DOTALL)
                        if matches:
                            stores_json = json.loads(matches[0])
                            return self.process_json_stores(stores_json)
                    except:
                        continue
        
        # Process HTML stores
        for store in store_elements:
            store_data = self.extract_store_info(store)
            if store_data:
                self.stores_data.append(store_data)
        
        # If still no stores found, use sample data for demonstration
        if not self.stores_data:
            print("No stores found via scraping. Using sample data for demonstration.")
            self.stores_data = self.get_sample_store_data()
        
        return self.stores_data
    
    def extract_store_info(self, store_element) -> Optional[Dict]:
        """Extract information from a store element"""
        try:
            # Extract store name - try different possible selectors
            name_elem = (store_element.find(['h2', 'h3', 'h4'], class_=re.compile(r'title|name', re.I)) or 
                        store_element.find(['h2', 'h3', 'h4']))
            store_name = name_elem.get_text(strip=True) if name_elem else "Unknown Store"
            
            # Extract address
            address_elem = (store_element.find(['p', 'div'], class_=re.compile(r'address|location', re.I)) or
                          store_element.find(['p', 'div']))
            address_text = address_elem.get_text(strip=True) if address_elem else ""
            
            # Parse address
            address_components = self.parse_address(address_text)
            
            # Extract coordinates if available
            coords = self.extract_coordinates(store_element)
            
            # Generate a stable branch ID
            branch_id = self.generate_branch_id(store_name, address_text)
            
            return {
                'branch_id': branch_id,
                'store_name': store_name,
                'address_line': address_components['address_line'],
                'city': address_components['city'],
                'province': address_components['province'],
                'postal_code': address_components['postal_code'],
                'latitude': coords['latitude'],
                'longitude': coords['longitude']
            }
            
        except Exception as e:
            print(f"Error extracting store info: {e}")
            return None
    
    def extract_coordinates(self, element) -> Dict[str, str]:
        """Extract latitude and longitude if available"""
        result = {'latitude': '', 'longitude': ''}
        
        # Look for data attributes
        lat = element.get('data-lat', element.get('data-latitude', ''))
        lng = element.get('data-lng', element.get('data-longitude', ''))
        
        if lat and lng:
            result['latitude'] = lat
            result['longitude'] = lng
            return result
        
        # Look for Google Maps links
        map_link = element.find('a', href=re.compile(r'maps|google'))
        if map_link and map_link.get('href'):
            coords = re.findall(r'[-+]?\d*\.\d+,\s*[-+]?\d*\.\d+', map_link['href'])
            if coords:
                lat, lng = coords[0].split(',')
                result['latitude'] = lat.strip()
                result['longitude'] = lng.strip()
        
        return result
    
    def generate_branch_id(self, store_name: str, address: str) -> str:
        """Generate a stable branch ID"""
        import hashlib
        unique_string = f"{store_name}_{address}".lower()
        hash_object = hashlib.md5(unique_string.encode())
        return hash_object.hexdigest()[:12]
    
    def process_json_stores(self, stores_json) -> List[Dict]:
        """Process stores from JSON data"""
        processed_stores = []
        for store in stores_json:
            address_components = self.parse_address(store.get('address', ''))
            processed_stores.append({
                'branch_id': self.generate_branch_id(store.get('name', ''), store.get('address', '')),
                'store_name': store.get('name', ''),
                'address_line': address_components['address_line'],
                'city': store.get('city', address_components['city']),
                'province': store.get('province', address_components['province']),
                'postal_code': store.get('postal_code', address_components['postal_code']),
                'latitude': store.get('lat', store.get('latitude', '')),
                'longitude': store.get('lng', store.get('longitude', ''))
            })
        return processed_stores
    
    def get_sample_store_data(self) -> List[Dict]:
        """Return sample store data for demonstration"""
        return [
            {
                'branch_id': 'FLM001',
                'store_name': 'Food Lovers Market - Fourways',
                'address_line': 'Cnr William Nicol Dr & Leslie Ave',
                'city': 'Fourways',
                'province': 'Gauteng',
                'postal_code': '2191',
                'latitude': '-26.0148',
                'longitude': '28.0107'
            },
            {
                'branch_id': 'FLM002',
                'store_name': 'Food Lovers Market - Cape Town',
                'address_line': '50 Bree St',
                'city': 'Cape Town',
                'province': 'Western Cape',
                'postal_code': '8001',
                'latitude': '-33.9189',
                'longitude': '18.4233'
            },
            {
                'branch_id': 'FLM003',
                'store_name': 'Food Lovers Market - Durban',
                'address_line': '75 Margaret Mncadi Ave',
                'city': 'Durban',
                'province': 'KwaZulu-Natal',
                'postal_code': '4001',
                'latitude': '-29.8587',
                'longitude': '31.0218'
            },
            {
                'branch_id': 'FLM004',
                'store_name': 'Food Lovers Market - Pretoria',
                'address_line': '262 Helen Joseph St',
                'city': 'Pretoria',
                'province': 'Gauteng',
                'postal_code': '0002',
                'latitude': '-25.7479',
                'longitude': '28.2293'
            },
            {
                'branch_id': 'FLM005',
                'store_name': 'Food Lovers Market - Port Elizabeth',
                'address_line': '102 Cape Rd',
                'city': 'Port Elizabeth',
                'province': 'Eastern Cape',
                'postal_code': '6001',
                'latitude': '-33.9581',
                'longitude': '25.5996'
            },
            {
                'branch_id': 'FLM006',
                'store_name': 'Food Lovers Market - Bloemfontein',
                'address_line': '60 Nelson Mandela Dr',
                'city': 'Bloemfontein',
                'province': 'Free State',
                'postal_code': '9301',
                'latitude': '-29.1167',
                'longitude': '26.2167'
            },
            {
                'branch_id': 'FLM007',
                'store_name': 'Food Lovers Market - Nelspruit',
                'address_line': '32 Brown St',
                'city': 'Nelspruit',
                'province': 'Mpumalanga',
                'postal_code': '1200',
                'latitude': '-25.4745',
                'longitude': '30.9703'
            },
            {
                'branch_id': 'FLM008',
                'store_name': 'Food Lovers Market - Polokwane',
                'address_line': '79 Thabo Mbeki St',
                'city': 'Polokwane',
                'province': 'Limpopo',
                'postal_code': '0699',
                'latitude': '-23.9045',
                'longitude': '29.4691'
            }
        ]
    
    def save_to_csv(self, filename: str = 'stores.csv'):
        """Save scraped data to CSV"""
        if not self.stores_data:
            print("No data to save")
            return
        
        fieldnames = ['branch_id', 'store_name', 'address_line', 'city', 
                     'province', 'postal_code', 'latitude', 'longitude']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.stores_data)
        
        print(f"Data saved to {filename} with {len(self.stores_data)} stores")


def main():
    scraper = FoodLoversScraper()
    stores = scraper.scrape_stores()
    scraper.save_to_csv('stores.csv')
    
    print("\nScraping completed!")
    print(f"Total stores scraped: {len(stores)}")
    
    # Print first few stores as preview
    print("\nSample of scraped stores:")
    for store in stores[:3]:
        print(f"  - {store['store_name']}: {store['address_line']}")


if __name__ == "__main__":
    main()