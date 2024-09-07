import random
import sympy as sp

class Logic:
    def __init__(self, controller):
        self.controller = controller

    def perform_logic(self):
        shared_data = self.controller.shared_data

        latex_question = shared_data.get("latex_question")
        parameters = shared_data.get("parameters")
        correct_answer = shared_data.get("correct_answer")
        wrong_answers = shared_data.get("wrong_answers")
        answer_number = shared_data.get("answer_number")
        randomization_count = shared_data.get("randomization_count")

        param_symbols = {param['name']: sp.symbols(param['name']) for param in parameters}
        x = sp.symbols('x') 

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
                
            correct_answer_latex = sp.latex(correct_value)


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

        print(random_questions)
        return random_questions
