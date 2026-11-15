import pandas as pd

df = pd.read_csv("bank_reviews.csv")
df = df.drop_duplicates()
df = df[(df["date"] >= "2026-05-25") & (df["date"] <= "2026-11-13")]

# park Wio: too few reviews for a fair ranking
wio = df[df["bank"] == "Wio Bank"]
wio.to_csv("wio_parked.csv", index=False)
df = df[df["bank"] != "Wio Bank"].copy()

df["month"] = df["date"].str[:7]
df["text_length"] = df["text"].str.len()
df.to_csv("bank_reviews_clean.csv", index=False)

print(f"Clean file saved: {len(df)} reviews (Wio parked: {len(wio)})\n")
g = df.groupby("bank")
print(g["rating"].agg(["count", "mean"]).round(2))
print()
print("Share of 1-2 star reviews (%):")
print((g["rating"].apply(lambda s: (s <= 2).mean() * 100)).round(1))
print("\nShare of 4-5 star reviews (%):")
print((g["rating"].apply(lambda s: (s >= 4).mean() * 100)).round(1))
print("\nAverage review length (characters):")
print(g["text_length"].mean().round(0))
