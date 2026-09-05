"""Create reusable CSV and Markdown summaries."""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "transactions_clean.csv"
REPORTS = ROOT / "reports"

def build_tables(df):
    monthly = df.pivot_table(index="month", columns="transaction_type", values="amount", aggfunc="sum", fill_value=0)
    for col in ["income","expense"]:
        if col not in monthly:
            monthly[col] = 0
    monthly["saving_amount"] = monthly.income - monthly.expense
    monthly["saving_rate_pct"] = monthly.saving_amount.div(monthly.income.where(monthly.income.ne(0))).mul(100)
    monthly["expense_growth_pct"] = monthly.expense.pct_change().mul(100)
    expenses = df[df.transaction_type.eq("expense")]
    category = expenses.groupby("category").amount.agg(["sum","mean","median","count"]).sort_values("sum", ascending=False)
    category["share_pct"] = category["sum"].div(category["sum"].sum()).mul(100)
    payment = expenses.groupby("payment_method").amount.agg(["sum","mean","count"]).sort_values("count", ascending=False)
    return monthly, category, payment

def main():
    REPORTS.mkdir(exist_ok=True)
    df = pd.read_csv(DATA, parse_dates=["transaction_date"])
    monthly, category, payment = build_tables(df)
    monthly.to_csv(REPORTS/"monthly_summary.csv")
    category.to_csv(REPORTS/"category_summary.csv")
    payment.to_csv(REPORTS/"payment_summary.csv")
    df[df.is_unusual].sort_values("amount", ascending=False).to_csv(REPORTS/"unusual_transactions.csv", index=False)
    latest, previous = monthly.index[-1], monthly.index[-2]
    total_income = df.loc[df.transaction_type.eq("income"),"amount"].sum()
    total_expense = df.loc[df.transaction_type.eq("expense"),"amount"].sum()
    text = f"""# Automated Financial Report\n\nGenerated from the cleaned synthetic dataset.\n\n- Total income: {total_income:,.0f} VND\n- Total expense: {total_expense:,.0f} VND\n- Net saving: {total_income-total_expense:,.0f} VND\n- Overall saving rate: {(total_income-total_expense)/total_income*100:.1f}%\n- Latest month ({latest}) expense: {monthly.loc[latest,'expense']:,.0f} VND\n- Change from {previous}: {monthly.loc[latest,'expense_growth_pct']:.1f}%\n- Largest category: {category.index[0]} ({category.iloc[0].share_pct:.1f}%)\n- Category-level IQR outliers: {int(df.is_unusual.sum())}\n\nOutliers are review signals, not proof of error or fraud.\n"""
    (REPORTS/"summary.md").write_text(text, encoding="utf-8")
    print(text)

if __name__ == "__main__": main()
