# server.py (versión para despliegue en la nube)

import os
import smtplib
import ssl
from email.message import EmailMessage
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Inicializar la aplicación Flask
app = Flask(__name__, static_folder='.')
CORS(app)

# --- LEER LOS SECRETOS DESDE LAS VARIABLES DE ENTORNO ---
# Render (o cualquier servicio en la nube) nos proporcionará estos valores de forma segura.
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_PASSWORD = os.environ.get('SENDER_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

# --- RUTAS DE LA APLICACIÓN ---

# 1. Ruta para servir la página web (index.html)
@app.route('/')
def serve_index():
    # send_from_directory busca el archivo en la carpeta raíz del proyecto.
    return send_from_directory('.', 'index.html')

# 2. Ruta para manejar el envío del formulario (la que ya teníamos)
@app.route('/submit', methods=['POST'])
def handle_submission():
    # Comprobar si las credenciales están configuradas en el servidor
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
        return jsonify({"error": "La configuración del servidor de correo está incompleta."}), 500

    data = request.get_json()
    
    fuerza_normal = data.get('fuerza_normal', 'No respondido')
    fuerza_friccion = data.get('fuerza_friccion', 'No respondido')
    aceleracion = data.get('aceleracion', 'No respondido')
    tiempo_restante = data.get('tiempo_restante', 'N/A')

    subject = "Nuevas Respuestas del Parcial de Física (Desde la Web)"
    body = f"""
    Se han recibido nuevas respuestas desde la página web desplegada.
    
    Detalles:
    - Fuerza Normal (N): {fuerza_normal}
    - Fuerza de Fricción (N): {fuerza_friccion}
    - Aceleración (m/s²): {aceleracion}
    - Tiempo restante: {tiempo_restante}
    """

    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        
        return jsonify({"message": "Respuestas recibidas y correo enviado."}), 200

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return jsonify({"error": "Hubo un problema al enviar el correo."}), 500

# Esto es necesario para que los servicios de despliegue sepan cómo ejecutar la app
if __name__ == '__main__':
    # El puerto lo asigna Render automáticamente, no es necesario especificarlo aquí.
    app.run(debug=False)
