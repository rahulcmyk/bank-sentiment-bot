import pandas as pd

df = pd.read_csv("bank_reviews_themed.csv")
checks = [
    ("DBS digibank", "Login and access"),
    ("Revolut", "Blocked account and KYC"),
    ("Revolut", "Fraud and security"),
    ("Liv X", "Customer support"),
]
for bank, theme in checks:
    sub = df[(df["bank"] == bank) & (df["rating"] <= 2) & (df[theme])]
    print(f"\n=== {bank} | {theme} | {len(sub)} reviews ===")
    for t in sub.sample(5, random_state=1)["text"]:
        print("-", str(t)[:200])
