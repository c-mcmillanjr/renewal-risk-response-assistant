import sys
import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

# Allow imports from the scripts/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "scripts"))
from risk_engine import validate_csv, calculate_risk, analyze_customer

# Load OPENAI_API_KEY from a .env file if present
load_dotenv()

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
# Deterministic risk analysis for the selected customer
# ---------------------------------------------------------------------------
customer_row = df[df["customer_name"] == selected_name].iloc[0]

try:
    score, level, reasons = calculate_risk(customer_row)
    result = analyze_customer(customer_row)
except Exception as e:
    st.error(f"Risk calculation failed: {e}")
    st.stop()

badge_color = {"Low": "green", "Medium": "orange", "High": "red"}.get(level, "gray")

st.subheader("Risk Assessment")
st.markdown(f"**Customer:** {selected_name}")
st.markdown(f"**Risk Score:** {score}")
st.markdown(f"**Risk Level:** :{badge_color}[{level}]")

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

# ---------------------------------------------------------------------------
# BASELINE EMAIL GENERATOR
# ---------------------------------------------------------------------------
# The baseline represents a simpler workflow with no deterministic scoring,
# no risk reasoning, and no structured prompt. It passes raw customer data
# directly to the model with a generic instruction. This is the "before"
# state — used as a comparison point to evaluate the value added by the
# improved system below.
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Baseline Email Generator")
st.caption(
    "Generates a generic follow-up email using only raw account data — "
    "no risk scoring, no structured reasoning, no prompt engineering."
)

if st.button("Generate Baseline Email"):

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        st.error(
            "OPENAI_API_KEY is not set. Add it to a .env file or export it in your terminal before running the app."
        )
        st.stop()

    # Build a plain summary of the raw row — no scoring, no analysis
    raw_data_summary = (
        f"Customer Name: {customer_row['customer_name']}\n"
        f"Usage Change (%): {customer_row['usage_change_percent']}\n"
        f"Days Since Last Login: {customer_row['last_login_days']}\n"
        f"Support Tickets: {customer_row['support_ticket_count']}\n"
        f"Days Until Renewal: {customer_row['renewal_days_remaining']}\n"
        f"Customer Sentiment: {customer_row['customer_sentiment']}\n"
        f"Feature Request Status: {customer_row['feature_request_status']}\n"
        f"Notes: {customer_row.get('notes', 'N/A')}"
    )

    # Simple, unstructured prompt — no risk score, no required sections,
    # no safety rules, no signal-by-signal reasoning
    baseline_prompt = (
        "Generate a professional customer-success follow-up email based on "
        "this customer account data.\n\n"
        + raw_data_summary
    )

    with st.spinner("Generating baseline email..."):
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": baseline_prompt}],
                temperature=0.7,
            )
            baseline_output = response.choices[0].message.content
        except OpenAIError as e:
            st.error(f"OpenAI API call failed: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error during API call: {e}")
            st.stop()

    st.markdown("**Baseline Output**")
    st.markdown(baseline_output)

# ---------------------------------------------------------------------------
# IMPROVED AI-ASSISTED OUTPUT
# ---------------------------------------------------------------------------
# The improved system uses the deterministic risk engine to score and
# classify the customer before passing structured results to the model.
# The prompt enforces signal-by-signal reasoning, required output sections,
# safety rules, and a human review disclaimer. This is the "after" state.
# ---------------------------------------------------------------------------
st.divider()
st.subheader("Improved AI-Assisted Output")
st.caption(
    "Uses deterministic risk scoring, structured signal reasoning, "
    "and a prompt-engineered system prompt to generate a CSM response plan."
)

if st.button("Generate GenAI Response"):

    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        st.error(
            "OPENAI_API_KEY is not set. Add it to a .env file or export it in your terminal before running the app."
        )
        st.stop()

    # Load the structured prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "renewal_prompt.txt")
    try:
        with open(prompt_path, "r") as f:
            prompt_template = f.read()
    except FileNotFoundError:
        st.error("Could not find prompts/renewal_prompt.txt. Make sure the file exists.")
        st.stop()

    # Fill the prompt placeholders with structured risk engine output
    filled_prompt = prompt_template.format(
        customer_name=result["customer_name"],
        risk_score=result["risk_score"],
        risk_level=result["risk_level"],
        risk_reasons=", ".join(result["risk_reasons"]) if result["risk_reasons"] else "None",
        usage_change_percent=result["source_metrics"]["usage_change_percent"],
        last_login_days=result["source_metrics"]["last_login_days"],
        support_ticket_count=result["source_metrics"]["support_ticket_count"],
        renewal_days_remaining=result["source_metrics"]["renewal_days_remaining"],
        customer_sentiment=result["source_metrics"]["customer_sentiment"],
        feature_request_status=result["source_metrics"]["feature_request_status"],
        notes=customer_row.get("notes", "None"),
    )

    with st.spinner("Generating response..."):
        try:
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": filled_prompt}],
                temperature=0.3,
            )
            genai_output = response.choices[0].message.content
        except OpenAIError as e:
            st.error(f"OpenAI API call failed: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected error during API call: {e}")
            st.stop()

    st.markdown("**Improved Output**")
    st.markdown(genai_output)
