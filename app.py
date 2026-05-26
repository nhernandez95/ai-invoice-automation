import re
import pandas as pd
import streamlit as st
from dateutil.parser import parse

st.set_page_config(page_title="AI Invoice Processing Automation", layout="wide")
st.title("AI Invoice / PDF Processing Automation")
st.caption("Extract invoice fields from raw document text and convert them into structured financial data.")

uploaded_file = st.file_uploader("Upload invoice text file", type=["txt"])

if uploaded_file:
    text = uploaded_file.read().decode("utf-8", errors="ignore")
else:
    with open("data/sample_invoice_text.txt", "r") as f:
        text = f.read()
    st.info("Using sample invoice text. Upload your own .txt invoice extraction to test the workflow.")

st.subheader("Raw Document Text")
st.text_area("Invoice Text", text, height=260)

def extract(pattern, text, default=""):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else default

vendor = extract(r"Vendor:\s*(.+)", text)
invoice_number = extract(r"Invoice Number:\s*(.+)", text)
invoice_date = extract(r"Invoice Date:\s*(.+)", text)
due_date = extract(r"Due Date:\s*(.+)", text)
subtotal = extract(r"Subtotal:\s*([\d,.]+)", text)
tax = extract(r"Tax:\s*([\d,.]+)", text)
total = extract(r"Total:\s*([\d,.]+)", text)
terms = extract(r"Payment Terms:\s*(.+)", text)

summary = pd.DataFrame([
    {
        "Vendor": vendor,
        "Invoice Number": invoice_number,
        "Invoice Date": invoice_date,
        "Due Date": due_date,
        "Subtotal": subtotal,
        "Tax": tax,
        "Total": total,
        "Payment Terms": terms,
        "Expense Category": "Office / Operations" if "office" in text.lower() else "General Expense"
    }
])

st.subheader("Structured Invoice Output")
st.dataframe(summary, use_container_width=True)

line_items = []
for line in text.splitlines():
    match = re.match(r"(.+?)\s-\s(.+?)\s-\s([\d,.]+)$", line.strip())
    if match:
        line_items.append({
            "Item": match.group(1),
            "Quantity": match.group(2),
            "Amount": float(match.group(3).replace(",", ""))
        })

if line_items:
    items_df = pd.DataFrame(line_items)
    st.subheader("Extracted Line Items")
    st.dataframe(items_df, use_container_width=True)

st.subheader("AI-Style Finance Summary")
st.write(f"""
This invoice from **{vendor}** totals **${total}** and appears to be categorized as **Office / Operations**.
Payment terms are **{terms}**, with a due date of **{due_date}**.

**Recommended Action:** Store this invoice in the finance database, route it for approval, and compare vendor spend against prior monthly totals to detect unusual expense changes.
""")

csv = summary.to_csv(index=False).encode("utf-8")
st.download_button("Download Structured Invoice CSV", csv, "invoice_output.csv", "text/csv")
