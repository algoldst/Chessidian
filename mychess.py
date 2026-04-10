import os
import random
import argparse
import chess
import chess.svg
import yaml


def chess_img(board, fen_filename):
    """
    Generate an SVG image of a chessboard and save it as an SVG file.
    """
    svg = chess.svg.board(board)
    
    with open(fen_filename, "w") as f:
        f.write(svg)
    
    print(f"Board image saved to {fen_filename}")


def create_markdown_file(fen_str, board, svg_filename):
    """
    Create a markdown file with YAML frontmatter and embedded SVG image.
    Uses simplified FEN (pieces and whose turn it is).
    """
    # Get simplified FEN without the full FEN
    simplified = simplified_fen(board)
    
    frontmatter = {
        "fen": simplified,
        "turn": "white" if board.turn else "black",
    }
    
    # Create markdown filename (same as svg but with .md extension)
    md_filename = svg_filename.replace(".svg", ".md")
    
    # Read the SVG file to embed it
    svg_basename = os.path.basename(svg_filename)
    
    with open(md_filename, "w") as f:
        f.write("---\n")
        f.write(yaml.dump(frontmatter))
        f.write("---\n\n")
        f.write(f"**Position:** `{simplified}`\n\n")
        f.write(f"![Board Position]({svg_basename})\n\n")


# --- Fixed piece encoding ---
PIECE_TYPES = [
    "P", "N", "B", "R", "Q", "K",
    "p", "n", "b", "r", "q", "k"
]

FILES = "abcdefgh"


# --- Parse simplified FEN (only pieces and side to move) ---
def simplified_fen(board):
    """
    Create a simplified FEN that only includes piece positions and whose turn it is.
    This makes the hash independent of move counts, castling rights, and en passant.
    """
    # Get the piece placement part (first part of FEN)
    fen_parts = board.fen().split()
    piece_placement = fen_parts[0]
    side_to_move = fen_parts[1]
    
    return f"{piece_placement} {side_to_move}"


# --- Convert FEN to filename ---
def fen_to_filename(fen_str):
    """Convert a simplified FEN to a filename by replacing slashes and spaces with underscores."""
    return fen_str.replace("/", "_").replace(" ", "_")


# --- Convert underscore-based FEN back to standard FEN ---
def filename_to_fen(filename_fen):
    """
    Convert underscore-based FEN format back to standard FEN.
    Detects underscores and converts them back to slashes and spaces.
    """
    if "_" not in filename_fen:
        # Already in standard FEN format
        return filename_fen
    
    # Replace all underscores with slashes first
    fen = filename_fen.replace("_", "/")
    
    # The second-to-last character should be converted from a slash back to a space
    # (this is the space between piece placement and side-to-move)
    fen_list = list(fen)
    # Find the last slash and replace the second-to-last occurrence with a space
    # We need to replace the last slash that separates piece placement from side-to-move
    last_slash_idx = fen.rfind("/")
    if last_slash_idx != -1:
        fen_list[last_slash_idx] = " "
    
    return "".join(fen_list)


# --- Parse move notation to board ---
def moves_to_board(moves_str):
    """
    Parse move notation (e.g., "1. e4 e5 2. Nc3") and return the board.
    """
    board = chess.Board()
    
    # Remove move numbers and split by moves
    moves_str = moves_str.replace(".", "").split()
    
    for move_str in moves_str:
        if move_str and not move_str[0].isdigit():
            try:
                move = board.parse_san(move_str)
                board.push(move)
            except (chess.InvalidMoveError, chess.IllegalMoveError) as e:
                print(f"Error parsing move '{move_str}': {e}")
                return None
    
    return board


# --- Apply moves to an existing board ---
def apply_moves_to_board(board, moves_str):
    """
    Apply move notation to an existing board position.
    Move numbers are ignored, so ordering is determined by the moves themselves.
    """
    # Remove move numbers and split by moves
    moves_str = moves_str.replace(".", "").split()
    
    for move_str in moves_str:
        if move_str and not move_str[0].isdigit():
            try:
                move = board.parse_san(move_str)
                board.push(move)
            except (chess.InvalidMoveError, chess.IllegalMoveError) as e:
                print(f"Error parsing move '{move_str}': {e}")
                return None
    
    return board


def main():
    """Main function to handle FEN or move notation input using argparse."""
    parser = argparse.ArgumentParser(
        description="Generate Zobrist hashes and visualizations for chess positions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python mychess.py                    # Use starting position
  python mychess.py --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b"
  python mychess.py --moves "1. e4 e5 2. Nc3"
  python mychess.py --fen "r1bqkbnr/pppppppp/2n5/8/4P3/8/PPPP1PPP/RNBQKBNR b" --moves "2. Nc3 Nc6"
        """
    )
    
    # Input options (no longer mutually exclusive)
    parser.add_argument(
        "--fen",
        type=str,
        help="FEN string representing the starting position"
    )
    parser.add_argument(
        "--moves",
        type=str,
        help="Move notation to apply (numbering ignored)"
    )
    
    args = parser.parse_args()
    
    os.makedirs("output", exist_ok=True)
    
    # Determine which board to use based on provided arguments
    if args.fen and args.moves:
        # Both FEN and moves provided
        try:
            standard_fen = filename_to_fen(args.fen)
            board = chess.Board(standard_fen)
        except ValueError as e:
            print(f"Error: Invalid FEN: {e}")
            return
        
        board = apply_moves_to_board(board, args.moves)
        if board is None:
            print("Error: Invalid moves provided for FEN position.")
            return
    elif args.fen:
        # Only FEN provided
        try:
            standard_fen = filename_to_fen(args.fen)
            board = chess.Board(standard_fen)
        except ValueError as e:
            print(f"Error: Invalid FEN: {e}")
            return
    elif args.moves:
        # Only moves provided (apply from starting position)
        board = moves_to_board(args.moves)
        if board is None:
            print("Error: Invalid move notation provided.")
            return
    else:
        # No arguments provided, use default starting position
        board = chess.Board()
    
    # Get simplified FEN and convert to filename
    fen_str = simplified_fen(board)
    fen_filename = fen_to_filename(fen_str)
    
    print(f"\nPosition: {fen_str}")
    print(f"Filename: {fen_filename}\n")
    
    # Create output directory and files
    svg_file = f"output/{fen_filename}.svg"
    
    chess_img(board, svg_file)
    create_markdown_file(fen_str, board, svg_file)
    
    md_file = f"output/{fen_filename}.md"
    print(f"Files created:\n  - {md_file}\n  - {svg_file}")


if __name__ == "__main__":
    main()