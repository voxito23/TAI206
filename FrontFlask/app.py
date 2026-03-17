from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

API_URL = "http://127.0.0.1:5000/v1/usuarios/"
API_AUTH = ("vichdz", "1234")

@app.route("/")
def index():
    error = request.args.get("error")
    try:
        response = requests.get(API_URL)
        response.raise_for_status()
        data = response.json()
        lista_usuarios = data.get("data", [])
    except Exception as e:
        lista_usuarios = []
        error = f"Error de conexión con la API: {e}"

    return render_template("index.html", usuarios=lista_usuarios, error=error)


@app.route("/agregar", methods=["POST"])
def agregar():
    try:
        id_val = request.form.get("id")
        nombre = request.form.get("nombre")
        edad = request.form.get("edad")

        if not id_val or not nombre or not edad:
            return redirect(url_for("index", error="Todos los campos son obligatorios"))

        nombre = nombre.strip()

        try:
            id_val = int(id_val)
            edad = int(edad)
        except ValueError:
            return redirect(url_for("index", error="ID y edad deben ser números enteros"))

        if id_val <= 0:
            return redirect(url_for("index", error="El ID debe ser mayor que 0"))

        if len(nombre) < 3 or len(nombre) > 50:
            return redirect(url_for("index", error="El nombre debe tener entre 3 y 50 caracteres"))

        if edad < 0 or edad > 121:
            return redirect(url_for("index", error="La edad debe estar entre 0 y 121"))

        nuevo_usuario = {
            "id": id_val,
            "nombre": nombre,
            "edad": edad
        }

        response = requests.post(API_URL, json=nuevo_usuario)

        if response.status_code == 400:
            return redirect(url_for("index", error="El ID ya está registrado"))

        if response.status_code == 422:
            return redirect(url_for("index", error="Datos inválidos"))

        response.raise_for_status()
        return redirect(url_for("index"))

    except Exception as e:
        return redirect(url_for("index", error=f"Ocurrió un error: {e}"))


@app.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
        response = requests.delete(
            f"{API_URL}{id}",
            auth=API_AUTH
        )

        if response.status_code == 401:
            return redirect(url_for("index", error="Credenciales incorrectas para eliminar"))

        if response.status_code == 404:
            return redirect(url_for("index", error="Usuario no encontrado"))

        response.raise_for_status()

    except Exception as e:
        return redirect(url_for("index", error=f"Error al eliminar: {e}"))

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010, debug=True)