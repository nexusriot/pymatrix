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
INTRO_DELAY = 1.2
TYPE_SPEED = 0.04
CURSOR_BLINK = 0.15

GLITCH_DURATION = 0.2  # seconds
GLITCH_FPS = 40
GLITCH_NOISE_DENSITY = 0.08


def safe_addstr(scr, y, x, s, attr=0):
    h, w = scr.getmaxyx()
    if 0 <= y < h and 0 <= x < w:
        try:
            scr.addstr(y, x, s, attr)
        except curses.error:
            pass

def build_columns(width):
    step = max(2, int(1 / max(0.01, DENSITY)))
    return list(range(0, width, step))


def glitch_effect(stdscr, duration=GLITCH_DURATION):
    """CRT-like glitch that runs automatically without waiting for input."""
    h, w = stdscr.getmaxyx()

    # ensure non-blocking reads just for the glitch
    old_delay = stdscr.getdelay() if hasattr(stdscr, "getdelay") else None
    stdscr.nodelay(True)
    stdscr.timeout(0)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_WHITE, -1)
    green = curses.color_pair(1)
    white = curses.color_pair(2)

    start = time.time()
    frame_dt = 1.0 / GLITCH_FPS

    while time.time() - start < duration:
        # optional quit
        if stdscr.getch() == ord('q'):
            break

        phase = random.random()
        stdscr.erase()


        if phase < 0.08:
            for y in range(h):
                safe_addstr(stdscr, y, 0, " " * max(0, w - 1), white | curses.A_REVERSE)
            stdscr.refresh()
            time.sleep(0.02)
            continue

        for y in range(0, h, 2):
            safe_addstr(stdscr, y, 0, " " * max(0, w - 1), curses.A_DIM)


        for _ in range(random.randint(1, 4)):
            ry = random.randrange(0, h)
            shift = random.choice([-3, -2, -1, 1, 2, 3])
            segment = "".join(random.choice(CHARS) for _ in range(max(0, w - abs(shift) - 1)))
            x = max(0, shift)
            attr = green | (curses.A_BOLD if random.random() < 0.3 else 0)
            safe_addstr(stdscr, ry, x, segment, attr)

        # noise
        cells = int(h * w * GLITCH_NOISE_DENSITY)
        for _ in range(cells):
            ny = random.randrange(0, h)
            nx = random.randrange(0, max(1, w - 1))
            ch = random.choice(CHARS)
            attr = green | (curses.A_DIM if random.random() < 0.7 else curses.A_BOLD)
            safe_addstr(stdscr, ny, nx, ch, attr)

        stdscr.refresh()
        time.sleep(frame_dt)

    stdscr.erase()
    stdscr.refresh()
    time.sleep(0.08)

    # restore previous delay mode if available
    if old_delay is not None:
        stdscr.timeout(old_delay)
    else:
        stdscr.nodelay(False)


def type_line(stdscr, text):
    sh, sw = stdscr.getmaxyx()
    x = 2
    y = sh // 2
    green = curses.color_pair(1)

    for i, ch in enumerate(text):
        safe_addstr(stdscr, y, x + i, ch, green)
        stdscr.refresh()
        time.sleep(TYPE_SPEED)

    for _ in range(4):
        safe_addstr(stdscr, y, x + len(text), "█", green)
        stdscr.refresh()
        time.sleep(CURSOR_BLINK)
        safe_addstr(stdscr, y, x + len(text), " ")
        stdscr.refresh()
        time.sleep(CURSOR_BLINK)

def intro_sequence(stdscr):
    curses.curs_set(0)
    glitch_effect(stdscr)   # auto-run, no input needed
    for line in INTRO_LINES:
        stdscr.erase()
        type_line(stdscr, line)
        time.sleep(INTRO_DELAY)
    stdscr.erase()
    stdscr.refresh()
    time.sleep(0.4)


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
        if stdscr.getch() == ord('q'):
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
    def runner(stdscr):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_WHITE, -1)

        intro_sequence(stdscr)
        matrix_rain(stdscr)

    curses.wrapper(runner)

if __name__ == "__main__":
    main()
