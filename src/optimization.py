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
from copy import deepcopy



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
    
    f = solver.Solve()
    if f == 0:
        print('Solution:')
        print('fare_lift =', objective.Value())
        opt_solution = {}
        for k,x in variables.items():
            #print(metrics[k]['segment'], x.solution_value())
            opt_solution[k] = {'segment' : metrics[k]['segment'],
                            'fraction': x.solution_value()}
        return opt_solution,objective.Value()


def metrics_evalution(opt_solution, metrics,b):
    result = []
    opt_fraction = {}
    for k, sg in metrics.items():
        temp  = dict()
        temp['budget'] = b
        temp['applied'] = opt_solution[k]['fraction']*metrics[k]['applied']
        temp['delta_ni'] = opt_solution[k]['fraction']*metrics[k]['delta_ni']
        temp['fare_lift'] = opt_solution[k]['fraction']*metrics[k]['fare_lift']
        temp['spend'] = opt_solution[k]['fraction']*metrics[k]['spend']
        result.append(temp)
        opt_fraction[opt_solution[k]['segment']]=opt_solution[k]['fraction']
    return dict(pd.DataFrame(result).agg(sum)),opt_fraction

def different_budget():
    B = np.arange(1000,50000,1000)
    summary_metric = []
    opt_fraction = []
    for b in B:
        opt_solution , opt_value = solver(b)
        me,fr = metrics_evalution(opt_solution, metrics,b)
        opt_fraction.append(fr)
        summary_metric.append(me)
    pd.DataFrame(opt_fraction).plot()
    return summary_metric

    
if __name__ == '__main__':
    B = np.arange(1000,50000,1000)
    summary_metric
    pd.DataFrame(opt_fraction).plot()
    summary_metric = pd.DataFrame(summary_metric)    
    summary_metric.plot.scatter(x='budget', y = 'fare_lift')
    summary_metric.plot.scatter(x='budget', y = 'fare_lift')
    summary_metric.plot.scatter(x='spend', y = 'fare_lift')
    summary_metric.plot.scatter(x='budget', y = 'fare_lift')
    summary_metric.plot.scatter(x='budget', y = 'spend')
