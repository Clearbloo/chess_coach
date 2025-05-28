"""
Chess Engine Interface Module for Chess Coach Software

This module provides an interface to chess engines for move validation,
position evaluation, and optimal move suggestions.
"""

import chess
import chess.engine
import chess.pgn
import io
import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ChessEngineInterface:
    """
    Interface to chess engines for move validation and position evaluation.
    """

    def __init__(self, engine_path: Optional[str] = None):
        """
        Initialize the Chess Engine Interface.

        Args:
            engine_path: Optional path to the chess engine executable
        """
        self.engine = None
        self.engine_path = engine_path
        self.initialized = False
        logger.info("Chess Engine Interface created")

    def initialize(self) -> bool:
        """
        Initialize the chess engine.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # If no engine path is provided, try to use stockfish from PATH
            if not self.engine_path:
                try:
                    from stockfish import Stockfish

                    self.stockfish = Stockfish()
                    logger.info("Using Stockfish from stockfish package")
                    self.initialized = True
                    return True
                except Exception as e:
                    logger.warning(
                        f"Could not initialize Stockfish from package: {str(e)}"
                    )
                    logger.info("Falling back to python-chess engine")

            # Use python-chess with the provided engine path or try to find it
            try:
                if not self.engine_path:
                    # Try common locations for Stockfish
                    common_paths = [
                        "stockfish",
                        "/usr/local/bin/stockfish",
                        "/usr/bin/stockfish",
                        "C:/Program Files/Stockfish/stockfish.exe",
                    ]

                    for path in common_paths:
                        try:
                            self.engine = chess.engine.SimpleEngine.popen_uci(path)
                            self.engine_path = path
                            break
                        except Exception:
                            continue
                else:
                    self.engine = chess.engine.SimpleEngine.popen_uci(self.engine_path)

                if self.engine:
                    logger.info(
                        f"Chess engine initialized with path: {self.engine_path}"
                    )
                    self.initialized = True
                    return True
                else:
                    logger.warning("Could not initialize chess engine with any path")
                    # We'll continue without an engine, using only python-chess for validation
                    self.initialized = True
                    return True

            except Exception as e:
                logger.error(f"Error initializing chess engine: {str(e)}")
                # We'll continue without an engine, using only python-chess for validation
                self.initialized = True
                return True

        except Exception as e:
            logger.error(f"Error during chess engine initialization: {str(e)}")
            return False

    def validate_game(self, game_data: Dict[str, Any]) -> bool:
        """
        Validate a chess game record.

        Args:
            game_data: The game data to validate, containing PGN or move list

        Returns:
            True if the game is valid, False otherwise
        """
        try:
            # Add detailed logging
            logger.info(f"Validating game data: {game_data}")

            # Check if we have PGN data
            if "pgn" in game_data and game_data["pgn"]:
                pgn_str = game_data["pgn"]
                logger.info(f"Validating PGN: {pgn_str}")

                # Ensure PGN has proper headers if not present
                if not pgn_str.startswith("["):
                    logger.info("Adding minimal headers to PGN")
                    pgn_str = f'[Event "Game"]\n[Site "Chess Coach"]\n[Date "????.??.??"]\n[Round "?"]\n[White "?"]\n[Black "?"]\n[Result "*"]\n\n{pgn_str}'

                pgn_io = io.StringIO(pgn_str)
                game = chess.pgn.read_game(pgn_io)

                if game is None:
                    logger.error("Failed to parse PGN: game is None")
                    return False

                logger.info("PGN parsed successfully")

                # Validate all moves in the game
                board = game.board()
                for move in game.mainline_moves():
                    if move not in board.legal_moves:
                        logger.error(f"Illegal move found: {move}")
                        return False
                    board.push(move)

                logger.info("All moves validated successfully")
                return True

            # Check if we have a move list
            elif "moves" in game_data and game_data["moves"]:
                logger.info(f"Validating move list: {game_data['moves']}")
                board = chess.Board()
                for move_str in game_data["moves"]:
                    try:
                        move = board.parse_san(move_str)
                        if move not in board.legal_moves:
                            logger.error(f"Illegal move found: {move_str}")
                            return False
                        board.push(move)
                    except ValueError as e:
                        logger.error(
                            f"Invalid move notation: {move_str}, error: {str(e)}"
                        )
                        return False

                logger.info("All moves in move list validated successfully")
                return True

            else:
                logger.error("No valid game data found in input")
                return False

        except Exception as e:
            logger.error(f"Error validating game: {str(e)}")
            return False

    def evaluate_position(self, fen: str, depth: int = 15) -> Dict[str, Any]:
        """
        Evaluate a chess position.

        Args:
            fen: FEN string representing the position
            depth: Search depth for evaluation

        Returns:
            Dictionary containing evaluation results
        """
        try:
            board = chess.Board(fen)

            # Check if we have a chess engine available
            if self.engine:
                info = self.engine.analyse(board, chess.engine.Limit(depth=depth))
                score = info["score"].relative.score(mate_score=10000)

                # Get best move
                result = self.engine.play(board, chess.engine.Limit(depth=depth))
                best_move = result.move

                return {
                    "score": score / 100.0,  # Convert centipawns to pawns
                    "best_move": board.san(best_move),
                    "best_move_uci": best_move.uci(),
                    "depth": depth,
                }
            elif hasattr(self, "stockfish"):
                # Use stockfish package if available
                self.stockfish.set_fen_position(fen)
                evaluation = self.stockfish.get_evaluation()
                best_move = self.stockfish.get_best_move()

                # Convert evaluation to standard format
                if evaluation["type"] == "cp":
                    score = evaluation["value"] / 100.0
                else:  # mate
                    score = 10000 if evaluation["value"] > 0 else -10000

                return {
                    "score": score,
                    "best_move": best_move,  # This is already in UCI format
                    "best_move_uci": best_move,
                    "depth": depth,
                }
            else:
                # Fallback to a simple material count if no engine is available
                material = self._calculate_material(board)
                return {
                    "score": material,
                    "best_move": None,
                    "best_move_uci": None,
                    "depth": 0,
                    "note": "No chess engine available, using simple material count",
                }

        except Exception as e:
            logger.error(f"Error evaluating position: {str(e)}")
            return {
                "error": str(e),
                "score": 0,
                "best_move": None,
                "best_move_uci": None,
                "depth": 0,
            }

    def _calculate_material(self, board: chess.Board) -> float:
        """
        Calculate material balance for a position.

        Args:
            board: Chess board position

        Returns:
            Material balance in pawns (positive for white advantage)
        """
        piece_values = {
            chess.PAWN: 1.0,
            chess.KNIGHT: 3.0,
            chess.BISHOP: 3.0,
            chess.ROOK: 5.0,
            chess.QUEEN: 9.0,
            chess.KING: 0.0,  # King has no material value for counting
        }

        material = 0.0

        for piece_type in piece_values:
            material += (
                len(board.pieces(piece_type, chess.WHITE)) * piece_values[piece_type]
            )
            material -= (
                len(board.pieces(piece_type, chess.BLACK)) * piece_values[piece_type]
            )

        return material

    def get_legal_moves(self, fen: str) -> List[str]:
        """
        Get all legal moves for a position.

        Args:
            fen: FEN string representing the position

        Returns:
            List of legal moves in SAN notation
        """
        try:
            board = chess.Board(fen)
            legal_moves = []

            for move in board.legal_moves:
                legal_moves.append(board.san(move))

            return legal_moves

        except Exception as e:
            logger.error(f"Error getting legal moves: {str(e)}")
            return []

    def classify_move(self, fen: str, move_san: str, depth: int = 15) -> Dict[str, Any]:
        """
        Classify a move's quality compared to the best move.

        Args:
            fen: FEN string representing the position before the move
            move_san: The move to classify in SAN notation
            depth: Search depth for evaluation

        Returns:
            Dictionary with move classification and evaluation
        """
        try:
            board = chess.Board(fen)

            # Parse the move
            try:
                move = board.parse_san(move_san)
            except ValueError:
                return {"error": f"Invalid move: {move_san}"}

            # Evaluate the position before the move
            pre_eval = self.evaluate_position(fen, depth)

            # Make the move and evaluate the new position
            board.push(move)
            post_fen = board.fen()
            post_eval = self.evaluate_position(post_fen, depth)

            # Calculate the evaluation difference (from the perspective of the player to move)
            if board.turn == chess.WHITE:
                eval_diff = -post_eval["score"] - pre_eval["score"]
            else:
                eval_diff = post_eval["score"] - pre_eval["score"]

            # Classify the move based on the evaluation difference
            classification = self._classify_by_eval_diff(eval_diff)

            return {
                "move": move_san,
                "evaluation": post_eval["score"],
                "eval_diff": eval_diff,
                "classification": classification,
                "best_move": pre_eval["best_move"],
                "depth": depth,
            }

        except Exception as e:
            logger.error(f"Error classifying move: {str(e)}")
            return {"error": str(e)}

    def _classify_by_eval_diff(self, eval_diff: float) -> str:
        """
        Classify a move based on evaluation difference.

        Args:
            eval_diff: Evaluation difference in pawns

        Returns:
            Classification string
        """
        if eval_diff >= 2.0:
            return "Blunder"
        elif eval_diff >= 1.0:
            return "Mistake"
        elif eval_diff >= 0.3:
            return "Inaccuracy"
        elif eval_diff >= -0.1:
            return "Good"
        else:
            return "Best"

    def get_alternative_moves(
        self, fen: str, num_moves: int = 3, depth: int = 15
    ) -> List[Dict[str, Any]]:
        """
        Get top alternative moves for a position.

        Args:
            fen: FEN string representing the position
            num_moves: Number of top moves to return
            depth: Search depth for evaluation

        Returns:
            List of top moves with evaluations
        """
        try:
            board = chess.Board(fen)

            if self.engine:
                # Use the chess engine to get multiple top moves
                multipv_info = self.engine.analyse(
                    board, chess.engine.Limit(depth=depth), multipv=num_moves
                )

                alternatives = []
                for i, info in enumerate(multipv_info):
                    score = info["score"].relative.score(mate_score=10000)
                    move = info["pv"][0]

                    alternatives.append(
                        {
                            "move": board.san(move),
                            "move_uci": move.uci(),
                            "score": score / 100.0,
                            "rank": i + 1,
                        }
                    )

                return alternatives

            elif hasattr(self, "stockfish"):
                # Use stockfish package if available
                self.stockfish.set_fen_position(fen)
                top_moves = self.stockfish.get_top_moves(num_moves)

                alternatives = []
                for i, move_info in enumerate(top_moves):
                    alternatives.append(
                        {
                            "move": move_info["Move"],
                            "move_uci": move_info["Move"],
                            "score": move_info["Centipawn"] / 100.0
                            if "Centipawn" in move_info
                            else 0,
                            "rank": i + 1,
                        }
                    )

                return alternatives

            else:
                # Fallback to a simple approach if no engine is available
                return [
                    {
                        "move": "N/A",
                        "move_uci": "",
                        "score": 0,
                        "rank": 1,
                        "note": "No chess engine available",
                    }
                ]

        except Exception as e:
            logger.error(f"Error getting alternative moves: {str(e)}")
            return []

    def shutdown(self) -> None:
        """Clean up resources used by the chess engine."""
        if self.engine:
            try:
                self.engine.quit()
                logger.info("Chess engine shut down successfully")
            except Exception as e:
                logger.error(f"Error shutting down chess engine: {str(e)}")
