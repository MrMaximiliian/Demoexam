"""Точка входа информационной системы производства ООО «Хлебус».

Создаёт главное окно, проверяет доступность базы данных и управляет
переключением экранов: форма авторизации → рабочий стол в соответствии
с ролью пользователя.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import config
from app.database import DatabaseConnection, ReferenceRepository, UserRepository
from app.database.connection import DatabaseError
from app.services import AuthenticationService, PasswordHasher
from app.ui.admin_window import AdminFrame
from app.ui.app_theme import apply_theme, center_window
from app.ui.login_window import LoginFrame
from app.ui.user_window import UserFrame


class HlebusApplication:
    def __init__(self, root):
        self.root = root
        apply_theme(root)
        self.root.report_callback_exception = self._handle_exception

        self.connection = DatabaseConnection(config.DATABASE_PATH)
        self.user_repository = UserRepository(self.connection)
        self.reference_repository = ReferenceRepository(self.connection)
        self.password_hasher = PasswordHasher()
        self.auth_service = AuthenticationService(
            self.user_repository, self.password_hasher
        )

        self.current_screen = None
        self.show_login()

    def _clear_screen(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def show_login(self):
        self._clear_screen()
        self.root.title("Хлебус — Авторизация")
        self.root.minsize(540, 680)
        self.current_screen = LoginFrame(
            self.root, self.auth_service, on_success=self.show_desktop
        )
        self.current_screen.pack(fill="both", expand=True)
        center_window(self.root, 560, 720)

    def show_desktop(self, user):
        self._clear_screen()
        if user.is_administrator:
            self.root.title("Хлебус — Рабочий стол администратора")
            self.root.minsize(900, 600)
            self.current_screen = AdminFrame(
                self.root, self.user_repository, self.reference_repository,
                self.password_hasher, user, on_logout=self.show_login,
            )
            center_window(self.root, 1040, 660)
        else:
            self.root.title("Хлебус — Рабочий стол пользователя")
            self.root.minsize(820, 540)
            self.current_screen = UserFrame(
                self.root, self.reference_repository, user, on_logout=self.show_login,
            )
            center_window(self.root, 900, 600)
        self.current_screen.pack(fill="both", expand=True)

    def _handle_exception(self, exc_type, exc_value, traceback_object):
        messagebox.showerror(
            "Непредвиденная ошибка",
            "В работе приложения возникла ошибка:\n{0}".format(exc_value),
        )


def main():
    root = tk.Tk()
    try:
        DatabaseConnection(config.DATABASE_PATH).connect().close()
    except DatabaseError as error:
        root.withdraw()
        messagebox.showerror("База данных", str(error))
        root.destroy()
        return

    HlebusApplication(root)
    root.mainloop()


if __name__ == "__main__":
    main()
