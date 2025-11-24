import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

project_folder = os.path.dirname(__file__)
if project_folder not in sys.path:
    sys.path.insert(0, project_folder)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject1.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()