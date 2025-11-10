#!/usr/bin/env python3
import curses
import random
import time

DENSITY = 0.35
TRAIL_LEN = 4
SPEED_RANGE = (1, 3)

CHARS = "abcdefghijklmnopqrstuvwxyz0123456789@#$%&*ナニヌネノ"

INTRO_LINES = [
    "Wake up, Neo...",
    "The Matrix has you...",
    "Follow the white rabbit.",
    "Knock, knock, Neo."
]

INTRO_DELAY = 1.2    # pause between lines
TYPE_SPEED = 0.05    # typing speed per character
CURSOR_BLINK = 0.15  # blinking time for intro cursor


def safe_addstr(scr, y, x, s, attr=0):
    h, w = scr.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try:
            scr.addstr(y, x, s, attr)
        except curses.error:
            pass

def type_line(stdscr, text):
    """Typewriter effect for each intro message."""
    sh, sw = stdscr.getmaxyx()
    x = 2
    y = sh // 2

    for i, ch in enumerate(text):
        safe_addstr(stdscr, y, x + i, ch, curses.color_pair(1))
        stdscr.refresh()
        time.sleep(TYPE_SPEED)

    # blinking cursor after line
    for _ in range(4):
        safe_addstr(stdscr, y, x + len(text), "█", curses.color_pair(1))
        stdscr.refresh()
        time.sleep(CURSOR_BLINK)
        safe_addstr(stdscr, y, x + len(text), " ")
        stdscr.refresh()
        time.sleep(CURSOR_BLINK)

def intro_sequence(stdscr):
    """Display all intro lines with typewriter effect."""
    curses.curs_set(0)
    stdscr.erase()
    stdscr.refresh()

    for line in INTRO_LINES:
        stdscr.erase()
        type_line(stdscr, line)
        time.sleep(INTRO_DELAY)

    # small fade before rain
    stdscr.erase()
    stdscr.refresh()
    time.sleep(0.6)

def build_columns(width):
    step = max(2, int(1 / max(0.01, DENSITY)))
    return list(range(0, width, step))


def matrix_rain(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(30)

    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_GREEN, -1)

    h, w = stdscr.getmaxyx()
    cols = build_columns(w)

    y_heads = [random.randint(0, h - 1) for _ in cols]
    speeds  = [random.randint(*SPEED_RANGE) for _ in cols]

    while True:
        ch = stdscr.getch()
        if ch == ord('q'):
            break

        nh, nw = stdscr.getmaxyx()
        if (nh, nw) != (h, w):
            h, w = nh, nw
            cols = build_columns(w)
            y_heads = [random.randint(0, h - 1) for _ in cols]
            speeds  = [random.randint(*SPEED_RANGE) for _ in cols]

        stdscr.erase()

        for idx, x in enumerate(cols):
            y = y_heads[idx]

            safe_addstr(
                stdscr,
                y, x,
                random.choice(CHARS),
                curses.color_pair(1) | curses.A_BOLD
            )

            for t in range(1, TRAIL_LEN + 1):
                yy = y - t
                if yy < 0:
                    break
                safe_addstr(
                    stdscr,
                    yy, x,
                    random.choice(CHARS),
                    curses.color_pair(1) | curses.A_DIM
                )

            y_heads[idx] = (y + speeds[idx]) % h

            if random.random() < 0.02:
                speeds[idx] = random.randint(*SPEED_RANGE)

        stdscr.refresh()
        time.sleep(0.02)


def main():
    def runner(stdscr):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)

        intro_sequence(stdscr)
        matrix_rain(stdscr)

    curses.wrapper(runner)

if __name__ == "__main__":
    main()
