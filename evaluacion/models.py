from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Empresa(models.Model):
    nombre = models.CharField(max_length=150, default="4Seasons")
    giro = models.CharField(max_length=255, default="Comercialización de prendas de vestir y accesorios")
    propietario_contacto = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    # Tasa de impuesto sobre la renta según legislación salvadoreña (por defecto 30%)
    tasa_impuesto = models.DecimalField(
        max_digits=5, decimal_places=2, default=30.00,
        help_text="Tasa de ISR en % (ej. 30 para 30%)",
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)]
    )

    class Meta:
        verbose_name_plural = "Empresa"

    def __str__(self):
        return self.nombre

class AlternativaInversion(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, related_name='alternativas')
    nombre = models.CharField(max_length=150)  # Ej: Moto propia, Tercerizado C807, Bicicleta
    descripcion = models.TextField()
    
    # Parámetros financieros base
    inversion_inicial = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0.00, message="La inversión inicial no puede ser negativa.")]
    )
    costo_operativo_anual = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.00, message="El costo operativo no puede ser negativo.")]
    )
    ingreso_anual = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        help_text="Ingresos directos o ahorro anual bruto atribuible a esta alternativa",
        validators=[MinValueValidator(0.00)]
    )
    vida_util_anios = models.IntegerField(
        default=5,
        validators=[
            MinValueValidator(1, message="La vida útil mínima es de 1 año."),
            MaxValueValidator(50, message="La vida útil máxima permitida es de 50 años.")
        ]
    )
    valor_salvamento = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0.00, message="El valor de rescate no puede ser negativo.")]
    )
    tasa_tmar = models.DecimalField(
        max_digits=5, decimal_places=2,
        help_text="TMAR en porcentaje (ej: 12 para 12%)",
        validators=[
            MinValueValidator(0.01, message="La TMAR debe ser mayor al 0%."),
            MaxValueValidator(100.00, message="La TMAR no puede exceder el 100%.")
        ]
    )

    class Meta:
        verbose_name_plural = "Alternativas de Inversión"

    def clean(self):
        super().clean()
        if self.inversion_inicial > 0 and self.valor_salvamento > self.inversion_inicial:
            raise ValidationError({
                'valor_salvamento': 'El valor de salvamento no puede superar la inversión inicial.'
            })

    def __str__(self):
        return f"{self.nombre} - {self.empresa.nombre}"

class EvidenciaDocumental(models.Model):
    TIPO_CHOICES = [
        ('COTIZACION', 'Cotización de equipo / activo'),
        ('FACTURA', 'Factura o recibo de gasto'),
        ('ENTREVISTA', 'Registro de entrevista'),
        ('ESTADO_FINANCIERO', 'Estado financiero / Registro contable'),
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