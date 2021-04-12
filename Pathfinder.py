import numpy as np
import pygame
import tkinter as tk
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import filedialog
import os
import platform
import heapq
from queue import PriorityQueue
import json

from pygame.locals import QUIT, KEYDOWN, K_RETURN, K_ESCAPE, K_BACKSPACE, K_s, K_d, K_w, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION


class Node:
    def __init__(self, coords, shape, distance_from_start=np.inf, is_wall=False, is_visited=False, predecessor=None, f=np.inf, g=np.inf, h=np.inf):
        self.coords = coords
        self.shape = shape
        self.distance_from_start = distance_from_start
        self.is_wall = is_wall
        self.is_visited = is_visited
        self.predecessor = predecessor
        self.f = f      # f-value for A Search
        self.g = g      # g-value for A Search
        self.h = h      # h-value for A Search

    def __lt__(self, node_to_check):
        global algo_selection
        if algo_selection.get() == 'Dijkstra':
            return self.distance_from_start < node_to_check.distance_from_start
        elif algo_selection.get() == 'ASearch':
            return self.f < node_to_check.f


class Enum(set):
    """
    Class used to emulate Enum
    """

    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError


class TkWindow:
    """
    Class used to handle the tkinter window
    """

    def __init__(self, win):
        global algo_selection, edit_mode_rb

        #####   DECLARING LABELS AND ENTRIES   #####
        self.lbl_rows = Label(win, text='Rows:')
        self.lbl_cols = Label(win, text='Columns:')
        self.lbl_cell_size = Label(win, text='Cell Size:')
        self.lbl_algo = Label(win, text='Algorithm:')
        self.t_rows = Entry()
        self.t_rows.insert(END, str(ROWS))
        self.t_cols = Entry()
        self.t_cols.insert(END, str(COLUMNS))
        self.t_cell_size = Entry()
        self.t_cell_size.insert(END, str(CELL_SIZE))

        algo_selection.set('Dijkstra')
        data = ('Dijkstra', 'ASearch', 'BFS', 'DFS')
        self.cb = Combobox(win, values=data)
        self.cb.bind('<<ComboboxSelected>>', self.change_algo_selection)
        self.cb.current(0)

        #####   RADIO BUTTONS    #####
        edit_mode_rb.set(1)
        self.lbl_editmode = Label(win, text='Editing Mode:')
        self.rb_src = Radiobutton(
            win, text='Source', variable=edit_mode_rb, value=1, command=change_editing_mode)
        self.rb_dest = Radiobutton(
            win, text='Destination', variable=edit_mode_rb, value=2, command=change_editing_mode)
        self.rb_wall = Radiobutton(
            win, text='Wall', variable=edit_mode_rb, value=3, command=change_editing_mode)
        self.rb_erase = Radiobutton(
            win, text='Erase', variable=edit_mode_rb, value=4, command=change_editing_mode)

        #####   BUTTONS    #####
        self.btn_find = Button(win, text='Find Path', command=find_path)
        self.btn_build_grid = Button(
            win, text='Build Grid', command=self.build_click)
        self.btn_reset_last_grid = Button(
            win, text='Reset Last', command=reset_last_grid)

        self.btn_load_grid = Button(win, text='Load Grid', command=load_grid)
        self.btn_save_grid = Button(win, text='Save Grid', command=save_grid)
        #####   PLACING #####

        self.lbl_rows.place(x=50, y=40)
        self.t_rows.place(x=150, y=40)
        self.lbl_cols.place(x=50, y=80)
        self.t_cols.place(x=150, y=80)
        self.lbl_cell_size.place(x=50, y=120)
        self.t_cell_size.place(x=150, y=120)
        self.lbl_algo.place(x=50, y=160)

        self.cb.place(x=150, y=160)

        self.lbl_editmode.place(x=50, y=200)
        self.rb_src.place(x=150, y=200)
        self.rb_dest.place(x=150, y=220)
        self.rb_wall.place(x=150, y=240)
        self.rb_erase.place(x=150, y=260)

        self.btn_build_grid.place(x=50, y=300)
        self.btn_reset_last_grid.place(x=150, y=300)
        self.btn_find.place(x=250, y=340)
        self.btn_load_grid.place(x=50, y=340)
        self.btn_save_grid.place(x=150, y=340)

        root.title('Pathfinder Settings')
        root.geometry("350x400+10+10")

        os.environ['SDL_WINDOWID'] = str(root.winfo_id())
        if platform.system == "Windows":
            os.environ['SDL_VIDEODRIVER'] = 'windib'

        os.environ['SDL_VIDEO_CENTERED'] = '0'

    def build_click(self):
        tmp_rows = int(self.t_rows.get())
        tmp_cols = int(self.t_cols.get())
        tmp_cell_size = int(self.t_cell_size.get())

        refresh_rows_cols(tmp_rows, tmp_cols, tmp_cell_size)
        init_pygame()

    def change_algo_selection(self, event):
        global algo_selection
        algo_selection.set(self.cb.get())


EDITING_MODES = Enum(["SOURCE", "DESTINATION", "WALL", "ERASE"])

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 500

CELL_SIZE = 20
MARGIN = 1
ROWS = 25
COLUMNS = 25

WINDOW_WIDTH = COLUMNS*CELL_SIZE
WINDOW_HEIGHT = ROWS*CELL_SIZE

CELL = (255, 255, 255)
WALL = (128, 128, 128)
CELL_BORDER = (172, 172, 172)
SOURCE = (0, 220, 0)
DESTINATION = (237, 67, 0)
VISITED = (198, 255, 255)
PATH = (251, 255, 100)


def close():
    """
    Closes the program
    """
    global running, pygame_started
    running = False
    pygame_started = False
    pygame.quit()


"""
Settings Window (Tkinter)
"""
root = tk.Tk()
root.protocol('WM_DELETE_WINDOW', close)

"""
Grid Window (PyGame)
"""
screen = None

current_mode = EDITING_MODES.SOURCE
edit_mode_rb = IntVar()

algo_selection = StringVar()

matrix = None

source_coords = None
destination_coords = None

path_found = False

running = True
pygame_started = False


"""
true when holding down the mouse button
"""
holding = False


def init_settings_window():
    """
    Starts the settings window
    """
    settings_win = TkWindow(root)


def init_pygame():
    """
    Starts the pygame window
    """
    global pygame_started, matrix, screen

    if screen:
        pygame_started = False
        pygame.quit()

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
    """
    Returns a bidimensional matrix
    """
    return np.empty((ROWS, COLUMNS), dtype=Node)


def init_grid():
    """
    Initializes the grid into the pygame window
    """
    global screen, matrix, source_coords, destination_coords
    PADDING = (WINDOW_WIDTH - MARGIN * COLUMNS) // COLUMNS

    if source_coords and (source_coords[0] >= ROWS or source_coords[1] >= COLUMNS):
        source_coords = None

    if destination_coords and (destination_coords[0] >= ROWS or destination_coords[1] >= COLUMNS):
        destination_coords = None

    for y in range(ROWS):
        for x in range(COLUMNS):
            shape = pygame.Rect(
                (MARGIN + PADDING) * x + MARGIN,
                (MARGIN + PADDING) * y + MARGIN,
                PADDING,
                PADDING,
            )
            pygame.draw.rect(screen, CELL, shape)
            matrix[y][x] = Node(coords=(y, x),
                                shape=shape.copy())


def reset_last_grid():
    global source_coords, destination_coords

    if not pygame_started:
        init_pygame()
        return

    walls = []
    for y in range(ROWS):
        for x in range(COLUMNS):
            if matrix[y][x].is_wall and matrix[y][x].coords != source_coords:
                walls.append((matrix[y][x].coords))

    _source_coords = source_coords
    _destination_coords = destination_coords

    init_pygame()

    source_coords = _source_coords
    destination_coords = _destination_coords

    for wall in walls:
        wall_coords = wall
        wall_cell = matrix[wall_coords[0], wall_coords[1]]
        rect = wall_cell.shape
        pygame.draw.rect(screen, WALL, rect)
        wall_cell.is_wall = True

    pygame.display.update()

    if destination_coords:
        destination_cell = matrix[destination_coords[0], destination_coords[1]]
        pygame.draw.rect(screen, DESTINATION, destination_cell.shape)
        matrix[destination_coords[0], destination_coords[1]] = Node(
            destination_coords, destination_cell.shape.copy())

    if source_coords:
        source_cell = matrix[source_coords[0], source_coords[1]]
        pygame.draw.rect(screen, SOURCE, source_cell.shape)
        matrix[source_coords[0], source_coords[1]] = Node(source_coords, source_cell.shape.copy(),
                                                          distance_from_start=0, is_wall=True, is_visited=True, predecessor=None)

    pygame.display.update()


def load_grid():
    """
    Loads grid-datas from file and starts the pygame windows 
    """
    global source_coords, destination_coords, matrix
    fd = filedialog.askopenfilename(
        initialdir='grid_saves', initialfile='grid0.dat')
    if fd:
        f = open(fd, 'r')
        if f:
            text = f.read()
            f.close()
            decoded = json.loads(text)

            rows = decoded['rows']
            cols = decoded['columns']
            cell_size = decoded['cell_size']

            refresh_rows_cols(rows, cols, cell_size)

            source_coords = decoded['source_coords']
            destination_coords = decoded['destination_coords']

            walls = decoded['walls']

            init_pygame()

            """
            Drawing the walls 
            """
            for wall in walls:
                wall_coords = wall
                wall_cell = matrix[wall_coords[0], wall_coords[1]]
                rect = wall_cell.shape
                pygame.draw.rect(screen, WALL, rect)
                wall_cell.is_wall = True

            pygame.display.update()

            """
            Drawing the destination 
            """
            if destination_coords:
                destination_cell = matrix[destination_coords[0],
                                          destination_coords[1]]
                pygame.draw.rect(screen, DESTINATION, destination_cell.shape)
                matrix[destination_coords[0], destination_coords[1]] = Node(
                    destination_coords, destination_cell.shape.copy())

            """
            Drawing the source 
            """
            if source_coords:
                source_cell = matrix[source_coords[0], source_coords[1]]
                pygame.draw.rect(screen, SOURCE, source_cell.shape)
                matrix[source_coords[0], source_coords[1]] = Node(source_coords, source_cell.shape.copy(),
                                                                  distance_from_start=0, is_wall=True, is_visited=True,
                                                                  predecessor=None)

            pygame.display.update()


def save_grid():
    """
    Saves grid-datas from file and starts the pygame windows 
    """
    fd = filedialog.asksaveasfilename(
        initialdir='grid_saves', initialfile='grid0.dat')

    if fd:
        f = open(fd, 'w')
        if f:
            walls = []
            for y in range(ROWS):
                for x in range(COLUMNS):
                    if matrix[y][x].is_wall and matrix[y][x].coords != source_coords:
                        walls.append((matrix[y][x].coords))

            text = {"rows": ROWS, "columns": COLUMNS, "cell_size": CELL_SIZE, "source_coords": source_coords,
                    "destination_coords": destination_coords, "walls": walls}

            js = json.dumps(text)
            f.write(js)
            f.close()


def mark_cell():
    """
    Marks the cell hovered by the mouse cursor 
    """
    global matrix, screen, source_coords, destination_coords
    coords = pygame.mouse.get_pos()
    x = coords[1]//CELL_SIZE
    y = coords[0]//CELL_SIZE

    hover_node = matrix[x][y]

    """
    SOURCE CELL MODE 
    """
    if current_mode == EDITING_MODES.SOURCE:
        if hover_node.coords is not source_coords and hover_node.coords is not destination_coords:
            source_cell = None

            """
            If there is no Source node it initializes it, overwrites instead
            """
            if source_coords is None:
                source_coords = x, y
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

    """
    DESTINATION CELL MODE 
    """
    if current_mode == EDITING_MODES.DESTINATION:
        if hover_node.coords is not source_coords and hover_node.coords is not destination_coords:
            destination_cell = None

            """
            If there is no Destination node it initializes it, overwrites instead
            """
            if destination_coords is None:
                destination_coords = x, y
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

    """
    WALL CELL MODE 
    """
    if current_mode == EDITING_MODES.WALL:
        if hover_node.coords is not source_coords and hover_node.coords is not destination_coords:
            hover_node.is_wall = True
            rect = hover_node.shape
            pygame.draw.rect(screen, WALL, rect)

    """
    ERASE CELL MODE 
    """
    if current_mode == EDITING_MODES.ERASE:
        if hover_node.coords is not source_coords and hover_node.coords is not destination_coords:
            pygame.draw.rect(screen, CELL, hover_node.shape)
            matrix[hover_node.coords[0], hover_node.coords[1]] = Node(hover_node.coords, hover_node.shape.copy(), distance_from_start=np.inf,
                                                                      is_wall=False, is_visited=False, predecessor=None)

    pygame.display.update()


def place_random_nodes():
    global source_coords, destination_coords

    init_grid()

    source_coords = (np.random.randint(0, ROWS),
                     np.random.randint(0, COLUMNS))
    destination_coords = (np.random.randint(0, ROWS),
                          np.random.randint(0, COLUMNS))

    while source_coords == destination_coords:
        destination_coords = (np.random.randint(0, ROWS),
                              np.random.randint(0, COLUMNS))

    reset_last_grid()


def find_path():
    """
    Finds the path using the selected algorithm
    """

    global pygame_started, path_found

    if not pygame_started:
        init_pygame()
        return

    if path_found:
        reset_last_grid()
        path_found = False

    if source_coords and destination_coords:

        if algo_selection.get() == 'Dijkstra':
            Dijkstra()

        if algo_selection.get() == 'ASearch':
            ASearch()

        if algo_selection.get() == 'BFS':
            BFS()

        if algo_selection.get() == 'DFS':
            DFS()


def refresh_rows_cols(rows, cols, cell_size):
    """
    Refreshs the values for rows, columns and cell size
    """

    global ROWS, COLUMNS, WINDOW_WIDTH, WINDOW_HEIGHT, CELL_SIZE

    if rows != 0:
        ROWS = rows

    if cols != 0:
        COLUMNS = cols

    if cell_size != 0:
        CELL_SIZE = cell_size

    WINDOW_WIDTH = COLUMNS*CELL_SIZE
    WINDOW_HEIGHT = ROWS*CELL_SIZE


def check_for_events():
    """
    Listens for events inside of the pygame window
    """
    global pygame_started, holding, screen

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame_started = False
            pygame.quit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame_started = False
                pygame.quit()

            if event.key == K_RETURN:
                place_random_nodes()

            if event.key == K_BACKSPACE:
                reset_last_grid()

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
    if edit_mode_rb.get() == 4:
        current_mode = EDITING_MODES.ERASE


def Dijkstra():
    global path_found

    source = matrix[source_coords[0], source_coords[1]]
    unvisited = [source]

    path_found = False

    while unvisited:
        if path_found:
            highlight_path()
            break

        nearest_node = heapq.heappop(unvisited)
        distance_from_start = nearest_node.distance_from_start + 1

        neighbours = find_neighbours(nearest_node.coords)

        for neighbour in neighbours:
            if neighbour and not neighbour.is_visited and not neighbour.is_wall:
                heapq.heappush(unvisited, neighbour)
                mark_as_visited(neighbour, nearest_node, distance_from_start)

    if not unvisited or not path_found:
        print('THERE IS NO PATH')


def ASearch():
    global path_found

    source = matrix[source_coords[0], source_coords[1]]
    destination = matrix[destination_coords[0], destination_coords[1]]

    source.g = 0
    source.h = calculate_manhattan_distance(source, destination)
    source.f = source.g + source.h

    count = 0
    unvisited = PriorityQueue()
    unvisited.put((0, count, source))

    path_found = False

    while unvisited:
        if path_found:
            highlight_path()
            break

        nearest_node = unvisited.get()[2]

        neighbours = find_neighbours(nearest_node.coords)

        for neighbour in neighbours:

            if neighbour and not neighbour.is_wall:
                tmp_g = calculate_manhattan_distance(neighbour, source)

                if tmp_g < neighbour.g:
                    tmp_h = calculate_manhattan_distance(
                        neighbour, destination)
                    tmp_f = tmp_g + tmp_h

                    if not neighbour.is_visited:
                        mark_as_visited(neighbour, nearest_node,
                                        tmp_f, tmp_g, tmp_h)
                        count += 1
                        unvisited.put((neighbour.f, count, neighbour))

    if not unvisited or not path_found:
        print('THERE IS NO PATH')


def BFS():
    global path_found

    source = matrix[source_coords[0], source_coords[1]]
    destination = matrix[destination_coords[0], destination_coords[1]]

    unvisited = [source]

    path_found = False

    while unvisited:
        if path_found:
            highlight_path()
            break

        nearest_node = unvisited.pop(0)

        neighbours = find_neighbours(nearest_node.coords)

        for neighbour in neighbours:
            if neighbour and not neighbour.is_visited and not neighbour.is_wall:

                if neighbour not in unvisited:
                    heapq.heappush(unvisited, neighbour)
                    mark_as_visited(neighbour, predecessor=nearest_node)

    if not unvisited or not path_found:
        print('THERE IS NO PATH')


def DFS():
    global path_found

    source = matrix[source_coords[0], source_coords[1]]
    destination = matrix[destination_coords[0], destination_coords[1]]

    unvisited = [source]

    path_found = False

    while unvisited:
        if path_found:
            highlight_path()
            break

        nearest_node = unvisited.pop()

        neighbours = find_neighbours(nearest_node.coords)

        for neighbour in neighbours:
            if neighbour and not neighbour.is_visited and not neighbour.is_wall:
                if neighbour not in unvisited:
                    heapq.heappush(unvisited, neighbour)
                    mark_as_visited(neighbour, predecessor=nearest_node)

    if not unvisited or not path_found:
        print('THERE IS NO PATH')


def find_neighbours(coords):
    """
    Finds the neighbours of the cell at given matrix coords
    """
    y, x = coords

    left_node = None
    if 0 <= x-1:
        left_node = matrix[y][x-1]

    right_node = None
    if x+1 < COLUMNS:
        right_node = matrix[y][x+1]

    upper_node = None
    if 0 <= y-1:
        upper_node = matrix[y-1][x]

    lower_node = None
    if y+1 < ROWS:
        lower_node = matrix[y+1][x]

    return [left_node, right_node, upper_node, lower_node]


def calculate_manhattan_distance(first_node, second_node):
    """
    Calculates the manhattan distance between 2 nodes
    """
    return abs(first_node.coords[0] - second_node.coords[0]) + abs(first_node.coords[1] - second_node.coords[1])


def mark_as_visited(node: Node, predecessor, distance=None, g=None, h=None):
    """
    Marks the given node as visited
    """
    global destination_coords, path_found

    node.is_visited = True

    if algo_selection.get() == 'Dijkstra':
        if distance < node.distance_from_start:
            node.distance_from_start = distance
            node.predecessor = predecessor

    if algo_selection.get() == 'ASearch':
        node.g = g
        node.h = h
        node.f = g+h
        node.predecessor = predecessor

    if algo_selection.get() == 'BFS':
        node.predecessor = predecessor

    if algo_selection.get() == 'DFS':
        node.predecessor = predecessor

    if node.coords != destination_coords:
        rect = node.shape
        pygame.draw.rect(screen, VISITED, rect)

        pygame.display.update()
    else:
        path_found = True


def highlight_path():
    """
    Highlights the path
    """
    global destination_coords, source_coords

    path_lenght = 0

    current = matrix[destination_coords[0], destination_coords[1]].predecessor
    source_node = matrix[source_coords[0], source_coords[1]]

    while current != source_node:
        rect = current.shape
        pygame.draw.rect(screen, PATH, rect)

        pygame.display.update()

        current = current.predecessor

        path_lenght += 1

    print(path_lenght)


def main():
    init_settings_window()

    while running:
        root.update()

        if pygame_started:
            check_for_events()

    root.destroy()


if __name__ == "__main__":
    main()
