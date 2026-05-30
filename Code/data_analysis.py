import os, json, zipfile
from pathlib import Path
from datetime import datetime
import duckdb
import pandas as pd
import numpy as np
import paramiko
import matplotlib.pyplot as plt

# --- Configuration ---
STATION = "NY0"      # or CT0
YEAR = 2024
MONTH = 10

BASE_DIR = Path("/Users/manpreetmahal/Desktop/big data")
DOWNLOAD_DIR = BASE_DIR / "downloads"
EXTRACT_DIR = BASE_DIR / "raw_txt"
DB_PATH = BASE_DIR / "adsb.duckdb"
OUT_DIR = BASE_DIR / "outputs"

for p in [DOWNLOAD_DIR, EXTRACT_DIR, OUT_DIR]:
    p.mkdir(parents=True, exist_ok=True)

# --- SFTP credentials (updated) ---
SFTP_HOST = "files.clarksonmsda.org"
SFTP_PORT = 2022
SFTP_USER = "ia628@clarkson.edu"
SFTP_PASS = "ia628.clarks0n"

REMOTE_DIR = f"/srv/sftpgo/data/users/{SFTP_USER}/adsb/{STATION.lower()}"
LOOKUP_REMOTE = "/srv/sftpgo/data/users/ia628@clarkson.edu/adsb/basic-ac-db.json"
LOOKUP_LOCAL = BASE_DIR / "basic-ac-db.json"
TABLE_NAME = f"adsb_{STATION}_{YEAR}_{MONTH:02d}"


# --- Connect and download files ---
def sftp_connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=SFTP_HOST,
        port=SFTP_PORT,
        username=SFTP_USER,
        password=SFTP_PASS,
        look_for_keys=False,
        allow_agent=False,
    )
    return client, client.open_sftp()

def download_month(sftp, remote_dir, local_dir, year, month):
    want_tag = f".{year}{month:02d}"
    entries = sftp.listdir_attr(remote_dir)
    count = 0
    for e in entries:
        name = e.filename
        if name.endswith(".zip") and want_tag in name:
            remote = f"{remote_dir}/{name}"
            local = local_dir / name
            if local.exists():
                continue
            print(f"Downloading {name} ...")
            sftp.get(remote, str(local))
            count += 1
    print(f"✅ {count} file(s) downloaded")

def download_lookup(sftp):
    if LOOKUP_LOCAL.exists():
        return
    print("Downloading lookup file ...")
    sftp.get(LOOKUP_REMOTE, str(LOOKUP_LOCAL))

client, sftp = sftp_connect()
try:
    download_month(sftp, REMOTE_DIR, DOWNLOAD_DIR, YEAR, MONTH)
    download_lookup(sftp)
finally:
    sftp.close()
    client.close()

# Build DuckDB table
con = duckdb.connect(str(DB_PATH))
pattern = str(EXTRACT_DIR / "*.txt")

con.execute(f"""
    CREATE OR REPLACE TABLE {TABLE_NAME} AS
    SELECT
      TRY_CAST(json_extract(line, '$.dt') AS TIMESTAMP) AS dt,
      TRY_CAST(json_extract(line, '$.payload.hex') AS VARCHAR) AS hex,
      TRY_CAST(json_extract(line, '$.payload.flight') AS VARCHAR) AS flight,
      TRY_CAST(json_extract(line, '$.payload.alt_baro') AS INTEGER) AS alt_baro,
      TRY_CAST(json_extract(line, '$.payload.alt_geom') AS INTEGER) AS alt_geom,
      TRY_CAST(json_extract(line, '$.payload.gs') AS DOUBLE) AS gs,
      TRY_CAST(json_extract(line, '$.payload.lat') AS DOUBLE) AS lat,
      TRY_CAST(json_extract(line, '$.payload.lon') AS DOUBLE) AS lon
    FROM read_ndjson_objects('{pattern}', ignore_errors=true) AS t(line)
    WHERE json_valid(line)
""")

count = con.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}").fetchone()[0]
print(f"✅ Loaded {count:,} records into {TABLE_NAME}")

# Q1 – Top 10 hex IDs and flight numbers
top_hex = con.execute(f"""
    SELECT hex, COUNT(*) AS num
    FROM {TABLE_NAME}
    WHERE hex IS NOT NULL
    GROUP BY hex
    ORDER BY num DESC
    LIMIT 10
""").fetchdf()

top_flights = con.execute(f"""
    SELECT flight, COUNT(*) AS num
    FROM {TABLE_NAME}
    WHERE flight IS NOT NULL AND LENGTH(TRIM(flight))>0
    GROUP BY flight
    ORDER BY num DESC
    LIMIT 10
""").fetchdf()

display(top_hex)
display(top_flights)

df = con.execute(f"SELECT alt_baro, alt_geom, gs FROM {TABLE_NAME}").fetchdf()

plt.figure(figsize=(8,4))
plt.hist(df["alt_baro"].dropna(), bins=50)
plt.title("Histogram of Altitude (Baro)")
plt.xlabel("alt_baro")
plt.ylabel("Count")
plt.show()

plt.figure(figsize=(8,4))
plt.hist(df["gs"].dropna(), bins=50)
plt.title("Histogram of Ground Speed (gs)")
plt.xlabel("gs")
plt.ylabel("Count")
plt.show()

