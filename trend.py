import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

df = pd.read_csv("bank_reviews_themed.csv")
full = df[(df["month"] >= "2026-06") & (df["month"] <= "2026-10")]

def net(r):
    return ((r >= 4).mean() - (r <= 2).mean()) * 100

monthly = full.groupby(["bank", "month"])["rating"].agg(reviews="count", avg_rating="mean", net_sentiment=net).round(2)
monthly.to_csv("monthly_trend.csv")

print("Average rating per month:")
rating = monthly["avg_rating"].unstack("month")
print(rating)
print("\nNet sentiment per month:")
print(monthly["net_sentiment"].unstack("month").round(1))
print("\nReviews per month:")
print(monthly["reviews"].unstack("month"))

print("\nTrend (rating change per month, from a straight-line fit):")
for bank, row in rating.iterrows():
    slope = np.polyfit(range(len(row)), row.values, 1)[0]
    print(f"{bank}: {slope:+.3f} per month   (June {row.iloc[0]:.2f} -> October {row.iloc[-1]:.2f})")

plt.figure(figsize=(8, 4.5))
for bank, row in rating.iterrows():
    plt.plot(row.index, row.values, marker="o", label=bank)
plt.title("Average Google Play rating by month (Jun to Oct 2026)")
plt.ylabel("Average rating (1 to 5)")
plt.ylim(1, 5)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.savefig("monthly_trend.png", dpi=150)
print("\nChart saved as monthly_trend.png")
