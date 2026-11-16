"""Scrape Google Play reviews for any apps into a NEW csv.

Example:
  python3 scrape_apps.py --out reviews_hsbc_chase.csv \
    --app "HSBC UK|London|uk.co.hsbc.hsbcukmobilebanking|gb|8000" \
    --app "Chase UK|London|com.chase.intl|gb|8000"

Each --app is: name|city|app_id|country|count
Writes columns: bank, city, date, rating, text
"""
import argparse
import pandas as pd
from google_play_scraper import reviews, Sort

p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--app", action="append", required=True)
p.add_argument("--lang", default="en")
a = p.parse_args()

rows = []
for spec in a.app:
    name, city, app_id, country, count = [s.strip() for s in spec.split("|")]
    data, _ = reviews(app_id, lang=a.lang, country=country,
                      sort=Sort.NEWEST, count=int(count))
    for r in data:
        text = (r.get("content") or "").strip()
        if text:
            rows.append({"bank": name, "city": city, "date": r["at"].date(),
                         "rating": r["score"], "text": text})
    print(name, "done:", len(data), "fetched")

if not rows:
    raise SystemExit("No reviews fetched. Check each app id, e.g. the text after id= in the Google Play URL, and the country code.")

df = pd.DataFrame(rows).drop_duplicates(subset=["bank", "date", "text"])
df.to_csv(a.out, index=False)
print(df.groupby("bank").agg(count=("rating", "size"), mean=("rating", "mean"),
      first=("date", "min"), last=("date", "max")))
print("Saved", a.out)
