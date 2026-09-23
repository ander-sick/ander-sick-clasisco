"""Formularios de la tienda."""
from django import forms


class BusquedaForm(forms.Form):
    """Buscador de productos (usado en la barra de navegación y catálogo)."""

    q = forms.CharField(
        label="Buscar",
        required=False,
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar productos…",
                "aria-label": "Buscar productos",
            }
        ),
    )