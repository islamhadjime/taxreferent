from django.db import models
from django.contrib.auth.models import AbstractUser

class CompanyUser(AbstractUser):
    
    inn = models.CharField(max_length=12, unique=True, null=True, blank=True)
    ogrn = models.CharField(max_length=13, unique=True, null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    main_company = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    egrul_data = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Компания/Пользователь"
        verbose_name_plural = "Компании/Пользователи"

    def __str__(self):
        return self.name or self.username

class Analysis(models.Model):
    user = models.ForeignKey(
        CompanyUser,
        on_delete=models.CASCADE,
        related_name='analyses',
        verbose_name="Компания/Пользователь"
    )
    
    name = models.CharField(max_length=255, default="Безымянный анализ", verbose_name="Название анализа")
    visible = models.BooleanField(default=False, verbose_name="Видимый для пользователя")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    period_start_date = models.DateField(verbose_name="Начало отчетного периода")
    period_end_date = models.DateField(verbose_name="Конец отчетного периода")

    # начало периода
    revenue_base_start = models.FloatField(default=0.0, verbose_name="Выручка базового периода (начало)")
    revenue_early_start = models.FloatField(default=0.0, verbose_name="Выручка раннего периода (начало)")
    profit_sales_start = models.FloatField(default=0.0, verbose_name="Прибыль от продаж (начало)")
    profit_tax_base_start = models.FloatField(default=0.0, verbose_name="Прибыль до налогообложения базовый (начало)")
    profit_tax_rent_start = models.FloatField(default=0.0, verbose_name="Прибыль до налогообложения ренный (начало)")
    other_income_start = models.FloatField(default=0.0, verbose_name="Прочие доходы (начало)")
    cost_sales_base_start = models.FloatField(default=0.0, verbose_name="Себестоимость продаж базовый (начало)")
    cost_sales_rent_start = models.FloatField(default=0.0, verbose_name="Себестоимость продаж ренный (начало)")
    commercial_expenses_start = models.FloatField(default=0.0, verbose_name="Коммерческие расходы (начало)")
    management_expenses_start = models.FloatField(default=0.0, verbose_name="Управленческие расходы (начало)")
    employee_count_start = models.IntegerField(default=0, verbose_name="Численность сотрудников (начало)")
    salary_fund_start = models.FloatField(default=0.0, verbose_name="Фонд заработной платы (начало)")
    balance_sheet_asset_start = models.FloatField(default=0.0, verbose_name="Актив баланса (начало)")
    accrued_interest_start = models.FloatField(default=0.0, verbose_name="Проценты к начислению (начало)")
    total_taxes_paid_start = models.FloatField(default=0.0, verbose_name="Итого уплаченных налогов (начало)")
    vat_deduction_start = models.FloatField(default=0.0, verbose_name="НДС вычет (начало)")
    vat_accrued_start = models.FloatField(default=0.0, verbose_name="НДС начислил (начало)")

    # конец периода
    revenue_base_end = models.FloatField(default=0.0, verbose_name="Выручка базового периода (конец)")
    revenue_early_end = models.FloatField(default=0.0, verbose_name="Выручка раннего периода (конец)")
    profit_sales_end = models.FloatField(default=0.0, verbose_name="Прибыль от продаж (конец)")
    profit_tax_base_end = models.FloatField(default=0.0, verbose_name="Прибыль до налогообложения базовый (конец)")
    profit_tax_rent_end = models.FloatField(default=0.0, verbose_name="Прибыль до налогообложения ренный (конец)")
    other_income_end = models.FloatField(default=0.0, verbose_name="Прочие доходы (конец)")
    cost_sales_base_end = models.FloatField(default=0.0, verbose_name="Себестоимость продаж базовый (конец)")
    cost_sales_rent_end = models.FloatField(default=0.0, verbose_name="Себестоимость продаж ренный (конец)")
    commercial_expenses_end = models.FloatField(default=0.0, verbose_name="Коммерческие расходы (конец)")
    management_expenses_end = models.FloatField(default=0.0, verbose_name="Управленческие расходы (конец)")
    employee_count_end = models.IntegerField(default=0, verbose_name="Численность сотрудников (конец)")
    salary_fund_end = models.FloatField(default=0.0, verbose_name="Фонд заработной платы (конец)")
    balance_sheet_asset_end = models.FloatField(default=0.0, verbose_name="Актив баланса (конец)")
    accrued_interest_end = models.FloatField(default=0.0, verbose_name="Проценты к начислению (конец)")
    total_taxes_paid_end = models.FloatField(default=0.0, verbose_name="Итого уплаченных налогов (конец)")
    vat_deduction_end = models.FloatField(default=0.0, verbose_name="НДС вычет (конец)")
    vat_accrued_end = models.FloatField(default=0.0, verbose_name="НДС начислил (конец)")

    # Факторы риска (булевы поля)
    doubtful_counterparties = models.BooleanField(default=False, verbose_name="Сомнительные контрагенты")
    no_explanation_notification = models.BooleanField(default=False, verbose_name="Отсутствие пояснений")
    frequent_location_change = models.BooleanField(default=False, verbose_name="Частая смена местонахождения")

    # Результаты анализа (рассчитываемые поля)
    profitability_ratio_start = models.FloatField(default=0.0, verbose_name="Рентабельность (начало)")
    profitability_ratio_end = models.FloatField(default=0.0, verbose_name="Рентабельность (конец)")
    revenue_growth = models.FloatField(default=0.0, verbose_name="Рост выручки")
    profit_growth = models.FloatField(default=0.0, verbose_name="Рост прибыли")
    tax_burden = models.FloatField(default=0.0, verbose_name="Налоговая нагрузка")
    risk_score = models.FloatField(default=0.0, verbose_name="Общий балл риска")

    # Логические индикаторы (рассчитываемые)
    prbm = models.BooleanField(default=False, verbose_name="Индикатор PRBM")
    optr = models.BooleanField(default=False, verbose_name="Индикатор OPTR")
    ndss = models.BooleanField(default=False, verbose_name="Индикатор NDSS")
    retab = models.BooleanField(default=False, verbose_name="Индикатор RETAB")

    # Дополнительные флаги
    finance_check = models.BooleanField(default=False, verbose_name="Финансовая проверка")
    explanation_needed = models.BooleanField(default=False, verbose_name="Требуется пояснение")
    accounting_check = models.BooleanField(default=False, verbose_name="Бухгалтерская проверка")
    
    # Итоговый результат
    is_positive_result = models.BooleanField(default=False, verbose_name="Положительный результат анализа")

    class Meta:
        verbose_name = "Анализ"
        verbose_name_plural = "Анализы"
        ordering = ['-creation_date']

    def __str__(self):
        return f"Анализ '{self.name}' для {self.user} ({self.period_start_date} - {self.period_end_date})"