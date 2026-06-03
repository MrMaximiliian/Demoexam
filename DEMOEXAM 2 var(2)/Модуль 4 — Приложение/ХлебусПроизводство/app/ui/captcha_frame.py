"""Визуальный компонент капчи-пазла.

Компонент отображает исходное изображение, разбитое на фрагменты, которые
пользователь перетаскивает мышью, меняя их местами. Состояние головоломки
хранит класс PuzzleCaptcha, а данный компонент отвечает только за отрисовку
и обработку перетаскивания.
"""

import os
import tkinter as tk
from tkinter import ttk

from app import config
from app.services import PuzzleCaptcha
from app.ui import app_theme


class CaptchaFrame(ttk.Frame):
    def __init__(self, master, on_solved=None):
        super().__init__(master, style="Surface.TFrame")
        self.on_solved = on_solved
        self.grid_size = config.CAPTCHA_GRID_SIZE
        self.puzzle = PuzzleCaptcha(self.grid_size)

        self._source = self._load_source_image()
        self.board_size = self._source.width()
        self.tile_size = self.board_size // self.grid_size
        self._tiles = self._slice_tiles()

        self._cell_items = {}
        self._drag_cell = None
        self._drag_item = None
        self._drag_offset = (0, 0)
        self._solved_notified = False

        self._build_widgets()
        self.shuffle()

    def _load_source_image(self):
        if not os.path.exists(config.CAPTCHA_IMAGE):
            raise FileNotFoundError(
                "Изображение капчи не найдено: {0}".format(config.CAPTCHA_IMAGE)
            )
        return tk.PhotoImage(file=config.CAPTCHA_IMAGE)

    def _slice_tiles(self):
        tiles = []
        for row in range(self.grid_size):
            for column in range(self.grid_size):
                left = column * self.tile_size
                top = row * self.tile_size
                fragment = tk.PhotoImage(width=self.tile_size, height=self.tile_size)
                fragment.tk.call(
                    fragment, "copy", self._source,
                    "-from", left, top, left + self.tile_size, top + self.tile_size,
                    "-to", 0, 0,
                )
                tiles.append(fragment)
        return tiles

    def _build_widgets(self):
        instruction = ttk.Label(
            self,
            text="Соберите изображение: перетащите фрагменты на свои места",
            style="Hint.TLabel",
            wraplength=self.board_size,
        )
        instruction.grid(row=0, column=0, sticky="w", pady=(0, 6))

        self.canvas = tk.Canvas(
            self, width=self.board_size, height=self.board_size,
            highlightthickness=1, highlightbackground=app_theme.BORDER,
            cursor="hand2", background=app_theme.SURFACE,
        )
        self.canvas.grid(row=1, column=0)
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_drop)

        controls = ttk.Frame(self, style="Surface.TFrame")
        controls.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        controls.columnconfigure(0, weight=1)

        self.status_label = ttk.Label(
            controls, text="Пазл не собран", style="Error.TLabel"
        )
        self.status_label.grid(row=0, column=0, sticky="w")

        ttk.Button(controls, text="Перемешать", command=self.shuffle).grid(
            row=0, column=1, sticky="e"
        )

    def shuffle(self):
        self.puzzle.shuffle()
        self._solved_notified = False
        self._render()
        self._update_status()

    def is_solved(self):
        return self.puzzle.is_solved()

    def _cell_origin(self, cell_index):
        row, column = divmod(cell_index, self.grid_size)
        return column * self.tile_size, row * self.tile_size

    def _cell_from_point(self, x, y):
        if x < 0 or y < 0 or x >= self.board_size or y >= self.board_size:
            return None
        column = int(x // self.tile_size)
        row = int(y // self.tile_size)
        return row * self.grid_size + column

    def _render(self):
        self.canvas.delete("all")
        self._cell_items = {}
        for cell_index in range(self.puzzle.tiles_count):
            tile_id = self.puzzle.tile_at(cell_index)
            origin_x, origin_y = self._cell_origin(cell_index)
            item = self.canvas.create_image(
                origin_x, origin_y, anchor="nw", image=self._tiles[tile_id]
            )
            self._cell_items[cell_index] = item
        self._draw_grid()
        if self.puzzle.is_solved():
            self.canvas.create_rectangle(
                1, 1, self.board_size - 1, self.board_size - 1,
                outline="#2E7D32", width=4,
            )

    def _draw_grid(self):
        for index in range(1, self.grid_size):
            offset = index * self.tile_size
            self.canvas.create_line(offset, 0, offset, self.board_size,
                                    fill="#FFFFFF")
            self.canvas.create_line(0, offset, self.board_size, offset,
                                    fill="#FFFFFF")

    def _on_press(self, event):
        cell_index = self._cell_from_point(event.x, event.y)
        if cell_index is None:
            return
        self._drag_cell = cell_index
        self._drag_item = self._cell_items[cell_index]
        origin_x, origin_y = self._cell_origin(cell_index)
        self._drag_offset = (event.x - origin_x, event.y - origin_y)
        self.canvas.tag_raise(self._drag_item)

    def _on_drag(self, event):
        if self._drag_item is None:
            return
        offset_x, offset_y = self._drag_offset
        self.canvas.coords(self._drag_item, event.x - offset_x, event.y - offset_y)

    def _on_drop(self, event):
        if self._drag_item is None:
            return
        target_cell = self._cell_from_point(event.x, event.y)
        if target_cell is not None and target_cell != self._drag_cell:
            self.puzzle.swap(self._drag_cell, target_cell)
        self._drag_cell = None
        self._drag_item = None
        self._render()
        self._update_status()

    def _update_status(self):
        if self.puzzle.is_solved():
            self.status_label.configure(text="Изображение собрано", style="Success.TLabel")
            if not self._solved_notified and self.on_solved is not None:
                self._solved_notified = True
                self.on_solved()
        else:
            self.status_label.configure(text="Пазл не собран", style="Error.TLabel")
