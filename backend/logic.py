
class Logic:
    def __init__(self, controller):
        self.controller = controller

    def perform_logic(self):
        shared_data = self.controller.shared_data
        
        correct_answer = shared_data.get("correct_answer")
        wrong_answers = shared_data.get("wrong_answers")
        answer_number = shared_data.get("answer_number")
        

        print(f"Correct Answer: {correct_answer}")
        print(f"Wrong Answers: {wrong_answers}")
        print(f"Number of Wrong Answers to Display: {answer_number}")

