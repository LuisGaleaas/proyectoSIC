from django.shortcuts import render
from .models import AlternativaInversion, Empresa
from .calculos import (
    calcular_caue,
    depreciacion_linea_recta,
    depreciacion_suma_digitos,
    flujo_despues_de_impuestos,
    calcular_vpn,
    calcular_tir,
    calcular_beneficio_costo
)

def dashboard(request):
    alternativas = AlternativaInversion.objects.all()
    empresa = Empresa.objects.first()
    tasa_isr = float(empresa.tasa_impuesto) if empresa else 30.0

    resultados = []
    mejor_opcion = None
    menor_caue = float('inf')

    for alt in alternativas:
        # 1. Indicador CAUE
        caue = calcular_caue(
            alt.inversion_inicial,
            alt.costo_operativo_anual,
            alt.valor_salvamento,
            alt.tasa_tmar,
            alt.vida_util_anios
        )

        # 2. Dos métodos de depreciación (Línea Recta y Suma de Dígitos)
        deprec_lr = depreciacion_linea_recta(
            alt.inversion_inicial, 
            alt.valor_salvamento, 
            alt.vida_util_anios
        ) if alt.inversion_inicial > 0 else []
        
        deprec_sda = depreciacion_suma_digitos(
            alt.inversion_inicial, 
            alt.valor_salvamento, 
            alt.vida_util_anios
        ) if alt.inversion_inicial > 0 else []

        # 3. Flujo de Efectivo Después de Impuestos (FEDI) para VPN y TIR
        flujos_fedi = flujo_despues_de_impuestos(
            alt.ingreso_anual,
            alt.costo_operativo_anual,
            alt.inversion_inicial,
            alt.valor_salvamento,
            alt.vida_util_anios,
            tasa_impuesto=tasa_isr
        )

        # 4. Indicadores restantes (VPN, TIR, B/C)
        vpn = calcular_vpn(flujos_fedi, alt.tasa_tmar)
        tir = calcular_tir(flujos_fedi)
        bc = calcular_beneficio_costo(
            alt.inversion_inicial,
            alt.ingreso_anual,
            alt.costo_operativo_anual,
            alt.valor_salvamento,
            alt.tasa_tmar,
            alt.vida_util_anios
        )

        # 5. Flujo neto para la línea de tiempo visual (Ingresos - Costos + Rescate)
        flujo_caja = []
        for anio in range(alt.vida_util_anios + 1):
            if anio == 0:
                monto = -alt.inversion_inicial
            elif anio == alt.vida_util_anios:
                monto = alt.ingreso_anual - alt.costo_operativo_anual + alt.valor_salvamento
            else:
                monto = alt.ingreso_anual - alt.costo_operativo_anual
            
            flujo_caja.append({'anio': anio, 'monto': monto})

        resultados.append({
            'objeto': alt,
            'caue': caue,
            'vpn': vpn,
            'tir': tir if tir is not None else "N/A",
            'bc': bc,
            'depreciacion': deprec_lr,
            'depreciacion_sda': deprec_sda,
            'flujo_caja': flujo_caja,
            'evidencias': alt.evidencias.all()
        })

        # Selección de la alternativa más viable (menor CAUE)
        if caue > 0 and caue < menor_caue:
            menor_caue = caue
            mejor_opcion = alt.nombre

    return render(request, 'evaluacion/dashboard.html', {
        'empresa': empresa,
        'resultados': resultados,
        'mejor_opcion': mejor_opcion
    })