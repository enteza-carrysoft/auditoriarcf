# routes/audit/v1.py

from flask import request, jsonify
from datetime import datetime
import traceback
import requests
from config import supabase
from . import audit_bp  # Importamos el blueprint definido en __init__.py

@audit_bp.route('/api/auditar/v1/papel', methods=['POST'])
def auditar_facturas_papel():
    """
    Ejecuta las pruebas de auditoría V.1 para facturas en papel,
    en un periodo determinado por fecha de registro en RCF.
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

        # Duplicidad
        claves_vistas = {}
        ids_duplicados = set()

        for f in facturas_papel:
            factura_id = f.get('id')
            nif = f.get('proveedor_nif')
            num = f.get('numero_factura')
            fecha_f_str = f.get('fecha_factura')
            if not factura_id or not nif or not num or not fecha_f_str:
                continue
            clave = (str(nif).strip().upper(), str(num).strip(), str(fecha_f_str).strip())
            if clave in claves_vistas:
                ids_duplicados.add(factura_id)
                ids_duplicados.add(claves_vistas[clave])
            else:
                claves_vistas[clave] = factura_id

        duplicadas_list = []
        if ids_duplicados:
            for f in facturas_papel:
                if f.get('id') in ids_duplicados:
                    nif = f.get('proveedor_nif')
                    num = f.get('numero_factura')
                    fecha_f_str = f.get('fecha_factura')
                    clave_actual = (str(nif).strip().upper(), str(num).strip(), str(fecha_f_str).strip())
                    ids_asociados = [f_inner.get('id') for f_inner in facturas_papel if
                                     (str(f_inner.get('proveedor_nif')).strip().upper(),
                                      str(f_inner.get('numero_factura')).strip(),
                                      str(f_inner.get('fecha_factura')).strip()) == clave_actual]
                    duplicadas_list.append({
                        "id": f.get('id'),
                        "numero_factura": num,
                        "proveedor_nif": nif,
                        "fecha_factura": fecha_f_str,
                        "fecha_registro_rcf": f.get('fecha_registro_rcf'),
                        "ids_duplicados_asociados": sorted(list(set(ids_asociados)))
                    })
            resultados["v1_4_duplicadas_potenciales"] = sorted(duplicadas_list, key=lambda x: (x['proveedor_nif'], x['numero_factura'], x['fecha_factura']))

        return jsonify(resultados), 200

    except requests.exceptions.RequestException as e:
        traceback.print_exc()
        return jsonify({"error": "Error de conexión externa durante la auditoría"}), 503
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor durante la auditoría V.1", "details": str(e)}), 500
