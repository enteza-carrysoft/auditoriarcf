# routes/audit/v4.py

from flask import request, jsonify
from config import supabase
import traceback
from . import audit_bp

@audit_bp.route('/api/auditar/v4/tramitacion', methods=['POST'])
def auditar_tramitacion():
    """
    Ejecuta pruebas de auditoría V.4: Tramitación de facturas.
    Verifica que el campo 'estado' de cada factura esté dentro de los valores válidos.
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503
    try:
        data = request.get_json()
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        query = supabase.table('facturas')\
            .select('id, numero_factura, proveedor_nif, estado, fecha_factura')\
            .eq('es_electronica', True)
        if fecha_inicio_str:
            query = query.gte('fecha_factura', fecha_inicio_str)
        if fecha_fin_str:
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
