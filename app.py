from flask import Flask, render_template, request, redirect, url_for
import json
import os
import ast
import operator
from datetime import datetime

app = Flask(__name__)

HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'history.json')

# ---- Safe arithmetic evaluator ----
# We avoid Python's built-in eval() because it can run ANY code (security risk).
# Instead we parse the expression into a syntax tree and only allow numbers
# and basic math operators.
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expression: str):
    """Safely evaluate a basic arithmetic expression like '12 + 3 * 4'."""
    parsed = ast.parse(expression, mode='eval').body
    return _eval_node(parsed)


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError("Operator not allowed")
        return ALLOWED_OPERATORS[op_type](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in ALLOWED_OPERATORS:
            raise ValueError("Operator not allowed")
        return ALLOWED_OPERATORS[op_type](_eval_node(node.operand))
    raise ValueError("Invalid expression")


# ---- History storage (JSON file) ----
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# ---- Routes ----
@app.route('/')
def home():
    history = list(reversed(load_history()))  # newest first
    return render_template('index.html', history=history, error=None, last_expression='')


@app.route('/calculate', methods=['POST'])
def calculate():
    expression = request.form.get('expression', '').strip()
    history = load_history()
    error = None

    if expression:
        try:
            result = safe_eval(expression)
            if isinstance(result, float) and result == int(result):
                result = int(result)
            history.append({
                'expression': expression,
                'result': result,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            save_history(history)
        except ZeroDivisionError:
            error = "Can't divide by zero"
        except Exception:
            error = "Invalid expression"

    return render_template(
        'index.html',
        history=list(reversed(history)),
        error=error,
        last_expression=expression if error else ''
    )


@app.route('/clear-history', methods=['POST'])
def clear_history():
    save_history([])
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
# if __name__ == '__main__':
#     app.run(debug=True)