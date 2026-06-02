# -*- coding: utf-8 -*-
# Модуль 4. Информационная система авторизации
# Заказчик: Молочный комбинат «Полесье»

from forms.login_form import LoginForm


def main():
    application = LoginForm()
    application.mainloop()


if __name__ == "__main__":
    main()
