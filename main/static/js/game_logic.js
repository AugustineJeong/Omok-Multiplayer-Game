const main_board = document.getElementById('main_board');

const move = (c, x, y) => {
    const stone = document.createElement('div');

    if (c) {
        stone.classList.add('blueStone')
    } else {
        stone.classList.add('greyStone')
    }

    let x_start = (x - 1) * 2;
    let y_start = (y - 1) * 2;

    stone.style.gridRowStart = x_start;
    stone.style.gridRowEnd = x_start + 2;
    stone.style.gridColumnStart = y_start;
    stone.style.gridColumnEnd = y_start + 2;

    main_board.append(stone)
}

window.onload = () => {
    move(0, 5, 7);
    move(1, 7, 7);
    move(0, 7, 8);
}

