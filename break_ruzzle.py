from collections import defaultdict
import json
import math

class GridPath:
    letter_pts = dict(
	a = 1,
	b = 4,
	c = 4,
	d = 2,
	e = 1,
	f = 4,
	g = 3,
	h = 4,
	i = 1,
	j = 10,
	k = 5,
	l = 1,
	m = 3,
	n = 1,
	o = 1,
	p = 4,
	q = 0,
	r = 1,
	s = 1,
	t = 1,
	u = 2,
	v = 4,
	w = 4,
	x = 0,
	y = 4,
	z = 0
    )

    def __init__(self, grid):
        if grid is None:
            self.grid_positions = []
        else:
            self.grid_positions = grid.grid_positions.copy()

    def add(self, row, col):
        self.grid_positions.append(Node(row, col))

    def is_visited(self, row, col):
        for grid_position in self.grid_positions:
            if grid_position.row == row and grid_position.col == col:
                return True
        return False

    def to_string(self, grid):
        word = ""
        for grid_position in self.grid_positions:
            word += grid[grid_position.row][grid_position.col]
        return word

    def get_points(self, grid, special_nodes):
        length_score = 0
        num_letters = len(self.grid_positions)
        if num_letters <= 4:
            length_score = 0
        elif num_letters <= 5:
            length_score = 5
        elif num_letters <= 6:
            length_score = 10
        elif num_letters <= 7:
            length_score = 15
        elif num_letters <= 8:
            length_score = 20
        else:
            length_score = 25

        word_score = 0
        double_word = False
        triple_word = False
        for grid_position in self.grid_positions:
            row = grid_position.row
            col = grid_position.col

            char = grid[row][col]
            pts = self.letter_pts[char]

            if special_nodes[row * 4 + col] == "DL":
                pts = pts * 2
            elif special_nodes[row * 4 + col] == "TL":
                pts = pts * 3
            elif special_nodes[row * 4 + col] == "DW":
                double_word = True
            elif special_nodes[row * 4 + col] == "TW":
                triple_word = True

            word_score += pts

        total_score = word_score
        if triple_word:
            total_score += (3 * word_score)
        if double_word:
            total_score += (2 * word_score)
        return total_score + length_score

    def get_nodes(self):
        nodes = []
        for grid_position in self.grid_positions:
            nodes.append(str(grid_position.row) + "," + str(grid_position.col))
        return ";".join(nodes)

class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def equals(self, other):
        other.row == self.row and other.col == self.col

    def to_string(self, ):
        str(self.row) + str(self.col)

def load_dictionary():
    dictionary = []
    with open("dictionary.txt") as dictionary_file:
        dictionary = dictionary_file.read().splitlines()
    
    return dictionary

found_words = defaultdict(list)
dictionary = load_dictionary()

def execute(event, context):
    grid = get_cell_grid(event)
    print(grid)
    special_cells = get_special_cells(event)

    solve(grid)
    puzzles = create_puzzles(grid, special_cells)

    total_stats = get_number_of_words(puzzles)
    special_words = get_special_words(puzzles)

    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(dict(
            puzzles = puzzles,
            total_stats = total_stats,
            special_words = special_words
        ))
    }

    return response


def get_cell_grid(event):
    cells = event["queryStringParameters"]["grid"].split(",")
    print(cells)
    grid = []
    for row in range(0,4):
        grid.append([])
        for col in range(0,4):
            cell_entry = cells[row * 4 + col]
            grid[row].append(cell_entry)
    
    return grid

def get_special_cells(event):
    return event["queryStringParameters"]["specialCells"].split(",")

def solve(grid):
    for row in range(0, 4):
        for col in range(0, 4):
            string_so_far = grid[row][col]
            path_so_far = GridPath(None)
            solve_with_string_so_far(grid, row, col, row, col, string_so_far, path_so_far)

def solve_with_string_so_far(grid, starting_row, starting_col, current_row, current_col, string_so_far, path_so_far):
    path_so_far.add(current_row, current_col)
    if maybe_in_dictionary(string_so_far):
        for node in get_available_nodes(current_row, current_col, path_so_far):
            next_string = string_so_far
            next_string += grid[node.row][node.col]
            new_grid_path = GridPath(path_so_far)

            solve_with_string_so_far(grid, starting_row, starting_col, node.row, node.col, next_string, new_grid_path)

    if is_in_dictionary(string_so_far):
        print(string_so_far)
        found_words[str(starting_row) + str(starting_col)].append(path_so_far)


def maybe_in_dictionary(search_word):
    start_index = 0
    end_index = len(dictionary) - 1
    return maybe_in_dictionary_helper(search_word, start_index, end_index)

def maybe_in_dictionary_helper(search_word, start_index, end_index):
    mid_index = math.floor((start_index + end_index) / 2)
    mid_word = dictionary[mid_index]
    if len(mid_word) >= len(search_word):
        mid_word = mid_word[0:len(search_word)]

    if start_index == end_index:
        return search_word == mid_word
    elif search_word < mid_word:
        return maybe_in_dictionary_helper(search_word, start_index, mid_index)
    elif search_word > mid_word:
        return maybe_in_dictionary_helper(search_word, mid_index + 1, end_index)
    else:
        return True

def is_in_dictionary(search_word):
    start_index = 0
    end_index = len(dictionary) - 1
    return is_in_dictionary_helper(search_word, start_index, end_index)

def is_in_dictionary_helper(search_word, start_index, end_index):
    mid_index = math.floor((start_index + end_index) / 2)
    mid_word = dictionary[mid_index]

    if start_index == end_index:
        return search_word == mid_word
    elif search_word < mid_word:
        return is_in_dictionary_helper(search_word, start_index, mid_index)
    elif search_word > mid_word:
        return is_in_dictionary_helper(search_word, mid_index + 1, end_index)
    else:
        return True

def get_available_nodes(row, col, temp_grid):
    nodes = []
    add_if_available(row - 1, col - 1, temp_grid, nodes)
    add_if_available(row - 1, col    , temp_grid, nodes)
    add_if_available(row - 1, col + 1, temp_grid, nodes)
    add_if_available(row    , col - 1, temp_grid, nodes)
    add_if_available(row    , col    , temp_grid, nodes)
    add_if_available(row    , col + 1, temp_grid, nodes)
    add_if_available(row + 1, col - 1, temp_grid, nodes)
    add_if_available(row + 1, col    , temp_grid, nodes)
    add_if_available(row + 1, col + 1, temp_grid, nodes)
    return nodes

def add_if_available(row, col, temp_grid, nodes):
    if row >= 0 and row <= 3:
        if col >= 0 and col <= 3:
            if temp_grid.is_visited(row, col) == False:
                nodes.append(Node(row, col))
    return nodes

def create_puzzles(grid, special_cells):
    puzzles = []

    def word_key(word):
        return word["pts"]

    def puzzle_key(puzzle):
        return str(puzzle["row"]) + str(puzzle["col"])

    for key, values in found_words.items():
        row = key[0]
        col = key[1]

        words = []
        for value in values:
            word = value.to_string(grid)
            pts = value.get_points(grid, special_cells)
            nodes = value.get_nodes()
            words.append(dict(word=word, pts=pts, nodes=nodes))

        sorted(words, key=word_key)

        puzzles.append(dict(row=row, col=col, words=words))

    sorted(puzzles, key=puzzle_key)

    return puzzles

def get_number_of_words(puzzles):
    count = 0
    total_pts = 0
    for puzzle in puzzles:
        count += len(puzzle["words"])
        for word in puzzle["words"]:
            total_pts += word["pts"]
    return dict(count=count, total_pts=total_pts)

def get_special_words(puzzles):
    top_word = ""
    top_pts = 0
    longest_word = ""
    longest_word_length = 0
    longest_word_pts = 0
    for puzzle in puzzles:
        for puzzle_entry in puzzle["words"]:
            word = puzzle_entry["word"]
            pts = puzzle_entry["pts"]
            length = len(word)
            if pts > top_pts:
                top_word = word
                top_pts = pts
            if length > longest_word_length:
                longest_word = word
                longest_word_length = length
                longest_word_pts = pts

    return dict(top_word=top_word, top_pts=top_pts, longest_word=longest_word, longest_word_pts=longest_word_pts)

