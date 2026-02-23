# 🛒 Food Lover's Market Store Location Pipeline

A Python-based data pipeline that scrapes Food Lover's Market store locations and loads them into SQL Server.

## 📋 Project Files

- **`scrape.txt`** - Web scraper that collects store data from Food Lover's Market website
- **`load.txt`** - Python script to load CSV data into SQL Server
- **`create_table.sql`** - SQL Server table creation script
- **`stores.csv`** - Sample output with store location data

## 🚀 Features

- Web scraping of store locations
- Data cleaning and validation
- CSV export functionality
- SQL Server integration
- Automated data loading with upsert capability

## 🛠️ Technologies Used

- Python 3.10+
- BeautifulSoup4 for web scraping
- Pandas for data processing
- pyODBC for SQL Server connection
- SQL Server for data storage

## 📊 Data Fields

- `branch_id` - Unique store identifier
- `store_name` - Store name
- `address_line` - Street address
- `city` - City or suburb
- `province` - South African province
- `postal_code` - Postal code
- `latitude` - GPS latitude
- `longitude` - GPS longitude

## 🏁 Getting Started

1. Clone the repository
2. Set up virtual environment: `python3 -m venv venv`
3. Activate it: `source venv/bin/activate`
4. Install requirements: `pip install -r requirements.txt`
5. Run scraper: `python scrape.txt`
6. Load data: `python load.txt`

## 👤 Author

**Lesego Mbulumeti**
- GitHub: [@LesegoMbulumeti](https://github.com/LesegoMbulumeti)
- Email: Lesegombulumeti2@gmail.com

## 📝 License

This project is open source and available for educational purposes.
