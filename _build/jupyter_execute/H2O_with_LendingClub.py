#!/usr/bin/env python
# coding: utf-8

# # Fit an H2O GBM on the Lending Club data

# ### Imports

# In[1]:


import pandas as pd
import numpy as np
import random, time, os, pickle

import matplotlib.pyplot as plt
from feature_engine import categorical_encoders as ce
from feature_engine import discretisers as dsc
from feature_engine import missing_data_imputers as mdi
from feature_engine import feature_selection as fs
from sklearn.pipeline import Pipeline as pipe

import h2o
from h2o.estimators import H2OXGBoostEstimator, H2OGradientBoostingEstimator
from h2o.grid.grid_search import H2OGridSearch

import warnings
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)

get_ipython().run_line_magic('matplotlib', 'inline')


# ### Read data into pandas and fix date columns

# In[2]:


df = pd.read_csv("../data/lending_club_loan_two.csv")


# In[3]:


## Fix date columns:
dt_cols = ['issue_d','earliest_cr_line']

df.loc[:,dt_cols] = df.loc[:,dt_cols]   .applymap(lambda x: np.nan if x in ['null','NULL',''] else x)   .apply(lambda x: pd.to_datetime(x,format = "%b-%Y"))


# ### Split into train and test

# In[4]:


p_trn = 0.8
n = df.shape[0]

df = df.sample(frac=1,random_state=1).reset_index(drop=True)

df_train = df.iloc[:int(n*p_trn),:].copy()
df_test = df.iloc[int(n*p_trn):,:].copy()


# In[5]:


df_train.head(5)


# ## Verify data types

# ### Make sure all columns are of the correct data type

# In[6]:


dtype_dict = df_train.dtypes.to_dict()


# In[7]:


numeric_cols = [k for k,v in dtype_dict.items() if pd.api.types.is_numeric_dtype(v)]
numeric_cols.sort()

print("Numeric columns: " + ", ".join(numeric_cols))


# In[8]:


object_cols = [k for k,v in dtype_dict.items() if pd.api.types.is_object_dtype(v)]
object_cols.sort()

print("Object columns: " + ", ".join(object_cols))


# In[9]:


datetime_cols = [k for k,v in dtype_dict.items() if pd.api.types.is_datetime64_any_dtype(v)]
datetime_cols.sort()

print("Datetime columns: " + ", ".join(datetime_cols))


# In[10]:


other_cols = [c for c in df.columns if c not in numeric_cols + object_cols + datetime_cols]
print("Columns not accounted for: " + ", ".join(other_cols))


# ## Apply NULL/null/NA/NaN consistently
# 
# Different datesources may result in different formats for null/missing values. It's typically a good idea to apply a consistent format. I'll do this by replacing 'NULL', 'null' and '' in character columns with `np.nan`.

# In[11]:


df_train.loc[:,object_cols] = df_train.loc[:,object_cols]   .applymap(lambda x: np.nan if str(x).lower() in ['null',''] else x)


# In[12]:


target = 'loan_status'

object_cols_x_target = [c for c in object_cols if c != target]

cols_to_drop = datetime_cols + ['address']

p = pipe([
    # Add missing indicators for numeric features
    ("num_nan_ind",mdi.AddMissingIndicator(variables=numeric_cols)),
    # Add missing level for categorical features
    ("fill_cat_nas",mdi.CategoricalVariableImputer(
        fill_value = "_MISSING_", variables=object_cols_x_target)),
    # Bin rare levels of categorical variables
    ("rare_cats",ce.RareLabelCategoricalEncoder(
        tol = 0.02, replace_with = "_RARE_", variables=object_cols_x_target)),
    # Impute missing numeric variables with media
    ("rmmean",mdi.MeanMedianImputer(imputation_method = 'median',variables=numeric_cols)),
    # Drop dates and address columns
    ("drop_date",fs.DropFeatures(features_to_drop=cols_to_drop))])


# In[13]:


df_train_prepped = p.fit_transform(df_train)


# In[14]:


df_train_prepped.head()


# In[15]:


h2o.init()


# In[16]:


h2o_train = h2o.H2OFrame(df_train_prepped)
h2o_train['loan_status'] = h2o_train['loan_status'].asfactor()


# In[17]:


predictors = df_train_prepped.columns.to_list()
predictors.remove('loan_status')


# In[18]:


# Set up gbm parameter grid and fit in h2o
hyper_params = {
    'ntrees': [100,200],
    'max_depth': [2,4,6],
    'learn_rate': [0.05, 0.1]
}

gbm = H2OGradientBoostingEstimator(
    distribution='bernoulli',
    seed = 1)

h2o_train1, h2o_train2 = h2o_train.split_frame(
    ratios=[0.8],
    seed = 1)

xgb_grid = H2OGridSearch(
    model = gbm,
    hyper_params = hyper_params
)

xgb_grid.train(
    training_frame = h2o_train1,
    x = predictors,
    y = 'loan_status',
    validation_frame = h2o_train2)


# In[19]:


grid_results = xgb_grid.get_grid(
    sort_by="logloss")


# In[20]:


best_params = grid_results.models[0].actual_params
best_params = dict((k,best_params[k]) for k in ('ntrees','max_depth','learn_rate'))


# In[21]:


best_params


# In[22]:


df_test_prepped = p.transform(df_test)

h2o_test = h2o.H2OFrame(df_test_prepped)
h2o_test['loan_status'] = h2o_test['loan_status'].asfactor()


# In[23]:


gbm = H2OGradientBoostingEstimator(
    distribution='bernoulli',
    model_id = 'final_gbm',
    **best_params,
    seed = 1)


# In[24]:


gbm.train(
training_frame = h2o_train,
    x = predictors,
    y = 'loan_status',
    validation_frame = h2o_test)


# In[25]:


#path = os.getcwd() + '/lendingclub-app/src/main/resources/'
#if not os.path.exists(path):
#    os.makedirs(path)
#gbm.download_mojo(path=path, get_genmodel_jar=False)


# In[26]:


gbm.predict(h2o_test[0:10,:])


# In[29]:


df_test.head(10).to_pickle(path = 'test_cases.pkl')


# In[31]:


with open('pipeline.pkl','wb') as f:
    pickle.dump(p,f)


# In[30]:


h2o.shutdown()

