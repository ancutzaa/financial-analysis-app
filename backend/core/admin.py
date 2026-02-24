from django.contrib import admin
from .models import User, Company, FinancialUpload, FinancialStatement, KPISnapshot, MLModelVersion

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    list_filter = ('role', 'is_staff')

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'cui', 'owner', 'analyst')
    search_fields = ('name', 'cui')

@admin.register(FinancialUpload)
class FinancialUploadAdmin(admin.ModelAdmin):
    list_display = ('company', 'uploaded_at', 'status')
    list_filter = ('status',)

@admin.register(FinancialStatement)
class FinancialStatementAdmin(admin.ModelAdmin):
    list_display = ('company', 'reporting_date', 'net_profit', 'total_assets')
    list_filter = ('reporting_date', 'company')

@admin.register(KPISnapshot)
class KPISnapshotAdmin(admin.ModelAdmin):
    list_display = ('get_company_name', 'get_date', 'prediction_label', 'bankruptcy_probability')
    list_filter = ('prediction_label', 'statement__company')
    readonly_fields = ('calculated_at',) # Să nu poată fi modificată data calculului

    def get_company_name(self, obj):
        return obj.statement.company.name
    get_company_name.short_description = 'Companie'

    def get_date(self, obj):
        return obj.statement.reporting_date
    get_date.short_description = 'Data Raportării'

    fieldsets = (
        ('Informații Generale', {
            'fields': ('statement', 'calculated_at')
        }),
        ('Rezultat Predicție ML', {
            'fields': ('prediction_label', 'bankruptcy_probability', 'feature_importance_data'),
            'description': 'Aceste valori sunt generate automat de modelul Random Forest / XGBoost.'
        }),
        ('Indicatori de Profitabilitate (Exemplu: X1, X7, X11...)', {
            'classes': ('collapse',), # Această secțiune va fi restrânsă implicit
            'fields': ('x1', 'x7', 'x11', 'x13', 'x14', 'x18', 'x19', 'x22', 'x23', 'x24', 'x31', 'x35', 'x39', 'x42', 'x44', 'x48', 'x49', 'x56')
        }),
        ('Indicatori de Lichiditate și Capital de Lucru', {
            'classes': ('collapse',),
            'fields': ('x3', 'x4', 'x5', 'x12', 'x16', 'x28', 'x32', 'x33', 'x36', 'x40', 'x43', 'x45', 'x46', 'x47', 'x50', 'x52', 'x55', 'x57', 'x60', 'x61', 'x62', 'x63')
        }),
        ('Indicatori de Îndatorare și Structură', {
            'classes': ('collapse',),
            'fields': ('x2', 'x6', 'x8', 'x10', 'x15', 'x17', 'x25', 'x26', 'x29', 'x30', 'x34', 'x37', 'x38', 'x41', 'x51', 'x53', 'x54', 'x58', 'x59')
        }),
        ('Indicatori de Eficiență a Activelor', {
            'classes': ('collapse',),
            'fields': ('x9', 'x20', 'x21', 'x27', 'x64')
        }),
    )

@admin.register(MLModelVersion)
class MLModelVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'is_active', 'accuracy', 'f1_score', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'version')