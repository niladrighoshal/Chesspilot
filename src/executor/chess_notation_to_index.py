import logging

logger = logging.getLogger(__name__)

def chess_notation_to_index(move):
    logger.debug(f"Parsing move: {move}")
    try:
        start_square = move[:2]
        end_square = move[2:4]
        return start_square, end_square
    except (TypeError, IndexError) as e:
        logger.error(f"Invalid move format: {move}, Error: {e}")
        return None, None
