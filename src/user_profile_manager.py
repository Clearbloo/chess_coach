"""
User Profile Manager Module for Chess Coach Software

This module handles user data, preferences, and progress tracking.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UserProfileManager:
    """
    Manages user profiles, preferences, and progress tracking.
    """
    
    def __init__(self, data_dir: str = "./data/profiles"):
        """
        Initialize the User Profile Manager.
        
        Args:
            data_dir: Directory to store user profile data
        """
        self.data_dir = data_dir
        self.profiles = {}  # Cache of loaded profiles
        self.initialized = False
        logger.info("User Profile Manager created")
        
    def initialize(self) -> bool:
        """
        Initialize the User Profile Manager.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Create data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)
            
            # Load existing profiles into cache
            self._load_profiles()
            
            self.initialized = True
            logger.info(f"User Profile Manager initialized with data directory: {self.data_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing User Profile Manager: {str(e)}")
            return False
            
    def _load_profiles(self) -> None:
        """Load all existing user profiles into memory cache."""
        try:
            if not os.path.exists(self.data_dir):
                return
                
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    user_id = filename[:-5]  # Remove .json extension
                    file_path = os.path.join(self.data_dir, filename)
                    
                    with open(file_path, 'r') as f:
                        profile_data = json.load(f)
                        self.profiles[user_id] = profile_data
                        
            logger.info(f"Loaded {len(self.profiles)} user profiles")
            
        except Exception as e:
            logger.error(f"Error loading profiles: {str(e)}")
            
    def _save_profile(self, user_id: str) -> bool:
        """
        Save a user profile to disk.
        
        Args:
            user_id: ID of the user profile to save
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            if user_id not in self.profiles:
                logger.error(f"Cannot save non-existent profile for user: {user_id}")
                return False
                
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            
            with open(file_path, 'w') as f:
                json.dump(self.profiles[user_id], f, indent=2)
                
            logger.info(f"Saved profile for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving profile for user {user_id}: {str(e)}")
            return False
            
    def create_profile(self, name: str, initial_data: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new user profile.
        
        Args:
            name: User's name
            initial_data: Optional initial profile data
            
        Returns:
            User ID of the created profile
        """
        try:
            # Generate a unique user ID
            user_id = str(uuid.uuid4())
            
            # Create default profile structure
            profile = {
                "id": user_id,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "skill_level": "Beginner",
                "preferences": {
                    "learning_style": "Visual",
                    "session_duration": 30,  # minutes
                    "focus_areas": []
                },
                "statistics": {
                    "games_played": 0,
                    "puzzles_solved": 0,
                    "average_accuracy": 0.0,
                    "strength_areas": [],
                    "weakness_areas": []
                },
                "history": []
            }
            
            # Update with any provided initial data
            if initial_data:
                self._deep_update(profile, initial_data)
                
            # Save to cache and disk
            self.profiles[user_id] = profile
            self._save_profile(user_id)
            
            logger.info(f"Created new profile for user: {name} with ID: {user_id}")
            return user_id
            
        except Exception as e:
            logger.error(f"Error creating profile for user {name}: {str(e)}")
            return ""
            
    def _deep_update(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """
        Recursively update a nested dictionary.
        
        Args:
            target: Target dictionary to update
            source: Source dictionary with updates
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_update(target[key], value)
            else:
                target[key] = value
                
    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a user profile.
        
        Args:
            user_id: ID of the user profile to retrieve
            
        Returns:
            User profile data or empty dict if not found
        """
        try:
            # Check if profile is in cache
            if user_id in self.profiles:
                return self.profiles[user_id]
                
            # Try to load from disk
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    profile_data = json.load(f)
                    self.profiles[user_id] = profile_data
                    return profile_data
                    
            logger.warning(f"Profile not found for user ID: {user_id}")
            return {}
            
        except Exception as e:
            logger.error(f"Error retrieving profile for user {user_id}: {str(e)}")
            return {}
            
    def update_profile(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a user profile.
        
        Args:
            user_id: ID of the user profile to update
            updates: Dictionary of profile updates
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            profile = self.get_profile(user_id)
            if not profile:
                logger.error(f"Cannot update non-existent profile for user: {user_id}")
                return False
                
            # Update the profile
            self._deep_update(profile, updates)
            
            # Update the timestamp
            profile["updated_at"] = datetime.now().isoformat()
            
            # Save changes
            self.profiles[user_id] = profile
            return self._save_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {str(e)}")
            return False
            
    def update_with_analysis(self, user_id: str, analysis_results: Dict[str, Any]) -> bool:
        """
        Update user profile with game analysis results.
        
        Args:
            user_id: ID of the user profile to update
            analysis_results: Results from game analysis
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            profile = self.get_profile(user_id)
            if not profile:
                logger.error(f"Cannot update non-existent profile for user: {user_id}")
                return False
                
            # Extract relevant data from analysis results
            stats = profile["statistics"]
            
            # Update games played count
            stats["games_played"] += 1
            
            # Update average accuracy
            if "overall_accuracy" in analysis_results:
                new_accuracy = analysis_results["overall_accuracy"]
                old_accuracy = stats["average_accuracy"]
                games_played = stats["games_played"]
                
                # Weighted average calculation
                if games_played > 1:
                    stats["average_accuracy"] = (old_accuracy * (games_played - 1) + new_accuracy) / games_played
                else:
                    stats["average_accuracy"] = new_accuracy
                    
            # Update strengths and weaknesses
            if "strengths_identified" in analysis_results:
                self._update_strengths(stats, analysis_results["strengths_identified"])
                
            if "weaknesses_identified" in analysis_results:
                self._update_weaknesses(stats, analysis_results["weaknesses_identified"])
                
            # Add to history
            timestamp = datetime.now().isoformat()
            history_entry = {
                "timestamp": timestamp,
                "type": "game_analysis",
                "game_id": analysis_results.get("game_id", "unknown"),
                "accuracy": analysis_results.get("overall_accuracy", 0.0),
                "strengths": [s["concept"] for s in analysis_results.get("strengths_identified", [])],
                "weaknesses": [w["concept"] for w in analysis_results.get("weaknesses_identified", [])]
            }
            
            profile["history"].append(history_entry)
            
            # Save changes
            self.profiles[user_id] = profile
            return self._save_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error updating profile with analysis for user {user_id}: {str(e)}")
            return False
            
    def _update_strengths(self, stats: Dict[str, Any], strengths: List[Dict[str, Any]]) -> None:
        """
        Update strength areas in user statistics.
        
        Args:
            stats: User statistics dictionary
            strengths: List of identified strengths
        """
        # Get current strengths
        current_strengths = {s["concept"]: s for s in stats["strength_areas"]}
        
        # Update with new strengths
        for strength in strengths:
            concept = strength["concept"]
            if concept in current_strengths:
                # Update existing strength
                current = current_strengths[concept]
                current["confidence"] = min(1.0, current["confidence"] + 0.1)
                current["examples"].append(strength.get("example", ""))
                current["last_observed"] = datetime.now().isoformat()
            else:
                # Add new strength
                current_strengths[concept] = {
                    "concept": concept,
                    "confidence": 0.6,  # Initial confidence
                    "examples": [strength.get("example", "")],
                    "first_observed": datetime.now().isoformat(),
                    "last_observed": datetime.now().isoformat()
                }
                
        # Update the statistics
        stats["strength_areas"] = list(current_strengths.values())
        
    def _update_weaknesses(self, stats: Dict[str, Any], weaknesses: List[Dict[str, Any]]) -> None:
        """
        Update weakness areas in user statistics.
        
        Args:
            stats: User statistics dictionary
            weaknesses: List of identified weaknesses
        """
        # Get current weaknesses
        current_weaknesses = {w["concept"]: w for w in stats["weakness_areas"]}
        
        # Update with new weaknesses
        for weakness in weaknesses:
            concept = weakness["concept"]
            if concept in current_weaknesses:
                # Update existing weakness
                current = current_weaknesses[concept]
                current["severity"] = (current["severity"] * current["occurrences"] + 
                                     weakness.get("severity", 0.5)) / (current["occurrences"] + 1)
                current["occurrences"] += 1
                current["examples"].append(weakness.get("example", ""))
                current["last_observed"] = datetime.now().isoformat()
            else:
                # Add new weakness
                current_weaknesses[concept] = {
                    "concept": concept,
                    "severity": weakness.get("severity", 0.5),
                    "occurrences": 1,
                    "examples": [weakness.get("example", "")],
                    "first_observed": datetime.now().isoformat(),
                    "last_observed": datetime.now().isoformat()
                }
                
        # Update the statistics
        stats["weakness_areas"] = list(current_weaknesses.values())
        
    def update_with_exercise_result(self, user_id: str, exercise_id: str, 
                                   result: Dict[str, Any]) -> bool:
        """
        Update user profile with exercise completion results.
        
        Args:
            user_id: ID of the user profile to update
            exercise_id: ID of the completed exercise
            result: Results from the exercise attempt
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            profile = self.get_profile(user_id)
            if not profile:
                logger.error(f"Cannot update non-existent profile for user: {user_id}")
                return False
                
            # Extract relevant data from result
            stats = profile["statistics"]
            
            # Update puzzles solved count
            stats["puzzles_solved"] += 1
            
            # Add to history
            timestamp = datetime.now().isoformat()
            history_entry = {
                "timestamp": timestamp,
                "type": "exercise_completion",
                "exercise_id": exercise_id,
                "success": result.get("success", False),
                "attempts": result.get("attempts", 1),
                "time_taken": result.get("time_taken", 0),
                "concepts": result.get("concepts", [])
            }
            
            profile["history"].append(history_entry)
            
            # If the exercise targeted a specific weakness, update that weakness
            if "target_weakness" in result and result.get("success", False):
                weakness_concept = result["target_weakness"]
                self._update_weakness_after_success(stats, weakness_concept)
                
            # Save changes
            self.profiles[user_id] = profile
            return self._save_profile(user_id)
            
        except Exception as e:
            logger.error(f"Error updating profile with exercise result for user {user_id}: {str(e)}")
            return False
            
    def _update_weakness_after_success(self, stats: Dict[str, Any], concept: str) -> None:
        """
        Update a weakness after successful exercise completion.
        
        Args:
            stats: User statistics dictionary
            concept: The weakness concept that was targeted
        """
        for i, weakness in enumerate(stats["weakness_areas"]):
            if weakness["concept"] == concept:
                # Reduce severity after successful practice
                weakness["severity"] = max(0.1, weakness["severity"] - 0.1)
                
                # If severity is low enough, consider it a strength
                if weakness["severity"] < 0.2:
                    # Remove from weaknesses
                    stats["weakness_areas"].pop(i)
                    
                    # Check if it's already in strengths
                    strength_concepts = [s["concept"] for s in stats["strength_areas"]]
                    if concept not in strength_concepts:
                        # Add to strengths
                        stats["strength_areas"].append({
                            "concept": concept,
                            "confidence": 0.5,  # Initial confidence
                            "examples": [],
                            "first_observed": datetime.now().isoformat(),
                            "last_observed": datetime.now().isoformat()
                        })
                break
                
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Args:
            user_id: ID of the user profile
            
        Returns:
            User statistics or empty dict if not found
        """
        try:
            profile = self.get_profile(user_id)
            if not profile:
                logger.error(f"Cannot get statistics for non-existent profile: {user_id}")
                return {}
                
            return profile.get("statistics", {})
            
        except Exception as e:
            logger.error(f"Error getting statistics for user {user_id}: {str(e)}")
            return {}
            
    def get_progress_report(self, user_id: str, 
                           time_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a progress report for a user.
        
        Args:
            user_id: ID of the user profile
            time_period: Optional time period for the report (e.g., "week", "month")
            
        Returns:
            Progress report data
        """
        try:
            profile = self.get_profile(user_id)
            if not profile:
                logger.error(f"Cannot generate report for non-existent profile: {user_id}")
                return {}
                
            # Filter history based on time period
            history = profile.get("history", [])
            filtered_history = self._filter_history_by_time(history, time_period)
            
            # Calculate progress metrics
            games_played = sum(1 for entry in filtered_history if entry["type"] == "game_analysis")
            puzzles_solved = sum(1 for entry in filtered_history if entry["type"] == "exercise_completion")
            
            # Calculate accuracy trend
            accuracy_entries = [entry.get("accuracy", 0) for entry in filtered_history 
                              if entry["type"] == "game_analysis" and "accuracy" in entry]
            
            accuracy_trend = 0
            if len(accuracy_entries) >= 2:
                first_half = accuracy_entries[:len(accuracy_entries)//2]
                second_half = accuracy_entries[len(accuracy_entries)//2:]
                first_avg = sum(first_half) / len(first_half) if first_half else 0
                second_avg = sum(second_half) / len(second_half) if second_half else 0
                accuracy_trend = second_avg - first_avg
                
            # Get current strengths and weaknesses
            strengths = profile.get("statistics", {}).get("strength_areas", [])
            weaknesses = profile.get("statistics", {}).get("weakness_areas", [])
            
            # Generate report
            report = {
                "user_id": user_id,
                "name": profile.get("name", ""),
                "time_period": time_period or "all",
                "generated_at": datetime.now().isoformat(),
                "metrics": {
                    "games_played": games_played,
                    "puzzles_solved": puzzles_solved,
                    "current_accuracy": profile.get("statistics", {}).get("average_accuracy", 0),
                    "accuracy_trend": accuracy_trend
                },
                "strengths": strengths,
                "weaknesses": weaknesses,
                "recommendations": self._generate_recommendations(strengths, weaknesses)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating progress report for user {user_id}: {str(e)}")
            return {}
            
    def _filter_history_by_time(self, history: List[Dict[str, Any]], 
                              time_period: Optional[str]) -> List[Dict[str, Any]]:
        """
        Filter history entries by time period.
        
        Args:
            history: List of history entries
            time_period: Time period to filter by
            
        Returns:
            Filtered history list
        """
        if not time_period:
            return history
            
        now = datetime.now()
        cutoff = None
        
        if time_period == "day":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "week":
            cutoff = now.replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff = cutoff.replace(day=cutoff.day - cutoff.weekday())
        elif time_period == "month":
            cutoff = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        elif time_period == "year":
            cutoff = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            return history
            
        return [entry for entry in history if datetime.fromisoformat(entry["timestamp"]) >= cutoff]
        
    def _generate_recommendations(self, strengths: List[Dict[str, Any]], 
                                weaknesses: List[Dict[str, Any]]) -> List[str]:
        """
        Generate personalized recommendations based on strengths and weaknesses.
        
        Args:
            strengths: List of user strengths
            weaknesses: List of user weaknesses
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Focus on top weaknesses
        sorted_weaknesses = sorted(weaknesses, key=lambda w: w.get("severity", 0), reverse=True)
        for i, weakness in enumerate(sorted_weaknesses[:3]):
            concept = weakness.get("concept", "")
            if concept:
                recommendations.append(f"Practice {concept} to improve your weakest area")
                
        # Leverage strengths
        for strength in strengths[:2]:
            concept = strength.get("concept", "")
            if concept:
                recommendations.append(f"Continue to build on your strength in {concept}")
                
        # General recommendations
        recommendations.append("Analyze your games regularly to track improvement")
        recommendations.append("Practice tactical puzzles daily to improve pattern recognition")
        
        return recommendations
        
    def delete_profile(self, user_id: str) -> bool:
        """
        Delete a user profile.
        
        Args:
            user_id: ID of the user profile to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            # Remove from cache
            if user_id in self.profiles:
                del self.profiles[user_id]
                
            # Remove from disk
            file_path = os.path.join(self.data_dir, f"{user_id}.json")
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Deleted profile for user: {user_id}")
                return True
            else:
                logger.warning(f"Profile file not found for user: {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting profile for user {user_id}: {str(e)}")
            return False
            
    def shutdown(self) -> bool:
        """
        Perform a clean shutdown, saving any unsaved profiles.
        
        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            # Save all profiles in cache
            for user_id in self.profiles:
                self._save_profile(user_id)
                
            logger.info("User Profile Manager shut down successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error during User Profile Manager shutdown: {str(e)}")
            return False
