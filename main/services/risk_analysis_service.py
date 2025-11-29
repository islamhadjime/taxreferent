import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RiskAnalysisService:
    """
    Улучшенный сервис анализа рисков по методике ФНС
    """
    
    INDUSTRY_STANDARDS = {
        'profitability_sales': 9.6,  # Рентабельность продаж
        'profitability_assets': 5.4, # Рентабельность активов  
        'avg_salary': 43000,         # Средняя зарплата по отрасли
        'tax_burden': 8.0,           # Средняя налоговая нагрузка
    }
    
    @staticmethod
    def calculate_risk_analysis(form_data):
        """
        Основной метод анализа рисков по методике ФНС
        """
        try:
            print("🔍 Начинаем анализ рисков по методике ФНС...")
            
            # Подготовка данных
            analysis_data = RiskAnalysisService._prepare_data(form_data)
            
            # Расчет всех критериев ФНС
            fns_criteria = RiskAnalysisService._calculate_fns_criteria(analysis_data)
            
            # Определение индикаторов риска
            indicators = RiskAnalysisService._determine_risk_indicators(analysis_data, fns_criteria)
            
            # Итоговый результат
            result = RiskAnalysisService._compile_final_result(analysis_data, fns_criteria, indicators)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка при анализе рисков: {e}")
            raise

    @staticmethod
    def _calculate_fns_criteria(data):
        """Расчет всех 12 критериев ФНС"""
        print("📊 Расчет критериев ФНС...")
        criteria = {}
        
        # 1. Низкая налоговая нагрузка
        total_revenue = data.get('revenue_base_end', 0) + data.get('other_income_end', 0)
        total_taxes = data.get('total_taxes_paid_end', 0)
        
        if total_revenue > 0:
            criteria['tax_burden'] = (total_taxes / total_revenue) * 100
            criteria['low_tax_burden_risk'] = criteria['tax_burden'] < RiskAnalysisService.INDUSTRY_STANDARDS['tax_burden']
            print(f"   Критерий 1 - Налоговая нагрузка: {criteria['tax_burden']:.2f}% (риск: {criteria['low_tax_burden_risk']})")
        else:
            criteria['tax_burden'] = 0
            criteria['low_tax_burden_risk'] = True
        
        # 2. Наличие убытков
        profit_start = data.get('profit_sales_start', 0)
        profit_end = data.get('profit_sales_end', 0)
        criteria['loss_risk'] = profit_start < 0 and profit_end < 0
        print(f"   Критерий 2 - Убытки: старт={profit_start}, конец={profit_end} (риск: {criteria['loss_risk']})")
        
        # 3. Значительные налоговые вычеты по НДС (≥89%)
        vat_accrued = data.get('vat_accrued_end', 0)
        vat_deduction = data.get('vat_deduction_end', 0)
        
        if vat_accrued > 0:
            criteria['vat_deduction_ratio'] = (vat_deduction / vat_accrued) * 100
            criteria['high_vat_deduction_risk'] = criteria['vat_deduction_ratio'] >= 89
            print(f"   Критерий 3 - Вычеты НДС: {criteria['vat_deduction_ratio']:.2f}% (риск: {criteria['high_vat_deduction_risk']})")
        else:
            criteria['vat_deduction_ratio'] = 0
            criteria['high_vat_deduction_risk'] = False
        
        # 4. Темп роста расходов > темп роста доходов
        revenue_start = data.get('revenue_base_start', 0)
        revenue_end = data.get('revenue_base_end', 0)
        
        cost_start = (data.get('cost_sales_base_start', 0) + 
                     data.get('commercial_expenses_start', 0) + 
                     data.get('management_expenses_start', 0))
        cost_end = (data.get('cost_sales_base_end', 0) + 
                   data.get('commercial_expenses_end', 0) + 
                   data.get('management_expenses_end', 0))
        
        if revenue_start > 0 and cost_start > 0:
            revenue_growth = ((revenue_end - revenue_start) / revenue_start) * 100
            cost_growth = ((cost_end - cost_start) / cost_start) * 100
            criteria['expense_growth_risk'] = cost_growth > revenue_growth
            print(f"   Критерий 4 - Рост: выручка={revenue_growth:.2f}%, расходы={cost_growth:.2f}% (риск: {criteria['expense_growth_risk']})")
        else:
            criteria['expense_growth_risk'] = False
        
        # 5. Низкая среднемесячная зарплата
        employee_count = data.get('employee_count_end', 1)
        salary_fund = data.get('salary_fund_end', 0)
        
        if employee_count > 0:
            criteria['avg_salary'] = salary_fund / employee_count / 12
            criteria['low_salary_risk'] = criteria['avg_salary'] < RiskAnalysisService.INDUSTRY_STANDARDS['avg_salary']
            print(f"   Критерий 5 - Зарплата: {criteria['avg_salary']:.2f} (риск: {criteria['low_salary_risk']})")
        else:
            criteria['avg_salary'] = 0
            criteria['low_salary_risk'] = True
        
        # 6. Низкая рентабельность продаж
        revenue = data.get('revenue_base_end', 0)
        total_costs = (data.get('cost_sales_base_end', 0) + 
                      data.get('commercial_expenses_end', 0) + 
                      data.get('management_expenses_end', 0))
        
        if revenue > 0:
            criteria['profitability_sales'] = ((revenue - total_costs) / revenue) * 100
            criteria['low_profitability_sales_risk'] = (
                criteria['profitability_sales'] < RiskAnalysisService.INDUSTRY_STANDARDS['profitability_sales']
            )
            print(f"   Критерий 6 - Рент. продаж: {criteria['profitability_sales']:.2f}% (риск: {criteria['low_profitability_sales_risk']})")
        else:
            criteria['profitability_sales'] = 0
            criteria['low_profitability_sales_risk'] = True
        
        # 7. Низкая рентабельность активов
        profit_before_tax = data.get('profit_tax_base_end', 0)
        assets = data.get('balance_sheet_asset_end', 0)
        
        if assets > 0:
            criteria['profitability_assets'] = (profit_before_tax / assets) * 100
            criteria['low_profitability_assets_risk'] = (
                criteria['profitability_assets'] < RiskAnalysisService.INDUSTRY_STANDARDS['profitability_assets']
            )
            print(f"   Критерий 7 - Рент. активов: {criteria['profitability_assets']:.2f}% (риск: {criteria['low_profitability_assets_risk']})")
        else:
            criteria['profitability_assets'] = 0
            criteria['low_profitability_assets_risk'] = True
        
        # 8. Сомнительные контрагенты
        criteria['doubtful_counterparties_risk'] = data.get('doubtful_counterparties', False)
        
        # 9. Непредоставление пояснений
        criteria['no_explanation_risk'] = data.get('no_explanation_notification', False)
        
        # 10. Частая смена местонахождения
        criteria['location_change_risk'] = data.get('frequent_location_change', False)
        
        # 11. Неоднократное снятие и постановка на учет
        criteria['reregistration_risk'] = data.get('frequent_reregistration', False)
        
        # 12. Значительное отклонение уровня рентабельности
        criteria['profitability_deviation_risk'] = (
            criteria.get('profitability_sales', 0) < 5 or 
            criteria.get('profitability_assets', 0) < 3
        )
        
        print(f"   Качественные риски: контрагенты={criteria['doubtful_counterparties_risk']}, "
              f"пояснения={criteria['no_explanation_risk']}, адрес={criteria['location_change_risk']}")
        
        return criteria

    @staticmethod
    def _determine_risk_indicators(data, criteria):
        """Определение индикаторов риска на основе критериев ФНС"""
        print("🚦 Определение индикаторов риска...")
        indicators = {}
        
        # PRBM - Риск по прибыли/убыткам
        indicators['prbm'] = criteria['loss_risk']
        
        # OPTR - Операционный риск (рост расходов)
        indicators['optr'] = criteria['expense_growth_risk']
        
        # NDSS - Налоговые риски
        indicators['ndss'] = (
            criteria['low_tax_burden_risk'] or 
            criteria['high_vat_deduction_risk'] or
            criteria['no_explanation_risk']
        )
        
        # RETAB - Риск рентабельности
        indicators['retab'] = (
            criteria['low_profitability_sales_risk'] or 
            criteria['low_profitability_assets_risk'] or
            criteria['low_salary_risk'] or
            criteria['profitability_deviation_risk']
        )
        
        print(f"   Индикаторы: PRBM={indicators['prbm']}, OPTR={indicators['optr']}, "
              f"NDSS={indicators['ndss']}, RETAB={indicators['retab']}")
        
        return indicators

    @staticmethod
    def _compile_final_result(data, criteria, indicators):
        """Формирование итогового результата"""
        print("📋 Формирование итоговых результатов...")
        
        # Подсчет количества активных рисков (все 12 критериев)
        risk_count = sum([
            criteria['low_tax_burden_risk'],           # 1
            criteria['loss_risk'],                     # 2
            criteria['high_vat_deduction_risk'],       # 3
            criteria['expense_growth_risk'],           # 4
            criteria['low_salary_risk'],               # 5
            criteria['low_profitability_sales_risk'],  # 6
            criteria['low_profitability_assets_risk'], # 7
            criteria['doubtful_counterparties_risk'],  # 8
            criteria['no_explanation_risk'],           # 9
            criteria['location_change_risk'],          # 10
            criteria['reregistration_risk'],           # 11
            criteria['profitability_deviation_risk']   # 12
        ])
        
        # Общий балл риска (0-100)
        total_risk_score = min(risk_count * 8.33, 100)  # 100/12 ≈ 8.33 за каждый риск
        
        # Положительный результат - менее 3 рисков
        is_positive = risk_count < 3
        
        # Определение необходимости проверок
        finance_check = risk_count >= 4
        explanation_needed = any([
            criteria['no_explanation_risk'],
            criteria['doubtful_counterparties_risk'],
            criteria['high_vat_deduction_risk']
        ])
        accounting_check = any([
            criteria['low_tax_burden_risk'],
            criteria['high_vat_deduction_risk'],
            criteria['location_change_risk'],
            criteria['reregistration_risk']
        ])
        
        result = {
            # Основные метрики
            'profitability_ratio_start': round(criteria.get('profitability_sales', 0), 2),
            'profitability_ratio_end': round(criteria.get('profitability_sales', 0), 2),
            'revenue_growth': 0,  
            'profit_growth': 0,   
            'tax_burden': round(criteria.get('tax_burden', 0), 2),
            'risk_score': total_risk_score,
            
            # Индикаторы
            'prbm': indicators['prbm'],
            'optr': indicators['optr'],
            'ndss': indicators['ndss'],
            'retab': indicators['retab'],
            
            # Флаги проверок
            'finance_check': finance_check,
            'explanation_needed': explanation_needed,
            'accounting_check': accounting_check,
            
            # Итоговый результат
            'is_positive_result': is_positive,
            
            # Дополнительная информация для отчета
            'risk_count': risk_count,
            'total_criteria': 12,  # Все 12 критериев ФНС
            'avg_salary': round(criteria.get('avg_salary', 0), 2),
            'vat_deduction_ratio': round(criteria.get('vat_deduction_ratio', 0), 2),
            'profitability_assets': round(criteria.get('profitability_assets', 0), 2),
        }
        
        print(f"🎯 ИТОГ: {risk_count} рисков из 12, общий балл: {total_risk_score}, "
              f"положительный: {is_positive}")
        
        return result

    @staticmethod
    def _prepare_data(form_data):
        """Подготовка данных"""
        prepared_data = {}
        
        print("📊 Подготовка данных формы...")
        
        for key, value in form_data.items():
            if key.endswith(('_start', '_end')) and value:
                try:
                    prepared_data[key] = float(value)
                except (ValueError, TypeError):
                    prepared_data[key] = 0.0
            elif key in ['doubtful_counterparties', 'no_explanation_notification', 'frequent_location_change', 'frequent_reregistration']:
                prepared_data[key] = bool(value)
            elif key in ['period_start', 'period_end']:
                try:
                    prepared_data[key] = datetime.strptime(value, '%Y-%m-%d').date()
                except:
                    prepared_data[key] = datetime.now().date()
            else:
                prepared_data[key] = value
        
        return prepared_data
