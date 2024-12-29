from ninja import NinjaAPI, Schema
from ninja.errors import HttpError
from ninja.responses import JsonResponse
from typing import Annotated, Union
from django.conf import settings
from ravenback.game.checkers import Checkers, calc_ai_move
from ravenback.parsing.PDN import PDNReader, PDNWriter, translate_to_fen
from ravenback.util.globalconst import keymap


# Initialize NinjaAPI
api = NinjaAPI()

# Middleware setup is handled in Django settings (e.g., CORS and SessionMiddleware)

# Endpoint to create a session
@api.post("/create_session")
def create_session(request, fen: Annotated[Union[str, None], str] = None):
    board = Checkers()
    state = board.curr_state
    if fen:
        try:
            reader = PDNReader(None)
            game_params = reader.game_params_from_fen(fen)
            state.setup_game(game_params)
        except RuntimeError:
            raise HttpError(422, "Invalid FEN string")

    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state()
    fen_dict = {
        "fen": translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings)
    }
    #deta = Deta(settings.DETA_SPACE_DATA_KEY)
    #db = deta.Base("raven_db")
    #db_entry = db.put(fen_dict, "session")
    db_entry = None
    return JsonResponse(db_entry)

# Endpoint to end a session
@api.post("/end_session")
def end_session(request):
    #deta = Deta(settings.DETA_SPACE_DATA_KEY)
    #db = deta.Base("raven_db")
    #db.delete("session")
    return JsonResponse({"message": "Session ended."})

# Endpoint to get legal moves
@api.get("/legal_moves")
def legal_moves(request, fen: Annotated[Union[str, None], str] = None):
    board = Checkers()
    state = board.curr_state
    if fen:
        try:
            reader = PDNReader(None)
            game_params = reader.game_params_from_fen(fen)
            state.setup_game(game_params)
        except (SyntaxError, RuntimeError) as e:
            raise HttpError(422, e.args[0])

    captures = [
        [keymap[sq[0]] for sq in capture.affected_squares[::2]]
        for capture in board.curr_state.captures
    ]

    moves = [
        [keymap[sq[0]] for sq in move.affected_squares]
        for move in board.curr_state.moves
    ] if not captures else []

    captures.sort()
    moves.sort()
    return JsonResponse({"captures": captures, "moves": moves})

# Endpoint to get the checkerboard state
@api.get("/cb_state")
def get_checkerboard_state(request):
    #deta = Deta(settings.DETA_SPACE_DATA_KEY)
    #db = deta.Base("raven_db")
    #result = db.get("session")
    #if not result:
    #    return JsonResponse({"message": "Session not found."}, status=404)
    result = {}
    return JsonResponse({"fen": result["fen"]})

# Endpoint to make a move
@api.post("/make_move")
def make_move(request, start_sq: int, end_sq: int):
    #deta = Deta(settings.DETA_SPACE_DATA_KEY)
    #db = deta.Base("raven_db")
    #result = db.get("session")
    result = {}
    if not result:
        return JsonResponse({"message": "Session not found."}, status=404)

    reader = PDNReader(None)
    game_params = reader.game_params_from_fen(result["fen"])
    board = Checkers()
    state = board.curr_state
    state.setup_game(game_params)

    legal_moves = state.captures or state.moves
    found_move = False
    for move in legal_moves:
        move_start = move.affected_squares[0][0]
        move_end = move.affected_squares[-1][0]
        if start_sq == keymap[move_start] and end_sq == keymap[move_end]:
            state.make_move(move, False, False)
            found_move = True
            break

    if not found_move:
        return JsonResponse({"message": "Illegal move. Check squares, along with player turn."}, status=404)

    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state()
    fen_dict = {
        "fen": translate_to_fen(next_to_move, black_men, white_men, black_kings, white_kings)
    }
    #db_entry = db.put(fen_dict, "session")
    db_entry = None
    return JsonResponse(db_entry)

# Endpoint to calculate AI move
@api.post("/calc_move/")
def calc_move(request, search_time: int):
    #deta = Deta(settings.DETA_SPACE_DATA_KEY)
    #db = deta.Base("raven_db")
    #result = db.get("session")
    result = {}
    if not result:
        return JsonResponse({"message": "Session not found."}, status=404)

    reader = PDNReader(None)
    game_params = reader.game_params_from_fen(result["fen"])
    board = Checkers()
    state = board.curr_state
    state.setup_game(game_params)

    move = calc_ai_move(board, search_time)
    if not move:
        return JsonResponse({"message": "Could not find move within search time."}, status=404)

    state.make_move(move, False, False)
    next_to_move, black_men, black_kings, white_men, white_kings = state.save_board_state()
    pdn = {
        "pdn": PDNWriter.to_string(
            '', '', '', '', '', '', next_to_move, black_men, white_men, black_kings, white_kings, '', 'white_on_top', []
        )
    }
    #db.put(pdn, "session")
    move_start = move.affected_squares[0][0]
    move_end = move.affected_squares[-1][0]
    move_dict = {"start_sq": keymap[move_start], "end_sq": keymap[move_end]}
    return JsonResponse(move_dict)
