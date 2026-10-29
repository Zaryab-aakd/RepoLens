// PubSub event bus
class EventEmitter {
    constructor() {
        this.listeners = {};
    }
    on(event, handler) {
        if (!this.listeners[event]) this.listeners[event] = [];
        this.listeners[event].push(handler);
    }
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(fn => fn(data));
        }
    }
}
module.exports = { EventEmitter };
