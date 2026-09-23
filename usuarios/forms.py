"""Formularios de usuarios: registro, perfil y direcciones."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Direccion, Perfil


class RegistroForm(UserCreationForm):
    """Formulario de creación de cuenta con datos personales."""

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"placeholder": "tucorreo@ejemplo.com"}),
    )
    first_name = forms.CharField(
        label="Nombre", max_length=100, required=False
    )
    last_name = forms.CharField(
        label="Apellidos", max_length=100, required=False
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Nombre de usuario"}
        )
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este correo electrónico."
            )
        return email

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.email = self.cleaned_data["email"]
        usuario.first_name = self.cleaned_data.get("first_name", "")
        usuario.last_name = self.cleaned_data.get("last_name", "")
        if commit:
            usuario.save()
        return usuario


class PerfilForm(forms.ModelForm):
    """Formulario para editar datos personales (perfil + datos de usuario)."""

    nombre = forms.CharField(
        label="Nombre", max_length=100, required=False
    )
    apellidos = forms.CharField(
        label="Apellidos", max_length=100, required=False
    )
    email = forms.EmailField(label="Correo electrónico")

    class Meta:
        model = Perfil
        fields = ["telefono", "fecha_nacimiento", "avatar"]
        widgets = {
            "telefono": forms.TextInput(attrs={"placeholder": "55 1234 5678"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date"}, format="%Y-%m-%d"
            ),
        }

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)
        if self.usuario:
            self.fields["nombre"].initial = self.usuario.first_name
            self.fields["apellidos"].initial = self.usuario.last_name
            self.fields["email"].initial = self.usuario.email
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if (
            User.objects.filter(email=email)
            .exclude(pk=self.usuario.pk if self.usuario else None)
            .exists()
        ):
            raise forms.ValidationError("Este correo ya está en uso por otra cuenta.")
        return email

    def save(self, commit=True):
        perfil = super().save(commit=False)
        if self.usuario:
            self.usuario.first_name = self.cleaned_data.get("nombre", "")
            self.usuario.last_name = self.cleaned_data.get("apellidos", "")
            self.usuario.email = self.cleaned_data["email"]
            if commit:
                self.usuario.save()
        if commit:
            perfil.save()
        return perfil


class DireccionForm(forms.ModelForm):
    """Formulario de alta/edición de direcciones de envío."""

    class Meta:
        model = Direccion
        fields = [
            "etiqueta",
            "nombre_completo",
            "telefono",
            "calle",
            "ciudad",
            "estado",
            "codigo_postal",
            "pais",
            "referencias",
            "es_principal",
        ]
        widgets = {
            "etiqueta": forms.TextInput(attrs={"placeholder": "Casa"}),
            "nombre_completo": forms.TextInput(
                attrs={"placeholder": "Nombre y apellidos del destinatario"}
            ),
            "telefono": forms.TextInput(attrs={"placeholder": "55 1234 5678"}),
            "calle": forms.TextInput(
                attrs={"placeholder": "Calle, número y colonia"}
            ),
            "referencias": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for campo in self.fields.values():
            if isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs["class"] = "form-check-input"
            else:
                campo.widget.attrs.setdefault("class", "form-control")