import json
import os

from flask import Flask, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_HISTORIAL = os.path.join(BASE_DIR, "historial.json")
app = Flask(__name__, static_folder=".", static_url_path="")


def numero(datos, campo):
    valor = datos.get(campo)
    try:
        valor = float(valor)
    except (TypeError, ValueError):
        raise ValueError(f"Falta o es inválido el campo '{campo}'")
    if valor <= 0:
        raise ValueError(f"El campo '{campo}' debe ser mayor que cero")
    return valor


def formatear(valor):
    if abs(valor - round(valor)) < 1e-9:
        return int(round(valor))
    if abs(valor) < 0.1:
        return round(valor, 3)
    return round(valor, 2)


def item(etiqueta, valor, unidad):
    return {"etiqueta": etiqueta, "valor": formatear(valor), "unidad": unidad}


def calcular_techo(datos):
    espesor = numero(datos, "espesor")
    ancho = numero(datos, "ancho")
    largo = numero(datos, "largo")
    superficie = ancho * largo
    volumen = superficie * espesor / 100
    return [
        item("Superficie", superficie, "m²"),
        item("Cemento", volumen * 330, "kg"),
        item("Arena", volumen * 0.72, "m³"),
        item("Piedra", volumen * 0.72, "m³"),
        item("Hierro Ø8", superficie * 7, "m"),
        item("Hierro Ø6", superficie * 4, "m"),
    ]


def calcular_piso(datos):
    ancho = numero(datos, "ancho")
    largo = numero(datos, "largo")
    superficie = ancho * largo
    return [
        item("Superficie base", superficie, "m²"),
        item("Con 10% de recorte", superficie * 1.10, "m²"),
    ]


def calcular_pintura(datos):
    superficie = numero(datos, "superficie")
    return [
        item("Pintura necesaria", superficie / 6, "litros"),
    ]


def calcular_muro(datos):
    espesor = numero(datos, "espesor")
    largo = numero(datos, "largo")
    alto = numero(datos, "alto")
    superficie = largo * alto
    return [
        item("Cemento", superficie * 3.8 * (espesor / 20), "kg"),
        item("Ladrillos", superficie * 30, "unidades"),
    ]


def calcular_viga(datos):
    largo = numero(datos, "largo")
    volumen = largo * 0.15 * 0.25
    return [
        item("Cemento", volumen * 300, "kg"),
        item("Arena", volumen * (2 / 3), "m³"),
        item("Piedra", volumen * (2 / 3), "m³"),
        item("Hierro Ø8", largo * 5, "m"),
        item("Hierro Ø4", largo * 3.75, "m"),
    ]


def calcular_columna(datos):
    largo = numero(datos, "largo")
    volumen = largo * 0.15 * 0.15
    return [
        item("Cemento", volumen * 333.333, "kg"),
        item("Arena", volumen * (32 / 45), "m³"),
        item("Piedra", volumen * (32 / 45), "m³"),
        item("Hierro Ø10", largo * 6, "m"),
        item("Hierro Ø4", largo * 3, "m"),
    ]


def calcular_contrapiso(datos):
    espesor = numero(datos, "espesor")
    ancho = numero(datos, "ancho")
    largo = numero(datos, "largo")
    volumen = ancho * largo * espesor / 100
    return [
        item("Volumen", volumen, "m³"),
        item("Cemento", volumen * 105, "kg"),
        item("Arena", volumen * 0.45, "m³"),
        item("Piedra", volumen * 0.9, "m³"),
    ]


def calcular(tipo, datos):
    if tipo == "techo":
        return calcular_techo(datos)
    if tipo == "piso":
        return calcular_piso(datos)
    if tipo == "pintura":
        return calcular_pintura(datos)
    if tipo == "muro":
        return calcular_muro(datos)
    if tipo == "viga":
        return calcular_viga(datos)
    if tipo == "columna":
        return calcular_columna(datos)
    if tipo == "contrapiso":
        return calcular_contrapiso(datos)
    raise ValueError("Cálculo no válido")


def guardar_historial(registro):
    historial = []
    if os.path.exists(RUTA_HISTORIAL):
        with open(RUTA_HISTORIAL, "r", encoding="utf-8") as archivo:
            historial = json.load(archivo)
    historial.append(registro)
    with open(RUTA_HISTORIAL, "w", encoding="utf-8") as archivo:
        json.dump(historial, archivo, ensure_ascii=False, indent=2)


@app.get("/")
def inicio():
    return app.send_static_file("01-login.html")


@app.post("/api/calcular/<tipo>")
def calcular_api(tipo):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Los datos deben ser un objeto JSON"}), 400

    try:
        resultados = calcular(tipo, datos)
        guardar_historial({"tipo": tipo, "datos": datos, "resultados": resultados})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify({"tipo": tipo, "resultados": resultados})

@app.route('/')
def home():
    return send_from_directory('.', '01-login.html')

if __name__ == "__main__":
    app.run(port=8000)
    from flask import send_from_directory


