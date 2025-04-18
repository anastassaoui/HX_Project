import streamlit as st
from pyomo.environ import ConcreteModel, Var, Objective, NonNegativeReals, SolverFactory, minimize

st.title("🧠 Solver - Pyomo Heat Exchanger")

a = st.number_input('Coefficient a', value=1.0)
b = st.number_input('Coefficient b', value=2.0)

if st.button('Run Simulation'):
    model = ConcreteModel()
    model.x = Var(within=NonNegativeReals)
    model.obj = Objective(expr=a * model.x + b, sense=minimize)
    solver = SolverFactory('glpk')
    result = solver.solve(model)

    st.success(f'✅ Optimal x: {model.x.value:.4f}')
    st.write(f'Minimum Objective: {model.obj():.4f}')
