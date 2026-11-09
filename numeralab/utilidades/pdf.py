"""Genera un PDF con el procedimiento paso a paso (texto, ecuaciones y resultados) de un método."""
import html
import io
import os

import matplotlib
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image, NextPageTemplate, PageBreak, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

from utilidades.ecuaciones import png_ecuacion

ROJO = colors.HexColor("#D90429")
_FUENTES = False


def _registrar_fuentes():
    """Usa las fuentes DejaVu que trae matplotlib (cubren ε, δ, subíndices, ≈, →...). No hay que instalar nada."""
    global _FUENTES
    if _FUENTES:
        return
    carpeta = os.path.join(matplotlib.get_data_path(), "fonts", "ttf")
    pdfmetrics.registerFont(TTFont("DV", os.path.join(carpeta, "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DV-B", os.path.join(carpeta, "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DVM", os.path.join(carpeta, "DejaVuSansMono.ttf")))
    _FUENTES = True


def _estilos():
    return {
        "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=15, textColor=ROJO, spaceBefore=4, spaceAfter=6),
        "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=10.5, spaceBefore=8, spaceAfter=3),
        "p": ParagraphStyle("p", fontName="DV", fontSize=9.5, leading=13.5, spaceAfter=3),
        "ok": ParagraphStyle("ok", fontName="DV", fontSize=9.5, leading=13.5, backColor=colors.HexColor("#E8F5E9"),
                             borderPadding=5, spaceBefore=5, spaceAfter=7),
        "warn": ParagraphStyle("warn", fontName="DV", fontSize=9.5, leading=13.5, backColor=colors.HexColor("#FFF4E5"),
                               borderPadding=5, spaceBefore=5, spaceAfter=7),
        "calc": ParagraphStyle("calc", fontName="DVM", fontSize=8.5, leading=12, spaceAfter=2),
        "titulo": ParagraphStyle("t", fontName="DV-B", fontSize=20, textColor=ROJO, spaceAfter=2),
        "sub": ParagraphStyle("s", fontName="DV", fontSize=10, textColor=colors.HexColor("#6B7280"), spaceAfter=8),
    }


def _ecuacion(tex, ancho_max, color):
    png = png_ecuacion(tex, tam=13, color=color, dpi=200, max_ancho=int(ancho_max / 72 * 200))
    if png is None:
        return Paragraph(html.escape(tex), _estilos()["calc"])
    from PIL import Image as PILImage
    w, h = PILImage.open(io.BytesIO(png)).size
    ancho = w / 200 * 72
    alto = h / 200 * 72
    img = Image(io.BytesIO(png), width=ancho, height=alto)
    img.hAlign = "LEFT"
    return img


def _flowables(bloques, st, ancho_max):
    out = []
    for estilo, contenido in bloques:
        if estilo == "h1":
            out.append(Paragraph(html.escape(contenido), st["h1"]))
        elif estilo == "h2":
            out.append(Paragraph(html.escape(contenido), st["h2"]))
        elif estilo == "p":
            if contenido.strip():
                out.append(Paragraph(html.escape(contenido), st["p"]))
        elif estilo in ("ok", "warn"):
            out.append(Paragraph(html.escape(contenido), st[estilo]))
        elif estilo in ("eq", "eqf"):
            out.append(_ecuacion(contenido, ancho_max, "#111827"))
        elif estilo == "eqr":
            out.append(_ecuacion(contenido, ancho_max, "#C8102E"))
        else:
            out.append(Paragraph(html.escape(contenido).replace(" ", "&nbsp;"), st["calc"]))
    return out


def _tabla(cols, filas, ancho_total):
    """Tabla de iteraciones con encabezado rojo, filas alternadas y encabezado repetido en cada página."""
    n = len(cols)
    tam = 8.5 if n <= 7 else 7.5
    enc = ParagraphStyle("enc", fontName="DV-B", fontSize=tam, leading=tam + 2, textColor=colors.white,
                         alignment=TA_CENTER)
    datos = [[Paragraph(html.escape(str(c)), enc) for c in cols]] + [[str(v) for v in fila] for fila in filas]
    # ancho de cada columna proporcional al texto más largo (con un mínimo)
    pesos = [max(len(str(cols[j])) * 0.8, *(len(str(f[j])) for f in filas), 4) for j in range(n)]
    anchos = [ancho_total * p / sum(pesos) for p in pesos]
    t = Table(datos, colWidths=anchos, repeatRows=1)
    estilo = [("FONTNAME", (0, 1), (-1, -1), "DV"), ("FONTSIZE", (0, 1), (-1, -1), tam),
              ("BACKGROUND", (0, 0), (-1, 0), ROJO), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 4),
              ("BOTTOMPADDING", (0, 0), (-1, -1), 4), ("LEFTPADDING", (0, 0), (-1, -1), 3),
              ("RIGHTPADDING", (0, 0), (-1, -1), 3),
              ("LINEBELOW", (0, 0), (-1, -1), 0.4, colors.HexColor("#E5E7EB")),
              ("BOX", (0, 0), (-1, -1), 0.8, ROJO),
              ("FONTNAME", (0, 1), (0, -1), "DV-B")]
    for r in range(2, len(datos), 2):
        estilo.append(("BACKGROUND", (0, r), (-1, r), colors.HexColor("#FDECEF")))
    t.setStyle(TableStyle(estilo))
    return t


def procedimiento_pdf(nombre_metodo, funcion, mensaje, resumen, paginas, tabla=None):
    """Devuelve los bytes del PDF.

    resumen: bloques de `res.bloques_resumen(dec)`; paginas: lista (titulo, bloques) de `generar_pasos(res, dec)`;
    tabla: (encabezados, filas) de `tabla_iteraciones(...)`; si se da, se agrega al final en hoja horizontal.
    """
    _registrar_fuentes()
    st = _estilos()
    buf = io.BytesIO()
    marg = 2 * cm
    vertical, horizontal = A4, landscape(A4)

    def pie(canvas, d):
        w = canvas._pagesize[0]
        canvas.saveState()
        canvas.setFont("DV", 8)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.drawString(marg, 1 * cm, "NumeraLab · Métodos Numéricos · Universidad Piloto de Colombia")
        canvas.drawRightString(w - marg, 1 * cm, f"Página {d.page}")
        canvas.restoreState()

    doc = BaseDocTemplate(buf, pagesize=vertical, title=f"NumeraLab - {nombre_metodo}", author="NumeraLab",
                          leftMargin=marg, rightMargin=marg, topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    f_v = Frame(marg, 1.8 * cm, vertical[0] - 2 * marg, vertical[1] - 3.6 * cm, id="v")
    f_h = Frame(1.5 * cm, 1.6 * cm, horizontal[0] - 3 * cm, horizontal[1] - 3.2 * cm, id="h")
    doc.addPageTemplates([PageTemplate("vertical", [f_v], onPage=pie, pagesize=vertical),
                          PageTemplate("horizontal", [f_h], onPage=pie, pagesize=horizontal)])
    ancho = vertical[0] - 2 * marg

    historia = [Paragraph("NumeraLab", st["titulo"]),
                Paragraph(f"{html.escape(nombre_metodo)} · procedimiento completo", st["sub"]),
                HRFlowable(width="100%", color=ROJO, thickness=2, spaceAfter=8),
                Paragraph(f"<b>Función:</b> f(x) = {html.escape(funcion)}", st["p"]),
                Paragraph(html.escape(mensaje), st["p"]), Spacer(1, 6)]
    historia += _flowables(resumen, st, ancho)
    for titulo, bloques in paginas:
        historia.append(PageBreak())
        historia += _flowables(bloques, st, ancho)
    if tabla is not None:
        cols, filas = tabla
        historia += [NextPageTemplate("horizontal"), PageBreak(),
                     Paragraph("Tabla de iteraciones", st["h1"]),
                     Paragraph(f"{html.escape(nombre_metodo)} · f(x) = {html.escape(funcion)}", st["sub"]),
                     _tabla(cols, filas, horizontal[0] - 3 * cm)]
    doc.build(historia)
    return buf.getvalue()
