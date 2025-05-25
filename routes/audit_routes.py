# routes/audit_routes.py

from flask import Blueprint, request, jsonify
from config import supabase
from datetime import datetime
import traceback
import requests
from .utils import parse_date_range, find_potential_duplicate_paper_invoices # Import the new utility functions

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/api/auditar/v1/papel', methods=['POST'])
def auditar_facturas_papel():
    """
    Ejecuta las pruebas de auditoría V.1 para facturas en papel
    en un periodo determinado por fecha de registro en RCF.
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503

    try:
        data = request.get_json()
        # Use parse_date_range for date validation
        fecha_inicio, fecha_fin, error_response, error_code = parse_date_range(data)
        if error_response:
            return error_response, error_code
        
        # fecha_inicio_str and fecha_fin_str are still needed for Supabase queries
        fecha_inicio_str = data['fecha_inicio']
        fecha_fin_str = data['fecha_fin']

        query_facturas_papel = supabase.table('facturas')\
            .select('id, numero_factura, proveedor_nif, fecha_factura, fecha_presentacion_registro, fecha_registro_rcf')\
            .eq('es_electronica', False)\
            .gte('fecha_registro_rcf', fecha_inicio_str)\
            .lte('fecha_registro_rcf', fecha_fin_str)\
            .execute()

        if not hasattr(query_facturas_papel, 'data') or (hasattr(query_facturas_papel, 'error') and query_facturas_papel.error):
            error_details = str(query_facturas_papel.error) if hasattr(query_facturas_papel, 'error') else str(query_facturas_papel)
            return jsonify({"error": "Error al consultar facturas en papel", "details": error_details}), 500

        facturas_papel = query_facturas_papel.data
        total_facturas_papel = len(facturas_papel)

        resultados = {
            "periodo_analizado": {"inicio": fecha_inicio_str, "fin": fecha_fin_str},
            "total_facturas_papel_analizadas": total_facturas_papel,
            "v1_2_fuera_plazo_30_dias": [],
            "v1_2_sin_fecha_presentacion": [],
            "v1_2_sin_fecha_registro_rcf": [],
            "v1_4_duplicadas_potenciales": [],
            "requiere_verificacion_manual": {
                "v1_1_completitud": True,
                "v1_3_contenido": True
            },
            "errores_procesamiento_fechas": []
        }

        ids_procesados_plazo = set()
        facturas_sin_fecha_presentacion_ids = []
        facturas_sin_fecha_registro_ids = []

        for f in facturas_papel:
            factura_id = f.get('id')
            if not factura_id or factura_id in ids_procesados_plazo:
                continue
            ids_procesados_plazo.add(factura_id)

            f_presentacion_str = f.get('fecha_presentacion_registro')
            f_registro_str = f.get('fecha_registro_rcf')

            if not f_presentacion_str:
                facturas_sin_fecha_presentacion_ids.append(factura_id)
                continue

            if not f_registro_str:
                facturas_sin_fecha_registro_ids.append(factura_id)
                continue

            try:
                f_presentacion = datetime.fromisoformat(f_presentacion_str.replace('Z', '+00:00')).date()
                f_registro = datetime.fromisoformat(f_registro_str.replace('Z', '+00:00')).date()
                dias_diferencia = (f_registro - f_presentacion).days
                if dias_diferencia > 30:
                    resultados["v1_2_fuera_plazo_30_dias"].append({
                        "id": factura_id,
                        "numero_factura": f.get('numero_factura'),
                        "proveedor_nif": f.get('proveedor_nif'),
                        "fecha_presentacion": f_presentacion_str,
                        "fecha_registro_rcf": f_registro_str,
                        "dias_transcurridos": dias_diferencia
                    })
            except Exception as e:
                resultados["errores_procesamiento_fechas"].append({
                    "id": factura_id,
                    "error": str(e),
                    "fecha_presentacion": f_presentacion_str,
                    "fecha_registro_rcf": f_registro_str
                })

        resultados["v1_2_sin_fecha_presentacion"] = facturas_sin_fecha_presentacion_ids
        resultados["v1_2_sin_fecha_registro_rcf"] = facturas_sin_fecha_registro_ids

        # Use the new utility function for duplicate detection
        resultados["v1_4_duplicadas_potenciales"] = find_potential_duplicate_paper_invoices(facturas_papel)

        return jsonify(resultados), 200

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return jsonify({"error": "Error de conexión externa durante la auditoría"}), 503
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor durante la auditoría V.1", "details": str(e)}), 500


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
        # Use parse_date_range for date validation
        fecha_inicio, fecha_fin, error_response, error_code = parse_date_range(data)
        if error_response:
            return error_response, error_code

        # fecha_inicio_str and fecha_fin_str are still needed for Supabase queries
        fecha_inicio_str = data['fecha_inicio']
        fecha_fin_str = data['fecha_fin']
        
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


@audit_bp.route('/api/auditar/v3/validaciones', methods=['POST'])
def auditar_validaciones():
    """
    Ejecuta las pruebas de auditoría V.3: Validaciones del contenido de las facturas.
    Revisa que las facturas cumplan las reglas de validación.
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503
    try:
        data = request.get_json()
        # Use parse_date_range for optional date validation
        fecha_inicio, fecha_fin, error_response, error_code = parse_date_range(data, required=False)
        if error_response:
            return error_response, error_code

        # Get string versions if needed for Supabase, can be None
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')

        query = supabase.table('facturas').select('*').eq('es_electronica', True)
        if fecha_inicio_str: # Check if the string date is available
            query = query.gte('fecha_factura', fecha_inicio_str)
        if fecha_fin_str: # Check if the string date is available
            query = query.lte('fecha_factura', fecha_fin_str)
        response = query.execute()
        if not hasattr(response, 'data') or (hasattr(response, 'error') and response.error):
            error_details = str(response.error) if hasattr(response, 'error') else str(response)
            return jsonify({"error": "Error al consultar facturas para validaciones", "details": error_details}), 500
        facturas = response.data
        resultados_validaciones = []
        for f in facturas:
            errores = []
            try:
                total_importe_bruto = float(f.get('total_importe_bruto', 0))
                total_descuentos = float(f.get('total_descuentos', 0))
                total_cargos = float(f.get('total_cargos', 0))
                total_importe_bruto_antes_impuestos = float(f.get('total_importe_bruto_antes_impuestos', 0))
                total_impuestos_repercutidos = float(f.get('total_impuestos_repercutidos', 0))
                total_impuestos_retenidos = float(f.get('total_impuestos_retenidos', 0))
                total_factura = float(f.get('total_factura', 0))
                if round(total_importe_bruto - total_descuentos + total_cargos, 2) != round(total_importe_bruto_antes_impuestos, 2):
                    errores.append("Error en cálculo de total_importe_bruto_antes_impuestos")
                if round(total_importe_bruto_antes_impuestos + total_impuestos_repercutidos - total_impuestos_retenidos, 2) != round(total_factura, 2):
                    errores.append("Error en cálculo de total_factura")
            except Exception as e:
                errores.append(f"Error al procesar datos numéricos: {str(e)}")
            if errores:
                resultados_validaciones.append({
                    "id": f.get('id'),
                    "numero_factura": f.get('numero_factura'),
                    "errores": errores
                })
        resultados = {
            "total_facturas_validadas": len(facturas),
            "facturas_con_errores": resultados_validaciones
        }
        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": "Error interno en auditoría V.3", "details": str(e)}), 500


@audit_bp.route('/api/auditar/v4/tramitacion', methods=['POST'])
def auditar_tramitacion():
    """
    Ejecuta pruebas de auditoría V.4: Tramitación de facturas.
    Verifica que el campo 'estado' de cada factura esté en un conjunto de valores válidos.
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503
    try:
        data = request.get_json()
        # Use parse_date_range for optional date validation
        fecha_inicio, fecha_fin, error_response, error_code = parse_date_range(data, required=False)
        if error_response:
            return error_response, error_code

        # Get string versions if needed for Supabase, can be None
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        
        query = supabase.table('facturas')\
            .select('id, numero_factura, proveedor_nif, estado, fecha_factura')\
            .eq('es_electronica', True)
        if fecha_inicio_str: # Check if the string date is available
            query = query.gte('fecha_factura', fecha_inicio_str)
        if fecha_fin_str: # Check if the string date is available
            query = query.lte('fecha_factura', fecha_fin_str)
        response = query.execute()
        if not hasattr(response, 'data') or (hasattr(response, 'error') and response.error):
            error_details = str(response.error) if hasattr(response, 'error') else str(response)
            return jsonify({"error": "Error al consultar facturas para tramitación", "details": error_details}), 500
        facturas = response.data
        estados_incorrectos = []
        estados_validos = ["REGISTRADA", "REGISTRADA EN RCF", "VERIFICADA EN RCF", "RECIBIDA EN DESTINO",
                           "CONFORMADA", "CONTABILIZADA", "PAGADA", "ANULADA", "RECHAZADA"]
        for f in facturas:
            estado = f.get('estado', '')
            if estado not in estados_validos:
                estados_incorrectos.append({
                    "id": f.get('id'),
                    "numero_factura": f.get('numero_factura'),
                    "estado": estado
                })
        resultados = {
            "total_facturas_tramitacion": len(facturas),
            "facturas_con_estado_incorrecto": estados_incorrectos
        }
        return jsonify(resultados), 200

    except Exception as e:
        return jsonify({"error": "Error interno en auditoría V.4", "details": str(e)}), 500
