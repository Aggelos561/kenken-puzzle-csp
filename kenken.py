from csp import *
from search import *
import time
import sys



class Kenken(CSP):
    
    def __init__(self, kenken_file):
        
        # Variables list
        self.variables = []
        
        # Domains dict for every variable
        self.domains = {}
        
        # Neighbors to apply constraints
        self.neighbors = {}
        
        # Given a cage get get operator and number to equal
        self.cage_to_operator = {}
        
        # Given a point get the cage that belongs
        self.point_to_cage = {}
        
        # Kenken matrix size (quadratic)
        self.__kenken_size = 0
        
        # Number of conflicts
        self.conflicts = 0
        
        # Private method to read kenken input file
        self.__read_kenken_file(kenken_file)
        
        # Every variable has [1, ..., n] numbers domain
        for variable in self.variables:
            self.domains[variable] = [number for number in range(1, self.__kenken_size + 1)]
        
        # Creating the dictionary point_to_cage so we can get with O(1) complexity the cage that a point belongs
        for point in self.variables:
            for cage in self.cage_to_operator:
                if point in cage:
                    self.point_to_cage[point] = cage
            
        # Creating neighbors    
        for variable in self.variables:
            
            neighbors_list = []
            for neighbor in self.variables:
                
                # Variable not having itself as a neighbor
                if variable == neighbor:
                    continue
                
                # If variable and neigbor var in same row or same column then they are neigbors
                if (self.same_row(variable, neighbor) or self.same_column(variable, neighbor)):
                    neighbors_list.append(neighbor)

                # If the variable AND neigbor in same cage then they are also neighbor (so we can check for cage constraints)
                for cage in self.cage_to_operator.keys():
                    if variable in cage and neighbor in cage:
                        if neighbor not in neighbors_list:
                            neighbors_list.append(neighbor)
                            
            self.neighbors[variable] = neighbors_list
                    
        super().__init__(self.variables, self.domains, self.neighbors, self.constraint_check)
       
       
    # Contraint checking method passed in CSP
    def constraint_check(self, a, value_a, b, value_b):
        
        # Every time this method is called infer_assignment has the all the partial assignments
        # that have been stored so far
        current_assignments = self.infer_assignment()
        
        # Using dict to find the cage for a and cage for b points
        cage_for_a = self.point_to_cage[a]
        cage_for_b = self.point_to_cage[b]
        
        # Now that the cages have been found, find the goal number abd operator for this cage
        goal_number_cage_a, operator_cage_a = self.cage_to_operator[cage_for_a]
        goal_number_cage_b, operator_cage_b = self.cage_to_operator[cage_for_b]
        
        # If the size of cage is not one (not equal = operator then) AND the two cages are the same (the two points a and b are in same cage)
        if len(cage_for_a) > 1 and cage_for_a == cage_for_b:
            
            # Creating a list and remove the 2 points a and b
            cage_list = list(cage_for_a)
                
            cage_list.remove(a)
            cage_list.remove(b)
            
            # Adding the values of the two points in a list so they can be calculated with the already assigned once later
            calculations_numbers = [value_a, value_b]
             
            # Getting all the already assigned points from infer assignment that are NOT a and b (no duplicates if a or b already inside)               
            for remaining_point in cage_list:
                if remaining_point in current_assignments.keys() and remaining_point != a and remaining_point != b:
                    cage_list.remove(remaining_point)
                    calculations_numbers.append(current_assignments[remaining_point])
            
            # Getting how many points are still left to be assigned        
            cage_remaining_size = len(cage_list)
            
            # Cage A and Cage B are equal in this statement so i just use cage a values
            
            if operator_cage_a == '+':
                
                # Sum of a + b + already assigned values from infer assignment
                cage_sum = sum(calculations_numbers)
                
                # If the are NOT ANY remaining point to assign then it means that the sum MUST be equal to the number for this cage
                if (not cage_remaining_size):
                    if cage_sum != goal_number_cage_a:
                        self.conflicts += 1
                        return False
                else:
                    # Else if there are still points that need to be assigned then the sum must be < goal number of cage
                    if cage_sum >= goal_number_cage_a:
                        self.conflicts += 1
                        return False
                    
            # "-" cages have only 2 points inside
            elif operator_cage_a == '-':
                if abs(value_a - value_b) != goal_number_cage_a:
                    self.conflicts += 1
                    return False
                
                
            # Same as "+" operator. Checking if all the values of this cage have been assigned
            # If all values assigned then it must be equal to the cage goal number
            # If not all values assigned then it must not be greater than the goal cage number
            elif operator_cage_a == '*':
                cage_product = reduce((lambda x, y: x * y), calculations_numbers)
                
                if (not cage_remaining_size):   
                    if cage_product != goal_number_cage_a:
                        self.conflicts += 1
                        return False
                else:        
                    if cage_product > goal_number_cage_a:
                        self.conflicts += 1
                        return False
                    
            # "/" cages have only 2 points inside
            elif operator_cage_a == '/':
                div_result = value_a / value_b if value_a > value_b else value_b / value_a
                if div_result != goal_number_cage_a:
                    self.conflicts += 1
                    return False
        
        # if cage for point a has only one point inside then the cage has equal operator
        # Checking if values is equal to the goal cage number      
        elif len(cage_for_a) == 1:
            if operator_cage_a == '=':
                if value_a != goal_number_cage_a:
                    self.conflicts += 1
                    return False
        
        # Same for cage B as above
        elif len(cage_for_b) == 1:
            if operator_cage_b == '=':
                if value_b != goal_number_cage_b:
                    self.conflicts += 1
                    return False    
            
        # Even with the above contraint checking if later the points a and b are in same row or col
        # They can change and the constraints are not going to be satisfied
        # For that reason every time it needs to be checked if the cage a AND cage b are equal to the cage goal number
        if not self.cage_contraint(cage_for_a, operator_cage_a, goal_number_cage_a, current_assignments):
            self.conflicts += 1
            return False

        if not self.cage_contraint(cage_for_b, operator_cage_b, goal_number_cage_b, current_assignments):
            self.conflicts += 1
            return False
        
        # Also checking if a and b are in same row or column then they must not have the same values
        if self.same_row(a, b) or self.same_column(a, b):
            if value_a == value_b:
                self.conflicts += 1
                return False
        
        return True
    
    # Single cage constraint checking
    def cage_contraint(self, cage, cage_operator, cage_number, current_assignments):
        
        # ONLY if all the assignments have be done check if the sum/mult is equal
        # to the goal cage number
        assignments_size = 0
        
        for point in cage:
            if point in current_assignments:
                assignments_size += 1

        if assignments_size == len(cage):
            if cage_operator == '*':
                mult = 1
                for point in cage:
                    mult *= current_assignments[point]
            
                if mult != cage_number:
                    return False
            
            elif cage_operator == '+':
                addition = 0
                for point in cage:
                    addition += current_assignments[point]
            
                if addition != cage_number:
                    return False

        return True
    
    # Reading the kenken input file that was given from command line
    def __read_kenken_file(self, kenken_file):
        
        with open(kenken_file) as file:
            
            data = file.read()
            
            # Splitting the cages from input
            cages_list = data.split(',')
            
            # For every cage get the points that are inside
            for cage in cages_list:
                
                positions_list = re.findall("\((.*?)\)", cage) 
                
                cage_positions = []
                
                for position in positions_list:
                    
                    # x, y coordinates
                    x, y = position.split('_')
                    
                    # From the input we can find out the kenken size
                    if int(x) > self.__kenken_size:
                        self.__kenken_size = int(x)
                    
                    # Tuple of coordinates
                    x_y = (int(x), int(y))
                    
                    cage_positions.append(x_y)
                    self.variables.append(x_y)

                # Getting operator +, - , *, /, = for every cage
                operator = cage[-2]

                # Getting the number that the cage must be equal
                number_equal = self.__parse_goal_number(cage)
                
                # Creating the helping dict cage to operator  
                self.cage_to_operator[tuple(cage_positions)] = [number_equal, operator]   

    # Getting the goal number for the cage
    def __parse_goal_number(self, cage):
        number = ''
        start_parsing_result = False

        for char in cage:
            
            if start_parsing_result:
                if  char != '+' and char !='-' and char!='*' and char!='/' and char!='=':
                    number += char
                else:
                    break
                
            if char == '~':
                start_parsing_result = True;

        return int(number)
     
    # if Same x then the 2 points are in same row
    def same_row(self, position1, position2):
        return position1[0] == position2[0]            
     
    # if Same y then the 2 points are in same column    
    def same_column(self, position1, position2):
        return position1[1] == position2[1]            
    
    # Display like a matrix            
    def display(self, assignment):
        
        print()
        assignments = sorted(assignment.items())
        
        index = 1
        for element in assignments:
            print(element[1], end=' ')
            if not (index % self.__kenken_size):
                print()
            index += 1

        print()
       
       
                
if __name__ == '__main__':
    
    # Read kenken input file from command line as parameter
    kenken_file = sys.argv[-1]
    

    # Backtracking
    kenken = Kenken(kenken_file)
    start_time = time.time()
    agent = backtracking_search(kenken)
    total_time = time.time() - start_time
    print('Backtracking')
    print(f'Total time: {total_time}, Total Conflicts: {kenken.conflicts}, Assignments: {kenken.nassigns}')
    kenken.display(agent)
    
    
    # Forward checking
    kenken = Kenken(kenken_file)
    start_time = time.time()
    agent = backtracking_search(kenken, inference=forward_checking)
    total_time = time.time() - start_time
    print('Forward Checking')
    print(f'Total time: {total_time}, Total Conflicts: {kenken.conflicts}, Assignments: {kenken.nassigns}')
    kenken.display(agent)
    
    # Froward checking with mrv and lcv
    kenken = Kenken(kenken_file)
    start_time = time.time()
    agent = backtracking_search(kenken, select_unassigned_variable=mrv, order_domain_values=lcv, inference=forward_checking)
    total_time = time.time() - start_time
    print('Forward Checking, MRV, LCV')
    print(f'Total time: {total_time}, Total Conflicts: {kenken.conflicts}, Assignments: {kenken.nassigns}')
    kenken.display(agent)
    
    # MAC
    kenken = Kenken(kenken_file)
    start_time = time.time()
    agent = backtracking_search(kenken, inference=mac)
    total_time = time.time() - start_time
    print('MAC')
    print(f'Total time: {total_time}, Total Conflicts: {kenken.conflicts}, Assignments: {kenken.nassigns}')
    kenken.display(agent)
    
    # MAC with mrv and lcv
    kenken = Kenken(kenken_file)
    start_time = time.time()
    agent = backtracking_search(kenken, select_unassigned_variable=mrv, order_domain_values=lcv, inference=mac)
    total_time = time.time() - start_time
    print('MAC, MRV, LCV')
    print(f'Total time: {total_time}, Total Conflicts: {kenken.conflicts}, Assignments: {kenken.nassigns}')
    kenken.display(agent)

    # QUESTION 4 Min Conflicts. For kenken > 3 it takes time
    
    # kenken = Kenken(kenken_file)
    # start_time = time.time()
    # agent = min_conflicts(kenken)
    # total_time = time.time() - start_time
    # print('Min Conflicts')
    # print(f'Total time: {total_time}, Total Conflicts: {kenken.conflicts}, Assignments: {kenken.nassigns}')
    # kenken.display(agent)
