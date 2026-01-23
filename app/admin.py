from django.contrib import admin
from .models import CajaCierre, CajaCierreEfectivo, CajaCierreDivisa, CajaCierreCheque, CajaCierreTarjeta

class CajaCierreEfectivoInline(admin.TabularInline):
    model = CajaCierreEfectivo
    extra = 0

class CajaCierreDivisaInline(admin.TabularInline):
    model = CajaCierreDivisa
    extra = 0

class CajaCierreChequeInline(admin.TabularInline):
    model = CajaCierreCheque
    extra = 0

class CajaCierreTarjetaInline(admin.TabularInline):
    model = CajaCierreTarjeta
    extra = 0

@admin.register(CajaCierre)
class CajaCierreAdmin(admin.ModelAdmin):
    list_display = ("id","vendedor_codigo","fecha_ini","fecha_fin","creado_por","creado_en")
    inlines = [CajaCierreEfectivoInline, CajaCierreDivisaInline, CajaCierreChequeInline, CajaCierreTarjetaInline]
