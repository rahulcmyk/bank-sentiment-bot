"""Fetch each app's Google Play marketing text (title, summary, description).

Example:
  python3 fetch_claims.py --out descriptions.csv \
    --app "HSBC Singapore|sg.com.hsbc.hsbcsingapore|sg" \
    --app "Chase UK|com.chase.intl|gb"

Each --app is: name|app_id|country.  Name must match the 'bank' column in your reviews csv.
"""
import argparse
import pandas as pd
from google_play_scraper import app

p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--app", action="append", required=True)
a = p.parse_args()

rows = []
for spec in a.app:
    name, app_id, country = [s.strip() for s in spec.split("|")]
    d = app(app_id, lang="en", country=country)
    rows.append({"bank": name, "app_id": app_id, "title": d.get("title", ""),
                 "summary": d.get("summary", ""), "description": d.get("description", ""),
                 "store_score": d.get("score")})
    print(name, "done")
pd.DataFrame(rows).to_csv(a.out, index=False)
print("Saved", a.out)
