/**
 * Chess Board Component for Chess Coach Application
 * Provides an interactive chess board with move validation and visualization
 */

class ChessBoard {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        if (!this.container) {
            throw new Error(`Container with ID "${containerId}" not found`);
        }
        
        // Default options
        this.options = {
            size: 400,
            lightSquareColor: '#f0d9b5',
            darkSquareColor: '#b58863',
            highlightColor: 'rgba(255, 255, 0, 0.5)',
            selectedColor: 'rgba(0, 255, 0, 0.3)',
            lastMoveColor: 'rgba(0, 0, 255, 0.2)',
            orientation: 'white',
            draggable: true,
            showCoordinates: true,
            showLegalMoves: true,
            pieceTheme: 'standard',
            position: 'start',
            ...options
        };
        
        // State variables
        this.board = null;
        this.selectedSquare = null;
        this.legalMoves = [];
        this.moveHistory = [];
        this.currentPosition = 'start';
        this.orientation = this.options.orientation;
        this.pieceImages = {};
        
        // Event callbacks
        this.onMove = options.onMove || (() => {});
        this.onSelect = options.onSelect || (() => {});
        
        // Initialize the board
        this.init();
    }
    
    init() {
        // Create the board container
        this.boardElement = document.createElement('div');
        this.boardElement.className = 'chess-board';
        this.boardElement.style.width = `${this.options.size}px`;
        this.boardElement.style.height = `${this.options.size}px`;
        this.boardElement.style.position = 'relative';
        this.boardElement.style.display = 'grid';
        this.boardElement.style.gridTemplateColumns = 'repeat(8, 1fr)';
        this.boardElement.style.gridTemplateRows = 'repeat(8, 1fr)';
        this.boardElement.style.border = '2px solid #333';
        this.boardElement.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
        
        // Clear the container and add the board
        this.container.innerHTML = '';
        this.container.appendChild(this.boardElement);
        
        // Load piece images
        this.loadPieceImages();
        
        // Create the squares
        this.createSquares();
        
        // Set up the initial position
        this.setPosition(this.options.position);
        
        // Add event listeners
        if (this.options.draggable) {
            this.setupDragAndDrop();
        } else {
            this.setupClickHandlers();
        }
        
        // Create controls if needed
        if (this.options.showControls) {
            this.createControls();
        }
    }
    
    loadPieceImages() {
        const pieces = ['p', 'n', 'b', 'r', 'q', 'k'];
        const colors = ['w', 'b'];
        
        colors.forEach(color => {
            pieces.forEach(piece => {
                const img = new Image();
                img.src = `/static/img/pieces/${this.options.pieceTheme}/${color}${piece}.png`;
                this.pieceImages[`${color}${piece}`] = img;
            });
        });
    }
    
    createSquares() {
        const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        const ranks = ['1', '2', '3', '4', '5', '6', '7', '8'];
        
        // Clear existing squares
        this.boardElement.innerHTML = '';
        
        // Create squares based on orientation
        const orderedFiles = this.orientation === 'white' ? files : [...files].reverse();
        const orderedRanks = this.orientation === 'white' ? [...ranks].reverse() : ranks;
        
        for (let rankIndex = 0; rankIndex < 8; rankIndex++) {
            const rank = orderedRanks[rankIndex];
            
            for (let fileIndex = 0; fileIndex < 8; fileIndex++) {
                const file = orderedFiles[fileIndex];
                const squareName = file + rank;
                const isLight = (fileIndex + rankIndex) % 2 === 0;
                
                const square = document.createElement('div');
                square.className = `square ${isLight ? 'light' : 'dark'} square-${squareName}`;
                square.dataset.square = squareName;
                square.style.backgroundColor = isLight ? this.options.lightSquareColor : this.options.darkSquareColor;
                square.style.position = 'relative';
                
                // Add coordinates if enabled
                if (this.options.showCoordinates) {
                    if (fileIndex === 0) {
                        const rankCoord = document.createElement('div');
                        rankCoord.className = 'coordinate rank';
                        rankCoord.textContent = rank;
                        rankCoord.style.position = 'absolute';
                        rankCoord.style.left = '2px';
                        rankCoord.style.top = '2px';
                        rankCoord.style.fontSize = '12px';
                        rankCoord.style.color = isLight ? '#b58863' : '#f0d9b5';
                        rankCoord.style.pointerEvents = 'none';
                        square.appendChild(rankCoord);
                    }
                    
                    if (rankIndex === 7) {
                        const fileCoord = document.createElement('div');
                        fileCoord.className = 'coordinate file';
                        fileCoord.textContent = file;
                        fileCoord.style.position = 'absolute';
                        fileCoord.style.right = '2px';
                        fileCoord.style.bottom = '2px';
                        fileCoord.style.fontSize = '12px';
                        fileCoord.style.color = isLight ? '#b58863' : '#f0d9b5';
                        fileCoord.style.pointerEvents = 'none';
                        square.appendChild(fileCoord);
                    }
                }
                
                this.boardElement.appendChild(square);
            }
        }
    }
    
    setupClickHandlers() {
        this.boardElement.addEventListener('click', (event) => {
            const square = event.target.closest('.square');
            if (!square) return;
            
            const squareName = square.dataset.square;
            
            // If a square is already selected
            if (this.selectedSquare) {
                // If clicking the same square, deselect it
                if (this.selectedSquare === squareName) {
                    this.deselectSquare();
                    return;
                }
                
                // Check if the move is legal
                if (this.isLegalMove(this.selectedSquare, squareName)) {
                    this.makeMove(this.selectedSquare, squareName);
                } else {
                    // If the clicked square has a piece of the same color, select it instead
                    const piece = this.getPieceOnSquare(squareName);
                    if (piece && this.isPieceOfCurrentTurn(piece)) {
                        this.selectSquare(squareName);
                    } else {
                        this.deselectSquare();
                    }
                }
            } else {
                // Select the square if it has a piece of the current turn
                const piece = this.getPieceOnSquare(squareName);
                if (piece && this.isPieceOfCurrentTurn(piece)) {
                    this.selectSquare(squareName);
                }
            }
        });
    }
    
    setupDragAndDrop() {
        let draggedPiece = null;
        let draggedSquare = null;
        let dragElement = null;
        
        // Create a drag element
        dragElement = document.createElement('div');
        dragElement.className = 'dragged-piece';
        dragElement.style.position = 'absolute';
        dragElement.style.pointerEvents = 'none';
        dragElement.style.zIndex = '1000';
        dragElement.style.opacity = '0.8';
        dragElement.style.display = 'none';
        document.body.appendChild(dragElement);
        
        // Mouse down - start drag
        this.boardElement.addEventListener('mousedown', (event) => {
            const square = event.target.closest('.square');
            if (!square) return;
            
            const squareName = square.dataset.square;
            const piece = this.getPieceOnSquare(squareName);
            
            if (piece && this.isPieceOfCurrentTurn(piece)) {
                draggedPiece = piece;
                draggedSquare = squareName;
                
                // Show the piece being dragged
                dragElement.style.display = 'block';
                dragElement.style.width = `${square.offsetWidth}px`;
                dragElement.style.height = `${square.offsetHeight}px`;
                dragElement.style.backgroundImage = `url(${this.pieceImages[piece].src})`;
                dragElement.style.backgroundSize = 'contain';
                dragElement.style.backgroundRepeat = 'no-repeat';
                dragElement.style.backgroundPosition = 'center';
                
                // Position at mouse cursor
                dragElement.style.left = `${event.clientX - square.offsetWidth / 2}px`;
                dragElement.style.top = `${event.clientY - square.offsetHeight / 2}px`;
                
                // Highlight legal moves
                if (this.options.showLegalMoves) {
                    this.legalMoves = this.getLegalMovesFromSquare(squareName);
                    this.highlightLegalMoves(this.legalMoves);
                }
                
                // Hide the piece on the original square
                const pieceElement = square.querySelector('.piece');
                if (pieceElement) {
                    pieceElement.style.opacity = '0.3';
                }
                
                event.preventDefault();
            }
        });
        
        // Mouse move - update drag position
        document.addEventListener('mousemove', (event) => {
            if (draggedPiece) {
                dragElement.style.left = `${event.clientX - parseInt(dragElement.style.width) / 2}px`;
                dragElement.style.top = `${event.clientY - parseInt(dragElement.style.height) / 2}px`;
                event.preventDefault();
            }
        });
        
        // Mouse up - end drag and make move if valid
        document.addEventListener('mouseup', (event) => {
            if (draggedPiece) {
                // Get the square under the cursor
                const boardRect = this.boardElement.getBoundingClientRect();
                const squareSize = boardRect.width / 8;
                
                // Check if the drop is within the board
                if (
                    event.clientX >= boardRect.left &&
                    event.clientX < boardRect.right &&
                    event.clientY >= boardRect.top &&
                    event.clientY < boardRect.bottom
                ) {
                    // Calculate the square coordinates
                    const fileIndex = Math.floor((event.clientX - boardRect.left) / squareSize);
                    const rankIndex = Math.floor((event.clientY - boardRect.top) / squareSize);
                    
                    // Convert to square name based on orientation
                    let targetSquare;
                    if (this.orientation === 'white') {
                        const file = String.fromCharCode(97 + fileIndex);
                        const rank = 8 - rankIndex;
                        targetSquare = file + rank;
                    } else {
                        const file = String.fromCharCode(97 + (7 - fileIndex));
                        const rank = rankIndex + 1;
                        targetSquare = file + rank;
                    }
                    
                    // Make the move if legal
                    if (this.isLegalMove(draggedSquare, targetSquare)) {
                        this.makeMove(draggedSquare, targetSquare);
                    }
                }
                
                // Reset drag state
                dragElement.style.display = 'none';
                draggedPiece = null;
                
                // Restore opacity of the original piece
                const originalSquare = this.boardElement.querySelector(`.square-${draggedSquare}`);
                if (originalSquare) {
                    const pieceElement = originalSquare.querySelector('.piece');
                    if (pieceElement) {
                        pieceElement.style.opacity = '1';
                    }
                }
                
                // Clear highlights
                this.clearHighlights();
                draggedSquare = null;
                
                event.preventDefault();
            }
        });
    }
    
    createControls() {
        const controlsContainer = document.createElement('div');
        controlsContainer.className = 'board-controls';
        controlsContainer.style.display = 'flex';
        controlsContainer.style.justifyContent = 'center';
        controlsContainer.style.marginTop = '10px';
        
        // First move button
        const firstButton = document.createElement('button');
        firstButton.innerHTML = '&#x23EE;'; // Unicode for "first"
        firstButton.title = 'First move';
        firstButton.addEventListener('click', () => this.navigateToMove(0));
        
        // Previous move button
        const prevButton = document.createElement('button');
        prevButton.innerHTML = '&#x23EA;'; // Unicode for "previous"
        prevButton.title = 'Previous move';
        prevButton.addEventListener('click', () => this.navigateToPreviousMove());
        
        // Next move button
        const nextButton = document.createElement('button');
        nextButton.innerHTML = '&#x23E9;'; // Unicode for "next"
        nextButton.title = 'Next move';
        nextButton.addEventListener('click', () => this.navigateToNextMove());
        
        // Last move button
        const lastButton = document.createElement('button');
        lastButton.innerHTML = '&#x23ED;'; // Unicode for "last"
        lastButton.title = 'Last move';
        lastButton.addEventListener('click', () => this.navigateToMove(this.moveHistory.length));
        
        // Flip board button
        const flipButton = document.createElement('button');
        flipButton.innerHTML = '&#x21C4;'; // Unicode for "flip"
        flipButton.title = 'Flip board';
        flipButton.addEventListener('click', () => this.flipBoard());
        
        // Add buttons to container
        controlsContainer.appendChild(firstButton);
        controlsContainer.appendChild(prevButton);
        controlsContainer.appendChild(nextButton);
        controlsContainer.appendChild(lastButton);
        controlsContainer.appendChild(flipButton);
        
        // Add controls to the main container
        this.container.appendChild(controlsContainer);
    }
    
    setPosition(position) {
        if (position === 'start') {
            // Standard starting position in FEN
            this.currentPosition = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';
        } else if (position === 'empty') {
            // Empty board
            this.currentPosition = '8/8/8/8/8/8/8/8 w - - 0 1';
        } else {
            // Assume FEN string
            this.currentPosition = position;
        }
        
        this.renderPosition();
    }
    
    renderPosition() {
        // Clear all pieces
        const pieceElements = this.boardElement.querySelectorAll('.piece');
        pieceElements.forEach(piece => piece.remove());
        
        // Parse FEN
        const [piecePlacement, activeColor, castling, enPassant, halfmoveClock, fullmoveNumber] = this.currentPosition.split(' ');
        
        // Place pieces according to FEN
        const ranks = piecePlacement.split('/');
        
        for (let rankIndex = 0; rankIndex < 8; rankIndex++) {
            const rank = 8 - rankIndex;
            let fileIndex = 0;
            
            for (let i = 0; i < ranks[rankIndex].length; i++) {
                const char = ranks[rankIndex][i];
                
                if (/\d/.test(char)) {
                    // Skip empty squares
                    fileIndex += parseInt(char);
                } else {
                    // Place a piece
                    const file = String.fromCharCode(97 + fileIndex);
                    const squareName = file + rank;
                    
                    // Determine piece type and color
                    const isWhite = char === char.toUpperCase();
                    const pieceType = char.toLowerCase();
                    const pieceCode = (isWhite ? 'w' : 'b') + pieceType;
                    
                    this.placePiece(squareName, pieceCode);
                    
                    fileIndex++;
                }
            }
        }
    }
    
    placePiece(square, pieceCode) {
        const squareElement = this.boardElement.querySelector(`.square-${square}`);
        if (!squareElement) return;
        
        // Create piece element
        const pieceElement = document.createElement('div');
        pieceElement.className = `piece ${pieceCode}`;
        pieceElement.dataset.piece = pieceCode;
        pieceElement.style.width = '100%';
        pieceElement.style.height = '100%';
        pieceElement.style.backgroundImage = `url(${this.pieceImages[pieceCode].src})`;
        pieceElement.style.backgroundSize = 'contain';
        pieceElement.style.backgroundRepeat = 'no-repeat';
        pieceElement.style.backgroundPosition = 'center';
        pieceElement.style.position = 'absolute';
        pieceElement.style.top = '0';
        pieceElement.style.left = '0';
        
        squareElement.appendChild(pieceElement);
    }
    
    selectSquare(square) {
        this.deselectSquare();
        
        this.selectedSquare = square;
        
        // Highlight the selected square
        const squareElement = this.boardElement.querySelector(`.square-${square}`);
        if (squareElement) {
            squareElement.style.backgroundColor = this.options.selectedColor;
        }
        
        // Highlight legal moves
        if (this.options.showLegalMoves) {
            this.legalMoves = this.getLegalMovesFromSquare(square);
            this.highlightLegalMoves(this.legalMoves);
        }
        
        // Trigger onSelect callback
        this.onSelect(square);
    }
    
    deselectSquare() {
        if (this.selectedSquare) {
            // Reset square color
            const squareElement = this.boardElement.querySelector(`.square-${this.selectedSquare}`);
            if (squareElement) {
                const isLight = (this.selectedSquare.charCodeAt(0) - 97 + (8 - parseInt(this.selectedSquare[1]))) % 2 === 0;
                squareElement.style.backgroundColor = isLight ? this.options.lightSquareColor : this.options.darkSquareColor;
            }
            
            // Clear legal move highlights
            this.clearHighlights();
            
            this.selectedSquare = null;
        }
    }
    
    highlightLegalMoves(moves) {
        moves.forEach(move => {
            const squareElement = this.boardElement.querySelector(`.square-${move.to}`);
            if (squareElement) {
                // Create highlight element
                const highlight = document.createElement('div');
                highlight.className = 'move-highlight';
                highlight.style.position = 'absolute';
                highlight.style.top = '0';
                highlight.style.left = '0';
                highlight.style.width = '100%';
                highlight.style.height = '100%';
                highlight.style.pointerEvents = 'none';
                
                // If the target square has a piece (capture), show a different highlight
                const hasPiece = squareElement.querySelector('.piece');
                if (hasPiece) {
                    highlight.style.border = `2px solid ${this.options.highlightColor}`;
                    highlight.style.borderRadius = '50%';
                } else {
                    // For empty squares, show a dot
                    highlight.style.display = 'flex';
                    highlight.style.justifyContent = 'center';
                    highlight.style.alignItems = 'center';
                    
                    const dot = document.createElement('div');
                    dot.style.width = '30%';
                    dot.style.height = '30%';
                    dot.style.borderRadius = '50%';
                    dot.style.backgroundColor = this.options.highlightColor;
                    
                    highlight.appendChild(dot);
                }
                
                squareElement.appendChild(highlight);
            }
        });
    }
    
    clearHighlights() {
        const highlights = this.boardElement.querySelectorAll('.move-highlight');
        highlights.forEach(highlight => highlight.remove());
    }
    
    makeMove(from, to) {
        // Get the piece being moved
        const piece = this.getPieceOnSquare(from);
        if (!piece) return false;
        
        // Record the move
        const move = {
            from,
            to,
            piece,
            captured: this.getPieceOnSquare(to),
            // Additional move data would be added here (e.g., promotion, castling, en passant)
        };
        
        // Update the board
        this.removePiece(from);
        this.removePiece(to);
        this.placePiece(to, piece);
        
        // Highlight the move
        this.highlightLastMove(from, to);
        
        // Add to move history
        this.moveHistory.push(move);
        
        // Deselect the square
        this.deselectSquare();
        
        // Trigger onMove callback
        this.onMove(move);
        
        return true;
    }
    
    highlightLastMove(from, to) {
        // Clear previous highlights
        const lastMoveHighlights = this.boardElement.querySelectorAll('.last-move');
        lastMoveHighlights.forEach(highlight => {
            const square = highlight.closest('.square');
            if (square) {
                const squareName = square.dataset.square;
                const isLight = (squareName.charCodeAt(0) - 97 + (8 - parseInt(squareName[1]))) % 2 === 0;
                square.style.backgroundColor = isLight ? this.options.lightSquareColor : this.options.darkSquareColor;
            }
            highlight.remove();
        });
        
        // Highlight the from and to squares
        [from, to].forEach(square => {
            const squareElement = this.boardElement.querySelector(`.square-${square}`);
            if (squareElement) {
                const highlight = document.createElement('div');
                highlight.className = 'last-move';
                highlight.style.position = 'absolute';
                highlight.style.top = '0';
                highlight.style.left = '0';
                highlight.style.width = '100%';
                highlight.style.height = '100%';
                highlight.style.backgroundColor = this.options.lastMoveColor;
                highlight.style.pointerEvents = 'none';
                
                squareElement.style.backgroundColor = this.options.lastMoveColor;
            }
        });
    }
    
    getPieceOnSquare(square) {
        const squareElement = this.boardElement.querySelector(`.square-${square}`);
        if (!squareElement) return null;
        
        const pieceElement = squareElement.querySelector('.piece');
        return pieceElement ? pieceElement.dataset.piece : null;
    }
    
    removePiece(square) {
        const squareElement = this.boardElement.querySelector(`.square-${square}`);
        if (!squareElement) return;
        
        const pieceElement = squareElement.querySelector('.piece');
        if (pieceElement) {
            pieceElement.remove();
        }
    }
    
    isPieceOfCurrentTurn(piece) {
        // In a real implementation, this would check against the current turn
        // For now, we'll just check if the piece is white (assuming white moves first)
        const [piecePlacement, activeColor] = this.currentPosition.split(' ');
        return (activeColor === 'w' && piece[0] === 'w') || (activeColor === 'b' && piece[0] === 'b');
    }
    
    isLegalMove(from, to) {
        // In a real implementation, this would check against the chess rules
        // For now, we'll just check if the move is in the legal moves list
        return this.legalMoves.some(move => move.from === from && move.to === to);
    }
    
    getLegalMovesFromSquare(square) {
        // In a real implementation, this would calculate legal moves based on chess rules
        // For now, we'll return some dummy moves
        const piece = this.getPieceOnSquare(square);
        if (!piece) return [];
        
        // Simple moves for demonstration
        const moves = [];
        const file = square.charCodeAt(0) - 97; // 'a' -> 0, 'b' -> 1, etc.
        const rank = parseInt(square[1]);
        
        // Different move patterns based on piece type
        switch (piece[1]) {
            case 'p': // Pawn
                const direction = piece[0] === 'w' ? 1 : -1;
                const startRank = piece[0] === 'w' ? 2 : 7;
                
                // Forward move
                if (rank + direction >= 1 && rank + direction <= 8) {
                    const forwardSquare = String.fromCharCode(97 + file) + (rank + direction);
                    if (!this.getPieceOnSquare(forwardSquare)) {
                        moves.push({ from: square, to: forwardSquare });
                        
                        // Double move from starting position
                        if (rank === startRank) {
                            const doubleSquare = String.fromCharCode(97 + file) + (rank + 2 * direction);
                            if (!this.getPieceOnSquare(doubleSquare)) {
                                moves.push({ from: square, to: doubleSquare });
                            }
                        }
                    }
                }
                
                // Captures
                for (let offset of [-1, 1]) {
                    if (file + offset >= 0 && file + offset < 8 && rank + direction >= 1 && rank + direction <= 8) {
                        const captureSquare = String.fromCharCode(97 + file + offset) + (rank + direction);
                        const targetPiece = this.getPieceOnSquare(captureSquare);
                        if (targetPiece && targetPiece[0] !== piece[0]) {
                            moves.push({ from: square, to: captureSquare });
                        }
                    }
                }
                break;
                
            case 'n': // Knight
                const knightOffsets = [
                    { file: 1, rank: 2 }, { file: 2, rank: 1 },
                    { file: 2, rank: -1 }, { file: 1, rank: -2 },
                    { file: -1, rank: -2 }, { file: -2, rank: -1 },
                    { file: -2, rank: 1 }, { file: -1, rank: 2 }
                ];
                
                for (const offset of knightOffsets) {
                    const newFile = file + offset.file;
                    const newRank = rank + offset.rank;
                    
                    if (newFile >= 0 && newFile < 8 && newRank >= 1 && newRank <= 8) {
                        const targetSquare = String.fromCharCode(97 + newFile) + newRank;
                        const targetPiece = this.getPieceOnSquare(targetSquare);
                        
                        if (!targetPiece || targetPiece[0] !== piece[0]) {
                            moves.push({ from: square, to: targetSquare });
                        }
                    }
                }
                break;
                
            case 'b': // Bishop
            case 'r': // Rook
            case 'q': // Queen
                const directions = [];
                
                // Bishop moves diagonally
                if (piece[1] === 'b' || piece[1] === 'q') {
                    directions.push({ file: 1, rank: 1 });
                    directions.push({ file: 1, rank: -1 });
                    directions.push({ file: -1, rank: -1 });
                    directions.push({ file: -1, rank: 1 });
                }
                
                // Rook moves horizontally and vertically
                if (piece[1] === 'r' || piece[1] === 'q') {
                    directions.push({ file: 0, rank: 1 });
                    directions.push({ file: 1, rank: 0 });
                    directions.push({ file: 0, rank: -1 });
                    directions.push({ file: -1, rank: 0 });
                }
                
                for (const direction of directions) {
                    for (let i = 1; i < 8; i++) {
                        const newFile = file + i * direction.file;
                        const newRank = rank + i * direction.rank;
                        
                        if (newFile < 0 || newFile >= 8 || newRank < 1 || newRank > 8) {
                            break;
                        }
                        
                        const targetSquare = String.fromCharCode(97 + newFile) + newRank;
                        const targetPiece = this.getPieceOnSquare(targetSquare);
                        
                        if (!targetPiece) {
                            moves.push({ from: square, to: targetSquare });
                        } else {
                            if (targetPiece[0] !== piece[0]) {
                                moves.push({ from: square, to: targetSquare });
                            }
                            break;
                        }
                    }
                }
                break;
                
            case 'k': // King
                const kingOffsets = [
                    { file: 0, rank: 1 }, { file: 1, rank: 1 },
                    { file: 1, rank: 0 }, { file: 1, rank: -1 },
                    { file: 0, rank: -1 }, { file: -1, rank: -1 },
                    { file: -1, rank: 0 }, { file: -1, rank: 1 }
                ];
                
                for (const offset of kingOffsets) {
                    const newFile = file + offset.file;
                    const newRank = rank + offset.rank;
                    
                    if (newFile >= 0 && newFile < 8 && newRank >= 1 && newRank <= 8) {
                        const targetSquare = String.fromCharCode(97 + newFile) + newRank;
                        const targetPiece = this.getPieceOnSquare(targetSquare);
                        
                        if (!targetPiece || targetPiece[0] !== piece[0]) {
                            moves.push({ from: square, to: targetSquare });
                        }
                    }
                }
                
                // Castling would be added here in a full implementation
                break;
        }
        
        return moves;
    }
    
    navigateToMove(moveIndex) {
        // Reset to starting position
        this.setPosition(this.options.position);
        
        // Apply moves up to the specified index
        for (let i = 0; i < moveIndex && i < this.moveHistory.length; i++) {
            const move = this.moveHistory[i];
            this.removePiece(move.from);
            this.removePiece(move.to);
            this.placePiece(move.to, move.piece);
        }
        
        // Highlight the last move if any
        if (moveIndex > 0 && moveIndex <= this.moveHistory.length) {
            const lastMove = this.moveHistory[moveIndex - 1];
            this.highlightLastMove(lastMove.from, lastMove.to);
        }
    }
    
    navigateToPreviousMove() {
        // Find the current position in the move history
        const currentIndex = this.getCurrentMoveIndex();
        if (currentIndex > 0) {
            this.navigateToMove(currentIndex - 1);
        }
    }
    
    navigateToNextMove() {
        // Find the current position in the move history
        const currentIndex = this.getCurrentMoveIndex();
        if (currentIndex < this.moveHistory.length) {
            this.navigateToMove(currentIndex + 1);
        }
    }
    
    getCurrentMoveIndex() {
        // This is a simplified implementation
        // In a real app, you would track the current position more accurately
        return this.moveHistory.length;
    }
    
    flipBoard() {
        this.orientation = this.orientation === 'white' ? 'black' : 'white';
        this.createSquares();
        this.renderPosition();
        
        // Highlight the last move if any
        if (this.moveHistory.length > 0) {
            const lastMove = this.moveHistory[this.moveHistory.length - 1];
            this.highlightLastMove(lastMove.from, lastMove.to);
        }
    }
    
    // Public API methods
    
    /**
     * Make a move programmatically
     * @param {string} from - Starting square (e.g., 'e2')
     * @param {string} to - Target square (e.g., 'e4')
     * @returns {boolean} - Whether the move was successful
     */
    move(from, to) {
        if (this.isLegalMove(from, to)) {
            return this.makeMove(from, to);
        }
        return false;
    }
    
    /**
     * Set a new position
     * @param {string} fen - Position in FEN notation
     */
    setFen(fen) {
        this.setPosition(fen);
    }
    
    /**
     * Get the current position
     * @returns {string} - Current position in FEN notation
     */
    getFen() {
        return this.currentPosition;
    }
    
    /**
     * Get the piece on a square
     * @param {string} square - Square name (e.g., 'e4')
     * @returns {string|null} - Piece code (e.g., 'wp' for white pawn) or null if empty
     */
    getPiece(square) {
        return this.getPieceOnSquare(square);
    }
    
    /**
     * Clear the board
     */
    clear() {
        this.setPosition('empty');
    }
    
    /**
     * Reset to starting position
     */
    reset() {
        this.setPosition('start');
        this.moveHistory = [];
    }
}

// Export the ChessBoard class
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChessBoard;
}
