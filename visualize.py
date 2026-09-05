"""Generate ten decision-oriented charts from cleaned data."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "transactions_clean.csv"
OUT = ROOT / "reports" / "figures"
VND = lambda x, pos: f"{x/1e6:.1f}M"

def save(name, title):
    plt.title(title); plt.tight_layout(); plt.savefig(OUT/name, dpi=150, bbox_inches="tight"); plt.close()

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA, parse_dates=["transaction_date"])
    exp = df[df.transaction_type.eq("expense")].copy()
    monthly = df.pivot_table(index="month", columns="transaction_type", values="amount", aggfunc="sum", fill_value=0)
    colors = {"income":"#2a9d8f", "expense":"#e76f51"}
    ax = monthly[["income","expense"]].plot(kind="bar", figsize=(11,5), color=[colors["income"],colors["expense"]]); ax.yaxis.set_major_formatter(VND); ax.set_ylabel("Million VND"); save("01_monthly_income_expense.png", "Monthly income and expense")
    cat = exp.groupby("category").amount.sum().sort_values(); ax=cat.plot.barh(figsize=(9,5), color="#457b9d"); ax.xaxis.set_major_formatter(VND); ax.set_xlabel("Million VND"); save("02_category_spending.png", "Total expense by category")
    latest=exp.month.max(); shares=exp[exp.month.eq(latest)].groupby("category").amount.sum().sort_values(ascending=False); shares.plot.pie(figsize=(7,7), autopct="%1.1f%%", ylabel=""); save("03_latest_month_share.png", f"Expense share by category — {latest}")
    order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]; dow=exp.groupby("day_of_week").amount.sum().reindex(order); ax=dow.plot.bar(figsize=(9,5), color="#f4a261"); ax.yaxis.set_major_formatter(VND); ax.set_ylabel("Million VND"); save("04_day_of_week.png", "Expense by day of week")
    exp.amount.clip(upper=exp.amount.quantile(.99)).plot.hist(bins=35, figsize=(9,5), color="#6d597a"); plt.xlabel("Amount (VND, capped at 99th percentile)"); save("05_transaction_distribution.png", "Distribution of expense transaction values")
    weekend=exp.groupby("is_weekend").amount.mean().rename(index={False:"Weekday",True:"Weekend"}); ax=weekend.plot.bar(figsize=(7,5), color=["#264653","#e9c46a"]); ax.yaxis.set_major_formatter(VND); ax.set_ylabel("Average VND"); save("06_weekday_weekend.png", "Average transaction: weekday vs weekend")
    merchants=exp.groupby("merchant").amount.sum().nlargest(10).sort_values(); ax=merchants.plot.barh(figsize=(9,5), color="#8ab17d"); ax.xaxis.set_major_formatter(VND); ax.set_xlabel("Million VND"); save("07_top_merchants.png", "Top 10 merchants by expense")
    sample=exp.sort_values("transaction_date"); plt.figure(figsize=(11,5)); plt.scatter(sample.transaction_date, sample.amount, c=sample.is_unusual.map({True:"#d62828",False:"#90a4ae"}), s=12, alpha=.65); plt.gca().yaxis.set_major_formatter(VND); plt.ylabel("Amount (million VND)"); save("08_unusual_transactions.png", "Category-level IQR outlier signals (red)")
    recurring=exp.groupby("is_recurring").amount.sum().rename(index={False:"Non-recurring",True:"Recurring"}); ax=recurring.plot.bar(figsize=(7,5), color=["#577590","#f94144"]); ax.yaxis.set_major_formatter(VND); ax.set_ylabel("Million VND"); save("09_recurring.png", "Recurring vs non-recurring expense")
    monthly["saving_rate"]=(monthly.income-monthly.expense).div(monthly.income.where(monthly.income.ne(0))).mul(100); ax=monthly.saving_rate.plot(figsize=(10,5), marker="o", color="#2a9d8f"); ax.axhline(20, ls="--", color="gray", label="20% reference"); ax.set_ylabel("Percent"); ax.legend(); save("10_saving_rate.png", "Monthly saving rate")
    print(f"Created 10 charts in {OUT}")

if __name__ == "__main__": main()
