import sympy as sp
from sympy.parsing.latex import parse_latex

def test_latex(input_text):
    input = parse_latex(input_text)

    print("Parsed expression:", input)
    # Assume that you are given a valid latex expression with a valid equation/problem
    # Your task is to solve the equation
    # and print the solution

    # Code:
    # Parse the equation is already handled by parse_latex and sympify above.
    # Check if the parsed expression is an equation and solve it.
    if input.is_Equality:
        # Solve the equation for the free symbols present in the equation.
        solutions = sp.solve(input)
        print("Solution:", solutions)
    # You should also be able to solve things such as definite integrals
    elif isinstance(input, sp.Integral):
        # Evaluate the definite integral
        result = input.doit()
        print("Result:", result)
    elif isinstance(input, sp.Mul):
        # If the input is a multiplication expression, we can evaluate it directly
        result = input.doit()
        print("Result:", result)

    # Automatically solve whatever expression is given
    print("Automatically solved expression:", input.doit())





if __name__ == "__main__":
    # Test whether things such as 10*x = 40 are parsed correctly
    test_latex(r"10x = 40")
    print()
    # Test whether things such as 1/2 x = 40
    test_latex(r"\frac{1}{2} x = 40")
    print()
    # simple definite integral
    test_latex(r"\int_0^1 x^2 dx")
    print()
    # simple derivative
    test_latex(r"\frac{d}{dx} x^2")
    # simple limit
    test_latex(r"\lim_{x \to 0} \frac{\sin x}{x}")