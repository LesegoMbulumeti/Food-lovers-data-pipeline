📊 Dataset Fields
FieldTypeDescriptionbranch_idNVARCHAR(12)Stable unique identifier (MD5 hash of name + address)store_nameNVARCHAR(255)Store nameaddress_lineNVARCHAR(500)Full street addresscityNVARCHAR(100)City or suburbprovinceNVARCHAR(100)South African provincepostal_codeNVARCHAR(10)Postal codelatitudeDECIMAL(10,7)GPS latitudelongitudeDECIMAL(10,7)GPS longitude

🚀 How It Works
The pipeline runs in two steps:
1. Scrape — scraper.py calls the Food Lover's Market WordPress REST API (/wp-json/wp/v2/store), paginates through all records, parses and cleans each store's fields, then saves:

Raw API response → data/raw/stores_raw.json
Cleaned dataset → data/processed/stores.csv

2. Load — loader.py reads stores.csv and upserts each row into dbo.Stores on SQL Server using a MERGE statement, so the pipeline is safe to re-run without creating duplicates.

🛠️ Tech Stack

Python 3.9+
Requests — API calls
BeautifulSoup4 — HTML parsing
Pandas — data cleaning
pyODBC — SQL Server connection
SQL Server — data storage (via Docker locally)
python-dotenv — environment variable management


⚙️ Setup & Usage
1. Clone the repository
bashgit clone https://github.com/LesegoMbulumeti/Food-lovers-data-pipeline-for-location.git
cd Food-lovers-data-pipeline-for-location
2. Create and activate virtual environment
bashpython3 -m venv venv
source venv/bin/activate
3. Install dependencies
bashpip install -r requirements.txt
4. Configure environment variables
Create a .env file in the project root:
DB_SERVER=localhost
DB_DATABASE=FoodLovers
DB_USERNAME=SA
DB_PASSWORD=your_password
5. Set up SQL Server (Docker)
bashdocker run -e ACCEPT_EULA=Y -e SA_PASSWORD=your_password -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
6. Create the database and table
bashdocker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P your_password -No -Q "CREATE DATABASE FoodLovers"

docker cp sql/create_table.sql sqlserver:/create_table.sql

docker exec -it sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U SA -P your_password -No -d FoodLovers -i /create_table.sql
7. Run the scraper
bashpython src/scraper.py
8. Load data into SQL Server
bashpython src/loader.py

👤 Author
Lesego Mbulumeti

GitHub: @LesegoMbulumeti
Email: Lesegombulumeti2@gmail.com


📝 License
This project is open source and available for educational purposes.