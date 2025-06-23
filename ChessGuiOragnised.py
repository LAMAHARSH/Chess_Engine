import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from ChessBoardOrganised import (
    board,
    move_piece,
    is_valid_move,
    get_best_move_ab,
    is_checkmate,
    is_stalemate,
    indices_to_chess_notation,
)

CELL_SIZE = 60

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game - Human vs AI")
        self.canvas = tk.Canvas(self.root, width=8 * CELL_SIZE, height=8 * CELL_SIZE)
        self.canvas.pack()
        self.selected = None
        self.color_turn = "white"
        self.piece_images = self.load_piece_images()
        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)

    def load_piece_images(self):
        images = {}
        base_path = os.path.join(os.path.dirname(__file__), "ChessPieces")
        piece_map = {
            'K': 'king-w', 'Q': 'queen-w', 'R': 'rook-w', 'B': 'bishop-w', 'N': 'knight-w', 'P': 'pawn-w',
            'k': 'king-b', 'q': 'queen-b', 'r': 'rook-b', 'b': 'bishop-b', 'n': 'knight-b', 'p': 'pawn-b',
        }
        for piece_code, filename in piece_map.items():
            path = os.path.join(base_path, f"{filename}.png")
            img = Image.open(path).resize((CELL_SIZE, CELL_SIZE), Image.Resampling.LANCZOS)
            images[piece_code] = ImageTk.PhotoImage(img)
        return images

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(8):
            for col in range(8):
                x1, y1 = col * CELL_SIZE, row * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                color = "white" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

                # Highlight selected cell
                if self.selected == (row, col):
                    self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3)

                piece = board[row][col]
                if piece:
                    img = self.piece_images.get(piece)
                    if img:
                        self.canvas.create_image(x1, y1, image=img, anchor="nw")

    def on_click(self, event):
        col = event.x // CELL_SIZE
        row = event.y // CELL_SIZE
        print(f"Clicked at row: {row}, col: {col}")

        if self.selected:
            start_row, start_col = self.selected
            if is_valid_move(board, (start_row, start_col), (row, col), self.color_turn):
                move_piece(board, (start_row, start_col), (row, col))
                print(
                    f"{self.color_turn.capitalize()} moved from {indices_to_chess_notation((start_row, start_col))} "
                    f"to {indices_to_chess_notation((row, col))}"
                )
                self.selected = None
                self.color_turn = "black"
                self.draw_board()

                if is_checkmate(board, "black"):
                    messagebox.showinfo("Game Over", "Checkmate! White wins!")
                    return
                if is_stalemate(board, "black"):
                    messagebox.showinfo("Game Over", "Stalemate! Draw!")
                    return

                self.root.after(400, self.ai_move)
            else:
                print("Invalid move, try again.")
                self.selected = None
        else:
            if (
                board[row][col]
                and self.color_turn == "white"
                and board[row][col].isupper()
            ):
                self.selected = (row, col)

        self.draw_board()

    def ai_move(self):
        best_move = get_best_move_ab(board, "black", depth=3)
        if best_move:
            move_piece(board, best_move[0], best_move[1])
            print(
                f"AI moved from {indices_to_chess_notation(best_move[0])} to {indices_to_chess_notation(best_move[1])}"
            )
            self.color_turn = "white"
            self.draw_board()

            if is_checkmate(board, "white"):
                messagebox.showinfo("Game Over", "Checkmate! Black wins!")
            elif is_stalemate(board, "white"):
                messagebox.showinfo("Game Over", "Stalemate! Draw!")
        else:
            messagebox.showinfo("Game Over", "No valid moves for AI.")

if __name__ == "__main__":
    root = tk.Tk()
    ChessGUI(root)
    root.mainloop()




# ---------------------------------------------------------------------------------------



# import tkinter as tk
# from tkinter import messagebox
# from PIL import Image, ImageTk
# import os
# from ChessBoardOrganised import (
#     board,
#     move_piece,
#     is_valid_move,
#     get_best_move_ab,
#     is_checkmate,
#     is_stalemate,
#     indices_to_chess_notation,
# )

# CELL_SIZE = 60 # This is now primarily a reference for initial sizing, actual size is dynamic

# class ChessGUI:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Chess Game - Human vs AI")

#         # Allow the root window to be resizable
#         self.root.resizable(True, True) 
        
#         # Initialize fullscreen state tracking
#         self.is_fullscreen = False
        
#         # Bind F11 key to toggle fullscreen (common for applications)
#         self.root.bind("<F11>", self.toggle_fullscreen)
#         # Bind Escape key to also toggle fullscreen (common for exiting)
#         self.root.bind("<Escape>", self.toggle_fullscreen)

#         self.canvas = tk.Canvas(self.root, bg="lightgray")
#         # Use expand=True and fill=tk.BOTH to make the canvas expand and fill the window area
#         self.canvas.pack(expand=True, fill=tk.BOTH) 
        
#         self.selected = None
#         self.color_turn = "white"
#         # Stores ImageTk.PhotoImage objects keyed by piece type (e.g., 'P', 'k')
#         self.piece_images = {} 
#         # Initialize with a default, will be updated by draw_board based on canvas size
#         self.current_cell_size = CELL_SIZE 

#         # Initial draw of the board and pieces
#         self.draw_board() 
        
#         # Bind mouse click event to the canvas
#         self.canvas.bind("<Button-1>", self.on_click)

#         # Bind the <Configure> event to redraw the board when the window size changes
#         self.canvas.bind("<Configure>", self.on_resize)
        
#     def load_piece_images(self):
#         # This method is no longer actively used, as images are loaded/resized dynamically
#         # within draw_board and cached in self.piece_images.
#         pass 

#     def draw_board(self):
#         # Clear the entire canvas before redrawing
#         self.canvas.delete("all")
        
#         # Force Tkinter to update its internal geometry information
#         self.root.update_idletasks() 
#         canvas_width = self.canvas.winfo_width()
#         canvas_height = self.canvas.winfo_height()

#         # Calculate the new cell size based on current canvas dimensions, ensuring it's at least 1
#         new_cell_size = max(1, min(canvas_width // 8, canvas_height // 8))
        
#         # If the cell size has changed, clear the cached images to force them to reload at the new size
#         if new_cell_size != self.current_cell_size:
#             self.current_cell_size = new_cell_size
#             self.piece_images = {} # Clears the cache

#         # Draw squares and pieces
#         for row in range(8):
#             for col in range(8):
#                 x1, y1 = col * self.current_cell_size, row * self.current_cell_size
#                 x2, y2 = x1 + self.current_cell_size, y1 + self.current_cell_size
#                 color = "white" if (row + col) % 2 == 0 else "gray"
#                 # Add tags for potential future selective updates
#                 self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square") 

#                 # Draw highlight for the selected cell
#                 if self.selected == (row, col):
#                     self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=3, tags="highlight")

#                 piece = board[row][col]
#                 if piece:
#                     # Only load/resize image if it's not already in the cache for the current cell size
#                     if piece not in self.piece_images: 
#                         base_path = os.path.join(os.path.dirname(__file__), "ChessPieces")
#                         piece_filename_map = {
#                             'K': 'king-w', 'Q': 'queen-w', 'R': 'rook-w', 'B': 'bishop-w', 'N': 'knight-w', 'P': 'pawn-w',
#                             'k': 'king-b', 'q': 'queen-b', 'r': 'rook-b', 'b': 'bishop-b', 'n': 'knight-b', 'p': 'pawn-b',
#                         }
#                         filename = piece_filename_map.get(piece)
#                         if filename:
#                             path = os.path.join(base_path, f"{filename}.png")
#                             try:
#                                 img = Image.open(path).resize((self.current_cell_size, self.current_cell_size), Image.Resampling.LANCZOS)
#                                 self.piece_images[piece] = ImageTk.PhotoImage(img) 
#                             except FileNotFoundError:
#                                 print(f"Warning: Piece image not found at {path}. Skipping this piece.")
#                                 continue # Skip drawing this piece if its image is missing
#                             except Exception as e:
#                                 print(f"Error loading/resizing image {path}: {e}. Skipping this piece.")
#                                 continue 

#                     # Draw the piece image if it's available in the cache
#                     if piece in self.piece_images: 
#                         self.canvas.create_image(x1, y1, image=self.piece_images[piece], anchor="nw", tags="piece")

#     def on_click(self, event):
#         # Calculate row and column based on current cell size
#         col = event.x // self.current_cell_size
#         row = event.y // self.current_cell_size
#         print(f"Clicked at row: {row}, col: {col}")

#         # Flag to determine if a full board redraw is necessary
#         redraw_needed = False

#         if self.selected:
#             start_row, start_col = self.selected
            
#             # If the user clicks on the already selected piece, deselect it
#             if (start_row, start_col) == (row, col):
#                 self.selected = None
#                 redraw_needed = True # A redraw is needed to remove the highlight
#             else:
#                 # Attempt to make a move
#                 if is_valid_move(board, (start_row, start_col), (row, col), self.color_turn):
#                     move_piece(board, (start_row, start_col), (row, col))
#                     print(
#                         f"{self.color_turn.capitalize()} moved from {indices_to_chess_notation((start_row, start_col))} "
#                         f"to {indices_to_chess_notation((row, col))}"
#                     )
#                     self.selected = None # Deselect the piece after a valid move
#                     self.color_turn = "black"
#                     redraw_needed = True # A redraw is needed to show the new board state

#                     # Check for game over conditions after human move
#                     if is_checkmate(board, "black"):
#                         messagebox.showinfo("Game Over", "Checkmate! White wins!")
#                         return # Exit function if game is over
#                     if is_stalemate(board, "black"):
#                         messagebox.showinfo("Game Over", "Stalemate! Draw!")
#                         return # Exit function if game is over

#                     # Trigger AI move after a short delay
#                     self.root.after(400, self.ai_move)
#                 else:
#                     print("Invalid move, try again.")
#                     self.selected = None # Deselect if the move was invalid
#                     redraw_needed = True # A redraw is needed to remove the invalid highlight
#         else:
#             # First click: attempt to select a piece
#             if (
#                 board[row][col] # Check if there's a piece at the clicked location
#                 and self.color_turn == "white" # Ensure it's white's turn
#                 and board[row][col].isupper() # Ensure the piece belongs to white
#             ):
#                 self.selected = (row, col)
#                 redraw_needed = True # A redraw is needed to show the selection highlight
#             else:
#                 # Provide feedback if no piece or wrong color piece is selected
#                 print("No piece selected or not your turn/piece.")
        
#         # Perform redraw only if a change occurred that requires it
#         if redraw_needed:
#             self.draw_board()

#     def ai_move(self):
#         # Get the best move for black (AI)
#         best_move = get_best_move_ab(board, "black", depth=4) 
#         if best_move:
#             move_piece(board, best_move[0], best_move[1])
#             print(
#                 f"AI moved from {indices_to_chess_notation(best_move[0])} to {indices_to_chess_notation(best_move[1])}"
#             )
#             self.color_turn = "white" # Switch turn back to white (human)
#             self.draw_board() # Redraw the board after AI's move

#             # Check for game over conditions after AI move
#             if is_checkmate(board, "white"):
#                 messagebox.showinfo("Game Over", "Checkmate! Black wins!")
#             elif is_stalemate(board, "white"):
#                 messagebox.showinfo("Game Over", "Stalemate! Draw!")
#         else:
#             # Handle cases where AI has no valid moves
#             if is_checkmate(board, "black"): # If AI is checkmated, human wins
#                 messagebox.showinfo("Game Over", "Checkmate! White wins!")
#             elif is_stalemate(board, "black"): # If AI is stalemated, it's a draw
#                 messagebox.showinfo("Game Over", "Stalemate! Draw!")
#             else: 
#                 messagebox.showinfo("Game Over", "AI has no valid moves (unexpected).")

#     def on_resize(self, event):
#         # Redraw the board whenever the canvas (and thus the window) is resized
#         self.draw_board()
        
#     def toggle_fullscreen(self, event=None):
#         # Toggle the fullscreen state
#         self.is_fullscreen = not self.is_fullscreen
#         self.root.attributes('-fullscreen', self.is_fullscreen)

# if __name__ == "__main__":
#     root = tk.Tk()
#     ChessGUI(root)
#     root.mainloop()