# utils.py

from datetime import datetime, timedelta

def calcular_diferencia_dias_habiles(fecha_inicio, fecha_fin):
    """
    Calcula la diferencia en días hábiles (Lunes a Viernes) entre dos fechas.
    """
    if not fecha_inicio or not fecha_fin:
        return None
    # Asegurarse que ambas fechas son objetos date
    if isinstance(fecha_inicio, datetime):
        fecha_inicio = fecha_inicio.date()
    if isinstance(fecha_fin, datetime):
        fecha_fin = fecha_fin.date()

    dias_habiles = 0
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        if current_date.weekday() < 5:  # 0=Lunes, 4=Viernes
            dias_habiles += 1
        current_date += timedelta(days=1)
    return dias_habiles
