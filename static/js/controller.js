//'use strict'
const e = React.createElement
let roomid = ""
let boardid = ""
const socket = io()

socket.on("connect", () => {
    socket.on("start", (data) => {
        console.log("Game start event")
    })
})

function sendInput(command) {
    if (socket) {
        socket.emit("input", {
            "room": roomid,
            "bid": boardid,
            "command": command
        })
    }
}


function Intro({ title }) {
    const [visible, setVisible] = React.useState(true)
    const [roomId, setRoomId] = React.useState("")

    handleJoin = () => {
        roomid = roomId
        console.log(`Joining ${roomId}`)
        socket.emit("join", { "room": roomId })
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
                )
            ),
            e(Reactstrap.Button, {"onClick":() => handleJoin()}, "Join Game"),
        )
    return visible ? form : null
}

function ControllerBtn({ name, display, className }) {
    return e(Reactstrap.Button,
        {
            "className": className || `bt-${name}`,
            "onClick": () => sendInput(name)
        },
        display
    )
}

function Controller() {
    return (
        e("div", null, 
            e(ControllerBtn, {"name":"left", "display":"Left"}),
            e(ControllerBtn, {"name":"right", "display":"Right"}),
            e(ControllerBtn, {"name":"soft_drop", "display":"Down", "className":"bt-soft"}),
            e(ControllerBtn, {"name":"hard", "display":"Drop"}),
            e(ControllerBtn, {"name":"rotate_cw", "display":"A", "className":"bt-a"}),
            e(ControllerBtn, {"name":"rotate_ccw", "display":"B", "className":"bt-b"}),
            e(ControllerBtn, {"name":"hold", "display":"Hold"}),
        )
    )
}

ReactDOM.render(e(Intro, {"title":"Block Party"}, null), document.getElementById("intro"))
ReactDOM.render(e(Controller, null, null), document.getElementById("play"))
