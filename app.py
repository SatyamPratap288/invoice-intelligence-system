import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from inference.predict_freight import predict_freight_cost
from inference.predict_invoice_flag import predict_invoice_flag

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------
st.set_page_config(
    page_title="Vendor Invoice Intelligence Portal",
    page_icon="📦",
    layout="wide"
)

# -------------------------------------------------------
# Header Section
# -------------------------------------------------------
st.markdown("""
# 📦 Vendor Invoice Intelligence Portal  
### AI-Driven Freight Cost Prediction & Invoice Risk Flagging

This internal analytics portal leverages machine learning to  
- **Forecast freight costs accurately**
- **Detect risky or abnormal vendor invoices**
- **Reduce financial leakage and manual workload**
""")

st.divider()

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------
st.sidebar.title("🔍 Model Selection")
selected_model = st.sidebar.radio(
    "Choose Prediction Module",
    [
        "Freight Cost Prediction",
        "Invoice Manual Approval Flag"
    ]
)

st.sidebar.markdown("""
---
**Business Impact**
- 📉 Improved cost forecasting  
- 🧾 Reduced invoice fraud & anomalies  
- ⚙️ Faster finance operations
""")

# -------------------------------------------------------
# Freight Cost Prediction
# -------------------------------------------------------
if selected_model == "Freight Cost Prediction":
    st.subheader("🚚 Freight Cost Prediction")

    st.markdown("""
    **Objective:**  
    Predict freight cost for a vendor invoice using **Invoice Dollars**  
    to support budgeting, forecasting, and vendor negotiations.
    """)

    with st.form("freight_form"):
        col1, col2 = st.columns(2)

        with col1:
            dollars = st.number_input(
                "💰 Invoice Dollars",
                min_value=1.0,
                value=18500.0
            )

        submit_freight = st.form_submit_button("🔮 Predict Freight Cost")

    if submit_freight:
        input_data = {
            "Dollars": [dollars]
        }

        prediction = predict_freight_cost(input_data)['Predicted_Freight']

        st.success("Prediction completed successfully.")

        st.metric(
            label="📊 Estimated Freight Cost",
            value=f"${prediction[0]:,.2f}"
        )



# -------------------------------------------------------
# Invoice Flag Prediction
# -------------------------------------------------------
else:
    st.subheader("🚨 Invoice Manual Approval Prediction")

    st.markdown("""
    **Objective:**  
    Predict whether a vendor invoice should be **flagged for manual approval**  
    based on abnormal cost, freight, or delivery patterns.
    """)

    with st.form("invoice_flag_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            invoice_quantity = st.number_input(
                "Invoice Quantity",
                min_value=1,
                value=50
            )
            freight = st.number_input(
                "Freight Cost",
                min_value=0.0,
                value=1.73
            )

        with col2:
            invoice_dollars = st.number_input(
                "Invoice Dollars",
                min_value=1.0,
                value=352.95
            )
            total_item_quantity = st.number_input(
                "Total Item Quantity",
                min_value=1,
                value=162
            )

        with col3:
            total_item_dollars = st.number_input(
                "Total Item Dollars",
                min_value=1.0,
                value=2476.0
            )

        submit_flag = st.form_submit_button("🧠 Evaluate Invoice Risk")

    if submit_flag:
        input_data = {
            "invoice_quantity": [invoice_quantity],
            "invoice_dollars": [invoice_dollars],
            "Freight": [freight],
            "total_item_quantity": [total_item_quantity],
            "total_item_dollars": [total_item_dollars]
        }

        flag_prediction = predict_invoice_flag(input_data)['Predicted_Flag']

        is_flagged = bool(flag_prediction[0])

        if is_flagged:
            st.error("🚨 Invoice requires **MANUAL APPROVAL**")
        else:
            st.success("✅ Invoice is **SAFE for Auto-Approval**")


            # --- ADDED: ENTERPRISE FREIGHT AUDIT MODULE ---
st.markdown("---")
st.header("🔍 Carrier Freight Audit & Leakage Detector")
st.write("Compare the Machine Learning baseline prediction against the actual carrier bill (e.g., FedEx/UPS) to detect revenue leakage and overcharges.")

col1, col2 = st.columns(2)

with col1:
    actual_billed = st.number_input("Actual Billed Cost by Carrier ($)", min_value=0.0, value=250.00, step=10.0)

with col2:
    predicted_baseline = st.number_input("ML Predicted Baseline Cost ($)", min_value=0.0, value=200.00, step=10.0)

# Business Logic for Anomaly Detection
difference_usd = actual_billed - predicted_baseline
if predicted_baseline > 0:
    variance_pct = (difference_usd / predicted_baseline) * 100
else:
    variance_pct = 0.0

# eBay Business Rule: Flag if carrier charges > 15% over prediction
TOLERANCE_THRESHOLD = 15.0  

st.subheader("Audit Status:")

if variance_pct > TOLERANCE_THRESHOLD:
    st.error(f"🚨 **REVENUE LEAKAGE DETECTED:** Carrier billed {variance_pct:.1f}% higher than expected!")
    st.write(f"**Financial Impact:** Potential overcharge of **${difference_usd:.2f}**.")
    st.warning("Recommended Action: Route invoice to Logistics Finance for manual dispute.")
elif variance_pct < 0:
    st.success(f"✅ **CLEARED:** Carrier billed less than expected. No action needed.")
else:
    st.success(f"✅ **CLEARED:** Billed amount is within the acceptable {TOLERANCE_THRESHOLD}% variance threshold. Auto-approve for payment.")
