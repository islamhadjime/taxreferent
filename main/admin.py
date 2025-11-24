from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CompanyUser, Analysis

@admin.register(CompanyUser)
class CompanyUserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        (('Company Info'), {'fields': ('inn', 'ogrn', 'name', 'address', 'main_company', 'egrul_data')}),
    )
    list_display = BaseUserAdmin.list_display + ('inn', 'ogrn', 'name')
    search_fields = ('username', 'inn', 'ogrn', 'name')

@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'period_start_date', 'period_end_date', 'visible', 'is_positive_result', 'creation_date')
    list_filter = ('visible', 'is_positive_result', 'creation_date', 'user')
    search_fields = ('name', 'user__username', 'user__inn') 
    date_hierarchy = 'creation_date'