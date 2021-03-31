import numpy as np
import pygame
import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
import os
import platform

from pygame.locals import QUIT, KEYDOWN, K_KP_ENTER, K_SPACE, K_ESCAPE, K_s, K_d, K_w


class Node:
    def __init__(self, coords, shape, distance_from_start, is_wall=False, is_visited=False, predecessor=None):
        self.coords = coords
        self.shape = shape
        self.distance_from_start = distance_from_start
        self.is_wall = is_wall
        self.is_visited = is_visited
        self.predecessor = predecessor

    def __lt__(self, node_to_check):
        return self.distance_from_start < node_to_check.distance_from_start


class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class TkWindow:
    def __init__(self, win):
        self.lbl1 = Label(win, text='Columns:')
        self.lbl2 = Label(win, text='Rows:')
        self.lbl3 = Label(win, text='Algorithm:')
        self.t1 = Entry()
        self.t1.insert(END, str(COLUMNS))
        self.t2 = Entry()
        self.t2.insert(END, str(ROWS))

        var = StringVar()
        var.set('Dijkstra')
        data = ('Dijkstra')
        self.cb = Combobox(win, values=data)
        self.cb.current(0)

        self.btn1 = Button(win, text='Find Path', command=find_path)
        self.btn2 = Button(win, text='Build Grid', command=rebuild)

        self.lbl1.place(x=50, y=40)
        self.t1.place(x=150, y=40)
        self.lbl2.place(x=50, y=80)
        self.t2.place(x=150, y=80)
        self.lbl3.place(x=50, y=120)

        self.cb.place(x=150, y=120)

        self.btn2.place(x=50, y=160)
        self.btn1.place(x=150, y=160)

        root.title('Pathfinder Settings')
        root.geometry("400x300+10+10")

        os.environ['SDL_WINDOWID'] = str(root.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'


EDITING_MODES = Enum(["SOURCE", "DESTINATION", "WALL"])

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

CELL_SIZE = 20
MARGIN = 1
ROWS = 25
COLUMNS = 25

WINDOW_WIDTH = COLUMNS*CELL_SIZE
WINDOW_HEIGHT = ROWS*CELL_SIZE

CELL = (255, 255, 255)
WALL = (0, 0, 0)
CELL_BORDER = (0, 0, 0)
SOURCE = (0, 0, 255)
DESTINATION = (255, 0, 0)
VISITED = (255, 255, 0)
PATH = (0, 255, 0)


def dont_close_tk():
    pass


root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', dont_close_tk)


def find_path():
    pass


def rebuild():
    pass


def init_settings_window():
    settings_win = TkWindow(root)


def main():
    init_settings_window()

    while True:
        root.update()


if __name__ == "__main__":
    main()
