import random
import glob
import sympy as sp
import json
import os
from sympy.parsing.latex import parse_latex

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
        # Used for naming the output files.
        self.file_counter = 1  
        self.path_to_output_json = "output.json"
        self.path_to_output_txt = "output.txt"
        self.data = None
        self.precision = 0

    def save_to_file(self, data):
        def default_converter(obj):
            if isinstance(obj, sp.Integer):
                return int(obj)
            elif isinstance(obj, sp.Rational):
                return f"{obj.p}/{obj.q}"
            return str(obj)

        with open(self.path_to_output_json, 'w') as f:
            json_data = json.dumps(data, indent=4, default=default_converter)
            # Replace double backslashes with a single backslash
            # json_data = json_data.replace('\\\\', '\\')
            f.write(json_data)

    def save_to_txt(self, questions):
        lines = []
        for idx, q in enumerate(questions, start=1):
            # The question_text already includes the evaluated formula wrapped in \[ \]
            question_text = q.get("question_text")
            if q.get("wrong_answers"):
                header = f"MCQ: {idx}. {question_text}"
                lines.append(header.replace('\\\\', '\\'))
                lines.append(f"*{q.get('correct_answer')}")
                for wa in q.get("wrong_answers"):
                    lines.append(f"{wa}")
            else:
                header = f"FIB: {idx}. {question_text} = *{q.get('correct_answer')}*"
                lines.append(header.replace('\\\\', '\\'))
            lines.append("")

        with open(self.path_to_output_txt, 'w') as f:
            f.write("\n".join(lines))

    def generate_h5p(self, h5p_id=""):
        """
        Generates a single H5P file from self.path_to_output_txt using the txt2h5p parser.
        After generation, renames the file by appending h5p_id to the base name.
        """
        h5p_parser.generate("./backend/txt2h5p/control.txt", self.path_to_output_txt)
        base_name = "example-file"  # Modify if needed
        default_output = f"{base_name}.h5p"
        new_name = f"{base_name}{h5p_id}.h5p" if h5p_id else default_output

        if os.path.exists(default_output):
            os.rename(default_output, new_name)
            util.logger.info(f"Renamed {default_output} to {new_name}")
        else:
            util.logger.error(f"Expected H5P file {default_output} not found.")

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
            if self.precision > 0:
                numeric_value = round(numeric_value, self.precision)
            else:
                numeric_value = int(numeric_value)
        except (TypeError, ValueError):
            pass

        return numeric_value

    def process_correct_answer(self, correct_answer_data, latex_question, randomized_params):
        """
        Stores the original function after substitution and its evaluated answer.
        The 'original_formula' is stored in LaTeX format exactly as given.
        """
        if correct_answer_data['answer_mode'] == 'function':
            func_val = correct_answer_data['function']
            expr = sp.sympify(func_val) if isinstance(func_val, str) else func_val
        else:
            expr = sp.sympify(latex_question)

        substituted_expr = expr.subs(randomized_params)
        original_formula_latex = sp.latex(substituted_expr)
        evaluated_value = self.evaluate_expression(expr, randomized_params)

        return {
            'correct_answer': evaluated_value,
            'original_formula': original_formula_latex
        }

    def process_wrong_answers(self, wrong_answers, randomized_params, answer_number):
        wrong_options = []
        for wrong_item in wrong_answers:
            try:
                wrong_expr = sp.sympify(wrong_item)
                substituted_expr = wrong_expr.subs(randomized_params)
                evaluated_val = self.evaluate_expression(substituted_expr, randomized_params)
                original_wrong_expr_latex = sp.latex(substituted_expr)
                wrong_options.append({
                    "value": str(evaluated_val),
                    "formula": original_wrong_expr_latex
                })
            except (sp.SympifyError, TypeError, ValueError):
                wrong_options.append({
                    "value": wrong_item,
                    "formula": wrong_item
                })

        if answer_number is None or answer_number <= 0:
            answer_number = len(wrong_options)

        final_wrong_options = random.sample(wrong_options, min(answer_number, len(wrong_options)))
        final_wrong_values = [opt["value"] for opt in final_wrong_options]
        final_wrong_formulas = [opt["formula"] for opt in final_wrong_options]
        return final_wrong_values, final_wrong_formulas

    def perform_logic(self, data):
        """
        Processes a single question dictionary.
        Expects data to include:
         - "question_text": the full text with the original bracketed LaTeX.
         - "formula_index" and "formula_length" to locate the LaTeX expression.
         - "latex_question": the extracted LaTeX expression.
        """
        self.data = data
        raw_question_text = data.get("question_text", "")
        formula_index = data.get("formula_index", None)
        formula_length = data.get("formula_length", 0)
        latex_question = data.get("latex_question", "")

        try:
            precision = int(data.get("precision"))
            self.precision = precision if precision > 0 else 0
        except (TypeError, ValueError):
            util.logger.error(f"Invalid precision value: {data.get('precision')}")

        parameters = data.get("parameters", [])
        correct_answer_data = data.get("correct_answer", {})
        wrong_answers = data.get("wrong_answers", None)
        answer_number = data.get("answer_number", 0)
        randomization_count = data.get("randomization_count", 1)

        random_questions = []
        for i in range(randomization_count):
            randomized_params = self.randomize_parameters(parameters)
            correct_data = self.process_correct_answer(correct_answer_data, latex_question, randomized_params)
            # Replace the original bracketed formula with evaluated formula wrapped in \[ and \]
            if formula_index is not None:
                final_question_text = (raw_question_text[:formula_index] +
                                        f"\\[{correct_data['original_formula']}\\]" +
                                        raw_question_text[formula_index+formula_length:])
            else:
                final_question_text = raw_question_text

            question_dict = {
                'identifier': i + 1,
                'question_text': final_question_text,
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

        self.path_to_output_json = f"data/output{self.file_counter}.json"
        self.path_to_output_txt = f"data/output{self.file_counter}.txt"

        os.makedirs("data", exist_ok=True)
        self.save_to_file(random_questions)
        self.save_to_txt(random_questions)
        self.file_counter += 1
        return random_questions

    def generate_final_h5p_set(self, times=1):
        """
        Gathers one random question from each output*.json, writes them to finalOutput_i.json/.txt,
        and calls the H5P generator 'times' times.
        """
        for i in range(times):
            final_questions = []
            for filename in sorted(glob.glob("data/output*.json"), 
                                   key=lambda x: int(''.join(filter(str.isdigit, x))) or 0):
                with open(filename, 'r') as f:
                    questions = json.load(f)
                if questions:
                    final_questions.append(random.choice(questions))

            final_json = f"data/final/finalOutput_{i+1}.json"
            final_txt = f"data/final/finalOutput_{i+1}.txt"
            os.makedirs("data/final", exist_ok=True)
            
            with open(final_json, 'w') as f:
                json.dump(final_questions, f, indent=4)

            lines = []
            for idx, q in enumerate(final_questions, start=1):
                # The question_text already contains the evaluated formula
                question_text = q.get("question_text")
                if q.get("wrong_answers"):
                    header = f"MCQ: {idx}. {question_text}"
                    lines.append(header)
                    lines.append(f"*{q.get('correct_answer')}")
                    for wa in q.get("wrong_answers"):
                        lines.append(f"{wa}")
                else:
                    header = f"FIB: {idx}. {question_text} = *{q.get('correct_answer')}*"
                    lines.append(header)
                lines.append("")

            with open(final_txt, 'w') as f:
                f.write("\n".join(lines))

            self.path_to_output_txt = final_txt
            self.generate_h5p(h5p_id=i+1)
            util.logger.info(f"Generated final H5P set #{i+1} -> {final_json}, {final_txt}")

    def perform_logic_all(self, data_list):
        """
        Processes a list of question dictionaries.
        For each question, performs the required number of randomizations,
        aggregates all questions, and writes them to output files.
        """
        all_questions = []
        for data in data_list:
            raw_question_text = data.get("question_text", "")
            formula_index = data.get("formula_index", None)
            formula_length = data.get("formula_length", 0)
            latex_question = data.get("latex_question", "")

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

            for _ in range(randomization_count):
                randomized_params = self.randomize_parameters(parameters)
                correct_data = self.process_correct_answer(correct_answer_data, latex_question, randomized_params)
                if formula_index is not None:
                    final_question_text = (raw_question_text[:formula_index] +
                                            f"\\[{correct_data['original_formula']}\\]" +
                                            raw_question_text[formula_index+formula_length:])
                else:
                    final_question_text = raw_question_text

                question_dict = {
                    'question_text': final_question_text,
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

                all_questions.append(question_dict)

        self.save_to_file(all_questions)
        self.save_to_txt(all_questions)
        self.generate_h5p()
        return all_questions

if __name__ == "__main__":
    logic_instance = Logic()

    # Example MCQ-type data
    data_mcq = {
        "question_text": "Solve the equation [Eq(a*x, b)] to the 3rd decimal place.",
        "latex_question": "Eq(a*x, b)",
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
            "function": "b/a"
        },
        "wrong_answers": [
            "a/b",
            "a - b",
            "Just a random string",
            "a*b",
            "(a + b) / 2"
        ],
        "answer_number": 3,
        "randomization_count": 4,
        "precision": 3,
        # Example stored formula position data:
        "formula_index": 18,
        "formula_length": 12
    }

    # Example FIB-type data
    data_fib = {
        "question_text": "Find x given the equation: [Eq(a*x, b)]",
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
            "function": "b/a"
        },
        "wrong_answers": None,
        "answer_number": 0,
        "randomization_count": 4,
        "precision": 3,
        "formula_index": 30,
        "formula_length": 12
    }

    # Example integral question
    data_integral = {
        "question_text": "Compute the definite integral from 0 to a: [Integral(x**2, (x, 0, a))]",
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
            "function": "a**3/3"
        },
        "wrong_answers": [
            "a**2/2",
            "2*a**2",
            "No integral done"
        ],
        "answer_number": 2,
        "randomization_count": 3,
        "precision": 3,
        "formula_index": 40,
        "formula_length": 38
    }

    sample_data = [data_mcq, data_fib, data_integral]
    questions = logic_instance.perform_logic_all(sample_data)
    print("Generated questions:", questions)
    logic_instance.generate_final_h5p_set(times=2)
