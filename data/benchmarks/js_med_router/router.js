// HTTP Router
const { createMiddlewareChain } = require("./middleware.js");

class Router {
    constructor() {
        this.routes = {};
        this.middleware = createMiddlewareChain();
    }
    get(path, handler) {
        this.routes[`GET:${path}`] = handler;
    }
    post(path, handler) {
        this.routes[`POST:${path}`] = handler;
    }
    dispatch(method, path, req, res) {
        this.middleware.run(req, res);
        const key = `${method.toUpperCase()}:${path}`;
        if (this.routes[key]) {
            return this.routes[key](req, res);
        }
        return "404 Not Found";
    }
}
module.exports = { Router };
