import os
import sys
import json
import shutil
import time
import uuid
import zipfile


def create_h5p(directory_path, h5p_filename):
    if not os.path.isdir(directory_path):
        raise ValueError("Directory path does not exist.")
    
    try:
        original_dir = os.getcwd()
        os.chdir(directory_path)
        with zipfile.ZipFile(os.path.join(original_dir, h5p_filename), 'w') as h5p_file:
            for root, _, files in os.walk('.'):
                for file in files:
                    file_path = os.path.join(root, file)
                    h5p_file.write(file_path, arcname=file_path)
                    print(f"Added {file_path} as {file_path}")
        os.chdir(original_dir)
    except Exception as e:
        print(f"Error while creating the H5P file: {e}")
        os.chdir(original_dir)
        raise


def parse_line(line, question):
    line_content = line
    if line.startswith("*"):
        line_content = line[1:].strip()
        answer = {
            "text": "",
            "correct": True,
            "tipsAndFeedback": {}
        }
    else:
        answer = {
            "text": "",
            "correct": False,
            "tipsAndFeedback": {}
        }

    tip_index = line_content.find("TIP:")
    ysel_index = line_content.find("YSEL:")
    nsel_index = line_content.find("NSEL:")

    if tip_index != -1:
        end_index = tip_index
    elif ysel_index != -1:
        end_index = ysel_index
    elif nsel_index != -1:
        end_index = nsel_index
    else:
        end_index = len(line_content)

    answer["text"] = line_content[:end_index].strip()

    if tip_index != -1:
        tip_start = tip_index + len("TIP:")
        if ysel_index != -1:
            tip_end = min(ysel_index, nsel_index if nsel_index != -1 else len(line_content))
        elif nsel_index != -1:
            tip_end = nsel_index
        else:
            tip_end = len(line_content)
        answer["tipsAndFeedback"]["tip"] = line_content[tip_start:tip_end].strip()
    else:
        answer["tipsAndFeedback"]["tip"] = ""

    if ysel_index != -1:
        ysel_start = ysel_index + len("YSEL:")
        if nsel_index != -1:
            ysel_end = nsel_index
        else:
            ysel_end = len(line_content)
        answer["tipsAndFeedback"]["chosenFeedback"] = line_content[ysel_start:ysel_end].strip()
    else:
        answer["tipsAndFeedback"]["chosenFeedback"] = ""

    if nsel_index != -1:
        nsel_start = nsel_index + len("NSEL:")
        answer["tipsAndFeedback"]["notChosenFeedback"] = line_content[nsel_start:].strip()
    else:
        answer["tipsAndFeedback"]["notChosenFeedback"] = ""

    question["params"]["answers"].append(answer)


def parse_fib(line, question):
    if not line:
        return

    parts = line.split('*')
    formatted_question = ""
    blanks = []

    for i, part in enumerate(parts):
        if i % 2 == 0:
            formatted_question += part
        else:
            blank_id = len(blanks) + 1
            formatted_question += f'{{{blank_id}}}'
            blanks.append(part.strip())

    question["params"]["questions"].append({
        "question": formatted_question.strip(),
        "answers": [{"text": blank} for blank in blanks]
    })


def main():
    if len(sys.argv) != 3:
        print("USAGE: python-script.py controlFile.txt mcQuestionsFile.txt")
        sys.exit(1)

    control_file = sys.argv[1]
    questions_file = sys.argv[2]

    if not os.path.isfile(control_file):
        control_file = input(f"ERROR: {control_file} does not exist. Enter the control filename (^C to quit): ")

    if not os.path.isfile(questions_file):
        questions_file = input(f"ERROR: {questions_file} does not exist. Enter the questions filename (^C to quit): ")

    for file in ["h5p-pr.json", "content-pr.json"]:
        if os.path.isfile(file):
            os.remove(file)

    time.sleep(3)

    control_params = {}
    with open(control_file, 'r') as f:
        for line in f:
            key, value = line.strip().split(':', 1)
            control_params[key.strip()] = value.strip().strip('"')

    print("The following control parameters were set for the H5P to be made:")
    for key, value in control_params.items():
        print(f"{key}: {value}")

    h5p_data = {
        "title": control_params.get("TITLE", "THIS IS THE TITLE"),
        "language": "und",
        "mainLibrary": "H5P.QuestionSet",
        "embedTypes": ["div"],
        "authors": [{"name": control_params.get("AUTHOR", "I am The Author"), "role": "Author"}],
        "license": control_params.get("LICENSE", "ODC PDDL"),
        "defaultLanguage": "en",
        "preloadedDependencies": [
            {"machineName": "H5P.Image", "majorVersion": "1", "minorVersion": "1"},
            {"machineName": "H5P.MultiChoice", "majorVersion": "1", "minorVersion": "16"},
            {"machineName": "H5P.Blanks", "majorVersion": "1", "minorVersion": "14"},
            {"machineName": "H5P.TextUtilities", "majorVersion": "1", "minorVersion": "3"},
            {"machineName": "FontAwesome", "majorVersion": "4", "minorVersion": "5"},
            {"machineName": "H5P.JoubelUI", "majorVersion": "1", "minorVersion": "3"},
            {"machineName": "H5P.Transition", "majorVersion": "1", "minorVersion": "0"},
            {"machineName": "H5P.FontIcons", "majorVersion": "1", "minorVersion": "0"},
            {"machineName": "H5P.Question", "majorVersion": "1", "minorVersion": "5"},
            {"machineName": "H5P.DragQuestion", "majorVersion": "1", "minorVersion": "14"},
            {"machineName": "jQuery.ui", "majorVersion": "1", "minorVersion": "10"},
            {"machineName": "H5P.QuestionSet", "majorVersion": "1", "minorVersion": "20"},
            {"machineName": "H5P.Video", "majorVersion": "1", "minorVersion": "6"},
            {"machineName": "H5P.MathDisplay", "majorVersion": "1", "minorVersion": "0"}
        ]
    }

    with open("h5p-pr.json", 'w') as f:
        json.dump(h5p_data, f, indent=2)

    content_data = {
        "introPage": {
            "showIntroPage": True,
            "startButtonText": "Start Quiz",
            "title": control_params.get("TITLE", "THIS IS THE TITLE"),
            "introduction": f"<p>{control_params.get('INTRODUCTION', '')}<br>\n&nbsp;</p>\n"
        },
        "progressType": "dots",
        "passPercentage": int(control_params.get("PASS_PERCENTAGE", 50)),
        "disableBackwardsNavigation": control_params.get("DISABLE_BACKWARDS_NAVIGATION", "false").lower() == "true",
        "randomQuestions": control_params.get("RANDOM_QUESTIONS", "true").lower() == "true",
        "endGame": {
            "showResultPage": True,
            "showSolutionButton": True,
            "showRetryButton": True,
            "noResultMessage": "Finished",
            "message": "Your result:",
            "scoreBarLabel": "You got @finals out of @totals points",
            "overallFeedback": [{"from": 0, "to": 100}],
            "solutionButtonText": "Show solution",
            "retryButtonText": "Retry",
            "finishButtonText": "Finish",
            "submitButtonText": "Submit",
            "showAnimations": False,
            "skippable": False,
            "skipButtonText": "Skip video"
        },
        "override": {"checkButton": True},
        "texts": {
            "prevButton": "Previous question",
            "nextButton": "Next question",
            "finishButton": "Finish",
            "submitButton": "Submit",
            "textualProgress": "Question: @current of @total questions",
            "jumpToQuestion": "Question %d of %total",
            "questionLabel": "Question",
            "readSpeakerProgress": "Question @current of @total",
            "unansweredText": "Unanswered",
            "answeredText": "Answered",
            "currentQuestionText": "Current question",
            "navigationLabel": "Questions"
        },
        "poolSize": int(control_params.get("POOL_SIZE", 5)),
        "questions": []
    }

    with open(questions_file, 'r') as f:
        questions = f.readlines()

    question = None
    for line in questions:
        line = line.strip()

        if not line:
            continue

        if line.startswith("MCQ:") or line.startswith("TF:"):
            if question:
                content_data["questions"].append(question)
            question_type = line.split(':')[0]
            question_text = line[len(question_type) + 1:].strip()
            question = {
                "library": "H5P.MultiChoice 1.16",
                "params": {
                    "question": question_text,
                    "answers": []
                },
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "contentType": "Multiple Choice",
                    "license": "U",
                    "title": "Untitled Multiple Choice"
                }
            }
            continue 

        elif line.startswith("FIB:"):
            if question:
                content_data["questions"].append(question)
            question_type = line.split(':')[0]
            question_text = line[len(question_type) + 1:].strip()
            print(f"Question: {question_text}")

            firstIndex = -1
            secondIndex = -1
            for i in range(len(question_text)):
                if question_text[i] == "*":
                    if firstIndex == -1:
                        firstIndex = i
                    elif secondIndex == -1:
                        secondIndex = i
                        break
            answer = question_text[firstIndex+1:secondIndex]

            question_text = f"{question_text}"
            question = {
                "library": "H5P.Blanks 1.14",
                "Text": "Fill in the blanks",
                "params": {
                    "questions": [
                        question_text
                    ]
                },
                "answers": [
                  {
                    "text": answer,
                    "correct": True
                  }
                ],
                "subContentId": str(uuid.uuid4()),
                "metadata": {
                    "contentType": "Fill in the Blanks",
                    "license": "U",
                    "title": "Untitled Fill in the Blanks"
                }
            }
            continue

        if question["library"] == "H5P.Blanks 1.14":
            parse_fib(line.strip(), question)
        else:
            parse_line(line.strip(), question)

    if question:
        content_data["questions"].append(question)

    with open("content-pr.json", 'w') as f:
        json.dump(content_data, f, indent=2)

    minify_json("h5p-pr.json", "h5p.json")
    minify_json("content-pr.json", "content.json")
    
    name_h5p_dir = control_params.get("NAME_H5P", "myMCQ-fb.h5p").replace('.h5p', '')
    if os.path.isdir(name_h5p_dir):
        shutil.rmtree(name_h5p_dir)

    shutil.copytree("h5p-mcq-616_libs", name_h5p_dir)
    os.chmod(name_h5p_dir, 0o755)

    content_dir = os.path.join(name_h5p_dir, "content")
    os.makedirs(content_dir, exist_ok=True)

    shutil.move("h5p.json", os.path.join(name_h5p_dir, "h5p.json"))
    shutil.move("content.json", os.path.join(content_dir, "content.json"))

    shutil.move("h5p-pr.json", os.path.join(name_h5p_dir, "h5p-pr.json"))
    shutil.move("content-pr.json", os.path.join(content_dir, "content-pr.json"))

    output_h5p_file = f"{name_h5p_dir}.h5p"
    print(f"Creating H5P file: {os.getcwd()}")

    create_h5p(name_h5p_dir, output_h5p_file)

    shutil.rmtree(name_h5p_dir)

    print("Done.")


def minify_json(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    with open(output_file, 'w') as f:
        json.dump(data, f, separators=(',',':'),indent=2)
        f.write('\n')


if __name__ == "__main__":
    main()