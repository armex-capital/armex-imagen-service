import os
import base64
import textwrap
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

_BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(_BASE, "fonts") if os.path.isdir(os.path.join(_BASE, "fonts")) else _BASE

NAVY      = (15,  11, 119)
GOLD      = (180, 145,  60)
WHITE     = (255, 255, 255)
TEXT_DARK = ( 26,  26,  46)
TEXT_MID  = ( 85,  85, 110)
CARD_BG   = (238, 242, 250)

W          = 600
HEADER_H   = 130
BODY_PAD   = 36
CARD_ROW_H = 36
CARD_ROWS  = 5
FOOTER_H   = 44


def _font(variant, size):
    names = {
        "Bold":     "Montserrat-Bold.ttf",
        "SemiBold": "Montserrat-SemiBold.ttf",
        "Regular":  "Montserrat-Regular.ttf",
        "Light":    "Montserrat-Light.ttf",
    }
    path = os.path.join(FONT_DIR, names.get(variant, "Montserrat-Regular.ttf"))
    return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()


def _tw(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[2] - bb[0]

def _th(draw, text, fnt):
    bb = draw.textbbox((0, 0), text, font=fnt)
    return bb[3] - bb[1]


def generar_imagen_base64(nombre, numero_cita, fecha_cita, hora_cita, modalidad, ubicacion=None):
    f_title    = _font("Bold",     30)
    f_subtitle = _font("Light",    11)
    f_greeting = _font("SemiBold", 18)
    f_body     = _font("Regular",  14)
    f_label    = _font("Light",    12)
    f_value    = _font("SemiBold", 13)
    f_small    = _font("Regular",  11)
    f_footer   = _font("Light",    10)

    dummy = Image.new("RGB", (W, 10))
    dd    = ImageDraw.Draw(dummy)

    wrapped = textwrap.fill(f"Hola, {nombre}", width=32)
    g_lines = wrapped.count("\n") + 1
    g_h     = g_lines * (_th(dd, "A", f_greeting) + 4)
    CARD_H  = 16 + CARD_ROWS * CARD_ROW_H + 16

    body_h = (
        20 + g_h + 10
        + _th(dd, "A", f_body)  + 8
        + _th(dd, "A", f_label) + 16
        + CARD_H + 20
        + _th(dd, "A", f_small) + 6
        + _th(dd, "A", f_small) + 24
    )
    H = HEADER_H + body_h + FOOTER_H

    img  = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # Encabezado
    draw.rectangle([(0, 0), (W, HEADER_H)], fill=NAVY)
    draw.rectangle([(0, HEADER_H - 3), (W, HEADER_H)], fill=GOLD)

    title = "ARMEX CAPITAL"
    tw = _tw(draw, title, f_title)
    draw.text(((W - tw) / 2, 28), title, font=f_title, fill=WHITE)

    sub = "CONFIRMACIÓN DE CITA"
    sw  = _tw(draw, sub, f_subtitle)
    line_len = (W - sw) // 2 - 24
    draw.rectangle([(BODY_PAD, 85), (BODY_PAD + line_len, 86)], fill=GOLD)
    draw.text(((W - sw) / 2, 80), sub, font=f_subtitle, fill=(176, 196, 232))
    draw.rectangle([(W - BODY_PAD - line_len, 85), (W - BODY_PAD, 86)], fill=GOLD)

    # Cuerpo
    y = HEADER_H + 20
    draw.text((BODY_PAD, y), wrapped, font=f_greeting, fill=NAVY, spacing=4)
    y += g_h + 10

    msg1 = "Tu cita ha sido registrada exitosamente."
    draw.text((BODY_PAD, y), msg1, font=f_body, fill=TEXT_DARK)
    y += _th(draw, msg1, f_body) + 8

    msg2 = "A continuación encontrarás los detalles:"
    draw.text((BODY_PAD, y), msg2, font=f_label, fill=TEXT_MID)
    y += _th(draw, msg2, f_label) + 16

    # Tarjeta de detalles
    cx0, cx1 = BODY_PAD, W - BODY_PAD
    cy0, cy1 = y, y + CARD_H
    draw.rounded_rectangle([cx0, cy0, cx1, cy1], radius=6, fill=CARD_BG)
    draw.rectangle([(cx0, cy0), (cx0 + 4, cy1)], fill=NAVY)

    hora_fmt = str(hora_cita)[:5] if hora_cita else ""
    if ubicacion is None:
        ubicacion = (
            "Av. 50 Mts. 100, Torre 3, Piso 7, Cuernavaca"
            if str(modalidad).lower() == "presencial"
            else "Videollamada (enlace por correo)"
        )
    rows = [
        ("N.° de cita",  str(numero_cita)),
        ("Fecha",        str(fecha_cita)),
        ("Hora",         f"{hora_fmt} hrs"),
        ("Modalidad",    str(modalidad).capitalize()),
        ("Ubicación",    str(ubicacion)),
    ]
    ry = cy0 + 16
    for label, value in rows:
        draw.text((cx0 + 20, ry), label, font=f_label, fill=TEXT_MID)
        draw.text((cx0 + 190, ry), value, font=f_value, fill=NAVY)
        ry += CARD_ROW_H
    y = cy1 + 20

    # Contacto
    c1 = "¿Necesitas reprogramar o tienes alguna duda?"
    draw.text((BODY_PAD, y), c1, font=f_small, fill=TEXT_MID)
    y += _th(draw, c1, f_small) + 6

    c2 = "atclientes@armexcapital.com"
    draw.text((BODY_PAD, y), c2, font=f_small, fill=NAVY)
    uw = _tw(draw, c2, f_small)
    uh = _th(draw, c2, f_small)
    draw.rectangle([(BODY_PAD, y + uh + 1), (BODY_PAD + uw, y + uh + 2)], fill=NAVY)

    # Footer
    fy0 = H - FOOTER_H
    draw.rectangle([(0, fy0), (W, H)], fill=NAVY)
    foot = "© 2026 ARMEX CAPITAL S.A.P.I. de C.V. — Todos los derechos reservados."
    fw = _tw(draw, foot, f_footer)
    fh = _th(draw, foot, f_footer)
    draw.text(((W - fw) / 2, fy0 + (FOOTER_H - fh) // 2), foot, font=f_footer, fill=(176, 196, 232))

    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")
