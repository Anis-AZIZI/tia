import streamlit as st

# Importing your classes and functions
import aspic_generator as ag

# Function to display rules in a table
def display_rules(rules):
    st.header("Rules")
    if rules:
        for rule in rules:
            st.write(rule)  # Increase font size for better readability 

# Main function to run the Streamlit app
def main(rules):
    strict_rules = ag.strict_rules
    defeasible_rules = ag.defeasible_rules
    st.write('''
             # Welcome to the Argumentation Framework Generator!
                ## This is a tool to generate argumentation frameworks using the aspicGenerator library. 
                #### By AZIZI Anis,BOUDJEBBOUR Maya,RABEHI Amira
             ''')
    
    # Set up the sidebar
    st.sidebar.header("Add Rule")

    # Add form elements to the sidebar
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
    if st.button("Create Contrapositions"):
        contraposition_rules = ag.create_contrapositions(strict_rules,len(rules))
        st.header("Contraposition Rules")
        rules.extend(contraposition_rules)
        display_rules(rules)

if __name__ == "__main__":
    # Initialize an empty list to store rules
    rules = []
    main(rules)
