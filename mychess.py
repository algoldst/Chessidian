import os
import random
import chess
import chess.svg


def chess_img(fen, zobrist_name):
    """
    Generate an SVG image of a chessboard and save it to board.svg.
    """

    board = chess.Board(fen)
    svg = chess.svg.board(board)
    
    with open(zobrist_name, "w") as f:
        f.write(svg)
    
    print(f"Board image saved to {zobrist_name}")


# --- Fixed piece encoding ---
PIECE_TYPES = [
    "P", "N", "B", "R", "Q", "K",
    "p", "n", "b", "r", "q", "k"
]

FILES = "abcdefgh"


# --- Zobrist table (deterministic seed) ---
def init_zobrist(seed=42):
    """
    Initialize Zobrist hash tables with a deterministic seed.
    Returns dictionaries/lists of random 64-bit integers for:
    - piece_square: hash values for each piece on each square
    - side_to_move: hash value for side to move
    - castling: hash values for each castling right
    - en_passant_file: hash values for en passant files
    """
    rng = random.Random(seed)

    piece_square = {
        piece: [rng.getrandbits(64) for _ in range(64)]
        for piece in PIECE_TYPES
    }

    side_to_move = rng.getrandbits(64)

    castling = {
        "K": rng.getrandbits(64),
        "Q": rng.getrandbits(64),
        "k": rng.getrandbits(64),
        "q": rng.getrandbits(64),
    }

    en_passant_file = [rng.getrandbits(64) for _ in range(8)]

    return piece_square, side_to_move, castling, en_passant_file


PIECE_SQ, STM_KEY, CASTLE_KEYS, EP_KEYS = init_zobrist()


# --- Parse FEN ---
def parse_fen(fen):
    """
    Parse a FEN string into its components.
    Returns: (board_position, side_to_move, castling_rights, en_passant_square)
    """
    parts = fen.split()
    board = parts[0]
    stm = parts[1]
    castling = parts[2]
    ep = parts[3] if len(parts) > 3 else "-"

    return board, stm, castling, ep


# --- Compute Zobrist hash ---
def zobrist_hash(fen):
    """
    Calculate the Zobrist hash for a given FEN position.
    The hash is computed by XORing random values for:
    - Each piece and its square
    - Side to move
    - Castling rights
    - En passant opportunity
    """
    board, stm, castling, ep = parse_fen(fen)

    h = 0

    # Pieces on the board
    rows = board.split("/")
    for r, row in enumerate(rows):
        file = 0
        for c in row:
            if c.isdigit():
                # Skip empty squares
                file += int(c)
            else:
                # Convert row/file to square index (0-63)
                sq = (7 - r) * 8 + file
                h ^= PIECE_SQ[c][sq]
                file += 1

    # Side to move (if black, XOR with the side-to-move key)
    if stm == "b":
        h ^= STM_KEY

    # Castling rights
    for c in castling:
        if c in CASTLE_KEYS:
            h ^= CASTLE_KEYS[c]

    # En passant (only hash if there's an en passant square)
    if ep != "-":
        file = FILES.index(ep[0])
        h ^= EP_KEYS[file]

    return h

# --- Optional: Convert FEN to filename using hash ---
def fen_to_filename(fen):
    """Convert a FEN position to a hexadecimal filename based on its Zobrist hash."""
    h = zobrist_hash(fen)
    return f"{h:016x}"


# --- Example usage ---
if __name__ == "__main__":
    # Test the Zobrist hash function
    fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    hash_value = zobrist_hash(fen)
    print(f"Zobrist Hash: {hash_value:016x}")
    print(f"Filename: {fen_to_filename(fen)}.md")
    
    # Generate a board image (requires python-chess)
    # Uncomment the line below to generate an SVG image:
    os.makedirs("output", exist_ok=True)
    chess_img(fen, f"output/{fen_to_filename(fen)}.svg")