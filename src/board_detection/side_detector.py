import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def detect_side_from_fen(fen):
    """
    Detects which side is at the bottom of the board based on the FEN.
    The side with more pieces on its starting side of the board is considered to be at the bottom.
    """
    logger.info(f"Detecting side from FEN: {fen}")
    piece_placement = fen.split(' ')[0]
    rows = piece_placement.split('/')

    white_pieces_bottom = 0
    black_pieces_bottom = 0

    # Ranks 1-4 are the 4th to 7th rows in the FEN string
    for i in range(4, 8):
        row = rows[i]
        for char in row:
            if char.isdigit():
                continue
            if char.isupper():
                white_pieces_bottom += 1
            else:
                black_pieces_bottom += 1

    logger.info(f"White pieces on bottom half: {white_pieces_bottom}")
    logger.info(f"Black pieces on bottom half: {black_pieces_bottom}")

    if white_pieces_bottom > black_pieces_bottom:
        return 'w'
    else:
        return 'b'
