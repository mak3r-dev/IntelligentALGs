

# PROJECT : GENETIC ALGORITHM

# OVERVIEW : A CLASSIC ATTEMPT AT IMPLEMENTING GENERIC ALGORITHM FROM SCRATCH
# VERSION : V.0.0.0
import random
CHAR_LIST : list[chr] = [chr(i) for i in range(32, 123)]

# This class models a problem, in this case the word problem
class solution:
    def __init__(self, problem_dimension : int , value : list[str] = None , best : bool = False, max_char_pool : int = 123):
        self.dimension : int = problem_dimension if problem_dimension else 0
        self.max_char_pool : int = max_char_pool
        self.value : list[str] = [] if not value else value
        self.fitness_score : int = problem_dimension if best else 0
        self.h_n = 0

        if (best == False): 
            self.__init_random_solution()

    def __init_random_solution(self):

        for i in range(self.dimension):
            self.value.append(random.choice(CHAR_LIST))

    def reset(self):
        self.value = []
        self.fitness_score = 0

    def calculate_fitness(self, best : solution):
        self.fitness_score = sum([1 if self.value[i] == best.value[i] else 0 for i in range(0,self.dimension)])
        self.h_n = best.fitness_score - self.fitness_score

class GA:

    def __init__(self, pop_size : int, problem_dimension : int, problem_solution : solution):
        self.min_slice : int = 3
        if (problem_dimension < self.min_slice): ValueError("The problem dimension < 3")
        if (pop_size < 3): ValueError("The population size < 3")

        self.population_size : int = pop_size
        self.population_pool : list[solution] = []

        self.problem_dimension : int = problem_dimension
        self.problem_solution : solution = problem_solution
        self.best_solution : solution = solution(self.problem_dimension)
        self.best_solution.calculate_fitness(self.problem_solution)

        self.survivors : list[set[solution]] = []
        self.offsprings : list[solution] = []
        self.generation = 0

        self.__generate_population_pool()

    def GA_Run(self):

        # for i in range(130):
        while self.best_solution.fitness_score < self.problem_solution.fitness_score:  
        
            self.__dominant_selection()
            self.__tournament()
            self.__evaluate()

            self.generation += 1
    
    # Private methods
    def __generate_population_pool(self):

        for i in range(0,self.population_size):
            sol : solution = solution(self.problem_dimension)
            self.population_pool.append(sol)

    def __dominant_selection(self):

        # 1. Calculate fitness scores for each solution in the pool
        for i in range(0,self.population_size):
            candidate : solution = self.population_pool[i]   
            candidate.calculate_fitness(self.problem_solution)        

    def __tournament(self):
        self.survivors = []
        tourny_pairs : list[set[solution]] = []
        dominant_parents : list[solution] = []

        # 1. Generate Tournament pairs
        for i in range(0, self.population_size):
            tourny_candidate1 = self.population_pool[random.randint(0,self.population_size-1)]
            tourny_candidate2 = self.population_pool[random.randint(0,self.population_size-1)]

            new_pairs : list = list()
            new_pairs.extend([tourny_candidate1,tourny_candidate2])

            tourny_pairs.append(new_pairs)

        # 2. Collaspe into suitable candidates
        for tourney_pair in tourny_pairs:
            pair : list[solution] = list(tourney_pair)

            winner : solution = pair[0] if pair[0].fitness_score >= pair[1].fitness_score else pair[1]
            dominant_parents.append(winner)

        # 3. Clamp the dominant_parents
        if (len(dominant_parents) % 2 != 0):
            dominant_parents.append(dominant_parents[random.randint(0,len(dominant_parents) - 1)])

        # 4. Re-pair the dominant solutions
        for i in range(0,len(dominant_parents),2):
            sur_pair : list = list()
            sur_pair.extend([dominant_parents[i],dominant_parents[i+1]])

            self.survivors.append(sur_pair)
    
        # 4. Select new childs using crossover
        self.crossover()
        self.targeted_mutation()

    def __roulette(self):
        total_fitness_of_population : int = sum([sol.fitness_score for sol in self.population_pool])

    def crossover(self):

        slice_length : int = random.randint(self.min_slice,self.problem_dimension - 1)

        for survivor_pair in self.survivors:
            pair : list[solution] = survivor_pair

            survivor1 : solution = pair[0]
            survivor2 : solution = pair[1]

            survivor1_slice : list[list] = [survivor1.value[0 : slice_length], survivor1.value[slice_length:]]
            survivor2_slice : list[list] = [survivor2.value[0 : slice_length], survivor2.value[slice_length:]]

            offspring1 : solution = solution(self.problem_dimension)
            offspring2 : solution = solution(self.problem_dimension)

            offspring1.reset()
            offspring2.reset()

            offspring1.value.extend(survivor1_slice[0])
            offspring1.value.extend(survivor2_slice[1])

            offspring2.value.extend(survivor1_slice[1])
            offspring2.value.extend(survivor2_slice[0])

            self.offsprings.extend([offspring1,offspring2])
    
    # GENERAL SCOPE -  slow
    def mutation(self):
        rate = 1 / self.problem_dimension

        for offspring in self.offsprings:

            for i in range(0,self.problem_dimension):
               if (random.random() < rate):
                   offspring.value[i] = random.choice(CHAR_LIST)

    # GENERAL SCOPE - mildly fast
    def hill_climbing(self):
        rate = 1 / self.problem_dimension

        for offspring in self.offsprings:

            new_value = solution(self.problem_dimension)
            new_value.value = offspring.value
            for i in range(0,self.problem_dimension):
               if (random.random() < rate):
                   new_value.value[i] = random.choice(CHAR_LIST)

            new_value.calculate_fitness(self.problem_solution)
            if new_value.fitness_score >= offspring.fitness_score:
                offspring.value = new_value.value

    # TARGETED SCOPE - very fast
    def targeted_mutation(self):

        for offspring in self.offsprings:

            for i in range(0,self.problem_dimension):
                if (offspring.value[i] != self.problem_solution.value[i]):
                    offspring.value[i] = random.choice(CHAR_LIST)    

    def __evaluate(self):
    
        for offspring in self.offsprings:
            offspring.calculate_fitness(self.problem_solution)   

            # greedy best first - improves convergence time midly
            if offspring.h_n < self.best_solution.h_n:
                self.best_solution = offspring

            # NORMAL - Adds a small overhead to convergence time
            # if offspring.fitness_score > self.best_solution.fitness_score:         
            #     self.best_solution = offspring

        if self.best_solution.fitness_score < self.problem_solution.fitness_score:
            self.population_pool = []
            self.population_pool.extend(self.offsprings)
            self.offsprings = []

        print(f"Best Solution is, {self.best_solution.value}")

p_d = 11
GENETIC_ALGORITHMS = GA(200,p_d,solution(p_d,['H','E','L','L','O', ' ','W','O','R','L','D'],True))
GENETIC_ALGORITHMS.GA_Run()