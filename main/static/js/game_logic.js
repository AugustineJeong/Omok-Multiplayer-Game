const main_board = document.getElementById('main_board');

// only to be manipulated from move()
let blueStoneCount = 0;
let greyStoneCount = 0;
let blueStoneTurn = 0;
let gridMatrix;

// this is the colour assigned to the player (1 is blue, 0 is grey)
let player = 1;

// check if the win condition has been reached for the player
function checkWinCondition() {
    consectiveStonesCount = 0;

    // check horizontal win condition
    for (let i = 0; i < 17; i++) {
        for (let j = 0; j < 17; j++) {
            if (gridMatrix[i][j] === player) {
                consectiveStonesCount++;
                if (consectiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consectiveStonesCount = 0;
            }
        }
        consectiveStonesCount = 0;
    }

    // check vertical win condition
    for (let j = 0; j < 17; j++) {
        for (let i = 0; i < 17; i++) {
            if (gridMatrix[i][j] === player) {
                consectiveStonesCount++;
                if (consectiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consectiveStonesCount = 0;
            }
        }
        consectiveStonesCount = 0;
    }

    // check diagonal win condition
    for (let x = 0; x <= 12; x++) {
        for (let i = x, j = 0; i < 17 && j < 17; i++, j++) {
            if (gridMatrix[i][j] === player) {
                consectiveStonesCount++;
                if (consectiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consectiveStonesCount = 0;
            }       
        }
        consectiveStonesCount = 0;
    }

    for (let y = 1; y <= 12; y++) {
        for (let i = 0, j = y; i < 17 && j < 17; i++, j++) {
            if (gridMatrix[i][j] === player) {
                consectiveStonesCount++;
                if (consectiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consectiveStonesCount = 0;
            }       
        }
        consectiveStonesCount = 0;
    }

    for (let x = 16; x >= 4; x--) {
        for (let i = x, j = 0; i >= 0 && j < 17; i--, j++) {
            if (gridMatrix[i][j] === player) {
                consectiveStonesCount++;
                if (consectiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consectiveStonesCount = 0;
            }       
        }
        consectiveStonesCount = 0;
    }

    for (let y = 1; y <= 12; y++) {
        for (let i = 16, j = y; i >= 0 && j < 17; i--, j++) {
            if (gridMatrix[i][j] === player) {
                consectiveStonesCount++;
                if (consectiveStonesCount >= 5) {
                    return true;
                }
            } else {
                consectiveStonesCount = 0;
            }       
        }
        consectiveStonesCount = 0;
    }

    return false;
}

// this function places the stone on the specified position and also 
// adds this information to gridMatrix
function move(c, x, y) {
    const stone = document.createElement('div');

    // return if player attempts to make move when it is not their turn
    if ((c && !blueStoneTurn) || (!c && blueStoneTurn)) {
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

    if (x <= 1 || x >= 36 || y <= 1 || y >= 36) {
        return;
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
    } 
}

window.onload = setup;

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

                move(1, x_start, y_start);
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

    move(0, 2, 12);
    move(1, 4, 6);
    move(0, 4, 10);
    move(1, 4, 16);
    move(0, 10, 16);
    move(1, 4, 12);
    move(0, 8, 10);
}
