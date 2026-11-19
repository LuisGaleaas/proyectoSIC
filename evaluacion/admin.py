from django.contrib import admin
from .models import Empresa, AlternativaInversion, EvidenciaDocumental, CostoConcepto


class CostoConceptoInline(admin.TabularInline):
    model = CostoConcepto
    extra = 1


class AlternativaInversionAdmin(admin.ModelAdmin):
    inlines = [CostoConceptoInline]


admin.site.register(Empresa)
admin.site.register(AlternativaInversion, AlternativaInversionAdmin)
admin.site.register(EvidenciaDocumental)