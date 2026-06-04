import pandas as pd
import numpy as np
import json
import os

os.makedirs('data', exist_ok=True)

# ─────────────────────────────────────────
# 1. TRANSACTIONS DATA (500 rows)
# ─────────────────────────────────────────
np.random.seed(42)
n = 500

categories = ['Salary', 'Rent', 'Marketing',
              'Operations', 'Tax', 'Utilities', 'Others']

df = pd.DataFrame({
    'txn_id':   [f'T{str(i).zfill(4)}' for i in range(n)],
    'date':     pd.date_range('2024-01-01', periods=n, freq='D'),
    'category': np.random.choice(categories, n),
    'type':     np.random.choice(['credit', 'debit'], n, p=[0.4, 0.6]),
    'amount':   np.random.randint(1000, 500000, n)
})

# Add 20 fake fraud transactions
df.loc[df.sample(20).index, 'amount'] = \
    np.random.randint(1000000, 5000000, 20)

df.to_csv('data/sample_transactions.csv', index=False)
print("✅ sample_transactions.csv created")


# ─────────────────────────────────────────
# 2. GST DATA (50 invoices)
# ─────────────────────────────────────────
gst_df = pd.DataFrame({
    'invoice_no':     [f'INV{i:03d}' for i in range(50)],
    'date':           pd.date_range('2024-01-01', periods=50, freq='7D'),
    'gstin':          '27AAAAA0000A1Z5',
    'taxable_amount': np.random.randint(10000, 200000, 50),
    'gst_rate':       np.random.choice([5, 12, 18, 28], 50),
    'filing_status':  np.random.choice(
                          ['filed', 'pending', 'overdue'], 50,
                          p=[0.6, 0.3, 0.1])
})

gst_df.to_csv('data/gst_data.csv', index=False)
print("✅ gst_data.csv created")


# ─────────────────────────────────────────
# 3. SYNTHETIC FINANCIAL DATA (monthly P&L)
# ─────────────────────────────────────────
months = pd.date_range('2024-01-01', periods=12, freq='MS')

# Simulate realistic monthly revenue with growth trend
base_revenue = 7000000  # ₹70L base
revenue = [
    int(base_revenue * (1 + 0.03 * i) + np.random.randint(-200000, 300000))
    for i in range(12)
]

# Expenses ~ 65-70% of revenue
expenses = [int(r * np.random.uniform(0.62, 0.70)) for r in revenue]
profit   = [r - e for r, e in zip(revenue, expenses)]
margin   = [round((p / r) * 100, 2) for p, r in zip(profit, revenue)]

# Expense category breakdown (must sum to total expense per month)
fin_df = pd.DataFrame({
    'month':              months.strftime('%Y-%m'),
    'revenue':            revenue,
    'total_expense':      expenses,
    'profit':             profit,
    'profit_margin_pct':  margin,
    'operations_expense': [int(e * 0.45) for e in expenses],
    'marketing_expense':  [int(e * 0.20) for e in expenses],
    'finance_expense':    [int(e * 0.20) for e in expenses],
    'others_expense':     [int(e * 0.15) for e in expenses],
    'cash_flow':          [int(p * np.random.uniform(0.85, 1.10))
                           for p in profit],
    'accounts_receivable': [int(r * np.random.uniform(0.10, 0.20))
                            for r in revenue],
    'accounts_payable':   [int(e * np.random.uniform(0.08, 0.15))
                           for e in expenses],
})

fin_df.to_csv('data/synthetic_financial_data.csv', index=False)
print("✅ synthetic_financial_data.csv created")


# ─────────────────────────────────────────
# 4. GST RULES JSON
# ─────────────────────────────────────────
gst_rules = {
    "filing_deadlines": {
        "GSTR-1": {
            "description": "Outward supplies return",
            "due_date": "11th of next month",
            "frequency": "Monthly",
            "penalty_per_day": 50,
            "max_penalty": 5000
        },
        "GSTR-3B": {
            "description": "Monthly summary return",
            "due_date": "20th of next month",
            "frequency": "Monthly",
            "penalty_per_day": 50,
            "max_penalty": 5000
        },
        "GSTR-9": {
            "description": "Annual return",
            "due_date": "31st December",
            "frequency": "Annual",
            "penalty_per_day": 200,
            "max_penalty": 10000
        },
        "GSTR-2A": {
            "description": "Auto-drafted inward supplies",
            "due_date": "Auto-generated",
            "frequency": "Monthly",
            "penalty_per_day": 0,
            "max_penalty": 0
        }
    },
    "tax_slabs": {
        "0%":  ["Essential food items", "Healthcare services",
                "Education services"],
        "5%":  ["Household necessities", "Coal", "Lifesaving drugs",
                "Small restaurants"],
        "12%": ["Processed food", "Computers", "Business class air travel",
                "Ayurvedic medicines"],
        "18%": ["Most goods and services", "IT services", "Telecom",
                "Financial services", "Restaurants (AC)"],
        "28%": ["Luxury items", "Cars", "Tobacco", "Aerated drinks",
                "High-end motorcycles"]
    },
    "itc_rules": {
        "eligible": [
            "Inputs used for business",
            "Capital goods for business",
            "Input services for business"
        ],
        "ineligible": [
            "Personal use items",
            "Food and beverages",
            "Health and life insurance",
            "Works contract services for immovable property"
        ],
        "claim_window_months": 12
    },
    "compliance_scoring": {
        "filed_on_time":   30,
        "filed_late":      10,
        "pending":          0,
        "overdue":        -20,
        "itc_claimed":     20,
        "no_mismatches":   30
    },
    "penalty_rules": {
        "late_filing":        "₹50/day (₹25 CGST + ₹25 SGST)",
        "nil_return_late":    "₹20/day (₹10 CGST + ₹10 SGST)",
        "non_filing":         "18% interest on tax due + penalty",
        "fraud":              "100% of tax due as penalty"
    }
}

with open('data/gst_rules.json', 'w') as f:
    json.dump(gst_rules, f, indent=4)
print("✅ gst_rules.json created")


# ─────────────────────────────────────────
# 5. PAYROLL DATA (20 employees, 12 months)
# ─────────────────────────────────────────
np.random.seed(99)

departments = ['Engineering', 'Marketing', 'Sales',
               'Finance', 'HR', 'Operations']
designations = {
    'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead'],
    'Marketing':   ['Marketing Executive', 'Brand Manager', 'SEO Analyst'],
    'Sales':       ['Sales Executive', 'Sales Manager', 'BDM'],
    'Finance':     ['Accountant', 'Finance Analyst', 'CFO Assistant'],
    'HR':          ['HR Executive', 'Recruiter', 'HR Manager'],
    'Operations':  ['Operations Executive', 'Ops Manager', 'Coordinator']
}

# Base salaries per department (₹)
base_salaries = {
    'Engineering': (60000, 150000),
    'Marketing':   (40000, 90000),
    'Sales':       (35000, 85000),
    'Finance':     (50000, 110000),
    'HR':          (35000, 75000),
    'Operations':  (30000, 70000)
}

n_employees = 20
emp_departments  = np.random.choice(departments, n_employees)
emp_designations = [np.random.choice(designations[d])
                    for d in emp_departments]
emp_salaries     = [
    int(np.random.randint(*base_salaries[d]))
    for d in emp_departments
]

payroll_rows = []
for month in pd.date_range('2024-01-01', periods=12, freq='MS'):
    for i in range(n_employees):
        basic       = emp_salaries[i]
        hra         = int(basic * 0.40)
        allowances  = int(basic * 0.20)
        gross       = basic + hra + allowances

        pf_employee = int(basic * 0.12)   # Employee PF
        pf_employer = int(basic * 0.12)   # Employer PF
        esi         = int(gross * 0.0075) if gross <= 21000 else 0
        tds         = int(gross * 0.10)   if gross > 50000  else 0

        net_salary  = gross - pf_employee - esi - tds

        payroll_rows.append({
            'month':           month.strftime('%Y-%m'),
            'emp_id':          f'EMP{str(i+1).zfill(3)}',
            'department':      emp_departments[i],
            'designation':     emp_designations[i],
            'basic_salary':    basic,
            'hra':             hra,
            'allowances':      allowances,
            'gross_salary':    gross,
            'pf_employee':     pf_employee,
            'pf_employer':     pf_employer,
            'esi':             esi,
            'tds':             tds,
            'net_salary':      net_salary,
            'payment_status':  np.random.choice(
                                   ['paid', 'pending'],
                                   p=[0.95, 0.05])
        })

payroll_df = pd.DataFrame(payroll_rows)
payroll_df.to_csv('data/payroll_data.csv', index=False)
print("✅ payroll_data.csv created")


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
print("\n📁 All files created in data/ folder:")
print(f"   sample_transactions.csv     → {n} rows")
print(f"   gst_data.csv                → 50 invoices")
print(f"   synthetic_financial_data.csv→ 12 months P&L")
print(f"   gst_rules.json              → GST rules & slabs")
print(f"   payroll_data.csv            → {n_employees} employees × 12 months = {n_employees*12} rows")