"""Shared theme keyword lists (copied from find_themes.py)."""

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
