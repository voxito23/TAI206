from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

API_URL = "http://127.0.0.1:5000/v1/usuarios/"

@app.route("/")
def index():
    error = request.args.get('error')
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        lista_usuarios = data.get("data", [])
    except Exception as e:
        lista_usuarios = []
        error = f"Error de conexión con la API: {e}"
    
    return render_template("vista.html", usuarios=lista_usuarios, error=error)

@app.route("/agregar", methods=["POST"])
def agregar():
    try:
        id_val = request.form.get("id")
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")

        if not id_val or not nombre or not edad:
            return redirect(url_for("index", error="Todos los campos son obligatorios"))

        nuevo_usuario = {
            "id": int(id_val),
            "nombre": nombre,
            "edad": int(edad)
        }
        
        response = requests.post(API_URL, json=nuevo_usuario)
        
        if response.status_code == 400:
            return redirect(url_for("index", error="El ID ya esta registrado"))
        
        response.raise_for_status()
        return redirect(url_for("index"))

    except Exception as e:
        return redirect(url_for("index", error=f"Ocurrio un error: {e}"))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    try:
        requests.delete(f"{API_URL}{id}")
    except:
        pass
    return redirect(url_for("index"))

if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=5010, debug=True)