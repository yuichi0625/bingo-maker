import dataclasses
import random


@dataclasses.dataclass
class BingoData:
    title: str
    items: list[str]
    allow_duplicates: bool = False

    def pick_cell_items(self, cell_size: int) -> list[str]:
        n = cell_size**2
        return (
            random.choices
            if self.allow_duplicates or len(self.items) < n
            else random.sample
        )(self.items, k=n)


@dataclasses.dataclass
class BingoLayoutSpec:
    page_w: float
    page_h: float
    card_size: int
    cell_size: int
    margin_ratio: float
    font_type: str
    title_font_size: float
    item_font_size: float

    card_w: float = dataclasses.field(init=False)
    card_h: float = dataclasses.field(init=False)
    margin_w: float = dataclasses.field(init=False)
    margin_h: float = dataclasses.field(init=False)
    grid_w: float = dataclasses.field(init=False)
    grid_h: float = dataclasses.field(init=False)
    cell_w: float = dataclasses.field(init=False)
    cell_h: float = dataclasses.field(init=False)

    def __post_init__(self):
        self.card_w = self.page_w / self.card_size
        self.card_h = self.page_h / self.card_size
        self.margin_w = self.card_w * self.margin_ratio
        self.margin_h = self.card_h * self.margin_ratio
        self.grid_w = self.card_w - 2 * self.margin_w
        self.grid_h = (
            self.card_h - 2 * self.margin_h - self.title_font_size * 1.4
        )
        self.cell_w = self.grid_w / self.cell_size
        self.cell_h = self.grid_h / self.cell_size
