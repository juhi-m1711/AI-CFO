"""
generate_data.py
Converts AI_Accounting_Platform_Dataset.xlsx sheets into individual CSVs.
Run once: python data/generate_data.py
"""
import pandas as pd
import os

XLSX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'AI_Accounting_Platform_Dataset.xlsx')
OUT_DIR   = os.path.dirname(os.path.abspath(__file__))

SHEET_MAP = {
    'Financial_Transactions':  'financial_transactions.csv',
    'GST_Tax_Management':      'gst_tax_management.csv',
    'Fraud_Anomaly_Detection': 'fraud_anomaly_detection.csv',
    'Payroll_Management':      'payroll_management.csv',
    'Financial_Intelligence':  'financial_intelligence.csv',
    'Compliance_Tracking':     'compliance_tracking.csv',
}

def generate():
    if not os.path.exists(XLSX_PATH):
        print(f"❌ File not found: {XLSX_PATH}")
        print("   Place AI_Accounting_Platform_Dataset.xlsx inside the data/ folder.")
        return

    xl = pd.ExcelFile(XLSX_PATH)
    print("📂 Reading Excel file...\n")

    for sheet, filename in SHEET_MAP.items():
        df = pd.read_excel(xl, sheet_name=sheet, header=1)
        df = df.dropna(how='all').dropna(axis=1, how='all')
        out_path = os.path.join(OUT_DIR, filename)
        df.to_csv(out_path, index=False)
        print(f"✅ {filename:<40} → {df.shape[0]} rows, {df.shape[1]} cols")

    print("\n🎉 All CSVs created in data/ folder!")

if __name__ == '__main__':
    generate()