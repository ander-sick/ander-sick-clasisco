"""Django REST Framework - serializadores de la tienda."""
from rest_framework import serializers

from .models import Categoria, Marca, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ["id", "nombre", "slug", "url"]

    def get_url(self, obj):
        return obj.get_absolute_url()


class MarcaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Marca
        fields = ["id", "nombre", "slug"]


class ProductoSerializer(serializers.ModelSerializer):
    categoria = CategoriaSerializer(read_only=True)
    marca = MarcaSerializer(read_only=True)
    url = serializers.SerializerMethodField()
    descuento_porcentaje = serializers.IntegerField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id",
            "nombre",
            "slug",
            "precio",
            "precio_anterior",
            "descuento_porcentaje",
            "stock",
            "imagen",
            "descripcion",
            "categoria",
            "marca",
            "url",
        ]

    def get_url(self, obj):
        return obj.get_absolute_url()