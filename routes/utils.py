from flask import jsonify
from datetime import datetime

def parse_date_range(request_data, required=True):
    if required:
        if not request_data or 'fecha_inicio' not in request_data or 'fecha_fin' not in request_data:
            return None, None, jsonify({"error": "Faltan parámetros 'fecha_inicio' o 'fecha_fin' en el cuerpo JSON"}), 400
    else: # Not required
        if not request_data: # No data at all
            return None, None, None, None
        # If data exists, but both dates are missing, it's okay
        if 'fecha_inicio' not in request_data and 'fecha_fin' not in request_data:
            return None, None, None, None
        # If one is provided, the other must also be provided
        if 'fecha_inicio' in request_data and 'fecha_fin' not in request_data:
             return None, None, jsonify({"error": "Si se provee 'fecha_inicio', también se debe proveer 'fecha_fin'"}), 400
        if 'fecha_fin' in request_data and 'fecha_inicio' not in request_data:
             return None, None, jsonify({"error": "Si se provee 'fecha_fin', también se debe proveer 'fecha_inicio'"}), 400

    fecha_inicio_str = request_data.get('fecha_inicio')
    fecha_fin_str = request_data.get('fecha_fin')

    # This case is for when required=False and both dates are explicitly None or empty strings in the JSON
    # If not required and both are effectively absent, return Nones without error.
    if not required and not fecha_inicio_str and not fecha_fin_str:
        return None, None, None, None

    # If required=True, fecha_inicio_str and fecha_fin_str must exist due to the check at the beginning.
    # If required=False, but they are provided, they must be valid.
    if not fecha_inicio_str or not fecha_fin_str:
        # This condition should ideally be caught by the initial checks if required=True,
        # or by the one-missing-other-must-be-present check if required=False.
        # However, as a safeguard for any edge cases or direct calls where request_data might be manipulated:
        return None, None, jsonify({"error": "Ambas fechas son requeridas si una es proporcionada, o si son requeridas por defecto."}), 400

    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        if fecha_inicio > fecha_fin:
            return None, None, jsonify({"error": "La fecha de inicio no puede ser posterior a la fecha de fin"}), 400
        return fecha_inicio, fecha_fin, None, None
    except ValueError:
        return None, None, jsonify({"error": "Formato de fecha inválido para fechas proporcionadas. Usar YYYY-MM-DD"}), 400

def find_potential_duplicate_paper_invoices(facturas_papel):
    """
    Identifies potential duplicate paper invoices based on NIF, numero_factura, and fecha_factura.
    """
    claves_vistas = {}
    ids_duplicados = set()
    duplicadas_list = []

    for f in facturas_papel:
        factura_id = f.get('id')
        nif = f.get('proveedor_nif')
        num = f.get('numero_factura')
        fecha_f_str = f.get('fecha_factura')

        # Skip if essential fields are missing for duplicate check
        if not factura_id or not nif or not num or not fecha_f_str:
            continue

        clave = (str(nif).strip().upper(), str(num).strip(), str(fecha_f_str).strip())

        if clave in claves_vistas:
            # This invoice is a duplicate of an already seen one
            ids_duplicados.add(factura_id)
            # Add the ID of the first invoice seen with this key
            ids_duplicados.add(claves_vistas[clave])
        else:
            claves_vistas[clave] = factura_id

    if ids_duplicados:
        # Create a list of all invoices that were marked as duplicates (either the first one or subsequent ones)
        # Group them by their duplicate key to present associated duplicates
        
        # First, gather all details for invoices that are part of any duplication
        invoices_involved_in_duplication = {}
        for f_original in facturas_papel:
            if f_original.get('id') in ids_duplicados:
                nif = f_original.get('proveedor_nif')
                num = f_original.get('numero_factura')
                fecha_f_str = f_original.get('fecha_factura')
                
                # Ensure key components are not None before processing
                if nif is None or num is None or fecha_f_str is None:
                    continue # Should not happen if it was processed above, but as a safeguard

                clave_actual = (str(nif).strip().upper(), str(num).strip(), str(fecha_f_str).strip())
                
                if clave_actual not in invoices_involved_in_duplication:
                    invoices_involved_in_duplication[clave_actual] = []
                
                invoices_involved_in_duplication[clave_actual].append({
                    "id": f_original.get('id'),
                    "numero_factura": num,
                    "proveedor_nif": nif,
                    "fecha_factura": fecha_f_str,
                    "fecha_registro_rcf": f_original.get('fecha_registro_rcf')
                })

        # Now, format the output list
        processed_ids_for_output = set()
        for clave, facturas_con_misma_clave in invoices_involved_in_duplication.items():
            if len(facturas_con_misma_clave) > 1: # Only groups with more than one invoice are duplicates
                ids_asociados_a_esta_clave = sorted([f_dup.get('id') for f_dup in facturas_con_misma_clave])
                for factura_info in facturas_con_misma_clave:
                    if factura_info['id'] not in processed_ids_for_output:
                        duplicadas_list.append({
                            **factura_info, # Unpack all invoice details
                            "ids_duplicados_asociados": ids_asociados_a_esta_clave
                        })
                        processed_ids_for_output.add(factura_info['id'])
        
        # Sort the final list for consistent output
        duplicadas_list = sorted(duplicadas_list, key=lambda x: (x['proveedor_nif'], x['numero_factura'], x['fecha_factura'], x['id']))
        
    return duplicadas_list
