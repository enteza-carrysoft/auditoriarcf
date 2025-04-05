# -*- coding: utf-8 -*-
# backend-app.py

import os
import traceback  # Para imprimir errores detallados
from datetime import datetime, timedelta, date  # Asegúrate de importar date también
from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import requests  # Aunque no lo usemos directamente aquí, puede ser útil

# --- Carga de Variables de Entorno ---
load_dotenv()

# --- Configuración Inicial de Flask ---
app = Flask(__name__)

# --- Configuración de Supabase ---
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_SERVICE_KEY")  # Usar SERVICE KEY en el backend

if not supabase_url or not supabase_key:
    print("ERROR CRÍTICO: Las variables de entorno SUPABASE_URL y SUPABASE_SERVICE_KEY deben estar definidas.")
    supabase: Client = None
else:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("Conexión con Supabase establecida correctamente.")
    except Exception as e:
        print(f"Error CRÍTICO al inicializar el cliente de Supabase: {e}")
        supabase = None

# --- Funciones Auxiliares ---
def calcular_diferencia_dias_habiles(fecha_inicio, fecha_fin):
    """Calcula la diferencia en días hábiles (L-V) entre dos fechas."""
    if not fecha_inicio or not fecha_fin:
        return None
    if isinstance(fecha_inicio, datetime):
        fecha_inicio = fecha_inicio.date()
    if isinstance(fecha_fin, datetime):
        fecha_fin = fecha_fin.date()
    dias_habiles_count = 0
    current_date = fecha_inicio
    while current_date <= fecha_fin:
        if current_date.weekday() < 5:  # 0 a 4 -> Lunes a Viernes
            dias_habiles_count += 1
        current_date += timedelta(days=1)
    return dias_habiles_count

# --- Rutas Principales de la API ---
@app.route('/')
def home():
    """Ruta básica para verificar que la app funciona."""
    if supabase:
        return jsonify({"status": "OK", "message": "API Auditoría Facturas - Funcionando y conectada a Supabase."})
    else:
        return jsonify({"status": "ERROR", "message": "API Auditoría Facturas - Funcionando pero SIN conexión a Supabase."}), 503

@app.route('/api/facturas', methods=['GET'])
def get_facturas():
    """
    Endpoint para obtener una lista de facturas.
    TODO: Implementar filtros por fecha y otros criterios pasados como query params.
    """
    if not supabase:
        return jsonify({"error": "Servicio no disponible: Sin conexión con la base de datos"}), 503

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        offset = (page - 1) * per_page

        response = supabase.table('facturas')\
            .select('*')\
            .order('fecha_factura', desc=True)\
            .range(offset, offset + per_page - 1)\
            .execute()

        if response.data:
            return jsonify({
                "data": response.data,
                "page": page,
                "per_page": per_page,
            }), 200
        else:
            if hasattr(response, 'error') and response.error:
                return jsonify({"error": "Error al obtener facturas", "details": str(response.error)}), 500
            return jsonify({"data": [], "message": "No se encontraron facturas"}), 200

    except Exception as e:
        print(f"Error en /api/facturas: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500

# --- Rutas de Auditoría ---

# V.1 Auditoría de facturas en papel (ya existente)
@app.route('/api/auditar/v1/papel', methods=['POST'])
def auditar_facturas_papel():
    """
    Ejecuta las pruebas de auditoría V.1 (Guía IGAE) para facturas en papel
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

        print(f"Iniciando Auditoría V.1 (Papel) para el periodo: {fecha_inicio_str} a {fecha_fin_str}")

        query_facturas_papel = supabase.table('facturas')\
            .select('id, numero_factura, proveedor_nif, fecha_factura, fecha_presentacion_registro, fecha_registro_rcf')\
            .eq('es_electronica', False)\
            .gte('fecha_registro_rcf', fecha_inicio_str)\
            .lte('fecha_registro_rcf', fecha_fin_str)\
            .execute()

        if not hasattr(query_facturas_papel, 'data') or (hasattr(query_facturas_papel, 'error') and query_facturas_papel.error):
             error_details = str(query_facturas_papel.error) if hasattr(query_facturas_papel, 'error') else str(query_facturas_papel)
             print(f"Error al consultar facturas en papel: {error_details}")
             return jsonify({"error": "Error al consultar facturas en papel", "details": error_details}), 500

        facturas_papel = query_facturas_papel.data
        total_facturas_papel = len(facturas_papel)
        print(f"Encontradas {total_facturas_papel} facturas en papel.")

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

        # Prueba V.1.2: Anotación en plazo (30 días naturales)
        print("Ejecutando prueba V.1.2: Anotación en plazo...")
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
            except (ValueError, TypeError) as e:
                print(f"Error procesando fechas para factura ID {factura_id}: {e}")
                resultados["errores_procesamiento_fechas"].append({
                     "id": factura_id,
                     "error": str(e),
                     "fecha_presentacion": f_presentacion_str,
                     "fecha_registro_rcf": f_registro_str
                 })

        resultados["v1_2_sin_fecha_presentacion"] = facturas_sin_fecha_presentacion_ids
        resultados["v1_2_sin_fecha_registro_rcf"] = facturas_sin_fecha_registro_ids
        print("Prueba V.1.2 completada.")

        # Prueba V.1.4: Duplicidad
        print("Ejecutando prueba V.1.4: Duplicidad...")
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
                     # Buscar todas las facturas que compartan esta clave
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

        print("Prueba V.1.4 completada.")
        print("Recordatorio: Las pruebas V.1.1 (Completitud) y V.1.3 (Contenido) requieren verificación manual.")

        return jsonify(resultados), 200

    except requests.exceptions.RequestException as e:
         print(f"Error de conexión en Auditoría V.1: {e}")
         traceback.print_exc()
         return jsonify({"error": "Error de conexión externa durante la auditoría"}), 503
    except Exception as e:
        print(f"Error INESPERADO en Auditoría V.1: {e}")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor durante la auditoría V.1", "details": str(e)}), 500

# V.2 Auditoría de anotación electrónica
@app.route('/api/auditar/v2/anotacion', methods=['POST'])
def auditar_anotacion_electronica():
    """
    Ejecuta las pruebas de auditoría V.2: Anotación de facturas electrónicas en el RCF.
    Calcula los tiempos de anotación (diferencia entre fecha_presentacion_registro y fecha_registro_rcf)
    y genera estadísticas.
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

# V.3 Validaciones del contenido de las facturas
@app.route('/api/auditar/v3/validaciones', methods=['POST'])
def auditar_validaciones():
    """
    Ejecuta las pruebas de auditoría V.3: Validaciones del contenido de las facturas.
    Revisa que las facturas cumplan con las reglas de validación (ejemplo: redondeo, sumas correctas, etc.).
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

# V.4 Auditoría de la tramitación de facturas
@app.route('/api/auditar/v4/tramitacion', methods=['POST'])
def auditar_tramitacion():
    """
    Ejecuta pruebas de auditoría V.4: Tramitación de facturas.
    Verifica los cambios de estado de las facturas según lo esperado.
    Se espera que cada factura tenga un campo 'estado' que evoluciona según las fases.
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

# --- Ejecución de la Aplicación ---
if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
