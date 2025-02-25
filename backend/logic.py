import random
import glob
import sympy as sp
import json  
import backend.txt2h5p.parser as h5p_parser
import backend.util as util
from pathlib import Path

class Logic:
    def __init__(self):
        # Start counter at 1 (or load from shared state if needed)
        self.file_counter = 1  
        self.path_to_output_json = None
        self.path_to_output_txt = None
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
        lines = []
        for idx, q in enumerate(questions, start=1):
            question_text = q.get("question_text")
            substituted_text = q.get("correct_formula")
            
            if q.get("wrong_answers"):
                # MCQ header.
                header = f"MCQ: {idx}. {question_text} {substituted_text}"
                lines.append(header)
                lines.append(f"*{q.get('correct_answer')}")
                for wa in q.get("wrong_answers"):
                    lines.append(f"{wa}")
            else:
                # FIB header.
                header = f"FIB: {idx}. {question_text} {substituted_text}"
                lines.append(header)
                lines.append(f"=> *{q.get('correct_answer')}*")
            lines.append("")
            
        with open(self.path_to_output_txt, 'w') as f:
            f.write("\n".join(lines))

    def randomize_parameters(self, parameters):
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
        if correct_answer_data['answer_mode'] == 'function':
            expr = correct_answer_data['function']
        else:
            expr = sp.sympify(latex_question)
        evaluated_value, _ = self.evaluate_expression(expr, randomized_params)
        evaluated_value = round(evaluated_value, self.precision)
        substituted_formula = sp.latex(expr.subs(randomized_params))
        return {
            'correct_answer': evaluated_value,
            'correct_formula': substituted_formula
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

    def generate_h5p(self):
        h5p_parser.generate("./backend/txt2h5p/control.txt", self.path_to_output_txt)

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
        parameters = data.get("parameters")
        correct_answer_data = data.get("correct_answer")
        wrong_answers = data.get("wrong_answers")
        answer_number = data.get("answer_number")
        randomization_count = data.get("randomization_count")
        
        # Use current file counter as the identifier for this generation run.
        file_id = self.file_counter  
        random_questions = []
        for _ in range(randomization_count):
            randomized_params = self.randomize_parameters(parameters)
            correct_data = self.process_correct_answer(correct_answer_data, latex_question, randomized_params)
            question_dict = {
                'identifier': file_id,  # Embed the file identifier.
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

        # Set file names based on file_id.
        self.path_to_output_json = f"output{file_id}.json"
        self.path_to_output_txt = f"output{file_id}.txt"
        self.save_to_file(random_questions)
        self.save_to_txt(random_questions)
        self.generate_h5p()
        # Increment counter so next run uses a new identifier.
        self.file_counter += 1
        return random_questions

    def generate_final_h5p_set(self):
        """
        Gathers one random question from each output file (output*.json),
        writes the final JSON and TXT, and then runs the H5P generator.
        """
        final_questions = []
        # Sort files based on the numeric part of the filename.
        for filename in sorted(glob.glob("output*.json"), key=lambda x: int(''.join(filter(str.isdigit, x)))):
            with open(filename, 'r') as f:
                questions = json.load(f)
            if questions:
                final_questions.append(random.choice(questions))
        # Write the final outputs.
        final_json = "finalOutput.json"
        final_txt = "finalOutput.txt"
        with open(final_json, 'w') as f:
            json.dump(final_questions, f, indent=4)
        # Build TXT content.
        lines = []
        for idx, q in enumerate(final_questions, start=1):
            question_text = q.get("question_text")
            substituted_text = q.get("correct_formula")
            if q.get("wrong_answers"):
                header = f"MCQ: {idx}. {question_text} {substituted_text}"
                lines.append(header)
                lines.append(f"*{q.get('correct_answer')}")
                for wa in q.get("wrong_answers"):
                    lines.append(f"{wa}")
            else:
                header = f"FIB: {idx}. {question_text} {substituted_text}"
                lines.append(header)
                lines.append(f"=> *{q.get('correct_answer')}*")
            lines.append("")
        with open(final_txt, 'w') as f:
            f.write("\n".join(lines))
        # Run the H5P generator on the final TXT.
        self.path_to_output_txt = final_txt  # update path for H5P generator.
        self.generate_h5p()
