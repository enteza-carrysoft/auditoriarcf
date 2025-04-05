# routes/audit/__init__.py

from flask import Blueprint

# Creamos el blueprint común para auditoría
audit_bp = Blueprint('audit', __name__)

# Importamos los endpoints de cada versión para registrarlos en el blueprint
from . import v1, v2, v3, v4
