"""Единое оформление интерфейса.

Здесь настраиваются цвета, шрифты и стили виджетов ttk, чтобы все окна
приложения имели согласованный внешний вид.
"""

from tkinter import ttk

BACKGROUND = "#F4EFE7"
SURFACE = "#FFFFFF"
PRIMARY = "#2F4858"
ACCENT = "#C57B2C"
ACCENT_ACTIVE = "#A8661F"
TEXT = "#28323A"
MUTED = "#6B7782"
BORDER = "#D8CFC0"

BASE_FONT = ("Segoe UI", 10)
TITLE_FONT = ("Segoe UI Semibold", 18)
SUBTITLE_FONT = ("Segoe UI", 11)
HEADING_FONT = ("Segoe UI Semibold", 12)


def apply_theme(root):
    root.configure(background=BACKGROUND)
    root.option_add("*Font", BASE_FONT)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(".", background=BACKGROUND, foreground=TEXT, font=BASE_FONT)
    style.configure("TFrame", background=BACKGROUND)
    style.configure("Surface.TFrame", background=SURFACE)
    style.configure("Header.TFrame", background=PRIMARY)

    style.configure("TLabel", background=BACKGROUND, foreground=TEXT)
    style.configure("Surface.TLabel", background=SURFACE, foreground=TEXT)
    style.configure("Title.TLabel", font=TITLE_FONT, foreground=PRIMARY, background=SURFACE)
    style.configure("Subtitle.TLabel", font=SUBTITLE_FONT, foreground=MUTED, background=SURFACE)
    style.configure("Heading.TLabel", font=HEADING_FONT, foreground=PRIMARY, background=BACKGROUND)
    style.configure("HeaderTitle.TLabel", font=("Segoe UI Semibold", 14),
                    foreground="#FFFFFF", background=PRIMARY)
    style.configure("HeaderInfo.TLabel", foreground="#D6E0E8", background=PRIMARY)
    style.configure("Hint.TLabel", foreground=MUTED, background=SURFACE)
    style.configure("Success.TLabel", foreground="#2E7D32", background=SURFACE)
    style.configure("Error.TLabel", foreground="#C62828", background=SURFACE)

    style.configure("TEntry", fieldbackground=SURFACE, bordercolor=BORDER, padding=6)
    style.configure("TCombobox", fieldbackground=SURFACE, padding=4)

    style.configure("TButton", padding=(14, 8), background="#E7DFD2",
                    foreground=TEXT, borderwidth=0, focusthickness=1)
    style.map("TButton", background=[("active", "#D9CFBD")])

    style.configure("Accent.TButton", background=ACCENT, foreground="#FFFFFF")
    style.map("Accent.TButton",
              background=[("active", ACCENT_ACTIVE), ("disabled", "#C9BBA6")])

    style.configure("Treeview", background=SURFACE, fieldbackground=SURFACE,
                    foreground=TEXT, rowheight=26, borderwidth=1)
    style.configure("Treeview.Heading", font=("Segoe UI Semibold", 10),
                    background="#E7DFD2", foreground=PRIMARY, padding=6)
    style.map("Treeview", background=[("selected", "#3E5C76")],
              foreground=[("selected", "#FFFFFF")])

    style.configure("TNotebook", background=BACKGROUND, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(16, 8), font=BASE_FONT)
    style.map("TNotebook.Tab",
              background=[("selected", SURFACE)],
              foreground=[("selected", PRIMARY)])

    style.configure("TLabelframe", background=SURFACE, bordercolor=BORDER)
    style.configure("TLabelframe.Label", background=SURFACE, foreground=PRIMARY,
                    font=("Segoe UI Semibold", 10))


def center_window(window, width, height):
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 3
    window.geometry("{0}x{1}+{2}+{3}".format(width, height, x, max(y, 0)))
