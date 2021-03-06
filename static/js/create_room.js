const socket = io();

const game_message = document.getElementById('game_message');
const main_board = document.getElementById('main_board');

// only to be manipulated from move()
let playerInRoom = 0;
let blueStoneCount = 0;
let greyStoneCount = 0;
let blueStoneTurn = 1;
let isPlayerBlue = -1;
let isPlayerColourAssigned = 0;
let gridMatrix;
let isGameOver = 0;
let isRoundOver = 0;

// ------------------------------------------------------------------------------------------
// page setup on load

window.onload = onLoadSetup();

function onLoadSetup() {
    setup()
    additionalSetup()
}

function additionalSetup() {
    socket.emit('request_private_room_code');

    window.onbeforeunload = () => {
        socket.emit('disconnect_from_private_room');
    };

    window.onpagehide = () => {
        socket.emit('disconnect_from_private_room');
    };
}

// this function fills the grid with div elements with an id corresponding to their coordinates
// an event listener is also added to the div elements to place the stones when they are clicked
// gridMatrix is initialized with a default value of -1
function setup() {
    for (let y = 1; y <= 36; y++) {
        for (let x = 1; x <= 36; x++) {

            const click_box = document.createElement('div');
            click_box.id = x + "/" + y;

            let x_end = x + 2;
            let y_end = y + 2;

            click_box.style.gridColumnStart = x;
            click_box.style.gridColumnEnd = x_end;
            click_box.style.gridRowStart = y;
            click_box.style.gridRowEnd = y_end;

            click_box.addEventListener('click', function() {
                let x_start = parseInt(this.id.substring(0, this.id.indexOf('/')), 10);
                let y_start = parseInt(this.id.substring(this.id.indexOf('/') + 1, 10));

                move(isPlayerBlue, x_start, y_start);
            });

            main_board.append(click_box);
        }
    }

    gridMatrix = new Array(17);
    for (let i = 0; i < 17; i++) {
        gridMatrix[i] = new Array(17);
        for (let j = 0; j < 17; j++) {
            gridMatrix[i][j] = -1;
        }
    }
}

// ------------------------------------------------------------------------------------------
// SocketIO

socket.on('placement_response_private_room', function(json) {
    move(json.c, json.x, json.y)

    if (json.c != isPlayerBlue && !isGameOver && !isRoundOver) {
        game_message.style.color = "orange";
        game_message.style.borderColor = "orange";
        game_message.innerText = "Your turn!";
    }
});

socket.on('game_session_valid_response_private_room', function(json) {
    setTimeout(() => {
        if (!json.session_valid && !isGameOver) {
            game_message.style.color = "red";
            game_message.style.borderColor = "red";
            if (json.session_valid === 0) {
                game_message.innerText = "You were disconnected.";
            } else {
                game_message.innerText = "Opponent left the game :(";
            }
            isGameOver = 1;
            socket.emit('disconnect_from_private_room');
            setTimeout(() => {
                window.location.href = 'https://omok-game.herokuapp.com';
            }, 5000);      
        }
    }, 500);
});

socket.on('private_room_code', function(json) {
    document.getElementById('room_code_message').innerText = 
        "The room code is '" + json.room_code + "'.";
});

socket.on('start_game_private_room', function() {
    document.getElementById('room_code_view').style.display = 'none';
    document.getElementById('game_view').style.display = 'block';
});

function showRealTimeTurn() {
    if (isPlayerBlue != blueStoneTurn) {
        game_message.style.color = "black";
        game_message.style.borderColor = "black";
        game_message.innerText = "Opponent's turn!";  
    } else {
        game_message.style.color = "orange";
        game_message.style.borderColor = "orange";
        game_message.innerText = "Your turn!";
    }
}

function showTurn() {
    if (isPlayerBlue) {
        if (!isGameOver) {
            console.log("player is BLUE");
            game_message.style.color = "black";
            game_message.style.borderColor = "black";
            game_message.innerText = "You are BLUE!";
            setTimeout(() => {
                if (!isGameOver) {
                    showRealTimeTurn();
                }
            }, 3000);
        }
    } else {
        if (!isGameOver) {
            console.log("player is GREY");
            game_message.style.color = "black";
            game_message.style.borderColor = "black";
            game_message.innerText = "You are GREY!";
            setTimeout(() => {
                if (!isGameOver) {
                    showRealTimeTurn();
                }
            }, 3000);
        }
    }
}

socket.on('player_colour_assignment', function(json) {
    isPlayerBlue = json.isPlayerBlue

    if (isPlayerBlue == 0 || isPlayerBlue == 1) {
        console.log("player colour assigned!");

        showTurn();
        isPlayerColourAssigned = 1;
    }
});

// ------------------------------------------------------------------------------------------
// main game logic handling

// check if the win condition has been reached for the player
function checkWinCondition() {
    let consecutiveStonesCount = 0;

    // check horizontal win condition
    for (let i = 0; i < 17; i++) {
        for (let j = 0; j < 17; j++) {
            if (gridMatrix[i][j] === isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }
        }
        consecutiveStonesCount = 0;
    }

    // check vertical win condition
    for (let j = 0; j < 17; j++) {
        for (let i = 0; i < 17; i++) {
            if (gridMatrix[i][j] === isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }
        }
        consecutiveStonesCount = 0;
    }

    // check diagonal win condition
    for (let x = 0; x <= 12; x++) {
        for (let i = x, j = 0; i < 17 && j < 17; i++, j++) {
            if (gridMatrix[i][j] === isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    for (let y = 1; y <= 12; y++) {
        for (let i = 0, j = y; i < 17 && j < 17; i++, j++) {
            if (gridMatrix[i][j] === isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    for (let x = 16; x >= 4; x--) {
        for (let i = x, j = 0; i >= 0 && j < 17; i--, j++) {
            if (gridMatrix[i][j] === isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    for (let y = 1; y <= 12; y++) {
        for (let i = 16, j = y; i >= 0 && j < 17; i--, j++) {
            if (gridMatrix[i][j] === isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    return false;
}

// check if the lose condition has been reached for the player
function checkLoseCondition() {
    let consecutiveStonesCount = 0;

    // check horizontal win condition
    for (let i = 0; i < 17; i++) {
        for (let j = 0; j < 17; j++) {
            if (gridMatrix[i][j] == !isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }
        }
        consecutiveStonesCount = 0;
    }

    // check vertical win condition
    for (let j = 0; j < 17; j++) {
        for (let i = 0; i < 17; i++) {
            if (gridMatrix[i][j] == !isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }
        }
        consecutiveStonesCount = 0;
    }

    // check diagonal win condition
    for (let x = 0; x <= 12; x++) {
        for (let i = x, j = 0; i < 17 && j < 17; i++, j++) {
            if (gridMatrix[i][j] == !isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    for (let y = 1; y <= 12; y++) {
        for (let i = 0, j = y; i < 17 && j < 17; i++, j++) {
            if (gridMatrix[i][j] == isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    for (let x = 16; x >= 4; x--) {
        for (let i = x, j = 0; i >= 0 && j < 17; i--, j++) {
            if (gridMatrix[i][j] == !isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    for (let y = 1; y <= 12; y++) {
        for (let i = 16, j = y; i >= 0 && j < 17; i--, j++) {
            if (gridMatrix[i][j] == !isPlayerBlue) {
                consecutiveStonesCount++;
                if (consecutiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consecutiveStonesCount = 0;
            }       
        }
        consecutiveStonesCount = 0;
    }

    return false;
}

function startNewRound() {
    setTimeout(() => {
        if (!isGameOver) {
            game_message.style.color = "orange";
            game_message.style.borderColor = "orange";
            game_message.innerText = "Starting new round ...";
            setTimeout(() => {
                // reset board
                if (!isGameOver) {
                    isRoundOver = 0;
                    blueStoneCount = 0;
                    greyStoneCount = 0;
                    blueStoneTurn = 1;
                    isPlayerBlue = !isPlayerBlue;
                    for (let i = 0; i < 17; i++) {
                        for (let j = 0; j < 17; j++) {
                            gridMatrix[i][j] = -1;
                        }
                    }
                    main_board.innerHTML = "";
                    setup();
                    showTurn();
                } 
            }, 3000);
        } 
    }, 3000);
}

// this function places the stone on the specified position and also 
// adds this information to gridMatrix
function move(c, x, y) {
    const stone = document.createElement('div');

    if (!isPlayerColourAssigned) {
        return;
    }

    if (isGameOver || isRoundOver) {
        return;
    }

    // return if player attempts to make move when it is not their turn
    if (c != blueStoneTurn) {
        return;
    }

    if (x <= 1 || x >= 36 || y <= 1 || y >= 36) {
        return;
    }

    if (c) {
        stone.classList.add('blueStone')
        blueStoneCount++;
        blueStoneTurn = 0;
    } else {
        stone.classList.add('greyStone')
        greyStoneCount++;
        blueStoneTurn = 1;
    }

    if (x % 2 == 0 && y % 2 == 0) {
        stone.style.gridColumnStart = x;
        stone.style.gridColumnEnd = x + 2;
        stone.style.gridRowStart = y;
        stone.style.gridRowEnd = y + 2;    
    } else if (x % 2 != 0 && y % 2 != 0) {
        stone.style.gridColumnStart = x - 1;
        stone.style.gridColumnEnd = x + 1;
        stone.style.gridRowStart = y - 1;
        stone.style.gridRowEnd = y + 1;      
    } else if (x % 2 == 0 && y % 2 != 0) {
        stone.style.gridColumnStart = x;
        stone.style.gridColumnEnd = x + 2;
        stone.style.gridRowStart = y - 1;
        stone.style.gridRowEnd = y + 1;       
    } else {
        stone.style.gridColumnStart = x - 1;
        stone.style.gridColumnEnd = x + 1;
        stone.style.gridRowStart = y;
        stone.style.gridRowEnd = y + 2;         
    }

    let xCoordinate = stone.style.gridColumnStart / 2 - 1;
    let yCoordinate = stone.style.gridRowStart / 2 - 1

    if (gridMatrix[xCoordinate][yCoordinate] === -1) {
        gridMatrix[xCoordinate][yCoordinate] = c;
        main_board.append(stone);

        game_message.style.color = "black";
        game_message.style.borderColor = "black";
        game_message.innerText = "Opponent's turn!";

        socket.emit('stone_placement_private_room', {
            c : c,
            x : x,
            y : y
        });

        if (checkWinCondition()) {
            game_message.style.color = "green";
            game_message.style.borderColor = "green";
            game_message.innerText = "You won :)";
            isRoundOver = 1;
            // automatically start new round
            startNewRound();
        } else if (checkLoseCondition()) {
            game_message.style.color = "red";
            game_message.style.borderColor = "red";
            game_message.innerText = "You lost :(";
            isRoundOver = 1;
            // automatically start new round
            startNewRound();
        }
    }
}
