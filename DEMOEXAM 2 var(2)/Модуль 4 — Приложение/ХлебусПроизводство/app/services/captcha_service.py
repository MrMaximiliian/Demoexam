"""Логика капчи-пазла.

Класс описывает состояние головоломки независимо от способа отрисовки.
Изображение делится на grid_size × grid_size фрагментов. Каждая ячейка
поля хранит идентификатор находящегося в ней фрагмента. Пазл считается
собранным, когда фрагмент с индексом i стоит в ячейке i.
"""

import random


class PuzzleCaptcha:
    def __init__(self, grid_size, rng=None):
        self.grid_size = grid_size
        self.tiles_count = grid_size * grid_size
        self.rng = rng or random.Random()
        self.arrangement = list(range(self.tiles_count))

    def shuffle(self):
        shuffled = list(range(self.tiles_count))
        while True:
            self.rng.shuffle(shuffled)
            if shuffled != list(range(self.tiles_count)):
                break
        self.arrangement = shuffled

    def tile_at(self, cell_index):
        return self.arrangement[cell_index]

    def swap(self, first_cell, second_cell):
        if first_cell == second_cell:
            return
        self.arrangement[first_cell], self.arrangement[second_cell] = (
            self.arrangement[second_cell],
            self.arrangement[first_cell],
        )

    def is_solved(self):
        return self.arrangement == list(range(self.tiles_count))
