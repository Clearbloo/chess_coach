"""
Feedback Generator Module for Chess Coach Software

This module creates personalized, actionable feedback based on analysis results.
"""

import logging
import random
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FeedbackGenerator:
    """
    Creates personalized, actionable feedback based on analysis results.
    """
    
    def __init__(self):
        """Initialize the Feedback Generator."""
        self.user_profile_manager = None  # Will be set by core engine
        self.initialized = False
        logger.info("Feedback Generator created")
        
    def initialize(self) -> bool:
        """
        Initialize the Feedback Generator.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Initialization logic
            self.initialized = True
            logger.info("Feedback Generator initialized")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing Feedback Generator: {str(e)}")
            return False
            
    def set_user_profile_manager(self, user_profile_manager: Any) -> None:
        """
        Set the user profile manager reference.
        
        Args:
            user_profile_manager: Reference to the user profile manager
        """
        self.user_profile_manager = user_profile_manager
        logger.info("User Profile Manager reference set in Feedback Generator")
        
    def generate_feedback(self, analysis_results: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Generate personalized feedback based on game analysis.
        
        Args:
            analysis_results: Results from game analysis
            user_id: ID of the user to generate feedback for
            
        Returns:
            Feedback data
        """
        try:
            # Ensure user profile manager is available
            if not self.user_profile_manager:
                raise ValueError("User Profile Manager not available for feedback generation")
                
            # Get user profile
            user_profile = self.user_profile_manager.get_profile(user_id)
            if not user_profile:
                raise ValueError(f"User profile not found for ID: {user_id}")
                
            # Initialize feedback
            feedback = {
                "id": f"feedback_{random.randint(10000, 99999)}",
                "user_id": user_id,
                "game_id": analysis_results.get("game_id", "unknown"),
                "type": "game_feedback",
                "summary": "",
                "strengths": [],
                "weaknesses": [],
                "improvement_areas": [],
                "positive_notes": [],
                "detailed_feedback": [],
                "visual_aids": []
            }
            
            # Generate summary
            feedback["summary"] = self._generate_summary(analysis_results, user_profile)
            
            # Process strengths
            for strength in analysis_results.get("strengths_identified", []):
                feedback["strengths"].append({
                    "concept": strength.get("concept", ""),
                    "description": self._generate_strength_description(strength, user_profile),
                    "example": strength.get("example", "")
                })
                
            # Process weaknesses
            for weakness in analysis_results.get("weaknesses_identified", []):
                feedback["weaknesses"].append({
                    "concept": weakness.get("concept", ""),
                    "description": self._generate_weakness_description(weakness, user_profile),
                    "example": weakness.get("example", ""),
                    "improvement_suggestion": self._generate_improvement_suggestion(weakness)
                })
                
            # Generate improvement areas from suggestions
            for suggestion in analysis_results.get("improvement_suggestions", []):
                feedback["improvement_areas"].append({
                    "concept": suggestion.get("concept", ""),
                    "priority": suggestion.get("priority", "medium"),
                    "description": suggestion.get("description", ""),
                    "exercises": suggestion.get("exercises", [])
                })
                
            # Generate positive notes
            feedback["positive_notes"] = self._generate_positive_notes(analysis_results, user_profile)
            
            # Generate detailed feedback for specific moves
            feedback["detailed_feedback"] = self._generate_detailed_move_feedback(
                analysis_results.get("move_analysis", []),
                user_profile
            )
            
            # Generate visual aids
            feedback["visual_aids"] = self._generate_visual_aids(analysis_results)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating feedback: {str(e)}")
            return {
                "error": str(e),
                "user_id": user_id,
                "game_id": analysis_results.get("game_id", "unknown")
            }
            
    def _generate_summary(self, analysis_results: Dict[str, Any], 
                        user_profile: Dict[str, Any]) -> str:
        """
        Generate a summary of the game analysis.
        
        Args:
            analysis_results: Results from game analysis
            user_profile: User profile data
            
        Returns:
            Summary text
        """
        # Get user name and skill level
        name = user_profile.get("name", "Player")
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Get game statistics
        accuracy = analysis_results.get("overall_accuracy", 0.0)
        player_color = analysis_results.get("player_color", "white").capitalize()
        
        # Count move classifications
        best_moves = 0
        good_moves = 0
        inaccuracies = 0
        mistakes = 0
        blunders = 0
        
        for move in analysis_results.get("move_analysis", []):
            classification = move.get("classification", "")
            if classification == "Best":
                best_moves += 1
            elif classification == "Good":
                good_moves += 1
            elif classification == "Inaccuracy":
                inaccuracies += 1
            elif classification == "Mistake":
                mistakes += 1
            elif classification == "Blunder":
                blunders += 1
                
        # Generate summary text
        summary = f"Game Analysis Summary for {name}\n\n"
        summary += f"You played as {player_color} with an overall accuracy of {accuracy:.1f}%.\n"
        summary += f"Move Quality: {best_moves} best moves, {good_moves} good moves, "
        summary += f"{inaccuracies} inaccuracies, {mistakes} mistakes, and {blunders} blunders.\n\n"
        
        # Add strength/weakness summary
        strengths = analysis_results.get("strengths_identified", [])
        weaknesses = analysis_results.get("weaknesses_identified", [])
        
        if strengths:
            summary += "Key Strengths: "
            summary += ", ".join(s.get("concept", "").replace("_", " ").title() 
                               for s in strengths[:3])
            summary += ".\n"
            
        if weaknesses:
            summary += "Areas for Improvement: "
            summary += ", ".join(w.get("concept", "").replace("_", " ").title() 
                               for w in weaknesses[:3])
            summary += ".\n"
            
        # Add personalized note based on skill level
        if skill_level == "Beginner":
            summary += "\nAs a beginner, focus on the fundamental principles and don't be discouraged by mistakes. "
            summary += "Each game is a learning opportunity to improve your chess understanding."
        elif skill_level == "Intermediate":
            summary += "\nAt your intermediate level, work on consistency and reducing tactical oversights. "
            summary += "Pay attention to the detailed feedback to refine your strategic understanding."
        else:  # Advanced or Expert
            summary += "\nAt your advanced level, the subtle improvements in position evaluation and calculation "
            summary += "will make the biggest difference. Focus on the critical moments identified in the analysis."
            
        return summary
        
    def _generate_strength_description(self, strength: Dict[str, Any], 
                                     user_profile: Dict[str, Any]) -> str:
        """
        Generate a description for an identified strength.
        
        Args:
            strength: Strength data
            user_profile: User profile data
            
        Returns:
            Strength description
        """
        concept = strength.get("concept", "").replace("_", " ")
        confidence = strength.get("confidence", 0.5)
        evidence = strength.get("evidence", "")
        
        # Get user's skill level
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Base description templates by concept category
        templates = {
            "opening play": [
                "You demonstrate solid understanding of opening principles.",
                "Your opening play shows good piece development and center control.",
                "You handle the opening phase with confidence and purpose."
            ],
            "middlegame play": [
                "You navigate the middlegame with strategic clarity.",
                "Your middlegame planning shows good positional understanding.",
                "You demonstrate strong piece coordination in complex middlegame positions."
            ],
            "endgame play": [
                "You handle endgame positions with technical precision.",
                "Your endgame technique shows good understanding of key principles.",
                "You convert advantages effectively in the endgame."
            ],
            "tactical": [
                "You demonstrate good tactical awareness and calculation.",
                "Your tactical vision allows you to find strong combinations.",
                "You effectively exploit tactical opportunities when they arise."
            ],
            "strategic": [
                "You show good strategic understanding and planning.",
                "Your strategic decisions are well-founded and consistent.",
                "You demonstrate solid positional judgment."
            ],
            "default": [
                f"You demonstrate good skills in {concept}.",
                f"Your handling of {concept} is a notable strength.",
                f"You show competence and understanding in {concept}."
            ]
        }
        
        # Select template category
        template_category = "default"
        for category in templates:
            if category in concept:
                template_category = category
                break
                
        # Select a random template from the category
        template = random.choice(templates[template_category])
        
        # Add confidence modifier
        if confidence > 0.8:
            confidence_phrase = "consistently "
        elif confidence > 0.6:
            confidence_phrase = "often "
        else:
            confidence_phrase = "sometimes "
            
        # Insert confidence phrase if not already present
        if "consistently" not in template and "often" not in template and "sometimes" not in template:
            words = template.split()
            verb_indices = [i for i, word in enumerate(words) if word in 
                          ["demonstrate", "show", "handle", "navigate", "convert", "exploit"]]
            
            if verb_indices:
                words.insert(verb_indices[0] + 1, confidence_phrase)
                template = " ".join(words)
                
        # Add evidence if available
        if evidence:
            template += f" {evidence}"
            
        # Add skill-level specific advice
        if skill_level == "Beginner":
            template += f" Continue to build on this strength as you develop your overall game."
        elif skill_level == "Intermediate":
            template += f" This strength can be leveraged to improve other areas of your game."
        else:  # Advanced or Expert
            template += f" Even strong areas can be refined further; consider how to apply this strength in more complex positions."
            
        return template
        
    def _generate_weakness_description(self, weakness: Dict[str, Any], 
                                     user_profile: Dict[str, Any]) -> str:
        """
        Generate a description for an identified weakness.
        
        Args:
            weakness: Weakness data
            user_profile: User profile data
            
        Returns:
            Weakness description
        """
        concept = weakness.get("concept", "").replace("_", " ")
        severity = weakness.get("severity", 0.5)
        evidence = weakness.get("evidence", "")
        
        # Get user's skill level
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Base description templates by concept category
        templates = {
            "opening play": [
                "Your opening play could benefit from more attention to core principles.",
                "There are opportunities to improve your opening development and control.",
                "The opening phase shows some challenges in establishing a solid position."
            ],
            "middlegame play": [
                "Your middlegame planning could be more consistent and focused.",
                "There are opportunities to improve strategic decision-making in complex positions.",
                "The middlegame phase reveals some challenges in maintaining initiative."
            ],
            "endgame play": [
                "Your endgame technique could benefit from more precise calculation.",
                "There are opportunities to improve your understanding of key endgame principles.",
                "The endgame phase shows some technical challenges in converting advantages."
            ],
            "tactical": [
                "Your tactical awareness could be sharpened to spot more opportunities.",
                "There are missed tactical opportunities that could have changed the game.",
                "Some tactical patterns and combinations were overlooked during play."
            ],
            "strategic": [
                "Your strategic planning could benefit from more long-term thinking.",
                "There are opportunities to improve positional understanding and evaluation.",
                "Some strategic elements like pawn structure and piece placement need attention."
            ],
            "default": [
                f"Your handling of {concept} could benefit from focused practice.",
                f"There are opportunities to improve your understanding of {concept}.",
                f"Some aspects of {concept} present challenges in your play."
            ]
        }
        
        # Select template category
        template_category = "default"
        for category in templates:
            if category in concept:
                template_category = category
                break
                
        # Select a random template from the category
        template = random.choice(templates[template_category])
        
        # Add severity modifier
        if severity > 0.8:
            severity_phrase = "significant "
        elif severity > 0.6:
            severity_phrase = "noticeable "
        else:
            severity_phrase = "slight "
            
        # Insert severity phrase if appropriate
        if "challenges" in template:
            template = template.replace("challenges", f"{severity_phrase}challenges")
        elif "opportunities" in template:
            template = template.replace("opportunities", f"{severity_phrase}opportunities")
            
        # Add evidence if available
        if evidence:
            template += f" {evidence}"
            
        # Add skill-level specific advice
        if skill_level == "Beginner":
            template += f" This is a common area for improvement at your level and will develop with practice."
        elif skill_level == "Intermediate":
            template += f" Focused practice in this area could significantly improve your overall results."
        else:  # Advanced or Expert
            template += f" At your level, refining this aspect could lead to meaningful rating improvements."
            
        return template
        
    def _generate_improvement_suggestion(self, weakness: Dict[str, Any]) -> str:
        """
        Generate an improvement suggestion for a weakness.
        
        Args:
            weakness: Weakness data
            
        Returns:
            Improvement suggestion
        """
        concept = weakness.get("concept", "").replace("_", " ")
        
        # Suggestion templates by concept
        templates = {
            "opening play": [
                "Study core opening principles: development, center control, and king safety.",
                "Focus on developing a consistent opening repertoire for both white and black.",
                "Analyze master games in your preferred openings to understand key ideas."
            ],
            "middlegame play": [
                "Practice positional evaluation and creating long-term plans.",
                "Study typical middlegame structures and their associated plans.",
                "Analyze the transition from opening to middlegame in master games."
            ],
            "endgame play": [
                "Study essential endgame positions and principles.",
                "Practice technical conversion of advantages in common endgame types.",
                "Focus on king activation and pawn handling in the endgame."
            ],
            "tactical": [
                "Solve tactical puzzles daily to improve pattern recognition.",
                "Practice calculation by analyzing positions without moving pieces.",
                "Study common tactical motifs like forks, pins, and discovered attacks."
            ],
            "strategic": [
                "Study pawn structure principles and their influence on plans.",
                "Practice evaluating positions based on static features.",
                "Analyze games with clear strategic themes from strong players."
            ],
            "calculation": [
                "Practice visualization by solving puzzles without moving pieces.",
                "Develop a systematic approach to calculating variations.",
                "Set up complex positions and practice finding the best move."
            ],
            "time management": [
                "Practice allocating time based on position complexity.",
                "Develop a consistent thought process for each move.",
                "Play practice games with strict time controls to improve decision speed."
            ],
            "pawn structure": [
                "Study common pawn formations and their strategic implications.",
                "Practice identifying and creating pawn breaks.",
                "Analyze games featuring clear pawn structure themes."
            ],
            "piece activity": [
                "Focus on improving piece coordination and harmony.",
                "Practice identifying and utilizing outposts for pieces.",
                "Study games featuring strong piece play and coordination."
            ],
            "king safety": [
                "Study common attacking patterns against the king.",
                "Practice identifying defensive resources in complex positions.",
                "Analyze games featuring successful king attacks and defenses."
            ],
            "default": [
                f"Practice positions focusing specifically on {concept}.",
                f"Study examples of strong {concept} from master games.",
                f"Work with a coach or engine to identify improvements in {concept}."
            ]
        }
        
        # Select template category
        template_category = "default"
        for category in templates:
            if category in concept:
                template_category = category
                break
                
        # Select a random template from the category
        return random.choice(templates[template_category])
        
    def _generate_positive_notes(self, analysis_results: Dict[str, Any], 
                               user_profile: Dict[str, Any]) -> List[str]:
        """
        Generate positive reinforcement notes.
        
        Args:
            analysis_results: Results from game analysis
            user_profile: User profile data
            
        Returns:
            List of positive notes
        """
        positive_notes = []
        
        # Get move analysis
        move_analysis = analysis_results.get("move_analysis", [])
        
        # Check for best moves
        best_moves = [m for m in move_analysis if m.get("classification") == "Best"]
        if best_moves:
            # Pick a random best move to highlight
            best_move = random.choice(best_moves)
            move_str = best_move.get("move", "")
            if move_str:
                positive_notes.append(f"Excellent move {move_str}! This was the engine's top choice.")
                
        # Check for good tactical awareness
        tactical_concepts = ["fork", "pin", "discovered_attack", "check", "winning_capture"]
        tactical_moves = []
        
        for move in move_analysis:
            concepts = move.get("concepts", [])
            for concept_data in concepts:
                concept = concept_data.get("concept", "")
                if concept in tactical_concepts:
                    tactical_moves.append((move, concept))
                    
        if tactical_moves:
            # Pick a random tactical move to highlight
            move, concept = random.choice(tactical_moves)
            move_str = move.get("move", "")
            if move_str:
                positive_notes.append(
                    f"Good tactical awareness with {move_str}, creating a {concept.replace('_', ' ')}."
                )
                
        # Check for good strategic play
        strategic_concepts = ["piece_activity", "king_safety", "pawn_structure", "center_control"]
        strategic_moves = []
        
        for move in move_analysis:
            concepts = move.get("concepts", [])
            for concept_data in concepts:
                concept = concept_data.get("concept", "")
                if concept in strategic_concepts:
                    strategic_moves.append((move, concept))
                    
        if strategic_moves:
            # Pick a random strategic move to highlight
            move, concept = random.choice(strategic_moves)
            move_str = move.get("move", "")
            if move_str:
                positive_notes.append(
                    f"Good strategic decision with {move_str}, improving your {concept.replace('_', ' ')}."
                )
                
        # Add general encouragement based on accuracy
        accuracy = analysis_results.get("overall_accuracy", 0.0)
        
        if accuracy >= 90:
            positive_notes.append("Outstanding accuracy in this game! Your play was nearly perfect.")
        elif accuracy >= 80:
            positive_notes.append("Very strong accuracy overall. You're playing at a high level.")
        elif accuracy >= 70:
            positive_notes.append("Good overall accuracy. Your play shows solid understanding.")
        elif accuracy >= 60:
            positive_notes.append("Reasonable accuracy with room for growth. Keep practicing!")
        else:
            positive_notes.append(
                "While there were challenges in this game, every mistake is a learning opportunity."
            )
            
        # Add note about improvement if we have history
        history = user_profile.get("history", [])
        game_entries = [e for e in history if e.get("type") == "game_analysis"]
        
        if len(game_entries) >= 2:
            # Compare current accuracy with previous game
            prev_accuracy = game_entries[-2].get("accuracy", 0.0)
            if accuracy > prev_accuracy + 5:
                positive_notes.append(
                    f"Great improvement! Your accuracy increased from {prev_accuracy:.1f}% to {accuracy:.1f}%."
                )
                
        return positive_notes
        
    def _generate_detailed_move_feedback(self, move_analysis: List[Dict[str, Any]], 
                                       user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate detailed feedback for specific moves.
        
        Args:
            move_analysis: Analysis of individual moves
            user_profile: User profile data
            
        Returns:
            List of detailed feedback items
        """
        detailed_feedback = []
        
        # Get user's skill level
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Focus on mistakes and blunders
        critical_moves = [m for m in move_analysis 
                        if m.get("classification") in ["Mistake", "Blunder"]]
        
        # If we have too many critical moves, focus on the worst ones
        if len(critical_moves) > 5:
            critical_moves.sort(key=lambda m: m.get("accuracy", 0.0))
            critical_moves = critical_moves[:5]
            
        # Generate feedback for each critical move
        for move in critical_moves:
            move_str = move.get("move", "")
            classification = move.get("classification", "")
            accuracy = move.get("accuracy", 0.0)
            position = move.get("position", "")
            alternative_moves = move.get("alternative_moves", [])
            
            # Get the best alternative move
            best_move = alternative_moves[0].get("move", "") if alternative_moves else ""
            
            # Generate feedback text
            if classification == "Blunder":
                feedback_text = f"The move {move_str} was a significant mistake. "
            else:
                feedback_text = f"The move {move_str} was inaccurate. "
                
            if best_move:
                feedback_text += f"A stronger alternative was {best_move}, "
                
                # Add explanation based on skill level
                if skill_level == "Beginner":
                    feedback_text += "which would have given you a better position by "
                    feedback_text += self._generate_simple_explanation(move, best_move)
                elif skill_level == "Intermediate":
                    feedback_text += "which would have improved your position through "
                    feedback_text += self._generate_intermediate_explanation(move, best_move)
                else:  # Advanced or Expert
                    feedback_text += "which would have maintained your advantage by "
                    feedback_text += self._generate_advanced_explanation(move, best_move)
            else:
                feedback_text += "Consider analyzing this position further to find improvements."
                
            # Create feedback item
            feedback_item = {
                "move": move_str,
                "position": position,
                "classification": classification,
                "accuracy": accuracy,
                "feedback": feedback_text,
                "best_alternative": best_move
            }
            
            detailed_feedback.append(feedback_item)
            
        # If we have no critical moves but some inaccuracies, include those
        if not detailed_feedback:
            inaccuracies = [m for m in move_analysis if m.get("classification") == "Inaccuracy"]
            
            if inaccuracies:
                # Take up to 3 inaccuracies
                for move in inaccuracies[:3]:
                    move_str = move.get("move", "")
                    classification = move.get("classification", "")
                    accuracy = move.get("accuracy", 0.0)
                    position = move.get("position", "")
                    alternative_moves = move.get("alternative_moves", [])
                    
                    # Get the best alternative move
                    best_move = alternative_moves[0].get("move", "") if alternative_moves else ""
                    
                    # Generate feedback text
                    feedback_text = f"The move {move_str} was slightly inaccurate. "
                    
                    if best_move:
                        feedback_text += f"Consider {best_move} as an alternative, which "
                        feedback_text += "would have given you a slightly better position."
                    else:
                        feedback_text += "There may be room for small improvements in this position."
                        
                    # Create feedback item
                    feedback_item = {
                        "move": move_str,
                        "position": position,
                        "classification": classification,
                        "accuracy": accuracy,
                        "feedback": feedback_text,
                        "best_alternative": best_move
                    }
                    
                    detailed_feedback.append(feedback_item)
                    
        # If we still have no feedback items, add a positive note about a good move
        if not detailed_feedback:
            good_moves = [m for m in move_analysis 
                        if m.get("classification") in ["Best", "Good"]]
            
            if good_moves:
                # Pick a random good move
                move = random.choice(good_moves)
                move_str = move.get("move", "")
                classification = move.get("classification", "")
                accuracy = move.get("accuracy", 0.0)
                position = move.get("position", "")
                
                # Generate feedback text
                if classification == "Best":
                    feedback_text = f"Excellent move {move_str}! This was the engine's top choice. "
                    feedback_text += "You found the optimal continuation in this position."
                else:
                    feedback_text = f"Good move {move_str}. This was a strong choice that "
                    feedback_text += "maintained your position effectively."
                    
                # Create feedback item
                feedback_item = {
                    "move": move_str,
                    "position": position,
                    "classification": classification,
                    "accuracy": accuracy,
                    "feedback": feedback_text,
                    "best_alternative": ""
                }
                
                detailed_feedback.append(feedback_item)
                
        return detailed_feedback
        
    def _generate_simple_explanation(self, move: Dict[str, Any], best_move: str) -> str:
        """
        Generate a simple explanation for beginners.
        
        Args:
            move: Move data
            best_move: Best alternative move
            
        Returns:
            Simple explanation
        """
        # Simple explanations focus on basic concepts
        explanations = [
            "developing your pieces more effectively.",
            "better protecting your king.",
            "controlling more space in the center.",
            "avoiding material loss.",
            "creating threats against your opponent's pieces.",
            "improving your pawn structure.",
            "activating your pieces more effectively.",
            "preparing for tactical opportunities."
        ]
        
        return random.choice(explanations)
        
    def _generate_intermediate_explanation(self, move: Dict[str, Any], best_move: str) -> str:
        """
        Generate an intermediate explanation.
        
        Args:
            move: Move data
            best_move: Best alternative move
            
        Returns:
            Intermediate explanation
        """
        # Intermediate explanations focus on more specific concepts
        explanations = [
            "better piece coordination and harmony.",
            "creating long-term pressure on key squares.",
            "maintaining tension in the position.",
            "preparing favorable pawn breaks.",
            "restricting your opponent's piece activity.",
            "creating imbalances that favor your position.",
            "exploiting weaknesses in the opponent's structure.",
            "preparing tactical opportunities while maintaining positional pressure."
        ]
        
        return random.choice(explanations)
        
    def _generate_advanced_explanation(self, move: Dict[str, Any], best_move: str) -> str:
        """
        Generate an advanced explanation.
        
        Args:
            move: Move data
            best_move: Best alternative move
            
        Returns:
            Advanced explanation
        """
        # Advanced explanations focus on subtle concepts
        explanations = [
            "maintaining the initiative while addressing strategic weaknesses.",
            "creating long-term pressure while keeping tactical resources.",
            "exploiting small positional advantages in the pawn structure.",
            "preparing a favorable transformation of the position.",
            "restricting counterplay while advancing your strategic goals.",
            "maintaining flexibility while pursuing concrete advantages.",
            "creating multiple weaknesses that cannot be defended simultaneously.",
            "preserving resources for the upcoming phase of the game."
        ]
        
        return random.choice(explanations)
        
    def _generate_visual_aids(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate visual aids for feedback.
        
        Args:
            analysis_results: Results from game analysis
            
        Returns:
            List of visual aid descriptions
        """
        # In a real implementation, this would generate actual visual aids
        # For now, we'll just return descriptions
        visual_aids = []
        
        # Add visual aid for critical mistakes
        critical_moves = []
        for move in analysis_results.get("move_analysis", []):
            if move.get("classification") in ["Mistake", "Blunder"]:
                critical_moves.append(move)
                
        if critical_moves:
            # Sort by accuracy (ascending)
            critical_moves.sort(key=lambda m: m.get("accuracy", 0.0))
            
            # Take the worst mistake
            worst_move = critical_moves[0]
            position = worst_move.get("position", "")
            move_str = worst_move.get("move", "")
            
            if position and move_str:
                visual_aids.append({
                    "type": "position_diagram",
                    "title": f"Critical Position: Before {move_str}",
                    "description": "This position contains a critical mistake. The played move is highlighted in red, while the recommended move is highlighted in green.",
                    "position": position,
                    "played_move": move_str,
                    "recommended_move": worst_move.get("alternative_moves", [{}])[0].get("move", "")
                })
                
        # Add visual aid for strength area
        strengths = analysis_results.get("strengths_identified", [])
        if strengths:
            # Take the highest confidence strength
            strengths.sort(key=lambda s: s.get("confidence", 0.0), reverse=True)
            top_strength = strengths[0]
            
            visual_aids.append({
                "type": "concept_diagram",
                "title": f"Strength: {top_strength.get('concept', '').replace('_', ' ').title()}",
                "description": f"This diagram illustrates your strength in {top_strength.get('concept', '').replace('_', ' ')}. The highlighted elements show good decision-making in this area.",
                "concept": top_strength.get("concept", "")
            })
            
        # Add visual aid for weakness area
        weaknesses = analysis_results.get("weaknesses_identified", [])
        if weaknesses:
            # Take the highest severity weakness
            weaknesses.sort(key=lambda w: w.get("severity", 0.0), reverse=True)
            top_weakness = weaknesses[0]
            
            visual_aids.append({
                "type": "concept_diagram",
                "title": f"Improvement Area: {top_weakness.get('concept', '').replace('_', ' ').title()}",
                "description": f"This diagram illustrates an area for improvement in {top_weakness.get('concept', '').replace('_', ' ')}. The highlighted elements show opportunities for better decision-making.",
                "concept": top_weakness.get("concept", "")
            })
            
        # Add accuracy chart
        visual_aids.append({
            "type": "accuracy_chart",
            "title": "Move Accuracy Chart",
            "description": "This chart shows your move accuracy throughout the game. Higher values indicate better moves.",
            "data": [m.get("accuracy", 0.0) for m in analysis_results.get("move_analysis", [])]
        })
        
        return visual_aids
        
    def generate_exercise_feedback(self, user_id: str, exercise_id: str, 
                                 result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate feedback for a completed exercise.
        
        Args:
            user_id: ID of the user who completed the exercise
            exercise_id: ID of the completed exercise
            result: Results from the exercise attempt
            
        Returns:
            Exercise feedback data
        """
        try:
            # Ensure user profile manager is available
            if not self.user_profile_manager:
                raise ValueError("User Profile Manager not available for feedback generation")
                
            # Get user profile
            user_profile = self.user_profile_manager.get_profile(user_id)
            if not user_profile:
                raise ValueError(f"User profile not found for ID: {user_id}")
                
            # Initialize feedback
            feedback = {
                "id": f"feedback_{random.randint(10000, 99999)}",
                "user_id": user_id,
                "exercise_id": exercise_id,
                "type": "exercise_feedback",
                "success": result.get("success", False),
                "attempts": result.get("attempts", 1),
                "time_taken": result.get("time_taken", 0),
                "summary": "",
                "detailed_feedback": "",
                "concepts": result.get("concepts", []),
                "next_steps": []
            }
            
            # Generate summary based on success
            if feedback["success"]:
                feedback["summary"] = self._generate_success_summary(result, user_profile)
            else:
                feedback["summary"] = self._generate_failure_summary(result, user_profile)
                
            # Generate detailed feedback
            feedback["detailed_feedback"] = self._generate_exercise_detailed_feedback(result)
            
            # Generate next steps
            feedback["next_steps"] = self._generate_exercise_next_steps(result, user_profile)
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error generating exercise feedback: {str(e)}")
            return {
                "error": str(e),
                "user_id": user_id,
                "exercise_id": exercise_id
            }
            
    def _generate_success_summary(self, result: Dict[str, Any], 
                                user_profile: Dict[str, Any]) -> str:
        """
        Generate a summary for a successful exercise attempt.
        
        Args:
            result: Exercise result data
            user_profile: User profile data
            
        Returns:
            Success summary
        """
        # Get user name and skill level
        name = user_profile.get("name", "Player")
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Get exercise data
        attempts = result.get("attempts", 1)
        time_taken = result.get("time_taken", 0)
        exercise_type = result.get("type", "tactical")
        difficulty = result.get("difficulty", "medium")
        concepts = result.get("concepts", [])
        
        # Generate summary text
        summary = f"Well done, {name}! "
        
        if attempts == 1:
            summary += "You solved this exercise correctly on your first attempt. "
        else:
            summary += f"You solved this exercise correctly after {attempts} attempts. "
            
        # Add time comment if available
        if time_taken > 0:
            if time_taken < 30:
                summary += "You solved it very quickly! "
            elif time_taken < 60:
                summary += "You solved it in good time. "
            elif time_taken < 120:
                summary += "You took a reasonable amount of time to solve it. "
            else:
                summary += "You took your time to find the correct solution. "
                
        # Add concept comment if available
        if concepts:
            concept_str = ", ".join(c.replace("_", " ") for c in concepts[:2])
            summary += f"This exercise focused on {concept_str}. "
            
        # Add skill level specific comment
        if skill_level == "Beginner":
            summary += "Each successful exercise builds your pattern recognition and calculation skills. "
            summary += "Keep practicing regularly to reinforce these patterns."
        elif skill_level == "Intermediate":
            summary += "Your consistent practice is paying off in improved tactical vision. "
            summary += "Try to apply these patterns in your games."
        else:  # Advanced or Expert
            summary += "Even at your level, regular tactical practice maintains sharp calculation. "
            summary += "Focus on the subtleties of the position that make this combination work."
            
        return summary
        
    def _generate_failure_summary(self, result: Dict[str, Any], 
                                user_profile: Dict[str, Any]) -> str:
        """
        Generate a summary for an unsuccessful exercise attempt.
        
        Args:
            result: Exercise result data
            user_profile: User profile data
            
        Returns:
            Failure summary
        """
        # Get user name and skill level
        name = user_profile.get("name", "Player")
        skill_level = user_profile.get("skill_level", "Beginner")
        
        # Get exercise data
        attempts = result.get("attempts", 1)
        exercise_type = result.get("type", "tactical")
        difficulty = result.get("difficulty", "medium")
        concepts = result.get("concepts", [])
        
        # Generate summary text
        summary = f"Good effort, {name}. "
        summary += "This exercise presented a challenge, but each attempt is a learning opportunity. "
        
        # Add difficulty comment
        if difficulty == "hard" or difficulty == "expert":
            summary += "This was a particularly challenging exercise. "
        
        # Add concept comment if available
        if concepts:
            concept_str = ", ".join(c.replace("_", " ") for c in concepts[:2])
            summary += f"This exercise focused on {concept_str}. "
            
        # Add skill level specific comment
        if skill_level == "Beginner":
            summary += "Don't be discouraged by difficult puzzles. "
            summary += "The solution will help you recognize similar patterns in the future."
        elif skill_level == "Intermediate":
            summary += "Challenging exercises help identify areas for improvement. "
            summary += "Study the solution carefully to understand the key ideas."
        else:  # Advanced or Expert
            summary += "Even strong players encounter challenging positions. "
            summary += "Analyzing why the solution wasn't found can lead to important insights."
            
        return summary
        
    def _generate_exercise_detailed_feedback(self, result: Dict[str, Any]) -> str:
        """
        Generate detailed feedback for an exercise attempt.
        
        Args:
            result: Exercise result data
            
        Returns:
            Detailed feedback
        """
        # Get exercise data
        success = result.get("success", False)
        solution = result.get("solution", "")
        user_moves = result.get("user_moves", [])
        key_positions = result.get("key_positions", [])
        
        # Generate detailed feedback
        if success:
            feedback = "Your solution was correct. "
            
            if solution:
                feedback += f"The main line is: {solution}. "
                
            if key_positions:
                feedback += "The key ideas in this exercise include: "
                for pos in key_positions:
                    feedback += f"{pos.get('description', '')}. "
                    
        else:
            feedback = "Your solution wasn't optimal. "
            
            if user_moves and solution:
                feedback += f"You played {', '.join(user_moves)}, "
                feedback += f"but the correct solution is {solution}. "
                
            if key_positions:
                feedback += "The key ideas you should focus on are: "
                for pos in key_positions:
                    feedback += f"{pos.get('description', '')}. "
                    
        # Add general advice
        feedback += "\n\nWhen solving similar exercises, remember to: "
        feedback += "1) Check all forcing moves (checks, captures, threats), "
        feedback += "2) Consider the opponent's responses, and "
        feedback += "3) Calculate the full sequence before making your decision."
        
        return feedback
        
    def _generate_exercise_next_steps(self, result: Dict[str, Any], 
                                    user_profile: Dict[str, Any]) -> List[str]:
        """
        Generate next steps after an exercise attempt.
        
        Args:
            result: Exercise result data
            user_profile: User profile data
            
        Returns:
            List of next steps
        """
        next_steps = []
        
        # Get exercise data
        success = result.get("success", False)
        exercise_type = result.get("type", "tactical")
        difficulty = result.get("difficulty", "medium")
        concepts = result.get("concepts", [])
        
        # Add concept-specific next steps
        for concept in concepts:
            if concept == "fork":
                next_steps.append("Practice more fork exercises to reinforce this tactical pattern.")
            elif concept == "pin":
                next_steps.append("Study more pin motifs to deepen your understanding of this tactic.")
            elif concept == "discovered_attack":
                next_steps.append("Focus on discovered attack exercises to improve recognition of this pattern.")
            elif concept == "pawn_structure":
                next_steps.append("Study pawn structure principles to better understand positional play.")
            elif concept == "king_safety":
                next_steps.append("Practice king safety exercises to improve defensive skills.")
            elif concept == "piece_activity":
                next_steps.append("Work on piece coordination exercises to enhance your positional understanding.")
                
        # Add difficulty-based next steps
        if success:
            if difficulty in ["easy", "medium"]:
                next_steps.append(f"Try more challenging {exercise_type} exercises to continue improving.")
            else:
                next_steps.append(f"Continue practicing difficult {exercise_type} exercises to maintain your skills.")
        else:
            if difficulty in ["hard", "expert"]:
                next_steps.append(f"Try some easier {exercise_type} exercises to build confidence in this area.")
            else:
                next_steps.append(f"Review the solution carefully and try similar {exercise_type} exercises.")
                
        # Add general next steps
        next_steps.append("Apply the patterns from this exercise in your games.")
        next_steps.append("Review your recent games to find similar positions or opportunities.")
        
        return next_steps
        
    def shutdown(self) -> bool:
        """
        Perform a clean shutdown.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            logger.info("Feedback Generator shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during Feedback Generator shutdown: {str(e)}")
            return False
