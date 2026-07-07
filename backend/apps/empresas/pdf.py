"""
Genera el PDF del inventario de una empresa usando reportlab.

Formato:
  - Encabezado con nombre y datos de la empresa
  - Tabla: Código | Nombre | Descripción | Precio (COP) | Cantidad
  - Fila de totales: total productos, valor total del inventario
"""

from __future__ import annotations

import io
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from domain.entities.empresa import Empresa
from apps.productos.use_cases import ProductoConPrecios


def generar_pdf_inventario(
    empresa: Empresa,
    productos: list[ProductoConPrecios],
) -> bytes:
    """Retorna el PDF como bytes para enviar como HttpResponse o adjunto de email."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Inventario — {empresa.nombre}",
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Encabezado ────────────────────────────────────────────────────────────
    story.append(Paragraph(f"<b>Inventario de productos</b>", styles["Title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(f"<b>Empresa:</b> {empresa.nombre}", styles["Normal"]))
    story.append(Paragraph(f"<b>NIT:</b> {empresa.nit}", styles["Normal"]))
    story.append(Paragraph(f"<b>Dirección:</b> {empresa.direccion}", styles["Normal"]))
    story.append(Paragraph(f"<b>Teléfono:</b> {empresa.telefono}", styles["Normal"]))
    story.append(Spacer(1, 0.6 * cm))

    # ── Tabla ─────────────────────────────────────────────────────────────────
    header = ["Código", "Nombre", "Descripción", "Precio base", "Precio COP", "Cantidad"]
    rows = [header]

    total_valor = Decimal("0")
    total_cantidad = 0

    for pcp in productos:
        p = pcp.detalle.producto
        precio_base = f"{p.precio_base.monto:,.0f} {p.precio_base.moneda}"

        precio_cop_obj = pcp.precios.get("COP")
        if precio_cop_obj:
            precio_cop = f"${precio_cop_obj.monto:,.0f}"
            total_valor += precio_cop_obj.monto * p.cantidad
        else:
            precio_cop = precio_base
            total_valor += p.precio_base.monto * p.cantidad

        total_cantidad += p.cantidad

        # Truncar descripción larga para que quepa en la celda
        descripcion = (p.caracteristicas or "")[:120]
        if len(p.caracteristicas or "") > 120:
            descripcion += "..."

        rows.append([
            p.codigo,
            p.nombre,
            Paragraph(descripcion, styles["Normal"]),
            precio_base,
            precio_cop,
            str(p.cantidad),
        ])

    # Fila de totales
    rows.append([
        "", "",
        Paragraph("<b>TOTALES</b>", styles["Normal"]),
        "",
        Paragraph(f"<b>${total_valor:,.0f} COP</b>", styles["Normal"]),
        Paragraph(f"<b>{total_cantidad}</b>", styles["Normal"]),
    ])

    col_widths = [2.5 * cm, 5 * cm, 9 * cm, 3.5 * cm, 3.5 * cm, 2.2 * cm]
    table = Table(rows, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, 0),  9),
        ("ALIGN",       (0, 0), (-1, 0),  "CENTER"),
        # Body
        ("FONTSIZE",    (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#f1f5f9")]),
        # Totals row
        ("BACKGROUND",  (0, -1), (-1, -1), colors.HexColor("#dbeafe")),
        ("FONTNAME",    (0, -1), (-1, -1), "Helvetica-Bold"),
        # Grid
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))

    story.append(table)
    doc.build(story)
    return buffer.getvalue()
