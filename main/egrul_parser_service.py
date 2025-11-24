# myapp/egrul_parser_service.py
import requests
from bs4 import BeautifulSoup
import time
import os
import logging
import re

logger = logging.getLogger(__name__)

def get_company_data_from_rusprofile(inn):
    """
    Получает данные компании с rusprofile.ru по ИНН.
    Возвращает словарь с данными или ошибкой.
    """
    url = f"https://www.rusprofile.ru/search?query={inn}&type=ul"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.rusprofile.ru/',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Инициализация данных
        company_data = {
            'name': "Не найдено",
            'full_name': "Не найдено", 
            'address': "Не найден",
            'ogrn': "Не найден",
            'inn': "Не найден",
            'kpp': "Не найден",
            'registration_date': "Не найдена",
            'director': "Не найден",
            'status': "Не найден",
            'main_activity': "Не найдена",
            'status': 'error'
        }
        
        # Проверяем, найдена ли компания
        not_found = soup.find('div', class_='search-result__notfound')
        if not_found:
            logger.warning(f"Компания с ИНН {inn} не найдена на Rusprofile.")
            return {'error': 'Компания не найдена', 'status': 'error'}
        
        # Поиск краткого названия компании
        name_element = soup.find('h1', itemprop='name')
        if name_element:
            company_data['name'] = name_element.text.strip()
        
        # Поиск полного названия компании
        full_name_element = soup.find('span', itemprop='legalName')
        if full_name_element:
            company_data['full_name'] = full_name_element.text.strip()
        
        # Поиск статуса компании
        status_element = soup.find('span', class_='company-header__icon success')
        if status_element:
            company_data['status'] = status_element.text.strip()
        
        # Поиск адреса
        address_element = soup.find('address', itemprop='address')
        if address_element:
            # Извлекаем текст адреса, убирая лишние пробелы
            address_text = ' '.join(address_element.stripped_strings)
            company_data['address'] = address_text
        
        # Поиск ОГРН
        ogrn_element = soup.find('span', id='clip_ogrn')
        if ogrn_element:
            company_data['ogrn'] = ogrn_element.text.strip()
        else:
            # Альтернативный поиск ОГРН
            ogrn_text = soup.find(string=re.compile(r'ОГРН'))
            if ogrn_text:
                ogrn_value = ogrn_text.find_next('dd')
                if ogrn_value:
                    company_data['ogrn'] = ogrn_value.text.strip()
        
        # Поиск ИНН
        inn_element = soup.find('span', id='clip_inn')
        if inn_element:
            company_data['inn'] = inn_element.text.strip()
        else:
            # Альтернативный поиск ИНН
            inn_text = soup.find('dt', string='ИНН/КПП')
            if inn_text:
                inn_value = inn_text.find_next('dd')
                if inn_value:
                    inn_span = inn_value.find('span', class_='copy_target')
                    if inn_span:
                        inn_kpp_text = inn_span.text.strip()
                        # Разделяем ИНН и КПП
                        if '/' in inn_kpp_text:
                            inn_part, kpp_part = inn_kpp_text.split('/', 1)
                            company_data['inn'] = inn_part.strip()
                            company_data['kpp'] = kpp_part.strip()
        
        # Поиск КПП (если не нашли выше)
        if company_data['kpp'] == "Не найден":
            kpp_element = soup.find('span', id='clip_kpp')
            if kpp_element:
                company_data['kpp'] = kpp_element.text.strip()
        
        # Поиск даты регистрации
        reg_date_element = soup.find('dt', string='Дата регистрации')
        if reg_date_element:
            reg_date_value = reg_date_element.find_next('dd')
            if reg_date_value:
                company_data['registration_date'] = reg_date_value.text.strip()
        
        # Поиск руководителя
        director_element = soup.find('span', class_='company-info__text')
        if director_element:
            director_link = director_element.find('a')
            if director_link:
                company_data['director'] = director_link.text.strip()
        
        # Поиск основного вида деятельности
        activity_element = soup.find('span', string=re.compile(r'Основной вид деятельности'))
        if not activity_element:
            activity_element = soup.find('span', class_='company-info__title', string='Основной вид деятельности')
        
        if activity_element:
            activity_value = activity_element.find_next('span', class_='company-info__text')
            if activity_value:
                company_data['main_activity'] = activity_value.text.strip()
        
        # Проверяем, что хотя бы основные данные найдены
        if company_data['name'] == "Не найдено" and company_data['full_name'] == "Не найдено":
            logger.warning(f"Не удалось извлечь данные компании с ИНН {inn}")
            return {'error': 'Не удалось извлечь данные компании', 'status': 'error'}
        
        # Если данные найдены, меняем статус на success
        company_data['status'] = 'success'
        
        # Логируем успешное извлечение
        logger.info(f"Успешно извлечены данные для ИНН {inn}: {company_data['name']}")
        
        return company_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка HTTP запроса к Rusprofile для ИНН {inn}: {e}")
        return {'error': f'Ошибка запроса: {str(e)}', 'status': 'error'}
    except Exception as e:
        logger.error(f"Общая ошибка при парсинге Rusprofile для ИНН {inn}: {e}")
        return {'error': f'Ошибка парсинга: {str(e)}', 'status': 'error'}

def get_company_data_with_retry(inn, max_retries=3):
    """
    Получает данные компании с повторными попытками при ошибках.
    """
    for attempt in range(max_retries):
        try:
            result = get_company_data_from_rusprofile(inn)
            if result.get('status') == 'success':
                return result
            elif attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Экспоненциальная задержка
                logger.info(f"Повторная попытка {attempt + 1} для ИНН {inn} через {wait_time} сек")
                time.sleep(wait_time)
        except Exception as e:
            logger.error(f"Ошибка в попытке {attempt + 1} для ИНН {inn}: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
    
    return {'error': 'Не удалось получить данные после всех попыток', 'status': 'error'}

def validate_inn(inn):
    """
    Проверяет валидность ИНН.
    """
    if not inn or not inn.isdigit():
        return False
    
    if len(inn) not in [10, 12]:
        return False
    
    return True

def download_egrul_document(inn):
    """
    Скачивает выписку из ЕГРЮЛ (упрощенная версия).
    В реальном проекте здесь будет логика скачивания с официальных источников.
    """
    try:
        # В реальном проекте здесь будет код для скачивания с egrul.nalog.ru
        # Сейчас возвращаем заглушку
        logger.info(f"Запрос на скачивание ЕГРЮЛ для ИНН {inn}")
        
        # Создаем папку для загрузок если её нет
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DOWNLOADS_DIR = os.path.join(BASE_DIR, 'downloads')
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)
        
        # В реальной реализации здесь будет логика скачивания
        # Пока возвращаем None как индикатор того, что функция вызвана
        return None
        
    except Exception as e:
        logger.error(f"Ошибка при обработке запроса ЕГРЮЛ для ИНН {inn}: {e}")
        return None

# Дополнительные утилиты
def format_company_data_for_display(company_data):
    """
    Форматирует данные компании для отображения в интерфейсе.
    """
    if company_data.get('status') != 'success':
        return company_data
    
    formatted_data = company_data.copy()
    
    # Форматирование адреса
    if formatted_data['address'] != "Не найден":
        # Убираем лишние пробелы и переносы
        formatted_data['address'] = ' '.join(formatted_data['address'].split())
    
    return formatted_data

def extract_company_contacts(soup):
    """
    Извлекает контактные данные компании (если доступны).
    """
    contacts = {
        'phone': 'Не указан',
        'email': 'Не указан',
        'website': 'Не указан'
    }
    
    try:
        # Поиск телефона
        phone_section = soup.find('div', class_='company-info__contact phone')
        if phone_section:
            phone_text = phone_section.get_text(strip=True)
            # Ищем паттерн телефона
            phone_match = re.search(r'[\+]?[7|8][\s]?[\(]?[0-9]{3}[\)]?[\s]?[0-9]{3}[\s]?[0-9]{2}[\s]?[0-9]{2}', phone_text)
            if phone_match:
                contacts['phone'] = phone_match.group()
        
        # Поиск email
        email_section = soup.find('div', class_='company-info__contact mail')
        if email_section:
            email_text = email_section.get_text(strip=True)
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email_text)
            if email_match:
                contacts['email'] = email_match.group()
        
        # Поиск сайта
        website_element = soup.find('span', class_='company-info__contact-title', string='Сайт')
        if website_element:
            website_value = website_element.find_next('a')
            if website_value and website_value.get('href'):
                contacts['website'] = website_value.get('href')
    
    except Exception as e:
        logger.warning(f"Не удалось извлечь контактные данные: {e}")
    
    return contacts