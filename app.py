import streamlit as st
from pyomo.environ import ConcreteModel, Var, Objective, NonNegativeReals, SolverFactory, minimize

# Set up the Streamlit interface
st.title('Heat Exchanger Simulation Solver using Pyomo - Linear Model')

# Inputs
a = st.number_input('Coefficient a', value=1.0, format='%f')
b = st.number_input('Coefficient b', value=2.0, format='%f')

if st.button('Run Simulation'):
    # Define the model
    model = ConcreteModel()
    model.x = Var(within=NonNegativeReals)
    model.obj = Objective(expr=a * model.x + b, sense=minimize)  # Linear objective
    
    # Solve the model with GLPK
    solver = SolverFactory('glpk')
    result = solver.solve(model)

    # Output results
    st.write(f'Optimal x: {model.x.value}')
    st.write(f'Minimum Objective: {model.obj()}')
##