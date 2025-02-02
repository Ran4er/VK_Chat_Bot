import subprocess
import sys

try:
    import curses

except ImportError:
    print("vk_api не найден. Установка...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "windows_curses"])

    import vk_api


def draw_button(stdscr, y, x, text, selected):
    # Цвета для выбранной и невыбранной кнопки
    if selected:
        color = curses.color_pair(1)
        border_color = curses.color_pair(1)
    else:
        color = curses.color_pair(2)
        border_color = curses.color_pair(2)

    # Рисуем рамку кнопки
    stdscr.attron(border_color)
    stdscr.addstr(y, x, "+" + "-" * (len(text) + 2) + "+")
    stdscr.addstr(y + 1, x, "| " + text + " |")
    stdscr.addstr(y + 2, x, "+" + "-" * (len(text) + 2) + "+")
    stdscr.attroff(border_color)


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Выделенная кнопка
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # Обычная кнопка

    curses.curs_set(0)
    current_selection = 0
    buttons = ["Запуск", "Выход"]

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Центрируем кнопки
        start_y = (height - (len(buttons) * 4)) // 2
        start_x = (width - (max(len(b) for b in buttons) + 4)) // 2

        for idx, button in enumerate(buttons):
            y = start_y + idx * 4
            draw_button(stdscr, y, start_x, button, idx == current_selection)

        stdscr.refresh()
        key = stdscr.getch()

        # Управление выбором
        if key == curses.KEY_UP and current_selection > 0:
            current_selection -= 1
        elif key == curses.KEY_DOWN and current_selection < len(buttons) - 1:
            current_selection += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            if buttons[current_selection] == "Запуск":
                stdscr.clear()
                stdscr.addstr(height // 2, width // 2 - 8, "Программа запущена!")
                stdscr.refresh()
                stdscr.getch()
            elif buttons[current_selection] == "Выход":
                break

curses.wrapper(main)
