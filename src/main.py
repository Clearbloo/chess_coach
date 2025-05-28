"""
Main application server for Chess Coach Software

This module serves as the entry point for the Chess Coach application,
handling routing, API endpoints, and integrating all components.
"""

import logging
import os
import sys
import time
from flask import Flask, render_template, request, jsonify, send_from_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import core modules
from core_engine import CoreEngine
from chess_engine_interface import ChessEngineInterface
from user_profile_manager import UserProfileManager
from game_analysis_engine import GameAnalysisEngine
from feedback_generator import FeedbackGenerator
from practice_module import PracticeModule
from data_storage import DataStorage


# Initialize Flask app
app = Flask(__name__)

# Initialize core components
data_storage = DataStorage(data_dir="./data")
chess_engine = ChessEngineInterface()
user_profile_manager = UserProfileManager(
    data_dir="./data/profiles"
)  # Fixed: pass directory path instead of DataStorage object
game_analysis_engine = GameAnalysisEngine(chess_engine)
feedback_generator = FeedbackGenerator()
practice_module = PracticeModule(data_dir="./data/exercises")

# Initialize core engine and register components
core_engine = CoreEngine()
core_engine.register_component("data_storage", data_storage)
core_engine.register_component("chess_engine", chess_engine)
core_engine.register_component("user_profile", user_profile_manager)
core_engine.register_component("game_analysis", game_analysis_engine)
core_engine.register_component("feedback_generator", feedback_generator)
core_engine.register_component("practice_module", practice_module)

# Initialize all components
data_storage.initialize()
chess_engine.initialize()
user_profile_manager.initialize()
game_analysis_engine.initialize()
feedback_generator.initialize()
practice_module.initialize()
core_engine.initialize_system()

# Set up cross-references between components
practice_module.set_chess_engine(chess_engine)
practice_module.set_user_profile_manager(user_profile_manager)
# Removed set_feedback_generator as it doesn't exist in GameAnalysisEngine


# Create sample data for testing
def create_sample_data():
    """Create sample user data for testing purposes"""
    try:
        # Check if we already have sample data
        if data_storage.get_profile("sample_user"):
            logger.info("Sample data already exists")
            return

        # Create a sample user profile
        sample_user = {
            "id": "sample_user",
            "username": "Sample Player",
            "skill_level": "Intermediate",
            "created_at": "2025-05-01T12:00:00Z",
            "statistics": {
                "games_analyzed": 5,
                "puzzles_solved": 25,
                "accuracy": 68,
                "strength_areas": [
                    {"concept": "Opening Play", "count": 3},
                    {"concept": "Pawn Structure", "count": 2},
                ],
                "weakness_areas": [
                    {"concept": "Tactical Awareness", "count": 4},
                    {"concept": "Endgame Technique", "count": 3},
                ],
            },
        }

        # Store the sample user
        data_storage.store_profile(sample_user)

        # Create sample games
        sample_games = [
            {
                "id": "game1",
                "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6 8. c3 O-O",
                "analysis": {
                    "accuracy": 72,
                    "best_moves": 5,
                    "good_moves": 3,
                    "inaccuracies": 1,
                    "mistakes": 0,
                    "blunders": 0,
                },
                "strengths": [
                    {
                        "concept": "Opening Play",
                        "description": "Good piece development and center control",
                    }
                ],
                "weaknesses": [
                    {
                        "concept": "Tactical Awareness",
                        "description": "Missed tactical opportunity on move 7",
                    }
                ],
            },
            {
                "id": "game2",
                "pgn": "1. d4 Nf6 2. c4 e6 3. Nc3 Bb4 4. e3 O-O 5. Bd3 d5 6. Nf3 c5 7. O-O Nc6 8. a3 Bxc3",
                "analysis": {
                    "accuracy": 65,
                    "best_moves": 4,
                    "good_moves": 2,
                    "inaccuracies": 2,
                    "mistakes": 1,
                    "blunders": 0,
                },
                "strengths": [
                    {
                        "concept": "Pawn Structure",
                        "description": "Maintained solid pawn structure throughout",
                    }
                ],
                "weaknesses": [
                    {
                        "concept": "Endgame Technique",
                        "description": "Inefficient piece coordination in the middlegame",
                    }
                ],
            },
        ]

        # Store sample games
        for game in sample_games:
            data_storage.store_game(game, "sample_user")

        # Create sample practice sessions
        sample_sessions = [
            {
                "id": "session1",
                "type": "tactical",
                "created_at": "2025-05-10T14:30:00Z",
                "exercises": [
                    {
                        "id": "ex1",
                        "type": "fork",
                        "difficulty": "medium",
                        "completed": True,
                        "result": "correct",
                    },
                    {
                        "id": "ex2",
                        "type": "pin",
                        "difficulty": "medium",
                        "completed": True,
                        "result": "incorrect",
                    },
                ],
                "completed": True,
                "results": {"total": 2, "correct": 1, "incorrect": 1, "skipped": 0},
            }
        ]

        # Store sample exercises
        for session in sample_sessions:
            data_storage.store_exercises(session["exercises"], "sample_user")

        logger.info("Sample data created successfully")

    except Exception as e:
        logger.error(f"Error creating sample data: {str(e)}")


# Create sample data
create_sample_data()


# Routes
@app.route("/")
def index():
    """Render the main application page"""
    return render_template("index.html")


@app.route("/static/<path:path>")
def serve_static(path):
    """Serve static files"""
    return send_from_directory("static", path)


# API endpoints
@app.route("/api/user/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get user profile"""
    profile = user_profile_manager.get_profile(user_id)
    if profile:
        return jsonify(profile)
    else:
        return jsonify({"error": "User not found"}), 404


@app.route("/api/user/<user_id>", methods=["POST"])
def update_user(user_id):
    """Update user profile"""
    data = request.json
    success = user_profile_manager.update_profile(user_id, data)
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"error": "Failed to update user"}), 400


@app.route("/api/analyze", methods=["POST"])
def analyze_game():
    """Analyze a chess game"""
    data = request.json
    user_id = data.get("user_id", "guest")
    pgn = data.get("pgn", "")

    if not pgn:
        return jsonify({"error": "PGN is required"}), 400

    # Create a properly formatted game_data dictionary
    game_data = {"pgn": pgn, "id": data.get("id", f"game_{user_id}_{int(time.time())}")}

    # Log the game data for debugging
    logger.info(f"Analyzing game for user {user_id}: {game_data['id']}")
    logger.info(f"PGN string received: {pgn}")

    # Note: core_engine.analyze_game expects (game_data, user_id) not (user_id, game_data)
    analysis_results = core_engine.analyze_game(game_data, user_id)
    return jsonify(analysis_results)


@app.route("/api/practice/generate", methods=["POST"])
def generate_practice():
    """Generate practice exercises"""
    data = request.json
    user_id = data.get("user_id", "guest")
    focus_areas = data.get("focus_areas", None)

    # Log the practice generation request
    logger.info(
        f"Generating practice exercises for user {user_id} with focus areas: {focus_areas}"
    )

    # Fixed: Using the correct method name generate_practice instead of generate_practice_exercises
    exercises = core_engine.generate_practice(user_id, focus_areas)
    return jsonify(exercises)


@app.route("/api/practice/validate", methods=["POST"])
def validate_exercise():
    """Validate a practice exercise solution"""
    data = request.json
    user_id = data.get("user_id", "guest")
    exercise_id = data.get("exercise_id", "")
    user_move = data.get("move", "")

    if not exercise_id or not user_move:
        return jsonify({"error": "Exercise ID and move are required"}), 400

    result = core_engine.validate_exercise_solution(user_id, exercise_id, user_move)
    return jsonify(result)


@app.route("/api/feedback/<user_id>/<game_id>", methods=["GET"])
def get_feedback(user_id, game_id):
    """Get feedback for a game"""
    feedback = core_engine.get_game_feedback(user_id, game_id)
    if feedback:
        return jsonify(feedback)
    else:
        return jsonify({"error": "Feedback not found"}), 404


@app.route("/api/games/<user_id>", methods=["GET"])
def get_user_games(user_id):
    """Get all games for a user"""
    games = data_storage.get_user_games(user_id)
    return jsonify(games)


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Internal server error"}), 500


# Run the application
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
