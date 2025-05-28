"""
Game Analysis Engine Module for Chess Coach Software

This module analyzes chess games to identify patterns, strengths, and weaknesses.
"""

import chess
import chess.pgn
import io
import json
import logging
import os
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GameAnalysisEngine:
    """
    Analyzes chess games to identify patterns and areas for improvement.
    """
    
    def __init__(self, chess_engine=None):
        """
        Initialize the Game Analysis Engine.
        
        Args:
            chess_engine: Optional reference to the chess engine interface
        """
        self.chess_engine = chess_engine  # Can be set now or later by core engine
        self.initialized = False
        self.chess_concepts = self._load_chess_concepts()
        logger.info("Game Analysis Engine created")
        
    def initialize(self) -> bool:
        """
        Initialize the Game Analysis Engine.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Initialization logic
            self.initialized = True
            logger.info("Game Analysis Engine initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Game Analysis Engine: {str(e)}")
            return False
            
    def set_chess_engine(self, chess_engine: Any) -> None:
        """
        Set the chess engine reference.
        
        Args:
            chess_engine: Reference to the chess engine interface
        """
        self.chess_engine = chess_engine
        logger.info("Chess engine reference set in Game Analysis Engine")
        
    def _load_chess_concepts(self) -> Dict[str, Dict[str, Any]]:
        """
        Load chess concepts database.
        
        Returns:
            Dictionary of chess concepts
        """
        # This would typically load from a file, but for now we'll define inline
        concepts = {
            # Tactical concepts
            "fork": {
                "type": "tactical",
                "description": "A move that attacks two or more pieces simultaneously",
                "detection_patterns": ["multiple_attacks"]
            },
            "pin": {
                "type": "tactical",
                "description": "A piece is prevented from moving because it would expose a more valuable piece to capture",
                "detection_patterns": ["aligned_pieces", "relative_value"]
            },
            "skewer": {
                "type": "tactical",
                "description": "Similar to a pin, but the more valuable piece is in front",
                "detection_patterns": ["aligned_pieces", "relative_value"]
            },
            "discovered_attack": {
                "type": "tactical",
                "description": "A piece moves to reveal an attack by another piece",
                "detection_patterns": ["revealed_attack"]
            },
            "double_check": {
                "type": "tactical",
                "description": "Two pieces check the king simultaneously",
                "detection_patterns": ["multiple_checks"]
            },
            
            # Strategic concepts
            "pawn_structure": {
                "type": "strategic",
                "description": "The arrangement of pawns that determines strategic play",
                "detection_patterns": ["pawn_islands", "isolated_pawns", "doubled_pawns"]
            },
            "piece_activity": {
                "type": "strategic",
                "description": "How active and well-placed the pieces are",
                "detection_patterns": ["central_control", "piece_mobility"]
            },
            "king_safety": {
                "type": "strategic",
                "description": "The security of the king's position",
                "detection_patterns": ["king_exposure", "pawn_shield"]
            },
            "space_advantage": {
                "type": "strategic",
                "description": "Control of more squares, especially in the opponent's territory",
                "detection_patterns": ["controlled_squares", "advanced_pieces"]
            },
            
            # Opening concepts
            "development": {
                "type": "opening",
                "description": "Bringing pieces out from their starting positions",
                "detection_patterns": ["piece_development", "early_game"]
            },
            "center_control": {
                "type": "opening",
                "description": "Control of the central squares (d4, d5, e4, e5)",
                "detection_patterns": ["central_pawns", "central_pieces"]
            },
            "castling": {
                "type": "opening",
                "description": "Special king move for safety",
                "detection_patterns": ["king_castled", "early_game"]
            },
            
            # Endgame concepts
            "pawn_promotion": {
                "type": "endgame",
                "description": "Advancing a pawn to the eighth rank to promote it",
                "detection_patterns": ["advanced_pawns", "promotion_potential"]
            },
            "king_activity": {
                "type": "endgame",
                "description": "Using the king as an active piece in the endgame",
                "detection_patterns": ["active_king", "late_game"]
            },
            "zugzwang": {
                "type": "endgame",
                "description": "A position where any move worsens the position",
                "detection_patterns": ["limited_moves", "forced_deterioration"]
            }
        }
        
        return concepts
        
    def analyze_game(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a chess game to identify patterns, strengths, and weaknesses.
        
        Args:
            game_data: The game data to analyze, containing PGN or move list
            
        Returns:
            Analysis results including strengths, weaknesses, and feedback
        """
        try:
            # Ensure chess engine is available
            if not self.chess_engine:
                raise ValueError("Chess engine not available for analysis")
                
            # Parse the game
            game, moves = self._parse_game(game_data)
            if not game or not moves:
                raise ValueError("Could not parse game data")
                
            # Initialize analysis results
            analysis_results = {
                "game_id": game_data.get("id", "unknown"),
                "player_color": game_data.get("player_color", "white"),
                "overall_accuracy": 0.0,
                "move_analysis": [],
                "phases_analysis": {
                    "opening": {},
                    "middlegame": {},
                    "endgame": {}
                },
                "tactical_opportunities": [],
                "strategic_assessments": [],
                "mistake_patterns": [],
                "strengths_identified": [],
                "weaknesses_identified": [],
                "improvement_suggestions": []
            }
            
            # Analyze each move
            total_accuracy = 0.0
            move_count = 0
            
            board = chess.Board()
            for i, move_data in enumerate(moves):
                # Determine game phase
                phase = self._determine_game_phase(board, i, len(moves))
                
                # Get move details
                move_str = move_data.get("notation", "")
                if not move_str:
                    continue
                    
                # Only analyze the player's moves
                is_player_move = (
                    (analysis_results["player_color"] == "white" and board.turn == chess.WHITE) or
                    (analysis_results["player_color"] == "black" and board.turn == chess.BLACK)
                )
                
                if is_player_move:
                    # Analyze the position before the move
                    position_analysis = self._analyze_position(board)
                    
                    # Get the move object
                    try:
                        move = board.parse_san(move_str)
                    except ValueError:
                        logger.error(f"Invalid move notation: {move_str}")
                        continue
                    
                    # Analyze the move
                    move_analysis = self._analyze_move(board, move, move_str, phase)
                    
                    # Update accuracy metrics
                    accuracy = move_analysis.get("accuracy", 0.0)
                    total_accuracy += accuracy
                    move_count += 1
                    
                    # Add to move analysis list
                    analysis_results["move_analysis"].append(move_analysis)
                    
                    # Check for tactical opportunities
                    self._check_tactical_opportunities(board, move, position_analysis, 
                                                     analysis_results)
                    
                    # Update phase analysis
                    self._update_phase_analysis(analysis_results["phases_analysis"][phase], 
                                              move_analysis)
                    
                # Make the move on the board
                try:
                    move = board.parse_san(move_str)
                    board.push(move)
                except ValueError:
                    logger.error(f"Invalid move notation: {move_str}")
                    continue
                
            # Calculate overall accuracy
            if move_count > 0:
                analysis_results["overall_accuracy"] = total_accuracy / move_count
                
            # Identify mistake patterns
            self._identify_mistake_patterns(analysis_results)
            
            # Identify strengths and weaknesses
            self._identify_strengths_and_weaknesses(analysis_results)
            
            # Generate improvement suggestions
            self._generate_improvement_suggestions(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error analyzing game: {str(e)}")
            return {"error": str(e)}
            
    def _parse_game(self, game_data: Dict[str, Any]) -> Tuple[Any, List[Dict[str, Any]]]:
        """
        Parse game data into a chess.pgn.Game object and move list.
        
        Args:
            game_data: The game data to parse
            
        Returns:
            Tuple of (game object, move list)
        """
        game = None
        moves = []
        
        # Check if we have PGN data
        if 'pgn' in game_data and game_data['pgn']:
            pgn_io = io.StringIO(game_data['pgn'])
            game = chess.pgn.read_game(pgn_io)
            
            if game:
                # Extract moves from the game
                board = game.board()
                for i, move in enumerate(game.mainline_moves()):
                    san_move = board.san(move)
                    fen = board.fen()
                    
                    move_data = {
                        "number": i + 1,
                        "notation": san_move,
                        "position": fen
                    }
                    
                    moves.append(move_data)
                    board.push(move)
                    
        # Check if we have a move list
        elif 'moves' in game_data and game_data['moves']:
            board = chess.Board()
            
            for i, move_str in enumerate(game_data['moves']):
                try:
                    move = board.parse_san(move_str)
                    fen = board.fen()
                    
                    move_data = {
                        "number": i + 1,
                        "notation": move_str,
                        "position": fen
                    }
                    
                    moves.append(move_data)
                    board.push(move)
                except ValueError:
                    logger.error(f"Invalid move notation: {move_str}")
                    continue
                    
            # Create a game object from the moves
            game = chess.pgn.Game()
            
        return game, moves
        
    def _determine_game_phase(self, board: chess.Board, move_number: int, 
                            total_moves: int) -> str:
        """
        Determine the current phase of the game.
        
        Args:
            board: Current board position
            move_number: Current move number
            total_moves: Total number of moves in the game
            
        Returns:
            Game phase as string: "opening", "middlegame", or "endgame"
        """
        # Simple heuristic based on move number and piece count
        if move_number < 10:
            return "opening"
            
        # Count pieces (excluding pawns and kings)
        piece_count = 0
        for piece_type in [chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN]:
            piece_count += len(board.pieces(piece_type, chess.WHITE))
            piece_count += len(board.pieces(piece_type, chess.BLACK))
            
        if piece_count <= 6:
            return "endgame"
        elif move_number < 20:
            return "middlegame"
        elif piece_count <= 10:
            return "endgame"
        else:
            return "middlegame"
            
    def _analyze_position(self, board: chess.Board) -> Dict[str, Any]:
        """
        Analyze a chess position.
        
        Args:
            board: The chess position to analyze
            
        Returns:
            Position analysis results
        """
        position_analysis = {
            "fen": board.fen(),
            "evaluation": 0.0,
            "best_move": None,
            "tactical_opportunities": [],
            "piece_activity": {},
            "king_safety": {},
            "pawn_structure": {}
        }
        
        # Get position evaluation from chess engine
        eval_result = self.chess_engine.evaluate_position(board.fen())
        position_analysis["evaluation"] = eval_result.get("score", 0.0)
        position_analysis["best_move"] = eval_result.get("best_move", None)
        
        # Analyze piece activity
        position_analysis["piece_activity"] = self._analyze_piece_activity(board)
        
        # Analyze king safety
        position_analysis["king_safety"] = self._analyze_king_safety(board)
        
        # Analyze pawn structure
        position_analysis["pawn_structure"] = self._analyze_pawn_structure(board)
        
        # Check for tactical opportunities
        position_analysis["tactical_opportunities"] = self._find_tactical_opportunities(board)
        
        return position_analysis
        
    def _analyze_piece_activity(self, board: chess.Board) -> Dict[str, Any]:
        """
        Analyze piece activity in a position.
        
        Args:
            board: The chess position to analyze
            
        Returns:
            Piece activity analysis
        """
        activity = {
            "mobility": {},
            "center_control": 0,
            "development": 0
        }
        
        # Calculate mobility for each piece type
        for color in [chess.WHITE, chess.BLACK]:
            color_name = "white" if color == chess.WHITE else "black"
            activity["mobility"][color_name] = {}
            
            for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
                piece_name = chess.piece_name(piece_type)
                mobility = 0
                
                for square in board.pieces(piece_type, color):
                    # Count legal moves for this piece
                    piece_mobility = 0
                    for move in board.legal_moves:
                        if move.from_square == square:
                            piece_mobility += 1
                    mobility += piece_mobility
                    
                activity["mobility"][color_name][piece_name] = mobility
                
        # Calculate center control
        center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
        for square in center_squares:
            if board.is_attacked_by(chess.WHITE, square):
                activity["center_control"] += 1
            if board.is_attacked_by(chess.BLACK, square):
                activity["center_control"] -= 1
                
        # Calculate development (for opening phase)
        initial_knight_squares = [chess.B1, chess.G1, chess.B8, chess.G8]
        initial_bishop_squares = [chess.C1, chess.F1, chess.C8, chess.F8]
        
        for square in initial_knight_squares + initial_bishop_squares:
            piece = board.piece_at(square)
            if piece is None:
                # Piece has moved from its initial square
                if square in initial_knight_squares:
                    if square in [chess.B1, chess.G1]:
                        activity["development"] += 1
                    else:
                        activity["development"] -= 1
                else:  # Bishop squares
                    if square in [chess.C1, chess.F1]:
                        activity["development"] += 1
                    else:
                        activity["development"] -= 1
                        
        return activity
        
    def _analyze_king_safety(self, board: chess.Board) -> Dict[str, Any]:
        """
        Analyze king safety in a position.
        
        Args:
            board: The chess position to analyze
            
        Returns:
            King safety analysis
        """
        safety = {
            "white": {
                "castled": False,
                "pawn_shield": 0,
                "attacker_count": 0,
                "defender_count": 0,
                "safety_score": 0
            },
            "black": {
                "castled": False,
                "pawn_shield": 0,
                "attacker_count": 0,
                "defender_count": 0,
                "safety_score": 0
            }
        }
        
        # Check king positions
        white_king_square = board.king(chess.WHITE)
        black_king_square = board.king(chess.BLACK)
        
        # Check if kings are castled
        white_castled = white_king_square in [chess.G1, chess.C1]
        black_castled = black_king_square in [chess.G8, chess.C8]
        
        safety["white"]["castled"] = white_castled
        safety["black"]["castled"] = black_castled
        
        # Check pawn shields
        for color, king_square in [(chess.WHITE, white_king_square), (chess.BLACK, black_king_square)]:
            color_name = "white" if color == chess.WHITE else "black"
            
            # Define potential pawn shield squares based on king position
            shield_squares = []
            file = chess.square_file(king_square)
            rank = chess.square_rank(king_square)
            
            if color == chess.WHITE:
                # White king's pawn shield is one rank above
                for f in range(max(0, file - 1), min(7, file + 2)):
                    shield_squares.append(chess.square(f, min(7, rank + 1)))
            else:
                # Black king's pawn shield is one rank below
                for f in range(max(0, file - 1), min(7, file + 2)):
                    shield_squares.append(chess.square(f, max(0, rank - 1)))
                    
            # Count pawns in shield
            pawn_shield = 0
            for square in shield_squares:
                piece = board.piece_at(square)
                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                    pawn_shield += 1
                    
            safety[color_name]["pawn_shield"] = pawn_shield
            
            # Count attackers and defenders
            king_attackers = 0
            king_defenders = 0
            
            # Define squares around the king
            king_zone = []
            for dr in [-1, 0, 1]:
                for df in [-1, 0, 1]:
                    if dr == 0 and df == 0:
                        continue  # Skip the king's square itself
                    new_rank = rank + dr
                    new_file = file + df
                    if 0 <= new_rank < 8 and 0 <= new_file < 8:
                        king_zone.append(chess.square(new_file, new_rank))
                        
            # Count attackers
            opponent = not color
            for square in king_zone:
                if board.is_attacked_by(opponent, square):
                    king_attackers += 1
                    
            # Count defenders
            for square in king_zone:
                if board.is_attacked_by(color, square):
                    king_defenders += 1
                    
            safety[color_name]["attacker_count"] = king_attackers
            safety[color_name]["defender_count"] = king_defenders
            
            # Calculate safety score
            safety_score = (
                (1 if safety[color_name]["castled"] else 0) * 2 +
                safety[color_name]["pawn_shield"] * 1.5 +
                safety[color_name]["defender_count"] -
                safety[color_name]["attacker_count"] * 1.5
            )
            
            safety[color_name]["safety_score"] = safety_score
            
        return safety
        
    def _analyze_pawn_structure(self, board: chess.Board) -> Dict[str, Any]:
        """
        Analyze pawn structure in a position.
        
        Args:
            board: The chess position to analyze
            
        Returns:
            Pawn structure analysis
        """
        structure = {
            "white": {
                "isolated_pawns": 0,
                "doubled_pawns": 0,
                "pawn_islands": 0,
                "passed_pawns": 0,
                "backward_pawns": 0
            },
            "black": {
                "isolated_pawns": 0,
                "doubled_pawns": 0,
                "pawn_islands": 0,
                "passed_pawns": 0,
                "backward_pawns": 0
            }
        }
        
        # Analyze for each color
        for color in [chess.WHITE, chess.BLACK]:
            color_name = "white" if color == chess.WHITE else "black"
            opponent = not color
            
            # Get all pawns of this color
            pawns = board.pieces(chess.PAWN, color)
            
            # Count pawns by file
            files = [0] * 8
            for square in pawns:
                file = chess.square_file(square)
                files[file] += 1
                
            # Count doubled pawns
            doubled = sum(1 for count in files if count >= 2)
            structure[color_name]["doubled_pawns"] = doubled
            
            # Count pawn islands
            islands = 0
            in_island = False
            for count in files:
                if count > 0 and not in_island:
                    islands += 1
                    in_island = True
                elif count == 0:
                    in_island = False
                    
            structure[color_name]["pawn_islands"] = islands
            
            # Check each pawn for isolated, passed, and backward status
            isolated = 0
            passed = 0
            backward = 0
            
            for square in pawns:
                file = chess.square_file(square)
                rank = chess.square_rank(square)
                
                # Check if isolated (no friendly pawns on adjacent files)
                is_isolated = True
                for adj_file in [file - 1, file + 1]:
                    if 0 <= adj_file < 8 and files[adj_file] > 0:
                        is_isolated = False
                        break
                        
                if is_isolated:
                    isolated += 1
                    
                # Check if passed (no enemy pawns ahead on same or adjacent files)
                is_passed = True
                direction = 1 if color == chess.WHITE else -1
                for check_rank in range(rank + direction, 8 if direction > 0 else -1, direction):
                    for check_file in [file - 1, file, file + 1]:
                        if 0 <= check_file < 8 and 0 <= check_rank < 8:
                            check_square = chess.square(check_file, check_rank)
                            piece = board.piece_at(check_square)
                            if piece and piece.piece_type == chess.PAWN and piece.color == opponent:
                                is_passed = False
                                break
                    if not is_passed:
                        break
                        
                if is_passed:
                    passed += 1
                    
                # Check if backward (no friendly pawns on adjacent files ahead, and cannot advance safely)
                if not is_isolated and not is_passed:
                    is_backward = True
                    
                    # Check if pawn can be supported by adjacent pawns
                    for adj_file in [file - 1, file + 1]:
                        if 0 <= adj_file < 8:
                            for check_rank in range(rank, 8 if color == chess.WHITE else -1, 
                                                 1 if color == chess.WHITE else -1):
                                check_square = chess.square(adj_file, check_rank)
                                piece = board.piece_at(check_square)
                                if piece and piece.piece_type == chess.PAWN and piece.color == color:
                                    is_backward = False
                                    break
                        if not is_backward:
                            break
                            
                    # Check if pawn can advance safely
                    advance_rank = rank + (1 if color == chess.WHITE else -1)
                    if 0 <= advance_rank < 8:
                        advance_square = chess.square(file, advance_rank)
                        
                        # If square ahead is occupied, pawn cannot advance
                        if board.piece_at(advance_square):
                            is_backward = True
                        else:
                            # Check if advance square is attacked by enemy pawns
                            for attack_file in [file - 1, file + 1]:
                                if 0 <= attack_file < 8:
                                    attack_rank = advance_rank + (-1 if color == chess.WHITE else 1)
                                    if 0 <= attack_rank < 8:
                                        attack_square = chess.square(attack_file, attack_rank)
                                        piece = board.piece_at(attack_square)
                                        if piece and piece.piece_type == chess.PAWN and piece.color == opponent:
                                            is_backward = True
                                            break
                                            
                    if is_backward:
                        backward += 1
                        
            structure[color_name]["isolated_pawns"] = isolated
            structure[color_name]["passed_pawns"] = passed
            structure[color_name]["backward_pawns"] = backward
            
        return structure
        
    def _find_tactical_opportunities(self, board: chess.Board) -> List[Dict[str, Any]]:
        """
        Find tactical opportunities in a position.
        
        Args:
            board: The chess position to analyze
            
        Returns:
            List of tactical opportunities
        """
        opportunities = []
        
        # Get the side to move
        side_to_move = board.turn
        
        # Get alternative moves from the chess engine
        alt_moves = self.chess_engine.get_alternative_moves(board.fen(), num_moves=5)
        
        # Check each move for tactical patterns
        for move_info in alt_moves:
            move_uci = move_info.get("move_uci", "")
            if not move_uci:
                continue
                
            try:
                move = chess.Move.from_uci(move_uci)
            except ValueError:
                continue
                
            # Make the move on a copy of the board
            board_copy = board.copy()
            board_copy.push(move)
            
            # Check for various tactical patterns
            tactics = []
            
            # Check for check
            if board_copy.is_check():
                tactics.append("check")
                
            # Check for capture
            is_capture = board.piece_at(move.to_square) is not None
            if is_capture:
                tactics.append("capture")
                
                # Check for captured piece value vs moving piece value
                captured_piece = board.piece_at(move.to_square)
                moving_piece = board.piece_at(move.from_square)
                
                if captured_piece and moving_piece:
                    captured_value = self._get_piece_value(captured_piece.piece_type)
                    moving_value = self._get_piece_value(moving_piece.piece_type)
                    
                    if captured_value > moving_value:
                        tactics.append("winning_capture")
                    elif captured_value == moving_value:
                        tactics.append("equal_capture")
                    else:
                        tactics.append("losing_capture")
                        
            # Check for fork (attacking multiple pieces)
            attacked_pieces = []
            for square in chess.SQUARES:
                piece = board_copy.piece_at(square)
                if piece and piece.color != side_to_move:
                    if board_copy.is_attacked_by(side_to_move, square):
                        attacked_pieces.append((square, piece.piece_type))
                        
            if len(attacked_pieces) >= 2:
                tactics.append("fork")
                
                # Check if fork targets high-value pieces
                high_value_targets = sum(1 for _, piece_type in attacked_pieces 
                                      if piece_type in [chess.QUEEN, chess.ROOK])
                if high_value_targets >= 1:
                    tactics.append("high_value_fork")
                    
            # Check for pin
            pins = []
            for square in chess.SQUARES:
                piece = board_copy.piece_at(square)
                if piece and piece.color != side_to_move:
                    # Check if this piece is pinned to its king
                    king_square = board_copy.king(not side_to_move)
                    if king_square is not None:
                        if self._is_pinned(board_copy, square, king_square, side_to_move):
                            pins.append(square)
                            
            if pins:
                tactics.append("pin")
                
            # If we found tactics, add this move as an opportunity
            if tactics:
                opportunities.append({
                    "move": board.san(move),
                    "move_uci": move_uci,
                    "tactics": tactics,
                    "evaluation": move_info.get("score", 0)
                })
                
        return opportunities
        
    def _is_pinned(self, board: chess.Board, square: chess.Square, 
                 king_square: chess.Square, attacker_color: chess.Color) -> bool:
        """
        Check if a piece is pinned to its king.
        
        Args:
            board: The chess position
            square: Square of the potentially pinned piece
            king_square: Square of the king
            attacker_color: Color of the potential pinner
            
        Returns:
            True if the piece is pinned, False otherwise
        """
        # Get the direction from king to piece
        file_diff = chess.square_file(square) - chess.square_file(king_square)
        rank_diff = chess.square_rank(square) - chess.square_rank(king_square)
        
        # Check if they're aligned (same rank, file, or diagonal)
        if file_diff == 0:  # Same file
            step = 8 if rank_diff > 0 else -8
        elif rank_diff == 0:  # Same rank
            step = 1 if file_diff > 0 else -1
        elif abs(file_diff) == abs(rank_diff):  # Same diagonal
            step = 9 if file_diff > 0 and rank_diff > 0 else \
                   7 if file_diff < 0 and rank_diff > 0 else \
                   -9 if file_diff < 0 and rank_diff < 0 else -7
        else:
            return False  # Not aligned
            
        # Check for a pinner on the other side of the piece
        current = square + step
        edge = chess.square(7, 7) if step > 0 else chess.square(0, 0)
        
        while 0 <= current <= 63 and abs(chess.square_file(current) - chess.square_file(current - step)) <= 1:
            piece = board.piece_at(current)
            if piece:
                if piece.color == attacker_color:
                    # Check if this piece can pin along this direction
                    if step in [8, -8, 1, -1]:  # Orthogonal
                        return piece.piece_type in [chess.QUEEN, chess.ROOK]
                    else:  # Diagonal
                        return piece.piece_type in [chess.QUEEN, chess.BISHOP]
                else:
                    return False  # Blocked by another piece
                    
            if current == edge:
                break
                
            current += step
            
        return False
        
    def _get_piece_value(self, piece_type: chess.PieceType) -> int:
        """
        Get the standard value of a chess piece.
        
        Args:
            piece_type: The type of chess piece
            
        Returns:
            Piece value in centipawns
        """
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 300,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 20000  # Effectively infinite
        }
        return values.get(piece_type, 0)
        
    def _analyze_move(self, board: chess.Board, move: chess.Move, move_str: str, 
                    phase: str) -> Dict[str, Any]:
        """
        Analyze a chess move.
        
        Args:
            board: The chess position before the move
            move: The chess move to analyze
            move_str: String representation of the move
            phase: Current game phase
            
        Returns:
            Move analysis results
        """
        # Initialize move analysis
        move_analysis = {
            "move": move_str,
            "position": board.fen(),
            "phase": phase,
            "evaluation": 0.0,
            "accuracy": 0.0,
            "classification": "",
            "alternative_moves": [],
            "concepts": []
        }
        
        # Classify the move using the chess engine
        classification = self.chess_engine.classify_move(board.fen(), move_str)
        
        move_analysis["evaluation"] = classification.get("evaluation", 0.0)
        move_analysis["classification"] = classification.get("classification", "")
        
        # Calculate move accuracy (0-100 scale)
        if classification.get("classification") == "Best":
            move_analysis["accuracy"] = 100.0
        elif classification.get("classification") == "Good":
            move_analysis["accuracy"] = 80.0
        elif classification.get("classification") == "Inaccuracy":
            move_analysis["accuracy"] = 60.0
        elif classification.get("classification") == "Mistake":
            move_analysis["accuracy"] = 40.0
        elif classification.get("classification") == "Blunder":
            move_analysis["accuracy"] = 20.0
        else:
            move_analysis["accuracy"] = 50.0  # Default
            
        # Get alternative moves
        move_analysis["alternative_moves"] = self.chess_engine.get_alternative_moves(board.fen())
        
        # Identify chess concepts in the move
        move_analysis["concepts"] = self._identify_move_concepts(board, move, phase)
        
        return move_analysis
        
    def _identify_move_concepts(self, board: chess.Board, move: chess.Move, 
                              phase: str) -> List[Dict[str, Any]]:
        """
        Identify chess concepts demonstrated in a move.
        
        Args:
            board: The chess position before the move
            move: The chess move to analyze
            phase: Current game phase
            
        Returns:
            List of identified concepts
        """
        concepts = []
        
        # Make the move on a copy of the board
        board_copy = board.copy()
        board_copy.push(move)
        
        # Check phase-specific concepts
        if phase == "opening":
            # Check for development
            if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type != chess.PAWN:
                if chess.square_rank(move.from_square) in [0, 7]:  # Starting rank
                    concepts.append({
                        "concept": "development",
                        "confidence": 0.8
                    })
                    
            # Check for center control
            center_squares = [chess.E4, chess.D4, chess.E5, chess.D5]
            if move.to_square in center_squares or board_copy.is_attacked_by(board.turn, chess.E4):
                concepts.append({
                    "concept": "center_control",
                    "confidence": 0.7
                })
                
            # Check for castling
            if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.KING:
                if abs(chess.square_file(move.from_square) - chess.square_file(move.to_square)) > 1:
                    concepts.append({
                        "concept": "castling",
                        "confidence": 0.9
                    })
                    
        elif phase == "middlegame":
            # Check for piece activity
            if board.piece_at(move.from_square):
                # Count legal moves before and after
                before_mobility = 0
                for m in board.legal_moves:
                    if m.from_square == move.from_square:
                        before_mobility += 1
                        
                after_mobility = 0
                for m in board_copy.legal_moves:
                    if m.from_square == move.to_square:
                        after_mobility += 1
                        
                if after_mobility > before_mobility:
                    concepts.append({
                        "concept": "piece_activity",
                        "confidence": 0.7
                    })
                    
            # Check for king safety
            if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.KING:
                # King moved to a safer position?
                king_attackers_before = 0
                for square in chess.SQUARES:
                    if board.piece_at(square) and board.piece_at(square).color != board.turn:
                        if move.from_square in board.attacks(square):
                            king_attackers_before += 1
                            
                king_attackers_after = 0
                for square in chess.SQUARES:
                    if board_copy.piece_at(square) and board_copy.piece_at(square).color != board.turn:
                        if move.to_square in board_copy.attacks(square):
                            king_attackers_after += 1
                            
                if king_attackers_after < king_attackers_before:
                    concepts.append({
                        "concept": "king_safety",
                        "confidence": 0.8
                    })
                    
        elif phase == "endgame":
            # Check for pawn promotion
            if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.PAWN:
                if chess.square_rank(move.to_square) in [0, 7]:
                    concepts.append({
                        "concept": "pawn_promotion",
                        "confidence": 0.9
                    })
                    
            # Check for king activity
            if board.piece_at(move.from_square) and board.piece_at(move.from_square).piece_type == chess.KING:
                # King moved to a more central position?
                center_distance_before = self._distance_to_center(move.from_square)
                center_distance_after = self._distance_to_center(move.to_square)
                
                if center_distance_after < center_distance_before:
                    concepts.append({
                        "concept": "king_activity",
                        "confidence": 0.7
                    })
                    
        # Check for tactical concepts (any phase)
        
        # Check for check
        if board_copy.is_check():
            concepts.append({
                "concept": "check",
                "confidence": 0.9
            })
            
        # Check for capture
        if board.piece_at(move.to_square):
            concepts.append({
                "concept": "capture",
                "confidence": 0.9
            })
            
            # Check for captured piece value vs moving piece value
            captured_piece = board.piece_at(move.to_square)
            moving_piece = board.piece_at(move.from_square)
            
            if captured_piece and moving_piece:
                captured_value = self._get_piece_value(captured_piece.piece_type)
                moving_value = self._get_piece_value(moving_piece.piece_type)
                
                if captured_value > moving_value:
                    concepts.append({
                        "concept": "winning_capture",
                        "confidence": 0.8
                    })
                    
        # Check for fork
        attacked_pieces = []
        for square in chess.SQUARES:
            piece = board_copy.piece_at(square)
            if piece and piece.color != board.turn:
                if board_copy.is_attacked_by(board.turn, square):
                    attacked_pieces.append((square, piece.piece_type))
                    
        if len(attacked_pieces) >= 2:
            concepts.append({
                "concept": "fork",
                "confidence": 0.8
            })
            
        # Check for pin
        pins = []
        for square in chess.SQUARES:
            piece = board_copy.piece_at(square)
            if piece and piece.color != board.turn:
                # Check if this piece is pinned to its king
                king_square = board_copy.king(not board.turn)
                if king_square is not None:
                    if self._is_pinned(board_copy, square, king_square, board.turn):
                        pins.append(square)
                        
        if pins:
            concepts.append({
                "concept": "pin",
                "confidence": 0.8
            })
            
        return concepts
        
    def _distance_to_center(self, square: chess.Square) -> float:
        """
        Calculate the distance from a square to the center of the board.
        
        Args:
            square: Chess square
            
        Returns:
            Distance to center (0-4)
        """
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        
        # Distance from file to center files (d and e)
        file_distance = min(abs(file - 3), abs(file - 4))
        
        # Distance from rank to center ranks (4 and 5)
        rank_distance = min(abs(rank - 3), abs(rank - 4))
        
        # Euclidean distance
        return (file_distance ** 2 + rank_distance ** 2) ** 0.5
        
    def _check_tactical_opportunities(self, board: chess.Board, move: chess.Move, 
                                    position_analysis: Dict[str, Any], 
                                    analysis_results: Dict[str, Any]) -> None:
        """
        Check for missed tactical opportunities.
        
        Args:
            board: The chess position before the move
            move: The move that was played
            position_analysis: Analysis of the position before the move
            analysis_results: Overall analysis results to update
        """
        # Get tactical opportunities from position analysis
        opportunities = position_analysis.get("tactical_opportunities", [])
        
        # Check if the played move was one of the tactical opportunities
        move_uci = move.uci()
        played_opportunity = False
        
        for opp in opportunities:
            if opp.get("move_uci") == move_uci:
                played_opportunity = True
                break
                
        # If there were opportunities but the played move wasn't one of them,
        # record this as a missed tactical opportunity
        if opportunities and not played_opportunity:
            # Find the best tactical opportunity
            best_opp = max(opportunities, key=lambda x: x.get("evaluation", 0))
            
            # Add to missed opportunities
            analysis_results["tactical_opportunities"].append({
                "position": board.fen(),
                "played_move": board.san(move),
                "missed_move": best_opp.get("move", ""),
                "tactics": best_opp.get("tactics", []),
                "evaluation_diff": best_opp.get("evaluation", 0) - position_analysis.get("evaluation", 0)
            })
            
    def _update_phase_analysis(self, phase_analysis: Dict[str, Any], 
                             move_analysis: Dict[str, Any]) -> None:
        """
        Update phase-specific analysis with move data.
        
        Args:
            phase_analysis: Phase analysis to update
            move_analysis: Analysis of the current move
        """
        # Initialize phase analysis if empty
        if not phase_analysis:
            phase_analysis.update({
                "move_count": 0,
                "accuracy_sum": 0.0,
                "best_moves": 0,
                "good_moves": 0,
                "inaccuracies": 0,
                "mistakes": 0,
                "blunders": 0,
                "concepts": {}
            })
            
        # Update move count and accuracy
        phase_analysis["move_count"] += 1
        phase_analysis["accuracy_sum"] += move_analysis.get("accuracy", 0.0)
        
        # Update move classification counts
        classification = move_analysis.get("classification", "")
        if classification == "Best":
            phase_analysis["best_moves"] += 1
        elif classification == "Good":
            phase_analysis["good_moves"] += 1
        elif classification == "Inaccuracy":
            phase_analysis["inaccuracies"] += 1
        elif classification == "Mistake":
            phase_analysis["mistakes"] += 1
        elif classification == "Blunder":
            phase_analysis["blunders"] += 1
            
        # Update concepts
        for concept_data in move_analysis.get("concepts", []):
            concept = concept_data.get("concept", "")
            if concept:
                if concept not in phase_analysis["concepts"]:
                    phase_analysis["concepts"][concept] = {
                        "count": 0,
                        "confidence_sum": 0.0
                    }
                    
                phase_analysis["concepts"][concept]["count"] += 1
                phase_analysis["concepts"][concept]["confidence_sum"] += concept_data.get("confidence", 0.5)
                
    def _identify_mistake_patterns(self, analysis_results: Dict[str, Any]) -> None:
        """
        Identify patterns in mistakes and blunders.
        
        Args:
            analysis_results: Analysis results to update
        """
        # Collect all mistakes and blunders
        mistakes = []
        
        for move in analysis_results.get("move_analysis", []):
            if move.get("classification") in ["Mistake", "Blunder"]:
                mistakes.append(move)
                
        # If not enough mistakes to identify patterns, return
        if len(mistakes) < 2:
            return
            
        # Check for phase-specific patterns
        phase_mistakes = {}
        for move in mistakes:
            phase = move.get("phase", "middlegame")
            if phase not in phase_mistakes:
                phase_mistakes[phase] = []
            phase_mistakes[phase].append(move)
            
        for phase, moves in phase_mistakes.items():
            if len(moves) >= 2:
                analysis_results["mistake_patterns"].append({
                    "pattern": f"frequent_{phase}_mistakes",
                    "description": f"Multiple mistakes in the {phase} phase",
                    "count": len(moves),
                    "examples": [m.get("move", "") for m in moves[:2]]
                })
                
        # Check for concept-specific patterns
        concept_mistakes = {}
        for move in mistakes:
            for concept_data in move.get("concepts", []):
                concept = concept_data.get("concept", "")
                if concept:
                    if concept not in concept_mistakes:
                        concept_mistakes[concept] = []
                    concept_mistakes[concept].append(move)
                    
        for concept, moves in concept_mistakes.items():
            if len(moves) >= 2:
                analysis_results["mistake_patterns"].append({
                    "pattern": f"{concept}_mistakes",
                    "description": f"Multiple mistakes involving {concept}",
                    "count": len(moves),
                    "examples": [m.get("move", "") for m in moves[:2]]
                })
                
        # Check for tactical oversight patterns
        tactical_oversights = analysis_results.get("tactical_opportunities", [])
        if len(tactical_oversights) >= 2:
            tactics_by_type = {}
            for opp in tactical_oversights:
                for tactic in opp.get("tactics", []):
                    if tactic not in tactics_by_type:
                        tactics_by_type[tactic] = []
                    tactics_by_type[tactic].append(opp)
                    
            for tactic, opps in tactics_by_type.items():
                if len(opps) >= 2:
                    analysis_results["mistake_patterns"].append({
                        "pattern": f"missed_{tactic}_opportunities",
                        "description": f"Multiple missed {tactic} opportunities",
                        "count": len(opps),
                        "examples": [o.get("missed_move", "") for o in opps[:2]]
                    })
                    
    def _identify_strengths_and_weaknesses(self, analysis_results: Dict[str, Any]) -> None:
        """
        Identify player strengths and weaknesses based on analysis.
        
        Args:
            analysis_results: Analysis results to update
        """
        # Analyze phase performance
        phases = analysis_results.get("phases_analysis", {})
        
        for phase_name, phase_data in phases.items():
            if not phase_data or phase_data.get("move_count", 0) == 0:
                continue
                
            # Calculate phase accuracy
            accuracy = phase_data.get("accuracy_sum", 0) / phase_data.get("move_count", 1)
            
            # Determine if this phase is a strength or weakness
            if accuracy >= 75:
                analysis_results["strengths_identified"].append({
                    "concept": f"{phase_name}_play",
                    "confidence": min(1.0, accuracy / 100),
                    "evidence": f"Average accuracy of {accuracy:.1f}% in {phase_name}",
                    "example": ""
                })
            elif accuracy <= 60:
                analysis_results["weaknesses_identified"].append({
                    "concept": f"{phase_name}_play",
                    "severity": min(1.0, (100 - accuracy) / 100),
                    "evidence": f"Average accuracy of {accuracy:.1f}% in {phase_name}",
                    "example": ""
                })
                
        # Analyze concept performance
        all_concepts = {}
        
        # Collect concepts from all phases
        for phase_data in phases.values():
            for concept, data in phase_data.get("concepts", {}).items():
                if concept not in all_concepts:
                    all_concepts[concept] = {
                        "count": 0,
                        "confidence_sum": 0.0
                    }
                all_concepts[concept]["count"] += data.get("count", 0)
                all_concepts[concept]["confidence_sum"] += data.get("confidence_sum", 0.0)
                
        # Identify strengths and weaknesses based on concepts
        for concept, data in all_concepts.items():
            if data["count"] == 0:
                continue
                
            avg_confidence = data["confidence_sum"] / data["count"]
            
            # Concepts with high confidence and multiple occurrences are strengths
            if avg_confidence >= 0.7 and data["count"] >= 2:
                analysis_results["strengths_identified"].append({
                    "concept": concept,
                    "confidence": avg_confidence,
                    "evidence": f"Demonstrated {data['count']} times with high confidence",
                    "example": ""
                })
                
        # Analyze mistake patterns for weaknesses
        for pattern in analysis_results.get("mistake_patterns", []):
            pattern_name = pattern.get("pattern", "")
            if "mistakes" in pattern_name or "missed" in pattern_name:
                # Extract the concept from the pattern name
                concept = pattern_name.replace("_mistakes", "").replace("missed_", "").replace("_opportunities", "")
                
                analysis_results["weaknesses_identified"].append({
                    "concept": concept,
                    "severity": min(1.0, pattern.get("count", 0) / 5),  # Scale by number of occurrences
                    "evidence": pattern.get("description", ""),
                    "example": pattern.get("examples", [""])[0]
                })
                
        # Analyze tactical opportunities
        tactical_oversights = analysis_results.get("tactical_opportunities", [])
        if tactical_oversights:
            analysis_results["weaknesses_identified"].append({
                "concept": "tactical_awareness",
                "severity": min(1.0, len(tactical_oversights) / 5),  # Scale by number of missed tactics
                "evidence": f"Missed {len(tactical_oversights)} tactical opportunities",
                "example": tactical_oversights[0].get("missed_move", "") if tactical_oversights else ""
            })
            
    def _generate_improvement_suggestions(self, analysis_results: Dict[str, Any]) -> None:
        """
        Generate improvement suggestions based on analysis.
        
        Args:
            analysis_results: Analysis results to update
        """
        # Generate suggestions based on weaknesses
        for weakness in analysis_results.get("weaknesses_identified", []):
            concept = weakness.get("concept", "")
            severity = weakness.get("severity", 0.5)
            
            if not concept:
                continue
                
            # Generate suggestion based on concept
            suggestion = {
                "concept": concept,
                "priority": "high" if severity >= 0.7 else "medium" if severity >= 0.4 else "low",
                "description": "",
                "exercises": []
            }
            
            # Set description based on concept
            if "opening" in concept:
                suggestion["description"] = "Study opening principles and common opening lines"
                suggestion["exercises"] = ["Opening repertoire development", "Opening principles practice"]
            elif "middlegame" in concept:
                suggestion["description"] = "Focus on middlegame planning and piece coordination"
                suggestion["exercises"] = ["Positional understanding exercises", "Strategic planning practice"]
            elif "endgame" in concept:
                suggestion["description"] = "Study essential endgame techniques and principles"
                suggestion["exercises"] = ["Basic endgame positions", "Endgame technique drills"]
            elif "tactical" in concept:
                suggestion["description"] = "Improve tactical awareness through regular puzzle solving"
                suggestion["exercises"] = ["Tactical pattern recognition", "Calculation exercises"]
            elif concept in ["fork", "pin", "skewer", "discovered_attack"]:
                suggestion["description"] = f"Practice recognizing and creating {concept} opportunities"
                suggestion["exercises"] = [f"{concept.capitalize()} puzzles", "Tactical motif drills"]
            elif "pawn" in concept:
                suggestion["description"] = "Study pawn structure principles and common patterns"
                suggestion["exercises"] = ["Pawn structure analysis", "Pawn break exercises"]
            elif "king" in concept:
                suggestion["description"] = "Focus on king safety and king activity in appropriate phases"
                suggestion["exercises"] = ["King safety evaluation", "King activation in endgames"]
            elif "piece" in concept:
                suggestion["description"] = "Work on piece coordination and activity"
                suggestion["exercises"] = ["Piece coordination exercises", "Minor piece optimization"]
            else:
                suggestion["description"] = f"Practice {concept.replace('_', ' ')} through targeted exercises"
                suggestion["exercises"] = ["Focused drills", "Position analysis"]
                
            analysis_results["improvement_suggestions"].append(suggestion)
            
        # Add general suggestions if few specific ones were generated
        if len(analysis_results["improvement_suggestions"]) < 3:
            general_suggestions = [
                {
                    "concept": "calculation",
                    "priority": "medium",
                    "description": "Improve calculation skills through regular practice",
                    "exercises": ["Calculation training", "Visualization exercises"]
                },
                {
                    "concept": "pattern_recognition",
                    "priority": "medium",
                    "description": "Develop pattern recognition through consistent study",
                    "exercises": ["Common pattern drills", "Position comparison exercises"]
                },
                {
                    "concept": "game_analysis",
                    "priority": "medium",
                    "description": "Regularly analyze your games to identify improvement areas",
                    "exercises": ["Self-analysis routine", "Computer-assisted analysis"]
                }
            ]
            
            # Add general suggestions not already covered
            existing_concepts = {s["concept"] for s in analysis_results["improvement_suggestions"]}
            for suggestion in general_suggestions:
                if suggestion["concept"] not in existing_concepts:
                    analysis_results["improvement_suggestions"].append(suggestion)
                    
    def shutdown(self) -> bool:
        """
        Perform a clean shutdown.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            logger.info("Game Analysis Engine shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during Game Analysis Engine shutdown: {str(e)}")
            return False
