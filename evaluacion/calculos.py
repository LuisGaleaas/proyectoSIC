def depreciacion_linea_recta(costo, valor_salvamento, vida_util):
    costo = float(costo)
    valor_salvamento = float(valor_salvamento)
    base = costo - valor_salvamento
    cuota = base / vida_util
    tabla = []
    saldo = costo
    for anio in range(1, vida_util + 1):
        saldo -= cuota
        tabla.append({'anio': anio, 'cuota': round(cuota, 2), 'saldo': round(saldo, 2)})
    return tabla

def calcular_caue(inversion_inicial, costo_anual, valor_salvamento, tasa_interes, vida_util):
    P = float(inversion_inicial)
    A = float(costo_anual)
    F = float(valor_salvamento)
    i = float(tasa_interes) / 100.0
    n = int(vida_util)

    if i == 0:
        return round((P - F) / n + A, 2)

    factor_a_p = (i * ((1 + i) ** n)) / (((1 + i) ** n) - 1)
    factor_a_f = i / (((1 + i) ** n) - 1)
    caue = (P * factor_a_p) + A - (F * factor_a_f)
    return round(caue, 2)