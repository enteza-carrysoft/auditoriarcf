# routes/audit/v2.py

from flask import request, jsonify
from datetime import datetime
import traceback
from config import supabase
from . import audit_bp

@audit_bp.route('/api/auditar/v2/anotacion', methods=['POST'])
def auditar_anotacion_electronica():
    """
    Ejecuta las pruebas de auditoría V.2: Anotación de facturas electrónicas en el RCF.
    Calcula los tiempos de anotación y genera estadísticas.
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503
    try:
        data = request.get_json()
        if not data or 'fecha_inicio' not in data or 'fecha_fin' not in data:
            return jsonify({"error": "Faltan parámetros 'fecha_inicio' o 'fecha_fin' en el cuerpo JSON"}), 400
        fecha_inicio_str = data['fecha_inicio']
        fecha_fin_str = data['fecha_fin']
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            if fecha_inicio > fecha_fin:
                return jsonify({"error": "La fecha de inicio no puede ser posterior a la fecha de fin"}), 400
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usar YYYY-MM-DD"}), 400

        query_facturas = supabase.table('facturas')\
            .select('id, numero_factura, proveedor_nif, fecha_factura, fecha_presentacion_registro, fecha_registro_rcf')\
            .eq('es_electronica', True)\
            .gte('fecha_registro_rcf', fecha_inicio_str)\
            .lte('fecha_registro_rcf', fecha_fin_str)\
            .execute()
        if not hasattr(query_facturas, 'data') or (hasattr(query_facturas, 'error') and query_facturas.error):
            error_details = str(query_facturas.error) if hasattr(query_facturas, 'error') else str(query_facturas)
            return jsonify({"error": "Error al consultar facturas electrónicas", "details": error_details}), 500
        facturas = query_facturas.data
        total_facturas = len(facturas)
        tiempos = []
        facturas_sin_fechas = []

        for f in facturas:
            f_presentacion = f.get('fecha_presentacion_registro')
            f_registro = f.get('fecha_registro_rcf')
            if not f_presentacion or not f_registro:
                facturas_sin_fechas.append(f.get('id'))
                continue
            try:
                dt_presentacion = datetime.fromisoformat(f_presentacion.replace('Z', '+00:00'))
                dt_registro = datetime.fromisoformat(f_registro.replace('Z', '+00:00'))
                diferencia_minutos = (dt_registro - dt_presentacion).total_seconds() / 60
                tiempos.append(diferencia_minutos)
            except Exception as e:
                facturas_sin_fechas.append(f.get('id'))
        if tiempos:
            promedio = sum(tiempos) / len(tiempos)
            minimo = min(tiempos)
            maximo = max(tiempos)
        else:
            promedio = minimo = maximo = None
        resultados = {
            "periodo_analizado": {"inicio": fecha_inicio_str, "fin": fecha_fin_str},
            "total_facturas_electronicas_analizadas": total_facturas,
            "tiempos_anotacion": {
                "promedio_minutos": promedio,
                "minimo_minutos": minimo,
                "maximo_minutos": maximo,
                "detalle": tiempos,
            },
            "facturas_sin_fechas": facturas_sin_fechas
        }
        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor en auditoría V.2", "details": str(e)}), 500
