from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

API_BASE = "http://127.0.0.1:5000"


@app.route("/")
def index():
    error = request.args.get("error")
    mensaje = request.args.get("mensaje")
    busqueda = request.args.get("busqueda", "")

    try:
        response_libros = requests.get(f"{API_BASE}/v1/libros/")
        response_libros.raise_for_status()
        libros = response_libros.json().get("data", [])
    except requests.exceptions.RequestException as e:
        libros = []
        error = f"Error al obtener libros: {e}"

    try:
        response_prestamos = requests.get(f"{API_BASE}/v1/prestamos/")
        response_prestamos.raise_for_status()
        prestamos = response_prestamos.json().get("data", [])
    except requests.exceptions.RequestException as e:
        prestamos = []
        if not error:
            error = f"Error al obtener préstamos: {e}"

    if busqueda:
        try:
            response_busqueda = requests.get(f"{API_BASE}/v1/libros/buscar", params={"nombre": busqueda})
            response_busqueda.raise_for_status()
            libros_filtrados = response_busqueda.json().get("data", [])
        except requests.exceptions.RequestException as e:
            libros_filtrados = []
            if not error:
                error = f"Error en la búsqueda: {e}"
    else:
        libros_filtrados = libros

    return render_template(
        "index.html",
        libros=libros_filtrados,
        prestamos=prestamos,
        error=error,
        mensaje=mensaje,
        busqueda=busqueda
    )


@app.route("/agregar_libro", methods=["POST"])
def agregar_libro():
    libro = {
        "id": int(request.form.get("id")),
        "nombre": request.form.get("nombre"),
        "anio_publicacion": int(request.form.get("anio_publicacion")),
        "paginas": int(request.form.get("paginas")),
        "estado": request.form.get("estado")
    }

    try:
        response = requests.post(f"{API_BASE}/v1/libros/", json=libro)

        if response.status_code >= 400:
            try:
                detalle = response.json().get("detail", "Error al agregar libro")
            except Exception:
                detalle = "Error al agregar libro"
            return redirect(url_for("index", error=detalle))

        return redirect(url_for("index", mensaje="Libro agregado correctamente"))

    except requests.exceptions.RequestException as e:
        return redirect(url_for("index", error=f"Error de conexión: {e}"))


@app.route("/buscar_libro", methods=["GET"])
def buscar_libro():
    nombre = request.args.get("nombre", "")
    return redirect(url_for("index", busqueda=nombre))


@app.route("/registrar_prestamo", methods=["POST"])
def registrar_prestamo():
    prestamo = {
        "id_prestamo": int(request.form.get("id_prestamo")),
        "id_libro": int(request.form.get("id_libro")),
        "usuario": {
            "nombre": request.form.get("usuario_nombre"),
            "correo": request.form.get("usuario_correo")
        }
    }

    try:
        response = requests.post(f"{API_BASE}/v1/prestamos/", json=prestamo)

        if response.status_code >= 400:
            try:
                detalle = response.json().get("detail", "Error al registrar préstamo")
            except Exception:
                detalle = "Error al registrar préstamo"
            return redirect(url_for("index", error=detalle))

        return redirect(url_for("index", mensaje="Préstamo registrado correctamente"))

    except requests.exceptions.RequestException as e:
        return redirect(url_for("index", error=f"Error de conexión: {e}"))


@app.route("/devolver_prestamo", methods=["POST"])
def devolver_prestamo():
    id_prestamo = request.form.get("id_prestamo")

    try:
        response = requests.put(f"{API_BASE}/v1/prestamos/{id_prestamo}/devolver")

        if response.status_code >= 400:
            try:
                detalle = response.json().get("detail", "Error al devolver libro")
            except Exception:
                detalle = "Error al devolver libro"
            return redirect(url_for("index", error=detalle))

        return redirect(url_for("index", mensaje="Libro devuelto correctamente"))

    except requests.exceptions.RequestException as e:
        return redirect(url_for("index", error=f"Error de conexión: {e}"))


@app.route("/eliminar_prestamo", methods=["POST"])
def eliminar_prestamo():
    id_prestamo = request.form.get("id_prestamo")

    try:
        response = requests.delete(f"{API_BASE}/v1/prestamos/{id_prestamo}")

        if response.status_code >= 400:
            try:
                detalle = response.json().get("detail", "Error al eliminar préstamo")
            except Exception:
                detalle = "Error al eliminar préstamo"
            return redirect(url_for("index", error=detalle))

        return redirect(url_for("index", mensaje="Préstamo eliminado correctamente"))

    except requests.exceptions.RequestException as e:
        return redirect(url_for("index", error=f"Error de conexión: {e}"))


if __name__ == "__main__":
    app.run(debug=True, port=5015)