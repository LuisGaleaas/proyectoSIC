from django.shortcuts import render
from .models import AlternativaInversion
from .calculos import calcular_caue, depreciacion_linea_recta

def dashboard(request):
    alternativas = AlternativaInversion.objects.all()
    resultados = []
    mejor_opcion = None
    menor_caue = float('inf')

    for alt in alternativas:
        caue = calcular_caue(
            alt.inversion_inicial,
            alt.costo_operativo_anual,
            alt.valor_salvamento,
            alt.tasa_tmar,
            alt.vida_util_anios
        )
        deprec = depreciacion_linea_recta(alt.inversion_inicial, alt.valor_salvamento, alt.vida_util_anios) if alt.inversion_inicial > 0 else []

        item = {
            'objeto': alt,
            'caue': caue,
            'depreciacion': deprec,
            'evidencias': alt.evidencias.all()
        }
        resultados.append(item)

        # La alternativa más viable en costos es la que tenga menor CAUE
        if caue < menor_caue:
            menor_caue = caue
            mejor_opcion = alt.nombre

    return render(request, 'evaluacion/dashboard.html', {
        'resultados': resultados,
        'mejor_opcion': mejor_opcion
    })