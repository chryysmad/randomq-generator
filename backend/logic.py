import random
import sympy as sp
import json

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
            json.dump(data, f, indent=4, default=default_converter)

    def save_to_txt(self, questions):
        """
        Converts the list of question dictionaries into a txt file.
        For MCQs, the header is formatted as:
        "MCQ: {question number}. {question text} {question formula}"
        and the correct answer is prefixed with an asterisk on the next line,
        with each wrong answer on its own line.
        For FIBs, the header is formatted similarly, with the correct answer
        appended after an arrow.
        """
        lines = []
        for idx, q in enumerate(questions, start=1):
            question_text = q.get("question_text")
            # The substituted question formula (e.g., "3x+5=10") is stored as "correct_formula".
            substituted_text = q.get("correct_formula")
            params = q.get("randomized_params", {})
            
            if q.get("wrong_answers"):
                # MCQ header: "MCQ: {number}. {question_text} {substituted_text}"
                header = f"MCQ: {idx}. {question_text} {substituted_text}"
                lines.append(header)
                # List the correct answer with an asterisk prefix.
                lines.append(f"*{q.get('correct_answer')}")
                # List each wrong answer on its own line.
                for wa in q.get("wrong_answers"):
                    lines.append(f"{wa}")
            else:
                # FIB header: "FIB: {number}. {question_text} {substituted_text}"
                header = f"FIB: {idx}. {question_text} {substituted_text}"
                lines.append(header)
                # Append the correct answer enclosed in double asterisks.
                lines.append(f"=> **{q.get('correct_answer')}**")
            # Add an empty line between questions.
            lines.append("")

        with open(self.path_to_output_txt, 'w') as f:
            f.write("\n".join(lines))



    def randomize_parameters(self, parameters):
        """
        Randomize parameter values based on their ranges.
        """
        randomized_params = {}
        for param in parameters:
            param_name = param['name']
            range_from = int(param['range_from'])
            range_to = int(param['range_to'])
            excluding = int(param['excluding'])
            step = int(param['step'])

            param_values = [i for i in range(range_from, range_to + 1, step) if i != excluding]
            randomized_value = random.choice(param_values)
            randomized_params[param_name] = randomized_value

        return randomized_params

    def evaluate_expression(self, expr, randomized_params):
        """
        Substitutes randomized parameters in the expression, evaluates it,
        and returns a tuple with the numerical evaluated result and the original formula (LaTeX).
        If the expression is an equation (sp.Equality), it solves for x.
        """
        substituted_expr = expr.subs(randomized_params)

        if isinstance(substituted_expr, sp.Equality):
            solution = sp.solve(substituted_expr, sp.symbols('x'))
            if not solution:
                raise ValueError("No solution found for the equation.")
            evaluated_value = sp.N(solution[0])
        else:
            evaluated_value = substituted_expr.evalf()

        try:
            numerical_value = float(evaluated_value)
        except (TypeError, ValueError):
            numerical_value = evaluated_value

        original_formula_latex = sp.latex(expr)
        return numerical_value, original_formula_latex

    def process_correct_answer(self, correct_answer_data, latex_question, randomized_params):
        """
        Process the correct answer.
        If answer_mode is 'function', use the provided function expression,
        otherwise convert the LaTeX question to a sympy expression.
        Returns a dictionary with evaluated answer and the substituted formula.
        """
        if correct_answer_data['answer_mode'] == 'function':
            expr = correct_answer_data['function']
        else:
            expr = sp.sympify(latex_question)

        evaluated_value, _ = self.evaluate_expression(expr, randomized_params)
        evaluated_value = round(evaluated_value, self.precision)

        # Substitute the randomized parameters into the expression and convert to LaTeX.
        substituted_formula = sp.latex(expr.subs(randomized_params))

        return {
            'correct_answer': evaluated_value,
            'correct_formula': substituted_formula
        }

    def process_wrong_answers(self, wrong_answers, randomized_params, answer_number):
        """
        Process the wrong answers if provided.
        For each wrong answer that is a sympy expression, store its evaluated result and original formula.
        If a wrong answer is a string, just pass it through.
        Randomly selects the desired number of wrong answers.
        Returns a tuple (list of evaluated answers, list of original formulas).
        """
        wrong_options = []
        for wrong_item in wrong_answers:
            if isinstance(wrong_item, str):
                wrong_options.append({
                    "value": wrong_item,
                    "formula": wrong_item
                })
            else:
                original_wrong_expr = wrong_item
                substituted_wrong_expr = original_wrong_expr.subs(randomized_params)
                evaluated_wrong_value = substituted_wrong_expr.evalf()
                evaluated_wrong_value = round(evaluated_wrong_value, self.precision)
                wrong_options.append({
                    "value": sp.latex(evaluated_wrong_value),
                    "formula": sp.latex(original_wrong_expr)
                })
        
        if answer_number is None:
            answer_number = len(wrong_options)
        
        final_wrong_options = random.sample(wrong_options, answer_number)
        final_wrong_values = [opt["value"] for opt in final_wrong_options]
        final_wrong_formulas = [opt["formula"] for opt in final_wrong_options]

        return final_wrong_values, final_wrong_formulas

    def perform_logic(self, data):
        """
        Main logic to generate questions.
        Determines whether the question is FIB (no wrong answers) or MCQ (with wrong answers)
        based on whether 'wrong_answers' is None.
        """
        self.data = data
        latex_question = data.get("latex_question")
        question_text = data.get("question_text", latex_question)
        try:
            precision = int(data.get("precision"))
            if precision > 0:
                self.precision = precision
        except (TypeError, ValueError):
            util.logger.error(f"Invalid precision value: {data.get('precision')}")

        parameters = data.get("parameters")
        correct_answer_data = data.get("correct_answer")
        wrong_answers = data.get("wrong_answers")
        answer_number = data.get("answer_number")
        randomization_count = data.get("randomization_count")

        random_questions = []
        for _ in range(randomization_count):
            randomized_params = self.randomize_parameters(parameters)
            correct_data = self.process_correct_answer(correct_answer_data, latex_question, randomized_params)

            question_dict = {
                'question_text': question_text,
                'randomized_params': randomized_params,
                'correct_answer': correct_data['correct_answer'],
                'correct_formula': correct_data['correct_formula']
            }

            if wrong_answers is not None:
                wrong_vals, wrong_formulas = self.process_wrong_answers(wrong_answers, randomized_params, answer_number)
                question_dict['wrong_answers'] = wrong_vals
                question_dict['wrong_formulas'] = wrong_formulas
            else:
                question_dict['wrong_answers'] = []
                question_dict['wrong_formulas'] = []

            random_questions.append(question_dict)

        self.save_to_file(random_questions)
        self.save_to_txt(random_questions)
        return random_questions


if __name__ == "__main__":
    logic = Logic()

    # Example shared_data for MCQ-type (with wrong answers)
    data_mcq = {
        "question_text": "Solve the equation to the 3rd decimal place.",
        "latex_question": "Eq(a*x, b)",
        "parameters": [
            {
                "name": "a",
                "range_from": "0",
                "range_to": "100",
                "excluding": "0",
                "step": "2"
            },
            {
                "name": "b",
                "range_from": "0",
                "range_to": "50",
                "excluding": "1",
                "step": "1"
            }
        ],
        "correct_answer": {
            "answer_mode": "function",
            "function": sp.sympify("b/a")
        },
        "wrong_answers": [
            sp.sympify("a/b"),
            sp.sympify("a - b"),
            "String option"
        ],
        "answer_number": 3,
        "randomization_count": 4
    }

    # Example shared_data for FIB-type (without wrong answers)
    data_fib = {
        "question_text": "Find x given the equation.",
        "latex_question": "Eq(a*x, b)",
        "parameters": [
            {
                "name": "a",
                "range_from": "0",
                "range_to": "100",
                "excluding": "0",
                "step": "2"
            },
            {
                "name": "b",
                "range_from": "0",
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

    # Run the logic to generate questions.
    # Uncomment one of the following lines to test MCQ or FIB.
    
    # questions = logic.perform_logic(data_mcq)
    questions = logic.perform_logic(data_fib)
