from django.db import models

class Empresa(models.Model):
    nombre = models.CharField(max_length=150, default="4Seasons")
    giro = models.CharField(max_length=255, default="Comercialización de prendas de vestir y accesorios")
    propietario_contacto = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)

    class Meta:
        verbose_name_plural = "Empresa"

    def __str__(self):
        return self.nombre

class AlternativaInversion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='alternativas')
    nombre = models.CharField(max_length=150)  # Ej: Moto propia vs C807
    descripcion = models.TextField()
    inversion_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    costo_operativo_anual = models.DecimalField(max_digits=12, decimal_places=2)  # Gasolina/mantenimiento o fletes
    vida_util_anios = models.IntegerField(default=5)
    valor_salvamento = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    tasa_tmar = models.DecimalField(max_digits=5, decimal_places=2, help_text="TMAR en porcentaje (ej: 12 para 12%)")

    class Meta:
        verbose_name_plural = "Alternativas de Inversión"

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

class EvidenciaDocumental(models.Model):
    TIPO_CHOICES = [
        ('COTIZACION', 'Cotización de equipo / activo'),
        ('FACTURA', 'Factura o recibo de gasto'),
        ('ENTREVISTA', 'Registro de entrevista'),
        ('OTRO', 'Fotografía o documento de respaldo'),
    ]
    alternativa = models.ForeignKey(AlternativaInversion, on_delete=models.CASCADE, related_name='evidencias')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=255)
    archivo = models.FileField(upload_to='evidencias/')
    fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Evidencias Documentales"

    def __str__(self):
        return f"{self.tipo}: {self.descripcion}"