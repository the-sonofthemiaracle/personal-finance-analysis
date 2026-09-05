"""Clean raw transactions without modifying the source file."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "transactions.csv"
CLEAN = ROOT / "data" / "processed" / "transactions_clean.csv"
ALLOWED_CATEGORIES = {"income","food","transport","shopping","education","entertainment","health","housing","utilities","subscription","other"}
ALLOWED_METHODS = {"cash","card","e_wallet","bank_transfer","other"}

def clean_transactions(df: pd.DataFrame, as_of="2026-08-31") -> pd.DataFrame:
    data = df.copy()
    data.columns = data.columns.str.strip().str.lower()
    for col in ["transaction_id","description","transaction_type","category","payment_method","merchant","city","note"]:
        data[col] = data[col].astype("string").str.strip()
    data["transaction_type"] = data["transaction_type"].str.lower()
    data["category"] = data["category"].str.lower().replace({"ăn uống":"food", "shopping ":"shopping"})
    inferred = data["description"].str.lower().map(lambda x: "food" if any(k in x for k in ["food","coffee","pho","winmart"]) else "other")
    data["category"] = data["category"].fillna(inferred)
    data.loc[data["transaction_type"].eq("income"), "category"] = "income"
    data.loc[~data["category"].isin(ALLOWED_CATEGORIES), "category"] = "other"
    data["payment_method"] = data["payment_method"].str.lower()
    data.loc[~data["payment_method"].isin(ALLOWED_METHODS), "payment_method"] = "other"
    data["transaction_date"] = pd.to_datetime(data["transaction_date"], errors="coerce", dayfirst=False)
    data["amount"] = pd.to_numeric(data["amount"], errors="coerce").abs()
    data = data.drop_duplicates("transaction_id", keep="first")
    data = data[data["amount"].gt(0) & data["transaction_date"].notna()]
    data = data[data["transaction_date"].le(pd.Timestamp(as_of))]
    data["is_recurring"] = data["is_recurring"].astype(str).str.lower().map({"true": True, "false": False}).fillna(False)
    data["year"] = data["transaction_date"].dt.year
    data["month"] = data["transaction_date"].dt.to_period("M").astype(str)
    data["day_of_week"] = data["transaction_date"].dt.day_name()
    data["is_weekend"] = data["transaction_date"].dt.dayofweek.ge(5)
    expense_amounts = data.loc[data.transaction_type.eq("expense"), "amount"]
    q1, q2 = expense_amounts.quantile([.33, .67])
    data["expense_level"] = pd.cut(data["amount"], [-1, q1, q2, float("inf")], labels=["small","medium","large"])
    data = data.sort_values(["transaction_date","transaction_id"]).reset_index(drop=True)
    data["days_since_previous_transaction"] = data["transaction_date"].diff().dt.days.fillna(0).clip(lower=0)
    data["is_unusual"] = False
    expense_idx = data.index[data.transaction_type.eq("expense")]
    for _, group in data.loc[expense_idx].groupby("category"):
        q1, q3 = group.amount.quantile([.25,.75]); upper = q3 + 1.5 * (q3-q1)
        data.loc[group.index, "is_unusual"] = group.amount.gt(upper)
    return data

def main():
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    clean_transactions(pd.read_csv(RAW)).to_csv(CLEAN, index=False)
    print(f"Created {CLEAN}")

if __name__ == "__main__": main()

