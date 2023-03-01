#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 25 22:32:08 2023

@author: sylvain
"""

import julia
from julia.api import Julia
jl = Julia(compiled_modules=False)
from julia import Main

import pandas as pd

solver = 'HiGHS'   # tested with GLPK, HiGHS, CPLEX'

# julia.install() # needs to be run if it is the first time you are using julia package
#julia.install()

# Start a Julia process
julia_proc = julia.Julia()

# Read input data from CSV file
data = pd.read_csv("/home/sylvain/svn/EnergyScope_multi_cells/case_studies/dat_files/ES-PT_FR_IE-UK/td_dat/ndata.csv", header=None)

# Define the dimensions and days sets
DIMENSIONS = range(1,1+data.shape[1])
DAYS = range(1,1+data.shape[0])
Main.DIMENSIONS = DIMENSIONS
Main.DAYS = DAYS

Main.eval('using JuMP, ' + solver)
Main.eval("using CSV, DataFrames")
# Define the input data and distance matrix
Main.eval('Ndata = CSV.read("/home/sylvain/svn/EnergyScope_multi_cells/case_studies/dat_files/ES-PT_FR_IE-UK/td_dat/ndata.csv", DataFrame; header=false)')
Main.eval("Distance = [sum(abs(Ndata[i,k] - Ndata[j,k]) for k in DIMENSIONS) for i in DAYS, j in DAYS]")

# Define the number of typical days and create the model
Nbr_TD = 12
Main.eval('using ' + solver)
Main.eval('model = Model(' + solver + '.Optimizer)')

# Define the binary decision variables
Main.eval(f'@variable(model, Selected_TD[{list(DAYS)}], binary=true)')
Main.eval(f'@variable(model, Cluster_matrix[{list(DAYS)},{list(DAYS)}], binary=true)')

# Define the constraints
for j in DAYS:
    Main.eval(f'@constraint(model, sum(Cluster_matrix[i,{j}] for i in {list(DAYS)}) == 1)')
    for i in DAYS:
        Main.eval(f'@constraint(model, Cluster_matrix[{i},{j}] <= Selected_TD[{i}])')
Main.eval(f'@constraint(model, sum(Selected_TD[{list(DAYS)}]) == {Nbr_TD})')

# Define the objective function
Main.eval(f'@objective(model, Min, sum(Distance[i,j] * Cluster_matrix[i,j] for i in {list(DAYS)}, j in {list(DAYS)}))')

# Solve the problem
Main.eval('optimize!(model)')

# Print the output
for i in DAYS:
    TD_of_days = Main.eval(f'sum(j * value(Cluster_matrix[j,{i}]) for j in {list(DAYS)})')
    print(TD_of_days)
    
# Get the otpimization results:  
outputs = { 'Cluster_matrix' :  pd.DataFrame(Main.eval('value.(Cluster_matrix)')),
            'Selected_TD' :  pd.DataFrame(Main.eval('value.(Selected_TD)'))
         }
            