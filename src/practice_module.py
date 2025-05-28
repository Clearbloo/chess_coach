"""
Practice Module for Chess Coach Software

This module generates customized exercises targeting specific improvement areas.
"""

import chess
import chess.pgn
import io
import json
import logging
import os
import random
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PracticeModule:
    """
    Generates targeted exercises based on user needs.
    """
    
    def __init__(self, data_dir: str = "./data/exercises"):
        """
        Initialize the Practice Module.
        
        Args:
            data_dir: Directory to store exercise data
        """
        self.data_dir = data_dir
        self.chess_engine = None  # Will be set by core engine
        self.user_profile_manager = None  # Will be set by core engine
        self.exercise_templates = {}  # Cache of exercise templates
        self.initialized = False
        logger.info("Practice Module created")
        
    def initialize(self) -> bool:
        """
        Initialize the Practice Module.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Create data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Load exercise templates
            self._load_exercise_templates()
            
            self.initialized = True
            logger.info(f"Practice Module initialized with data directory: {self.data_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Practice Module: {str(e)}")
            return False
            
    def set_chess_engine(self, chess_engine: Any) -> None:
        """
        Set the chess engine reference.
        
        Args:
            chess_engine: Reference to the chess engine interface
        """
        self.chess_engine = chess_engine
        logger.info("Chess engine reference set in Practice Module")
        
    def set_user_profile_manager(self, user_profile_manager: Any) -> None:
        """
        Set the user profile manager reference.
        
        Args:
            user_profile_manager: Reference to the user profile manager
        """
        self.user_profile_manager = user_profile_manager
        logger.info("User Profile Manager reference set in Practice Module")
        
    def _load_exercise_templates(self) -> None:
        """Load exercise templates from files or create default templates."""
        try:
            template_file = os.path.join(self.data_dir, "templates.json")
            
            if os.path.exists(template_file):
                with open(template_file, 'r') as f:
                    self.exercise_templates = json.load(f)
                    logger.info(f"Loaded {len(self.exercise_templates)} exercise templates")
            else:
                # Create default templates
                self._create_default_templates()
                
                # Save templates to file
                with open(template_file, 'w') as f:
                    json.dump(self.exercise_templates, f, indent=2)
                    logger.info(f"Created and saved default exercise templates")
                    
        except Exception as e:
            logger.error(f"Error loading exercise templates: {str(e)}")
            # Create default templates as fallback
            self._create_default_templates()
            
    def _create_default_templates(self) -> None:
        """Create default exercise templates."""
        self.exercise_templates = {
            "tactical": {
                "fork": [
                    {
                        "name": "Knight Fork Basic",
                        "difficulty": "easy",
                        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
                        "solution": "Nxe5",
                        "description": "Find the knight fork targeting the king and queen."
                    },
                    {
                        "name": "Knight Fork Intermediate",
                        "difficulty": "medium",
                        "fen": "r2qkbnr/ppp2ppp/2np4/4p3/2B1P1b1/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 0 1",
                        "solution": "Nxe5",
                        "description": "Find the knight fork targeting multiple pieces."
                    }
                ],
                "pin": [
                    {
                        "name": "Bishop Pin Basic",
                        "difficulty": "easy",
                        "fen": "rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
                        "solution": "Bb5+",
                        "description": "Pin the knight to the king with the bishop."
                    },
                    {
                        "name": "Rook Pin Intermediate",
                        "difficulty": "medium",
                        "fen": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
                        "solution": "Bxf7+",
                        "description": "Create a pin that leads to material gain."
                    }
                ],
                "discovered_attack": [
                    {
                        "name": "Discovered Check Basic",
                        "difficulty": "easy",
                        "fen": "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 1",
                        "solution": "Bxf7+",
                        "description": "Find the discovered check that wins material."
                    }
                ],
                "mate_pattern": [
                    {
                        "name": "Back Rank Mate",
                        "difficulty": "easy",
                        "fen": "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1",
                        "solution": "Ra8#",
                        "description": "Find the back rank checkmate."
                    },
                    {
                        "name": "Smothered Mate",
                        "difficulty": "medium",
                        "fen": "6k1/5ppp/7N/8/8/8/5PPP/6K1 w - - 0 1",
                        "solution": "Nf7",
                        "description": "Find the smothered mate sequence."
                    }
                ]
            },
            "strategic": {
                "pawn_structure": [
                    {
                        "name": "Isolated Pawn Weakness",
                        "difficulty": "medium",
                        "fen": "r1bqkbnr/pp1p1ppp/2n1p3/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 0 1",
                        "solution": "d5",
                        "description": "Find the move that creates an isolated pawn weakness."
                    }
                ],
                "piece_activity": [
                    {
                        "name": "Knight Outpost",
                        "difficulty": "medium",
                        "fen": "r1bqkb1r/ppp2ppp/2np1n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 1",
                        "solution": "d4",
                        "description": "Find the move that prepares a strong knight outpost."
                    }
                ],
                "king_safety": [
                    {
                        "name": "King Safety Assessment",
                        "difficulty": "medium",
                        "fen": "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R b KQkq - 0 1",
                        "solution": "O-O",
                        "description": "Find the best move to ensure king safety."
                    }
                ]
            },
            "endgame": {
                "pawn_endgame": [
                    {
                        "name": "Pawn Promotion Race",
                        "difficulty": "medium",
                        "fen": "8/5p2/8/2k5/8/8/3P4/3K4 w - - 0 1",
                        "solution": "d4",
                        "description": "Find the winning move in this pawn endgame."
                    }
                ],
                "king_activity": [
                    {
                        "name": "Active King",
                        "difficulty": "medium",
                        "fen": "8/8/8/3k4/8/3P4/3K4/8 w - - 0 1",
                        "solution": "Ke3",
                        "description": "Find the best king move to support the pawn."
                    }
                ],
                "rook_endgame": [
                    {
                        "name": "Rook Behind Passed Pawn",
                        "difficulty": "hard",
                        "fen": "8/8/8/3k4/3p4/8/3R4/3K4 w - - 0 1",
                        "solution": "Rd8+",
                        "description": "Find the winning move in this rook endgame."
                    }
                ]
            },
            "opening": {
                "development": [
                    {
                        "name": "Opening Development",
                        "difficulty": "easy",
                        "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                        "solution": "e5",
                        "description": "Find the best developing move in this opening position."
                    }
                ],
                "center_control": [
                    {
                        "name": "Center Control",
                        "difficulty": "easy",
                        "fen": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
                        "solution": "Nf3",
                        "description": "Find the best move to control the center."
                    }
                ]
            }
        }
        
    def generate_exercises(self, user_profile: Dict[str, Any], 
                         focus_areas: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate practice exercises based on user profile.
        
        Args:
            user_profile: User profile data
            focus_areas: Optional list of specific areas to focus on
            
        Returns:
            List of generated exercises
        """
        try:
            # Ensure chess engine is available
            if not self.chess_engine:
                raise ValueError("Chess engine not available for exercise generation")
                
            # Initialize exercises list
            exercises = []
            
            # Determine areas to focus on
            target_areas = self._determine_target_areas(user_profile, focus_areas)
            
            # Generate exercises for each target area
            for area in target_areas:
                area_exercises = self._generate_area_exercises(area, user_profile)
                exercises.extend(area_exercises)
                
            # If we have too few exercises, add some general ones
            if len(exercises) < 5:
                general_exercises = self._generate_general_exercises(user_profile)
                exercises.extend(general_exercises)
                
            # Limit to a reasonable number of exercises
            if len(exercises) > 10:
                # Prioritize exercises targeting weaknesses
                weakness_exercises = [e for e in exercises if e.get("target_weakness")]
                other_exercises = [e for e in exercises if not e.get("target_weakness")]
                
                # Take up to 7 weakness exercises and 3 other exercises
                selected_weakness = weakness_exercises[:7]
                selected_other = other_exercises[:3]
                
                exercises = selected_weakness + selected_other
                
            # Ensure each exercise has a unique ID
            for i, exercise in enumerate(exercises):
                if "id" not in exercise:
                    exercise["id"] = f"exercise_{random.randint(10000, 99999)}_{i}"
                    
            return exercises
            
        except Exception as e:
            logger.error(f"Error generating exercises: {str(e)}")
            return []
            
    def _determine_target_areas(self, user_profile: Dict[str, Any], 
                              focus_areas: Optional[List[str]]) -> List[str]:
        """
        Determine which areas to focus on for exercise generation.
        
        Args:
            user_profile: User profile data
            focus_areas: Optional list of specific areas to focus on
            
        Returns:
            List of target areas
        """
        # If focus areas are explicitly provided, use those
        if focus_areas:
            return focus_areas
            
        # Otherwise, determine based on user profile
        target_areas = []
        
        # Get weaknesses from user profile
        weaknesses = user_profile.get("statistics", {}).get("weakness_areas", [])
        
        # Add all weakness concepts as target areas
        for weakness in weaknesses:
            concept = weakness.get("concept", "")
            if concept:
                target_areas.append(concept)
                
        # If we have too few target areas, add some general ones
        if len(target_areas) < 3:
            general_areas = ["tactical_awareness", "strategic_planning", "endgame_technique"]
            for area in general_areas:
                if area not in target_areas:
                    target_areas.append(area)
                    
        return target_areas
        
    def _generate_area_exercises(self, area: str, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate exercises for a specific target area.
        
        Args:
            area: Target area to generate exercises for
            user_profile: User profile data
            
        Returns:
            List of exercises for the target area
        """
        exercises = []
        
        # Map the target area to exercise categories and concepts
        category, concepts = self._map_area_to_exercise_types(area)
        
        # Get user's skill level
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Determine appropriate difficulty
        if skill_level == "Beginner":
            difficulties = ["easy", "medium"]
        elif skill_level == "Intermediate":
            difficulties = ["medium", "hard"]
        else:  # Advanced or Expert
            difficulties = ["hard", "expert"]
            
        # Generate exercises for each concept
        for concept in concepts:
            # Check if we have templates for this concept
            if category in self.exercise_templates and concept in self.exercise_templates[category]:
                templates = self.exercise_templates[category][concept]
                
                # Filter templates by difficulty
                suitable_templates = [t for t in templates if t.get("difficulty", "medium") in difficulties]
                
                # If no suitable templates, use any templates for this concept
                if not suitable_templates and templates:
                    suitable_templates = templates
                    
                # Select templates (up to 2 per concept)
                selected_templates = random.sample(suitable_templates, min(2, len(suitable_templates)))
                
                # Create exercises from templates
                for template in selected_templates:
                    exercise = self._create_exercise_from_template(template, area, category, concept)
                    exercises.append(exercise)
            else:
                # If no templates available, generate a custom exercise
                exercise = self._generate_custom_exercise(area, category, concept, difficulties[0])
                if exercise:
                    exercises.append(exercise)
                    
        return exercises
        
    def _map_area_to_exercise_types(self, area: str) -> Tuple[str, List[str]]:
        """
        Map a target area to exercise categories and concepts.
        
        Args:
            area: Target area
            
        Returns:
            Tuple of (category, list of concepts)
        """
        # Mapping of areas to exercise categories and concepts
        area_mapping = {
            # Tactical areas
            "tactical_awareness": ("tactical", ["fork", "pin", "discovered_attack", "mate_pattern"]),
            "calculation": ("tactical", ["mate_pattern", "discovered_attack"]),
            "pattern_recognition": ("tactical", ["fork", "pin", "discovered_attack"]),
            "fork": ("tactical", ["fork"]),
            "pin": ("tactical", ["pin"]),
            "discovered_attack": ("tactical", ["discovered_attack"]),
            
            # Strategic areas
            "strategic_planning": ("strategic", ["pawn_structure", "piece_activity"]),
            "positional_understanding": ("strategic", ["pawn_structure", "piece_activity", "king_safety"]),
            "pawn_structure": ("strategic", ["pawn_structure"]),
            "piece_activity": ("strategic", ["piece_activity"]),
            "king_safety": ("strategic", ["king_safety"]),
            
            # Endgame areas
            "endgame_technique": ("endgame", ["pawn_endgame", "king_activity", "rook_endgame"]),
            "pawn_endgame": ("endgame", ["pawn_endgame"]),
            "king_activity": ("endgame", ["king_activity"]),
            "rook_endgame": ("endgame", ["rook_endgame"]),
            
            # Opening areas
            "opening_play": ("opening", ["development", "center_control"]),
            "development": ("opening", ["development"]),
            "center_control": ("opening", ["center_control"])
        }
        
        # Default mapping if area not found
        default_mapping = ("tactical", ["fork", "pin", "discovered_attack"])
        
        # Convert area to lowercase and replace spaces with underscores
        normalized_area = area.lower().replace(" ", "_")
        
        # Return mapping for area or default
        return area_mapping.get(normalized_area, default_mapping)
        
    def _create_exercise_from_template(self, template: Dict[str, Any], target_area: str, 
                                     category: str, concept: str) -> Dict[str, Any]:
        """
        Create an exercise from a template.
        
        Args:
            template: Exercise template
            target_area: Target area for the exercise
            category: Exercise category
            concept: Exercise concept
            
        Returns:
            Exercise data
        """
        # Create exercise from template
        exercise = {
            "id": f"exercise_{random.randint(10000, 99999)}",
            "type": category,
            "concept": concept,
            "difficulty": template.get("difficulty", "medium"),
            "position": template.get("fen", ""),
            "correct_moves": [template.get("solution", "")],
            "hints": [
                template.get("description", ""),
                f"Look for a {concept.replace('_', ' ')} opportunity."
            ],
            "target_weakness": target_area,
            "user_attempts": []
        }
        
        return exercise
        
    def _generate_custom_exercise(self, target_area: str, category: str, 
                                concept: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """
        Generate a custom exercise when no template is available.
        
        Args:
            target_area: Target area for the exercise
            category: Exercise category
            concept: Exercise concept
            difficulty: Exercise difficulty
            
        Returns:
            Exercise data or None if generation fails
        """
        try:
            # In a real implementation, this would generate a custom exercise
            # For now, we'll return a placeholder exercise
            
            # Get a starting position based on the concept
            fen, solution, description = self._get_placeholder_position(concept, difficulty)
            
            if not fen:
                return None
                
            # Create exercise
            exercise = {
                "id": f"exercise_{random.randint(10000, 99999)}",
                "type": category,
                "concept": concept,
                "difficulty": difficulty,
                "position": fen,
                "correct_moves": [solution],
                "hints": [
                    description,
                    f"Look for a {concept.replace('_', ' ')} opportunity."
                ],
                "target_weakness": target_area,
                "user_attempts": []
            }
            
            return exercise
            
        except Exception as e:
            logger.error(f"Error generating custom exercise: {str(e)}")
            return None
            
    def _get_placeholder_position(self, concept: str, difficulty: str) -> Tuple[str, str, str]:
        """
        Get a placeholder position for a concept.
        
        Args:
            concept: Exercise concept
            difficulty: Exercise difficulty
            
        Returns:
            Tuple of (FEN, solution, description)
        """
        # Placeholder positions for different concepts
        positions = {
            "fork": (
                "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1",
                "Nxe5",
                "Find the knight fork targeting multiple pieces."
            ),
            "pin": (
                "rnbqkbnr/ppp2ppp/8/3pp3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1",
                "Bb5+",
                "Pin the knight to the king with the bishop."
            ),
            "discovered_attack": (
                "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 0 1",
                "Bxf7+",
                "Find the discovered check that wins material."
            ),
            "mate_pattern": (
                "6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1",
                "Ra8#",
                "Find the checkmate in one move."
            ),
            "pawn_structure": (
                "r1bqkbnr/pp1p1ppp/2n1p3/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 0 1",
                "d5",
                "Find the move that creates a pawn structure advantage."
            ),
            "piece_activity": (
                "r1bqkb1r/ppp2ppp/2np1n2/4p3/4P3/2N2N2/PPPP1PPP/R1BQKB1R w KQkq - 0 1",
                "d4",
                "Find the move that improves piece activity."
            ),
            "king_safety": (
                "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R b KQkq - 0 1",
                "O-O",
                "Find the best move to ensure king safety."
            ),
            "pawn_endgame": (
                "8/5p2/8/2k5/8/8/3P4/3K4 w - - 0 1",
                "d4",
                "Find the winning move in this pawn endgame."
            ),
            "king_activity": (
                "8/8/8/3k4/8/3P4/3K4/8 w - - 0 1",
                "Ke3",
                "Find the best king move to support the pawn."
            ),
            "rook_endgame": (
                "8/8/8/3k4/3p4/8/3R4/3K4 w - - 0 1",
                "Rd8+",
                "Find the winning move in this rook endgame."
            ),
            "development": (
                "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1",
                "e5",
                "Find the best developing move in this opening position."
            ),
            "center_control": (
                "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1",
                "Nf3",
                "Find the best move to control the center."
            )
        }
        
        # Return position for concept or empty strings if not found
        return positions.get(concept, ("", "", ""))
        
    def _generate_general_exercises(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate general exercises not targeting specific weaknesses.
        
        Args:
            user_profile: User profile data
            
        Returns:
            List of general exercises
        """
        exercises = []
        
        # Get user's skill level
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Determine appropriate difficulty
        if skill_level == "Beginner":
            difficulties = ["easy"]
        elif skill_level == "Intermediate":
            difficulties = ["medium"]
        else:  # Advanced or Expert
            difficulties = ["hard"]
            
        # Select general exercise categories
        categories = ["tactical", "strategic", "endgame", "opening"]
        
        # Generate exercises for each category
        for category in categories:
            if category in self.exercise_templates:
                # Get all concepts for this category
                concepts = list(self.exercise_templates[category].keys())
                
                # Select a random concept
                if concepts:
                    concept = random.choice(concepts)
                    templates = self.exercise_templates[category][concept]
                    
                    # Filter templates by difficulty
                    suitable_templates = [t for t in templates if t.get("difficulty", "medium") in difficulties]
                    
                    # If no suitable templates, use any templates for this concept
                    if not suitable_templates and templates:
                        suitable_templates = templates
                        
                    # Select a template
                    if suitable_templates:
                        template = random.choice(suitable_templates)
                        
                        # Create exercise from template
                        exercise = self._create_exercise_from_template(template, "", category, concept)
                        exercise.pop("target_weakness", None)  # Remove target weakness for general exercises
                        exercises.append(exercise)
                        
        return exercises
        
    def validate_exercise_solution(self, exercise_id: str, user_move: str) -> Dict[str, Any]:
        """
        Validate a user's solution to an exercise.
        
        Args:
            exercise_id: ID of the exercise
            user_move: User's move in SAN or UCI notation
            
        Returns:
            Validation result
        """
        try:
            # In a real implementation, this would load the exercise from storage
            # For now, we'll use a placeholder implementation
            
            # Find the exercise in the templates
            exercise = None
            for category in self.exercise_templates:
                for concept in self.exercise_templates[category]:
                    for template in self.exercise_templates[category][concept]:
                        if template.get("id") == exercise_id:
                            exercise = template
                            break
                    if exercise:
                        break
                if exercise:
                    break
                    
            if not exercise:
                return {
                    "exercise_id": exercise_id,
                    "success": False,
                    "message": "Exercise not found"
                }
                
            # Get the correct solution
            correct_solution = exercise.get("solution", "")
            
            # Normalize moves for comparison
            normalized_user_move = self._normalize_move(user_move)
            normalized_solution = self._normalize_move(correct_solution)
            
            # Check if the move is correct
            is_correct = normalized_user_move == normalized_solution
            
            # Generate result
            result = {
                "exercise_id": exercise_id,
                "success": is_correct,
                "user_move": user_move,
                "correct_move": correct_solution,
                "message": "Correct solution!" if is_correct else "Incorrect solution."
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating exercise solution: {str(e)}")
            return {
                "exercise_id": exercise_id,
                "success": False,
                "message": f"Error: {str(e)}"
            }
            
    def _normalize_move(self, move: str) -> str:
        """
        Normalize a move for comparison.
        
        Args:
            move: Move in SAN or UCI notation
            
        Returns:
            Normalized move
        """
        # Remove check and checkmate symbols
        normalized = move.replace("+", "").replace("#", "")
        
        # Convert to lowercase
        normalized = normalized.lower()
        
        return normalized
        
    def get_exercise_hint(self, exercise_id: str, hint_level: int = 1) -> Dict[str, Any]:
        """
        Get a hint for an exercise.
        
        Args:
            exercise_id: ID of the exercise
            hint_level: Level of hint to provide (1-3)
            
        Returns:
            Hint data
        """
        try:
            # In a real implementation, this would load the exercise from storage
            # For now, we'll use a placeholder implementation
            
            # Find the exercise in the templates
            exercise = None
            for category in self.exercise_templates:
                for concept in self.exercise_templates[category]:
                    for template in self.exercise_templates[category][concept]:
                        if template.get("id") == exercise_id:
                            exercise = template
                            break
                    if exercise:
                        break
                if exercise:
                    break
                    
            if not exercise:
                return {
                    "exercise_id": exercise_id,
                    "hint": "Exercise not found"
                }
                
            # Generate hint based on level
            hint = ""
            if hint_level == 1:
                hint = exercise.get("description", "Look for the best move in this position.")
            elif hint_level == 2:
                concept = next((c for c, templates in self.exercise_templates.get(category, {}).items() 
                              if exercise in templates), "")
                hint = f"Look for a {concept.replace('_', ' ')} opportunity."
            else:  # hint_level >= 3
                solution = exercise.get("solution", "")
                if solution:
                    piece = solution[0] if solution[0].isupper() else "pawn"
                    hint = f"The solution involves moving the {piece}."
                else:
                    hint = "No specific hint available for this level."
                    
            return {
                "exercise_id": exercise_id,
                "hint_level": hint_level,
                "hint": hint
            }
            
        except Exception as e:
            logger.error(f"Error getting exercise hint: {str(e)}")
            return {
                "exercise_id": exercise_id,
                "hint": f"Error: {str(e)}"
            }
            
    def record_exercise_attempt(self, exercise_id: str, user_id: str, 
                              result: Dict[str, Any]) -> bool:
        """
        Record a user's attempt at an exercise.
        
        Args:
            exercise_id: ID of the exercise
            user_id: ID of the user
            result: Result of the attempt
            
        Returns:
            True if recording was successful, False otherwise
        """
        try:
            # Ensure user profile manager is available
            if not self.user_profile_manager:
                raise ValueError("User Profile Manager not available for recording exercise attempt")
                
            # Update user profile with exercise result
            success = self.user_profile_manager.update_with_exercise_result(
                user_id, exercise_id, result
            )
            
            return success
            
        except Exception as e:
            logger.error(f"Error recording exercise attempt: {str(e)}")
            return False
            
    def generate_practice_session(self, user_id: str, session_type: str = "mixed", 
                                duration: int = 15) -> Dict[str, Any]:
        """
        Generate a complete practice session.
        
        Args:
            user_id: ID of the user
            session_type: Type of session (tactical, strategic, endgame, mixed)
            duration: Approximate duration in minutes
            
        Returns:
            Practice session data
        """
        try:
            # Ensure user profile manager is available
            if not self.user_profile_manager:
                raise ValueError("User Profile Manager not available for generating practice session")
                
            # Get user profile
            user_profile = self.user_profile_manager.get_profile(user_id)
            if not user_profile:
                raise ValueError(f"User profile not found for ID: {user_id}")
                
            # Determine focus areas based on session type
            focus_areas = []
            if session_type == "tactical":
                focus_areas = ["tactical_awareness", "calculation", "pattern_recognition"]
            elif session_type == "strategic":
                focus_areas = ["strategic_planning", "positional_understanding", "pawn_structure"]
            elif session_type == "endgame":
                focus_areas = ["endgame_technique", "king_activity", "pawn_endgame"]
            elif session_type == "opening":
                focus_areas = ["opening_play", "development", "center_control"]
                
            # Determine number of exercises based on duration
            # Assuming ~3 minutes per exercise
            num_exercises = max(1, min(10, duration // 3))
            
            # Generate exercises
            all_exercises = self.generate_exercises(user_profile, focus_areas)
            
            # Select exercises for the session
            session_exercises = all_exercises[:num_exercises]
            
            # Create session
            session = {
                "id": f"session_{random.randint(10000, 99999)}",
                "user_id": user_id,
                "type": session_type,
                "duration": duration,
                "exercises": session_exercises,
                "created_at": "",  # Would be set to current time in a real implementation
                "completed": False
            }
            
            return session
            
        except Exception as e:
            logger.error(f"Error generating practice session: {str(e)}")
            return {
                "error": str(e),
                "user_id": user_id
            }
            
    def shutdown(self) -> bool:
        """
        Perform a clean shutdown.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            logger.info("Practice Module shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during Practice Module shutdown: {str(e)}")
            return False
