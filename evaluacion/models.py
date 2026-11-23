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
    nombre = models.CharField(max_length=150)  # Ej: Moto propia, Tercerizado C807
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

    # Campos de Auditoría, Proveedores y Trazabilidad (Editables desde Admin)
    justificacion_seleccion = models.TextField(
        blank=True,
        verbose_name="¿Por qué se evaluó esta alternativa?",
        help_text="Explica la necesidad operativa en 4Seasons y el criterio de selección."
    )
    detalle_inversion = models.TextField(
        blank=True,
        verbose_name="Desglose y Proveedor de Inversión Inicial",
        help_text="Ej: Concesionario donde se cotizó la moto, modelo, placas y matrícula."
    )
    detalle_costos_operativos = models.TextField(
        blank=True,
        verbose_name="Desglose de Costos Operativos y Seguros",
        help_text="Ej: Aseguradora, talleres de mantenimiento, consumo de gasolina o tarifas de envíos."
    )
    fuentes_verificacion = models.TextField(
        blank=True,
        verbose_name="Fuentes de Verificación (Auditoría)",
        help_text="Ej: Cotización #104, Entrevista con propietario (fecha), Registros contables."
    )

    class Meta:
        verbose_name_plural = "Alternativas de Inversión"

    def clean(self):
        super().clean()
        if self.inversion_inicial > 0 and self.valor_salvamento > self.inversion_inicial:
            raise ValidationError({
                'valor_salvamento': 'El valor de salvamento no puede superar la inversión inicial.'
            })
        
    @property
    def total_costos_detallados(self):
        return sum((c.monto_anual for c in self.costos.all()), 0)

    @property
    def costos_cuadran(self):
        return self.total_costos_detallados == self.costo_operativo_anual

    @property
    def fuentes_por_dato(self):
        valores = {
            'INVERSION': f"${self.inversion_inicial}",
            'INGRESO': f"${self.ingreso_anual}",
            'VIDA_UTIL': f"{self.vida_util_anios} años",
            'TMAR': f"{self.tasa_tmar}%",
        }
        todas = [f for f in self.fuentes_datos.all() if f.fuente_evidencia_id or f.fuente_nota.strip()]
        resultado = []
        for clave, etiqueta in FuenteDato.DATO_CHOICES:
            fuentes = [f for f in todas if f.dato == clave]
            resultado.append({
                'etiqueta': etiqueta,
                'valor': valores[clave],
                'fuentes': fuentes,
                'cantidad': len(fuentes),
                'completo': len(fuentes) >= 2,
            })
        return resultado

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"

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

class CostoConcepto(models.Model):
    """Desglose del costo operativo anual, cada rubro con su fuente."""
    alternativa = models.ForeignKey(AlternativaInversion, on_delete=models.CASCADE, related_name='costos')
    concepto = models.CharField(max_length=150, help_text="Ej: Gasolina, Seguro, Mantenimiento, Tarifa C807")
    monto_anual = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.00, message="El monto no puede ser negativo.")]
    )
    fuente_evidencia = models.ForeignKey(
        EvidenciaDocumental, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="Evidencia (archivo subido)"
    )
    fuente_nota = models.CharField(
        max_length=255, blank=True,
        verbose_name="Otra fuente",
        help_text="Ej: Entrevista con el propietario, 12/11/2026"
    )

    class Meta:
        verbose_name = "Costo por concepto"
        verbose_name_plural = "Costos por concepto"

    @property
    def num_fuentes(self):
        return (1 if self.fuente_evidencia else 0) + (1 if self.fuente_nota.strip() else 0)

    @property
    def fuentes_completas(self):
        return self.num_fuentes >= 2

    def __str__(self):
        return f"{self.concepto}: {self.monto_anual}"


class FuenteDato(models.Model):
    """Una fuente que respalda un dato clave de la alternativa (inversión, ingreso, vida útil, TMAR)."""
    DATO_CHOICES = [
        ('INVERSION', 'Inversión inicial'),
        ('INGRESO', 'Ingreso / ahorro anual'),
        ('VIDA_UTIL', 'Vida útil'),
        ('TMAR', 'Tasa de interés (TMAR)'),
    ]
    alternativa = models.ForeignKey(AlternativaInversion, on_delete=models.CASCADE, related_name='fuentes_datos')
    dato = models.CharField(max_length=20, choices=DATO_CHOICES)
    fuente_evidencia = models.ForeignKey(
        EvidenciaDocumental, null=True, blank=True, on_delete=models.SET_NULL,
        verbose_name="Evidencia (archivo subido)"
    )
    fuente_nota = models.CharField(
        max_length=255, blank=True,
        verbose_name="Otra fuente",
        help_text="Ej: Entrevista con el propietario, 12/11/2026"
    )

    class Meta:
        verbose_name = "Fuente de dato clave"
        verbose_name_plural = "Fuentes de datos clave"

    def clean(self):
        super().clean()
        if not self.fuente_evidencia_id and not self.fuente_nota.strip():
            raise ValidationError("Elige una evidencia o escribe otra fuente.")

    def __str__(self):
        return f"{self.get_dato_display()}: {self.fuente_nota or self.fuente_evidencia}"