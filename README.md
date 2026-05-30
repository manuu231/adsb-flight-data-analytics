# ADS-B Flight Data Analytics

## Overview

This project builds an end-to-end analytics pipeline for ADS-B (Automatic Dependent Surveillance–Broadcast) aircraft telemetry data.

The pipeline:

- Connects to a remote ADS-B data server using SFTP
- Downloads monthly flight telemetry archives
- Extracts and processes JSON records
- Loads data into DuckDB for analytical querying
- Performs exploratory flight analysis
- Visualizes aircraft altitude and ground speed distributions

## Technologies Used

- Python
- DuckDB
- Pandas
- NumPy
- Matplotlib
- Paramiko (SFTP)
- JSON Processing

## Features

### Data Ingestion
- Secure SFTP connection
- Automated monthly data downloads
- Aircraft lookup database retrieval

### Data Processing
- Parsing ADS-B JSON records
- Extraction of:
  - Aircraft Hex IDs
  - Flight Numbers
  - Barometric Altitude
  - Geometric Altitude
  - Ground Speed
  - Latitude
  - Longitude
  - Timestamp

### Storage
- DuckDB analytical database
- Efficient columnar storage
- SQL-based querying

### Analytics
- Top 10 most active aircraft
- Top 10 most frequent flight numbers
- Altitude distribution analysis
- Ground speed distribution analysis

## Example Analyses

- Aircraft traffic density
- Flight frequency patterns
- Altitude distribution
- Speed distribution
- Geographic movement analysis

## Project Structure

```
adsb-flight-data-analytics/
│
├── data_analysis.py
├── downloads/
├── raw_txt/
├── outputs/
├── adsb.duckdb
└── README.md
```

## Learning Outcomes

- Large-scale telemetry processing
- Schema-on-read concepts
- DuckDB analytics
- Remote data ingestion
- Aviation data analysis

## Author

Manpreet Mahal
M.S. Applied Data Science
Clarkson University
