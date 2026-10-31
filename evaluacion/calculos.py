

def depreciacion_linea_recta(costo, valor_salvamento, vida_util):
    """
    Método 1: Depreciación en Línea Recta (LR)
    Cuota constante: D = (Costo - Salvamento) / n
    """
    try:
        costo = float(costo)
        salvamento = float(valor_salvamento)
        n = int(vida_util)

        if n <= 0 or costo <= 0:
            return []

        base = max(costo - salvamento, 0.0)
        cuota = round(base / n, 2)
        tabla = []
        saldo = costo
        dep_acumulada = 0.0

        for anio in range(1, n + 1):
            dep_acumulada = round(dep_acumulada + cuota, 2)
            saldo = round(costo - dep_acumulada, 2)
            tabla.append({
                'anio': anio,
                'cuota': cuota,
                'acumulada': dep_acumulada,
                'saldo': max(saldo, salvamento)
            })
        return tabla
    except (ValueError, ZeroDivisionError):
        return []


def depreciacion_suma_digitos(costo, valor_salvamento, vida_util):
    """
    Método 2: Depreciación Acelerada por Suma de los Dígitos de los Años (SDA)
    S = n(n + 1) / 2
    Cuota_t = (Costo - Salvamento) * ((n - t + 1) / S)
    """
    try:
        costo = float(costo)
        salvamento = float(valor_salvamento)
        n = int(vida_util)

        if n <= 0 or costo <= 0:
            return []

        base = max(costo - salvamento, 0.0)
        suma_digitos = (n * (n + 1)) / 2.0
        tabla = []
        saldo = costo
        dep_acumulada = 0.0

        for anio in range(1, n + 1):
            factor = (n - anio + 1) / suma_digitos
            cuota = round(base * factor, 2)
            dep_acumulada = round(dep_acumulada + cuota, 2)
            saldo = round(costo - dep_acumulada, 2)
            tabla.append({
                'anio': anio,
                'cuota': cuota,
                'acumulada': dep_acumulada,
                'saldo': max(saldo, salvamento)
            })
        return tabla
    except (ValueError, ZeroDivisionError):
        return []


def flujo_despues_de_impuestos(ingreso_anual, costo_anual, inversion_inicial, salvamento, vida_util, tasa_impuesto=30.0):
    """
    Construye los Flujos Netos de Efectivo Después de Impuestos (FEDI) año con año.
    Utilidad Antes de Impuestos = Ingresos - Costos - Depreciación
    Impuesto = UAI * t
    FEDI = Ingresos - Costos - Impuesto
    Año 0: - Inversión Inicial
    Año n: Incorpora el Valor de Salvamento
    """
    try:
        ingreso = float(ingreso_anual)
        costo = float(costo_anual)
        p = float(inversion_inicial)
        f = float(salvamento)
        n = int(vida_util)
        t = float(tasa_impuesto) / 100.0

        flujos = [-p]
        tabla_dep = depreciacion_linea_recta(p, f, n)

        for anio in range(1, n + 1):
            dep = tabla_dep[anio - 1]['cuota'] if tabla_dep else 0.0
            uai = ingreso - costo - dep
            impuesto = max(0.0, uai * t)
            fedi = (ingreso - costo) - impuesto

            # Al final de la vida útil se recupera el valor de rescate
            if anio == n:
                fedi += f

            flujos.append(round(fedi, 2))
        return flujos
    except Exception:
        return []


def calcular_caue(inversion_inicial, costo_anual, valor_salvamento, tasa_interes, vida_util):
    """
    Cálculo del Costo Anual Uniforme Equivalente (CAUE) blindado contra OverflowError.
    CAUE = P*(A/P, i, n) + A - F*(A/F, i, n)
    """
    try:
        p = float(inversion_inicial)
        a = float(costo_anual)
        f = float(valor_salvamento)
        i = float(tasa_interes) / 100.0
        n = int(vida_util)

        # Validación de límites para evitar colapso numérico
        if n < 1 or n > 50 or i < 0 or i > 1.0:
            return 0.0

        if i == 0:
            return round((p - f) / n + a, 2)

        # Factor (1 + i)^n
        potencia = (1.0 + i) ** n
        denominador = potencia - 1.0

        if denominador == 0:
            return round(a, 2)

        factor_a_p = (i * potencia) / denominador
        factor_a_f = i / denominador
        caue = (p * factor_a_p) + a - (f * factor_a_f)
        return round(caue, 2)
    except (OverflowError, ZeroDivisionError, ValueError):
        return 0.0


def calcular_vpn(flujos, tasa_interes):
    """
    Valor Presente Neto (VPN):
    VPN = Sumatoria [ FEDI_t / (1 + i)^t ]
    """
    try:
        i = float(tasa_interes) / 100.0
        if i <= -1.0 or not flujos:
            return 0.0

        vpn = 0.0
        for t, fedi in enumerate(flujos):
            vpn += float(fedi) / ((1.0 + i) ** t)
        return round(vpn, 2)
    except (OverflowError, ZeroDivisionError, ValueError):
        return 0.0


def calcular_tir(flujos, precision=0.0001, max_iter=1000):
    """
    Tasa Interna de Rendimiento (TIR):
    Tasa i que hace que el VPN(i) = 0.
    Calculada numéricamente por aproximación de bisección.
    """
    try:
        if not flujos or len(flujos) < 2:
            return None

        # Si no hay desembolso inicial negativo, la TIR no aplica
        if flujos[0] >= 0:
            return None

        bajo = -0.999
        alto = 5.0  # Límite superior del 500%

        def evaluar_vpn(tasa):
            return sum(float(cf) / ((1.0 + tasa) ** t) for t, cf in enumerate(flujos))

        vpn_bajo = evaluar_vpn(bajo)
        vpn_alto = evaluar_vpn(alto)

        # No hay cambio de signo
        if vpn_bajo * vpn_alto > 0:
            return None

        for _ in range(max_iter):
            medio = (bajo + alto) / 2.0
            vpn_medio = evaluar_vpn(medio)

            if abs(vpn_medio) < precision or (alto - bajo) / 2.0 < precision:
                return round(medio * 100.0, 2)

            if vpn_bajo * vpn_medio < 0:
                alto = medio
            else:
                bajo = medio
                vpn_bajo = vpn_medio

        return round(medio * 100.0, 2)
    except Exception:
        return None


def calcular_beneficio_costo(inversion_inicial, ingresos_anuales, costos_anuales, salvamento, tasa_interes, vida_util):
    """
    Relación Beneficio / Costo (B/C):
    B/C = VP(Beneficios) / VP(Costos e Inversión)
    """
    try:
        p = float(inversion_inicial)
        b = float(ingresos_anuales)
        c = float(costos_anuales)
        f = float(salvamento)
        i = float(tasa_interes) / 100.0
        n = int(vida_util)

        if n < 1 or i <= 0 or (p == 0 and c == 0):
            return 0.0

        # Factor (P/A, i, n) y Factor (P/F, i, n)
        potencia = (1.0 + i) ** n
        p_a = (potencia - 1.0) / (i * potencia)
        p_f = 1.0 / potencia

        vp_beneficios = (b * p_a) + (f * p_f)
        vp_costos = p + (c * p_a)

        if vp_costos == 0:
            return 0.0

        return round(vp_beneficios / vp_costos, 2)
    except (OverflowError, ZeroDivisionError, ValueError):
        return 0.0