from collections.abc import Generator
import pathlib
import re

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas

from . import models


class TextBlockAligner:
    def __init__(
        self, font_size: float, font_type: str, leading_factor: float = 1.2
    ) -> None:
        self.leading = font_size * leading_factor
        self.ascent = pdfmetrics.getAscent(font_type) * font_size / 1000
        self.descent = abs(pdfmetrics.getDescent(font_type) * font_size / 1000)

    def compute_line_y_positions(
        self, line_count: int, center_y: float
    ) -> Generator[float]:
        block_h = self.ascent + (line_count - 1) * self.leading + self.descent
        baseline = center_y + block_h / 2.0 - self.ascent
        for i in range(line_count):
            yield baseline - i * self.leading


def render_bingo_pdf(
    num_pages: int,
    data: models.BingoData,
    spec: models.BingoLayoutSpec,
    output_path: str | pathlib.Path,
) -> None:
    c = canvas.Canvas(str(output_path), pagesize=(spec.page_w, spec.page_h))

    for _ in range(num_pages):
        c.setStrokeColor(colors.black)
        c.setLineWidth(1)
        _draw_bingo_cards(c, data, spec)
        c.showPage()

    c.save()


def _draw_bingo_cards(
    c: canvas.Canvas, data: models.BingoData, spec: models.BingoLayoutSpec
) -> None:
    for card_xi in range(spec.card_size):
        origin_x = spec.card_w * card_xi
        for card_yi in range(spec.card_size):
            origin_y = spec.card_h * card_yi
            _draw_bingo_card(c, data, spec, origin_x, origin_y)


def _draw_bingo_card(
    c: canvas.Canvas,
    data: models.BingoData,
    spec: models.BingoLayoutSpec,
    origin_x: float,
    origin_y: float,
) -> None:
    c.setFont(spec.font_type, spec.title_font_size)
    c.drawCentredString(
        origin_x + spec.card_w / 2,
        origin_y + spec.card_h - spec.margin_h - spec.title_font_size,
        data.title,
    )
    c.setFont(spec.font_type, spec.item_font_size)

    c.rect(
        origin_x + spec.margin_w,
        origin_y + spec.margin_h,
        spec.grid_w,
        spec.grid_h,
        fill=False,
    )
    for i in range(spec.cell_size + 1):
        x = origin_x + spec.margin_w + i * spec.cell_w
        c.line(
            x,
            origin_y + spec.margin_h,
            x,
            origin_y + spec.margin_h + spec.grid_h,
        )
        y = origin_y + spec.margin_h + i * spec.cell_h
        c.line(
            origin_x + spec.margin_w,
            y,
            origin_x + spec.margin_w + spec.grid_w,
            y,
        )

    aligner = TextBlockAligner(spec.item_font_size, spec.font_type)
    items = data.pick_cell_items(spec.cell_size)
    for xi in range(spec.cell_size):
        x = origin_x + spec.margin_w + spec.cell_w / 2 + xi * spec.cell_w
        for yi in range(spec.cell_size):
            y = origin_y + spec.margin_h + spec.cell_h / 2 + yi * spec.cell_h

            lines = re.split(r'[\\/]+', items[xi * spec.cell_size + yi])
            aligned_ys = aligner.compute_line_y_positions(len(lines), y)
            for line, aligned_y in zip(lines, aligned_ys):
                c.drawCentredString(x, aligned_y, line)
