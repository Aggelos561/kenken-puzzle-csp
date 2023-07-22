# KenKen Solver using Constraint Satisfaction Problem (CSP) in Python

This repository contains a Python implementation of the KenKen game solver using the Constraint Satisfaction Problem (CSP) framework based on the `csp.py` module from the AIMA book (Artificial Intelligence: A Modern Approach).

## Usage

The solver script is `kenken.py`, and it takes the path to a text file containing the KenKen puzzle as input. The file should adhere to a specific format where each line represents a region in the puzzle and contains the target value, arithmetic operation, and the cells within that region.

To run the solver, execute the following command:

```bash
python kenken.py file.txt
```

Replace `file.txt` with the path to the text file containing the KenKen puzzle.

## Examples

We have provided five example puzzles in different text files (`example_3x3.txt`, `example_4x4.txt`, ..., `example_7x7.txt`). Each text file encodes the KenKen puzzle in the specified format.

## Supported Algorithms

The KenKen solver implements the following constraint satisfaction algorithms:

1. **Backtracking:** A basic backtracking algorithm that explores all possible assignments.

2. **Forward Checking:** A backtracking algorithm with forward checking to reduce the domain of unassigned variables.

3. **Forward Checking with MRV and LCV:** A variant of forward checking that uses Minimum Remaining Values (MRV) heuristic to choose the variable with the fewest legal values and Least Constraining Value (LCV) heuristic to select the value that rules out the fewest choices for neighboring variables.

4. **Maintaining Arc Consistency (MAC):** An algorithm that ensures that each value in a variable's domain is consistent with the values in its neighboring variables.

5. **MAC with MRV and LCV:** A variant of MAC that incorporates MRV and LCV heuristics.

6. **Min Conflicts:** A local search algorithm that iteratively improves the current assignment by resolving conflicts.

## Output

Upon executing the solver, it will output the solution using each of the algorithms mentioned above for the given KenKen puzzle. Additionally, for each algorithm, it will display the time taken to solve the puzzle, the total number of conflicts encountered during the search, and the total number of variable assignments made.

## Acknowledgments

The implementation of the Constraint Satisfaction Problem (CSP) framework is based on the `csp.py` module from the AIMA book (Artificial Intelligence: A Modern Approach) authored by Stuart Russell and Peter Norvig.
