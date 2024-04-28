import streamlit as st
import matplotlib.pyplot as plt

# Importing your classes and functions
import aspic_generator as ag

# Function to display rules in a table
def display_rules(rules):
    if rules:
        for rule in rules:
            st.write(rule)  # Increase font size for better readability 

def show_all_arguments(arguments):
    for argument in arguments:
        st.write(argument)

# Main function to run the Streamlit app
def main(rules):
    st.write('''
             # Welcome to the Argumentation Framework Generator!
                ## This is a tool to generate argumentation frameworks using the aspicGenerator library. 
                #### By AZIZI Anis  BOUDJEBBOUR Maya RABEHI Amira
             ''')
    
    # Set up the sidebar
    use_our_set = st.sidebar.checkbox("Use Our Set (Recommended)")
    st.sidebar.header("Add Rule")

    # Add form elements to the sidebar
    st.sidebar.write("Enter the premises and conclusion of the rule.")
    st.sidebar.write("Separate premises with commas and a negative premise is '-'premise.")
    premises = st.sidebar.text_input("Premises", "")
    premises = [literal.strip() for literal in premises.split(",")]
    premises = [ag.Literal(literal[1:], is_negative=True) if literal.startswith("~") else ag.Literal(literal) for literal in premises]
    
    conclusion = st.sidebar.text_input("Conclusion", "")
    conclusion = ag.Literal(conclusion[1:], is_negative=True) if conclusion.startswith("~") else ag.Literal(conclusion)
    
    is_defeasible = st.sidebar.checkbox("Is Defeasible")
    #burden_depth = st.sidebar.number_input("Max Depth of burden", 3)

    if st.sidebar.button("Add Rule"):
        # Process the form inputs and create a rule
        new_rule = ag.Rule(premises, conclusion, is_defeasible)
        rules.append(new_rule)
        st.sidebar.success("Rule added successfully!")

    # Display rules in a table on the main page
    display_rules(rules)

    # Option to load rules from aspicGenerator

    if use_our_set:
        # Load rules from aspicGenerator
        rules = []
        rules.extend(ag.rules)
        st.sidebar.success("Rules loaded from aspicGenerator!")
        display_rules(rules)
    
    # Button to execute create_contrapositions
    if st.sidebar.button(''' Create Contrapositions rules '''):
        # Generate contraposition rules
        strict_rules = ag.strict_rules
        contraposition_rules = ag.create_contrapositions(strict_rules, len(rules))
        
        # Create ArgumentationFramework object
        af = ag.ArgumentationFramework(rules + contraposition_rules)
        st.header("Contraposition Rules")
        display_rules(contraposition_rules)
    
    # Button to show arguments
    if st.sidebar.button(''' # generate Arguments'''):
        # Generate arguments
        strict_rules = ag.strict_rules
        contraposition_rules = ag.create_contrapositions(strict_rules, len(rules))
        af = ag.ArgumentationFramework(rules + contraposition_rules)
        arguments = af.get_arguments()
        st.header(''' Arguments''')
        show_all_arguments(arguments)

    if st.sidebar.button('''generate Attacks'''):
        # Generate attacks
        strict_rules = ag.strict_rules
        contraposition_rules = ag.create_contrapositions(strict_rules, len(rules))
        af = ag.ArgumentationFramework(rules + contraposition_rules)
        attacks = af.get_attacks()
        st.write(''' # Attacks''')
        undercuts = af.detect_undercuts()
        st.write('''## Undercuts''')
        for attacker, target in undercuts:
            printed = f'{attacker.name} undercuts {target.name}'
            st.write(printed)
        # generate rebuttals too
        st.write('''# rebuttals''')
        rebuttal_attacks = ag.find_rebuttal_attacks(af.get_arguments())
        for literal, arguments in rebuttal_attacks.items():
            rebuttal_attacks[literal] = list(set(rebuttal_attacks[literal]))
        extended_rebuttals = ag.extend_argument_chains(af.get_arguments(), rebuttal_attacks)
        rebuttals_tuples = ag.tuple_of_rubutlals(extended_rebuttals,af.get_arguments())
        counter = 0
        all_attacks = []
        for attacked , attackers in rebuttals_tuples.items():
            st.write(f'* Rebuttal attacks against {attacked}:')
            all_attacks.extend(attackers)
            st.write("counted :", len(attackers))
            counter += len(attackers)
        st.write("number of rebuttals attacks:", counter)
        # total number of attacks undercuts and rebuttals
        all_attacks.extend(undercuts)
        st.write("total number of attacks (undercuts and rebuttals):", len(all_attacks))
    if st.sidebar.button('''# Generate defeats'''):
        # Generate defeats
        strict_rules = ag.strict_rules
        contraposition_rules = ag.create_contrapositions(strict_rules, len(rules))
        af = ag.ArgumentationFramework(rules + contraposition_rules)
        attacks = af.get_attacks()
        undercuts = af.detect_undercuts()
        rebuttal_attacks = ag.find_rebuttal_attacks(af.get_arguments())
        for literal, arguments in rebuttal_attacks.items():
            rebuttal_attacks[literal] = list(set(rebuttal_attacks[literal]))
        extended_rebuttals = ag.extend_argument_chains(af.get_arguments(), rebuttal_attacks)
        rebuttals_tuples = ag.tuple_of_rubutlals(extended_rebuttals,af.get_arguments())
        counter = 0
        all_attacks = []
        for attacked , attackers in rebuttals_tuples.items():
            all_attacks.extend(attackers)
        all_attacks.extend(undercuts)
        defeats = ag.find_defeated(all_attacks)
        st.header("Defeats")
        #afficher nombre de defaites
        st.write(defeats.__repr__())
        st.write("number of defeats:", len(defeats))
    if st.sidebar.button('''# Generate historgramme'''):
        strict_rules = ag.strict_rules
        contraposition_rules = ag.create_contrapositions(strict_rules, len(rules))
        af = ag.ArgumentationFramework(rules + contraposition_rules)
        attacks = af.get_attacks()
        undercuts = af.detect_undercuts()
        rebuttal_attacks = ag.find_rebuttal_attacks(af.get_arguments())
        for literal, arguments in rebuttal_attacks.items():
            rebuttal_attacks[literal] = list(set(rebuttal_attacks[literal]))
        extended_rebuttals = ag.extend_argument_chains(af.get_arguments(), rebuttal_attacks)
        rebuttals_tuples = ag.tuple_of_rubutlals(extended_rebuttals,af.get_arguments())
        counter = 0
        all_attacks = []
        for attacked , attackers in rebuttals_tuples.items():
            all_attacks.extend(attackers)
        all_attacks.extend(undercuts)
        defeats = ag.find_defeated(all_attacks)
        plot = ag.generate_histogram(defeats)
        st.header("Histogramme")
        st.pyplot(plot)
        st.header("Argument Graph")
        graph = ag.create_argument_graph(af.get_arguments(), all_attacks)
        st.pyplot(graph)
    if st.sidebar.button('''# Burden'''):
        strict_rules = ag.strict_rules
        contraposition_rules = ag.create_contrapositions(strict_rules, len(rules))
        af = ag.ArgumentationFramework(rules + contraposition_rules)
        attacks = af.get_attacks()
        undercuts = af.detect_undercuts()
        rebuttal_attacks = ag.find_rebuttal_attacks(af.get_arguments())
        for literal, arguments in rebuttal_attacks.items():
            rebuttal_attacks[literal] = list(set(rebuttal_attacks[literal]))
        extended_rebuttals = ag.extend_argument_chains(af.get_arguments(), rebuttal_attacks)
        rebuttals_tuples = ag.tuple_of_rubutlals(extended_rebuttals,af.get_arguments())
        counter = 0
        all_attacks = []
        for attacked , attackers in rebuttals_tuples.items():
            all_attacks.extend(attackers)
        all_attacks.extend(undercuts)
        defeats = ag.find_defeated(all_attacks)
        burden_depth = st.sidebar.number_input("Max Depth of burden", placeholder=3, min_value=1, max_value=10, value=3)
        burden_numbers = af.compute_burdens_with_defeats(defeats, max_depth=burden_depth)
        ranked_arguments = af.rank_arguments_with_defeats(burden_numbers)
        st.write(burden_depth)
        for arg in ranked_arguments:
            st.write(f"Argument: {arg}, Burden: {burden_numbers[arg]}")
        

if __name__ == "__main__":
    # Initialize an empty list to store rules
    rules = []
    main(rules)
