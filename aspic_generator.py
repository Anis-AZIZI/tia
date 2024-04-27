
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from operator import itemgetter

class Literal:
    def __init__(self, name, is_negative=False):
        self.name = name
        self.is_negative = is_negative
    
    def __repr__(self):
        return f"{'¬' if self.is_negative else ''}{self.name}"

    def __eq__(self, other):
        if not isinstance(other, Literal):
            return NotImplemented
        return self.name == other.name and self.is_negative == other.is_negative

    def __hash__(self):
        return hash((self.name, self.is_negative))

class Rule:
    def __init__(self, premises, conclusion, is_defeasible=False, reference='', rule_weight=0):
        self.premises = frozenset(premises)  # Convertit les prémises en frozenset
        self.conclusion = conclusion
        self.is_defeasible = is_defeasible
        self.reference = reference
        self.rule_weight = rule_weight
    
    def __repr__(self):
        premises_str = ', '.join(map(str, self.premises))
        return f"{self.reference}: {premises_str} {'⇒' if self.is_defeasible else '→'} {self.conclusion}"
    def __eq__(self, other):
        if not isinstance(other, Rule):
            return NotImplemented
        return (self.premises == other.premises and self.conclusion == other.conclusion and 
                self.is_defeasible == other.is_defeasible and self.reference == other.reference)

    def __hash__(self):
        return hash((self.premises, self.conclusion, self.is_defeasible, self.reference))

class Argument:
    def __init__(self, top_rule, sub_arguments, name):
        self.top_rule = top_rule
        self.sub_arguments = frozenset(sub_arguments)  # Convertit sub_arguments en frozenset
        self.name = name

    def __repr__(self):
        rule_symbol = '⇒' if self.top_rule.is_defeasible else '→'
        if not self.sub_arguments:
            premises_str = ', '.join(map(str, self.top_rule.premises))
            return f"{self.name}:{premises_str} {rule_symbol} {self.top_rule.conclusion}"
        else:
            sub_args_repr = " ".join(arg.name for arg in self.sub_arguments)
            return f"{self.name}: {sub_args_repr} {rule_symbol} {self.top_rule.conclusion}"
        
    def __eq__(self, other):
        return isinstance(other, Argument) and \
            self.top_rule.conclusion == other.top_rule.conclusion and \
            self.sub_arguments == other.sub_arguments

    def __hash__(self):
        return hash((self.top_rule.conclusion, self.sub_arguments))


class ArgumentationFramework:
    def __init__(self, rules):
        self.rules = rules
        self.arguments = []
        self.argument_by_conclusion = {}
        self.argument_counter = 0
        self.generate_all_arguments()

    #getter for the arguments
    def get_arguments(self):
        return self.arguments

    def generate_all_arguments(self):
        self.arguments.clear()
        self.argument_by_conclusion.clear()
        self.initialize_arguments()
        changed = True
        while changed:
            changed = self.combine_arguments()


    def initialize_arguments(self):
        # Initialize arguments from rules with no premises (facts)
        for rule in self.rules:
            if not rule.premises:
                self.create_argument(rule, set())

    def create_argument(self, rule, sub_arguments):
        # Ensure unique names for each argument
        self.argument_counter += 1
        argument_name = f'A{self.argument_counter}'
        new_argument = Argument(rule, sub_arguments, argument_name)
        self.arguments.append(new_argument)
        # Group arguments by their conclusion for easier access
        self.argument_by_conclusion.setdefault(rule.conclusion, []).append(new_argument)

    def combine_arguments(self):
        new_arguments_formed = False
        for rule in self.rules:
            if rule.premises:
                # Generate all possible combinations of existing arguments that match the premises
                possible_combinations = [self.argument_by_conclusion.get(p, []) for p in rule.premises]
                for combo in itertools.product(*possible_combinations):
                    if self.validate_combination(rule, combo):
                        sub_arguments = frozenset(combo)
                        # Ensure no duplicate arguments with the same premises and top rule
                        if not any(arg.sub_arguments == sub_arguments and arg.top_rule == rule for arg in self.arguments):
                            self.create_argument(rule, sub_arguments)
                            new_arguments_formed = True
        return new_arguments_formed

    def validate_combination(self, rule, combination):
        # Check if the combination of arguments' conclusions matches the rule's premises exactly
        argument_conclusions = {arg.top_rule.conclusion for arg in combination}
        return argument_conclusions == set(rule.premises)

    def show_all_arguments(self):
        for argument in self.arguments:
            print(f" {argument}")

    def show_detailed_arguments(self):
        for argument in self.arguments:
            sub_args = ' '.join(arg.name for arg in argument.sub_arguments)
            print(f"{argument.name}: {sub_args} -> {argument.top_rule.conclusion} using {argument.top_rule.reference}")

    def count_arguments(self):
        return len(self.arguments)
    
    def get_defeasible_rules_for_argument(self, argument):
        defeasible_rules = set()
        for rule in self.rules:
            if rule.is_defeasible:
                # Vérifier si l'argument est basé sur cette règle
                if argument.top_rule == rule:
                    defeasible_rules.add(rule)
                # Vérifier si la conclusion de l'argument est dans les prémices de la règle
                if argument.top_rule.conclusion in rule.premises:
                    defeasible_rules.add(rule)
                # Vérifier si la conclusion de la règle est dans les prémices de l'argument
                for premise in argument.top_rule.premises:
                    if premise in rule.premises:
                        defeasible_rules.add(rule)
        if not defeasible_rules:
            print(f"No defeasible rules found for argument {argument.name}.")
        return defeasible_rules


    
    def get_last_defeasible_rules_for_argument(self, argument):
        last_defeasible_rules = set()
        visited_rules = set()

        def dfs(rule):
            visited_rules.add(rule)
            if rule.is_defeasible:
                last_defeasible_rules.add(rule)
            for premise in rule.premises:
                for r in self.rules:
                    if r.conclusion == premise and r not in visited_rules:
                        dfs(r)

        dfs(argument.top_rule)
        return last_defeasible_rules
    
    def get_sub_arguments(self, argument):
        sub_arguments = set()
        visited_arguments = set()

        def dfs(arg):
            visited_arguments.add(arg)
            sub_arguments.add(arg)
            for sub_arg in arg.sub_arguments:
                if sub_arg not in visited_arguments:
                    dfs(sub_arg)

        dfs(argument)
        return sub_arguments

    def detect_undercuts(self):
        undercuts = []
        rule_to_arguments = {}
        negated_rules_to_arguments = {}

        # Function to recursively check if an argument uses a specific rule
        def uses_rule(arg, rule_ref):
            if arg.top_rule.reference == rule_ref:
                return True
            return any(uses_rule(sub_arg, rule_ref) for sub_arg in arg.sub_arguments)

        # Map arguments to rules they directly or indirectly use
        for arg in self.arguments:
            for rule in self.rules:
                if uses_rule(arg, rule.reference):
                    rule_to_arguments.setdefault(rule.reference, []).append(arg)
                    #print(f"Rule {rule.reference} directly or indirectly used by argument {arg.name}")

        # Map negations directly mentioned in conclusions to arguments
        for arg in self.arguments:
            if isinstance(arg.top_rule.conclusion, Literal) and arg.top_rule.conclusion.is_negative:
                negated_rule_ref = arg.top_rule.conclusion.name.lstrip('¬')  # Handle negation symbol correctly
                negated_rules_to_arguments[negated_rule_ref] = arg
                #print(f"Negated rule {negated_rule_ref} mapped to argument {arg.name}")

        # Determine undercuts: Arguments asserting negations vs those using the negated rules
        for neg_rule_ref, negating_arg in negated_rules_to_arguments.items():
            if neg_rule_ref in rule_to_arguments:
                for target_arg in rule_to_arguments[neg_rule_ref]:
                    undercuts.append((negating_arg, target_arg))
                    #print(f"Undercut detected: {negating_arg.name} undercuts {target_arg.name}")

        if not undercuts:
            print("No undercuts found. Check the mappings and rules.")

        return undercuts

    def detect_rebuttals(self):
        rebuttals_by_conclusion = {}
        for arg1 in self.arguments:
            for arg2 in self.arguments:
                if arg1 != arg2:
                    # Check direct contradiction: Conc(arg1) is the negation of Conc(arg2)
                    if arg1.top_rule.conclusion.is_negative != arg2.top_rule.conclusion.is_negative and \
                    arg1.top_rule.conclusion.name == arg2.top_rule.conclusion.name:
                        rebuttals_by_conclusion.setdefault(arg1.top_rule.conclusion, []).append((arg1, arg2))
                        rebuttals_by_conclusion.setdefault(arg2.top_rule.conclusion, []).append((arg2, arg1))
        return rebuttals_by_conclusion


    def is_sub_argument(self, arg, possible_parent):
        # Check if 'arg' is a sub-argument of 'possible_parent', recursively
        if arg in possible_parent.sub_arguments:
            return True
        for sub_arg in possible_parent.sub_arguments:
            if self.is_sub_argument(arg, sub_arg):
                return True
        return False
    
    def print_rebuttals(self, rebuttals_by_conclusion):
        print("Rebuttals:")
        total_rebuttals = 0
        for conclusion, rebuttals in rebuttals_by_conclusion.items():
            if rebuttals:
                print(f"Rebuttals for conclusion {conclusion}:")
                seen = set()
                for arg1, arg2 in rebuttals:
                    pair = (arg1.name, arg2.name)
                    if pair not in seen and (arg2.name, arg1.name) not in seen:
                        print(f"{arg1.name} rebuts {arg2.name}")
                        seen.add(pair)
                        total_rebuttals += 1
        print(f"Total number of rebuttals: {total_rebuttals}")


    def count_rebuttals(self):
        return len(self.detect_rebuttals())
    
    def get_attacks(self):
        # Get all attacks, which are undercuts and rebuttals in your framework
        undercuts = self.detect_undercuts()
        rebuttals = self.detect_rebuttals()
        attacks = undercuts + [rebuttal for conclusions in rebuttals.values() for rebuttal in conclusions]
        return attacks

    def compute_burdens_with_defeats(self, defeats, max_depth):
        arguments = [arg.name for arg in self.arguments]
        
        # Create a dictionary to keep track of which arguments are defeated
        defeated_args = {defeat[1].name for defeat in defeats}
        
        # Attacks dictionary initialization considering the defeats
        attacks = {}
        for arg in self.arguments:
            # Exclude attacks from arguments that are defeated
            attacks[arg.name] = [attacker.name for attacker, attacked in self.get_attacks()
                                if attacked.name == arg.name and attacker.name not in defeated_args]

        # Initial burdens calculation at depth 0 for all arguments
        burdens = {(arg, 0): 1 for arg in arguments}

        # Defeated arguments should not have their burdens calculated beyond depth 0
        for arg in defeated_args:
            for depth in range(1, max_depth + 1):
                burdens[(arg, depth)] = float('inf')  # Assigning 'infinity' to defeated arguments
        
        # Now calculate burdens for non-defeated arguments
        for depth in range(1, max_depth + 1):
            for arg in arguments:
                if arg not in defeated_args:
                    # Sum of the inverse of burdens of attackers at previous depth
                    burdens[(arg, depth)] = 1 + sum(1 / burdens[(attacker, depth - 1)] for attacker in attacks[arg])

        # Extracting burden numbers for each argument up to the specified depth
        burden_numbers = {arg: [burdens[(arg, depth)] for depth in range(max_depth + 1)]
                        for arg in arguments}

        return burden_numbers

    def rank_arguments_with_defeats(self, burden_numbers):
        # Sort the arguments lexicographically by burden numbers
        return sorted(burden_numbers.keys(), key=lambda arg: burden_numbers[arg])

    
    # compare arguments given preferences between arguments and principles

class ArgumentComparator:
    @staticmethod
    def compare_arguments_with_preferences(arguments):
        # Création d'un dictionnaire pour stocker la force de chaque argument
        argument_strengths = {}
        
        # Parcours de tous les arguments
        for arg in arguments:
            # Initialisation de la force de l'argument
            argument_strength = 0
            
            # Ignorer le poids des règles dans un contexte démocratique
            
            # Parcours des attaques subies par l'argument
            for attack in arg.attacks:
                # Calcul de la force de l'attaque (ignore le poids de la règle)
                attack_strength = 1  # Toutes les attaques ont la même force dans un cadre démocratique
                
                # Comparaison de la force de l'attaque avec la force actuelle de l'argument
                if attack_strength > argument_strength:
                    argument_strength = attack_strength  # Mise à jour de la force de l'argument si nécessaire
            
            # Stockage de la force finale de l'argument dans le dictionnaire
            argument_strengths[arg] = argument_strength
        
        # Tri des arguments selon leur force, du plus fort au plus faible
        sorted_arguments = sorted(argument_strengths.items(), key=lambda x: x[1], reverse=True)
        
        # Retourner les arguments triés
        return sorted_arguments






# Function to create contrapositions for strict rules
# Function to create contrapositions for strict rules with multiple premises
# Adjusting the create_contrapositions function to handle all cases
def create_contrapositions(strict_rules, num_rules):
    contrapositions = []
    num_rules = num_rules
    for rule in strict_rules:
        # When there are no premises
        if len(rule.premises) == 0:
            conclusion = Literal(rule.conclusion.name, not rule.conclusion)
            contraposition_rule = Rule(set(), conclusion, reference="r" + str(num_rules))
        #    contrapositions.append(contraposition_rule)
        # When there is exactly one premise
        elif len(rule.premises) == 1:
            premise = next(iter(rule.premises))
            new_premises = {Literal(rule.conclusion.name, not rule.conclusion.is_negative)}
            new_conclusion = Literal(premise.name, not premise.is_negative)
            contraposition_rule = Rule(new_premises, new_conclusion, reference="r" + str(num_rules))
            contrapositions.append(contraposition_rule)
        # When there are multiple premises
        else:
            for premise in rule.premises:
                new_premises = set(rule.premises - {premise})  # All premises except the current one
                new_premises.add(Literal(rule.conclusion.name, not rule.conclusion.is_negative))
                new_conclusion = Literal(premise.name, not premise.is_negative)
                contraposition_rule = Rule(new_premises, new_conclusion, reference="r" + str(num_rules))
                contrapositions.append(contraposition_rule)
                num_rules += 1
            num_rules -=1
        num_rules += 1
    return contrapositions





# Define strict rules
strict_rules = [
    Rule([], Literal('a'), reference='r1'),              
    Rule([Literal('b'), Literal('d')], Literal('c'), reference='r2'),
    Rule([Literal('c', is_negative=True)], Literal('d'), reference='r3')
]

# Define defeasible rules
defeasible_rules = [
    Rule([Literal('a')], Literal('d', is_negative=True), is_defeasible=True, reference='r4'),
    Rule([], Literal('b'), is_defeasible=True, reference='r5',rule_weight=1),
    Rule([], Literal('c', is_negative=True), is_defeasible=True, reference='r6',rule_weight=1),
    Rule([], Literal('d'), is_defeasible=True, reference='r7'),
    Rule([Literal('c')], Literal('e'), is_defeasible=True, reference='r8'),
    Rule([Literal('c', is_negative=True)], Literal('r4', is_negative=True), is_defeasible=True, reference='r9')
]

rules = strict_rules + defeasible_rules

# Print the rules and their contrapositions

contraposition_rules = create_contrapositions(strict_rules, len(strict_rules) + len(defeasible_rules))
print("Original Strict Rules:")
for rule in strict_rules:
    print(rule)
print("Original Defeasible Rules:")
for rule in defeasible_rules:
    print(rule)
print("Contrapositions:")
for rule in contraposition_rules:
    print(rule)

# # Examples based on the provided information
# a = Literal('a')
# not_b = Literal('b', is_negative=True)
# c = Literal('c')
# not_a = Literal('a', is_negative=True) # Corrected definition

# rule1 = Rule([a, not_b], Literal('e'), reference='r1')
# rule2 = Rule([a], not_a, is_defeasible=True, reference='r2')
# rule3 = Rule([], not_a, is_defeasible=True, reference='r3')
# argument1 = Argument(rule1, set(), 'A1')
# argument2 = Argument(rule2, {argument1}, 'A2')

# # Display the created objects
# print(a)
# print(not_b)
# print(c)
# print(rule1)
# print(rule2)
# print(rule3)
# print(argument1)
# print(argument2)
# # Tester l'égalité entre les littéraux
# a_duplicate = Literal('a')
# print("a == a_duplicate (devrait être True):", a == a_duplicate)
# print("a == not_b (devrait être False):", a == not_b)

# # Tester l'égalité entre les règles
# # Correction de la création de la règle dupliquée pour tester l'égalité
# rule1_duplicate = Rule([a, not_b], Literal('e'), reference='r1')
# print("rule1 == rule1_duplicate (devrait être True):", rule1 == rule1_duplicate)
# print("rule1 == rule2 (devrait être False):", rule1 == rule2)

# # Tester l'égalité entre les arguments
# argument1_duplicate = Argument(rule1, set(), 'A1')
# print("argument1 == argument1_duplicate (devrait être True):", argument1 == argument1_duplicate)
# print("argument1 == argument2 (devrait être False):", argument1 == argument2)

# # Tester les valeurs de hachage
# print("Valeur de hachage de argument1:", hash(argument1))
# print("Valeur de hachage de argument2:", hash(argument2))

# Combine original and contraposition rules with defeasible rules
all_rules = strict_rules + contraposition_rules + defeasible_rules

# Now you create the ArgumentationFramework with all the rules
af = ArgumentationFramework(all_rules)

# Step 3: Generate and Combine Arguments
#af.generate_all_arguments()
#af.combine_arguments()  # This should create more complex arguments by combining existing ones

# Step 4: Display Results
print("All arguments:")
af.show_all_arguments()
# af.show_detailed_arguments()
print("Total number of arguments:", af.count_arguments())
# A1 : -> a
# A2 : => b
# A3 : => ¬c
# A4 : => d
# A5 : A3 -> d
# A6 : A3 => ¬r4 
# A7 : A1 => ¬d
# A8 : A4, A3 -> ¬c
# A9 : A4, A2 -> c
# A10 : A3, A2 -> ¬d
# A11 : A7 -> c
# A12 : A9 => e
# A13 : A10 -> c
# A14 : A5, A3 -> ¬b
# A15 : A5, A2 -> c
# A16 : A11  => e
# A17 :  A13 => e
# A18 : A15 => e 

# # #  Get all defeasible rules associated with an argument
# argument = af.arguments[4]  # we suppose that the argument is the 5th elemen

# # Obtain the defeasible rules for the argument
# defeasible_rules = af.get_defeasible_rules_for_argument(argument)

# # Display the defeasible rules
# print("Defeasible Rules for the argument:")
# for rule in defeasible_rules:
#     print(rule)

# # # Step 6: Get the last defeasible rules associated with an argument
# # Obtenir les dernières règles déféasibles pour l'argument donné
# last_defeasible_rules = af.get_last_defeasible_rules_for_argument(argument)

# # Afficher les dernières règles déféasibles obtenues
# print("Last Defeasible Rules for the argument:")
# for rule in last_defeasible_rules:
#     print(rule)

# # Get all sub-arguments for the given argument
# sub_arguments = af.get_sub_arguments(argument)

# # Print all sub-arguments obtained
# print("Sub-arguments for the argument:")
# for arg in sub_arguments:
#     print(arg)

## GENERATE ATTACKS

# # Generate undercuts for all arguments
# af = ArgumentationFramework(all_rules)

# # Generate undercuts for all arguments
# undercuts = af.generate_undercuts()

# # Print all undercuts obtained
# print("Undercuts:")
# for undercut in undercuts:
#     print(f"{undercut[0]} undercuts {undercut[1]}")
# Now call the methods to detect undercuts and rebuttals

undercuts = af.detect_undercuts()
rebuttals = af.detect_rebuttals()

print("Undercuts:")
for attacker, target in undercuts:
    print(f"{attacker} undercuts {target}")
#Expecting 
    # (A6,A7)
    # (A6,A11)
    # (A6,A16)



def generate_argument_chain(argument_set, starting_argument):
    argument_chain = [starting_argument]  # Initialize a list with the starting argument
    addedSomething = True
    while addedSomething:
        for arg in argument_set:
            for argchain in argument_chain:
                if argchain in arg.sub_arguments:
                    argument_chain.append(arg)
                else:
                    addedSomething = False
   
    argument_chain = list(set(argument_chain))
    return argument_chain
args = af.get_arguments()
conclusions = [arg.top_rule.conclusion for arg in args]
conclusions = list(set(conclusions))
conclusion_Args = {}
print(conclusions)
for conclusion in conclusions:
    conclusion_Args[conclusion] = [arg.name for arg in args if arg.top_rule.conclusion == conclusion]
for conclusion in conclusions:
    if conclusion_Args.get("¬"+str(conclusion)) is not None :
        print("rebuttals for ",conclusion)

def find_contrary_literals(arguments):
    conclusions = [arg.top_rule.conclusion for arg in arguments]
    contrary_literals = []
    for conclusion in conclusions:
        literal_name = conclusion.name
        literal = Literal(literal_name, is_negative=False)
        negation = Literal(literal_name, is_negative=True)
        if literal in conclusions and negation in conclusions:
            contrary_literals.append(literal)
            contrary_literals.append(negation)
    contrary_literals = list(set(contrary_literals))
    return contrary_literals


print(find_contrary_literals(args))
def find_rebuttal_attacks(arguments):
    contrary_literals = find_contrary_literals(arguments)
    rebuttal_attacks = {}
    for literal in contrary_literals:
        for arg in arguments:
            if arg.top_rule.conclusion.name == literal.name and arg.top_rule.conclusion.is_negative != literal.is_negative:
                if literal not in rebuttal_attacks:
                    rebuttal_attacks[literal] = []
                rebuttal_attacks[literal].append(arg)
    return rebuttal_attacks
rebuttal_attacks = find_rebuttal_attacks(args)
for literal, arguments in rebuttal_attacks.items():
    rebuttal_attacks[literal] = list(set(rebuttal_attacks[literal]))

print(rebuttal_attacks)
def find_sub_arguments( main_argument):
    sub_arguments = []

    def find_sub_arguments_recursive(argument):
        for sub_arg in argument.sub_arguments:
            sub_arguments.append(sub_arg)
            find_sub_arguments_recursive(sub_arg)

    find_sub_arguments_recursive(main_argument)
    return sub_arguments

def extend_rebuttals_with_sub_arguments(rebuttal_attacks, all_arguments):
    extended_rebuttals = rebuttal_attacks.copy()
    for literal, attacks in rebuttal_attacks.items():
        for arg in attacks:
            found = generate_argument_chain(all_arguments, arg)
            extended_rebuttals[literal].extend(found)
    return extended_rebuttals

def extend_rebuttals_with_sub_arguments1(rebuttal_attacks,all_arguments):
    extended_rebuttals = rebuttal_attacks.copy()
    for literal, attacks in rebuttal_attacks.items():
        for arg in attacks:
            # Find sub-arguments for the current argument
            sub_arguments = generate_argument_chain(all_arguments,arg)
            # Filter out sub-arguments with the same conclusion as the literal and different negation
            sub_arguments_filtered = []
            for sub_arg in sub_arguments:
                if sub_arg.top_rule.conclusion == literal.name or sub_arg.top_rule.conclusion.is_negative != literal.is_negative:
                    sub_arguments_filtered.append(sub_arg)
            # Extend the list of attacks with filtered sub-arguments
            extended_rebuttals[literal].extend(sub_arguments_filtered)
    return extended_rebuttals

extended_rebuttals = rebuttal_attacks
# remove duplicate from each list 
for literal, arguments in extended_rebuttals.items():
    extended_rebuttals[literal] = list(set(arguments))
for literal, arguments in extended_rebuttals.items():
    print(f"Rebuttal attacks against {literal}:")
    for arg in arguments:
        print(f"- Argument {arg}")

def find_arguments_with_conclusion(arguments, conclusion):
    return [arg for arg in arguments if arg.top_rule.conclusion == conclusion]

def tuple_of_rubutlals(rebuttal_attacks,args):
    count=0
    rebuttal_tuples = {}
    for literal, attacks in rebuttal_attacks.items():
        sub_conc = find_arguments_with_conclusion(args,literal)
        for element1 in sub_conc:
            for element2 in attacks:
                if rebuttal_tuples.get(literal) is  None:
                    rebuttal_tuples[literal] = []
                rebuttal_tuples[literal].append((element1,element2))
                count += 1
    print("Number of rebuttal attacks:```````````````````````````````````", count)

    return rebuttal_tuples
#rebuttal_tuples = tuple_of_rubutlals(extended_rebuttals,args)
total = 0

def delete_arguments_with_same_conclusion(rebuttal_attacks={}):
    for literal, attacks in rebuttal_attacks.items():
        # Get the conclusion from the literal
        conclusion = literal.name
        for arg in attacks[:]:  # Iterate over a copy of the list to avoid modifying it while iterating
            # Check if the argument's conclusion is the same as the key
            if arg.top_rule.conclusion.name == conclusion and arg.top_rule.conclusion.is_negative != literal.is_negative:
                # Remove the argument from the list
                attacks.remove(arg)
#delete_arguments_with_same_conclusion(extended_rebuttals)
saved_rebuttal = find_rebuttal_attacks(args)


#final_rebut = tuple_of_rubutlals(extended_rebuttals,args)
print("Final Rebuttal Attacks:")


def extend_argument_chains(argument_set, argument_dict):
    extended_argument_dict = {}  # Initialize a new dictionary to store extended argument chains
    for literal, arguments in argument_dict.items():
        extended_argument_list = []  # Initialize a list to store extended argument chains for the current literal
        for arg in arguments:
            # Generate the argument chain starting from the current argument
            argument_chain = generate_argument_chain(argument_set, arg)
            extended_argument_list.extend(argument_chain)  # Extend the list with the generated argument chain
        # Add the extended argument list to the dictionary with the same key
        extended_argument_dict[literal] = extended_argument_list
    return extended_argument_dict

# Extend the rebuttal attacks with sub-arguments
ext_rebuttals = extend_argument_chains(args, rebuttal_attacks)

for literal, arguments in ext_rebuttals.items():
    print(f"Rebuttal attacks against {literal}:")
    print(rebuttal_attacks[literal])
    print("Extended:")
    print(ext_rebuttals[literal])
final_tuple = tuple_of_rubutlals(ext_rebuttals,args)
print(final_tuple)
count = 0
for literal, arguments in final_tuple.items():
    count += len(arguments)
print("Number of rebuttal attacks:", count)
# count for each litteral
for literal, arguments in final_tuple.items():
    print(f"Rebuttal attacks against {literal}:")
    lenght = len(arguments)
    print(lenght)


# fonction qui cherche toutes les régles defeasible d'une attaque en utilisant la fonction get_defeasible_rules_for_argument
def find_defeasible_rules_for_rebuttal_attacks(rebuttal_attacks, af):
    defeasible_rules_for_rebuttal_attacks = {}
    for literal, arguments in rebuttal_attacks.items():
        for arg in arguments:
            defeasible_rules = af.get_defeasible_rules_for_argument(arg)
            defeasible_rules_for_rebuttal_attacks[arg] = defeasible_rules
    return defeasible_rules_for_rebuttal_attacks

def find_defeasible_rules_for_undercuts_attack(undercuts, af):
    defeasible_rules_for_undercuts = {}
    for attacker, target in undercuts:
        for arg in af.arguments:
            # Check if the attacker's conclusion is the premise of the target argument's top rule
            if arg.top_rule.conclusion == target.top_rule.premises:
                defeasible_rules = af.get_defeasible_rules_for_argument(arg)
                defeasible_rules_for_undercuts[arg] = defeasible_rules
    return defeasible_rules_for_undercuts

# Find defeasible rules for attacks
defeasible_rules_for_rebuttal_attacks = find_defeasible_rules_for_rebuttal_attacks(rebuttal_attacks, af)
#defeasible_rules_for_undercuts = find_defeasible_rules_for_undercuts_attack(undercuts, af)
# Undercuts renvoie une chaine de caractere il faut des tuples pour simplifier je vais donc essayer de le faire avec rebuts


for arg, defeasible_rules in defeasible_rules_for_rebuttal_attacks.items():
    print(f"Defeasible rules for rebuttal attack against argument {arg.name}:")
    for rule in defeasible_rules:
        print(rule)

def weakest(rule_set1, rule_set2):
    """
    Determine if rule_set1 is the weakest compared to rule_set2.
    """
    if not rule_set1:
        return True
    for rule1 in rule_set1:
        is_weakest = True
        for rule2 in rule_set2:
            if rule2.rule_weight > rule1.rule_weight:
                is_weakest = False
                break
        if is_weakest:
            return True
    return False



# fonction qui loop sur tous les tuples de rebutts puis cherche les membres defeasible de ces derniers puis les donne en parametre a la fonction weakest, elle devra renvoyer les defeats 
def find_defeats(defeasible_rules_for_rebuttal_attacks):
    defeats = {}
    for arg, defeasible_rules in defeasible_rules_for_rebuttal_attacks.items():
        for rule in defeasible_rules:
            if weakest(defeasible_rules, af.get_defeasible_rules_for_argument(arg)):
                defeats[arg] = rule
    return defeats


# regroupe all the attacks into one array 
attacks = undercuts
for key,value in final_tuple.items():
    attacks.extend(value)


def find_defeated(attacks):
    defeats =[]
    for attack in attacks:
        attacker = attack[0]
        attacked = attack[1]
        # get defeasible rule for each 
        attacker_Def = af.get_defeasible_rules_for_argument(attacker)
        attacked_Def = af.get_defeasible_rules_for_argument(attacked)
        if not attacker_Def:
            defeats.append(attack)
        else :
            for rule in attacker_Def:
                is_preferred = False
                for defence_rule in attacked_Def:
                    if rule.rule_weight >= defence_rule.rule_weight:
                        is_preferred = True
                        break
        if is_preferred:
            defeats.append(attack)
    return defeats
                
            
def generate_histogram(defeats):
    # Calculate in-degree for each argument (number of times it is defeated)
    in_degree_count = {}
    for attack in defeats:
        attacked = attack[1]  # Assuming the second element of the tuple is the attacked argument
        if attacked.name not in in_degree_count:
            in_degree_count[attacked.name] = 0
        in_degree_count[attacked.name] += 1

    # Create a histogram data, where keys are in-degree and values are counts of arguments
    histogram_data = {}
    for count in in_degree_count.values():
        if count not in histogram_data:
            histogram_data[count] = 0
        histogram_data[count] += 1

    # Data for plotting
    x = list(histogram_data.keys())
    y = [histogram_data[count] for count in x]

    plt.bar(x, y, color='blue')
    plt.xlabel('Defeat In-Degree')
    plt.ylabel('Number of Arguments')
    plt.title('Histogram of Argument Defeat In-Degree')

    # Show the plot
    plt.show()

# def create_argument_graph(arguments, attacks):
#     # Create a directed graph
#     G = nx.DiGraph()
    
#     # Map each unique conclusion to a list of arguments having that conclusion
#     conclusion_to_args = {}
#     for arg in arguments:
#         conclusion = str(arg.top_rule.conclusion)
#         if conclusion not in conclusion_to_args:
#             conclusion_to_args[conclusion] = []
#         conclusion_to_args[conclusion].append(arg.name)
    
#     # Add nodes (each unique conclusion is a node)
#     for conclusion, args in conclusion_to_args.items():
#         label = conclusion + '\n' + ', '.join(args)
#         G.add_node(conclusion, label=label)
    
#     # Add edges (each attack is a directed edge towards conclusions)
#     seen_attacks = set()
#     for attacker, attacked in attacks:
#         attacker_conclusion = str(attacker.top_rule.conclusion)
#         attacked_conclusion = str(attacked.top_rule.conclusion)
#         attack_tuple = (attacker_conclusion, attacked_conclusion)
#         if attack_tuple not in seen_attacks:
#             G.add_edge(attacker_conclusion, attacked_conclusion)
#             seen_attacks.add(attack_tuple)

#     # Draw the graph
#     pos = nx.spring_layout(G)  # positions for all nodes
#     labels = nx.get_node_attributes(G, 'label')

#     nx.draw(G, pos, with_labels=True, labels=labels, node_size=2000, node_color='lightblue', 
#             linewidths=0.25, font_size=10, font_weight='bold', arrowsize=20)
    
#     plt.show()






defeats = find_defeated(attacks)
print(len(defeats))
generate_histogram(defeats)
# create_argument_graph(args, attacks)

burden_numbers = af.compute_burdens_with_defeats(defeats, max_depth=3)
ranked_arguments = af.rank_arguments_with_defeats(burden_numbers)
for arg in ranked_arguments:
    print(f"Argument: {arg}, Burden: {burden_numbers[arg]}")

