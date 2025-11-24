from django.urls import path
from .import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.home_page, name='home'), 
    path('analys/', views.analys_page, name='analys'), 
    path('contact/', views.contact_page, name='contact'), 
    path('signin/', views.signin_page, name='signin'), 
    path('signup/', views.signup_page, name='signup'), 
    path('logout/', views.logout_view, name='logout'),


    path('profile/', views.profile_page, name='profile'),
    path('profile/<str:section>/', views.profile_page, name='profile'),
    path('analysis/create/', views.create_analysis, name='create_analysis'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:analysis_id>/delete/', views.delete_analysis, name='delete_analysis'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)