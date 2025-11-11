"""
https://www.begueradj.com/tkinter-best-practices/
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import messagebox
from tkinter import ttk
from typing import Any

from bingo_maker import utils
from bingo_maker.pdf import models
from bingo_maker.pdf import renderer
from bingo_maker.ui import widgets


class BingoMaker(ttk.Frame):
    def __init__(
        self,
        parent: tk.Tk,
        app_title: str,
        app_geometry: str,
        app_font_size: int,
        app_padx: float,
        app_pady: float,
        bingo_page_width: float,
        bingo_page_height: float,
        bingo_margin_ratio: float,
        bingo_font_types: list[str],
        **kwargs: Any
    ):
        super().__init__(parent, **kwargs)
        self.parent = parent

        self.bingo_page_width = bingo_page_width
        self.bingo_page_height = bingo_page_height
        self.bingo_margin_ratio = bingo_margin_ratio

        self._configure_gui(
            title=app_title, geometry=app_geometry, font_size=app_font_size
        )
        self._create_widgets(
            padx=app_padx, pady=app_pady, font_types=bingo_font_types
        )

    def _configure_gui(
        self, title: str, geometry: str, font_size: int
    ) -> None:
        self.parent.title(title)
        self.parent.geometry(geometry)
        self.parent.resizable(False, False)

        tkfont.nametofont('TkDefaultFont').configure(size=font_size)
        tkfont.nametofont('TkTextFont').configure(size=font_size)

    def _create_widgets(self, padx: float, pady: float, font_types: list[str]):
        row_id = 0
        self.fields: dict[str, ttk.Frame] = {}

        self.fields['title'] = widgets.LabelEntry(
            self, label='タイトル：', default='ビンゴカード', width=20
        )
        self.fields['title'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['card_size'] = widgets.LabelSpinbox(
            self,
            label='一辺あたりのカードの数：',
            default=2,
            from_=1,
            to=10,
            increment=1,
            width=4,
        )
        self.fields['card_size'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['cell_size'] = widgets.LabelSpinbox(
            self,
            label='一辺あたりのマスの数：',
            default=5,
            from_=2,
            to=10,
            increment=1,
            width=4,
        )
        self.fields['cell_size'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['num_pages'] = widgets.LabelSpinbox(
            self,
            label='ページ数：',
            default=2,
            from_=1,
            to=100,
            increment=1,
            width=4,
        )
        self.fields['num_pages'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['bingo_items'] = widgets.BingoItemFileLoader(
            self,
            label='ビンゴの中身：',
            button_text='ファイルを選択する',
            window_title='ビンゴの中身が記載されたテキストファイルを選択',
        )
        self.fields['bingo_items'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['allow_duplicates'] = widgets.BooleanSelector(
            self,
            label='中身の重複：',
            default=False,
            true_text='あり',
            false_text='なし',
        )
        self.fields['allow_duplicates'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['font_type'] = widgets.LabelCombobox(
            self,
            label='フォントの種類：',
            default=next(
                (ft for ft in font_types if 'regular' in ft.lower()),
                font_types[0],
            ),
            values=font_types,
        )
        self.fields['font_type'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['title_font_size'] = widgets.LabelSpinbox(
            self,
            label='タイトルのフォントの大きさ：',
            default=20.0,
            from_=0.5,
            to=50,
            increment=0.5,
            width=6,
        )
        self.fields['title_font_size'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['item_font_size'] = widgets.LabelSpinbox(
            self,
            label='中身のフォントの大きさ：',
            default=10.0,
            from_=0.5,
            to=50,
            increment=0.5,
            width=6,
        )
        self.fields['item_font_size'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['output_path'] = widgets.LabelEntry(
            self,
            label='出力ファイル名：',
            default='outputs/bingo.pdf',
            width=20,
        )
        self.fields['output_path'].grid(
            row=row_id, column=0, sticky='w', padx=padx, pady=pady
        )
        row_id += 1

        self.fields['create_bingo'] = widgets.Button(
            self,
            text='ビンゴを作成する',
            state='disabled',
            command=self._on_render_bingo_button_click,
        )
        self.fields['create_bingo'].grid(
            row=row_id, column=0, sticky='ew', padx=padx, pady=pady
        )

        self.parent.bind(
            widgets.BINGO_ITEM_LOADED_EVENT, self._on_bingo_item_loaded
        )
        self.parent.bind(
            widgets.VALIDITY_CHANGED_EVENT, self._on_validity_changed
        )
        self.after_idle(self._align_first_columns)

    def _on_render_bingo_button_click(self) -> None:
        for frame in self.fields.values():
            frame.disable()

        renderer.render_bingo_pdf(
            num_pages=self.fields['num_pages'].get(),
            data=models.BingoData(
                title=self.fields['title'].get(),
                items=self.fields['bingo_items'].get(),
                allow_duplicates=self.fields['allow_duplicates'].get(),
            ),
            spec=models.BingoLayoutSpec(
                page_w=self.bingo_page_width,
                page_h=self.bingo_page_height,
                card_size=self.fields['card_size'].get(),
                cell_size=self.fields['cell_size'].get(),
                margin_ratio=self.bingo_margin_ratio,
                font_type=self.fields['font_type'].get(),
                title_font_size=self.fields['title_font_size'].get(),
                item_font_size=self.fields['item_font_size'].get(),
            ),
            output_path=utils.resolve_output_path(
                self.fields['output_path'].get()
            ),
        )

        messagebox.showinfo('完了', 'PDFが作成されました。')

        for frame in self.fields.values():
            frame.enable()

    def _on_bingo_item_loaded(self, event: tk.Event) -> None:
        if len(event.widget.get()) < self.fields['cell_size'].get() ** 2:
            self.fields['allow_duplicates'].disable_option('false')
        else:
            self.fields['allow_duplicates'].enable_option('false')

    def _on_validity_changed(self, event: tk.Event) -> None:
        if all([frame.is_valid() for frame in self.fields.values()]):
            self.fields['create_bingo'].enable()
        else:
            self.fields['create_bingo'].disable()

    def _align_first_columns(self) -> None:
        for frame in self.fields.values():
            frame.update_idletasks()

        max_1st_col_width = 0
        max_2nd_col_width = 0
        for frame in self.fields.values():
            for child in frame.winfo_children():
                info = child.grid_info()
                if int(info['column']) == 0:
                    max_1st_col_width = max(
                        max_1st_col_width, child.winfo_reqwidth()
                    )
                elif int(info['column']) == 1:
                    max_2nd_col_width = max(
                        max_2nd_col_width, child.winfo_reqwidth()
                    )

        for key, frame in self.fields.items():
            size = (
                max_1st_col_width + max_2nd_col_width
                if key == 'create_bingo'
                else max_1st_col_width
            )
            frame.grid_columnconfigure(0, minsize=size)
