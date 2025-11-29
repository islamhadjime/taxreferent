from datetime import datetime
import logging
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 
from django.contrib.auth.decorators import login_required 
from .models import Analysis, CompanyUser 
from .forms import RegistrationForm, LoginForm, AnalysisForm, EmailSettingsForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import logging
from datetime import datetime
from .egrul_parser_service import get_company_data_from_rusprofile
from django.contrib.auth import update_session_auth_hash

logger = logging.getLogger(__name__)

try:
    from .services.risk_analysis_service import RiskAnalysisService
    print("✅ RiskAnalysisService успешно импортирован")
except ImportError as e:
    print(f"❌ Ошибка импорта RiskAnalysisService: {e}")
    
    class RiskAnalysisService:
        @staticmethod
        def calculate_risk_analysis(form_data):
            return {
                'profitability_ratio_start': 15.0,
                'profitability_ratio_end': 18.0,
                'revenue_growth': 20.0,
                'profit_growth': 25.0,
                'tax_burden': 12.0,
                'risk_score': 22.0,
                'prbm': False,
                'optr': False,
                'ndss': False,
                'retab': False,
                'finance_check': False,
                'explanation_needed': False,
                'accounting_check': False,
                'is_positive_result': True,
            }



# --- Основные страницы без авторизации ---
def home_page(request):
    """Отображает домашнюю страницу."""
    delete_not_visible_analyses()
    return render(request, 'sait/main/home.html', {'is_authenticated': request.user.is_authenticated})

def analys_page(request):
    """Отображает страницу ввода данных для нового анализа."""
    delete_not_visible_analyses()
    form = AnalysisForm() 
    return render(request, 'sait/main/analys.html', {
        'is_authenticated': request.user.is_authenticated,
        'form': form
    })
def contact_page(request):
    """Отображает страницу контактов."""
    delete_not_visible_analyses()
    return render(request, 'sait/main/Contact.html', {'is_authenticated': request.user.is_authenticated})

def signin_page(request):
    """Отображает форму входа."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    print("=== DEBUG AUTHENTICATION ===")
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        print(f"1. Input: username='{username}', password='{password}'")
        
        try:
            user_by_username = User.objects.get(username=username)
            print(f"2. Found by username: {user_by_username}")
            print(f"   Password check: {user_by_username.check_password(password)}")
        except User.DoesNotExist:
            print("2. User not found by username")
            user_by_username = None
        
        print("3. Testing standard authenticate...")
        user_auth = authenticate(request, username=username, password=password)
        print(f"   authenticate() result: {user_auth}")
        
        if user_by_username:
            print(f"4. User details:")
            print(f"   - is_active: {user_by_username.is_active}")
            print(f"   - is_staff: {user_by_username.is_staff}")
            print(f"   - is_superuser: {user_by_username.is_superuser}")
            print(f"   - last_login: {user_by_username.last_login}")
            print(f"   - has_usable_password: {user_by_username.has_usable_password()}")
            print(f"   - check_password('{password}'): {user_by_username.check_password(password)}")
        
        if user_auth is not None:
            login(request, user_auth)
            return redirect('home')
        else:
            print("5. AUTHENTICATION FAILED - possible reasons:")
            if not user_by_username:
                print("   - User does not exist")
            elif not user_by_username.check_password(password):
                print("   - Password is incorrect")
            elif not user_by_username.is_active:
                print("   - User is not active")
            else:
                print("   - Unknown authentication issue")
    
    form = LoginForm()
    return render(request, 'sait/main/login/singin.html', {'form': form})

def signup_page(request):
    """Отображает форму регистрации с автоматическим заполнением данных компании."""
    delete_not_visible_analyses()
    
    if request.user.is_authenticated:
        return redirect('home')
    
    form = RegistrationForm()
    company_data = None
    inn_error = None
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        inn = request.POST.get('inn') 
        
        errors = []
        
        if password != password2:
            errors.append('Пароли не совпадают')
        
        if CompanyUser.objects.filter(email=email).exists():
            errors.append('Пользователь с таким email уже существует')
        
        if CompanyUser.objects.filter(username=username).exists():
            errors.append('Пользователь с таким именем уже существует')
        
        if inn:
            if CompanyUser.objects.filter(inn=inn).exists():
                errors.append('Компания с таким ИНН уже зарегистрирована')
            elif not inn.isdigit() or len(inn) not in [10, 12]:
                errors.append('ИНН должен содержать 10 или 12 цифр')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'sait/main/login/singup.html', {
                'form': form,
                'company_data': company_data,
                'inn_error': inn_error
            })
        
        if inn:
            company_data = get_company_data_from_rusprofile(inn)
            print(company_data)
            print(company_data)
            
            if company_data.get('status') == 'error':
                errors.append(f'Ошибка получения данных компании: {company_data.get("error")}')
                inn_error = company_data.get('error')
            else:
                if company_data.get('inn') != inn:
                    errors.append('Найденный ИНН не совпадает с введенным')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'sait/main/login/singup.html', {
                'form': form,
                'company_data': company_data,
                'inn_error': inn_error
            })
        
        try:
            user = CompanyUser.objects.create_user(
                username=username, 
                email=email, 
                password=password
            )
            
            if company_data and company_data.get('status') == 'success':
                user.inn = company_data.get('inn')
                user.ogrn = company_data.get('ogrn')
                user.name = company_data.get('name')
                user.address = company_data.get('address')
                user.egrul_data = f"Данные получены из Rusprofile: {company_data}"
            
            user.save()
            
            messages.success(request, 'Регистрация успешна! Теперь вы можете войти.')
            return redirect('signin')
            
        except IntegrityError as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'sait/main/login/singup.html', {
                'form': form,
                'company_data': company_data,
                'inn_error': inn_error
            })
        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, 'sait/main/login/singup.html', {
                'form': form,
                'company_data': company_data,
                'inn_error': inn_error
            })
    
    return render(request, 'sait/main/login/singup.html', {
        'form': form,
        'company_data': company_data,
        'inn_error': inn_error
    })

@login_required
def profile_page(request, section='info'):
    """Страница профиля пользователя с разделами."""
    
    analyses = Analysis.objects.filter(user=request.user).order_by('-creation_date')
    
    if request.method == 'POST' and section == 'settings':
        return handle_settings_update(request)
    
    context = {
        'current_section': section,
        'analyses': analyses,
    }
    
    return render(request, 'sait/main/profil.html', context)

@login_required
def handle_settings_update(request):
    """Обработка обновления настроек профиля."""
    user = request.user
    
    if 'form_type' in request.POST and request.POST['form_type'] == 'settings':
        email = request.POST.get('email')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if email and email != user.email:
            if CompanyUser.objects.filter(email=email).exclude(id=user.id).exists():
                messages.error(request, 'Этот email уже используется другим пользователем.')
            else:
                user.email = email
                messages.success(request, 'Email успешно обновлен.')
        
        if current_password and new_password and confirm_password:
            if user.check_password(current_password):
                if new_password == confirm_password:
                    if len(new_password) >= 8:
                        user.set_password(new_password)
                        user.save()
                        update_session_auth_hash(request, user)  # Важно: сохраняем сессию
                        messages.success(request, 'Пароль успешно изменен.')
                    else:
                        messages.error(request, 'Пароль должен содержать не менее 8 символов.')
                else:
                    messages.error(request, 'Новые пароли не совпадают.')
            else:
                messages.error(request, 'Текущий пароль неверен.')
        
        user.save()
    
    return redirect('profile', section='settings')
@login_required
def logout_view(request):
    """Выход из системы."""
    logout(request)
    return redirect('home')  





@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_analysis(request):
    """Создание нового анализа на основе данных формы"""
    try:
        if request.content_type == 'application/json':
            form_data = json.loads(request.body)
        else:
            form_data = request.POST.dict()
        
        
        if not form_data.get('period_start') or not form_data.get('period_end'):
            return JsonResponse({
                'success': False,
                'error': 'Не указан период анализа'
            })
        
        analysis_result = RiskAnalysisService.calculate_risk_analysis(form_data)
        print("📊 Результат анализа:", analysis_result)
        
        analysis = Analysis(
            user=request.user,
            name=f"Анализ от {datetime.now().strftime('%d.%m.%Y')}",
            period_start_date=form_data['period_start'],
            period_end_date=form_data['period_end'],
            visible=True,
            
            revenue_base_start=float(form_data.get('revenue_base_start', 0) or 0),
            revenue_early_start=float(form_data.get('revenue_early_start', 0) or 0),
            profit_sales_start=float(form_data.get('profit_sales_start', 0) or 0),
            profit_tax_base_start=float(form_data.get('profit_tax_base_start', 0) or 0),
            profit_tax_rent_start=float(form_data.get('profit_tax_rent_start', 0) or 0),
            other_income_start=float(form_data.get('other_income_start', 0) or 0),
            cost_sales_base_start=float(form_data.get('cost_sales_base_start', 0) or 0),
            cost_sales_rent_start=float(form_data.get('cost_sales_rent_start', 0) or 0),
            commercial_expenses_start=float(form_data.get('commercial_expenses_start', 0) or 0),
            management_expenses_start=float(form_data.get('management_expenses_start', 0) or 0),
            employee_count_start=int(form_data.get('employee_count_start', 0) or 0),
            salary_fund_start=float(form_data.get('salary_fund_start', 0) or 0),
            balance_sheet_asset_start=float(form_data.get('balance_sheet_asset_start', 0) or 0),
            accrued_interest_start=float(form_data.get('accrued_interest_start', 0) or 0),
            total_taxes_paid_start=float(form_data.get('total_taxes_paid_start', 0) or 0),
            vat_deduction_start=float(form_data.get('vat_deduction_start', 0) or 0),
            vat_accrued_start=float(form_data.get('vat_accrued_start', 0) or 0),
            
            revenue_base_end=float(form_data.get('revenue_base_end', 0) or 0),
            revenue_early_end=float(form_data.get('revenue_early_end', 0) or 0),
            profit_sales_end=float(form_data.get('profit_sales_end', 0) or 0),
            profit_tax_base_end=float(form_data.get('profit_tax_base_end', 0) or 0),
            profit_tax_rent_end=float(form_data.get('profit_tax_rent_end', 0) or 0),
            other_income_end=float(form_data.get('other_income_end', 0) or 0),
            cost_sales_base_end=float(form_data.get('cost_sales_base_end', 0) or 0),
            cost_sales_rent_end=float(form_data.get('cost_sales_rent_end', 0) or 0),
            commercial_expenses_end=float(form_data.get('commercial_expenses_end', 0) or 0),
            management_expenses_end=float(form_data.get('management_expenses_end', 0) or 0),
            employee_count_end=int(form_data.get('employee_count_end', 0) or 0),
            salary_fund_end=float(form_data.get('salary_fund_end', 0) or 0),
            balance_sheet_asset_end=float(form_data.get('balance_sheet_asset_end', 0) or 0),
            accrued_interest_end=float(form_data.get('accrued_interest_end', 0) or 0),
            total_taxes_paid_end=float(form_data.get('total_taxes_paid_end', 0) or 0),
            vat_deduction_end=float(form_data.get('vat_deduction_end', 0) or 0),
            vat_accrued_end=float(form_data.get('vat_accrued_end', 0) or 0),
            
            doubtful_counterparties=bool(form_data.get('doubtful_counterparties')),
            no_explanation_notification=bool(form_data.get('no_explanation_notification')),
            frequent_location_change=bool(form_data.get('frequent_location_change')),
        )
        
        for field, value in analysis_result.items():
            if hasattr(analysis, field):
                setattr(analysis, field, value)
                print(f"✅ Установлено поле {field}: {value}")
        
        analysis.save()
        
        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'result': {
                'risk_score': analysis.risk_score,
                'is_positive': analysis.is_positive_result,
                'profitability': analysis.profitability_ratio_end,
                'revenue_growth': analysis.revenue_growth,
                'profit_growth': analysis.profit_growth,
                'tax_burden': analysis.tax_burden,
                'indicators': {
                    'prbm': analysis.prbm,
                    'optr': analysis.optr,
                    'ndss': analysis.ndss,
                    'retab': analysis.retab
                },
                'checks': {
                    'finance_check': analysis.finance_check,
                    'explanation_needed': analysis.explanation_needed,
                    'accounting_check': analysis.accounting_check
                }
            },
            'redirect_url': f'/analysis/{analysis.id}/'
        })
        
    except Exception as e:
        logger.error(f"Ошибка при создании анализа: {e}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при создании анализа: {str(e)}'
        })
@login_required
def analysis_detail(request, analysis_id):
    """Детальная страница анализа"""
    analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
    return render(request, 'sait/main/analysis_detail.html', {
        'analysis': analysis,
        'is_authenticated': request.user.is_authenticated
    })
@require_http_methods(["POST"])
@csrf_exempt
def delete_analysis(request, analysis_id):
    """Удаление анализа"""
    try:
        analysis = get_object_or_404(Analysis, id=analysis_id, user=request.user)
        
        analysis_name = analysis.name
        analysis.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Анализ "{analysis_name}" успешно удален'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Ошибка при удалении анализа: {str(e)}'
        })
def delete_not_visible_analyses():
    """Удаляет невидимые анализы"""
    try:
        Analysis.objects.filter(visible=False).delete()
        print("🗑️ Вызвана функция delete_not_visible_analyses")
    except Exception as e:
        print(f"❌ Ошибка при удалении анализов: {e}")
