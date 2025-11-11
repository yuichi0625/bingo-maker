import abc
from collections.abc import Callable
import functools
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from typing import Any
from typing import Literal

from bingo_maker import utils

ERROR_MESSAGES = {
    'empty': '値を入力してください',
    'not_integer': '整数を入力してください',
    'not_float': '整数か小数を入力してください',
    'too_small': '{from_}以上の値を入力してください',
    'too_big': '{to}以下の値を入力してください',
}
VALIDITY_CHANGED_EVENT = '<<ValidityChanged>>'
BINGO_ITEM_LOADED_EVENT = '<<BingoItemLoaded>>'


class ValidatableFrame(ttk.Frame, abc.ABC):
    def __init__(self, master: tk.Misc, **kwargs: Any) -> None:
        super().__init__(master, **kwargs)
        self._is_valid_var = tk.BooleanVar(value=False)

    def _set_validity(self, is_valid: bool) -> None:
        if self._is_valid_var.get() is not is_valid:
            self._is_valid_var.set(is_valid)
            self.event_generate(VALIDITY_CHANGED_EVENT, when='tail')

    def is_valid(self) -> bool:
        return self._is_valid_var.get()

    @abc.abstractmethod
    def get(self) -> Any:
        raise NotImplementedError

    @abc.abstractmethod
    def enable(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def disable(self) -> None:
        raise NotImplementedError


class LabelEntry(ValidatableFrame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        default: str,
        width: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self._entry_var = tk.StringVar(value=default)
        self._error_message_var = tk.StringVar(value='')
        self._validate(default)

        ttk.Label(self, text=label, anchor='w').grid(
            row=0, column=0, sticky='w'
        )

        self._entry = ttk.Entry(
            self,
            textvariable=self._entry_var,
            width=width,
            validate='key',
            validatecommand=(self.register(self._validate), '%P'),
        )
        self._entry.grid(row=0, column=1, sticky='w')

        ttk.Label(
            self, textvariable=self._error_message_var, foreground='red'
        ).grid(row=0, column=2, sticky='w')

    def _validate(self, proposed: str) -> bool:
        """入力が空かどうか判定する"""
        is_valid = bool(proposed)
        self._set_validity(is_valid)
        self._error_message_var.set(
            '' if is_valid else ERROR_MESSAGES['empty']
        )
        return True  # 空のままにする

    def get(self) -> str:
        return self._entry_var.get()

    def enable(self) -> None:
        self._entry.state(['!disabled'])

    def disable(self) -> None:
        self._entry.state(['disabled'])


class LabelSpinbox(ValidatableFrame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        default: float,
        from_: float,
        to: float,
        increment: float,
        width: int,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self.from_ = from_
        self.to = to
        self._spinbox_var = (
            tk.IntVar(value=int(default))
            if all(n.is_integer() for n in [default, from_, to, increment])
            else tk.DoubleVar(value=default)
        )
        self._error_message_var = tk.StringVar(value='')
        self._validate_on_input(str(default))

        ttk.Label(self, text=label, anchor='w').grid(
            row=0, column=0, sticky='w'
        )

        self._spinbox = ttk.Spinbox(
            self,
            from_=from_,
            to=to,
            increment=increment,
            textvariable=self._spinbox_var,
            width=width,
            validate='key',
            validatecommand=(self.register(self._validate_on_input), '%P'),
            command=self._validate_on_click,
        )
        self._spinbox.grid(row=0, column=1, sticky='w')

        ttk.Label(
            self, textvariable=self._error_message_var, foreground='red'
        ).grid(row=0, column=2, sticky='w')

    def _validate_on_input(self, proposed: str) -> bool:
        # 入力が空
        if not bool(proposed):
            self._set_validity(False)
            self._error_message_var.set(ERROR_MESSAGES['empty'])
            return True  # 空のままにする

        # 入力が数字ではない
        if not utils.is_number(proposed):
            self._error_message_var.set(
                ERROR_MESSAGES[
                    (
                        'not_integer'
                        if isinstance(self._spinbox_var, tk.IntVar)
                        else 'not_float'
                    )
                ]
            )
            return False

        input_ = float(proposed)

        # 入力が整数であってほしい場合に整数ではない
        if (
            isinstance(self._spinbox_var, tk.IntVar)
            and not input_.is_integer()
        ):
            self._error_message_var.set(ERROR_MESSAGES['not_integer'])
            return False

        # 入力が最小値より小さい
        if input_ < self.from_:
            self._error_message_var.set(
                ERROR_MESSAGES['too_small'].format(from_=self.from_)
            )
            self._set_validity(False)
            return True

        # 入力が最大値より大きい
        if input_ > self.to:
            self._error_message_var.set(
                ERROR_MESSAGES['too_big'].format(to=self.to)
            )
            self._set_validity(False)
            return True

        self._set_validity(True)
        self._error_message_var.set('')
        return True

    def _validate_on_click(self) -> None:
        # エラー後の矢印操作でエラーメッセージが消えるようにする
        if self.from_ <= self._spinbox_var.get() <= self.to:
            self._error_message_var.set('')

    def get(self) -> float:
        return self._spinbox_var.get()

    def enable(self) -> None:
        self._spinbox.state(['!disabled'])

    def disable(self) -> None:
        self._spinbox.state(['disabled'])


class LabelCombobox(ValidatableFrame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        default: str,
        values: list[str] | tuple[str, ...],
        **kwargs: Any,
    ):
        super().__init__(master, **kwargs)

        self._set_validity(True)  # バリデーションなし
        self._combobox_var = tk.StringVar(value=default)

        ttk.Label(self, text=label, anchor='w').grid(
            row=0, column=0, sticky='w'
        )

        self._combobox = ttk.Combobox(
            self,
            state='readonly',
            values=values,
            textvariable=self._combobox_var,
        )
        self._combobox.grid(row=0, column=1, sticky='w')

    def get(self) -> str:
        return self._combobox_var.get()

    def enable(self) -> None:
        self._combobox.state(['!disabled'])

    def disable(self) -> None:
        self._combobox.state(['disabled'])


class BooleanSelector(ValidatableFrame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        default: bool,
        true_text: str,
        false_text: str,
        **kwargs: Any,
    ):
        super().__init__(master, **kwargs)

        self._set_validity(True)  # バリデーションなし
        self._radiobutton_var = tk.BooleanVar(value=default)
        self._radiobuttons: dict[str, ttk.Widget] = {}

        ttk.Label(self, text=label, anchor='w').grid(
            row=0, column=0, sticky='w'
        )

        self._radiobuttons['true'] = ttk.Radiobutton(
            self, text=true_text, value=True, variable=self._radiobutton_var
        )
        self._radiobuttons['true'].grid(row=0, column=1, sticky='w')

        self._radiobuttons['false'] = ttk.Radiobutton(
            self, text=false_text, value=False, variable=self._radiobutton_var
        )
        self._radiobuttons['false'].grid(row=0, column=2, sticky='w')

    def get(self) -> bool:
        return self._radiobutton_var.get()

    def enable(self) -> None:
        for button_type in ['true', 'false']:
            self._radiobuttons[button_type].state(['!disabled'])

    def disable(self) -> None:
        for button_type in ['true', 'false']:
            self._radiobuttons[button_type].state(['disabled'])

    def enable_option(self, button_type: Literal['true', 'false']) -> None:
        self._radiobuttons[button_type].state(['!disabled'])

    def disable_option(self, button_type: Literal['true', 'false']) -> None:
        self._radiobuttons[button_type].state(['disabled'])
        self._radiobutton_var.set(True if button_type == 'false' else False)


class BingoItemFileLoader(ValidatableFrame):
    def __init__(
        self,
        master: tk.Misc,
        label: str,
        button_text: str,
        window_title: str,
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self._items: list[str] = []
        self._status_message_var = tk.StringVar(
            value='ファイルが読み込まれていません'
        )

        ttk.Label(self, text=label, anchor='w').grid(
            row=0, column=0, sticky='w'
        )

        self._button = ttk.Button(
            self,
            text=button_text,
            command=functools.partial(
                self._on_button_click, title=window_title
            ),
        )
        self._button.grid(row=0, column=1, sticky='w')

        ttk.Label(self, textvariable=self._status_message_var).grid(
            row=1, column=1, sticky='w'
        )

    def _on_button_click(self, title: str) -> None:
        file_path = filedialog.askopenfilename(
            parent=self, title=title, filetypes=[('テキストファイル', '*.txt')]
        )
        if not file_path:
            return

        self._items = self._load_items_from_file(file_path)
        self._status_message_var.set(
            f'{os.path.basename(file_path)}：{len(self._items)}種類'
        )
        self._set_validity(True)
        self.event_generate(BINGO_ITEM_LOADED_EVENT, when='tail')

    @staticmethod
    def _load_items_from_file(file_path: str) -> list[str]:
        with open(file_path, encoding='utf-8') as f:
            items = (line.strip() for line in f.readlines())
            return sorted(
                {item for item in items if item and not item.startswith('#')}
            )

    def get(self) -> list[str]:
        return self._items

    def enable(self) -> None:
        self._button.state(['!disabled'])

    def disable(self) -> None:
        self._button.state(['disabled'])


class Button(ValidatableFrame):
    def __init__(
        self,
        master: tk.Misc,
        text: str,
        state: str,
        command: Callable[[], None],
        sticky: str = '',
        **kwargs: Any,
    ) -> None:
        super().__init__(master, **kwargs)

        self._set_validity(True)

        self._button = ttk.Button(
            self, text=text, state=state, command=command
        )
        self._button.grid(row=0, column=0, sticky=sticky)

    def get(self) -> None:
        return None

    def enable(self) -> None:
        self._button.state(['!disabled'])

    def disable(self) -> None:
        self._button.state(['disabled'])
