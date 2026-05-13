import pandas as pd

REQUIRED_COLUMNS = [
    "customer_name",
    "usage_change_percent",
    "last_login_days",
    "support_ticket_count",
    "renewal_days_remaining",
    "customer_sentiment",
    "feature_request_status",
    "notes",
]


def validate_csv(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required columns: {missing}")


def check_missing_values(df):
    warnings = {}
    for col in REQUIRED_COLUMNS:
        if col not in df.columns:
            continue
        blank_mask = df[col].isnull() | (df[col].astype(str).str.strip() == "")
        blank_indices = df.index[blank_mask].tolist()
        if blank_indices:
            warnings[col] = blank_indices
    return warnings


def calculate_risk(row):
    score = 0
    reasons = []

    if pd.notna(row["usage_change_percent"]) and row["usage_change_percent"] <= -25:
        score += 3
        reasons.append(f"Usage dropped {abs(row['usage_change_percent'])}%")

    if pd.notna(row["last_login_days"]) and row["last_login_days"] >= 14:
        score += 2
        reasons.append(f"No login for {int(row['last_login_days'])} days")

    if pd.notna(row["support_ticket_count"]) and row["support_ticket_count"] >= 3:
        score += 2
        reasons.append(f"{int(row['support_ticket_count'])} support tickets open")

    if pd.notna(row["renewal_days_remaining"]) and row["renewal_days_remaining"] <= 60:
        score += 2
        reasons.append(f"Renewal in {int(row['renewal_days_remaining'])} days")

    if pd.notna(row["customer_sentiment"]) and str(row["customer_sentiment"]).strip().lower() == "negative":
        score += 2
        reasons.append("Negative customer sentiment")

    if pd.notna(row["feature_request_status"]) and str(row["feature_request_status"]).strip().lower() in ("unavailable", "pending"):
        score += 1
        reasons.append(f"Feature request is {str(row['feature_request_status']).strip().lower()}")

    if score <= 3:
        level = "Low"
    elif score <= 6:
        level = "Medium"
    else:
        level = "High"

    return score, level, reasons


def analyze_customer(row):
    score, level, reasons = calculate_risk(row)

    data_quality_warnings = []
    for col in REQUIRED_COLUMNS:
        val = row.get(col, None)
        if pd.isna(val) or str(val).strip() == "":
            data_quality_warnings.append(f"Missing value: {col}")

    return {
        "customer_name": row["customer_name"],
        "risk_score": score,
        "risk_level": level,
        "risk_reasons": reasons,
        "data_quality_warnings": data_quality_warnings,
        "source_metrics": {
            "usage_change_percent": row["usage_change_percent"],
            "last_login_days": row["last_login_days"],
            "support_ticket_count": row["support_ticket_count"],
            "renewal_days_remaining": row["renewal_days_remaining"],
            "customer_sentiment": row["customer_sentiment"],
            "feature_request_status": row["feature_request_status"],
        },
    }


def analyze_dataframe(df):
    validate_csv(df)
    return [analyze_customer(row) for _, row in df.iterrows()]


if __name__ == "__main__":
    import os

    csv_path = os.path.join(os.path.dirname(__file__), "..", "sample_data", "renewal_accounts.csv")
    df = pd.read_csv(csv_path)

    validate_csv(df)

    missing = check_missing_values(df)
    if missing:
        print("Data quality warnings:")
        for col, indices in missing.items():
            print(f"  {col}: blank at row(s) {indices}")
        print()

    results = analyze_dataframe(df)

    for r in results:
        print(f"{'='*50}")
        print(f"Customer:      {r['customer_name']}")
        print(f"Risk Score:    {r['risk_score']}")
        print(f"Risk Level:    {r['risk_level']}")
        print(f"Reasons:       {', '.join(r['risk_reasons']) if r['risk_reasons'] else 'None'}")
        if r["data_quality_warnings"]:
            print(f"DQ Warnings:   {', '.join(r['data_quality_warnings'])}")
        print(f"Metrics:       {r['source_metrics']}")
    print(f"{'='*50}")
