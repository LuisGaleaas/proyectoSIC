from django.contrib import admin
from .models import Empresa, AlternativaInversion, EvidenciaDocumental, CostoConcepto, FuenteDato


class CostoConceptoInline(admin.TabularInline):
    model = CostoConcepto
    extra = 1


class FuenteDatoInline(admin.TabularInline):
    model = FuenteDato
    extra = 1


class AlternativaInversionAdmin(admin.ModelAdmin):
    inlines = [CostoConceptoInline, FuenteDatoInline]


admin.site.register(Empresa)
admin.site.register(AlternativaInversion, AlternativaInversionAdmin)
admin.site.register(EvidenciaDocumental)