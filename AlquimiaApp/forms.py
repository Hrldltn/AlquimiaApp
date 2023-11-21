from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Inventario, User ,Calendario
# Importa tu modelo personalizado

class CustomUserCreationForm(UserCreationForm):
    date_joined = forms.DateTimeField(label="Fecha de ingreso", required=True, widget=forms.NumberInput(attrs={'type': 'date'}))
   
    class Meta:
        model = User 
        fields = ('first_name', 'last_name','rut', 'date_joined', 'username', 'is_administrador', 'is_chef')
     
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return username
    
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User 
        fields = ('username', 'password')
        
class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario 
        fields = ('nombre','descripcion','precio', 'porciones_disponibles')
        

class CalendarioForm(forms.ModelForm):
    start_time = forms.DateTimeField(label="Fecha de inicio", required=True, widget=forms.NumberInput(attrs={'type': 'date'}))
    end_time = forms.DateTimeField(label="Fecha de termino", required=True, widget=forms.NumberInput(attrs={'type': 'date'}))
    class Meta:
        model = Calendario
        fields = ('nombre','productos','start_time','end_time','Porciones')