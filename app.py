# app.py
import os
import secrets
from datetime import timedelta
from functools import wraps
from flask import Flask, session, redirect, url_for, render_template
from flask_socketio import SocketIO, send, emit

# --- App Initialization ---
app = Flask(__name__, template_folder='templates', static_folder='static')

# --- Configurations ---
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production (HTTPS)
app.config['SESSION_COOKIE_HTTPONLY'] = True

# --- Add SocketIO ---
socketio = SocketIO(app, cors_allowed_origins="*")  # enable CORS for frontend apps

# --- Login Required Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Import and Register Blueprints ---
from api.auth import auth_bp
from api.customers import customers_bp
from api.enquiries import enquiries_bp
from api.orders import orders_bp
from api.invoices import invoices_bp
from api.deleted import deleted_bp

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
    return render_template('index.html', username=session.get('username'))

# --- Socket Handlers ---
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('server_message', {'data': 'Welcome, client!'})

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

@socketio.on('chat_message')
def handle_chat_message(msg):
    print(f"Received: {msg}")
    # Broadcast to all clients
    emit('chat_message', {'data': msg}, broadcast=True)

# --- Run the App ---
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # IMPORTANT: use socketio.run instead of app.run
    socketio.run(app, host="0.0.0.0", port=port, debug=True)
