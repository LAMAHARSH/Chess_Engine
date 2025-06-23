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

