import csv
import json
import io
import logging
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger(__name__)


class ReportGeneratorService:
    """
    Generates contract audit reports in PDF, CSV, and JSON formats.
    """

    @staticmethod
    def generate_json_report(document):
        meta = getattr(document, 'metadata', None)
        risk = getattr(document, 'risk_analysis', None)

        data = {
            'platform': 'LexVision AI – Contract Intelligence Platform',
            'contract_id': document.id,
            'title': document.title,
            'status': document.get_status_display(),
            'uploaded_at': document.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'file_size': document.formatted_size(),
            'page_count': document.page_count,
            'metadata': {
                'companies': getattr(meta, 'company_names', []) if meta else [],
                'contract_parties': getattr(meta, 'contract_parties', []) if meta else [],
                'effective_date': getattr(meta, 'effective_date', 'N/A') if meta else 'N/A',
                'expiration_date': getattr(meta, 'expiration_date', 'N/A') if meta else 'N/A',
                'duration': getattr(meta, 'contract_duration', 'N/A') if meta else 'N/A',
                'governing_law': getattr(meta, 'governing_law', 'N/A') if meta else 'N/A',
                'jurisdiction': getattr(meta, 'jurisdiction', 'N/A') if meta else 'N/A',
            },
            'risk_analysis': {
                'overall_risk_score': risk.overall_risk_score if risk else 0,
                'risk_level': risk.risk_level if risk else 'N/A',
                'summary': risk.risk_summary if risk else 'N/A',
                'detected_risk_clauses': [
                    {
                        'title': item.title,
                        'severity': item.severity,
                        'explanation': item.explanation,
                        'highlighted_text': item.highlighted_text,
                        'recommendation': item.recommendation
                    } for item in (risk.risk_items.all() if risk else [])
                ]
            },
            'categorized_clauses': [
                {
                    'clause_type': clause.get_clause_type_display(),
                    'page_number': clause.page_number,
                    'text': clause.text,
                    'confidence_score': clause.confidence_score
                } for clause in (document.clauses.all() if hasattr(document, 'clauses') else [])
            ]
        }
        return json.dumps(data, indent=2)

    @staticmethod
    def generate_csv_report(document):
        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(['LEXVISION AI CONTRACT AUDIT REPORT'])
        writer.writerow([])
        writer.writerow(['Contract Title', document.title])
        writer.writerow(['Contract ID', document.id])
        writer.writerow(['Status', document.get_status_display()])
        writer.writerow(['Uploaded At', document.created_at.strftime('%Y-%m-%d %H:%M:%S')])
        
        risk = getattr(document, 'risk_analysis', None)
        if risk:
            writer.writerow(['Overall Risk Score', f"{risk.overall_risk_score}/100"])
            writer.writerow(['Risk Level', risk.risk_level])

        meta = getattr(document, 'metadata', None)
        if meta:
            writer.writerow([])
            writer.writerow(['METADATA EXTRACTION'])
            writer.writerow(['Companies', ", ".join(meta.company_names)])
            writer.writerow(['Governing Law', meta.governing_law])
            writer.writerow(['Jurisdiction', meta.jurisdiction])
            writer.writerow(['Effective Date', meta.effective_date])
            writer.writerow(['Expiration Date', meta.expiration_date])
            writer.writerow(['Duration', meta.contract_duration])

        if risk and risk.risk_items.exists():
            writer.writerow([])
            writer.writerow(['DETECTED RISK FLAGS'])
            writer.writerow(['Severity', 'Title', 'Explanation', 'Recommendation', 'Snippet'])
            for item in risk.risk_items.all():
                writer.writerow([item.severity, item.title, item.explanation, item.recommendation, item.highlighted_text])

        return output.getvalue()

    @staticmethod
    def generate_pdf_report(document):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        story = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            leading=26,
            textColor=colors.HexColor('#0f52ba')
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#6c757d')
        )
        h2_style = ParagraphStyle(
            'H2Style',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyStyle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#334155')
        )

        # Header
        story.append(Paragraph("LexVision AI – Contract Intelligence Report", title_style))
        story.append(Paragraph(f"Generated for <b>{document.title}</b> | ID #{document.id}", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0'), spaceAfter=15))

        # Risk Summary Card Table
        risk = getattr(document, 'risk_analysis', None)
        score_str = f"{risk.overall_risk_score}/100 ({risk.risk_level})" if risk else "N/A"
        
        summary_data = [
            [Paragraph("<b>Overall Risk Score</b>", body_style), Paragraph(f"<font color='#0f52ba'><b>{score_str}</b></font>", body_style)],
            [Paragraph("<b>Contract Status</b>", body_style), Paragraph(document.get_status_display(), body_style)],
            [Paragraph("<b>Page Count / Size</b>", body_style), Paragraph(f"{document.page_count} Pages ({document.formatted_size()})", body_style)],
            [Paragraph("<b>Uploaded Date</b>", body_style), Paragraph(document.created_at.strftime('%B %d, %Y'), body_style)],
        ]
        
        summary_table = Table(summary_data, colWidths=[150, 380])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 15))

        # Metadata Section
        meta = getattr(document, 'metadata', None)
        if meta:
            story.append(Paragraph("Extracted Contract Metadata", h2_style))
            meta_data = [
                [Paragraph("<b>Governing Law:</b>", body_style), Paragraph(meta.governing_law or "N/A", body_style)],
                [Paragraph("<b>Jurisdiction:</b>", body_style), Paragraph(meta.jurisdiction or "N/A", body_style)],
                [Paragraph("<b>Effective Date:</b>", body_style), Paragraph(meta.effective_date or "N/A", body_style)],
                [Paragraph("<b>Expiration Date:</b>", body_style), Paragraph(meta.expiration_date or "N/A", body_style)],
                [Paragraph("<b>Contract Duration:</b>", body_style), Paragraph(meta.contract_duration or "N/A", body_style)],
                [Paragraph("<b>Companies Identified:</b>", body_style), Paragraph(", ".join(meta.company_names) if meta.company_names else "N/A", body_style)],
            ]
            meta_table = Table(meta_data, colWidths=[150, 380])
            meta_table.setStyle(TableStyle([
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
                ('PADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(meta_table)
            story.append(Spacer(1, 15))

        # Risk Flags Section
        if risk and risk.risk_items.exists():
            story.append(Paragraph("Detected Legal Risk Flags & Recommendations", h2_style))
            for item in risk.risk_items.all():
                flag_text = f"<b>[{item.severity}] {item.title}</b><br/>" \
                            f"<b>Issue:</b> {item.explanation}<br/>" \
                            f"<b>Snippet:</b> <i>\"{item.highlighted_text}\"</i><br/>" \
                            f"<b>Recommendation:</b> <font color='#0f52ba'>{item.recommendation}</font>"
                
                story.append(Paragraph(flag_text, body_style))
                story.append(Spacer(1, 8))

        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        return pdf_data
