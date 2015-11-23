# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER


class TransmittalPdf(object):
    def __init__(self, revision):
        self.buff = BytesIO()
        self.styles = getSampleStyleSheet()
        self.width, self.height = A4
        self.revision = revision
        self.document = revision.document
        self.transmittal = revision.metadata
        self.category = self.document.category
        self.revisions = self.transmittal.exportedrevision_set.select_related()
        self.build_document()

    def build_document(self):
        self.doc = SimpleDocTemplate(
            self.buff,
            pagesize=A4,
            leftMargin=13 * mm,
            rightMargin=13 * mm,
            topMargin=13 * mm,
            bottomtMargin=18 * mm)

        story = [
            Spacer(0, 4 * cm),
            self.build_subtitle(),
            Spacer(0, 6 * mm),
            self.build_trs_meta(),
            Spacer(0, 6 * mm),
            self.build_sender_addressee(),
            Spacer(0, 6 * mm),
            self.build_way_of_transmission(),
            Spacer(0, 6 * mm),
            self.build_revisions_table(),
        ]
        self.doc.build(story, onFirstPage=self.build_header)

    def build_header(self, canvas, doc):
        self.draw_title(canvas)
        self.draw_contract_nb_table(canvas)

    def get_table_style(self):
        style = TableStyle([
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ])
        return style

    def draw_title(self, canvas):
        title = self.category.organisation.name
        p = Paragraph(title, self.styles['Title'])
        p.wrapOn(canvas, 120 * mm, 150 * mm)
        p.drawOn(canvas, *self.coord(13, 55))

    def draw_contract_nb_table(self, canvas):
        data = [
            ('Contract NB', self.transmittal.contract_number),
            ('Phase', ''),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[25 * mm, 25 * mm])
        table.setStyle(self.get_table_style())
        table.wrapOn(canvas, 50 * mm, 50 * mm)
        table.drawOn(canvas, *self.coord(145, 55))

    def build_subtitle(self):
        style = ParagraphStyle(
            name='trs_style',
            parent=self.styles['Heading2'],
            alignment=TA_CENTER,
            borderWidth=1,
            borderColor=colors.black,
            textTransform='uppercase'
        )
        p = Paragraph('Transmittal sheet', style)
        return p

    def build_trs_meta(self):
        data = [
            ('Transmittal Number', self.document.document_key),
            ('Issue Date', self.document.created_on),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[45 * mm, None])
        table.setStyle(self.get_table_style())
        return table

    def build_sender_addressee(self):
        text = 'Sender: {}<br />Addressee: {}'.format(
            'XXX Sender name',
            'YYY Addressee name'
        )
        p = Paragraph(text, self.styles['Normal'])
        return p

    def build_way_of_transmission(self):
        data = [
            ('Way of transmission', ''),
            ('EDMS', 'X'),
            ('Email', ''),
            ('USB Key', ''),
            ('Post', ''),
            ('Other', ''),
        ]
        table = Table(data, hAlign='LEFT', colWidths=[45 * mm, 20 * mm])
        style = self.get_table_style()
        style.add('SPAN', (0, 0), (1, 0))
        style.add('ALIGN', (0, 0), (0, 0), 'CENTER')
        style.add('ALIGN', (1, 0), (1, -1), 'CENTER')
        table.setStyle(style)
        return table

    def build_revisions_table(self):
        style = self.styles['BodyText']
        style.alignment = TA_LEFT
        style.wordWrap = 'LTR'

        header = (
            'Document Number',
            'Title',
            'Rev.',
            'Status',
            'RC')
        data = [header]
        for revision in self.revisions:
            data.append((
                Paragraph(revision.document.document_key, style),
                Paragraph(revision.title, style),
                Paragraph('%s' % revision.revision, style),
                Paragraph(revision.status, style),
                Paragraph(revision.return_code, style)))
        table = Table(
            data,
            hAlign='LEFT',
            colWidths=[45 * mm, 90 * mm, 15 * mm, 15 * mm, 15 * mm])
        table.setStyle(self.get_table_style())
        return table

    def coord(self, x, y, unit=mm):
        """Helper class to computes pdf coordinary

        # http://stackoverflow.com/questions/4726011/wrap-text-in-a-table-reportlab

        """
        x, y = x * unit, self.height - y * unit
        return x, y

    def as_binary(self):
        """Writes the pdf to buffer and returns it as a binary value."""
        pdf_binary = self.buff.getvalue()
        self.buff.close()
        return pdf_binary


def transmittal_to_pdf(revision):
    pdf = TransmittalPdf(revision)
    return pdf.as_binary()
