# Chess Position Visualizer

Generate SVG board images and markdown documentation for chess positions using FEN notation.

## Usage

```bash
# Starting position
python mychess.py

# With FEN (standard or underscore format)
python mychess.py --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"
python mychess.py --fen "rnbqkbnr_pppppppp_8_8_8_8_PPPPPPPP_RNBQKBNR_w"

# With moves (from starting position)
# Note that numbers are stripped, and therefore optional.
python mychess.py --moves "e4 e5 Nc3"
python mychess.py --moves "1. e4 e5 2. Nc3"

# With both FEN and moves
python mychess.py --fen "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b" --moves "c5"
```

## Output

For each position, generates:
- **SVG file**: Visual board representation
- **Markdown file**: Board image with FEN metadata (pieces and side-to-move only)

Files are saved to `output/` with FEN-based filenames (slashes and spaces converted to underscores).
