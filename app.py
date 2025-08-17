# app.py
from flask import Flask, session, redirect, url_for, render_template
from functools import wraps
import secrets
from datetime import timedelta

# --- App Initialization ---
# Create the Flask app instance first.
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Configurations ---
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
# IMPORTANT: Set to False for local development over HTTP. Change back to True for production (HTTPS).
app.config['SESSION_COOKIE_SECURE'] = False 
app.config['SESSION_COOKIE_HTTPONLY'] = True

# --- Login Required Decorator ---
# This decorator needs to be defined before the blueprints are imported,
# as they will import it from this file.
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Import and Register Blueprints ---
# Import blueprints *after* the app and decorator are defined to avoid circular import errors.
from api.auth import auth_bp
from api.customers import customers_bp
from api.enquiries import enquiries_bp
from api.orders import orders_bp
from api.invoices import invoices_bp
from api.deleted import deleted_bp 

# It's more conventional for login/signup pages not to have a '/auth' prefix
app.register_blueprint(auth_bp) 
app.register_blueprint(customers_bp, url_prefix='/customers')
app.register_blueprint(enquiries_bp, url_prefix='/enquiries')
app.register_blueprint(orders_bp, url_prefix='/orders')
app.register_blueprint(invoices_bp, url_prefix='/invoices')
app.register_blueprint(deleted_bp)

# --- Main Route ---
@app.route('/')
@login_required
def index():
    # Pass the username to the template for display
    return render_template('index.html', username=session.get('username'))

# --- Run the App ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render sets $PORT automatically
    app.run(host="0.0.0.0", port=port)
