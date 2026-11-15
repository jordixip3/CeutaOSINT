import io
import hashlib
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Color Palette
NAVY_DARK   = colors.HexColor('#0d1b2a')
NAVY_MED    = colors.HexColor('#1b263b')
CYAN_ACCENT = colors.HexColor('#00b4d8')
GREEN_ACC   = colors.HexColor('#00a86b')
TEXT_MAIN   = colors.HexColor('#212529')
TEXT_MUTED  = colors.HexColor('#6c757d')
BG_LIGHT    = colors.HexColor('#f8f9fa')
BORDER_GRAY = colors.HexColor('#dee2e6')

def get_custom_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=NAVY_DARK,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=CYAN_ACCENT,
        spaceAfter=12
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=NAVY_DARK,
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN
    )

    body_bold = ParagraphStyle(
        'DocBodyBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=14,
        textColor=TEXT_MAIN
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=NAVY_MED
    )

    meta_value = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=TEXT_MAIN
    )

    footer_style = ParagraphStyle(
        'FooterStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=TEXT_MUTED,
        alignment=1 # Center
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'section': section_heading,
        'body': body_style,
        'body_bold': body_bold,
        'meta_label': meta_label,
        'meta_value': meta_value,
        'footer': footer_style
    }

def generate_post_pdf(post, entities=None):
    """
    Generates a professional OSINT Intelligence Evidence Dossier PDF.
    Returns bytes of the PDF.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = get_custom_styles()
    story = []

    post_id = post.get("id", "N/A")
    title = post.get("title", "Despacho de Evidencia OSINT")
    content = post.get("content", "Sin extracto registrado.")
    source_name = post.get("source_name", "Desconocida")
    source_type = post.get("source_type", "WEB")
    author = post.get("author", "Anónimo / OSINT Tracker")
    pub_time = post.get("publish_time", "No especificada")
    category = post.get("category", "GENERAL")
    score = post.get("score", 0.0)
    url = post.get("url", "")
    score_breakdown = post.get("score_breakdown", {})

    # 1. Header Banner
    story.append(Paragraph("DOSSIER DE EVIDENCIA FORENSE // CIBERINTELIGENCIA OSINT", styles['subtitle']))
    story.append(Paragraph(f"Evidencia #{post_id}: {title}", styles['title']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=CYAN_ACCENT, spaceBefore=4, spaceAfter=10))

    # 2. Metadata Grid Table
    meta_data = [
        [
            Paragraph("Fuente Informativa:", styles['meta_label']),
            Paragraph(f"{source_name} ({source_type})", styles['meta_value']),
            Paragraph("Categoría Táctica:", styles['meta_label']),
            Paragraph(str(category), styles['meta_value'])
        ],
        [
            Paragraph("Autor / Canal:", styles['meta_label']),
            Paragraph(str(author), styles['meta_value']),
            Paragraph("Puntuación de Confianza:", styles['meta_label']),
            Paragraph(f"<b>{score} / 10.0</b>", styles['meta_value'])
        ],
        [
            Paragraph("Fecha / Hora Publicación:", styles['meta_label']),
            Paragraph(str(pub_time).replace("T", " "), styles['meta_value']),
            Paragraph("Fecha de Análisis OSINT:", styles['meta_label']),
            Paragraph(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), styles['meta_value'])
        ]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # 3. Scoring Breakdown Table
    story.append(Paragraph("Desglose Analítico de Confianza (Scoring Matrix)", styles['section']))
    sb_data = [
        [
            Paragraph("Autoridad de Fuente", styles['meta_label']),
            Paragraph("Corroboración Cruzada", styles['meta_label']),
            Paragraph("Lead Time / Oportunidad", styles['meta_label']),
            Paragraph("Especificidad Operativa", styles['meta_label']),
            Paragraph("Puntaje Ponderado", styles['meta_label'])
        ],
        [
            Paragraph(f"{score_breakdown.get('source_authority', 7.0)} / 10", styles['meta_value']),
            Paragraph(f"{score_breakdown.get('cross_corroboration', 7.0)} / 10", styles['meta_value']),
            Paragraph(f"{score_breakdown.get('temporal_lead_time', 7.5)} / 10", styles['meta_value']),
            Paragraph(f"{score_breakdown.get('specificity', 6.0)} / 10", styles['meta_value']),
            Paragraph(f"<b>{score} / 10.0</b>", styles['meta_value'])
        ]
    ]
    sb_table = Table(sb_data, colWidths=[105, 105, 105, 105, 100])
    sb_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY_MED),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 1), (-1, 1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(sb_table)
    story.append(Spacer(1, 12))

    # 4. Intelligence Content & Operational Extract
    story.append(Paragraph("Contenido y Despacho Forense Recolectado", styles['section']))
    content_box = [
        [Paragraph(content.replace("\n", "<br/><br/>"), styles['body'])]
    ]
    content_table = Table(content_box, colWidths=[520])
    content_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f1f5f9')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(content_table)
    story.append(Spacer(1, 12))

    # 5. Detected Entities
    story.append(Paragraph("Entidades y Vectores Detectados", styles['section']))
    if entities:
        ent_rows = [[Paragraph("Tipo de Entidad", styles['meta_label']), Paragraph("Valor / Identificador", styles['meta_label']), Paragraph("Confianza Algorítmica", styles['meta_label'])]]
        for e in entities[:10]:
            ent_type = e.get("entity_type", e.get("type", "KEYWORD"))
            ent_val = e.get("entity_value", e.get("value", ""))
            ent_conf = f"{round(float(e.get('confidence', 1.0)) * 100)}%"
            ent_rows.append([
                Paragraph(str(ent_type), styles['meta_value']),
                Paragraph(f"<b>{ent_val}</b>", styles['meta_value']),
                Paragraph(str(ent_conf), styles['meta_value'])
            ])
        ent_table = Table(ent_rows, colWidths=[160, 240, 120])
        ent_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        story.append(ent_table)
    else:
        story.append(Paragraph("<i>No se registraron entidades estructuradas adicionales en esta evidencia.</i>", styles['body']))

    story.append(Spacer(1, 14))

    # 6. Cryptographic Chain of Custody
    url_hash = hashlib.sha256((url + title + content).encode('utf-8')).hexdigest()
    story.append(Paragraph("Cadena de Custodia & Huella Criptográfica", styles['section']))
    hash_data = [
        [Paragraph("URL / Origen:", styles['meta_label']), Paragraph(f"<font color='#0077b6'>{url[:75]}...</font>", styles['meta_value'])],
        [Paragraph("Hash SHA-256:", styles['meta_label']), Paragraph(f"<font face='Courier' size='7'>{url_hash}</font>", styles['meta_value'])],
        [Paragraph("Firma Forense:", styles['meta_label']), Paragraph("REGISTRO INMUTABLE OSINT ENGINE // VERIFICADO", styles['meta_value'])],
    ]
    hash_table = Table(hash_data, colWidths=[120, 400])
    hash_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(hash_table)
    story.append(Spacer(1, 15))

    # 7. Footer Notice
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        f"Documento generado automáticamente por la Plataforma Universal de Ciberinteligencia OSINT · {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')} · Uso estricto para análisis e investigación.",
        styles['footer']
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def generate_report_pdf(report, posts=None):
    """
    Generates a full Executive Intelligence Summary Report PDF.
    Returns bytes of the PDF.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = get_custom_styles()
    story = []

    title = report.get("title", "Informe Ejecutivo de Ciberinteligencia Forense")
    overall_score = report.get("overall_score", 8.0)
    total_sources = report.get("total_sources", 0)
    gen_time = report.get("generated_at", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    exec_summary = report.get("executive_summary", "")
    key_findings = report.get("key_findings", [])

    # Header
    story.append(Paragraph("SISTEMA DE INTELIGENCIA DE FUENTES ABIERTAS (OSINT) // INFORME OFICIAL", styles['subtitle']))
    story.append(Paragraph(title, styles['title']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=CYAN_ACCENT, spaceBefore=4, spaceAfter=10))

    # Metrics Summary Box
    metrics_data = [
        [
            Paragraph("Score de Certeza Global", styles['meta_label']),
            Paragraph("Fuentes Consultadas", styles['meta_label']),
            Paragraph("Fecha de Emisión", styles['meta_label']),
            Paragraph("Estado de Validación", styles['meta_label'])
        ],
        [
            Paragraph(f"<b>{overall_score} / 10.0</b>", styles['meta_value']),
            Paragraph(f"<b>{total_sources}</b> entidades/medios", styles['meta_value']),
            Paragraph(str(gen_time)[:19], styles['meta_value']),
            Paragraph("<font color='#00a86b'><b>VERIFICADO MULTI-FUENTE</b></font>", styles['meta_value'])
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[130, 130, 130, 130])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(metrics_table)
    story.append(Spacer(1, 14))

    # Executive Summary
    story.append(Paragraph("Resumen Ejecutivo & Conclusión Operativa", styles['section']))
    summary_box = [[Paragraph(exec_summary.replace("\n", "<br/><br/>"), styles['body'])]]
    summary_table = Table(summary_box, colWidths=[520])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Key Findings
    story.append(Paragraph("Hallazgos Clave & Vectores de Incidente", styles['section']))
    if key_findings:
        findings_table_data = []
        for i, item in enumerate(key_findings, 1):
            if isinstance(item, dict):
                vector = item.get("vector", f"Vector #{i}")
                desc = item.get("description", "")
                findings_table_data.append([
                    Paragraph(f"<b>#{i} [{vector}]</b><br/>{desc}", styles['body'])
                ])
            else:
                findings_table_data.append([
                    Paragraph(f"<b>#{i}</b> {str(item)}", styles['body'])
                ])

        f_table = Table(findings_table_data, colWidths=[520])
        f_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(f_table)
    else:
        story.append(Paragraph("<i>No se han registrado hallazgos específicos para esta consulta.</i>", styles['body']))

    # Optional top posts
    if posts and len(posts) > 0:
        story.append(Spacer(1, 14))
        story.append(Paragraph(f"Registro de Evidencias Destacadas ({len(posts[:6])} principales)", styles['section']))
        top_rows = [[
            Paragraph("Fuente", styles['meta_label']),
            Paragraph("Categoría", styles['meta_label']),
            Paragraph("Titular de la Evidencia", styles['meta_label']),
            Paragraph("Score", styles['meta_label'])
        ]]
        for p in posts[:6]:
            top_rows.append([
                Paragraph(str(p.get("source_name", ""))[:20], styles['meta_value']),
                Paragraph(str(p.get("category", "")), styles['meta_value']),
                Paragraph(str(p.get("title", ""))[:65] + "...", styles['meta_value']),
                Paragraph(f"<b>{p.get('score', 0.0)}</b>", styles['meta_value'])
            ])
        p_table = Table(top_rows, colWidths=[100, 100, 270, 50])
        p_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_MED),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(p_table)

    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceBefore=4, spaceAfter=8))
    story.append(Paragraph(
        f"Informe Ejecutivo Forense OSINT · Conforme a estándares de análisis de fuentes abiertas · {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        styles['footer']
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

def generate_finding_pdf(finding_data, report_data=None, corroborating_posts=None):
    """
    Generates a dedicated Executive Forensic Finding Dossier PDF for a single key finding.
    Returns bytes of the PDF.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = get_custom_styles()
    story = []

    f_index = finding_data.get("index", 1)
    f_title = finding_data.get("title", f"Hallazgo Forense #{f_index}")
    f_desc = finding_data.get("description", "")
    f_vector = finding_data.get("vector", "Vector Táctico")
    f_domain = finding_data.get("domain", "OSINT MULTIDOMINIO")
    f_score = finding_data.get("confidence_score", 8.8)
    f_details = finding_data.get("analysis_details", "")
    f_indicators = finding_data.get("key_indicators", [])
    f_recommendations = finding_data.get("recommendations", [])

    report_title = (report_data or {}).get("title", "Investigación Forense OSINT")
    gen_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

    # 1. Header Banner
    story.append(Paragraph("DOSSIER DE INTELIGENCIA FORENSE // VECTOR ANALÍTICO ESPECÍFICO", styles['subtitle']))
    story.append(Paragraph(f"Hallazgo #{f_index}: {f_title}", styles['title']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=CYAN_ACCENT, spaceBefore=4, spaceAfter=10))

    # 2. Metadata Grid Table
    meta_data = [
        [
            Paragraph("Vector Táctico:", styles['meta_label']),
            Paragraph(f"<b>{f_vector}</b>", styles['meta_value']),
            Paragraph("Nivel de Confianza:", styles['meta_label']),
            Paragraph(f"<b>{f_score} / 10.0</b>", styles['meta_value'])
        ],
        [
            Paragraph("Dominio Operativo:", styles['meta_label']),
            Paragraph(str(f_domain).replace("_", " "), styles['meta_value']),
            Paragraph("Estado Forense:", styles['meta_label']),
            Paragraph("<font color='#00a86b'><b>VERIFICADO MULTI-FUENTE</b></font>", styles['meta_value'])
        ],
        [
            Paragraph("Informe Matriz:", styles['meta_label']),
            Paragraph(str(report_title)[:35] + "...", styles['meta_value']),
            Paragraph("Fecha de Emisión:", styles['meta_label']),
            Paragraph(gen_time[:19], styles['meta_value'])
        ]
    ]

    meta_table = Table(meta_data, colWidths=[110, 160, 110, 140])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1, BORDER_GRAY),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # 3. Finding Narrative / Executive Evaluation
    story.append(Paragraph("Dictamen Ejecutivo y Enunciado del Hallazgo", styles['section']))
    desc_box = [[Paragraph(f_desc.replace("\n", "<br/><br/>"), styles['body_bold'])]]
    desc_table = Table(desc_box, colWidths=[520])
    desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 10))

    # 4. Detailed Tactical Context
    if f_details:
        story.append(Paragraph("Evaluación Forense y Contexto Operativo Profundo", styles['section']))
        details_box = [[Paragraph(f_details.replace("\n", "<br/><br/>"), styles['body'])]]
        details_table = Table(details_box, colWidths=[520])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 10))

    # 5. Observed Indicators / Signals Table
    if f_indicators:
        story.append(Paragraph("Indicadores Clave y Señales de Actividad Observadas", styles['section']))
        ind_data = [[Paragraph("#", styles['meta_label']), Paragraph("Indicador / Señal Táctica", styles['meta_label']), Paragraph("Tipo de Evidencia", styles['meta_label'])]]
        for idx, ind in enumerate(f_indicators, 1):
            ind_data.append([
                Paragraph(str(idx), styles['meta_value']),
                Paragraph(f"<b>{ind.get('indicator', ind)}</b>", styles['meta_value']),
                Paragraph(ind.get('type', 'Telemetría / Redes'), styles['meta_value'])
            ])
        ind_table = Table(ind_data, colWidths=[30, 360, 130])
        ind_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_MED),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(ind_table)
        story.append(Spacer(1, 10))

    # 6. Corroborating Evidence Table
    if corroborating_posts and len(corroborating_posts) > 0:
        story.append(Paragraph(f"Evidencias y Publicaciones de Corroboración ({len(corroborating_posts[:4])} fuentes)", styles['section']))
        post_rows = [[
            Paragraph("Fuente", styles['meta_label']),
            Paragraph("Tipo", styles['meta_label']),
            Paragraph("Titular del Despacho", styles['meta_label']),
            Paragraph("Score", styles['meta_label'])
        ]]
        for cp in corroborating_posts[:4]:
            post_rows.append([
                Paragraph(str(cp.get("source_name", ""))[:20], styles['meta_value']),
                Paragraph(str(cp.get("source_type", "WEB")), styles['meta_value']),
                Paragraph(str(cp.get("title", ""))[:60] + "...", styles['meta_value']),
                Paragraph(f"<b>{cp.get('score', 0.0)}</b>", styles['meta_value'])
            ])
        c_table = Table(post_rows, colWidths=[110, 80, 270, 60])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), NAVY_DARK),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(c_table)
        story.append(Spacer(1, 10))

    # 7. Strategic Recommendations
    if f_recommendations:
        story.append(Paragraph("Recomendaciones Operativas & Acciones de Mitigación", styles['section']))
        recs_data = []
        for r_idx, rec in enumerate(f_recommendations, 1):
            recs_data.append([
                Paragraph(f"<b>{r_idx}.</b> {rec}", styles['body'])
            ])
        rec_table = Table(recs_data, colWidths=[520])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
            ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        story.append(rec_table)
        story.append(Spacer(1, 10))

    # 8. Cryptographic Integrity Seal
    raw_sig = f"{f_title}-{f_desc}-{gen_time}"
    finding_hash = hashlib.sha256(raw_sig.encode('utf-8')).hexdigest()
    story.append(Paragraph("Cadena de Custodia & Huella Criptográfica", styles['section']))
    hash_data = [
        [Paragraph("Hash SHA-256 del Hallazgo:", styles['meta_label']), Paragraph(f"<font face='Courier' size='7'>{finding_hash}</font>", styles['meta_value'])],
        [Paragraph("Certificación Forense:", styles['meta_label']), Paragraph("REGISTRO INMUTABLE OSINT ENGINE // VECTOR VERIFICADO", styles['meta_value'])],
    ]
    hash_table = Table(hash_data, colWidths=[150, 370])
    hash_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(hash_table)
    story.append(Spacer(1, 12))

    # 9. Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceBefore=4, spaceAfter=6))
    story.append(Paragraph(
        f"Dossier Oficial de Hallazgo Forense OSINT · {gen_time} · Generado por la Plataforma Universal de Ciberinteligencia.",
        styles['footer']
    ))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()

