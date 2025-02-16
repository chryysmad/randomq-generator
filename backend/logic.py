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
                fraction_str = f"{obj.p}/{obj.q}"
                return fraction_str
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
            # randomize parameters within range
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

            
            # calculate the correct answer based on answer_mode
            if correct_answer['answer_mode'] == 'function':
                correct_answer_func = correct_answer['function']
                correct_value = correct_answer_func.subs(randomized_params)
            else:
                expr = sp.sympify(latex_question)
                correct_value = expr.subs(randomized_params)

            evaluated_value = correct_value.evalf()
            correct_answer_latex = sp.latex(evaluated_value)

            util.logger.info(f"Correct value: {correct_value}")
            util.logger.info(f"Evaluated value: {evaluated_value}")

            # select wrong answers
            selected_wrong_answers = []
            for wrong_answer in wrong_answers:
                if isinstance(wrong_answer, str):
                    selected_wrong_answers.append(wrong_answer)
                else:
                    wrong_value = wrong_answer.subs(randomized_params)
                    selected_wrong_answers.append(wrong_value)

            final_wrong_answers = random.sample(selected_wrong_answers, answer_number)

            random_questions.append({
                'randomized_params': randomized_params,
                'correct_answer': correct_answer_latex, 
                'wrong_answers': final_wrong_answers
            })

        # Should output the random questions to a specified file
        # with open(self.path_to_output, 'w') as f:
        #     json.dump(random_questions, f, indent=4)
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
        # Provide three wrong answer options (mix of sympy expressions and strings)
        "wrong_answers": [
            sp.sympify("a/b"),    # wrong: reciprocal of b/a
            sp.sympify("a - b"),   # wrong: difference between a and b
            "String option"           # a string option
        ],
        "answer_number": 3,
        "randomization_count": 4
    }

    # Run the logic to generate questions and output to output.json
    questions = logic.perform_logic(data)
    

