// Expression evaluator
const { tokenize } = require("./lexer.js");

function evaluateExpression(expr) {
    const tokens = tokenize(expr);
    let result = parseFloat(tokens[0]);
    for (let i = 1; i < tokens.length; i += 2) {
        const op = tokens[i];
        const val = parseFloat(tokens[i + 1]);
        if (op === "+") result += val;
        if (op === "-") result -= val;
        if (op === "*") result *= val;
        if (op === "/") result /= val;
    }
    return result;
}
module.exports = { evaluateExpression };
