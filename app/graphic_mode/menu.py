import subprocess
import sys
import time

try:
    import curses

except ImportError:
    print("curses не найден. Установка...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "windows_curses"])

    import curses


def draw_button(stdscr, y, x, text, selected):
    if selected:
        color = curses.color_pair(1)
        border_color = curses.color_pair(1)
    else:
        color = curses.color_pair(2)
        border_color = curses.color_pair(2)

    stdscr.attron(border_color)
    stdscr.addstr(y, x, "+" + "-" * (len(text) + 2) + "+")
    stdscr.addstr(y + 1, x, "| " + text + " |")
    stdscr.addstr(y + 2, x, "+" + "-" * (len(text) + 2) + "+")
    stdscr.attroff(border_color)


def run_bot():
    process = subprocess.Popen([sys.executable, "../main.py"])
    return process


def draw_progress_bar(stdscr, progress, y, x, width=30):
    fill_width = int(progress * width)
    bar = "█" * fill_width + "-" * (width - fill_width)
    stdscr.addstr(y, x, f"[{bar}] {int(progress * 100)}%")


def main(stdscr):
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Активная кнопка
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE) # Неактивная кнопка

    curses.curs_set(0)
    current_selection = 0
    buttons = ["Запустить", "Выход"]
    bot_process = None

    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Центрирование
        start_y = (height - (len(buttons) * 4)) // 2
        start_x = (width - 20) // 2


        for idx, button in enumerate(buttons):
            y = start_y + idx * 4
            draw_button(stdscr, y, start_x, button, idx == current_selection)
            '''color = curses.color_pair(1) if idx == current_selection else curses.color_pair(2)
            stdscr.attron(color)
            stdscr.addstr(y, start_x, f"  {button}  ")
            stdscr.attroff(color)'''

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and current_selection > 0:
            current_selection -= 1
        elif key == curses.KEY_DOWN and current_selection < len(buttons) - 1:
            current_selection += 1
        elif key in [curses.KEY_ENTER, 10, 13]:
            if buttons[current_selection] == "Запустить":
                stdscr.clear()
                stdscr.addstr(height // 2 - 2, start_x, "Запуск бота...")
                for i in range(1, 11):
                    draw_progress_bar(stdscr, i / 10, height // 2, start_x)
                    stdscr.refresh()
                    time.sleep(0.2)

                bot_process = run_bot()

                stdscr.clear()
                stdscr.addstr(height // 2, start_x, "Бот запущен!")
                stdscr.addstr(height // 2 + 2, start_x-(len("Нажмите 'Остановить' для выхода")//4), "Нажмите 'Остановить' для выхода")
                stdscr.refresh()

                stop_selection = 0
                while True:
                    stop_button = "Остановить"
                    color = curses.color_pair(1) if stop_selection == 0 else curses.color_pair(2)
                    stdscr.attron(color)
                    stdscr.addstr(height // 2 + 4, start_x, f"  {stop_button}  ")
                    stdscr.attroff(color)
                    stdscr.refresh()

                    key = stdscr.getch()
                    if key in [curses.KEY_ENTER, 10, 13]:
                        if bot_process:
                            bot_process.terminate()
                            bot_process.wait()
                        break

            elif buttons[current_selection] == "Выход":
                if bot_process:
                    bot_process.terminate()
                    bot_process.wait()
                break

curses.wrapper(main)
