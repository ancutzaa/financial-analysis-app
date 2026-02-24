from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'admin'
    ANALYST = 'analyst'
    CLIENT = 'client'

    ROLE_CHOICES = (
        (ADMIN, 'Administrator'),
        (ANALYST, 'Analist financiar'),
        (CLIENT, 'Client (firma)'),
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=CLIENT
    )

    def __str__(self):
        return f"{self.username}({self.get_role_display()})"

class Company(models.Model):
    name = models.CharField(max_length=255)
    cui = models.CharField(max_length=20, unique=True)
    address = models.TextField(blank=True, null=True)  # util pentru raportul PDF
    industry = models.CharField(max_length=100, blank=True, null=True)  # util pentru contextul ML
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    email_contact = models.EmailField(blank=True, null=True)

    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company',
        limit_choices_to={'role': User.CLIENT}
    )

    analyst = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_companies',
        limit_choices_to={'role': User.ANALYST}
    )

    is_onboarded = models.BooleanField(default=False)

    financial_summary = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.cui})"

    class Meta:
        verbose_name_plural = "Companies"

class FinancialUpload(models.Model):
    STATUS_CHOICES = (
        ('pending', 'În așteptare'),
        ('approved', 'Aprobat'),
        ('rejected', 'Respins'),
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='uploads')
    file = models.FileField(upload_to='imports/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_uploads',
        limit_choices_to={'role': User.ANALYST}  # Doar analiștii pot procesa
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Upload {self.company.name} - {self.status}"

class FinancialStatement(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='statements')
    source_upload = models.ForeignKey(FinancialUpload, on_delete=models.CASCADE, related_name='extracted_statements')
    reporting_date = models.DateField(help_text="Data bilanțului (ex: ultima zi a lunii)")

    net_profit = models.DecimalField(max_digits=15, decimal_places=2)
    ebit = models.DecimalField(max_digits=15, decimal_places=2)
    sales_revenue = models.DecimalField(max_digits=15, decimal_places=2)
    depreciation = models.DecimalField(max_digits=15, decimal_places=2)
    operating_expenses = models.DecimalField(max_digits=15, decimal_places=2)

    total_assets = models.DecimalField(max_digits=15, decimal_places=2)
    current_assets = models.DecimalField(max_digits=15, decimal_places=2)
    inventory = models.DecimalField(max_digits=15, decimal_places=2)
    cash = models.DecimalField(max_digits=15, decimal_places=2)

    total_liabilities = models.DecimalField(max_digits=15, decimal_places=2)
    short_term_liabilities = models.DecimalField(max_digits=15, decimal_places=2)
    equity = models.DecimalField(max_digits=15, decimal_places=2)
    retained_earnings = models.DecimalField(max_digits=15, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Financial Statement"
        verbose_name_plural = "Financial Statements"
        unique_together = ('company', 'reporting_date')
        ordering = ['-reporting_date']

    def __str__(self):
        return f"Statement {self.company.name} - {self.reporting_date}"

class KPISnapshot(models.Model):
    statement = models.OneToOneField(
        'FinancialStatement',
        on_delete=models.CASCADE,
        related_name='kpi_snapshot'
    )

    x1 = models.FloatField(null=True, blank=True, verbose_name="X1 (Net profit / total assets)")
    x2 = models.FloatField(null=True, blank=True, verbose_name="X2 (Total liabilities / total assets)")
    x3 = models.FloatField(null=True, blank=True, verbose_name="X3 (Working capital / total assets)")
    x4 = models.FloatField(null=True, blank=True, verbose_name="X4 (Current assets / short-term liabilities)")
    x5 = models.FloatField(null=True, blank=True,
                           verbose_name="X5 [(Cash + short-term securities + receivables - short-term liabilities) / (operating expenses - depreciation)] * 365")
    x6 = models.FloatField(null=True, blank=True, verbose_name="X6 (Retained earnings / total assets)")
    x7 = models.FloatField(null=True, blank=True, verbose_name="X7 (EBIT / total assets)")
    x8 = models.FloatField(null=True, blank=True, verbose_name="X8 (Book value of equity / total liabilities)")
    x9 = models.FloatField(null=True, blank=True, verbose_name="X9 (Sales / total assets)")
    x10 = models.FloatField(null=True, blank=True, verbose_name="X10 (Equity / total assets)")
    x11 = models.FloatField(null=True, blank=True,
                            verbose_name="X11 [(Gross profit + extraordinary items + financial expenses) / total assets]")
    x12 = models.FloatField(null=True, blank=True, verbose_name="X12 (Gross profit / short-term liabilities)")
    x13 = models.FloatField(null=True, blank=True, verbose_name="X13 [(Gross profit + depreciation) / sales]")
    x14 = models.FloatField(null=True, blank=True, verbose_name="X14 [(Gross profit + interest) / total assets]")
    x15 = models.FloatField(null=True, blank=True,
                            verbose_name="X15 [(Total liabilities * 365) / (gross profit + depreciation)]")
    x16 = models.FloatField(null=True, blank=True,
                            verbose_name="X16 [(Gross profit + depreciation) / total liabilities]")
    x17 = models.FloatField(null=True, blank=True, verbose_name="X17 (Total assets / total liabilities)")
    x18 = models.FloatField(null=True, blank=True, verbose_name="X18 (Gross profit / total assets)")
    x19 = models.FloatField(null=True, blank=True, verbose_name="X19 (Gross profit / sales)")
    x20 = models.FloatField(null=True, blank=True, verbose_name="X20 [(Inventory * 365) / sales]")
    x21 = models.FloatField(null=True, blank=True, verbose_name="X21 (Sales (n) / sales (n-1))")
    x22 = models.FloatField(null=True, blank=True, verbose_name="X22 (Profit on operating activities / total assets)")
    x23 = models.FloatField(null=True, blank=True, verbose_name="X23 (Net profit / sales)")
    x24 = models.FloatField(null=True, blank=True, verbose_name="X24 (Gross profit (in 3 years) / total assets)")
    x25 = models.FloatField(null=True, blank=True, verbose_name="X25 [(Equity - share capital) / total assets]")
    x26 = models.FloatField(null=True, blank=True, verbose_name="X26 [(Net profit + depreciation) / total liabilities]")
    x27 = models.FloatField(null=True, blank=True,
                            verbose_name="X27 (Profit on operating activities / financial expenses)")
    x28 = models.FloatField(null=True, blank=True, verbose_name="X28 (Working capital / fixed assets)")
    x29 = models.FloatField(null=True, blank=True, verbose_name="X29 (Logarithm of total assets)")
    x30 = models.FloatField(null=True, blank=True, verbose_name="X30 [(Total liabilities - cash) / sales]")
    x31 = models.FloatField(null=True, blank=True, verbose_name="X31 [(Gross profit + interest) / sales]")
    x32 = models.FloatField(null=True, blank=True,
                            verbose_name="X32 [(Current liabilities * 365) / cost of products sold]")
    x33 = models.FloatField(null=True, blank=True, verbose_name="X33 (Operating liabilities / total liabilities)")
    x34 = models.FloatField(null=True, blank=True, verbose_name="X34 (Operating liabilities / total expenses)")
    x35 = models.FloatField(null=True, blank=True, verbose_name="X35 (Profit on sales / total assets)")
    x36 = models.FloatField(null=True, blank=True, verbose_name="X36 (Total sales / total assets)")
    x37 = models.FloatField(null=True, blank=True,
                            verbose_name="X37 [(Current assets - inventories) / long-term liabilities]")
    x38 = models.FloatField(null=True, blank=True, verbose_name="X38 (Constant capital / total assets)")
    x39 = models.FloatField(null=True, blank=True, verbose_name="X39 (Profit on sales / sales)")
    x40 = models.FloatField(null=True, blank=True,
                            verbose_name="X40 [(Current assets - inventory - receivables) / short-term liabilities]")
    x41 = models.FloatField(null=True, blank=True,
                            verbose_name="X41 (Total liabilities / ((profit on operating activities + depreciation) * (12/365)))")
    x42 = models.FloatField(null=True, blank=True, verbose_name="X42 (Profit on operating activities / sales)")
    x43 = models.FloatField(null=True, blank=True, verbose_name="X43 [(Receivables * 365) / sales]")
    x44 = models.FloatField(null=True, blank=True, verbose_name="X44 [(Net profit + depreciation) / total liabilities]")
    x45 = models.FloatField(null=True, blank=True, verbose_name="X45 (Net profit / inventory)")
    x46 = models.FloatField(null=True, blank=True,
                            verbose_name="X46 (Current assets - inventory) / short-term liabilities")
    x47 = models.FloatField(null=True, blank=True, verbose_name="X47 [(Inventory * 365) / cost of products sold]")
    x48 = models.FloatField(null=True, blank=True,
                            verbose_name="X48 (EBITDA (profit on operating activities - depreciation) / total assets)")
    x49 = models.FloatField(null=True, blank=True,
                            verbose_name="X49 (EBITDA (profit on operating activities - depreciation) / sales)")
    x50 = models.FloatField(null=True, blank=True, verbose_name="X50 (Current assets / total liabilities)")
    x51 = models.FloatField(null=True, blank=True, verbose_name="X51 (Short-term liabilities / total assets)")
    x52 = models.FloatField(null=True, blank=True,
                            verbose_name="X52 [(Short-term liabilities * 365) / cost of products sold]")
    x53 = models.FloatField(null=True, blank=True, verbose_name="X53 (Equity / fixed assets)")
    x54 = models.FloatField(null=True, blank=True, verbose_name="X54 (Constant capital / fixed assets)")
    x55 = models.FloatField(null=True, blank=True, verbose_name="X55 (Working capital)")
    x56 = models.FloatField(null=True, blank=True, verbose_name="X56 [(Sales - cost of products sold) / sales]")
    x57 = models.FloatField(null=True, blank=True,
                            verbose_name="X57 [(Current assets - inventory - short-term liabilities) / (sales - gross profit - depreciation)]")
    x58 = models.FloatField(null=True, blank=True, verbose_name="X58 (Total costs /total sales)")
    x59 = models.FloatField(null=True, blank=True, verbose_name="X59 (Long-term liabilities / equity)")
    x60 = models.FloatField(null=True, blank=True, verbose_name="X60 (Sales / inventory)")
    x61 = models.FloatField(null=True, blank=True, verbose_name="X61 (Sales / receivables)")
    x62 = models.FloatField(null=True, blank=True, verbose_name="X62 [(Short-term liabilities * 365) / sales]")
    x63 = models.FloatField(null=True, blank=True, verbose_name="X63 (Sales / short-term liabilities)")
    x64 = models.FloatField(null=True, blank=True, verbose_name="X64 (Sales / fixed assets)")

    feature_importance_data = models.JSONField(
        null=True,
        blank=True,
        help_text="Top indicatori care au influențat predicția (ex: {'x2': 0.45, 'x4': 0.20})"
    )
    bankruptcy_probability = models.FloatField(null=True, blank=True, verbose_name="Probabilitate Faliment")
    prediction_label = models.CharField(max_length=50, null=True, blank=True, verbose_name="Etichetă Predicție")
    calculated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Snapshot KPI"
        verbose_name_plural = "Snapshots KPI"

    def __str__(self):
        return f"KPI {self.statement.company.name} - {self.statement.reporting_date}"

class Notification(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    action_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Notificare"
        verbose_name_plural = "Notificări"
        ordering = ['-created_at']

class MLModelVersion(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    file_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)

    accuracy = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ML model version"

class ReportRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'În așteptare'),
        ('in_progress', 'În lucru'),
        ('completed', 'Finalizat')
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='report_requests')
    analyst = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_report_requests',
        limit_choices_to={'role': User.ANALYST}
    )
    client_message = models.TextField(verbose_name="Mesaj/Cerințe Client",
                                      help_text="Ce dorește clientul să urmărească?")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class CustomReport(models.Model):
    request = models.OneToOneField(ReportRequest, on_delete=models.CASCADE, related_name='generated_report')
    analyst_message = models.TextField(verbose_name="Comentariu Analist",
                                       help_text="Explicații trimise clientului odată cu raportul")
    expert_recommendations = models.TextField()
    extra_data_json = models.JSONField(null=True, blank=True)
    pdf_file = models.FileField(upload_to='reports/custom/%Y/%m/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

class BaseReport(models.Model):
    snapshot = models.ForeignKey(
        'KPISnapshot',
        on_delete=models.CASCADE,
        related_name='base_reports'
    )
    pdf_file = models.FileField(upload_to='reports/standard/%Y/%m/', null=True, blank=True)
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Standard Report"
        verbose_name_plural = "Standard Reports"
        ordering = ['-generated_at']

    def __str__(self):
        return f"Raport Standard {self.snapshot.statement.company.name} - {self.snapshot.statement.reporting_date}"

