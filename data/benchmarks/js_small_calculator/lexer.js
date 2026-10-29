// Lexer tokenizer
function tokenize(expr) {
    return expr.match(/\d+|\+|\-|\*|\//g) || [];
}
module.exports = { tokenize };
