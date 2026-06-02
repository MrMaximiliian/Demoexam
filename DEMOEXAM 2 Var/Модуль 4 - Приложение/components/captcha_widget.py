# -*- coding: utf-8 -*-
# Интерактивная капча-пазл.
# Исходное изображение разрезается на 9 фрагментов (3x3) и перемешивается.
# Пользователь меняет фрагменты местами нажатием на два из них. Когда
# порядок совпадает с исходным, капча считается собранной.

import random
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

GRID = 3
TILE = 70
SIZE = GRID * TILE


def _create_source_image():
    """Создаёт исходное изображение пазла (цветные клетки с номерами)."""
    image = Image.new("RGB", (SIZE, SIZE))
    draw = ImageDraw.Draw(image)
    colors = [(46, 94, 140), (52, 152, 219), (26, 188, 156),
              (241, 196, 15), (230, 126, 34), (231, 76, 60),
              (155, 89, 182), (52, 73, 94), (149, 165, 166)]
    index = 0
    for row in range(GRID):
        for column in range(GRID):
            x = column * TILE
            y = row * TILE
            draw.rectangle([x, y, x + TILE, y + TILE], fill=colors[index])
            draw.text((x + TILE // 2 - 4, y + TILE // 2 - 8),
                      str(index + 1), fill="white")
            index += 1
    return image


class CaptchaWidget(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bd=1, relief="solid")
        self.source_image = _create_source_image()
        self.tiles = []
        self.order = list(range(GRID * GRID))
        self.selected_position = None
        self.buttons = []
        self._cut_tiles()
        self._build_widgets()
        self.shuffle()

    def _cut_tiles(self):
        self.tiles = []
        for row in range(GRID):
            for column in range(GRID):
                box = (column * TILE, row * TILE,
                       (column + 1) * TILE, (row + 1) * TILE)
                fragment = self.source_image.crop(box)
                self.tiles.append(ImageTk.PhotoImage(fragment))

    def _build_widgets(self):
        grid_frame = tk.Frame(self)
        grid_frame.pack(padx=5, pady=5)
        for position in range(GRID * GRID):
            button = tk.Button(
                grid_frame,
                command=lambda pos=position: self._on_tile_click(pos))
            button.grid(row=position // GRID, column=position % GRID)
            self.buttons.append(button)
        tk.Button(self, text="Перемешать", command=self.shuffle).pack(pady=(0, 5))

    def shuffle(self):
        """Перемешивает фрагменты так, чтобы пазл не оказался уже собранным."""
        self.order = list(range(GRID * GRID))
        while self.order == list(range(GRID * GRID)):
            random.shuffle(self.order)
        self.selected_position = None
        self._redraw()

    def _on_tile_click(self, position):
        if self.selected_position is None:
            self.selected_position = position
            self.buttons[position].config(relief="sunken")
        else:
            first = self.selected_position
            self.order[first], self.order[position] = \
                self.order[position], self.order[first]
            self.buttons[first].config(relief="raised")
            self.selected_position = None
            self._redraw()

    def _redraw(self):
        for position in range(GRID * GRID):
            self.buttons[position].config(
                image=self.tiles[self.order[position]], relief="raised")

    def is_solved(self):
        return self.order == list(range(GRID * GRID))
