import sys
print(sys.executable)

import pandas as pd

# Load PayPal payments data
payments = pd.read_csv("raw data/PayPal Payments.csv")

# Quick sanity check
print(payments.head())
print("\nShape:", payments.shape)
print("\nColumns:")
print(payments.columns)

# -----------------------------
#  Clean column names


# Parse created date
# -----------------------------

payments.columns = (
    payments.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
)

print("\nCleaned columns:")
print(payments.columns)

# -----------------------------
# Parse created date


payments["created_date_utc"] = pd.to_datetime(
    payments["created_date_utc"],
    errors="coerce"
)

print("\nDate parsing check:")
print(payments["created_date_utc"].head())
print("Null dates:", payments["created_date_utc"].isna().sum())

# -----------------------------
#Numeric cleanup


money_cols = [
    "amount",
    "amount_refunded",
    "converted_amount",
    "converted_amount_refunded",
    "fee"
]

for col in money_cols:
    payments[col] = pd.to_numeric(payments[col], errors="coerce").fillna(0)

print("\nNumeric check:")
print(payments[money_cols].describe())


# -----------------------------
# Step 4: Normalize payment status


payments["status_clean"] = payments["status"].str.lower().str.strip()

def map_status(status):
    if pd.isna(status):
        return "failed"

    status = status.lower()

    if status == "paid":
        return "captured"
    elif status == "refunded":
        return "refunded"
    elif status in ["failed", "canceled"]:
        return "failed"
    else:
        return "failed"

payments["payment_outcome"] = payments["status_clean"].apply(map_status)



print("\nPayment outcome breakdown:")
print(payments["payment_outcome"].value_counts())

print("\nRaw status values:")
print(payments["status_clean"].value_counts().head(20))


print("\nCaptured count:", (payments["payment_outcome"] == "captured").sum())


output_path = "cleaned data/paypal_payments_clean.csv"
payments.to_csv(output_path, index=False)

print(f"\nClean dataset saved to: {output_path}")


# ------------------------------------
# Step 5: Load products data


products = pd.read_csv("raw data/Products.csv")

print("\nProducts preview:")
print(products.head())

print("\nProducts shape:", products.shape)

print("\nProducts columns:")
print(products.columns)


# ------------------------------------
# Step 6: Clean products data


products.columns = (
    products.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
    .str.replace("(", "", regex=False)
    .str.replace(")", "", regex=False)
)

print("\nCleaned products columns:")
print(products.columns)


# ------------------------------------
# Step 7: Merge payments with products


payments_enriched = payments.merge(
    products,
    how="left",
    left_on="product_id_metadata",
    right_on="id"
)

print("\nMerged dataset preview:")
print(payments_enriched.head())

print("\nMerged shape:", payments_enriched.shape)


final_path = "cleaned data/paypal_payments_enriched.csv"
payments_enriched.to_csv(final_path, index=False)

print(f"\nFinal dataset saved to: {final_path}")


payments["payment_date"] = pd.to_datetime(payments["created_at"])
payments["month"] = payments["payment_date"].dt.to_period("M").astype(str)
payments["day"] = payments["payment_date"].dt.day_name()
payments["hour"] = payments["payment_date"].dt.hour


payments.to_csv("cleaned data/paypal_payments_final.csv", index=False)
