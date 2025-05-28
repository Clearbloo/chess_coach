#!/usr/bin/env python3
"""
Test script to isolate and debug PGN parsing with python-chess.
"""

import chess
import chess.pgn
import io
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pgn_test")

def test_pgn_parsing(pgn_str):
    """Test parsing a PGN string with python-chess."""
    logger.info(f"Testing PGN parsing for: {pgn_str}")
    
    # Try parsing without headers first
    logger.info("Attempting to parse PGN without adding headers")
    pgn_io = io.StringIO(pgn_str)
    game = chess.pgn.read_game(pgn_io)
    
    if game is None:
        logger.warning("Failed to parse PGN without headers")
        
        # Add minimal headers and try again
        logger.info("Adding minimal headers to PGN")
        pgn_with_headers = f"[Event \"Game\"]\n[Site \"Chess Coach\"]\n[Date \"????.??.??\"]\n[Round \"?\"]\n[White \"?\"]\n[Black \"?\"]\n[Result \"*\"]\n\n{pgn_str}"
        logger.debug(f"PGN with headers: {pgn_with_headers}")
        
        pgn_io = io.StringIO(pgn_with_headers)
        game = chess.pgn.read_game(pgn_io)
        
        if game is None:
            logger.error("Failed to parse PGN even with headers")
            return False
        else:
            logger.info("Successfully parsed PGN with added headers")
    else:
        logger.info("Successfully parsed PGN without adding headers")
    
    # Try to validate moves
    try:
        logger.info("Validating moves in the game")
        board = game.board()
        move_count = 0
        
        for move in game.mainline_moves():
            move_count += 1
            san_move = board.san(move)
            logger.debug(f"Move {move_count}: {san_move}")
            
            if move not in board.legal_moves:
                logger.error(f"Illegal move found: {move}")
                return False
                
            board.push(move)
            
        logger.info(f"All {move_count} moves validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error validating moves: {str(e)}")
        return False

def test_move_list_parsing(move_list):
    """Test parsing a list of moves with python-chess."""
    logger.info(f"Testing move list parsing for: {move_list}")
    
    try:
        board = chess.Board()
        move_count = 0
        
        for move_str in move_list:
            move_count += 1
            logger.debug(f"Parsing move {move_count}: {move_str}")
            
            try:
                move = board.parse_san(move_str)
                
                if move not in board.legal_moves:
                    logger.error(f"Illegal move found: {move_str}")
                    return False
                    
                board.push(move)
                logger.debug(f"Move {move_count} ({move_str}) is valid")
                
            except ValueError as e:
                logger.error(f"Invalid move notation: {move_str}, error: {str(e)}")
                return False
                
        logger.info(f"All {move_count} moves in move list validated successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error validating move list: {str(e)}")
        return False

def test_alternative_pgn_formats(base_moves):
    """Test various PGN formatting alternatives."""
    logger.info("Testing alternative PGN formats")
    
    # Format 1: Standard space-separated moves
    pgn1 = base_moves
    logger.info("Testing Format 1: Standard space-separated moves")
    result1 = test_pgn_parsing(pgn1)
    logger.info(f"Format 1 result: {'Success' if result1 else 'Failure'}")
    
    # Format 2: With newlines after each move pair
    moves = base_moves.split()
    pgn2 = ""
    for i in range(0, len(moves), 2):
        if i + 1 < len(moves):
            pgn2 += f"{moves[i]} {moves[i+1]}\n"
        else:
            pgn2 += f"{moves[i]}\n"
    logger.info("Testing Format 2: With newlines after each move pair")
    logger.debug(f"Format 2 PGN: {pgn2}")
    result2 = test_pgn_parsing(pgn2)
    logger.info(f"Format 2 result: {'Success' if result2 else 'Failure'}")
    
    # Format 3: With result at the end
    pgn3 = base_moves + " 1-0"
    logger.info("Testing Format 3: With result at the end")
    result3 = test_pgn_parsing(pgn3)
    logger.info(f"Format 3 result: {'Success' if result3 else 'Failure'}")
    
    # Format 4: Full PGN with headers and result
    pgn4 = f"""[Event "Test Game"]
[Site "Chess Coach"]
[Date "2025.05.27"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

{base_moves} 1-0"""
    logger.info("Testing Format 4: Full PGN with headers and result")
    logger.debug(f"Format 4 PGN: {pgn4}")
    result4 = test_pgn_parsing(pgn4)
    logger.info(f"Format 4 result: {'Success' if result4 else 'Failure'}")
    
    # Format 5: Convert to move list
    move_list = []
    moves = base_moves.split()
    for move in moves:
        if '.' not in move:  # Skip move numbers
            move_list.append(move)
    logger.info("Testing Format 5: As move list")
    logger.debug(f"Move list: {move_list}")
    result5 = test_move_list_parsing(move_list)
    logger.info(f"Format 5 result: {'Success' if result5 else 'Failure'}")
    
    return {
        "format1": result1,
        "format2": result2,
        "format3": result3,
        "format4": result4,
        "format5": result5
    }

if __name__ == "__main__":
    # Test with the PGN string that's failing in the application
    test_pgn = "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O"
    
    logger.info("=== Starting PGN parsing tests ===")
    
    # Test direct parsing
    logger.info("=== Test 1: Direct PGN parsing ===")
    result = test_pgn_parsing(test_pgn)
    logger.info(f"Direct parsing result: {'Success' if result else 'Failure'}")
    
    # Test alternative formats
    logger.info("=== Test 2: Alternative PGN formats ===")
    format_results = test_alternative_pgn_formats(test_pgn)
    
    # Summary
    logger.info("=== Test Summary ===")
    logger.info(f"Direct parsing: {'Success' if result else 'Failure'}")
    for fmt, res in format_results.items():
        logger.info(f"{fmt}: {'Success' if res else 'Failure'}")
    
    # Extract moves as a list for direct testing
    logger.info("=== Test 3: Extracting moves as list ===")
    moves = []
    for token in test_pgn.split():
        if not token[0].isdigit() and token != "O-O" and token != "O-O-O":
            # Skip move numbers
            moves.append(token)
        elif token == "O-O" or token == "O-O-O":
            # Include castling
            moves.append(token)
    
    logger.info(f"Extracted moves: {moves}")
    move_result = test_move_list_parsing(moves)
    logger.info(f"Move list parsing result: {'Success' if move_result else 'Failure'}")
