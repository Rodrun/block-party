socket = null


/**
 * Trigger an error animation on element with given id.
 */
function triggerErrorAnim(id) {
    let elem = document.getElementById(id)
    elem.classList.add("shake-horizontal")
    elem.onanimationend = () => {
        elem.classList.remove("shake-horizontal")
    }
}

/**
 * Connect to given addr.
 * Will throw error if could not connect.
 */
function connectTo(addr) {
    try {
        socket = io(addr)
    } catch (err) {
        throw err
    }
}

function onSubmit() {
    let txt = document.getElementById("ipinput")
    try {
        connectTo(txt.value)
    } catch (err) {
        console.log(err)
        triggerErrorAnim("submit")
    }
}

/**
 * Set up the controller buttons.
 */
function setupButtons() {
    let buttons = document.getElementsByClassName("bt")
    for (let button of buttons) {
        button.onclick = () => {
            console.log(button.dataset.input)
            sendInput(button.dataset.input)
        }
    }
}

/**
 * Send input to host.
 * @param name Name of input.
 */
function sendInput(name) {
    if (socket) {
        socket.emit("input", name)
    }
}
