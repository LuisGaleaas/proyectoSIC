  👥 Equipo de Desarrollo (UES-FMO)

Luis Manuel Galeas Rosales -> GR23030

Carlos Alejandro Barrientos Lapa -> BL23012

Juan Anderson Granados Alvarez -> GA22021

Empresa Caso de Estudio: 4Seasons (San Miguel, El Salvador)


📊 Sistema de Apoyo a la Decisión de Inversión — Caso Real: 4Seasons

Universidad de El Salvador — Facultad Multidisciplinaria Oriental (UES-FMO)

Departamento de Ingeniería y Arquitectura / Ciencias Económicas

Proyecto Integrador: Sistemas Contables (SIC) e Ingeniería Económica (Ciclo II-2026)

🎯 Descripción del Proyecto

Aplicación web desarrollada en Python + Django bajo el patrón arquitectónico MVT (Modelo - Vista - Template) que integra el registro contable y el sistema de costos de la empresa real 4Seasons (comercialización de prendas de vestir y accesorios) con técnicas de evaluación financiera de Ingeniería Económica.

El sistema permite comparar de forma automatizada, auditable y trazable dos estrategias logísticas en un horizonte de evaluación de 5 años (con una TMAR del 12.00% y tasa de ISR del 30.00% según la legislación salvadoreña):

Tercerización de Envíos con C807 Logistics (servicio recurrente sin inversión en activo fijo).

Adquisición de Motocicleta Propia 125cc (inversión en activo fijo con costos operativos, mantenimiento, seguros y valor de rescate).

🚀 Características Principales

Portada Ejecutiva (/): Presenta el contexto de la empresa 4Seasons, los parámetros fiscales y financieros base y los pilares metodológicos del sistema.

Panel Administrativo y Auditoría (/admin/): Módulo protegido donde se cargan los datos reales de la empresa, las justificaciones de selección, el desglose de proveedores/seguros y los archivos digitales de respaldo (cotizaciones, facturas, registros contables y entrevistas).

Tablero de Evaluación Económica (/dashboard/):

Indicadores Financieros Automatizados: Cálculo exacto de CAUE, VPN (FEDI con 30% ISR), TIR y Relación Beneficio/Costo (B/C).

Simulador de Sensibilidad en Tiempo Real: Permite modificar variables clave (Inversión, Ingreso/Ahorro, Costo Anual y Vida Útil) en vivo con validación contra valores negativos.

Diagrama de Flujo de Efectivo: Línea de tiempo visual que clasifica los flujos anuales en Salida, Neutro y Entrada.

Planificación de Depreciación: Comparativa automática entre el método de Línea Recta y Suma de los Dígitos de los Años (SDA) para activos propios.

Ficha de Trazabilidad Documental (Modal): Ventana emergente por alternativa que despliega el origen de cada cifra, proveedores cotizados y acceso directo a las evidencias adjuntas.

🛠️ Stack Tecnológico

Backend: Python 3.x, Django 5.x

Base de Datos: SQLite3 (db.sqlite3)

Frontend: HTML5, Bootstrap 5.3, JavaScript (ES6)

Control de Versiones: Git & GitHub (flujo colaborativo en rama main)
