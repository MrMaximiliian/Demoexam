# -*- coding: utf-8 -*-
# ДЕМО-ВЕРСИЯ для запуска на Mac/Linux без SQL Server.
# Пользователи хранятся в памяти. Нужен только Python 3 и Pillow
# (pip3 install Pillow). Логика входа, пазл, блокировка и панель
# администратора повторяют экзаменационную версию (Модуль 4).
#
# Запуск:  python3 demo.py
# Учётки:  admin / admin   и   user / user

import random
import tkinter as tk
from tkinter import ttk, messagebox

from PIL import Image, ImageDraw, ImageTk

# ===== Настройки (аналог config.py) =====
COMPANY_NAME = "Молочный комбинат «Полесье»"
APP_TITLE = f"ИС «{COMPANY_NAME}»"
LOGIN_MAX_LENGTH = 50
MAX_LOGIN_ATTEMPTS = 3

WRONG_CREDENTIALS_MESSAGE = ("Вы ввели неверный логин или пароль. "
                             "Пожалуйста проверьте ещё раз введенные данные.")
BLOCKED_MESSAGE = "Вы заблокированы. Обратитесь к администратору."
ROLES = ["Администратор", "Пользователь"]


# ===== Сущность «Пользователь» (аналог models/user.py) =====
class User:
    def __init__(self, user_id, login, password, role,
                 blocked=False, attempts=0):
        self.user_id = user_id
        self.login = login
        self.password = password
        self.role = role
        self.blocked = blocked
        self.attempts = attempts

    def is_admin(self):
        return self.role == "Администратор"


# ===== Репозиторий в памяти (аналог database/user_repository.py) =====
class InMemoryUserRepository:
    def __init__(self):
        self._users = [
            User(1, "admin", "admin", "Администратор"),
            User(2, "user", "user", "Пользователь"),
        ]
        self._next_id = 3

    def find_by_login(self, login):
        for user in self._users:
            if user.login == login:
                return user
        return None

    def register_failed_attempt(self, user):
        user.attempts += 1
        if user.attempts >= MAX_LOGIN_ATTEMPTS:
            user.blocked = True
        return user.blocked

    def reset_attempts(self, user):
        user.attempts = 0

    def get_all(self):
        return list(self._users)

    def exists(self, login):
        return self.find_by_login(login) is not None

    def add(self, login, password, role):
        self._users.append(User(self._next_id, login, password, role))
        self._next_id += 1

    def update(self, user):
        if not user.blocked:
            user.attempts = 0


# ===== Капча-пазл (аналог components/captcha_widget.py) =====
GRID = 3
TILE = 70
SIZE = GRID * TILE


def _create_source_image():
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
        tk.Button(self, text="Перемешать",
                  command=self.shuffle).pack(pady=(0, 5))

    def shuffle(self):
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


# ===== Окно добавления/изменения пользователя (аналог user_dialog.py) =====
class UserDialog(tk.Toplevel):
    def __init__(self, master, repository, user=None):
        super().__init__(master)
        self.master = master
        self.repository = repository
        self.editable_user = user
        is_new = user is None
        self.title("Новый пользователь" if is_new else "Изменение пользователя")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()
        self._build_widgets()

    def _build_widgets(self):
        length_validator = (self.register(self._limit_length), "%P", "%d")
        form = tk.Frame(self, padx=15, pady=15)
        form.pack()

        tk.Label(form, text="Логин:").grid(row=0, column=0, sticky="e", pady=4)
        self.login_entry = tk.Entry(form, width=25, validate="key",
                                    validatecommand=length_validator)
        self.login_entry.grid(row=0, column=1, pady=4)

        tk.Label(form, text="Пароль:").grid(row=1, column=0, sticky="e", pady=4)
        self.password_entry = tk.Entry(form, width=25, validate="key",
                                       validatecommand=length_validator)
        self.password_entry.grid(row=1, column=1, pady=4)

        tk.Label(form, text="Роль:").grid(row=2, column=0, sticky="e", pady=4)
        self.role_box = ttk.Combobox(form, width=22, state="readonly",
                                     values=ROLES)
        self.role_box.grid(row=2, column=1, pady=4)
        self.role_box.current(1)

        self.blocked_var = tk.IntVar()
        blocked_checkbox = tk.Checkbutton(form, text="Заблокирован",
                                          variable=self.blocked_var)

        if self.editable_user is not None:
            self.login_entry.insert(0, self.editable_user.login)
            self.password_entry.insert(0, self.editable_user.password)
            self.role_box.set(self.editable_user.role)
            self.blocked_var.set(1 if self.editable_user.blocked else 0)
            blocked_checkbox.grid(row=3, column=1, sticky="w", pady=4)

        tk.Button(form, text="Сохранить", width=20,
                  command=self.save).grid(row=4, column=0, columnspan=2,
                                          pady=(10, 0))
        self.login_entry.focus_set()

    def _limit_length(self, proposed_value, action):
        if action != "1":
            return True
        return len(proposed_value) <= LOGIN_MAX_LENGTH

    def save(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_box.get()

        if not login or not password:
            messagebox.showwarning(
                "Внимание", "Поля «Логин» и «Пароль» обязательны для заполнения.")
            return

        if self.editable_user is None:
            if self.repository.exists(login):
                messagebox.showerror(
                    "Ошибка", "Пользователь с таким логином уже существует.")
                return
            self.repository.add(login, password, role)
        else:
            self.editable_user.login = login
            self.editable_user.password = password
            self.editable_user.role = role
            self.editable_user.blocked = bool(self.blocked_var.get())
            self.repository.update(self.editable_user)

        self.master.load_users()
        self.destroy()


# ===== Панель администратора (аналог admin_form.py) =====
class AdminForm(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.repository = master.repository
        self.title(f"{APP_TITLE} — Панель администратора")
        self.minsize(560, 380)
        self.protocol("WM_DELETE_WINDOW", self._exit)
        self._build_widgets()
        self.load_users()

    def _build_widgets(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        tk.Label(self, text="Управление пользователями",
                 font=("Segoe UI", 13, "bold")).grid(row=0, column=0, pady=8)

        columns = ("id", "логин", "роль", "блокировка")
        self.users_table = ttk.Treeview(self, columns=columns,
                                         show="headings")
        headers = {"id": "ID", "логин": "Логин",
                   "роль": "Роль", "блокировка": "Блокировка"}
        for column in columns:
            self.users_table.heading(column, text=headers[column])
            self.users_table.column(column, anchor="center", width=120)
        self.users_table.grid(row=1, column=0, sticky="nsew",
                              padx=10, pady=(0, 10))

        scrollbar = ttk.Scrollbar(self, orient="vertical",
                                  command=self.users_table.yview)
        self.users_table.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(0, 10))

        actions = tk.LabelFrame(self, text="Действия", padx=10, pady=8)
        actions.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        tk.Button(actions, text="Добавить", width=14,
                  command=self.add_user).grid(row=0, column=0, padx=5)
        tk.Button(actions, text="Изменить", width=14,
                  command=self.edit_user).grid(row=0, column=1, padx=5)
        tk.Button(actions, text="Выход", width=14,
                  command=self._exit).grid(row=0, column=2, padx=5)

    def load_users(self):
        for item in self.users_table.get_children():
            self.users_table.delete(item)
        for user in self.repository.get_all():
            self.users_table.insert(
                "", "end", iid=user.user_id,
                values=(user.user_id, user.login, user.role,
                        "Да" if user.blocked else "Нет"))

    def add_user(self):
        UserDialog(self, self.repository)

    def edit_user(self):
        selection = self.users_table.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите пользователя в списке.")
            return
        user_id = int(selection[0])
        editable = next((u for u in self.repository.get_all()
                         if u.user_id == user_id), None)
        if editable is not None:
            UserDialog(self, self.repository, user=editable)

    def _exit(self):
        self.destroy()
        self.master.destroy()


# ===== Рабочий стол пользователя (аналог user_desktop_form.py) =====
class UserDesktopForm(tk.Toplevel):
    def __init__(self, master, user):
        super().__init__(master)
        self.master = master
        self.title(f"{APP_TITLE} — Рабочий стол")
        self.minsize(400, 220)
        self.protocol("WM_DELETE_WINDOW", self._exit)
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text=f"Здравствуйте, {user.login}!",
                 font=("Segoe UI", 13, "bold")).pack(pady=(0, 10))
        tk.Label(frame, text=f"Роль: {user.role}").pack(pady=(0, 20))
        tk.Button(frame, text="Выход", width=16,
                  command=self._exit).pack()

    def _exit(self):
        self.destroy()
        self.master.destroy()


# ===== Форма авторизации (аналог login_form.py) =====
class LoginForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.repository = InMemoryUserRepository()
        self.title(f"{APP_TITLE} — Авторизация")
        self.minsize(360, 470)
        self._build_widgets()

    def _build_widgets(self):
        length_validator = (self.register(self._limit_length), "%P", "%d")
        container = tk.Frame(self, padx=20, pady=15)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="Вход в систему",
                 font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        credentials = tk.LabelFrame(container, text="Учётные данные",
                                    padx=10, pady=10)
        credentials.pack(fill="x")

        tk.Label(credentials, text="Логин:").grid(row=0, column=0,
                                                  sticky="e", pady=4)
        self.login_entry = tk.Entry(credentials, width=25, validate="key",
                                    validatecommand=length_validator)
        self.login_entry.grid(row=0, column=1, pady=4)

        tk.Label(credentials, text="Пароль:").grid(row=1, column=0,
                                                   sticky="e", pady=4)
        self.password_entry = tk.Entry(credentials, width=25, show="*",
                                       validate="key",
                                       validatecommand=length_validator)
        self.password_entry.grid(row=1, column=1, pady=4)

        captcha_group = tk.LabelFrame(container, text="Соберите изображение",
                                      padx=10, pady=10)
        captcha_group.pack(fill="x", pady=(10, 0))
        self.captcha = CaptchaWidget(captcha_group)
        self.captcha.pack()

        tk.Button(container, text="Войти", width=20,
                  command=self.login).pack(pady=(12, 0))
        self.login_entry.focus_set()

    def _limit_length(self, proposed_value, action):
        if action != "1":
            return True
        return len(proposed_value) <= LOGIN_MAX_LENGTH

    def login(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()

        if not login or not password:
            messagebox.showwarning(
                "Внимание",
                "Поля «Логин» и «Пароль» обязательны для заполнения.")
            return

        user = self.repository.find_by_login(login)

        if user is None:
            messagebox.showerror("Ошибка", WRONG_CREDENTIALS_MESSAGE)
            return

        if user.blocked:
            messagebox.showerror("Доступ запрещён", BLOCKED_MESSAGE)
            return

        if not self.captcha.is_solved():
            self._handle_failed_attempt(
                user, "Изображение собрано неверно. Попробуйте ещё раз.")
            return

        if password != user.password:
            self._handle_failed_attempt(user, WRONG_CREDENTIALS_MESSAGE)
            return

        self.repository.reset_attempts(user)
        messagebox.showinfo("Успех", "Вы успешно авторизовались.")
        self._open_desktop(user)

    def _handle_failed_attempt(self, user, error_message):
        blocked = self.repository.register_failed_attempt(user)
        if blocked:
            messagebox.showerror("Доступ запрещён", BLOCKED_MESSAGE)
        else:
            messagebox.showerror("Ошибка", error_message)
        self.captcha.shuffle()

    def _open_desktop(self, user):
        self.withdraw()
        if user.is_admin():
            AdminForm(self, user)
        else:
            UserDesktopForm(self, user)


def main():
    LoginForm().mainloop()


if __name__ == "__main__":
    main()
