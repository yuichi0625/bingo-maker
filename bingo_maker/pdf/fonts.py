import pathlib

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import ttfonts

from bingo_maker import utils


def register_jp_fonts_in_dir(relative_path: str) -> list[str]:
    dir_path = utils.resolve_resource_path(relative_path)

    registered: list[str] = []
    for file_path in dir_path.rglob('*.[ot]tf'):
        _register_jp_font(file_path, registered)

    return sorted(registered)


def _register_jp_font(file_path: pathlib.Path, registered: list[str]) -> None:
    pdfmetrics.registerFont(ttfonts.TTFont(file_path.stem, str(file_path)))
    registered.append(file_path.stem)
