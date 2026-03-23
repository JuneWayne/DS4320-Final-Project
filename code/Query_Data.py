import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time

# query open street map to obtain data about lat long location of data centers
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[out:json][timeout:180];
area["ISO3166-1"="US"]->.searchArea;
(
  node["telecom"="data_center"](area.searchArea);
  way["telecom"="data_center"](area.searchArea);
  node["building"="data_center"](area.searchArea);
  way["building"="data_center"](area.searchArea);
);
out center tags;
"""

response = requests.get(overpass_url, params={"data": overpass_query})
data = response.json()

rows = []
for element in data["elements"]:
    lat = element.get("lat") or element.get("center", {}).get("lat")
    lon = element.get("lon") or element.get("center", {}).get("lon")
    tags = element.get("tags", {})
    rows.append({
        "name": tags.get("name"),
        "operator": tags.get("operator"),
        "lat": lat,
        "lon": lon,
        "state": tags.get("addr:state"),
        "city": tags.get("addr:city"),
        "county": tags.get("addr:county"),
    })

df = pd.DataFrame(rows)
print(f"Raw data: {df.shape}")

# Use geopy to fill in missing state, city, county information based on lat/lon
geolocator = Nominatim(user_agent="ds4320_project", timeout=10)
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1, error_wait_seconds=5, max_retries=2)

def fill_missing(row):
    if pd.isna(row["state"]) or pd.isna(row["city"]) or pd.isna(row["county"]):
        try:
            location = reverse(f"{row['lat']}, {row['lon']}", language="en")
            if location:
                addr = location.raw.get("address", {})
                if pd.isna(row["state"]) or row["state"] is None:
                    row["state"] = addr.get("state")
                if pd.isna(row["city"]) or row["city"] is None:
                    row["city"] = addr.get("city") or addr.get("town") or addr.get("village")
                if pd.isna(row["county"]) or row["county"] is None:
                    row["county"] = addr.get("county")
        except Exception as e:
            print(f"Skipping row {row.name}: {e}")
    return row

print("Geocoding...")
df = df.apply(fill_missing, axis=1)
df.to_csv("us_data_centers.csv", index=False)
print("Done")
print(df.head())