"""
Core Engine Module for Chess Coach Software

This module serves as the central coordinator for all other components,
managing the application flow and routing data between modules.
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CoreEngine:
    """
    Core Engine class that coordinates all system components and manages application flow.
    """
    
    def __init__(self):
        """Initialize the Core Engine and its component references."""
        self.components = {}
        self.initialized = False
        logger.info("Core Engine initialized")
        
    def register_component(self, name: str, component: Any) -> None:
        """
        Register a component with the Core Engine.
        
        Args:
            name: Unique identifier for the component
            component: The component instance to register
        """
        self.components[name] = component
        logger.info(f"Component '{name}' registered with Core Engine")
        
    def get_component(self, name: str) -> Any:
        """
        Retrieve a registered component by name.
        
        Args:
            name: The name of the component to retrieve
            
        Returns:
            The requested component instance
            
        Raises:
            KeyError: If the component is not registered
        """
        if name not in self.components:
            raise KeyError(f"Component '{name}' not registered with Core Engine")
        return self.components[name]
        
    def initialize_system(self) -> bool:
        """
        Initialize all registered components in the correct order.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Define initialization order
            init_order = [
                "data_storage",
                "chess_engine",
                "user_profile",
                "game_analysis",
                "feedback_generator",
                "practice_module",
                "user_interface"
            ]
            
            # Initialize components in order
            for component_name in init_order:
                if component_name in self.components:
                    component = self.components[component_name]
                    if hasattr(component, 'initialize'):
                        logger.info(f"Initializing component: {component_name}")
                        component.initialize()
            
            self.initialized = True
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during system initialization: {str(e)}")
            self.initialized = False
            return False
            
    def analyze_game(self, game_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """
        Coordinate the game analysis workflow.
        
        Args:
            game_data: The game data to analyze
            user_id: The ID of the user who played the game
            
        Returns:
            Analysis results including strengths, weaknesses, and feedback
        """
        try:
            # Validate the game data
            chess_engine = self.get_component("chess_engine")
            valid_game = chess_engine.validate_game(game_data)
            
            if not valid_game:
                return {"error": "Invalid game data provided"}
            
            # Analyze the game
            game_analysis = self.get_component("game_analysis")
            analysis_results = game_analysis.analyze_game(game_data)
            
            # Update user profile with analysis results
            user_profile = self.get_component("user_profile")
            user_profile.update_with_analysis(user_id, analysis_results)
            
            # Generate feedback based on analysis
            feedback_generator = self.get_component("feedback_generator")
            feedback = feedback_generator.generate_feedback(analysis_results, user_id)
            
            # Store analysis results and feedback
            data_storage = self.get_component("data_storage")
            data_storage.store_analysis(analysis_results, user_id)
            data_storage.store_feedback(feedback, user_id)
            
            # Return combined results
            return {
                "analysis": analysis_results,
                "feedback": feedback
            }
            
        except Exception as e:
            logger.error(f"Error during game analysis workflow: {str(e)}")
            return {"error": str(e)}
            
    def generate_practice(self, user_id: str, focus_areas: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Coordinate the practice generation workflow.
        
        Args:
            user_id: The ID of the user to generate practice for
            focus_areas: Optional list of specific areas to focus on
            
        Returns:
            Generated practice exercises
        """
        try:
            # Get user profile to determine weaknesses
            user_profile = self.get_component("user_profile")
            profile_data = user_profile.get_profile(user_id)
            
            # Generate practice exercises
            practice_module = self.get_component("practice_module")
            exercises = practice_module.generate_exercises(profile_data, focus_areas)
            
            # Store generated exercises
            data_storage = self.get_component("data_storage")
            data_storage.store_exercises(exercises, user_id)
            
            return {
                "exercises": exercises,
                "count": len(exercises)
            }
            
        except Exception as e:
            logger.error(f"Error during practice generation workflow: {str(e)}")
            return {"error": str(e)}
            
    def handle_exercise_completion(self, user_id: str, exercise_id: str, 
                                  result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the results of a completed practice exercise.
        
        Args:
            user_id: The ID of the user who completed the exercise
            exercise_id: The ID of the completed exercise
            result: The results of the exercise attempt
            
        Returns:
            Feedback and updated user statistics
        """
        try:
            # Update exercise attempt history
            data_storage = self.get_component("data_storage")
            data_storage.store_exercise_attempt(user_id, exercise_id, result)
            
            # Update user profile with exercise results
            user_profile = self.get_component("user_profile")
            user_profile.update_with_exercise_result(user_id, exercise_id, result)
            
            # Generate feedback for the exercise attempt
            feedback_generator = self.get_component("feedback_generator")
            feedback = feedback_generator.generate_exercise_feedback(user_id, exercise_id, result)
            
            # Store feedback
            data_storage.store_feedback(feedback, user_id)
            
            # Get updated user statistics
            stats = user_profile.get_statistics(user_id)
            
            return {
                "feedback": feedback,
                "statistics": stats
            }
            
        except Exception as e:
            logger.error(f"Error processing exercise completion: {str(e)}")
            return {"error": str(e)}
            
    def shutdown(self) -> bool:
        """
        Perform a clean shutdown of all components.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            # Shutdown components in reverse initialization order
            shutdown_order = [
                "user_interface",
                "practice_module",
                "feedback_generator",
                "game_analysis",
                "user_profile",
                "chess_engine",
                "data_storage"
            ]
            
            for component_name in shutdown_order:
                if component_name in self.components:
                    component = self.components[component_name]
                    if hasattr(component, 'shutdown'):
                        logger.info(f"Shutting down component: {component_name}")
                        component.shutdown()
            
            logger.info("All components shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during system shutdown: {str(e)}")
            return False
