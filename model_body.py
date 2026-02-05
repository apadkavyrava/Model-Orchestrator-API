#function to evaluate a model

import numpy as np
import pandas as pd
from collections import namedtuple

Variable = namedtuple('Variable', 'name factor')

def evaluate_model(dependent_variables_list, input_data):
  """
    dependent_variables_list: list of 'Variable' Named tuple
    input_data: pd dataframe, with the variables and dt column

    returns:  predicted value by dt column with dummy model
  """
  # check input params
  assert type(dependent_variables_list) == list
  assert all([type(dependent_variable) == Variable for dependent_variable in dependent_variables_list])
  # check that all values in dependent_variables_list are in input_data
  assert all([dependent_variable.name in input_data.columns for dependent_variable in dependent_variables_list])
  # enusre date is provided
  assert 'dt' in input_data.columns 


  factor_map = ({i.name: i.factor for i in dependent_variables_list})
  # apply factor map to the input data and sum row-wise
  input_data['prediction']  = input_data[list(factor_map.keys())].apply(lambda x: x*factor_map[x.name]).sum(axis=1)
  return input_data[['dt', 'prediction']]

# example model evaluation
df= pd.DataFrame([[1, 10, 5], [2, 20, 15], [3, 7, 7]],  columns = ['dt', 'var-1', 'var-2'])
print(evaluate_model([Variable('var-1',0.4), Variable('var-2',0.6)], df))