using CSV, DataFrames
using JuMP, GLPK, HiGHS, CPLEX

data = CSV.read("/home/sylvain/svn/EnergyScope_multi_cells/case_studies/dat_files/ES-PT_FR_IE-UK/td_dat/ndata.csv", DataFrame; header=false)

# Define the dimensions and days sets
DIMENSIONS = 1:size(data)[2]
DAYS = 1:size(data)[1]

# Define the input data and distance matrix
#Ndata = rand(DAYS, DIMENSIONS) # replace with your data
Ndata = data
Distance = [sum(abs(Ndata[i,k] - Ndata[j,k]) for k in DIMENSIONS) for i in DAYS, j in DAYS]

# Define the number of typical days and create the model
Nbr_TD = 12
model = Model(HiGHS.Optimizer)

# Define the binary decision variables
@variable(model, Selected_TD[DAYS], binary=true)
@variable(model, Cluster_matrix[DAYS,DAYS], binary=true)

# Define the constraints
for j in DAYS
    @constraint(model, sum(Cluster_matrix[i,j] for i in DAYS) == 1) # Allocate one cluster center (i) to each day (j)
    for i in DAYS
        @constraint(model, Cluster_matrix[i,j] <= Selected_TD[i]) # If cluster not allocated, it needs to be null
    end
end
@constraint(model, sum(Selected_TD[i] for i in DAYS) == Nbr_TD) # Limit the number of TD

# Define the objective function
@objective(model, Min, sum(Distance[i,j] * Cluster_matrix[i,j] for i in DAYS, j in DAYS))

# Solve the problem
optimize!(model)

# Print the output
for i in DAYS
    TD_of_days = sum(j * value(Cluster_matrix[j,i]) for j in DAYS)
    print(TD_of_days, "\n")
end
