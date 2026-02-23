import os
import pandas as pd
import pyodbc
from dotenv import load_dotenv

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(ROOT_DIR, ".env"))

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "data", "processed", "stores.csv"
)

SERVER   = os.getenv("DB_SERVER",   "localhost")
DATABASE = os.getenv("DB_DATABASE", "FoodLovers")
USERNAME = os.getenv("DB_USERNAME", "")
PASSWORD = os.getenv("DB_PASSWORD", "")

if USERNAME and PASSWORD:
    CONN_STR = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        f"UID={USERNAME};PWD={PASSWORD};"
        "TrustServerCertificate=yes;"
    )
else:
    CONN_STR = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER={SERVER};DATABASE={DATABASE};"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )


def read_csv() -> pd.DataFrame:
    print(f"Reading {CSV_PATH} ...")
    df = pd.read_csv(CSV_PATH, dtype=str)

    str_cols = ["branch_id", "store_name", "address_line", "city", "province", "postal_code"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].str.strip().replace("nan", None)

    for col in ["latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    print(f"  {len(df)} rows loaded from CSV.")
    return df

# ------------------------------------------------------------------ load

def load_to_sqlserver(df: pd.DataFrame):
    print(f"\nConnecting to SQL Server ({SERVER} / {DATABASE}) ...")
    try:
        conn = pyodbc.connect(CONN_STR, timeout=10)
    except pyodbc.Error as e:
        print(f"  ERROR: Could not connect — {e}")
        return

    cursor = conn.cursor()

    # MERGE upsert — safe to re-run without creating duplicates
    merge_sql = """
        MERGE dbo.Stores AS target
        USING (SELECT ? AS branch_id) AS source ON target.branch_id = source.branch_id
        WHEN MATCHED THEN UPDATE SET
            store_name   = ?, address_line = ?, city        = ?,
            province     = ?, postal_code  = ?, latitude    = ?,
            longitude    = ?, loaded_at    = GETDATE()
        WHEN NOT MATCHED THEN INSERT
            (branch_id, store_name, address_line, city, province, postal_code, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """

    def to_float(val):
        try:
            f = float(val)
            return None if (f != f) else f  # NaN check
        except (TypeError, ValueError):
            return None

    def to_str(val):
        if val is None or (isinstance(val, float) and val != val):
            return None
        s = str(val).strip()
        return None if s in ("", "nan", "None") else s

    count = 0
    for _, row in df.iterrows():
        bid  = to_str(row.get("branch_id"))
        name = to_str(row.get("store_name"))
        addr = to_str(row.get("address_line"))
        city = to_str(row.get("city"))
        prov = to_str(row.get("province"))
        post = to_str(row.get("postal_code"))
        lat  = to_float(row.get("latitude"))
        lng  = to_float(row.get("longitude"))

        cursor.execute(merge_sql, (
            bid,                                    
            name, addr, city, prov, post, lat, lng, 
            bid, name, addr, city, prov, post, lat, lng,
        ))
        count += 1

    conn.commit()
    cursor.close()
    conn.close()
    print(f"  Done. {count} rows upserted into dbo.Stores.")

# ------------------------------------------------------------------ main

if __name__ == "__main__":
    df = read_csv()
    load_to_sqlserver(df)