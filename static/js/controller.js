//'use strict'
const e = React.createElement
const socket = io()

// TODO: Consistent naming conventions
let roomid = "" // ID of the game room
let boardid = "" // ID of the board to control
let name = "" // Server-given name
let joinMessage = "" // Returned message from join attempt
let joinState = false // Returned status from join attempt

// TODO: delete this mess
class GlobalState {
    constructor(init) {
        this.value = init
    }
}
let globalState = new GlobalState("intro")

const introRoot = e(Intro, {"title":"Block Party", "state":globalState}, null)
const waitRoot = e(PlayerName, {"state":globalState}, null)
const playRoot = e(Controller, {"state":globalState}, null)

socket.on("start game", (data) => {
    globalState.value = "play"
})

/**
 * Join acknowledgement function.
 */
function joinAck(success, message, bid) {
    console.log(success)
    console.log(message)
    joinState = success
    if (success) {
        boardid = bid
        name = message
        globalState.value = "wait"
        ReactDOM.render(waitRoot, document.getElementById("wait"))
    } else {
        joinMessage = message
    }
}

/**
 * Send user input to server.
 */
function sendInput(command) {
    if (socket) {
        socket.emit("input", JSON.stringify({
            room: roomid,
            bid: boardid,
            command: command
        }))
    }
}

/**
 * Send join room request to server.
 */
function sendJoin(rid) {
    if (socket) {
        outRid = rid.replace(/\s/g, "")
        roomid = outRid
        console.log(`Joining ${outRid}`)
        socket.emit("join", JSON.stringify({"room": outRid}), joinAck)
    }
}

function Intro({ title, state }) {
    const [roomId, setRoomId] = React.useState("")
    const [visible, setVisible] = React.useState(true)

    const handleJoin = () => {
        sendJoin(roomId)
        setVisible(false)
    }

    const form =
        e(Reactstrap.Form, null,
            e("h1", null, title),
            e(Reactstrap.FormGroup, null,
                e(Reactstrap.Label, {"for":"roomid"}, "Enter Code:"),
                e(Reactstrap.Input,
                    {
                        "type":"text",
                        "name":"rid",
                        "id":"roomid",
                        "placeholder":"Room ID",
                        "onChange":(e) => setRoomId(e.target.value)
                    }
                ),
                e(Reactstrap.FormText, null, `You can host a game at ${window.location}/host`),
            ),
            e(Reactstrap.Button, {"onClick":(e) => handleJoin()}, "Join Game")
        )
    return visible ? form : null
}

function PlayerName({ state }) {
    return e(Reactstrap.Label, null,
            e("h1", {"className":"display-3"}, `You are ${name}`))
}

function ControllerBtn({ name, display, className }) {
    return (e("div",
        {
            "className": "bt " + (className || `bt-${name}`),
            "onClick": () => sendInput(name)
        },
        display
    ))
}

function Controller({ state }) {
    return state.value ? (
        e("div", {"className":"bt-grid-container"}, 
            e(ControllerBtn, {"name":"left", "display":"Left"}),
            e(ControllerBtn, {"name":"right", "display":"Right"}),
            e(ControllerBtn, {"name":"soft_drop", "display":"Down", "className":"bt-soft"}),
            e(ControllerBtn, {"name":"hard_drop", "display":"Drop", "className": "bt-hard"}),
            e(ControllerBtn, {"name":"rotate_cw", "display":"A", "className":"bt-a"}),
            e(ControllerBtn, {"name":"rotate_ccw", "display":"B", "className":"bt-b"}),
            e(ControllerBtn, {"name":"hold", "display":"Hold"}),
        )
    ) : null
}

ReactDOM.render(introRoot, document.getElementById("intro"))
ReactDOM.render(playRoot, document.getElementById("play"))
