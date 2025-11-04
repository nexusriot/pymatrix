#!/usr/bin/env python3
import curses
import random
import time


DENSITY = 0.35
TRAIL_LEN = 4
SPEED_RANGE = (1, 3)


CHARS = "abcdefghijklmnopqrstuvwxyz0123456789@#$%&*ナニヌネノ"

def safe_addstr(scr, y, x, s, attr=0):
    h, w = scr.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try:
            scr.addstr(y, x, s, attr)
        except curses.error:
            pass

def build_columns(width):
    step = max(2, int(1 / max(0.01, DENSITY)))
    cols = list(range(0, width, step))
    return cols

def matrix(stdscr):
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

            # head (bright)
            safe_addstr(stdscr, y, x, random.choice(CHARS),
                        curses.color_pair(1) | curses.A_BOLD)


            for t in range(1, TRAIL_LEN + 1):
                yy = y - t
                if yy < 0:
                    break

                safe_addstr(stdscr, yy, x, random.choice(CHARS),
                            curses.color_pair(1) | curses.A_DIM)


            y_heads[idx] = (y + speeds[idx]) % h

            if random.random() < 0.02:
                speeds[idx] = random.randint(*SPEED_RANGE)

        stdscr.refresh()
        time.sleep(0.02)

def main():
    curses.wrapper(matrix)

if __name__ == "__main__":
    main()

