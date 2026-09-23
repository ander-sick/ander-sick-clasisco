"""Vistas de usuarios: registro, sesión, perfil y direcciones."""
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import get_object_or_404, redirect, render

from tienda.services import obtener_carrito, transferir_carrito

from .forms import DireccionForm, PerfilForm, RegistroForm
from .models import Direccion, Perfil


def registro(request):
    """Registro de nuevos clientes."""
    if request.user.is_authenticated:
        return redirect("tienda:inicio")

    form = RegistroForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.save()
        Perfil.objects.get_or_create(usuario=usuario)
        login(request, usuario)
        transferir_carrito(request, usuario)
        messages.success(
            request, f"¡Bienvenido/a a CLASISCO, {usuario.username}! Tu cuenta fue creada."
        )
        return redirect("tienda:inicio")

    return render(request, "registro.html", {"form": form})


def iniciar_sesion(request):
    """Inicio de sesión de clientes."""
    if request.user.is_authenticated:
        return redirect("tienda:inicio")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        usuario = form.get_user()
        login(request, usuario)
        transferir_carrito(request, usuario)
        messages.success(request, f"¡Hola de nuevo, {usuario.username}!")
        siguiente = request.GET.get("next") or "tienda:inicio"
        return redirect(siguiente)

    return render(request, "iniciar_sesion.html", {"form": form})


def cerrar_sesion(request):
    """Cierre de sesión."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("tienda:inicio")


@login_required
def perfil(request):
    """Resumen del perfil del cliente."""
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    carrito = obtener_carrito(request)
    return render(
        request,
        "perfil.html",
        {
            "perfil": perfil,
            "total_pedidos": request.user.pedidos.count(),
            "total_direcciones": request.user.direcciones.count(),
            "total_favoritos": request.user.favoritos.count(),
            "carrito": carrito,
        },
    )


@login_required
def editar_perfil(request):
    """Formulario de edición de datos personales."""
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    form = PerfilForm(request.POST or None, request.FILES or None,
                      instance=perfil, usuario=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tus datos fueron actualizados correctamente.")
        return redirect("usuarios:perfil")

    return render(request, "perfil.html", {"form": form, "editando": True, "perfil": perfil})


@login_required
def direcciones(request):
    """Listado de direcciones del cliente."""
    return render(
        request,
        "direcciones.html",
        {"direcciones": request.user.direcciones.all()},
    )


@login_required
def nueva_direccion(request):
    """Alta de una nueva dirección."""
    form = DireccionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        direccion = form.save(commit=False)
        direccion.usuario = request.user
        direccion.save()
        messages.success(request, "Dirección guardada correctamente.")
        return redirect("usuarios:direcciones")

    return render(
        request,
        "direcciones.html",
        {"form": form, "direcciones": request.user.direcciones.all()},
    )


@login_required
def editar_direccion(request, pk):
    """Edición de una dirección existente."""
    direccion = get_object_or_404(Direccion, pk=pk, usuario=request.user)
    form = DireccionForm(request.POST or None, instance=direccion)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Dirección actualizada correctamente.")
        return redirect("usuarios:direcciones")

    return render(
        request,
        "direcciones.html",
        {"form": form, "direccion": direccion,
         "direcciones": request.user.direcciones.all()},
    )


@login_required
def eliminar_direccion(request, pk):
    """Eliminación de una dirección."""
    direccion = get_object_or_404(Direccion, pk=pk, usuario=request.user)
    direccion.delete()
    messages.success(request, "Dirección eliminada correctamente.")
    return redirect("usuarios:direcciones")