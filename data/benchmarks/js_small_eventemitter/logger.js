// Event logger
const { EventEmitter } = require("./events.js");

function attachLogger(emitter) {
    emitter.on("info", data => console.log("[INFO]", data));
    emitter.on("error", err => console.error("[ERROR]", err));
}
module.exports = { attachLogger };
