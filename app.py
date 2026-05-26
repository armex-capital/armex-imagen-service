from flask import Flask, request, jsonify
from generar_imagen import generar_imagen_base64

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/generar-imagen", methods=["POST"])
def generar():
    data = request.get_json(force=True) or {}
    try:
        imagen = generar_imagen_base64(
            nombre      = data.get("nombre", "Cliente"),
            numero_cita = data.get("numero_cita", "CIT-0000"),
            fecha_cita  = data.get("fecha_cita", ""),
            hora_cita   = data.get("hora_cita", ""),
            modalidad   = data.get("modalidad", "presencial"),
        )
        return jsonify({"imagen": imagen})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
