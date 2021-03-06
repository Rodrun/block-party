let canvas = document.getElementById("output")
let twoConfig = { width: window.width, height: window.height , fullscreen: false }
let two = new Two(twoConfig).appendTo(canvas)
const waitSound = new Howl({
    src: ["music/Dance_of_the_salty_boys.ogg"],
    loop: true,
    volume: 0.3
})
const gameSound = new Howl({
    src: ["music/Tetris_D_Theme.ogg"],
    loop: true,
    volume: 0.4
})
const socket = io("/host")

const WIDTH = two.height / 20 // Wontfix
let fields = [
    new field(WIDTH, WIDTH, WIDTH),
    new field(WIDTH * 10 + WIDTH, WIDTH, WIDTH)
] // Fields to be drawn; for now just 2

let roomId = ""

socket.on("connect", () => {
    waitSound.play()
})

socket.emit("host")

socket.on("start game", () => {
    const elem = document.getElementById("load")
    elem.classList.add("hidden")

    waitSound.stop()
    gameSound.play()
})

socket.on("host greet", (data) => {
    roomId = data["room_id"]
    document.getElementById("roomid").innerHTML = `${spaceOut(roomId)}`
})

socket.on("update", (data) => {
    two.clear()
    // data is expected to be a list of objects, each with
    // a board ID and grid data (2D array)
    // For now, only the first two available will be dealt with
    // Naive assumption that at least two boards are available!
    for (let i = 0; i < 2; i++) {
        let info = data[i]
        let grid = info["grid"]
        fields[i].draw(grid)
    }
    two.update()
})


function sendReady() {
    if (socket) {
        socket.emit("ready", roomId)
    }
}

/**
 * Add spaces every breaks characters in a string.
 * @param s - String to space out.
 * @param breaks - Characters between spaces.
 * @returns 
 */
function spaceOut(s, breaks) {
    if (breaks == null) {
        breaks = 4
    }
    let ret = ""
    for (let i = 0; i < s.length; i ++) {
        if (i % breaks == 0 && i != 0) {
            ret += " "
        }
        ret += s[i]
    }
    return ret
}


/**
 * Construct a playfield for rendering
 * @param width Width of each piece.
 * @param config Basic configuration object.
 *      Configurations:
 *      - color: Piece colors array.
 *      - stroke_color: Piece stroke colors array.
 *      - stroke_width: Piece stroke width.
 *      - grid_lines: Show grid lines?
 *      - lines_color: Grid line color.
 *      - grid_stroke: Grid stroke width.
 *      - background_color: Background color of the grid.
 */
function field(x, y, width, config) {
    this.squares = []
    this.x = x
    this.y = y
    this.width = width
    this.config = config || {
        "color": [ "rgb(137, 226, 136)" ],
        "stroke_color": [ "rgb(95, 165, 94)" ],
        "stroke_width": 5,
        "grid_lines": true,
        "lines_color": "rgb(52, 150, 51)",
        "grid_stroke": "1",
        "background_color": "rgb(171, 209, 115)"
    }

    /**
     * Dry draw the playfield. You must call Two.update to reflect the
     * new drawings.
     * @param data Raw 2D grid values.
     */
    this.draw = function(data) {
        if (!data) return;
        for (let r = 0; r < data.length; r++) {
            for (let c = 0; c < data[r].length; c++) {
                const value = data[r][c]
                let x = this.x + c * this.width
                let y = this.y + r * this.width
                if (this.config["grid_lines"] && value == 0) {
                    let rect = two.makeRectangle(x, y, width, width)
                    rect.fill = this.config["background_color"]
                    rect.strokeColor = this.config["lines_color"]
                    rect.lineWidth = this.config["grid_stroke"]
                } else {
                    let rect = two.makeRectangle(x, y, width, width)
                    let cols = this.determineColor(data[r][c])
                    rect.fill = cols[0]
                    rect.strokeColor = cols[1]
                    rect.lineWidth = this.config["stroke_width"]
                    if (value < 0) {
                        rect.opacity = .5
                    }
                }
            }
        }
    }

    /**
     * Determine piece color (does not account for alpha).
     * Assumes that there is at least one element in color and storke_color.
     * @param value Piece value.
     * @returns Array of piece color and piece stroke color.
     */
    this.determineColor = function(value) {
        value = Math.abs(value) - 1
        let choices = this.config["color"]
        let color = choices[value - 1] || choices[0]
        let strokeChoices = this.config["stroke_color"]
        let strokeColor = strokeChoices[value] || strokeChoices[0]
        return [ color, strokeColor ]
    }

}
