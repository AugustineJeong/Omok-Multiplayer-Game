const main_board = document.getElementById('main_board');

function move(c, x, y) {
    const stone = document.createElement('div');

    if (c) {
        stone.classList.add('blueStone')
    } else {
        stone.classList.add('greyStone')
    }

    console.log(x);
    console.log(y);

    if (x % 2 != 0 || y % 2 != 0) {
        return;
    }

    stone.style.gridColumnStart = x;
    stone.style.gridColumnEnd = x + 2;
    stone.style.gridRowStart = y;
    stone.style.gridRowEnd = y + 2;

    main_board.append(stone)
}

window.onload = setup;

function setup() {
    for (let y = 0; y < 36; y++) {
        for (let x = 0; x < 36; x++) {

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
    move(0, 2, 10);
    move(1, 4, 6);
    move(0, 4, 10);
    move(1, 4, 16);
    move(0, 10, 16);
    move(1, 4, 12);
    move(0, 8, 10);
}
