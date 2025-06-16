from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
import streamlit as st

def generate_pdf_report():
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    section_style = styles['Heading2']
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph("Résumé de l'Échangeur de Chaleur", title_style))
    elements.append(Spacer(1, 12))

    # Geometry Section
    g = st.session_state.get("inputs_geometry")
    if g:
        elements.append(Paragraph("Section Géométrie", section_style))
        geo_data = [["Paramètre", "Valeur"]]
        for k, v in g.items():
            geo_data.append([str(k), str(v)])
        geo_data += [
            ["DB_Perry", str(st.session_state.get('DB_Perry'))],
            ["N_Perry", str(st.session_state.get('N_Perry'))],
            ["DB_HEDH", str(st.session_state.get('DB_HEDH'))],
            ["DB_Phadkeb", str(st.session_state.get('DB_Phadkeb'))],
            ["DB_VDI", str(st.session_state.get('DB_VDI'))],
            ["DShell_min", str(st.session_state.get('DShell_min'))],
            ["Clearance auto", str(st.session_state.get('clearance_auto'))],
            ["Ø trou chicane", str(st.session_state.get('dB_hole'))],
            ["L_max sans support", str(st.session_state.get('L_max'))],
        ]
        geo_table = Table(geo_data, hAlign='LEFT')
        geo_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(geo_table)
        elements.append(Spacer(1, 12))

    # Clearance Section
    if st.session_state.get("clearance_result") is not None:
        elements.append(Paragraph("Section Jeu Calandre-Faisceau", section_style))
        clearance_data = [["Paramètre", "Valeur"], ["Jeu recommandé", str(st.session_state.get('clearance_result'))]]
        clearance_table = Table(clearance_data, hAlign='LEFT')
        clearance_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(clearance_table)
        elements.append(Spacer(1, 12))

    # Effectiveness Section
    p = st.session_state.get("inputs_pntu")
    if p:
        elements.append(Paragraph("Section Efficacité", section_style))
        eff_data = [["Paramètre", "Valeur"]]
        for k, v in p.items():
            eff_data.append([str(k), str(v)])
        eff_table = Table(eff_data, hAlign='LEFT')
        eff_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(eff_table)
        elements.append(Spacer(1, 12))

    # ML Prediction Section
    if st.session_state.get("fouling_prediction") is not None or st.session_state.get("ttc_prediction") is not None:
        elements.append(Paragraph("Section Prédiction ML", section_style))
        ml_data = [["Paramètre", "Valeur"]]
        if st.session_state.get("fouling_prediction") is not None:
            ml_data.append(["Niveau d'encrassement", str(st.session_state.get('fouling_prediction'))])
        if st.session_state.get("ttc_prediction") is not None:
            ml_data.append(["Heures avant nettoyage", str(st.session_state.get('ttc_prediction'))])
        ml_table = Table(ml_data, hAlign='LEFT')
        ml_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ]))
        elements.append(ml_table)
        elements.append(Spacer(1, 12))

    doc.build(elements)
    buffer.seek(0)
    return buffer 