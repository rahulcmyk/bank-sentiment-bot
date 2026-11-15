import pandas as pd
import numpy as np

df = pd.read_csv("bank_reviews_themed.csv")

rows = []
for bank, g in df.groupby("bank"):
    n = len(g)
    mean = g["rating"].mean()
    margin = 1.96 * g["rating"].std() / np.sqrt(n)
    pos = (g["rating"] >= 4).mean() * 100
    neg = (g["rating"] <= 2).mean() * 100
    rows.append({
        "bank": bank,
        "reviews": n,
        "avg_rating": round(mean, 2),
        "margin_of_error": round(margin, 2),
        "positive_pct": round(pos, 1),
        "negative_pct": round(neg, 1),
        "net_sentiment": round(pos - neg, 1),
        "avg_text_score": round(g["sentiment_score"].mean(), 3),
    })

out = pd.DataFrame(rows).sort_values("net_sentiment", ascending=False)
out.insert(0, "rank", range(1, len(out) + 1))
out.to_csv("ranking.csv", index=False)
print(out.to_string(index=False))
