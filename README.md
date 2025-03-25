# randomq-generator
This repository contains a GUI application that generates a pool of randomized .txt and h5p question files based on user-defined latex functions and parameters. 

### Notice 
This project was created by [chryysmad](https://github.com/chryysmad) and [shadygm](https://github.com/shadygm) as part of [Tamás Görbe's](https://www.rug.nl/staff/t.f.gorbe/?lang=en) Project Calculus, that aims for the creation of an adaptive educational tool that will enhance student engagement and success in Calculus.

## Major Features

- **Randomized Question Generation:**  
  Define custom parameters (e.g., range, step, exclusions) to automatically randomize values and generate multiple variants of each question.

- **Support for Multiple Question Types:**  
  Seamlessly create both Multiple-Choice (MCQ) and Fill-in-the-Blank (FIB) questions, with dynamic generation of answer choices based on the randomized parameters.

- **LaTeX & Sympy Integration:**  
  Use LaTeX to format mathematical expressions and leverage Sympy for parsing, substituting, and evaluating these expressions, ensuring precise computation.

- **Automated File Output:**  
  Generates output files in both JSON and plain text formats, facilitating easy review and integration with other educational tools.

- **H5P File Generation:**  
  Converts the generated text files into interactive H5P content, enhancing the delivery of educational materials with engaging digital formats.

- **Batch Processing Capability:**  
  Process multiple question definitions at once to produce comprehensive sets of randomized questions, and even combine them into final aggregated outputs.

- **Configurable Precision and Robust Error Handling:**  
  Allows users to set the numerical precision for evaluated answers, while built-in error handling ensures reliable execution across various scenarios.


## Getting Started 
To get a local copy up and running, follow these steps

### Prerequisites
* **Linux Terminal/Command Prompt:** Access is necessary to run the Python commands.
* **Python 3.x:** Required for the script to run and can be downloaded from the [official website](https://www.python.org/downloads/).


### Setting up 
1. Clone the repository.
```
git clone https://github.com/chryysmad/randomq-generator.git
```

### Running the Script
1. Enter the directory in which the cloned repository is located from your terminal.
```
cd randomq-generator
``` 

2. Install the dependencies.
```
pip install -r requirements.txt
```

3. Run the command.
```
python3 main.py 
```


<a rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">
  <img alt="Creative Commons License" style="border-width:0" src="https://i.creativecommons.org/l/by-nc-sa/4.0/80x15.png" />
</a><br />
<span xmlns:dct="http://purl.org/dc/terms/" property="dct:title">randomq-generator</span> by 
<a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/chryysmad" property="cc:attributionName" rel="cc:attributionURL">chryysmad</a> and 
<a xmlns:cc="http://creativecommons.org/ns#" href="https://github.com/shadygm" property="cc:attributionName" rel="cc:attributionURL">shadygm</a> 
is licensed under a 
<a rel="license" href="https://creativecommons.org/licenses/by-nc-sa/4.0/">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License</a>.<br />
Based on a work at 
<a xmlns:dct="http://purl.org/dc/terms/" href="https://github.com/chryysmad/randomq-generator" rel="dct:source">https://github.com/chryysmad/randomq-generator</a>.
