import pandas as pd
import numpy as np
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import FinancialUpload,FinancialStatement,KPISnapshot

def validate_and_parse_financial_excel(file_path, is_onboarding=True):
    try:
        df = pd.read_excel(file_path)
        df.columns = [col.strip().lower() for col in df.columns]

        required_columns = [
            'reporting_date',
            'net_profit',
            'ebit',
            'sales_revenue',
            'depreciation',
            'operating_expenses',
            'total_assets',
            'current_assets',
            'inventory',
            'cash',
            'total_liabilities',
            'short_term_liabilities',
            'equity',
            'retained_earnings'
        ]

        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValidationError(f"Fisier incomplet: Lipsesc: {', '.join(missing)}")

        if is_onboarding and len(df)<12:
            raise ValidationError(f"Onboarding esuat: Avem nevoie de 12 luni, dar fisierul are {len(df)}.")

        df['reporting_date'] = pd.to_datetime(df['reporting_date']).dt.date

        df = df.sort_values(by=['reporting_date'])
        return df

    except Exception as e:
        raise ValidationError(f"Eroare critică la citirea fișierului: {str(e)}")

def calculate_kpis(df):
    d = df.copy()

    working_capital = d['current_assets'] - d['short_term_liabilities']
    fixed_assets = d['total_assets'] - d['current_assets']
    cost_of_goods_sold = d['sales_revenue'] - d['net_profit']

    d['x1'] = d['net_profit'] / d['total_assets']
    d['x2'] = d['total_liabilities'] / d['total_assets']
    d['x3'] = working_capital / d['total_assets']
    d['x4'] = d['current_assets'] / d['short_term_liabilities']
    d['x5'] = ((d['cash'] + d['current_assets'] - d['inventory'] - d['short_term_liabilities']) /
               (d['operating_expenses'] - d['depreciation'])) * 365
    d['x6'] = d['retained_earnings'] / d['total_assets']
    d['x7'] = d['ebit'] / d['total_assets']
    d['x8'] = d['equity'] / d['total_liabilities']
    d['x9'] = d['sales_revenue'] / d['total_assets']
    d['x10'] = d['equity'] / d['total_assets']

    d['x11'] = (d['net_profit'] + d['depreciation']) / d['total_liabilities']
    d['x12'] = d['net_profit'] / d['short_term_liabilities']
    d['x13'] = (d['net_profit'] + d['depreciation']) / d['sales_revenue']
    d['x14'] = (d['net_profit'] + d['ebit']) / d['total_assets']
    d['x15'] = (d['total_liabilities'] * 365) / (d['net_profit'] + d['depreciation'])
    d['x16'] = (d['net_profit'] + d['depreciation']) / d['total_liabilities']
    d['x17'] = d['total_assets'] / d['total_liabilities']
    d['x18'] = d['net_profit'] / d['total_assets']
    d['x19'] = d['net_profit'] / d['sales_revenue']
    d['x20'] = (d['inventory'] * 365) / d['sales_revenue']

    d['x21'] = d['sales_revenue'] / d['sales_revenue'].shift(1)
    d['x22'] = d['ebit'] / d['total_assets']
    d['x23'] = d['net_profit'] / d['sales_revenue']
    d['x24'] = d['net_profit'] / d['total_assets']
    d['x25'] = (d['equity'] - d['retained_earnings']) / d['total_assets']
    d['x26'] = (d['net_profit'] + d['depreciation']) / d['total_liabilities']
    d['x27'] = d['ebit'] / d['operating_expenses']
    d['x28'] = working_capital / fixed_assets
    d['x29'] = np.log10(d['total_assets'].astype(float))
    d['x30'] = (d['total_liabilities'] - d['cash']) / d['sales_revenue']

    d['x31'] = (d['net_profit'] + d['ebit']) / d['sales_revenue']
    d['x32'] = (d['short_term_liabilities'] * 365) / cost_of_goods_sold
    d['x33'] = d['short_term_liabilities'] / d['total_liabilities']
    d['x34'] = d['operating_expenses'] / d['total_liabilities']
    d['x35'] = d['ebit'] / d['total_assets']
    d['x36'] = d['sales_revenue'] / d['total_assets']
    d['x37'] = (d['current_assets'] - d['inventory']) / (d['total_liabilities'] - d['short_term_liabilities'])
    d['x38'] = (d['equity'] + d['total_liabilities'] - d['short_term_liabilities']) / d['total_assets']
    d['x39'] = d['net_profit'] / d['sales_revenue']
    d['x40'] = (d['current_assets'] - d['inventory'] - d['cash']) / d['short_term_liabilities']

    d['x41'] = d['total_liabilities'] / ((d['ebit'] + d['depreciation']) * (12 / 365))
    d['x42'] = d['ebit'] / d['sales_revenue']
    d['x43'] = (d['current_assets'] * 365) / d['sales_revenue']
    d['x44'] = (d['net_profit'] + d['depreciation']) / d['total_liabilities']
    d['x45'] = d['net_profit'] / d['inventory']
    d['x46'] = (d['current_assets'] - d['inventory']) / d['short_term_liabilities']
    d['x47'] = (d['inventory'] * 365) / cost_of_goods_sold
    d['x48'] = (d['ebit'] - d['depreciation']) / d['total_assets']
    d['x49'] = (d['ebit'] - d['depreciation']) / d['sales_revenue']
    d['x50'] = d['current_assets'] / d['total_liabilities']

    d['x51'] = d['short_term_liabilities'] / d['total_assets']
    d['x52'] = (d['short_term_liabilities'] * 365) / cost_of_goods_sold
    d['x53'] = d['equity'] / fixed_assets
    d['x54'] = (d['equity'] + d['total_liabilities'] - d['short_term_liabilities']) / fixed_assets
    d['x55'] = working_capital
    d['x56'] = (d['sales_revenue'] - cost_of_goods_sold) / d['sales_revenue']
    d['x57'] = (d['current_assets'] - d['inventory'] - d['short_term_liabilities']) / (
                d['sales_revenue'] - d['net_profit'] - d['depreciation'])
    d['x58'] = d['operating_expenses'] / d['sales_revenue']
    d['x59'] = (d['total_liabilities'] - d['short_term_liabilities']) / d['equity']
    d['x60'] = d['sales_revenue'] / d['inventory']

    d['x61'] = d['sales_revenue'] / d['current_assets']
    d['x62'] = (d['short_term_liabilities'] * 365) / d['sales_revenue']
    d['x63'] = d['sales_revenue'] / d['short_term_liabilities']
    d['x64'] = d['sales_revenue'] / fixed_assets

    d = d.replace([float('inf'), float('-inf')], 0).fillna(0)

    return d

#doar in cazul in care toate lunile sunt valide salveaza in bd
def save_calculated_data(company, upload_instance, df_final):
    if upload_instance.status == 'approved':
        raise ValidationError('Acest fisier deja a fost procesat')

    with transaction.atomic():
        for _, row in df_final.iterrows():
            statement = FinancialStatement.objects.create(
                company=company,
                source_upload=upload_instance,  # Folosim instanța primită ca argument
                reporting_date=row['reporting_date'],
                net_profit=row['net_profit'],
                ebit=row['ebit'],
                sales_revenue=row['sales_revenue'],
                depreciation=row['depreciation'],
                operating_expenses=row['operating_expenses'],
                total_assets=row['total_assets'],
                current_assets=row['current_assets'],
                inventory=row['inventory'],
                cash=row['cash'],
                total_liabilities=row['total_liabilities'],
                short_term_liabilities=row['short_term_liabilities'],
                equity=row['equity'],
                retained_earnings=row['retained_earnings']
            )

            kpi_data = {f'x{i}': row.get(f'x{i}', 0) for i in range(1, 65)}

            KPISnapshot.objects.create(
                statement=statement,
                **kpi_data
            )

        upload_instance.status = 'approved'
        upload_instance.processed_at = timezone.now()
        upload_instance.save()

        company.is_onboarded = True
        company.save()

def process_financial_upload(upload_instance):
    try:
        onboarding_needed = not upload_instance.company.is_onboarded
        df_raw = validate_and_parse_financial_excel(
            upload_instance.file.path,
            is_onboarding=onboarding_needed
        )

        df_kpi = calculate_kpis(df_raw)

        save_calculated_data(upload_instance.company, upload_instance, df_kpi)

        return True, "Procesare reusita!"

    except ValidationError as e:
        upload_instance.status = 'rejected'
        upload_instance.rejection_reason = str(e)
        upload_instance.processed_at = timezone.now()
        upload_instance.save()
        return False, str(e)

    except Exception as e:
        upload_instance.status = 'rejected'
        upload_instance.rejection_reason = f"Eroare sistem: {str(e)}"
        upload_instance.processed_at = timezone.now()
        upload_instance.save()
        return False, "A intervenit o eroare tehnica neprevazuta"