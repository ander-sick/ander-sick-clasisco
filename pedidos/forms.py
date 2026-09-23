"""Formularios del proceso de compra (checkout)."""
from django import forms

from usuarios.models import Direccion

from .models import Pedido


class CheckoutForm(forms.Form):
    """Formulario de checkout: dirección de envío + método de pago.

    Permite reutilizar una dirección guardada o registrar una nueva.
    """

    direccion = forms.ModelChoiceField(
        queryset=Direccion.objects.none(),
        required=False,
        empty_label="Elegir una dirección guardada…",
        label="Dirección guardada",
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    # Nueva dirección (se validan en grupo si no se eligió una guardada)
    etiqueta = forms.CharField(
        label="Etiqueta", required=False, max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "Ej. Casa"}),
    )
    nombre_completo = forms.CharField(
        label="Nombre completo", required=False, max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nombre del destinatario"}),
    )
    telefono = forms.CharField(
        label="Teléfono", required=False, max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "55 1234 5678"}),
    )
    calle = forms.CharField(
        label="Calle y número", required=False, max_length=200,
        widget=forms.TextInput(attrs={"placeholder": "Calle, número y colonia"}),
    )
    ciudad = forms.CharField(label="Ciudad", required=False, max_length=100)
    estado = forms.CharField(label="Estado", required=False, max_length=100)
    codigo_postal = forms.CharField(label="Código postal", required=False, max_length=12)
    pais = forms.CharField(label="País", required=False, max_length=80, initial="México")
    referencias = forms.CharField(
        label="Referencias (opcional)", required=False, max_length=250,
        widget=forms.Textarea(attrs={"rows": 2}),
    )
    guardar_direccion = forms.BooleanField(
        label="Guardar esta nueva dirección para próximas compras",
        required=False,
    )

    # Pago
    metodo_pago = forms.ChoiceField(
        choices=Pedido.METODOS_PAGO,
        widget=forms.RadioSelect,
        label="Método de pago",
        initial="tarjeta",
    )
    notas = forms.CharField(
        label="Notas del pedido (opcional)", required=False, max_length=500,
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Instrucciones especiales…"}),
    )

    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)
        if self.usuario:
            self.fields["direccion"].queryset = Direccion.objects.filter(
                usuario=self.usuario
            )
        for nombre in [
            "etiqueta", "nombre_completo", "telefono", "calle", "ciudad",
            "estado", "codigo_postal", "pais", "referencias", "notas",
        ]:
            self.fields[nombre].widget.attrs.setdefault("class", "form-control")

    def _nueva_direccion_valida(self):
        """Indica si el formulario trae los datos mínimos de una nueva dirección."""
        return all(
            self.cleaned_data.get(campo)
            for campo in ["nombre_completo", "telefono", "calle", "ciudad",
                          "estado", "codigo_postal", "pais"]
        )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get("direccion") and not self._nueva_direccion_valida():
            raise forms.ValidationError(
                "Selecciona una dirección guardada o completa los datos de la "
                "nueva dirección."
            )
        return cleaned

    def obtener_direccion(self):
        """Devuelve la dirección elegida; crea y guarda la nueva si aplica."""
        if self.cleaned_data.get("direccion"):
            direccion = self.cleaned_data["direccion"]
        else:
            direccion = Direccion.objects.create(
                usuario=self.usuario,
                etiqueta=self.cleaned_data.get("etiqueta", "") or "Checkout",
                nombre_completo=self.cleaned_data["nombre_completo"],
                telefono=self.cleaned_data["telefono"],
                calle=self.cleaned_data["calle"],
                ciudad=self.cleaned_data["ciudad"],
                estado=self.cleaned_data["estado"],
                codigo_postal=self.cleaned_data["codigo_postal"],
                pais=self.cleaned_data["pais"],
                referencias=self.cleaned_data.get("referencias", ""),
                es_principal=self.cleaned_data.get("guardar_direccion", False),
            )
        return direccion