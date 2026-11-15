"""Step 1: collect Google Play reviews for each bank into bank_reviews.csv.

Columns: bank, city, date, rating, text
Takes about 10 to 15 minutes (Revolut is the slowest).
Google Play data changes over time, so a new run will not give exactly the same numbers.
"""
import pandas as pd
from google_play_scraper import reviews, Sort

# bank label, city, Google Play app id, storefront country, language, max reviews to ask for
BANKS = [
    {"bank": "Revolut", "city": "London", "app_id": "com.revolut.revolut", "country": "gb", "lang": "en", "count": 10000},
    {"bank": "DBS digibank", "city": "Singapore", "app_id": "com.dbs.sg.dbsmbanking", "country": "sg", "lang": "en", "count": 3000},
    {"bank": "Liv X", "city": "Dubai", "app_id": "me.livx.android", "country": "ae", "lang": "en", "count": 8000},
    {"bank": "Wio Bank", "city": "Dubai", "app_id": "io.wio.retail", "country": "ae", "lang": "en", "count": 3000},
]

rows = []
for b in BANKS:
    print(f"Collecting {b['bank']}... (this can take a few minutes)")
    try:
        result, _ = reviews(
            b["app_id"],
            lang=b["lang"],
            country=b["country"],
            sort=Sort.NEWEST,
            count=b["count"],
        )
    except Exception as e:
        print(f"  Could not collect {b['bank']}: {e}")
        continue
    for r in result:
        rows.append({
            "bank": b["bank"],
            "city": b["city"],
            "date": r["at"].strftime("%Y-%m-%d"),
            "rating": r["score"],
            "text": r["content"],
        })

df = pd.DataFrame(rows)
df = df.dropna(subset=["text"])          # remove empty reviews
df = df[df["text"].str.strip() != ""]
df.to_csv("bank_reviews.csv", index=False)

print(f"\nDone. Saved {len(df)} reviews to bank_reviews.csv\n")
print("Count and average rating per bank:")
print(df.groupby("bank")["rating"].agg(["count", "mean"]).round(2))
print("\nDate range per bank:")
print(df.groupby("bank")["date"].agg(["min", "max"]))
