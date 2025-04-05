# routes/audit/v3.py

from flask import request, jsonify
from config import supabase
import traceback
from . import audit_bp

@audit_bp.route('/api/auditar/v3/validaciones', methods=['POST'])
def auditar_validaciones():
    """
    Ejecuta las pruebas de auditoría V.3: Validaciones del contenido de las facturas.
    Revisa que las facturas cumplan con las reglas de validación (ej. redondeo, sumas correctas, etc.).
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503
    try:
        data = request.get_json()
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        query = supabase.table('facturas').select('*').eq('es_electronica', True)
        if fecha_inicio_str:
            query = query.gte('fecha_factura', fecha_inicio_str)
        if fecha_fin_str:
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
