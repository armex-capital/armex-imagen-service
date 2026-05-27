import os
import uuid
import base64
import requests as req
from flask import Flask, request, jsonify
from generar_imagen import generar_imagen_base64

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://api.armex.website")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")
BUCKET = "citas"


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/generar-imagen", methods=["POST"])
def generar():
    data = request.get_json(force=True) or {}
    try:
        imagen_b64 = generar_imagen_base64(
            nombre      = data.get("nombre", "Cliente"),
            numero_cita = data.get("numero_cita", "CIT-0000"),
            fecha_cita  = data.get("fecha_cita", ""),
            hora_cita   = data.get("hora_cita", ""),
            modalidad   = data.get("modalidad", "presencial"),
        )
        img_bytes = base64.b64decode(imagen_b64)
        filename = f"{uuid.uuid4()}.png"

        upload = req.put(
            f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{filename}",
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "image/png",
            },
            data=img_bytes,
            timeout=15,
        )
        upload.raise_for_status()

        url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{filename}"
        return jsonify({"url": url})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
