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

    if st.sidebar.button("Add Rule"):
        # Process the form inputs and create a rule
        new_rule = ag.Rule(premises, conclusion, is_defeasible)
        rules.append(new_rule)
        st.sidebar.success("Rule added successfully!")

    # Display rules in a table on the main page
    display_rules(rules)

    # Option to load rules from aspicGenerator
    use_our_set = st.sidebar.checkbox("Use Our Set")
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
        for literal, arguments in extended_rebuttals.items():
            st.write(f'* Rebuttal attacks against {literal}:')
            st.write(extended_rebuttals[literal].__repr__())
            st.write("nombre d'occurence:", len(extended_rebuttals[literal]))
        rebuttals_tuples = ag.tuple_of_rubutlals(extended_rebuttals,af.get_arguments())
        counter = 0
        for attacked , attackers in rebuttals_tuples.items():
            st.write(f'* Rebuttal attacks against {attacked}:')
            st.write(attackers.__repr__())
            st.write("nombre d'occurence:", len(attackers))
            counter += len(attackers)
        st.write("nombre total d'occurence:", counter)

if __name__ == "__main__":
    # Initialize an empty list to store rules
    rules = []
    main(rules)
