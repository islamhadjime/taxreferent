# myapp/forms.py
from django import forms
from .models import CompanyUser, Analysis # Импортируем обновленные модели

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    verify_password = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")

    class Meta:
        model = CompanyUser
        fields = ['username', 'inn', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        verify_password = cleaned_data.get("verify_password")

        if password and verify_password and password != verify_password:
            self.add_error('verify_password', "Пароли не совпадают.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(label="Логин (Username)")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

class AnalysisForm(forms.Form): 
    V1 = forms.FloatField(label="V1", min_value=0, required=True)
    V2 = forms.FloatField(label="V2", min_value=0, required=True)
    Vr1 = forms.FloatField(label="Vr1", min_value=0, required=True)
    Vr2 = forms.FloatField(label="Vr2", min_value=0, required=True)
    
    date1 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Дата 1", required=True)
    date2 = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Дата 2", required=True)

    finance = forms.BooleanField(label="Финансы", required=False)
    uch = forms.BooleanField(label="Учет", required=False)
    pos = forms.BooleanField(label="Пояснения", required=False)

    NDSV1 = forms.FloatField(label="NDSV1", min_value=0, required=True)
    NDSV2 = forms.FloatField(label="NDSV2", min_value=0, required=True)
    NDSN1 = forms.FloatField(label="NDSN1", min_value=0, required=True)
    NDSN2 = forms.FloatField(label="NDSN2", min_value=0, required=True)
    POP1 = forms.FloatField(label="POP1", min_value=0, required=True)
    POP2 = forms.FloatField(label="POP2", min_value=0, required=True)
    PDN1 = forms.FloatField(label="PDN1", min_value=0, required=True)
    PDN2 = forms.FloatField(label="PDN2", min_value=0, required=True)
    PDN1R = forms.FloatField(label="PDN1R", min_value=0, required=True)
    PDN2R = forms.FloatField(label="PDN2R", min_value=0, required=True)
    PD1 = forms.FloatField(label="PD1", min_value=0, required=True)
    PD2 = forms.FloatField(label="PD2", min_value=0, required=True)
    SP1 = forms.FloatField(label="SP1", min_value=0, required=True)
    SP2 = forms.FloatField(label="SP2", min_value=0, required=True)
    SPr1 = forms.FloatField(label="SPr1", min_value=0, required=True)
    SPr2 = forms.FloatField(label="SPr2", min_value=0, required=True)
    KR1 = forms.FloatField(label="KR1", min_value=0, required=True)
    KR2 = forms.FloatField(label="KR2", min_value=0, required=True)
    UR1 = forms.FloatField(label="UR1", min_value=0, required=True)
    UR2 = forms.FloatField(label="UR2", min_value=0, required=True)
    CHS1 = forms.FloatField(label="CHS1", min_value=0, required=True)
    CHS2 = forms.FloatField(label="CHS2", min_value=0, required=True)
    OSFZP1 = forms.FloatField(label="OSFZP1", min_value=0, required=True)
    OSFZP2 = forms.FloatField(label="OSFZP2", min_value=0, required=True)
    ABB1 = forms.FloatField(label="ABB1", min_value=0, required=True)
    ABB2 = forms.FloatField(label="ABB2", min_value=0, required=True)
    PKN1 = forms.FloatField(label="PKN1", min_value=0, required=True)
    PKN2 = forms.FloatField(label="PKN2", min_value=0, required=True)
    IUN1 = forms.FloatField(label="IUN1", min_value=0, required=True)
    IUN2 = forms.FloatField(label="IUN2", min_value=0, required=True)


class EmailSettingsForm(forms.ModelForm):
    current_password = forms.CharField(widget=forms.PasswordInput, label="Текущий пароль", required=False)
    new_password = forms.CharField(widget=forms.PasswordInput, label="Новый пароль", required=False)
    new_password_confirm = forms.CharField(widget=forms.PasswordInput, label="Подтвердите новый пароль", required=False)

    class Meta:
        model = CompanyUser
        fields = ['email'] 

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        new_password_confirm = cleaned_data.get('new_password_confirm')

        if new_password and new_password_confirm and new_password != new_password_confirm:
            self.add_error('new_password_confirm', "Новые пароли не совпадают.")
        
        if new_password and not cleaned_data.get('current_password'):
            self.add_error('current_password', "Введите текущий пароль для смены.")

        return cleaned_data