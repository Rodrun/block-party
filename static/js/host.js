socket = io()


socket.on("connect", () => {
    console.log("Retrieving host room ID...")
    socket.emit("host")
})

socket.on("host greet", (data) => {
    console.log(data)
    document.getElementById("roomid").innerHTML =
        `${spaceOut(data["room_id"])}`
})

socket.on("start game", () => {
    console.log("Starting game")
    // Set graphics to visible
})


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
