import tkinter as tk

from reportlab.lib import pagesizes

from bingo_maker.pdf import fonts
from bingo_maker.ui import view


def main() -> None:
    font_types = fonts.register_jp_fonts_in_dir('fonts')

    root = tk.Tk()
    view.BingoMaker(
        root,
        app_title='ビンゴメーカー',
        app_geometry='600x480',
        app_font_size=14,
        app_padx=0,
        app_pady=4,
        bingo_page_width=pagesizes.A4[0],
        bingo_page_height=pagesizes.A4[1],
        bingo_margin_ratio=0.05,
        bingo_font_types=font_types,
    ).pack(anchor='nw')
    root.mainloop()


if __name__ == '__main__':
    main()
