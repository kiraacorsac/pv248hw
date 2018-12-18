import sys
import http.client
import json
import time


def get_display(number):
    return "x" if number == 1 else "o" if number == 2 else "_"

host = sys.argv[1]
port = int(sys.argv[2])

def GETRequest(ttt, command, variables):
    variables = list(map(lambda var: var + "=" + str(variables[var]), variables))
    variables = "&".join(variables)
    connection_string = "/" + command + "?" + variables
    ttt.request("GET", connection_string)
    return ttt.getresponse()
    
def request_status(ttt, game):
    return GETRequest(ttt, "status", {"game": game})

def draw_board(board):
    for row in board:
        for col in row:
            print(get_display(col), end = "")
        print()

def prompt_coordinates(board, player):
    while(True):
        x, y = input("your turn (" + get_display(player) + ")").split(" ")
        check_coor = lambda coor: coor.isnumeric() and int(coor) >= 0 and int(coor) < 3
        if check_coor(x) and check_coor(y) and board[int(x)][int(y)] == 0:
            return int(x), int(y)
        print("invalid input")


def poll(ttt, game, player):
    first = True
    while (True):
        status = request_status(ttt, game)
        if status.status == 200:
            state = json.loads(status.read())
            if "winner" in state:
                return (state["winner"], state["board"])
            if "next" in state:
                if state["next"] == player:
                    return (None, state["board"])
                else:
                    if first:
                        print("waiting for the other player")
                        first = False
                    time.sleep(1)


def play(ttt, game_id, player):
    while (True):
        winner, board = poll(ttt, game_id, player)
        draw_board(board)
        if winner is not None:
            print("you " + ("win" if winner == player else "lose") if winner != 0 else "draw")
            break
        x, y = prompt_coordinates(board, player)
        GETRequest(ttt, "play", {"x": x, "y": y, "player": player, "game": game_id})
        

ttt = http.client.HTTPConnection(host, port)
game_list = GETRequest(ttt, "list", {})

if (game_list.status == 200):
    games = dict(map(lambda game: (dict(game)['id'], dict(game)['name']), json.loads(game_list.read())))
    for game in games:
        print(game, games[game])

prompt = input("Select game or type 'new': ")
if prompt.isnumeric() and int(prompt) in games:
    player = 2
    game_id = int(prompt)
    print("")
elif prompt[:3] == "new":
    name = prompt[3:].strip()
    try:
        new_game = GETRequest(ttt, "start", {"name": name})
        game_id = json.loads(new_game.read())["id"]
    except Exception:
        print("Sum-tin wong: ")
        exit(0)
    player = 1
else:
    print("Wrong game selec")

play(ttt, game_id, player)