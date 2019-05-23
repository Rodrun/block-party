//socket = new ReconnectingWebSocket("ws://" + String(window.location).replace(/http(s?):\/\//g, ""))
socket = null
name = ""
session_id = ""

/**
 * Very simplistic check if something is a function.
 */
function isFunction(f) {
    return typeof f === "function"
}


/**
 * Set the visibility of an element (flag = true means set visible).
 * Setting animationClasss to null will use defaults.
 */
function setVisibility(id, flag, animationClass, callback) {
    clist = document.getElementById(id).classList
    if (!animationClass) {
        if (flag) {
            animationClass = "puff-in-center"
            clist.remove("hidden")
            clist.add("visible")
        } else {
            animationClass = "puff-out-center"
        }
    }
    triggerAnimation(id, animationClass, () => {
        if (flag) {
            //clist.remove("hidden")
            //clist.add("visible")
        } else {
            clist.remove("visible")
            clist.add("hidden")
        }

        if (isFunction(callback)) {
            callback()
        }
    })
}


/**
 * Hides an element and shows another.
 * @param origId - ID of element to hide.
 * @param newId - ID of element to show.
 * @param animationClassOrig - Name of animation class to use for the original element.
 * @param animationClassNew - Name of animation class to use for the new element.
 * @param callback - Callback after operation is complete.
 */
function switchVisibility(origId, newId, animationClassOrig, animationClassNew,
    callback) {
        animationClass = "puff-out-center"

    setVisibility(origId, false, animationClassOrig,
        () => setVisibility(newId, true, animationClassNew, callback))
}


function triggerAnimation(id, className, afterEnd) {
    let elem = document.getElementById(id)
    if (elem) {
        elem.classList.add(className)
        elem.onanimationend = () => {
            elem.classList.remove(className)
            if (isFunction(afterEnd)) afterEnd()
        }
    }
}


/**
 * Trigger an error animation on element with given id.
 */
function triggerErrorAnim(id, callback) {
    triggerAnimation(id, "shake-horizontal", callback)
}


function updateWaitScreen() {
    document.getElementById("boardid").innerHTML = name
    document.getElementById("roomid").innerHTML = session_id
}

/**
 * Set up the controller buttons.
 */
function setupButtons() {
    let buttons = document.getElementsByClassName("bt")
    for (let button of buttons) {
        console.log(`Setting up ${button}`)
        button.onclick = () => {
            console.log(button.dataset.input)
            sendInput(button.dataset.input)
        }
    }
}


/**
 * Send input to host.
 * @param nm Name of input.
 */
function sendInput(nm) {
    if (socket) {
        msg = JSON.stringify([name, nm])
        socket.emit("input", msg)
        console.log("Emit input: " + msg)
    }
}


/**
 * Set the 'player name' to send data.
 */
function setPlayerName(n) {
    name = n
    setBackgroundColor(n)
}


/**
 * Handle room ID submission.
 */
function onSubmit() {
    socket = io()
    socket.on("error", (e) => {
        console.log(`SocketIO error: ${e}`)
    })
    socket.on("joined room", (data) => {
        room = data["room"] // Room ID
        bid = data["bid"] // Board ID
        session_id = room
        name = bid
        switchVisibility("intro", "wait", null, null, () => {
            setupButtons()
            updateWaitScreen()
        })
    })
    socket.on("connect", () => {
        let value = document.getElementById("ipinput").value.replace(/\s/g, "")
        if (value != "") {
            console.log(`Joining room: ${value}`)
            socket.emit("join", { "room": value })
        }
    })
}
