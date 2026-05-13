import sys
import os

import pandas as pd
import streamlit as st

# Allow imports from the scripts/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from risk_engine import validate_csv, calculate_risk

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Renewal Risk Response Assistant", layout="centered")
st.title("Renewal Risk Response Assistant")
st.caption("Upload a customer renewal CSV to assess churn risk.")

# ---------------------------------------------------------------------------
# CSV upload
# ---------------------------------------------------------------------------
uploaded_file = st.file_uploader("Upload renewal accounts CSV", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a CSV file to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Parse and validate the uploaded file
# ---------------------------------------------------------------------------
try:
    df = pd.read_csv(uploaded_file)
except Exception as e:
    st.error(f"Could not read the uploaded file: {e}")
    st.stop()

try:
    validate_csv(df)
except ValueError as e:
    st.error("CSV validation failed.")
    # Surface the missing columns so the user knows what to fix
    missing_cols = str(e).replace("CSV is missing required columns: ", "")
    st.write("**Missing columns:**", missing_cols)
    st.stop()

# ---------------------------------------------------------------------------
# Display uploaded data
# ---------------------------------------------------------------------------
st.subheader("Uploaded Data")
st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------------------------
# Customer selector
# ---------------------------------------------------------------------------
st.subheader("Select a Customer")
customer_names = df["customer_name"].dropna().unique().tolist()

selected_name = st.selectbox("Customer", options=customer_names)

# ---------------------------------------------------------------------------
# Risk analysis for the selected customer
# ---------------------------------------------------------------------------
customer_row = df[df["customer_name"] == selected_name].iloc[0]

try:
    score, level, reasons = calculate_risk(customer_row)
except Exception as e:
    st.error(f"Risk calculation failed: {e}")
    st.stop()

# Color-code the risk badge
badge_color = {"Low": "green", "Medium": "orange", "High": "red"}.get(level, "gray")

st.subheader("Risk Assessment")
st.markdown(f"**Customer:** {selected_name}")
st.markdown(f"**Risk Score:** {score}")
st.markdown(f"**Risk Level:** :{badge_color}[{level}]")

# Risk reasons
st.markdown("**Risk Reasons:**")
if reasons:
    for reason in reasons:
        st.markdown(f"- {reason}")
else:
    st.markdown("- No risk factors identified.")

# Source metrics
st.subheader("Source Metrics")
metrics = {
    "Usage Change (%)": customer_row["usage_change_percent"],
    "Days Since Last Login": customer_row["last_login_days"],
    "Support Tickets": customer_row["support_ticket_count"],
    "Days Until Renewal": customer_row["renewal_days_remaining"],
    "Customer Sentiment": customer_row["customer_sentiment"],
    "Feature Request Status": customer_row["feature_request_status"],
}

col1, col2, col3 = st.columns(3)
cols = [col1, col2, col3]
for i, (label, value) in enumerate(metrics.items()):
    cols[i % 3].metric(label, value)
