"""Generate a reproducible synthetic transaction dataset with intentional defects."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "raw" / "transactions.csv"

CATEGORIES = {
    "food": (["Highlands", "Pho 24", "GrabFood", "WinMart"], (35_000, 300_000)),
    "transport": (["Grab", "Be", "Petrolimex", "Metro"], (15_000, 500_000)),
    "shopping": (["Shopee", "Lazada", "Uniqlo", "Aeon"], (80_000, 2_500_000)),
    "education": (["Coursera", "Fahasa", "English Center"], (100_000, 3_000_000)),
    "entertainment": (["CGV", "Steam", "Karaoke"], (70_000, 800_000)),
    "health": (["Pharmacity", "Hospital", "Gym"], (50_000, 2_000_000)),
    "housing": (["Landlord", "Home Services"], (2_000_000, 8_000_000)),
    "utilities": (["EVN", "Internet", "Water"], (100_000, 1_200_000)),
    "subscription": (["Netflix", "Spotify", "iCloud"], (59_000, 260_000)),
    "other": (["Gift Shop", "Convenience Store"], (30_000, 900_000)),
}

def generate(n: int = 1600, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.to_datetime(rng.choice(pd.date_range("2025-01-01", "2026-08-31"), n))
    cats = rng.choice(list(CATEGORIES), n, p=[.30,.17,.10,.04,.08,.05,.012,.035,.025,.188])
    rows = []
    for i, (date, cat) in enumerate(zip(dates, cats), 1):
        merchants, bounds = CATEGORIES[cat]
        merchant = rng.choice(merchants)
        amount = int(rng.uniform(*bounds) // 1000 * 1000)
        rows.append([f"TX{i:06d}", date.strftime("%Y-%m-%d"), f"Thanh toan {merchant}", amount,
                     "expense", cat, rng.choice(["cash", "card", "e_wallet"], p=[.2,.35,.45]),
                     merchant, rng.choice(["Ha Noi", "Ho Chi Minh", "Da Nang"]),
                     cat in {"housing", "utilities", "subscription"} and rng.random() < .75, ""])
    # Add monthly salary income so saving analysis is meaningful.
    for j, date in enumerate(pd.date_range("2025-01-01", "2026-08-01", freq="MS") + pd.Timedelta(days=24), n + 1):
        rows.append([f"TX{j:06d}", date.strftime("%Y-%m-%d"), "Monthly salary", 60_000_000,
                     "income", "income", "bank_transfer", "Employer", "Ha Noi", True, "Salary"])
    df = pd.DataFrame(rows, columns=["transaction_id","transaction_date","description","amount",
        "transaction_type","category","payment_method","merchant","city","is_recurring","note"])
    # Inject realistic data-quality defects.
    idx = rng.choice(df.index, 65, replace=False)
    df.loc[idx[:15], "category"] = np.nan
    df.loc[idx[15:25], "category"] = rng.choice(["Food", "Ăn uống", "shopping "])
    df.loc[idx[25:33], "amount"] = rng.choice([0, -85_000], 8)
    df.loc[idx[33:41], "transaction_date"] = pd.to_datetime(df.loc[idx[33:41], "transaction_date"]).dt.strftime("%d/%m/%Y")
    df.loc[idx[41:46], "transaction_date"] = "2030-01-01"
    df.loc[idx[46:51], "payment_method"] = "crypto"
    df.loc[idx[51:56], "merchant"] = "  Highlands  "
    df.loc[idx[56:61], "amount"] = 35_000_000
    df = pd.concat([df, df.loc[idx[61:65]]], ignore_index=True)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)

if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    generate().to_csv(OUTPUT, index=False)
    print(f"Created {OUTPUT} ({len(generate()):,} rows)")
