# backend-app.py

from flask import Flask
from routes.main_routes import main_bp
from routes.audit_routes import audit_bp

app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(main_bp)
app.register_blueprint(audit_bp)

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('FLASK_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
