import sys
import urllib.parse
import json
from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    #lel
    pass

games_dict = {}

class TTT():
    def __init__(self, name):
        self.name = name
        self.id = len(games_dict) #todo
        self.over = False
        self.winner = 0
        self.game_board = [[0] * 3, [0] * 3, [0] * 3]
        self.next = 1
        games_dict[self.id] = self

    def update(self, row, col):
        self.game_board[row][col] = self.next
        self.try_win()
        self.next = 1 if self.next == 2 else 2

    def is_empty(self):
        for row in self.game_board:
            for col in row:
                if col != 0:
                    return False
        return True

    def are_same(self, array):
        return False if array[0] == 0 else array.count(array[0]) == 3

    def try_win(self):
        win = False
        coords = [0, 1, 2]

        for row in coords:
            win |= self.are_same([self.game_board[row][col] for col in coords])
        for col in coords:
            win |= self.are_same([self.game_board[row][col] for row in coords])
        win |= self.are_same([self.game_board[coor][coor] for coor in coords])
        win |= self.are_same([self.game_board[coor][len(coords) - 1 - coor] for coor in coords])

        self.over = win or (0 not in [n for s in self.game_board for n in s])
        self.winner = self.next if win else 0




class TTTHandler(BaseHTTPRequestHandler):
    def respond(self, resp):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(json.dumps(resp), "utf8"))
    
    def do_GET(self):
        try:
            request_url = urllib.parse.urlparse(self.path)
            query = dict(urllib.parse.parse_qsl(request_url.query))
            command = request_url.path[1:]
            if command == "start":
                game = TTT(query.get("name", ""))
                response = {
                    "id": game.id
                }
                self.respond(response)
            
            elif command == "list":
                response = []
                for game in games_dict.values():
                    if game.is_empty():
                        response.append({
                            "name": game.name,
                            "id": game.id
                        })
                self.respond(response)

            elif command == "status":
                if "game" in query and query["game"].isnumeric() and int(query["game"]) in games_dict:
                    game = games_dict[int(query["game"])]
                    if game.over:
                        response = {
                            "board": game.game_board,
                            "winner": game.winner
                        }
                    else:
                        response = {
                            "board": game.game_board,
                            "next": game.next
                        }
                    self.respond(response)
                else:
                    self.send_error(400)

            elif command == "play":
                if "game" in query and query["game"].isnumeric() and int(query["game"]) in games_dict:

                    game = games_dict[int(query["game"])]
                    player_check = "player" in query and query["player"].isnumeric() and game.next == int(query["player"])
                    check_coor = lambda coor: coor in query and query[coor].isnumeric() and int(query[coor]) >= 0 and int(query[coor]) < 3

                    if not player_check:
                        response = {
                            "status": "bad",
                            "message": u"player incorrect or missing (✖╭╮✖)"
                        }
                    elif not check_coor("x") or not check_coor("y"):
                        response = {
                            "status": "bad",
                            "message": u"coordinates incorrect or missing (∩︵∩)"
                        }
                    elif not game.game_board[int(query["y"])][int(query["x"])] == 0:
                        response = {
                            "status": "bad",
                            "message": u"coordinates taken (◕︿◕✿)"
                        }
                    else:
                        game.update(int(query["y"]), int(query["x"]))
                        response = {
                            "status": "ok"
                        }
                    self.respond(response)

                else:
                    self.send_error(400)

            else:
                self.send_error(404)
                
        except Exception as e:
            print(e)
            self.send_error(418)


        



port = int(sys.argv[1])

server = ThreadedHTTPServer(("", port), TTTHandler)
server.serve_forever()