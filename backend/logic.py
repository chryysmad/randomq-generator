import random
import sympy as sp
import json

try:
    import backend.util as util
except ModuleNotFoundError:
    import util

class Logic:
    def __init__(self):
        self.path_to_output = 'output.json'

    def save_to_file(self, data):
        def default_converter(obj):
            if isinstance(obj, sp.Integer):
                return int(obj)
            elif isinstance(obj, sp.Rational):
                return f"{obj.p}/{obj.q}"
            return str(obj)
        
        with open(self.path_to_output, 'w') as f:
            json.dump(data, f, indent=4, default=default_converter)

    def perform_logic(self, data):
        shared_data = data

        latex_question = shared_data.get("latex_question")
        parameters = shared_data.get("parameters")
        correct_answer = shared_data.get("correct_answer")
        wrong_answers = shared_data.get("wrong_answers")
        answer_number = shared_data.get("answer_number")
        randomization_count = shared_data.get("randomization_count")

        random_questions = []
        for _ in range(randomization_count):
            # Randomize parameters within range
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

            # Determine the original correct formula (without substitution)
            if correct_answer['answer_mode'] == 'function':
                original_correct_expr = correct_answer['function']
            else:
                original_correct_expr = sp.sympify(latex_question)
            
            # Now substitute the parameters for evaluation purposes
            substituted_expr = original_correct_expr.subs(randomized_params)
            evaluated_value = substituted_expr.evalf()
            correct_answer_latex = sp.latex(evaluated_value)
            # Store the original formula (unsolved) as LaTeX
            correct_formula = sp.latex(original_correct_expr)

            util.logger.info(f"Correct expression (unsolved): {original_correct_expr}")
            util.logger.info(f"Substituted expression: {substituted_expr}")
            util.logger.info(f"Evaluated value: {evaluated_value}")

            # Process wrong answers, storing original formulas before substitution.
            wrong_options = []
            for wrong_item in wrong_answers:
                if isinstance(wrong_item, str):
                    # If it's a string, use it as both value and formula.
                    wrong_options.append({
                        "value": wrong_item,
                        "formula": wrong_item
                    })
                else:
                    # For a sympy expression, capture the original formula
                    original_wrong_expr = wrong_item
                    # Substitute parameters for evaluation
                    substituted_wrong_expr = original_wrong_expr.subs(randomized_params)
                    wrong_value = substituted_wrong_expr.evalf()
                    wrong_options.append({
                        "value": sp.latex(wrong_value),
                        "formula": sp.latex(original_wrong_expr)
                    })

            # Randomly select the desired number of wrong answers
            final_wrong_options = random.sample(wrong_options, answer_number)
            final_wrong_values = [opt["value"] for opt in final_wrong_options]
            final_wrong_formulas = [opt["formula"] for opt in final_wrong_options]

            # Append the complete question data.
            random_questions.append({
                'randomized_params': randomized_params,
                'correct_answer': correct_answer_latex,
                'correct_formula': correct_formula,
                'wrong_answers': final_wrong_values,
                'wrong_formulas': final_wrong_formulas
            })
        
        # Save the generated questions to output.json.
        self.save_to_file(random_questions)
        return random_questions

if __name__ == "__main__":
    logic = Logic()

    # Emulate shared_data with the specified values:
    data = {
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
        # The correct answer is x = b/a (as a sympy expression)
        "correct_answer": {
            "answer_mode": "function",
            "function": sp.sympify("b/a")
        },
        # Provide three wrong answer options (a mix of sympy expressions and strings)
        "wrong_answers": [
            sp.sympify("a/b"),    # Wrong: reciprocal of b/a
            sp.sympify("a - b"),   # Wrong: difference between a and b
            "String option"        # A string option
        ],
        "answer_number": 3,
        "randomization_count": 4
    }

    # Run the logic to generate questions and output to output.json
    questions = logic.perform_logic(data)
