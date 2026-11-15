import pandas as pd

df = pd.read_csv("bank_reviews_themed.csv")
sub = df[(df["text_length"] >= 20) & (df["month"] >= "2026-06") & (df["month"] <= "2026-10")]

print("Reviews with at least 20 characters of text (Jun to Oct):")
print(sub.groupby("bank")["rating"].agg(["count", "mean"]).round(2))

print("\nAverage rating per month (substantive reviews only):")
print(sub.pivot_table(index="bank", columns="month", values="rating", aggfunc="mean").round(2))

print("\nReviews per month (substantive reviews only):")
print(sub.pivot_table(index="bank", columns="month", values="rating", aggfunc="count"))
