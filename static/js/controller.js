socket = null
name = ""
connectTo()


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
    if (!animationClass) {
        if (flag)
            animationClass = "puff-in-center"
        else
            animationClass = "puff-out-center"
    }
    triggerAnimation(id, animationClass, () => {
        clist = document.getElementById(id).classList
        if (flag)
            clist.remove("hidden")
        else
            clist.add("hidden")
        if (isFunction(callback)) callback()
    })
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


/**
 * Connect to given addr.
 * Will throw error if could not connect.
 */
function connectTo(addr) {
    try {
        socket = io(window.location, {
            reconnection: false,
            transports: ["websocket"],
            upgrade: false,
            multiplex: false
        })
        socket.on("connect", (data) => {
            name = data
            //setVisibility("intro", false, null, () => setVisibility("controller", true))
            setupButtons()
        })
    } catch (err) {
        throw err
    }
}


function onSubmit() {
    let txt = document.getElementById("ipinput")
    try {
        connectTo(txt.value)
        setVisibility("intro", false, null, () => {
            setVisibility("wait", true, null)
        })
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
        print("Emit " + name)
    }
}
