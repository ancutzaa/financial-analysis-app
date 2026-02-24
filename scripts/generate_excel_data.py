import pandas as pd
import datetime
import random


def generate_sample_excel(filename, scenario="healthy"):
    data = []
    assets = 500000
    liabilities = 150000

    for month in range(1, 13):
        report_date = datetime.date(2025, month, 28)

        if scenario == "healthy":
            profit = 5000 + (month * 1000)
            liabilities -= 2000
        elif scenario == "bankrupt":
            profit = -10000 - (month * 5000)
            liabilities += 15000
        else:
            profit = random.randint(-5000, 5000)
            liabilities += random.randint(-1000, 5000)

        #lista de dictionare
        data.append({
            'reporting_date': report_date,
            'net_profit': profit,
            'ebit': profit * 1.2,
            'sales_revenue': 100000 + (month * 2000),
            'depreciation': 2000,
            'operating_expenses': 80000,
            'total_assets': assets + profit,
            'current_assets': assets * 0.4,
            'inventory': 40000,
            'cash': 30000 if scenario == "healthy" else 1000,
            'total_liabilities': liabilities,
            'short_term_liabilities': liabilities * 0.7,
            'equity': assets - liabilities,
            'retained_earnings': 100000 + profit
        })

    #fiecare dictionar devine un rand din dataframe
    #keys devin nume de coloane, values devin date din celule
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)
    print(f"Generat: {filename} (Scenariu: {scenario})")


if __name__ == "__main__":
    generate_sample_excel("firma_buna.xlsx", scenario="healthy")
    generate_sample_excel("firma_probleme.xlsx", scenario="bankrupt")
    generate_sample_excel("firma_instabila.xlsx", scenario="unstable")