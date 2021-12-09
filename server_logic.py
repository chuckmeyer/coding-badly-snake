from algoliasearch.search_client import SearchClient
import random
from typing import List, Dict
import os

ALGOLIA_APP_ID = os.environ['ALGOLIA_APP_ID']
ALGOLIA_API_KEY = os.environ['ALGOLIA_API_KEY']

client = SearchClient.create(ALGOLIA_APP_ID, ALGOLIA_API_KEY)

"""
This file can be a nice home for your move logic, and to write helper functions.

We have started this for you, with a function to help remove the 'neck' direction
from the list of possible moves!
"""

def apple_vision(size: int, my_head: Dict[str, int], board: Dict[str, int]) -> str:
    vision = ''
    x_range = range(my_head['x'] - size//2, my_head['x'] + size//2 + 1)
    y_range = range(my_head['y'] - size//2, my_head['y'] + size//2 + 1)

    for y in y_range:
        for x in x_range:
            space = "S"
            if my_head["x"] == x and my_head["y"] == y:
                space = "H"
            else:
                for apple in board["food"]:
                    if x == apple["x"] and y == apple["y"]:
                        space = "O"
            vision += space
    return vision


def find_food(size: int, vision: str, possible_moves: List[str]) -> List[str]:
    best_moves = []
    index_name = 'boards-apples-' + str(size) + 'x' + str(size)
    index = client.init_index(index_name)
    results = index.search(vision)
    if results['hits']:
        for move in results['hits'][0]['best_move']:
            if move in possible_moves:
                best_moves.append(move)
    return best_moves


def remove_move(move: str, possible_moves: List[str]) -> List[str]:
    if move in possible_moves:
        possible_moves.remove(move)
    return possible_moves


def avoid_walls(my_head: Dict[str, int], board: Dict[str, int], possible_moves: List[str]) -> List[str]:
    top_row = board["height"] - 1
    right_column = board["width"] - 1

    if my_head["x"] == 0:  # near left wall
        print("Detected left wall")
        remove_move("left", possible_moves)
    elif my_head["x"] == right_column:  # near right wall
        print("Detected right wall")
        remove_move("right", possible_moves)

    if my_head["y"] == 0:  # near bottom wall
        print("Detected bottom wall")
        remove_move("down", possible_moves)
    elif my_head["y"] == top_row:  # near top wall
        print("Detected top wall")
        remove_move("up", possible_moves)

    return possible_moves


def avoid_my_neck(my_head: Dict[str, int], my_body: List[dict], possible_moves: List[str]) -> List[str]:
    """
    my_head: Dictionary of x/y coordinates of the Battlesnake head.
            e.g. {"x": 0, "y": 0}
    my_body: List of dictionaries of x/y coordinates for every segment of a Battlesnake.
            e.g. [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    possible_moves: List of strings. Moves to pick from.
            e.g. ["up", "down", "left", "right"]

    return: The list of remaining possible_moves, with the 'neck' direction removed
    """
    my_neck = my_body[1]  # The segment of body right after the head is the 'neck'

    if my_neck["x"] < my_head["x"]:  # my neck is left of my head
        possible_moves.remove("left")
    elif my_neck["x"] > my_head["x"]:  # my neck is right of my head
        possible_moves.remove("right")
    elif my_neck["y"] < my_head["y"]:  # my neck is below my head
        possible_moves.remove("down")
    elif my_neck["y"] > my_head["y"]:  # my neck is above my head
        possible_moves.remove("up")

    return possible_moves


def choose_move(data: dict) -> str:
    """
    data: Dictionary of all Game Board data as received from the Battlesnake Engine.
    For a full example of 'data', see https://docs.battlesnake.com/references/api/sample-move-request

    return: A String, the single move to make. One of "up", "down", "left" or "right".

    Use the information in 'data' to decide your next move. The 'data' variable can be interacted
    with as a Python Dictionary, and contains all of the information about the Battlesnake board
    for each move of the game.

    """
    my_head = data["you"]["head"]  # A dictionary of x/y coordinates like {"x": 0, "y": 0}
    my_body = data["you"]["body"]  # A list of x/y coordinate dictionaries like [ {"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 2, "y": 0} ]
    my_vision = apple_vision(5, my_head, data["board"])

    # TODO: uncomment the lines below so you can see what this data looks like in your output!
    # print(f"~~~ Turn: {data['turn']}  Game Mode: {data['game']['ruleset']['name']} ~~~")
    # print(f"All board data this turn: {data}")
    # print(f"My Battlesnakes head this turn is: {my_head}")
    # print(f"My Battlesnakes body this turn is: {my_body}")

    possible_moves = ["up", "down", "left", "right"]

    # Don't allow your Battlesnake to move back in on it's own neck
    possible_moves = avoid_my_neck(my_head, my_body, possible_moves)

    # TODO: Using information from 'data', find the edges of the board and don't let your Battlesnake move beyond them
    # board_height = ?
    # board_width = ?
    possible_moves = avoid_walls(my_head, data["board"], possible_moves)

    # TODO Using information from 'data', don't let your Battlesnake pick a move that would hit its own body

    # TODO: Using information from 'data', don't let your Battlesnake pick a move that would collide with another Battlesnake

    # TODO: Using information from 'data', make your Battlesnake move towards a piece of food on the board
    best_moves = find_food(5, my_vision, possible_moves)

    # Choose a random direction from the remaining possible_moves to move in, and then return that move
    if possible_moves:
        for best_move in best_moves:
            if best_moves in possible_moves:
                move = best_move
                print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked as best move {possible_moves}")
    if not move:
        move = random.choice(possible_moves)
        print(f"{data['game']['id']} MOVE {data['turn']}: {move} picked randomly from all valid options in {possible_moves}")
    
    # TODO: Explore new strategies for picking a move that are better than random

    return move
