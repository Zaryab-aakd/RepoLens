// Middleware pipeline
function createMiddlewareChain() {
    const stack = [];
    return {
        use(fn) { stack.push(fn); },
        run(req, res) { stack.forEach(fn => fn(req, res)); }
    };
}
module.exports = { createMiddlewareChain };
