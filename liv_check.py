import pandas as pd

df = pd.read_csv("bank_reviews_themed.csv")
liv = df[(df["bank"] == "Liv X") & (df["month"] >= "2026-06") & (df["month"] <= "2026-10")].copy()
liv["short"] = liv["text_length"] < 20
liv["five"] = liv["rating"] == 5

t = liv.groupby("month").agg(
    reviews=("rating", "count"),
    avg_rating=("rating", "mean"),
    five_star_pct=("five", "mean"),
    short_review_pct=("short", "mean"),
    avg_length=("text_length", "mean"),
)
t["five_star_pct"] *= 100
t["short_review_pct"] *= 100
print(t.round(1))

print("\nSample of October 5-star reviews:")
oct5 = liv[(liv["month"] == "2026-10") & (liv["rating"] == 5)]
for x in oct5.sample(8, random_state=2)["text"]:
    print("-", str(x)[:120])
