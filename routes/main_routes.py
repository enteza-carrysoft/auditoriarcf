# routes/main_routes.py

from flask import Blueprint, jsonify, request
from config import supabase
import traceback

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Ruta básica para verificar que la app funciona."""
    if supabase:
        return jsonify({"status": "OK", "message": "API Auditoría Facturas - Funcionando y conectada a Supabase."})
    else:
        return jsonify({"status": "ERROR", "message": "API Auditoría Facturas - Funcionando pero SIN conexión a Supabase."}), 503

@main_bp.route('/api/facturas', methods=['GET'])
def get_facturas():
    """
    Endpoint para obtener una lista de facturas.
    Se pueden agregar filtros mediante parámetros en la URL.
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
