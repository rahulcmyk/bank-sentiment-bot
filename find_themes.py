import pandas as pd

df = pd.read_csv("bank_reviews_scored.csv")

THEMES = {
    "Login and access": [r"log ?in", r"sign ?in", r"password", r"\botp\b", r"face id", r"biometric", r"locked out", r"authenticat", r"can.?t access", r"cannot access"],
    "App bugs and speed": [r"crash", r"\bbugs?\b", r"buggy", r"glitch", r"freez", r"\bslow", r"\blag", r"\berrors?\b", r"not working", r"doesn.?t work", r"stuck", r"loading", r"new update", r"latest update", r"after the update"],
    "Customer support": [r"support", r"customer service", r"customer care", r"helpline", r"\bagent", r"representative", r"call cent", r"no response", r"no reply", r"nobody"],
    "Fees and charges": [r"\bfees?\b", r"\bcharge", r"hidden", r"commission", r"expensive", r"subscription", r"exchange rate", r"markup"],
    "Blocked account and KYC": [r"\bblock", r"suspend", r"restrict", r"\bkyc\b", r"verif", r"documents?\b", r"passport", r"emirates id", r"closed my account", r"close my account", r"source of funds"],
    "Cards": [r"\bcards?\b", r"\batm\b", r"debit", r"credit", r"contactless", r"apple pay", r"google pay"],
    "Transfers and payments": [r"transfer", r"payment", r"send money", r"transaction", r"paynow", r"remittance", r"deposit", r"withdraw"],
    "Rewards and interest": [r"cashback", r"interest", r"reward", r"bonus", r"saving"],
    "Ease and design": [r"\beasy\b", r"simple", r"user.?friendly", r"intuitive", r"interface", r"design", r"convenient", r"smooth", r"\bui\b", r"\bux\b"],
    "Fraud and scams": [r"scam", r"fraud", r"hack", r"stolen", r"unauthori", r"phishing"],
    "Device and OS support": [r"graphene", r"rooted", r"\broot\b", r"custom rom", r"lineage", r"play integrity", r"compatib", r"unsupported", r"android \d+", r"old phone", r"jailbreak"],
}

lower = df["text"].astype(str).str.lower()
for theme, pats in THEMES.items():
    df[theme] = lower.str.contains("|".join(pats), regex=True)

df.to_csv("bank_reviews_themed.csv", index=False)
cols = list(THEMES.keys())

def show(subset, title):
    print(f"\n{title}")
    table = (subset.groupby("bank")[cols].mean() * 100).round(1).T
    print(table)
    covered = subset[cols].any(axis=1).groupby(subset["bank"]).mean() * 100
    print("\nReviews that matched at least one theme (%):")
    print(covered.round(1))

show(df[df["rating"] <= 2], "COMPLAINT THEMES: % of 1-2 star reviews that mention each theme")
show(df[df["rating"] >= 4], "PRAISE THEMES: % of 4-5 star reviews that mention each theme")
