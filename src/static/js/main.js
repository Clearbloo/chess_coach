/**
 * Main Application JavaScript for Chess Coach
 * Handles UI interactions and integrates all components
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    ChessCoach.init();
});

// Main application namespace
const ChessCoach = {
    // Configuration
    config: {
        apiEndpoint: '/api',
        defaultUser: 'guest',
        autoSaveInterval: 60000, // 1 minute
    },
    
    // State
    state: {
        currentUser: null,
        currentView: 'dashboard',
        chessBoard: null,
        gameBeingAnalyzed: null,
        practiceSession: null,
        isAnalyzing: false,
    },
    
    // Initialize the application
    init: function() {
        console.log('Initializing Chess Coach application...');
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Initialize components
        this.initializeComponents();
        
        // Load user data or create guest profile
        this.loadUserData();
        
        // Navigate to default view
        this.navigateTo('dashboard');
        
        console.log('Chess Coach application initialized');
    },
    
    // Set up event listeners for UI interactions
    setupEventListeners: function() {
        // Navigation menu
        document.querySelectorAll('.nav-menu a, .sidebar-nav a').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.target.closest('a').dataset.view;
                if (view) {
                    this.navigateTo(view);
                }
            });
        });
        
        // User menu
        const userMenu = document.getElementById('user-menu');
        if (userMenu) {
            userMenu.addEventListener('click', () => {
                document.getElementById('user-dropdown').classList.toggle('show');
            });
        }
        
        // Game analysis form
        const analysisForm = document.getElementById('analysis-form');
        if (analysisForm) {
            analysisForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.startGameAnalysis();
            });
        }
        
        // Practice session buttons
        document.querySelectorAll('.practice-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const practiceType = e.target.closest('.practice-card').dataset.type;
                this.startPracticeSession(practiceType);
            });
        });
        
        // Global click handler for closing dropdowns
        document.addEventListener('click', (e) => {
            if (!e.target.closest('#user-menu')) {
                const dropdown = document.getElementById('user-dropdown');
                if (dropdown && dropdown.classList.contains('show')) {
                    dropdown.classList.remove('show');
                }
            }
        });
    },
    
    // Initialize application components
    initializeComponents: function() {
        // Initialize chess board if the element exists
        const boardContainer = document.getElementById('chess-board');
        if (boardContainer) {
            this.state.chessBoard = new ChessBoard('chess-board', {
                size: 400,
                showControls: true,
                onMove: this.handleBoardMove.bind(this),
                onSelect: this.handleBoardSelect.bind(this)
            });
        }
        
        // Initialize charts for progress tracking
        this.initializeCharts();
        
        // Set up auto-save
        setInterval(() => {
            this.saveUserData();
        }, this.config.autoSaveInterval);
    },
    
    // Initialize charts for progress tracking
    initializeCharts: function() {
        // This would use a charting library like Chart.js
        // For now, we'll just log that charts would be initialized
        console.log('Charts would be initialized here');
    },
    
    // Load user data or create guest profile
    loadUserData: function() {
        // Try to load from localStorage
        const userData = localStorage.getItem('chessCoachUserData');
        
        if (userData) {
            try {
                this.state.currentUser = JSON.parse(userData);
                console.log('Loaded user data:', this.state.currentUser);
                this.updateUserDisplay();
            } catch (e) {
                console.error('Error parsing user data:', e);
                this.createGuestProfile();
            }
        } else {
            this.createGuestProfile();
        }
    },
    
    // Create a guest user profile
    createGuestProfile: function() {
        this.state.currentUser = {
            id: 'guest-' + Date.now(),
            username: 'Guest',
            skill_level: 'Beginner',
            created_at: new Date().toISOString(),
            games: [],
            practice_sessions: [],
            statistics: {
                games_analyzed: 0,
                puzzles_solved: 0,
                accuracy: 0,
                strength_areas: [],
                weakness_areas: []
            }
        };
        
        this.saveUserData();
        this.updateUserDisplay();
    },
    
    // Save user data to localStorage
    saveUserData: function() {
        if (this.state.currentUser) {
            localStorage.setItem('chessCoachUserData', JSON.stringify(this.state.currentUser));
            console.log('User data saved');
        }
    },
    
    // Update UI elements with user information
    updateUserDisplay: function() {
        const user = this.state.currentUser;
        
        // Update user name in header
        const userNameElement = document.getElementById('user-name');
        if (userNameElement) {
            userNameElement.textContent = user.username;
        }
        
        // Update user avatar
        const userAvatarElement = document.getElementById('user-avatar');
        if (userAvatarElement) {
            userAvatarElement.textContent = user.username.charAt(0).toUpperCase();
        }
        
        // Update dashboard stats
        this.updateDashboardStats();
    },
    
    // Update dashboard statistics
    updateDashboardStats: function() {
        const user = this.state.currentUser;
        
        // Only update if we're on the dashboard
        if (this.state.currentView !== 'dashboard') return;
        
        // Update stats
        const statsElements = {
            gamesAnalyzed: document.getElementById('stat-games-analyzed'),
            puzzlesSolved: document.getElementById('stat-puzzles-solved'),
            accuracy: document.getElementById('stat-accuracy'),
            skillLevel: document.getElementById('stat-skill-level')
        };
        
        if (statsElements.gamesAnalyzed) {
            statsElements.gamesAnalyzed.textContent = user.statistics.games_analyzed;
        }
        
        if (statsElements.puzzlesSolved) {
            statsElements.puzzlesSolved.textContent = user.statistics.puzzles_solved;
        }
        
        if (statsElements.accuracy) {
            statsElements.accuracy.textContent = user.statistics.accuracy + '%';
        }
        
        if (statsElements.skillLevel) {
            statsElements.skillLevel.textContent = user.skill_level;
        }
        
        // Update strengths and weaknesses
        this.updateStrengthsWeaknesses();
    },
    
    // Update strengths and weaknesses display
    updateStrengthsWeaknesses: function() {
        const user = this.state.currentUser;
        
        // Strengths list
        const strengthsList = document.getElementById('strengths-list');
        if (strengthsList) {
            strengthsList.innerHTML = '';
            
            if (user.statistics.strength_areas && user.statistics.strength_areas.length > 0) {
                user.statistics.strength_areas.forEach(strength => {
                    const li = document.createElement('li');
                    li.textContent = strength.concept;
                    strengthsList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No strengths identified yet';
                strengthsList.appendChild(li);
            }
        }
        
        // Weaknesses list
        const weaknessesList = document.getElementById('weaknesses-list');
        if (weaknessesList) {
            weaknessesList.innerHTML = '';
            
            if (user.statistics.weakness_areas && user.statistics.weakness_areas.length > 0) {
                user.statistics.weakness_areas.forEach(weakness => {
                    const li = document.createElement('li');
                    li.textContent = weakness.concept;
                    weaknessesList.appendChild(li);
                });
            } else {
                const li = document.createElement('li');
                li.textContent = 'No weaknesses identified yet';
                weaknessesList.appendChild(li);
            }
        }
    },
    
    // Navigate to a specific view
    navigateTo: function(view) {
        console.log('Navigating to:', view);
        
        // Update current view
        this.state.currentView = view;
        
        // Hide all views
        document.querySelectorAll('.view').forEach(el => {
            el.classList.add('hidden');
        });
        
        // Show the selected view
        const viewElement = document.getElementById(`${view}-view`);
        if (viewElement) {
            viewElement.classList.remove('hidden');
        }
        
        // Update active navigation links
        document.querySelectorAll('.nav-menu a, .sidebar-nav a').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.view === view) {
                link.classList.add('active');
            }
        });
        
        // Perform view-specific initialization
        switch (view) {
            case 'dashboard':
                this.updateDashboardStats();
                break;
                
            case 'analysis':
                this.initializeAnalysisView();
                break;
                
            case 'practice':
                this.initializePracticeView();
                break;
                
            case 'progress':
                this.initializeProgressView();
                break;
                
            case 'settings':
                this.initializeSettingsView();
                break;
        }
    },
    
    // Initialize the analysis view
    initializeAnalysisView: function() {
        console.log('Initializing analysis view');
        
        // Reset the analysis state
        this.state.isAnalyzing = false;
        this.state.gameBeingAnalyzed = null;
        
        // Clear the move list
        const moveList = document.getElementById('move-list');
        if (moveList) {
            moveList.innerHTML = '';
        }
        
        // Reset the board
        if (this.state.chessBoard) {
            this.state.chessBoard.reset();
        }
        
        // Clear analysis info
        const analysisInfo = document.getElementById('position-analysis');
        if (analysisInfo) {
            analysisInfo.innerHTML = '<p>Upload a game or enter moves to begin analysis.</p>';
        }
    },
    
    // Initialize the practice view
    initializePracticeView: function() {
        console.log('Initializing practice view');
        
        // Reset practice session
        this.state.practiceSession = null;
        
        // Update practice categories based on user weaknesses
        this.updatePracticeCategories();
    },
    
    // Update practice categories based on user weaknesses
    updatePracticeCategories: function() {
        const user = this.state.currentUser;
        const practiceGrid = document.getElementById('practice-grid');
        
        if (!practiceGrid) return;
        
        // Clear existing categories
        practiceGrid.innerHTML = '';
        
        // Add standard categories
        const categories = [
            { type: 'tactical', title: 'Tactical Training', description: 'Improve your tactical awareness with puzzles' },
            { type: 'strategic', title: 'Strategic Planning', description: 'Develop your strategic understanding' },
            { type: 'endgame', title: 'Endgame Technique', description: 'Master essential endgame positions' },
            { type: 'opening', title: 'Opening Repertoire', description: 'Build a solid opening foundation' }
        ];
        
        // Add weakness-specific categories
        if (user.statistics.weakness_areas && user.statistics.weakness_areas.length > 0) {
            user.statistics.weakness_areas.forEach(weakness => {
                categories.push({
                    type: weakness.concept.toLowerCase().replace(' ', '_'),
                    title: `Improve ${weakness.concept}`,
                    description: 'Targeted exercises for your specific weakness',
                    isWeakness: true
                });
            });
        }
        
        // Create category cards
        categories.forEach(category => {
            const card = document.createElement('div');
            card.className = 'practice-card';
            card.dataset.type = category.type;
            
            if (category.isWeakness) {
                card.classList.add('weakness-card');
            }
            
            card.innerHTML = `
                <div class="practice-card-icon">
                    <i class="fas fa-${this.getPracticeIcon(category.type)}"></i>
                </div>
                <h3 class="practice-card-title">${category.title}</h3>
                <p class="practice-card-description">${category.description}</p>
                <button class="btn">Start Practice</button>
            `;
            
            card.addEventListener('click', () => {
                this.startPracticeSession(category.type);
            });
            
            practiceGrid.appendChild(card);
        });
    },
    
    // Get icon for practice category
    getPracticeIcon: function(type) {
        const icons = {
            tactical: 'bullseye',
            strategic: 'chess-board',
            endgame: 'flag-checkered',
            opening: 'book-open',
            calculation: 'calculator',
            pattern_recognition: 'eye',
            piece_coordination: 'puzzle-piece',
            pawn_structure: 'chess-pawn',
            king_safety: 'shield-alt',
            time_management: 'clock'
        };
        
        return icons[type] || 'chess';
    },
    
    // Initialize the progress view
    initializeProgressView: function() {
        console.log('Initializing progress view');
        
        // Update progress charts
        this.updateProgressCharts();
    },
    
    // Update progress charts
    updateProgressCharts: function() {
        // This would use a charting library to render charts
        console.log('Progress charts would be updated here');
    },
    
    // Initialize the settings view
    initializeSettingsView: function() {
        console.log('Initializing settings view');
        
        // Populate settings form with current user data
        const user = this.state.currentUser;
        
        const usernameInput = document.getElementById('settings-username');
        if (usernameInput) {
            usernameInput.value = user.username;
        }
        
        const skillLevelSelect = document.getElementById('settings-skill-level');
        if (skillLevelSelect) {
            skillLevelSelect.value = user.skill_level;
        }
    },
    
    // Start game analysis
    startGameAnalysis: function() {
        console.log('Starting game analysis');
        
        // Get PGN input
        const pgnInput = document.getElementById('pgn-input');
        if (!pgnInput || !pgnInput.value.trim()) {
            alert('Please enter a game in PGN format or move notation');
            return;
        }
        
        const pgn = pgnInput.value.trim();
        
        // Set analyzing state
        this.state.isAnalyzing = true;
        
        // Show loading indicator
        const analysisContainer = document.getElementById('analysis-container');
        if (analysisContainer) {
            analysisContainer.classList.add('loading');
        }
        
        // In a real implementation, this would send the PGN to the backend
        // For now, we'll simulate analysis with a timeout
        setTimeout(() => {
            this.processAnalysisResults(this.simulateGameAnalysis(pgn));
        }, 2000);
    },
    
    // Simulate game analysis (would be replaced by actual backend call)
    simulateGameAnalysis: function(pgn) {
        // Create a simple game object with moves
        const game = {
            id: 'game-' + Date.now(),
            pgn: pgn,
            moves: [],
            analysis: {
                accuracy: Math.floor(Math.random() * 40) + 60, // 60-99%
                best_moves: Math.floor(Math.random() * 10) + 10,
                good_moves: Math.floor(Math.random() * 15) + 15,
                inaccuracies: Math.floor(Math.random() * 5) + 1,
                mistakes: Math.floor(Math.random() * 3),
                blunders: Math.floor(Math.random() * 2)
            },
            strengths: [
                { concept: 'Opening Play', description: 'Good piece development and center control' },
                { concept: 'Pawn Structure', description: 'Maintained solid pawn structure throughout' }
            ],
            weaknesses: [
                { concept: 'Tactical Awareness', description: 'Missed tactical opportunities on moves 15 and 23' },
                { concept: 'Endgame Technique', description: 'Inefficient king activation in the endgame' }
            ]
        };
        
        // Generate some moves
        const moveCount = Math.floor(Math.random() * 20) + 30; // 30-50 moves
        
        for (let i = 1; i <= moveCount; i++) {
            const whiteMove = {
                moveNumber: i,
                color: 'white',
                move: this.generateRandomMove(),
                evaluation: (Math.random() * 2 - 1).toFixed(2),
                comment: i % 5 === 0 ? this.generateRandomComment() : ''
            };
            
            game.moves.push(whiteMove);
            
            // Black's move (except for the last move if moveCount is odd)
            if (i < moveCount || moveCount % 2 === 0) {
                const blackMove = {
                    moveNumber: i,
                    color: 'black',
                    move: this.generateRandomMove(),
                    evaluation: (Math.random() * 2 - 1).toFixed(2),
                    comment: i % 7 === 0 ? this.generateRandomComment() : ''
                };
                
                game.moves.push(blackMove);
            }
        }
        
        return game;
    },
    
    // Generate a random chess move (for simulation)
    generateRandomMove: function() {
        const pieces = ['', '', '', '', '', 'N', 'B', 'R', 'Q', 'K'];
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        const ranks = ['1', '2', '3', '4', '5', '6', '7', '8'];
        
        const piece = pieces[Math.floor(Math.random() * pieces.length)];
        const file = files[Math.floor(Math.random() * files.length)];
        const rank = ranks[Math.floor(Math.random() * ranks.length)];
        
        // Sometimes add capture or check
        const extras = ['', '', '', '', 'x', '+', '#'];
        const extra = extras[Math.floor(Math.random() * extras.length)];
        
        return piece + file + rank + extra;
    },
    
    // Generate a random comment (for simulation)
    generateRandomComment: function() {
        const comments = [
            'Good move',
            'Best move',
            'Inaccuracy',
            'Mistake',
            'Blunder',
            'Interesting alternative',
            'Missed opportunity',
            'Strong positional play',
            'Tactical oversight',
            'Excellent calculation'
        ];
        
        return comments[Math.floor(Math.random() * comments.length)];
    },
    
    // Process analysis results
    processAnalysisResults: function(game) {
        console.log('Processing analysis results:', game);
        
        // Store the analyzed game
        this.state.gameBeingAnalyzed = game;
        
        // Add to user's games
        this.state.currentUser.games.push(game);
        this.state.currentUser.statistics.games_analyzed++;
        
        // Update user profile with strengths and weaknesses
        this.updateUserProfile(game);
        
        // Save user data
        this.saveUserData();
        
        // Update the UI
        this.updateAnalysisUI(game);
        
        // Hide loading indicator
        const analysisContainer = document.getElementById('analysis-container');
        if (analysisContainer) {
            analysisContainer.classList.remove('loading');
        }
    },
    
    // Update user profile with game analysis insights
    updateUserProfile: function(game) {
        const user = this.state.currentUser;
        
        // Initialize arrays if they don't exist
        if (!user.statistics.strength_areas) {
            user.statistics.strength_areas = [];
        }
        
        if (!user.statistics.weakness_areas) {
            user.statistics.weakness_areas = [];
        }
        
        // Add new strengths
        game.strengths.forEach(strength => {
            // Check if this strength already exists
            const existingIndex = user.statistics.strength_areas.findIndex(
                s => s.concept === strength.concept
            );
            
            if (existingIndex >= 0) {
                // Increment count for existing strength
                user.statistics.strength_areas[existingIndex].count = 
                    (user.statistics.strength_areas[existingIndex].count || 1) + 1;
            } else {
                // Add new strength
                user.statistics.strength_areas.push({
                    concept: strength.concept,
                    count: 1
                });
            }
        });
        
        // Add new weaknesses
        game.weaknesses.forEach(weakness => {
            // Check if this weakness already exists
            const existingIndex = user.statistics.weakness_areas.findIndex(
                w => w.concept === weakness.concept
            );
            
            if (existingIndex >= 0) {
                // Increment count for existing weakness
                user.statistics.weakness_areas[existingIndex].count = 
                    (user.statistics.weakness_areas[existingIndex].count || 1) + 1;
            } else {
                // Add new weakness
                user.statistics.weakness_areas.push({
                    concept: weakness.concept,
                    count: 1
                });
            }
        });
        
        // Sort strengths and weaknesses by count (descending)
        user.statistics.strength_areas.sort((a, b) => (b.count || 1) - (a.count || 1));
        user.statistics.weakness_areas.sort((a, b) => (b.count || 1) - (a.count || 1));
        
        // Limit to top 5
        user.statistics.strength_areas = user.statistics.strength_areas.slice(0, 5);
        user.statistics.weakness_areas = user.statistics.weakness_areas.slice(0, 5);
        
        // Update accuracy
        if (typeof game.analysis.accuracy === 'number') {
            // Weighted average of current accuracy and new game accuracy
            const gamesAnalyzed = user.statistics.games_analyzed;
            user.statistics.accuracy = Math.round(
                ((user.statistics.accuracy * (gamesAnalyzed - 1)) + game.analysis.accuracy) / gamesAnalyzed
            );
        }
    },
    
    // Update analysis UI with game results
    updateAnalysisUI: function(game) {
        // Update move list
        const moveList = document.getElementById('move-list');
        if (moveList) {
            moveList.innerHTML = '';
            
            let currentMoveNumber = 0;
            let moveRow = null;
            
            game.moves.forEach((move, index) => {
                // Create a new row for each move number
                if (move.moveNumber !== currentMoveNumber) {
                    currentMoveNumber = move.moveNumber;
                    moveRow = document.createElement('div');
                    moveRow.className = 'move-list-item';
                    
                    const moveNumber = document.createElement('div');
                    moveNumber.className = 'move-number';
                    moveNumber.textContent = currentMoveNumber + '.';
                    
                    const whiteMove = document.createElement('div');
                    whiteMove.className = 'move-white';
                    
                    const blackMove = document.createElement('div');
                    blackMove.className = 'move-black';
                    
                    moveRow.appendChild(moveNumber);
                    moveRow.appendChild(whiteMove);
                    moveRow.appendChild(blackMove);
                    
                    moveList.appendChild(moveRow);
                }
                
                // Add the move to the appropriate column
                const moveText = document.createElement('span');
                moveText.textContent = move.move;
                moveText.dataset.index = index;
                moveText.title = move.comment || '';
                
                if (move.comment) {
                    if (move.comment.toLowerCase().includes('blunder')) {
                        moveText.classList.add('text-error');
                    } else if (move.comment.toLowerCase().includes('mistake')) {
                        moveText.classList.add('text-warning');
                    } else if (move.comment.toLowerCase().includes('inaccuracy')) {
                        moveText.classList.add('text-warning');
                    } else if (move.comment.toLowerCase().includes('good') || 
                               move.comment.toLowerCase().includes('best') ||
                               move.comment.toLowerCase().includes('excellent')) {
                        moveText.classList.add('text-success');
                    }
                }
                
                moveText.addEventListener('click', () => {
                    this.selectMove(index);
                });
                
                if (move.color === 'white') {
                    moveRow.querySelector('.move-white').appendChild(moveText);
                } else {
                    moveRow.querySelector('.move-black').appendChild(moveText);
                }
            });
        }
        
        // Update analysis summary
        const analysisInfo = document.getElementById('analysis-summary');
        if (analysisInfo) {
            analysisInfo.innerHTML = `
                <div class="analysis-stat">
                    <span class="analysis-stat-label">Accuracy:</span>
                    <span class="analysis-stat-value">${game.analysis.accuracy}%</span>
                </div>
                <div class="analysis-stat">
                    <span class="analysis-stat-label">Best Moves:</span>
                    <span class="analysis-stat-value">${game.analysis.best_moves}</span>
                </div>
                <div class="analysis-stat">
                    <span class="analysis-stat-label">Good Moves:</span>
                    <span class="analysis-stat-value">${game.analysis.good_moves}</span>
                </div>
                <div class="analysis-stat">
                    <span class="analysis-stat-label">Inaccuracies:</span>
                    <span class="analysis-stat-value">${game.analysis.inaccuracies}</span>
                </div>
                <div class="analysis-stat">
                    <span class="analysis-stat-label">Mistakes:</span>
                    <span class="analysis-stat-value">${game.analysis.mistakes}</span>
                </div>
                <div class="analysis-stat">
                    <span class="analysis-stat-label">Blunders:</span>
                    <span class="analysis-stat-value">${game.analysis.blunders}</span>
                </div>
            `;
        }
        
        // Update strengths and weaknesses
        const strengthsContainer = document.getElementById('analysis-strengths');
        if (strengthsContainer) {
            strengthsContainer.innerHTML = '';
            
            game.strengths.forEach(strength => {
                const strengthItem = document.createElement('div');
                strengthItem.className = 'feedback-item';
                strengthItem.innerHTML = `
                    <div class="feedback-icon">
                        <i class="fas fa-check"></i>
                    </div>
                    <div class="feedback-content">
                        <div class="feedback-title">${strength.concept}</div>
                        <div class="feedback-description">${strength.description}</div>
                    </div>
                `;
                
                strengthsContainer.appendChild(strengthItem);
            });
        }
        
        const weaknessesContainer = document.getElementById('analysis-weaknesses');
        if (weaknessesContainer) {
            weaknessesContainer.innerHTML = '';
            
            game.weaknesses.forEach(weakness => {
                const weaknessItem = document.createElement('div');
                weaknessItem.className = 'feedback-item';
                weaknessItem.innerHTML = `
                    <div class="feedback-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div class="feedback-content">
                        <div class="feedback-title">${weakness.concept}</div>
                        <div class="feedback-description">${weakness.description}</div>
                    </div>
                `;
                
                weaknessesContainer.appendChild(weaknessItem);
            });
        }
        
        // Reset the board
        if (this.state.chessBoard) {
            this.state.chessBoard.reset();
        }
        
        // Select the first move
        if (game.moves.length > 0) {
            this.selectMove(0);
        }
    },
    
    // Select a move in the analysis
    selectMove: function(moveIndex) {
        const game = this.state.gameBeingAnalyzed;
        if (!game || !game.moves || moveIndex >= game.moves.length) return;
        
        // Highlight the selected move in the move list
        document.querySelectorAll('.move-list-item span').forEach(span => {
            span.classList.remove('active');
        });
        
        const moveSpan = document.querySelector(`.move-list-item span[data-index="${moveIndex}"]`);
        if (moveSpan) {
            moveSpan.classList.add('active');
            
            // Scroll the move into view
            moveSpan.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        
        // Update the board position
        // In a real implementation, this would set the board to the position after this move
        // For now, we'll just simulate it
        
        // Update position analysis
        const positionAnalysis = document.getElementById('position-analysis');
        if (positionAnalysis) {
            const move = game.moves[moveIndex];
            
            positionAnalysis.innerHTML = `
                <div class="position-info">
                    <p><strong>Move ${move.moveNumber}${move.color === 'white' ? ' (White)' : ' (Black)'}: ${move.move}</strong></p>
                    <p>Evaluation: ${move.evaluation > 0 ? '+' : ''}${move.evaluation}</p>
                    ${move.comment ? `<p>Comment: ${move.comment}</p>` : ''}
                </div>
            `;
        }
    },
    
    // Start a practice session
    startPracticeSession: function(practiceType) {
        console.log('Starting practice session:', practiceType);
        
        // Show loading indicator
        const practiceContainer = document.getElementById('practice-container');
        if (practiceContainer) {
            practiceContainer.classList.add('loading');
        }
        
        // In a real implementation, this would request exercises from the backend
        // For now, we'll simulate it with a timeout
        setTimeout(() => {
            this.processPracticeSession(this.simulatePracticeSession(practiceType));
        }, 1500);
    },
    
    // Simulate a practice session (would be replaced by actual backend call)
    simulatePracticeSession: function(practiceType) {
        // Create a practice session with exercises
        const session = {
            id: 'session-' + Date.now(),
            type: practiceType,
            created_at: new Date().toISOString(),
            exercises: [],
            current_exercise_index: 0,
            completed: false,
            results: {
                total: 0,
                correct: 0,
                incorrect: 0,
                skipped: 0
            }
        };
        
        // Generate exercises based on practice type
        const exerciseCount = Math.floor(Math.random() * 5) + 5; // 5-10 exercises
        
        for (let i = 0; i < exerciseCount; i++) {
            session.exercises.push(this.generateExercise(practiceType, i));
        }
        
        session.results.total = session.exercises.length;
        
        return session;
    },
    
    // Generate an exercise (for simulation)
    generateExercise: function(practiceType, index) {
        // Different exercise types based on practice type
        let exerciseType, difficulty, position, description;
        
        switch (practiceType) {
            case 'tactical':
                exerciseType = ['fork', 'pin', 'skewer', 'discovered_attack', 'double_attack'][Math.floor(Math.random() * 5)];
                difficulty = ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)];
                position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'; // Starting position as placeholder
                description = `Find the ${exerciseType.replace('_', ' ')} in this position`;
                break;
                
            case 'strategic':
                exerciseType = ['pawn_structure', 'piece_activity', 'king_safety', 'center_control'][Math.floor(Math.random() * 4)];
                difficulty = ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)];
                position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'; // Starting position as placeholder
                description = `Improve your ${exerciseType.replace('_', ' ')} in this position`;
                break;
                
            case 'endgame':
                exerciseType = ['pawn_endgame', 'rook_endgame', 'queen_endgame', 'minor_piece_endgame'][Math.floor(Math.random() * 4)];
                difficulty = ['easy', 'medium', 'hard'][Math.floor(Math.random() * 3)];
                position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'; // Starting position as placeholder
                description = `Find the winning plan in this ${exerciseType.replace('_', ' ')}`;
                break;
                
            default:
                exerciseType = 'general';
                difficulty = 'medium';
                position = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'; // Starting position as placeholder
                description = 'Find the best move in this position';
        }
        
        return {
            id: 'exercise-' + Date.now() + '-' + index,
            type: exerciseType,
            difficulty: difficulty,
            position: position,
            description: description,
            correct_moves: ['e4', 'd4'], // Example correct moves
            hints: [
                'Look for tactical opportunities',
                'Consider piece coordination',
                'The solution involves a key piece'
            ],
            completed: false,
            result: null
        };
    },
    
    // Process practice session
    processPracticeSession: function(session) {
        console.log('Processing practice session:', session);
        
        // Store the practice session
        this.state.practiceSession = session;
        
        // Add to user's practice sessions
        this.state.currentUser.practice_sessions.push(session);
        
        // Save user data
        this.saveUserData();
        
        // Update the UI
        this.updatePracticeUI(session);
        
        // Hide loading indicator
        const practiceContainer = document.getElementById('practice-container');
        if (practiceContainer) {
            practiceContainer.classList.remove('loading');
        }
        
        // Show the practice exercise view
        this.navigateTo('practice-exercise');
    },
    
    // Update practice UI
    updatePracticeUI: function(session) {
        // Create the practice exercise view if it doesn't exist
        let practiceExerciseView = document.getElementById('practice-exercise-view');
        
        if (!practiceExerciseView) {
            practiceExerciseView = document.createElement('div');
            practiceExerciseView.id = 'practice-exercise-view';
            practiceExerciseView.className = 'view hidden';
            
            practiceExerciseView.innerHTML = `
                <div class="content-area">
                    <div class="page-title">
                        <h1>Practice Exercise</h1>
                        <p>Solve the exercise to improve your skills</p>
                    </div>
                    
                    <div class="practice-exercise-container">
                        <div class="practice-info card">
                            <div class="card-header">
                                <h2 id="exercise-title">Exercise</h2>
                                <div>
                                    <span id="exercise-difficulty" class="badge">Medium</span>
                                    <span id="exercise-type" class="badge">Tactical</span>
                                </div>
                            </div>
                            <div class="card-body">
                                <p id="exercise-description">Find the best move in this position.</p>
                                <div class="exercise-progress">
                                    <div class="progress-bar">
                                        <div id="exercise-progress-value" class="progress-value" style="width: 0%"></div>
                                    </div>
                                    <div class="progress-label">
                                        <span>Progress:</span>
                                        <span id="exercise-progress-text">0/0</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="practice-board-container">
                            <div id="practice-board" class="chess-board-container"></div>
                            <div class="practice-controls">
                                <button id="hint-button" class="btn">Hint</button>
                                <button id="solution-button" class="btn">Show Solution</button>
                                <button id="next-button" class="btn">Next Exercise</button>
                            </div>
                        </div>
                        
                        <div class="practice-results card">
                            <div class="card-header">
                                <h2>Your Progress</h2>
                            </div>
                            <div class="card-body">
                                <div class="practice-stats">
                                    <div class="practice-stat">
                                        <span class="practice-stat-label">Completed:</span>
                                        <span id="practice-completed" class="practice-stat-value">0/0</span>
                                    </div>
                                    <div class="practice-stat">
                                        <span class="practice-stat-label">Correct:</span>
                                        <span id="practice-correct" class="practice-stat-value">0</span>
                                    </div>
                                    <div class="practice-stat">
                                        <span class="practice-stat-label">Incorrect:</span>
                                        <span id="practice-incorrect" class="practice-stat-value">0</span>
                                    </div>
                                </div>
                                <div id="hint-container" class="hint-container hidden">
                                    <h3>Hint</h3>
                                    <p id="hint-text"></p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(practiceExerciseView);
            
            // Initialize practice board
            this.initializePracticeBoard();
            
            // Set up event listeners for practice controls
            document.getElementById('hint-button').addEventListener('click', () => {
                this.showHint();
            });
            
            document.getElementById('solution-button').addEventListener('click', () => {
                this.showSolution();
            });
            
            document.getElementById('next-button').addEventListener('click', () => {
                this.nextExercise();
            });
        }
        
        // Update exercise information
        this.updateExerciseInfo();
    },
    
    // Initialize practice board
    initializePracticeBoard: function() {
        const boardContainer = document.getElementById('practice-board');
        if (!boardContainer) return;
        
        // Create a new chess board for practice
        this.practiceBoard = new ChessBoard('practice-board', {
            size: 400,
            showControls: false,
            onMove: this.handlePracticeMove.bind(this)
        });
    },
    
    // Update exercise information
    updateExerciseInfo: function() {
        const session = this.state.practiceSession;
        if (!session || !session.exercises || session.exercises.length === 0) return;
        
        const currentExercise = session.exercises[session.current_exercise_index];
        
        // Update exercise title and info
        document.getElementById('exercise-title').textContent = `Exercise ${session.current_exercise_index + 1}`;
        document.getElementById('exercise-difficulty').textContent = currentExercise.difficulty;
        document.getElementById('exercise-type').textContent = currentExercise.type.replace('_', ' ');
        document.getElementById('exercise-description').textContent = currentExercise.description;
        
        // Update progress
        const progressValue = (session.current_exercise_index / session.exercises.length) * 100;
        document.getElementById('exercise-progress-value').style.width = `${progressValue}%`;
        document.getElementById('exercise-progress-text').textContent = `${session.current_exercise_index + 1}/${session.exercises.length}`;
        
        // Update stats
        document.getElementById('practice-completed').textContent = `${session.current_exercise_index}/${session.exercises.length}`;
        document.getElementById('practice-correct').textContent = session.results.correct;
        document.getElementById('practice-incorrect').textContent = session.results.incorrect;
        
        // Hide hint
        document.getElementById('hint-container').classList.add('hidden');
        
        // Set board position
        if (this.practiceBoard) {
            this.practiceBoard.setFen(currentExercise.position);
        }
    },
    
    // Handle practice move
    handlePracticeMove: function(move) {
        const session = this.state.practiceSession;
        if (!session || !session.exercises) return;
        
        const currentExercise = session.exercises[session.current_exercise_index];
        
        // Check if the move is correct
        const isCorrect = currentExercise.correct_moves.includes(move.from + move.to) || 
                         currentExercise.correct_moves.includes(move.to);
        
        // Update exercise result
        currentExercise.completed = true;
        currentExercise.result = isCorrect ? 'correct' : 'incorrect';
        
        // Update session results
        if (isCorrect) {
            session.results.correct++;
        } else {
            session.results.incorrect++;
        }
        
        // Update user statistics
        this.state.currentUser.statistics.puzzles_solved++;
        
        // Save user data
        this.saveUserData();
        
        // Show feedback
        this.showExerciseFeedback(isCorrect);
    },
    
    // Show exercise feedback
    showExerciseFeedback: function(isCorrect) {
        // Create a feedback overlay
        const feedbackOverlay = document.createElement('div');
        feedbackOverlay.className = 'feedback-overlay';
        feedbackOverlay.innerHTML = `
            <div class="feedback-content ${isCorrect ? 'correct' : 'incorrect'}">
                <div class="feedback-icon">
                    <i class="fas fa-${isCorrect ? 'check' : 'times'}"></i>
                </div>
                <h2>${isCorrect ? 'Correct!' : 'Incorrect'}</h2>
                <p>${isCorrect ? 'Well done!' : 'Try again or see the solution.'}</p>
                <button class="btn next-button">Next Exercise</button>
            </div>
        `;
        
        document.body.appendChild(feedbackOverlay);
        
        // Add event listener to next button
        feedbackOverlay.querySelector('.next-button').addEventListener('click', () => {
            feedbackOverlay.remove();
            this.nextExercise();
        });
    },
    
    // Show hint
    showHint: function() {
        const session = this.state.practiceSession;
        if (!session || !session.exercises) return;
        
        const currentExercise = session.exercises[session.current_exercise_index];
        
        // Get a random hint
        const hint = currentExercise.hints[Math.floor(Math.random() * currentExercise.hints.length)];
        
        // Show hint container
        const hintContainer = document.getElementById('hint-container');
        const hintText = document.getElementById('hint-text');
        
        hintContainer.classList.remove('hidden');
        hintText.textContent = hint;
    },
    
    // Show solution
    showSolution: function() {
        const session = this.state.practiceSession;
        if (!session || !session.exercises) return;
        
        const currentExercise = session.exercises[session.current_exercise_index];
        
        // Mark as completed but incorrect
        if (!currentExercise.completed) {
            currentExercise.completed = true;
            currentExercise.result = 'skipped';
            session.results.skipped++;
            
            // Save user data
            this.saveUserData();
        }
        
        // Show the solution
        alert(`Solution: ${currentExercise.correct_moves.join(' or ')}`);
    },
    
    // Move to next exercise
    nextExercise: function() {
        const session = this.state.practiceSession;
        if (!session || !session.exercises) return;
        
        // Move to next exercise
        session.current_exercise_index++;
        
        // Check if we've completed all exercises
        if (session.current_exercise_index >= session.exercises.length) {
            this.completePracticeSession();
        } else {
            // Update exercise info
            this.updateExerciseInfo();
        }
    },
    
    // Complete practice session
    completePracticeSession: function() {
        const session = this.state.practiceSession;
        
        // Mark session as completed
        session.completed = true;
        
        // Save user data
        this.saveUserData();
        
        // Show completion message
        alert(`Practice session completed!\nCorrect: ${session.results.correct}\nIncorrect: ${session.results.incorrect}\nSkipped: ${session.results.skipped}`);
        
        // Return to practice view
        this.navigateTo('practice');
    },
    
    // Handle board move (for analysis)
    handleBoardMove: function(move) {
        console.log('Board move:', move);
    },
    
    // Handle board selection
    handleBoardSelect: function(square) {
        console.log('Square selected:', square);
    }
};
