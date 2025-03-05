import random
import sympy as sp
import json

try:
    import backend.txt2h5p.parser as h5p_parser
except ModuleNotFoundError:
    import txt2h5p.parser as h5p_parser

try:
    import backend.util as util
except ModuleNotFoundError:
    import util

class Logic:
    def __init__(self):
        self.path_to_output_json = 'output.json'
        self.path_to_output_txt = 'output.txt'
        self.data = None
        self.precision = 3

    def save_to_file(self, data):
        def default_converter(obj):
            if isinstance(obj, sp.Integer):
                return int(obj)
            elif isinstance(obj, sp.Rational):
                return f"{obj.p}/{obj.q}"
            return str(obj)

        with open(self.path_to_output_json, 'w') as f:
            json_data = json.dumps(data, indent=4, default=default_converter)
            json_data = json_data.replace('\\\\', '\\')  # Replace double backslashes with a single backslash
            f.write(json_data)


    def save_to_txt(self, questions):
        lines = []
        for idx, q in enumerate(questions, start=1):
            question_text = q.get("question_text")
            original_formula = q.get("original_formula")
            original_formula = f"\\[{original_formula}\\]"
            if q.get("wrong_answers"):
                header = f"MCQ: {idx}. {question_text} {original_formula}"
                lines.append(header.replace('\\\\', '\\'))  # Ensure raw LaTeX
                lines.append(f"*{q.get('correct_answer')}")
                for wa in q.get("wrong_answers"):
                    lines.append(f"{wa}")
            else:
                header = f"FIB: {idx}. {question_text} {original_formula}"
                lines.append(header.replace('\\\\', '\\'))  # Ensure raw LaTeX
                lines.append(f"=> *{q.get('correct_answer')}*")
            lines.append("")

        with open(self.path_to_output_txt, 'w') as f:
            f.write("\n".join(lines))


    def generate_h5p(self):
        h5p_parser.generate("./backend/txt2h5p/control.txt", self.path_to_output_txt)

    def randomize_parameters(self, parameters):
        if not parameters:
            return {}

        randomized_params = {}
        for param in parameters:
            param_name = param.get('name')
            if not param_name:
                continue
                
            try:
                range_from = int(param.get('range_from', 0))
                range_to = int(param.get('range_to', 0))
                excluding = int(param.get('excluding', None)) if param.get('excluding') is not None else None
                step = int(param.get('step', 1))
            except (ValueError, TypeError):
                continue

            param_values = [i for i in range(range_from, range_to + 1, step)
                            if excluding is None or i != excluding]
            if param_values:
                randomized_params[param_name] = random.choice(param_values)
        return randomized_params

    def auto_evaluate_expression(self, expr, randomized_params):
        substituted = expr.subs(randomized_params)

        if isinstance(substituted, (list, tuple)):
            solutions = sp.solve(substituted, dict=True)
            return solutions

        if isinstance(substituted, sp.Equality):
            solutions = sp.solve(substituted, dict=False)
            return solutions

        try:
            temp = substituted.doit()
        except (AttributeError, TypeError):
            temp = substituted

        if isinstance(temp, sp.Equality):
            solutions = sp.solve(temp, dict=False)
            return solutions

        return temp.evalf()

    def evaluate_expression(self, expr, randomized_params):
        result = self.auto_evaluate_expression(expr, randomized_params)

        if isinstance(result, list):
            if len(result) == 1 and isinstance(result[0], (sp.Expr, int, float)):
                numeric_value = result[0].evalf()
            else:
                numeric_value = result
        elif isinstance(result, dict):
            numeric_value = result
        elif isinstance(result, sp.Expr):
            numeric_value = result.evalf()
        else:
            numeric_value = result

        try:
            numeric_value = float(numeric_value)
            numeric_value = round(numeric_value, self.precision)
        except (TypeError, ValueError):
            pass

        return numeric_value

    def process_correct_answer(self, correct_answer_data, latex_question, randomized_params):
        """
        Stores the original function after substitution and its evaluated answer.
        The `original_formula` is stored in LaTeX format exactly as given.
        """
        if correct_answer_data['answer_mode'] == 'function':
            expr = correct_answer_data['function']
        else:
            expr = sp.sympify(latex_question)

        substituted_expr = expr.subs(randomized_params)  # Substitute parameters before storing
        original_formula_latex = sp.latex(substituted_expr)  # Convert to LaTeX without simplification

        evaluated_value = self.evaluate_expression(expr, randomized_params)

        return {
            'correct_answer': evaluated_value,
            'original_formula': original_formula_latex  # This stores the exact substituted expression
        }

    def process_wrong_answers(self, wrong_answers, randomized_params, answer_number):
        wrong_options = []
        for wrong_item in wrong_answers:
            if isinstance(wrong_item, str):
                wrong_options.append({
                    "value": wrong_item,
                    "formula": wrong_item
                })
            else:
                substituted_expr = wrong_item.subs(randomized_params)
                evaluated_val = self.evaluate_expression(wrong_item, randomized_params)
                original_wrong_expr_latex = sp.latex(substituted_expr)

                wrong_options.append({
                    "value": str(evaluated_val),
                    "formula": original_wrong_expr_latex
                })
        
        if answer_number is None or answer_number <= 0:
            answer_number = len(wrong_options)

        final_wrong_options = random.sample(wrong_options, min(answer_number, len(wrong_options)))
        final_wrong_values = [opt["value"] for opt in final_wrong_options]
        final_wrong_formulas = [opt["formula"] for opt in final_wrong_options]

        return final_wrong_values, final_wrong_formulas

    def perform_logic(self, data):
        self.data = data
        latex_question = data.get("latex_question")
        question_text = data.get("question_text", latex_question)

        try:
            precision = int(data.get("precision"))
            if precision > 0:
                self.precision = precision
        except (TypeError, ValueError):
            util.logger.error(f"Invalid precision value: {data.get('precision')}")

        parameters = data.get("parameters", [])
        correct_answer_data = data.get("correct_answer", {})
        wrong_answers = data.get("wrong_answers", None)
        answer_number = data.get("answer_number", 0)
        randomization_count = data.get("randomization_count", 1)

        random_questions = []
        for _ in range(randomization_count):
            randomized_params = self.randomize_parameters(parameters)
            correct_data = self.process_correct_answer(correct_answer_data, latex_question, randomized_params)

            question_dict = {
                'question_text': question_text,
                'randomized_params': randomized_params,
                'correct_answer': correct_data['correct_answer'],
                'original_formula': correct_data['original_formula']
            }

            if wrong_answers:
                wrong_vals, wrong_formulas = self.process_wrong_answers(wrong_answers, randomized_params, answer_number)
                question_dict['wrong_answers'] = wrong_vals
                question_dict['wrong_formulas'] = wrong_formulas
            else:
                question_dict['wrong_answers'] = []
                question_dict['wrong_formulas'] = []

            random_questions.append(question_dict)

        self.save_to_file(random_questions)
        self.save_to_txt(random_questions)

        self.generate_h5p()

        return random_questions


if __name__ == "__main__":
    logic = Logic()

    # Example MCQ-type data
    data_mcq = {
        "question_text": "Solve the equation to the 3rd decimal place.",
        "latex_question": "Eq(a*x, b)",  # e.g. a*x = b
        "parameters": [
            {
                "name": "a",
                "range_from": "1",
                "range_to": "100",
                "excluding": "0",
                "step": "2"
            },
            {
                "name": "b",
                "range_from": "1",
                "range_to": "50",
                "excluding": "1",
                "step": "1"
            }
        ],
        "correct_answer": {
            "answer_mode": "function",
            # e.g. x = b/a
            "function": sp.sympify("b/a")
        },
        "wrong_answers": [
            sp.sympify("a/b"),
            sp.sympify("a - b"),
            "Just a random string",
            sp.sympify("a*b"),
            sp.sympify("(a + b) / 2"),
        ],
        "answer_number": 3,
        "randomization_count": 4
    }

    # Example FIB-type data
    data_fib = {
        "question_text": "Find x given the equation:",
        "latex_question": "Eq(a*x, b)",
        "parameters": [
            {
                "name": "a",
                "range_from": "2",
                "range_to": "100",
                "excluding": "0",
                "step": "2"
            },
            {
                "name": "b",
                "range_from": "2",
                "range_to": "50",
                "excluding": "1",
                "step": "1"
            }
        ],
        "correct_answer": {
            "answer_mode": "function",
            "function": sp.sympify("b/a")
        },
        "wrong_answers": None,
        "answer_number": 0,
        "randomization_count": 4
    }

    # Example integral question (to show it automatically uses doit())
    data_integral = {
        "question_text": "Compute the definite integral from 0 to a:",
        "latex_question": "Integral(x**2, (x, 0, a))",
        "parameters": [
            {
                "name": "a",
                "range_from": "2",
                "range_to": "10",
                "excluding": "0",
                "step": "1"
            }
        ],
        "correct_answer": {
            "answer_mode": "function",
            # We can also define correct answer as a direct expression for the integral:
            # ∫ x^2 dx from 0 to a => a^3/3
            "function": sp.sympify("a**3/3")
        },
        "wrong_answers": [
            sp.sympify("a**2/2"),
            sp.sympify("2*a**2"),
            "No integral done"
        ],
        "answer_number": 2,
        "randomization_count": 3
    }


    # Uncomment any one to test:
    # questions = logic.perform_logic(data_mcq)
    # questions = logic.perform_logic(data_fib)
    # questions = logic.perform_logic(data_integral)
    print(questions)
