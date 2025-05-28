"""
Data Storage Module for Chess Coach Software

This module manages persistent storage of user data, games, and analysis results.
"""

import json
import logging
import os
import shutil
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataStorage:
    """
    Manages persistent data storage for the Chess Coach application.
    """

    def __init__(self, data_dir: str = "./data"):
        """
        Initialize the Data Storage module.

        Args:
            data_dir: Base directory for data storage
        """
        self.data_dir = data_dir
        self.initialized = False
        logger.info("Data Storage module created")

    def initialize(self) -> bool:
        """
        Initialize the Data Storage module.

        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Create main data directory if it doesn't exist
            os.makedirs(self.data_dir, exist_ok=True)

            # Create subdirectories for different data types
            subdirs = ["profiles", "games", "analysis", "feedback", "exercises"]
            for subdir in subdirs:
                os.makedirs(os.path.join(self.data_dir, subdir), exist_ok=True)

            self.initialized = True
            logger.info(
                f"Data Storage initialized with data directory: {self.data_dir}"
            )
            return True

        except Exception as e:
            logger.error(f"Error initializing Data Storage: {str(e)}")
            return False

    def store_profile(self, profile_data: Dict[str, Any]) -> bool:
        """
        Store a user profile.

        Args:
            profile_data: User profile data to store

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Ensure profile has an ID
            if "id" not in profile_data:
                logger.error("Cannot store profile without ID")
                return False

            user_id = profile_data["id"]
            file_path = os.path.join(self.data_dir, "profiles", f"{user_id}.json")

            with open(file_path, "w") as f:
                json.dump(profile_data, f, indent=2)

            logger.info(f"Stored profile for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing profile: {str(e)}")
            return False

    def get_profile(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a user profile.

        Args:
            user_id: ID of the user profile to retrieve

        Returns:
            User profile data or empty dict if not found
        """
        try:
            file_path = os.path.join(self.data_dir, "profiles", f"{user_id}.json")

            if not os.path.exists(file_path):
                logger.warning(f"Profile not found for user: {user_id}")
                return {}

            with open(file_path, "r") as f:
                profile_data = json.load(f)

            logger.info(f"Retrieved profile for user: {user_id}")
            return profile_data

        except Exception as e:
            logger.error(f"Error retrieving profile: {str(e)}")
            return {}

    def delete_profile(self, user_id: str) -> bool:
        """
        Delete a user profile.

        Args:
            user_id: ID of the user profile to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            file_path = os.path.join(self.data_dir, "profiles", f"{user_id}.json")

            if not os.path.exists(file_path):
                logger.warning(f"Profile not found for user: {user_id}")
                return False

            os.remove(file_path)
            logger.info(f"Deleted profile for user: {user_id}")

            # Also delete associated data
            self._delete_user_data(user_id)

            return True

        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            return False

    def _delete_user_data(self, user_id: str) -> None:
        """
        Delete all data associated with a user.

        Args:
            user_id: ID of the user whose data to delete
        """
        try:
            # Delete games
            games_dir = os.path.join(self.data_dir, "games")
            for filename in os.listdir(games_dir):
                if filename.startswith(f"{user_id}_"):
                    os.remove(os.path.join(games_dir, filename))

            # Delete analysis
            analysis_dir = os.path.join(self.data_dir, "analysis")
            for filename in os.listdir(analysis_dir):
                if filename.startswith(f"{user_id}_"):
                    os.remove(os.path.join(analysis_dir, filename))

            # Delete feedback
            feedback_dir = os.path.join(self.data_dir, "feedback")
            for filename in os.listdir(feedback_dir):
                if filename.startswith(f"{user_id}_"):
                    os.remove(os.path.join(feedback_dir, filename))

            # Delete exercises
            exercises_dir = os.path.join(self.data_dir, "exercises")
            for filename in os.listdir(exercises_dir):
                if filename.startswith(f"{user_id}_"):
                    os.remove(os.path.join(exercises_dir, filename))

            logger.info(f"Deleted all data for user: {user_id}")

        except Exception as e:
            logger.error(f"Error deleting user data: {str(e)}")

    def store_game(self, game_data: Dict[str, Any], user_id: str) -> bool:
        """
        Store a chess game.

        Args:
            game_data: Game data to store
            user_id: ID of the user who played the game

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Ensure game has an ID
            if "id" not in game_data:
                logger.error("Cannot store game without ID")
                return False

            game_id = game_data["id"]
            file_path = os.path.join(
                self.data_dir, "games", f"{user_id}_{game_id}.json"
            )

            with open(file_path, "w") as f:
                json.dump(game_data, f, indent=2)

            logger.info(f"Stored game {game_id} for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing game: {str(e)}")
            return False

    def get_game(self, game_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve a chess game.

        Args:
            game_id: ID of the game to retrieve
            user_id: ID of the user who played the game

        Returns:
            Game data or empty dict if not found
        """
        try:
            file_path = os.path.join(
                self.data_dir, "games", f"{user_id}_{game_id}.json"
            )

            if not os.path.exists(file_path):
                logger.warning(f"Game {game_id} not found for user: {user_id}")
                return {}

            with open(file_path, "r") as f:
                game_data = json.load(f)

            logger.info(f"Retrieved game {game_id} for user: {user_id}")
            return game_data

        except Exception as e:
            logger.error(f"Error retrieving game: {str(e)}")
            return {}

    def get_user_games(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all games for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of game data
        """
        try:
            games = []
            games_dir = os.path.join(self.data_dir, "games")

            if not os.path.exists(games_dir):
                return games

            for filename in os.listdir(games_dir):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    file_path = os.path.join(games_dir, filename)

                    with open(file_path, "r") as f:
                        game_data = json.load(f)
                        games.append(game_data)

            logger.info(f"Retrieved {len(games)} games for user: {user_id}")
            return games

        except Exception as e:
            logger.error(f"Error retrieving user games: {str(e)}")
            return []

    def store_analysis(self, analysis_results: Dict[str, Any], user_id: str) -> bool:
        """
        Store game analysis results.

        Args:
            analysis_results: Analysis results to store
            user_id: ID of the user

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Ensure analysis has a game ID
            if "game_id" not in analysis_results:
                logger.error("Cannot store analysis without game ID")
                return False

            game_id = analysis_results["game_id"]
            file_path = os.path.join(
                self.data_dir, "analysis", f"{user_id}_{game_id}.json"
            )

            with open(file_path, "w") as f:
                json.dump(analysis_results, f, indent=2)

            logger.info(f"Stored analysis for game {game_id}, user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing analysis: {str(e)}")
            return False

    def get_analysis(self, game_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve game analysis results.

        Args:
            game_id: ID of the game
            user_id: ID of the user

        Returns:
            Analysis results or empty dict if not found
        """
        try:
            file_path = os.path.join(
                self.data_dir, "analysis", f"{user_id}_{game_id}.json"
            )

            if not os.path.exists(file_path):
                logger.warning(
                    f"Analysis not found for game {game_id}, user: {user_id}"
                )
                return {}

            with open(file_path, "r") as f:
                analysis_data = json.load(f)

            logger.info(f"Retrieved analysis for game {game_id}, user: {user_id}")
            return analysis_data

        except Exception as e:
            logger.error(f"Error retrieving analysis: {str(e)}")
            return {}

    def store_feedback(self, feedback: Dict[str, Any], user_id: str) -> bool:
        """
        Store feedback.

        Args:
            feedback: Feedback data to store
            user_id: ID of the user

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Ensure feedback has an ID
            if "id" not in feedback:
                logger.error("Cannot store feedback without ID")
                return False

            feedback_id = feedback["id"]
            file_path = os.path.join(
                self.data_dir, "feedback", f"{user_id}_{feedback_id}.json"
            )

            with open(file_path, "w") as f:
                json.dump(feedback, f, indent=2)

            logger.info(f"Stored feedback {feedback_id} for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing feedback: {str(e)}")
            return False

    def get_feedback(self, feedback_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve feedback.

        Args:
            feedback_id: ID of the feedback to retrieve
            user_id: ID of the user

        Returns:
            Feedback data or empty dict if not found
        """
        try:
            file_path = os.path.join(
                self.data_dir, "feedback", f"{user_id}_{feedback_id}.json"
            )

            if not os.path.exists(file_path):
                logger.warning(f"Feedback {feedback_id} not found for user: {user_id}")
                return {}

            with open(file_path, "r") as f:
                feedback_data = json.load(f)

            logger.info(f"Retrieved feedback {feedback_id} for user: {user_id}")
            return feedback_data

        except Exception as e:
            logger.error(f"Error retrieving feedback: {str(e)}")
            return {}

    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all feedback for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of feedback data
        """
        try:
            feedback_list = []
            feedback_dir = os.path.join(self.data_dir, "feedback")

            if not os.path.exists(feedback_dir):
                return feedback_list

            for filename in os.listdir(feedback_dir):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    file_path = os.path.join(feedback_dir, filename)

                    with open(file_path, "r") as f:
                        feedback_data = json.load(f)
                        feedback_list.append(feedback_data)

            logger.info(
                f"Retrieved {len(feedback_list)} feedback items for user: {user_id}"
            )
            return feedback_list

        except Exception as e:
            logger.error(f"Error retrieving user feedback: {str(e)}")
            return []

    def store_exercises(self, exercises: List[Dict[str, Any]], user_id: str) -> bool:
        """
        Store practice exercises.

        Args:
            exercises: List of exercises to store
            user_id: ID of the user

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            for exercise in exercises:
                # Ensure exercise has an ID
                if "id" not in exercise:
                    logger.warning("Skipping exercise without ID")
                    continue

                exercise_id = exercise["id"]
                file_path = os.path.join(
                    self.data_dir, "exercises", f"{user_id}_{exercise_id}.json"
                )

                with open(file_path, "w") as f:
                    json.dump(exercise, f, indent=2)

            logger.info(f"Stored {len(exercises)} exercises for user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing exercises: {str(e)}")
            return False

    def store_exercise_attempt(
        self, user_id: str, exercise_id: str, result: Dict[str, Any]
    ) -> bool:
        """
        Store an exercise attempt result.

        Args:
            user_id: ID of the user
            exercise_id: ID of the exercise
            result: Result of the attempt

        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Get the exercise
            file_path = os.path.join(
                self.data_dir, "exercises", f"{user_id}_{exercise_id}.json"
            )

            if not os.path.exists(file_path):
                logger.warning(f"Exercise {exercise_id} not found for user: {user_id}")
                return False

            with open(file_path, "r") as f:
                exercise = json.load(f)

            # Add the attempt to the exercise
            if "user_attempts" not in exercise:
                exercise["user_attempts"] = []

            exercise["user_attempts"].append(result)

            # Save the updated exercise
            with open(file_path, "w") as f:
                json.dump(exercise, f, indent=2)

            logger.info(f"Stored attempt for exercise {exercise_id}, user: {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error storing exercise attempt: {str(e)}")
            return False

    def get_exercise(self, exercise_id: str, user_id: str) -> Dict[str, Any]:
        """
        Retrieve an exercise.

        Args:
            exercise_id: ID of the exercise to retrieve
            user_id: ID of the user

        Returns:
            Exercise data or empty dict if not found
        """
        try:
            file_path = os.path.join(
                self.data_dir, "exercises", f"{user_id}_{exercise_id}.json"
            )

            if not os.path.exists(file_path):
                logger.warning(f"Exercise {exercise_id} not found for user: {user_id}")
                return {}

            with open(file_path, "r") as f:
                exercise_data = json.load(f)

            logger.info(f"Retrieved exercise {exercise_id} for user: {user_id}")
            return exercise_data

        except Exception as e:
            logger.error(f"Error retrieving exercise: {str(e)}")
            return {}

    def get_user_exercises(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all exercises for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of exercise data
        """
        try:
            exercises = []
            exercises_dir = os.path.join(self.data_dir, "exercises")

            if not os.path.exists(exercises_dir):
                return exercises

            for filename in os.listdir(exercises_dir):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    file_path = os.path.join(exercises_dir, filename)

                    with open(file_path, "r") as f:
                        exercise_data = json.load(f)
                        exercises.append(exercise_data)

            logger.info(f"Retrieved {len(exercises)} exercises for user: {user_id}")
            return exercises

        except Exception as e:
            logger.error(f"Error retrieving user exercises: {str(e)}")
            return []

    def backup_user_data(self, user_id: str, backup_dir: str) -> bool:
        """
        Create a backup of all user data.

        Args:
            user_id: ID of the user
            backup_dir: Directory to store the backup

        Returns:
            True if backup was successful, False otherwise
        """
        try:
            # Create backup directory if it doesn't exist
            os.makedirs(backup_dir, exist_ok=True)

            # Create user backup directory
            user_backup_dir = os.path.join(backup_dir, user_id)
            os.makedirs(user_backup_dir, exist_ok=True)

            # Backup profile
            profile = self.get_profile(user_id)
            if profile:
                with open(os.path.join(user_backup_dir, "profile.json"), "w") as f:
                    json.dump(profile, f, indent=2)

            # Backup games
            games = self.get_user_games(user_id)
            if games:
                games_dir = os.path.join(user_backup_dir, "games")
                os.makedirs(games_dir, exist_ok=True)

                for game in games:
                    game_id = game.get("id", "unknown")
                    with open(os.path.join(games_dir, f"{game_id}.json"), "w") as f:
                        json.dump(game, f, indent=2)

            # Backup feedback
            feedback_list = self.get_user_feedback(user_id)
            if feedback_list:
                feedback_dir = os.path.join(user_backup_dir, "feedback")
                os.makedirs(feedback_dir, exist_ok=True)

                for feedback in feedback_list:
                    feedback_id = feedback.get("id", "unknown")
                    with open(
                        os.path.join(feedback_dir, f"{feedback_id}.json"), "w"
                    ) as f:
                        json.dump(feedback, f, indent=2)

            # Backup exercises
            exercises = self.get_user_exercises(user_id)
            if exercises:
                exercises_dir = os.path.join(user_backup_dir, "exercises")
                os.makedirs(exercises_dir, exist_ok=True)

                for exercise in exercises:
                    exercise_id = exercise.get("id", "unknown")
                    with open(
                        os.path.join(exercises_dir, f"{exercise_id}.json"), "w"
                    ) as f:
                        json.dump(exercise, f, indent=2)

            logger.info(f"Created backup for user: {user_id} in {user_backup_dir}")
            return True

        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            return False

    def restore_user_data(self, user_id: str, backup_dir: str) -> bool:
        """
        Restore user data from a backup.

        Args:
            user_id: ID of the user
            backup_dir: Directory containing the backup

        Returns:
            True if restoration was successful, False otherwise
        """
        try:
            # Check if backup exists
            user_backup_dir = os.path.join(backup_dir, user_id)
            if not os.path.exists(user_backup_dir):
                logger.error(f"Backup not found for user: {user_id}")
                return False

            # Delete existing user data
            self._delete_user_data(user_id)

            # Restore profile
            profile_path = os.path.join(user_backup_dir, "profile.json")
            if os.path.exists(profile_path):
                with open(profile_path, "r") as f:
                    profile = json.load(f)
                    self.store_profile(profile)

            # Restore games
            games_dir = os.path.join(user_backup_dir, "games")
            if os.path.exists(games_dir):
                for filename in os.listdir(games_dir):
                    if filename.endswith(".json"):
                        with open(os.path.join(games_dir, filename), "r") as f:
                            game = json.load(f)
                            self.store_game(game, user_id)

            # Restore feedback
            feedback_dir = os.path.join(user_backup_dir, "feedback")
            if os.path.exists(feedback_dir):
                for filename in os.listdir(feedback_dir):
                    if filename.endswith(".json"):
                        with open(os.path.join(feedback_dir, filename), "r") as f:
                            feedback = json.load(f)
                            self.store_feedback(feedback, user_id)

            # Restore exercises
            exercises_dir = os.path.join(user_backup_dir, "exercises")
            if os.path.exists(exercises_dir):
                for filename in os.listdir(exercises_dir):
                    if filename.endswith(".json"):
                        with open(os.path.join(exercises_dir, filename), "r") as f:
                            exercise = json.load(f)
                            self.store_exercises([exercise], user_id)

            logger.info(f"Restored data for user: {user_id} from {user_backup_dir}")
            return True

        except Exception as e:
            logger.error(f"Error restoring data: {str(e)}")
            return False

    def export_user_data(self, user_id: str, export_file: str) -> bool:
        """
        Export all user data to a single JSON file.

        Args:
            user_id: ID of the user
            export_file: File to export data to

        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Collect all user data
            export_data = {
                "profile": self.get_profile(user_id),
                "games": self.get_user_games(user_id),
                "feedback": self.get_user_feedback(user_id),
                "exercises": self.get_user_exercises(user_id),
            }

            # Write to file
            with open(export_file, "w") as f:
                json.dump(export_data, f, indent=2)

            logger.info(f"Exported data for user: {user_id} to {export_file}")
            return True

        except Exception as e:
            logger.error(f"Error exporting data: {str(e)}")
            return False

    def import_user_data(self, import_file: str) -> bool:
        """
        Import user data from a JSON file.

        Args:
            import_file: File to import data from

        Returns:
            True if import was successful, False otherwise
        """
        try:
            # Read import file
            with open(import_file, "r") as f:
                import_data = json.load(f)

            # Extract user ID from profile
            profile = import_data.get("profile", {})
            if not profile or "id" not in profile:
                logger.error("Import file does not contain a valid profile with ID")
                return False

            user_id = profile["id"]

            # Import profile
            self.store_profile(profile)

            # Import games
            for game in import_data.get("games", []):
                self.store_game(game, user_id)

            # Import feedback
            for feedback in import_data.get("feedback", []):
                self.store_feedback(feedback, user_id)

            # Import exercises
            self.store_exercises(import_data.get("exercises", []), user_id)

            logger.info(f"Imported data for user: {user_id} from {import_file}")
            return True

        except Exception as e:
            logger.error(f"Error importing data: {str(e)}")
            return False

    def clear_all_data(self) -> bool:
        """
        Clear all data from storage.

        Returns:
            True if clearing was successful, False otherwise
        """
        try:
            # Remove all subdirectories
            for subdir in ["profiles", "games", "analysis", "feedback", "exercises"]:
                dir_path = os.path.join(self.data_dir, subdir)
                if os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    os.makedirs(dir_path)

            logger.info("Cleared all data from storage")
            return True

        except Exception as e:
            logger.error(f"Error clearing data: {str(e)}")
            return False

    def shutdown(self) -> bool:
        """
        Perform a clean shutdown.

        Returns:
            True if shutdown was successful, False otherwise
        """
        try:
            logger.info("Data Storage shut down successfully")
            return True

        except Exception as e:
            logger.error(f"Error during Data Storage shutdown: {str(e)}")
            return False
