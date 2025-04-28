"""Python Flask WebApp Auth0 integration example with Calculator
"""

import json
from os import environ as env
from urllib.parse import quote_plus, urlencode
import sqlite3
from datetime import datetime

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, jsonify

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
app.secret_key = env.get("APP_SECRET_KEY")

# Configuración de la base de datos
def init_db():
    conn = sqlite3.connect('calculator.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS sessions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id TEXT,
                  email TEXT,
                  token TEXT,
                  created_at TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration',
)

# Controllers API
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get("user"),
        pretty=json.dumps(session.get("user"), indent=4),
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo_url = f'https://{env.get("AUTH0_DOMAIN")}/userinfo'
    resp = oauth.auth0.get(userinfo_url)
    userinfo = resp.json()
    
    # Asegurarnos de que tenemos toda la información del usuario
    session["user"] = {
        "name": userinfo["name"],
        "email": userinfo["email"],
        "picture": userinfo["picture"],
        "sub": userinfo["sub"]
    }
    
    # Guardar datos de sesión en la base de datos
    conn = sqlite3.connect('calculator.db')
    c = conn.cursor()
    c.execute('''INSERT INTO sessions (user_id, email, token, created_at)
                 VALUES (?, ?, ?, ?)''',
              (userinfo['sub'],
               userinfo['email'],
               json.dumps(token),
               datetime.now()))
    conn.commit()
    conn.close()
    
    return redirect("/")

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route("/calculate", methods=["POST"])
def calculate():
    if not session.get("user"):
        return jsonify({"error": "No autenticado"}), 401
    
    data = request.get_json()
    numbers = data.get("numbers", [])
    operation = data.get("operation", "+")
    
    if not numbers or len(numbers) < 2:
        return jsonify({"error": "Se necesitan al menos dos números"}), 400
    
    try:
        numbers = [float(num) for num in numbers]
    except ValueError:
        return jsonify({"error": "Todos los valores deben ser números"}), 400
    
    result = numbers[0]
    for num in numbers[1:]:
        if operation == "+":
            result += num
        elif operation == "-":
            result -= num
        elif operation == "*":
            result *= num
        elif operation == "/":
            if num == 0:
                return jsonify({"error": "División por cero"}), 400
            result /= num
    
    return jsonify({"result": result})

@app.route("/admin")
def admin():
    if not session.get("user"):
        return redirect("/login")
    
    # Verificar si el usuario es administrador
    if session["user"]["email"] != "tu_email@ejemplo.com":
        return jsonify({"error": "No autorizado"}), 403
    
    conn = sqlite3.connect('calculator.db')
    c = conn.cursor()
    c.execute('''SELECT id, user_id, email, created_at FROM sessions ORDER BY created_at DESC''')
    sessions = c.fetchall()
    conn.close()
    
    return render_template(
        "admin.html",
        session=session.get("user"),
        sessions=sessions
    )

@app.route("/admin/sessions/<int:session_id>", methods=["DELETE"])
def delete_session(session_id):
    if not session.get("user"):
        return jsonify({"error": "No autenticado"}), 401
    
    # Verificar si el usuario es administrador
    if session["user"]["email"] != "jose.leyva244685@potros.itson.edu.mx":
        return jsonify({"error": "No autorizado"}), 403
    
    conn = sqlite3.connect('calculator.db')
    c = conn.cursor()
    c.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"message": "Sesión eliminada correctamente"})

@app.route("/admin/sessions", methods=["GET"])
def get_sessions():
    if not session.get("user"):
        return jsonify({"error": "No autenticado"}), 401
    
    # Verificar si el usuario es administrador
    if session["user"]["email"] != "jose.leyva244685@potros.itson.edu.mx":
        return jsonify({"error": "No autorizado"}), 403
    
    conn = sqlite3.connect('calculator.db')
    c = conn.cursor()
    c.execute('''SELECT id, user_id, email, created_at FROM sessions ORDER BY created_at DESC''')
    sessions = c.fetchall()
    conn.close()
    
    return jsonify([{
        "id": s[0],
        "user_id": s[1],
        "email": s[2],
        "created_at": s[3]
    } for s in sessions])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))
