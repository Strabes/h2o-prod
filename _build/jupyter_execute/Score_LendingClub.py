#!/usr/bin/env python
# coding: utf-8

# # MOJO Scoring: Two Approaches
# 
# Now we will use the model we built on the Lending Club data to score the test cases we pickled. To mimick the scoring performance we would experience if the model were implemented in a real-time environment, we will score the records one at a time. We will use the MOJO we downloaded from H2O to score these records in two different ways:
# 
# 1. Use the `mojo_predict_pandas` method from the `h2o.utils.shared_utils` to score one record at a time
# 
# 2. Use the java application we just built to score one record at a time. To do so, we will first initialize a java virtual machine using python's `subprocess` package. This JVM will instantiate an instance of our scoring class, which loads the model just once at initialization. As we will see, loading the model once is far more efficient than repeatedly calling `mojo_predict_pandas`, which reloads the model for each call. We will then establish a gateway to our JVM using `JavaGateway` from `py4j` and score our test cases one at a time.
# 
# Timing of these two approaches will show that the second approach is far faster than the first approach. On my machine, the first approach takes more than 300 *milliseconds* per record whereas the second approach takes less than 100 *microseconds* per record. For many real-time production applications, the difference between the second approach and the first approach is the difference between easily hitting an SLA and almost always failing to hit the SLA.

# ### Imports

# In[1]:


import os, sys, json, pickle
import pandas as pd
import subprocess
from ast import literal_eval
from py4j.java_gateway import JavaGateway
from h2o.utils import shared_utils as su


# ### Read in our pickled test cases and feature engineering pipeline

# In[2]:


test_data = pd.read_pickle('test_cases.pkl')


# In[3]:


with open('pipeline.pkl','rb') as f:
    p = pickle.load(f)


# In[4]:


test_data.head()


# ### Apply feature engineering
# 
# In real-time production scoring, these transformations would constribute to the end-to-end runtime of the application and therefore influence whether scoring achieves its SLA. Here we are primarily interested in the time it takes to score with the MOJO itself under the two approaches outlined above. Therefore, we do not include this in the timing. 

# In[5]:


test_data_prepped = (
    p.transform(test_data)
     .reset_index(drop=True)
     .drop(labels = 'loan_status',axis=1))


# In[6]:


test_data_prepped.head()


# In[7]:


predictors = test_data_prepped.columns.to_list()


# ### Scoring Approach 1: `h2o`'s `mojo_predict_pandas` method

# In[8]:


mojo_zip_path = 'lendingclub-app/src/main/resources/final_gbm.zip'
genmodel_jar_path = 'h2o-genmodel.jar'

records = [test_data_prepped.iloc[[i]] for i in range(test_data_prepped.shape[0])]


# In[9]:


get_ipython().run_cell_magic('timeit', '', '\nresults = []\n\nfor record in records:\n    pred = su.mojo_predict_pandas(\n        record,\n        mojo_zip_path,\n        genmodel_jar_path)\n    results.append(pred)')


# In[10]:


results = []

for record in records:
    pred = su.mojo_predict_pandas(
        record,
        mojo_zip_path,
        genmodel_jar_path)
    results.append(pred)


# In[11]:


# Predictions:
pd.concat(results)


# ### Scoring Approach 2: Our Java Application

# In[12]:


## Start JVM using subprocess

cmd = "java -cp " + "lendingclub-app/target/" + "lendingclub-app-1.0-SNAPSHOT-jar-with-dependencies.jar " + "com.lendingclub.app.MojoScoringEntryPoint"
jvm = subprocess.Popen(cmd)


# In[13]:


## Establish gateway with the JVM

gateway = JavaGateway()
mojoscorer = gateway.entry_point.getScorer()


# In[14]:


## Construct cases as list of JSON objects

cases = test_data_prepped[predictors].to_dict(orient='records')
cases = [json.dumps(case) for case in cases]


# In[15]:


get_ipython().run_cell_magic('timeit', '', 'results = []\n\nfor case in cases:\n    results.append(literal_eval(mojoscorer.predict(case)))')


# In[16]:


results = []

for case in cases:
    results.append(literal_eval(mojoscorer.predict(case)))

pd.DataFrame(results)


# In[17]:


## Kill JVM

jvm.kill()

