import copy

# --- 1. Global Constants and Initial Board Setup ---
# Define the 8x8 board
board = [[None for _ in range(8)] for _ in range(8)]

# Piece notation:
# White pieces - uppercase: P, R, N, B, Q, K
# Black pieces - lowercase: p, r, n, b, q, k

# Define white and black pieces
white_back_row = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
white_pawns = ['P'] * 8

black_back_row = ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
black_pawns = ['p'] * 8

# Place the pieces on the board
board[0] = black_back_row        # Black back rank
board[1] = black_pawns          # Black pawns
board[2:6] = [[None]*8 for _ in range(4)]   # Empty rows in between
board[6] = white_pawns           # White pawns
board[7] = white_back_row        # White back rank

# --- 2. Helper Functions (General Utilities) ---

def print_board(board):
    """Function to print the board cleanly."""
    print("       a   b   c   d   e   f   g   h")
    print("  +" + "---+"*8)
    for i, row in enumerate(board):
        print(f"{8 - i} |", end="")
        for cell in row:
            if cell is None:
                print(" . |", end="")
            else:
                print(f" {cell} |", end="")
        print(f" {8 - i}")
        print("  +" + "---+"*8)
    print("       a   b   c   d   e   f   g   h")

def chess_notation_to_indices(move):
    """Function to convert move in chess notation to row, col indices."""
    chess_notation = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    start_pos, end_pos = move.split(' to ')
    start_col = chess_notation[start_pos[0].lower()]
    start_row = 8 - int(start_pos[1])
    end_col = chess_notation[end_pos[0].lower()]
    end_row = 8 - int(end_pos[1])
    return (start_row, start_col), (end_row, end_col)

def indices_to_chess_notation(pos):
    """Helper to turn (row, col) -> "e2"-style notation."""
    row, col = pos
    file = chr(col + ord('a'))       # 0 -> 'a', 1 -> 'b', …, 7 -> 'h'
    rank = str(8 - row)             # row 0 -> '8', row 7 -> '1'
    return file + rank

def parse_move(move):
    """Function to parse moves in algebraic notation (e.g., 'e2 to e4')."""
    start, end = move.split(" to ")
    start_col, start_row = ord(start[0]) - ord('a'), 8 - int(start[1])
    end_col, end_row = ord(end[0]) - ord('a'), 8 - int(end[1])
    return (start_row, start_col), (end_row, end_col)

# --- 3. Core Game Mechanics (Basic Actions) ---

def move_piece(board, start_pos, end_pos):
    """Function to move a piece."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    
    piece = board[start_row][start_col]
    board[start_row][start_col] = None
    board[end_row][end_col] = piece

# --- 4. Piece-Specific Move Validation Helpers (Unchanged from original) ---

def is_valid_pawn_move(board, start_pos, end_pos, color):
    """Checks if a pawn move is valid."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    direction = -1 if color == 'white' else 1   # White moves up (-1), Black moves down (+1)
    
    # Moving forward by 1
    if start_col == end_col:
        if end_row == start_row + direction and board[end_row][end_col] is None:
            return True
        # Moving forward by 2 from starting position
        if (start_row == 6 and color == 'white') or (start_row == 1 and color == 'black'):
            if end_row == start_row + 2 * direction and \
               board[start_row + direction][start_col] is None and \
               board[end_row][end_col] is None:
                return True

    # Capturing diagonally
    if abs(start_col - end_col) == 1 and end_row == start_row + direction:
        target = board[end_row][end_col]
        if target is not None:
            if (color == 'white' and target.islower()) or \
               (color == 'black' and target.isupper()):
                return True

    return False

def is_valid_rook_move(board, start_pos, end_pos):
    """Checks if a rook move is valid."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos

    if start_row != end_row and start_col != end_col:
        return False   # Must move in a straight line

    # Check if path is clear
    if start_row == end_row: # Horizontal move
        step = 1 if end_col > start_col else -1
        for col in range(start_col + step, end_col, step):
            if board[start_row][col] is not None:
                return False
    else: # Vertical move
        step = 1 if end_row > start_row else -1
        for row in range(start_row + step, end_row, step):
            if board[row][start_col] is not None:
                return False
    return True # Path is clear

def is_valid_knight_move(start_pos, end_pos):
    """Checks if a knight move is valid."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)
    return (row_diff, col_diff) in [(2, 1), (1, 2)]

def is_valid_bishop_move(board, start_pos, end_pos):
    """Checks if a bishop move is valid."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    row_diff = abs(start_row - end_row)
    col_diff = abs(start_col - end_col)

    if row_diff != col_diff:
        return False   # Must move diagonally

    row_step = 1 if end_row > start_row else -1
    col_step = 1 if end_col > start_col else -1

    for step in range(1, row_diff):
        if board[start_row + step * row_step][start_col + step * col_step] is not None:
            return False

    return True

def is_valid_queen_move(board, start_pos, end_pos):
    """Checks if a queen move is valid (combines rook and bishop moves)."""
    return is_valid_rook_move(board, start_pos, end_pos) or \
           is_valid_bishop_move(board, start_pos, end_pos)

def is_valid_king_move(start_pos, end_pos):
    """Checks if a king move is valid."""
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    return abs(start_row - end_row) <= 1 and abs(start_col - end_col) <= 1

# --- NEW: Piece-Specific Move Generation Functions (Extracted from second code) ---

def generate_pawn_moves(board, position, color):
    """Generates all possible moves for a pawn from its position."""
    moves = []
    row, col = position

    direction = -1 if color == 'white' else 1

    # Move forward one square
    if 0 <= row + direction < 8 and board[row + direction][col] is None:
        moves.append((row + direction, col))

        # Move two squares from starting row
        if (color == 'white' and row == 6) or (color == 'black' and row == 1):
            if board[row + 2*direction][col] is None:
                moves.append((row + 2*direction, col))

    # Capture diagonally (left)
    if 0 <= col - 1 < 8 and 0 <= row + direction < 8:
        target = board[row + direction][col - 1]
        if target is not None and ((color == 'white' and target.islower()) or (color == 'black' and target.isupper())):
            moves.append((row + direction, col - 1))

    # Capture diagonally (right)
    if 0 <= col + 1 < 8 and 0 <= row + direction < 8:
        target = board[row + direction][col + 1]
        if target is not None and ((color == 'white' and target.islower()) or (color == 'black' and target.isupper())):
            moves.append((row + direction, col + 1))
    return moves

def generate_rook_moves(board, position, color):
    """Generates all possible moves for a rook from its position."""
    moves = []
    row, col = position
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # (row_change, col_change)

    for dr, dc in directions:
        r, c = row + dr, col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]
            if target is None:
                moves.append((r, c))
            elif (color == 'white' and target.islower()) or (color == 'black' and target.isupper()):
                moves.append((r, c))
                break
            else:
                break
            r += dr
            c += dc
    return moves

def generate_knight_moves(board, position, color):
    """Generates all possible moves for a knight from its position."""
    moves = []
    row, col = position
    knight_directions = [
        (-2, -1), (-2, 1), (2, -1), (2, 1),
        (-1, -2), (-1, 2), (1, -2), (1, 2)
    ]

    for dr, dc in knight_directions:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]
            if target is None or (color == 'white' and target.islower()) or (color == 'black' and target.isupper()):
                moves.append((r, c))
    return moves

def generate_bishop_moves(board, position, color):
    """Generates all possible moves for a bishop from its position."""
    moves = []
    row, col = position
    directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        while 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]
            if target is None:
                moves.append((r, c))
            elif (color == 'white' and target.islower()) or (color == 'black' and target.isupper()):
                moves.append((r, c))
                break
            else:
                break
            r += dr
            c += dc
    return moves

def generate_queen_moves(board, position, color):
    """Generates all possible moves for a queen from its position (combines rook and bishop generation)."""
    # Queen moves are a combination of rook moves and bishop moves
    moves = generate_rook_moves(board, position, color)
    moves.extend(generate_bishop_moves(board, position, color))
    return moves

def generate_king_moves(board, position, color):
    """Generates all possible moves for a king from its position."""
    moves = []
    row, col = position
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                  (-1, -1), (-1, 1), (1, -1), (1, 1)]

    for dr, dc in directions:
        r, c = row + dr, col + dc
        if 0 <= r < 8 and 0 <= c < 8:
            target = board[r][c]
            # King cannot move into a square attacked by an opponent's piece,
            # but that check is handled by the overall is_valid_move later.
            # Here, we only check if the square is empty or has an opponent's piece.
            if target is None or \
               (color == 'white' and target.islower()) or \
               (color == 'black' and target.isupper()):
                moves.append((r, c))
    return moves

# --- 5. Comprehensive Move Validation ---

def is_valid_move(board, start_pos, end_pos, color):
    """
    Checks if a move is valid based on piece type, board boundaries,
    and whether it results in the king being in check.
    """
    start_row, start_col = start_pos
    end_row, end_col = end_pos
    piece = board[start_row][start_col]

    # 1. Basic checks
    if not (0 <= start_row < 8 and 0 <= start_col < 8 and 0 <= end_row < 8 and 0 <= end_col < 8):
        return False # Out of bounds
    if piece is None:
        return False   # No piece to move

    # Check piece color matches turn
    if (color == 'white' and not piece.isupper()) or \
       (color == 'black' and not piece.islower()):
        return False

    target = board[end_row][end_col]

    # Check if capturing own piece
    if target is not None:
        if (color == 'white' and target.isupper()) or \
           (color == 'black' and target.islower()):
            return False
        # Prevent capturing the king (this is a rule of chess; king is checkmated, not captured)
        if target.lower() == 'k': 
            return False

    # 2. Piece-specific movement rules (using the validation helpers)
    piece_type = piece.lower()
    valid_piece_move = False

    if piece_type == 'p':   # Pawn
        valid_piece_move = is_valid_pawn_move(board, start_pos, end_pos, color)
    elif piece_type == 'r':   # Rook
        valid_piece_move = is_valid_rook_move(board, start_pos, end_pos)
    elif piece_type == 'n':   # Knight
        valid_piece_move = is_valid_knight_move(start_pos, end_pos)
    elif piece_type == 'b':   # Bishop
        valid_piece_move = is_valid_bishop_move(board, start_pos, end_pos)
    elif piece_type == 'q':   # Queen
        valid_piece_move = is_valid_queen_move(board, start_pos, end_pos)
    elif piece_type == 'k':   # King
        valid_piece_move = is_valid_king_move(start_pos, end_pos)
    
    if not valid_piece_move:
        return False

    # 3. Check if move leaves king in check
    # Simulate the move on a temporary board
    temp_board = copy.deepcopy(board)
    move_piece(temp_board, start_pos, end_pos)
    
    if is_in_check(temp_board, color):
        return False # Cannot make a move that leaves own king in check

    return True

# --- MODIFIED: get_all_valid_moves to use explicit generation functions ---
def get_all_valid_moves(board, start_pos, color):
    """
    Returns a list of all legal moves for a specific piece at start_pos,
    considering if the move leaves the king in check.
    Uses explicit piece generation functions.
    """
    moves = []
    piece = board[start_pos[0]][start_pos[1]]
    if piece is None:
        return [] # No piece at start_pos

    piece_type = piece.lower()
    
    # Get potential moves using the explicit generation functions
    candidate_moves = []
    if piece_type == 'p':
        candidate_moves = generate_pawn_moves(board, start_pos, color)
    elif piece_type == 'r':
        candidate_moves = generate_rook_moves(board, start_pos, color)
    elif piece_type == 'n':
        candidate_moves = generate_knight_moves(board, start_pos, color)
    elif piece_type == 'b':
        candidate_moves = generate_bishop_moves(board, start_pos, color)
    elif piece_type == 'q':
        candidate_moves = generate_queen_moves(board, start_pos, color)
    elif piece_type == 'k':
        candidate_moves = generate_king_moves(board, start_pos, color)
    
    # Filter candidate moves to ensure they don't leave the king in check
    for end_pos in candidate_moves:
        # Note: is_valid_move already includes the deepcopy and is_in_check logic
        if is_valid_move(board, start_pos, end_pos, color):
            moves.append(end_pos)
            
    return moves

# --- 6. Game State Evaluation (for AI and End Conditions) ---

def evaluate_board(board):
    """Evaluates the board state for the AI."""
    piece_values = {
        'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000,
        'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -1000
    }
    score = 0
    for row in board:
        for piece in row:
            if piece:
                score += piece_values.get(piece, 0)
    return score

def get_all_moves(board, color):
    """
    Generates all legal moves for all pieces of a given color on the board.
    This is used by the AI to explore possible moves.
    """
    moves = []
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is None:
                continue
            if (color == 'white' and piece.isupper()) or \
               (color == 'black' and piece.islower()):
                start_pos = (row, col)
                # Now using the improved get_all_valid_moves
                for end_pos in get_all_valid_moves(board, start_pos, color):
                    moves.append((start_pos, end_pos))
    return moves

# --- 7. Check, Checkmate, and Stalemate Logic ---

def is_in_check(board, color):
    """Checks if the king of the given color is currently in check."""
    # Find the king's position
    king_pos = None
    for row in range(8):
        for col in range(8):
            if (color == 'white' and board[row][col] == 'K') or \
               (color == 'black' and board[row][col] == 'k'):
                king_pos = (row, col)
                break
        if king_pos:
            break
    
    if not king_pos:
        return False   # No king found (should ideally not happen in a valid game)

    # Check if any of the opponent's pieces can attack the king's position
    opponent_color = 'black' if color == 'white' else 'white'
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None and \
               ((color == 'white' and piece.islower()) or \
                (color == 'black' and piece.isupper())):
                
                # Create a temporary board to check hypothetical attacks without changing main board
                # This deepcopy is crucial to avoid modifying the actual board during hypothetical checks
                temp_board_for_attack_check = copy.deepcopy(board) 
                
                opponent_piece_type = piece.lower()
                can_attack = False
                # For checking attack, we need to consider how pieces *attack*, not just how they move normally
                # Pawns attack diagonally, other pieces attack by moving onto the square.
                if opponent_piece_type == 'p':
                    direction = -1 if opponent_color == 'white' else 1
                    # Pawns attack diagonally
                    if (king_pos[0] == row + direction and abs(king_pos[1] - col) == 1):
                        can_attack = True
                elif opponent_piece_type == 'r':
                    can_attack = is_valid_rook_move(temp_board_for_attack_check, (row, col), king_pos)
                elif opponent_piece_type == 'n':
                    can_attack = is_valid_knight_move((row, col), king_pos)
                elif opponent_piece_type == 'b':
                    can_attack = is_valid_bishop_move(temp_board_for_attack_check, (row, col), king_pos)
                elif opponent_piece_type == 'q':
                    can_attack = is_valid_queen_move(temp_board_for_attack_check, (row, col), king_pos)
                elif opponent_piece_type == 'k':
                    # A king can attack an opponent's king if they are adjacent
                    # This check is mainly to ensure kings don't move into adjacent squares
                    can_attack = is_valid_king_move((row, col), king_pos)
                
                if can_attack:
                    return True   # The king is in check

    return False   # The king is not in check


def is_checkmate(board, color):
    """Checks if the king of the given color is in checkmate."""
    if not is_in_check(board, color):
        return False   # The king is not in check, so it's not checkmate
    
    # Check if the player has any legal moves to get out of check
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None and \
               ((color == 'white' and piece.isupper()) or \
                (color == 'black' and piece.islower())):
                
                # Get all *valid* moves for this piece (which includes king safety check)
                possible_moves_for_piece = get_all_valid_moves(board, (row, col), color)
                if possible_moves_for_piece:
                    return False   # Found at least one legal move, so not checkmate

    return True   # No legal moves to get out of check, it's checkmate


def is_stalemate(board, color):
    """Checks if the king of the given color is in stalemate."""
    if is_in_check(board, color):
        return False   # If the king is in check, it's not stalemate
    
    # Check if the player has any legal moves left
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None and \
               ((color == 'white' and piece.isupper()) or \
                (color == 'black' and piece.islower())):
                
                # Get all *valid* moves for this piece (which includes king safety check)
                possible_moves_for_piece = get_all_valid_moves(board, (row, col), color)
                if possible_moves_for_piece:
                    return False   # There is at least one valid move, so it's not stalemate
    
    return True   # No valid moves, and not in check, it's stalemate

# --- 8. AI Algorithms ---

def minimax(board, depth, is_maximizing, color):
    """Minimax algorithm for AI decision making."""
    # Terminal node conditions
    if depth == 0 or is_checkmate(board, color) or is_stalemate(board, color):
        return evaluate_board(board), None

    best_move = None
    opponent_color = 'black' if color == 'white' else 'white'

    if is_maximizing: # AI's turn (or the maximizing player's turn)
        max_eval = float('-inf')
        for move in get_all_moves(board, color):
            new_board = copy.deepcopy(board)
            move_piece(new_board, move[0], move[1])
            eval_score, _ = minimax(new_board, depth - 1, False, opponent_color) # Recursively call for minimizing player
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
        return max_eval, best_move
    else: # Opponent's turn (or the minimizing player's turn)
        min_eval = float('inf')
        for move in get_all_moves(board, color):
            new_board = copy.deepcopy(board)
            move_piece(new_board, move[0], move[1])
            eval_score, _ = minimax(new_board, depth - 1, True, opponent_color) # Recursively call for maximizing player
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
        return min_eval, best_move

def alphabeta(board, depth, alpha, beta, maximizing_player, color):
    """
    Alpha-Beta pruning search.
    Returns (best_score, best_move)
    """
    # Terminal or quiescence test
    if depth == 0 or is_checkmate(board, color) or is_stalemate(board, color):
        return evaluate_board(board), None

    best_move = None
    opponent_color = 'black' if color == 'white' else 'white'

    if maximizing_player:
        value = float('-inf')
        for move in get_all_moves(board, color):
            new_board = copy.deepcopy(board)
            move_piece(new_board, move[0], move[1])
            score, _ = alphabeta(new_board, depth - 1, alpha, beta, False, opponent_color)
            if score > value:
                value, best_move = score, move
            alpha = max(alpha, value)
            if alpha >= beta:
                break   # β-cutoff
        return value, best_move
    else: # Minimizing player
        value = float('inf')
        for move in get_all_moves(board, color):
            new_board = copy.deepcopy(board)
            move_piece(new_board, move[0], move[1])
            score, _ = alphabeta(new_board, depth - 1, alpha, beta, True, opponent_color)
            if score < value:
                value, best_move = score, move
            beta = min(beta, value)
            if beta <= alpha:
                break   # α-cutoff
        return value, best_move

def get_best_move_ab(board, color, depth=3):
    """
    Returns the best move found by alpha-beta search to the given depth.
    """
    # Check if there are any legal moves at all for the current player
    all_possible_moves = get_all_moves(board, color)
    if not all_possible_moves:
        return None # Indicate no moves available
        
    _, move = alphabeta(board, depth, float('-inf'), float('inf'), True, color)
    return move

# --- 9. User Input / Console Game Turn Handling ---

def get_move_input(board, color):
    """Handles user input, parses, validates, and applies the move."""
    while True:
        # Directly prompt for the move, removing the "Press 1" choice
        move_str = input(f"Enter your move for {color} (e.g., e2 to e4): ")
        try:
            start_pos, end_pos = parse_move(move_str)
            if is_valid_move(board, start_pos, end_pos, color):
                move_piece(board, start_pos, end_pos)
                print(f"{color.capitalize()} moved from {indices_to_chess_notation(start_pos)} to {indices_to_chess_notation(end_pos)}")
                return # Exit the loop and function upon valid move
            else:
                print("Invalid move. Try again.")
                # Loop continues to prompt again
        except (ValueError, IndexError):
            print("Invalid move format. Please enter in the format 'e2 to e4'.")
            # Loop continues to prompt again



def main():
    """Main function to run the console chess game."""
    # Reinitialize board for the game loop (global 'board' might be modified by tests)
    game_board = [
        ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
        ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
        [None]*8, [None]*8, [None]*8, [None]*8,
        ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
        ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
    ]

    while True:
        # --- White (human) move ---
        print_board(game_board)
        print("\n--- White's Turn (Human) ---")
        
        # Check for White's immediate game over conditions before asking for move
        if is_checkmate(game_board, 'white'):
            print_board(game_board)
            print("Checkmate! Black wins!")
            break
        if is_stalemate(game_board, 'white'):
            print_board(game_board)
            print("Stalemate — draw.")
            break
        
        get_move_input(game_board, 'white') # This function now directly asks for input

        # Check after White’s move for Black’s conditions
        if is_checkmate(game_board, 'black'):
            print_board(game_board)
            print("Checkmate! White wins!")
            break
        if is_stalemate(game_board, 'black'):
            print_board(game_board)
            print("Stalemate — draw.")
            break

        # --- Black (AI) move ---
        print_board(game_board)
        print("\n--- Black's Turn (AI) ---")
        print("AI (black) is thinking...")
        
        best_move = get_best_move_ab(game_board, 'black', depth=3) # Using depth=3 as before

        if best_move:
            move_piece(game_board, best_move[0], best_move[1])
            a1 = indices_to_chess_notation(best_move[0])
            a2 = indices_to_chess_notation(best_move[1])
            print(f"Black AI moved from {a1} to {a2}")
        else:
            # AI has no valid moves. Determine if it's checkmate or stalemate for AI.
            if is_checkmate(game_board, 'black'):
                print_board(game_board)
                print("Checkmate! White wins!") # AI is in checkmate, human wins
            elif is_stalemate(game_board, 'black'):
                print_board(game_board)
                print("Stalemate — draw.") # AI is in stalemate, draw
            else:
                print("AI has no valid moves (unexpected state). Game over.") # Fallback for unexpected case
            break # Game ends if AI has no moves

        # Check after Black’s move for White’s conditions
        if is_checkmate(game_board, 'white'):
            print_board(game_board)
            print("Checkmate! Black wins!")
            break
        if is_stalemate(game_board, 'white'):
            print_board(game_board)
            print("Stalemate — draw.")
            break

        # Optional: continue? (Removed this from the GUI context, but keeping for console here)
        if input("Continue? (y/n): ").lower() != 'y':
           break

# --- 12. Entry Point ---

if __name__ == "__main__":
  
    main()
