#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 24 22:34:27 2019

@author: ehsan.mousavi
"""


from __future__ import print_function
from ortools.linear_solver import pywraplp
import ortools
import pandas as pd
import matplotlib.pyplot as plt


param = {}
param['min_frac'] = .0
param['max_frac'] = 1
param['popualtion'] = 5000000
param['promo-cost'] = 5

info = pd.read_csv("data.csv")[1:8].T.to_dict()

def seg_estimate(info):
    metrics = dict()
    for  k,sg in info.items():
        result  = dict()
        result['segment'] = sg['segment']
        result["applied"] = param['popualtion'] * sg['percentage'] *  sg['applies_per_send']
        result["spend"]   = result["applied"] * sg['redemptions_per_apply']* param['promo-cost']
        result["fare_lift"] = sg['fare_pu_lift']/(1+sg['fare_pu_lift']) *sg['fare_pu'] *result["applied"]
        result["delta_ni"] = sg['ni_pu_lift']/(1+sg['ni_pu_lift']) *sg['ni_pu'] *result["applied"]
        metrics[k] =result  
    return metrics


def solver(budget):

    # Create the linear solver with the GLOP backend.
    solver = pywraplp.Solver('segmentation',
                             pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)


    # define variables
    
    variables = {}
    for k,sg in info.items():
        variables[k] = solver.NumVar(param['min_frac'],
                                                 param['max_frac'],
                                                 sg['segment'])
        
    print('Number of variables =', solver.NumVariables())

    # define constraints
    
    c_budget = solver.Constraint(0,   budget , 'budget')
    c_applied = solver.Constraint(0, param["popualtion"], 'applied')
    for k,sg in info.items():
        applied,spend = metrics[k]['applied'],metrics[k]['spend']
        delta_ni  = metrics[k]['delta_ni']
        c_budget.SetCoefficient(variables[k], -delta_ni)
        c_applied.SetCoefficient(variables[k], applied)

    print('Number of constraints =', solver.NumConstraints())

    # Create the objective function, 3 * x + y.
    objective = solver.Objective()
    for k,sg in info.items():
        fare_lift = metrics[k]['fare_lift']
        objective.SetCoefficient(variables[k],fare_lift )
    objective.SetMaximization()

    # [START solve]
    solver.Solve()
    # [END solve]

    # [START print_solution]
    print('Solution:')
    print('fare_lift =', objective.Value())
    opt_solution = {}
    for k,x in variables.items():
        print(metrics[k]['segment'], x.solution_value())
        opt_solution[metrics[k]['segment']] = x.solution_value()
    opt_solution['opt'] = objective.Value()
    return opt_solution

def metrics_evalution(solution):
    


if __name__ == '__main__':
    metrics = seg_estimate(info)
    segment_list = list(pd.DataFrame(info).T['segment'])
    B = np.arange(1000,50000,1000)
    result = []
    for b in B:
        result.append(solver(b))
    pd.DataFrame(result)[segment_list].plot()
        
    fare = [solver(b) for b in B]
    plt.plot(B,fare)
    mm = pd.DataFrame(metrics).T
    
    tmp = pd.concat((mm['segment'] ,mm['fare_lift']/mm['delta_ni']), axis=1)
    
    
    
