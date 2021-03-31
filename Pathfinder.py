import numpy as np
import pygame
import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
import os
import platform

from pygame.locals import QUIT, KEYDOWN, K_KP_ENTER, K_SPACE, K_ESCAPE, K_s, K_d, K_w, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION


class Node:
    def __init__(self, coords, shape, distance_from_start=np.inf, is_wall=False, is_visited=False, predecessor=None):
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
        global edit_mode_rb

        self.lbl1 = Label(win, text='Rows:')
        self.lbl2 = Label(win, text='Columns:')
        self.lbl3 = Label(win, text='Algorithm:')
        self.t1 = Entry()
        self.t1.insert(END, str(ROWS))
        self.t2 = Entry()
        self.t2.insert(END, str(COLUMNS))

        algo = StringVar()
        algo.set('Dijkstra')
        data = ('Dijkstra')
        self.cb = Combobox(win, values=data)
        self.cb.current(0)

        edit_mode_rb.set(1)
        self.lbl4 = Label(win, text='Editing Mode:')
        self.rbtn1 = Radiobutton(
            win, text='Source', variable=edit_mode_rb, value=1, command=change_editing_mode)
        self.rbtn2 = Radiobutton(
            win, text='Destination', variable=edit_mode_rb, value=2, command=change_editing_mode)
        self.rbtn3 = Radiobutton(
            win, text='Wall', variable=edit_mode_rb, value=3, command=change_editing_mode)

        self.btn1 = Button(win, text='Find Path', command=find_path)
        self.btn2 = Button(win, text='Build Grid', command=self.build_click)

        self.lbl1.place(x=50, y=40)
        self.t1.place(x=150, y=40)
        self.lbl2.place(x=50, y=80)
        self.t2.place(x=150, y=80)
        self.lbl3.place(x=50, y=120)

        self.cb.place(x=150, y=120)

        self.lbl4.place(x=50, y=160)
        self.rbtn1.place(x=150, y=160)
        self.rbtn2.place(x=150, y=180)
        self.rbtn3.place(x=150, y=200)

        self.btn2.place(x=50, y=240)
        self.btn1.place(x=150, y=240)

        root.title('Pathfinder Settings')
        root.geometry("400x300+10+10")

        os.environ['SDL_WINDOWID'] = str(root.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'

    def build_click(self):
        tmp_rows = int(self.t1.get())
        tmp_cols = int(self.t2.get())

        refresh_rows_cols(tmp_rows, tmp_cols)
        init_pygame()


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


def close():
    global running, pygame_started
    running = False
    pygame_started = False
    pygame.quit()


root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', close)

screen = None

current_mode = EDITING_MODES.SOURCE
edit_mode_rb = IntVar()


matrix = None

source_coords = None
destination_coords = None

running = True
pygame_started = False

holding = False


def init_settings_window():
    settings_win = TkWindow(root)


def init_pygame():
    global pygame_started, matrix, screen

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    screen.fill(CELL_BORDER)
    pygame.display.set_caption('Pathfinder')

    pygame.display.init()

    pygame.display.update()

    matrix = init_matrix()
    init_grid()
    pygame.display.update()

    pygame_started = True


def init_matrix():
    return np.empty((ROWS, COLUMNS), dtype=Node)


def init_grid():
    global screen, matrix
    PADDING = (WINDOW_WIDTH - MARGIN * COLUMNS) // COLUMNS

    for x in range(ROWS):
        for y in range(COLUMNS):
            shape = pygame.Rect(
                (MARGIN + PADDING) * y + MARGIN,
                (MARGIN + PADDING) * x + MARGIN,
                PADDING,
                PADDING,
            )
            pygame.draw.rect(screen, CELL, shape)
            matrix[x][y] = Node(coords=(x, y),
                                shape=shape.copy(),
                                distance_from_start=np.inf)


def mark_cell():
    global matrix, screen, source_coords, destination_coords
    coords = pygame.mouse.get_pos()
    x = coords[1]//CELL_SIZE
    y = coords[0]//CELL_SIZE

    hover_node = matrix[x][y]

    if current_mode == EDITING_MODES.SOURCE:
        source_cell = None
        if source_coords is None:
            source_coords = x, y
            source_cell = matrix[source_coords[0], source_coords[1]]

        else:
            source_cell = matrix[source_coords[0], source_coords[1]]
            pygame.draw.rect(screen, CELL, source_cell.shape)
            matrix[source_coords[0], source_coords[1]] = Node(source_coords, source_cell.shape.copy(), distance_from_start=np.inf,
                                                              is_wall=False, is_visited=False, predecessor=None)
            source_coords = x, y
            source_cell = matrix[source_coords[0], source_coords[1]]

        pygame.draw.rect(screen, SOURCE, source_cell.shape)
        matrix[source_coords[0], source_coords[1]] = Node(source_coords, source_cell.shape.copy(), distance_from_start=0,
                                                          is_wall=True, is_visited=True, predecessor=None)

    if current_mode == EDITING_MODES.DESTINATION:
        destination_cell = None
        if destination_coords is None:
            destination_coords = x, y
            destination_cell = matrix[destination_coords[0],
                                      destination_coords[1]]

        else:
            destination_cell = matrix[destination_coords[0],
                                      destination_coords[1]]
            pygame.draw.rect(screen, CELL, destination_cell.shape)

            matrix[destination_coords[0], destination_coords[1]] = Node(
                destination_coords, destination_cell.shape.copy())

            destination_coords = x, y
            destination_cell = matrix[destination_coords[0],
                                      destination_coords[1]]

        pygame.draw.rect(screen, DESTINATION, destination_cell.shape)
        matrix[destination_coords[0], destination_coords[1]] = Node(
            destination_coords, destination_cell.shape.copy())

    if current_mode == EDITING_MODES.WALL:
        if hover_node is not source_coords and hover_node is not destination_coords:
            hover_node.is_wall = True
            rect = hover_node.shape
            pygame.draw.rect(screen, WALL, rect)

    pygame.display.update()


def find_path():
    pass


def refresh_rows_cols(rows, cols):
    global ROWS, COLUMNS, WINDOW_WIDTH, WINDOW_HEIGHT
    ROWS = rows
    COLUMNS = cols

    WINDOW_WIDTH = COLUMNS*CELL_SIZE
    WINDOW_HEIGHT = ROWS*CELL_SIZE


def check_for_events():
    global pygame_started, holding, screen

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame_started = False
            pygame.quit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame_started = False
                pygame.quit()

            if event.key == K_KP_ENTER:
                pass

            if event.key == K_SPACE:
                pass

        if event.type == MOUSEBUTTONDOWN:
            mark_cell()
            holding = True

        if event.type == MOUSEBUTTONUP:
            holding = False

        if event.type == MOUSEMOTION and holding:
            mark_cell()


def change_editing_mode():
    global edit_mode_rb, current_mode

    if edit_mode_rb.get() == 1:
        current_mode = EDITING_MODES.SOURCE
    if edit_mode_rb.get() == 2:
        current_mode = EDITING_MODES.DESTINATION
    if edit_mode_rb.get() == 3:
        current_mode = EDITING_MODES.WALL


def main():
    init_settings_window()

    while running:
        root.update()

        if pygame_started:
            check_for_events()

    root.destroy()


if __name__ == "__main__":
    main()
