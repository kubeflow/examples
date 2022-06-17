# import matplotlib.pyplot as plt
# import seaborn as sns
import warnings
import pickle5 as pkl
import numpy as np 
import pandas as pd 

warnings.filterwarnings('ignore')

def import_dataset(path):
    df = pd.read_csv(path)
    return df

df = import_dataset("https://raw.githubusercontent.com/ajinkya933/examples-1/master/telco-kaggle-competition/data/WA_Fn-UseC_-Telco-Customer-Churn.csv") 

df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

# for col in df.columns:
#     print(col, " : ",df[col].isna().sum())

df.dropna(axis=0, inplace=True)

#  look into uniques elements for every column
df.apply(lambda x: x.unique())
df.apply(lambda x: x.unique())

#  "No" and "No internet service" has no meaning to stay toghether so I will repalce them with "No"
df["OnlineSecurity"] = df["OnlineSecurity"].apply(lambda x: x.replace("No internet service", "No"))
df["OnlineBackup"] = df["OnlineBackup"].apply(lambda x: x.replace("No internet service", "No"))
df["DeviceProtection"] = df["DeviceProtection"].apply(lambda x: x.replace("No internet service", "No"))
df["TechSupport"] = df["TechSupport"].apply(lambda x: x.replace("No internet service", "No"))
df["StreamingTV"] = df["StreamingTV"].apply(lambda x: x.replace("No internet service", "No"))
df["StreamingMovies"] = df["StreamingMovies"].apply(lambda x: x.replace("No internet service", "No"))

# Same for "No phone service"
df["MultipleLines"] = df["MultipleLines"].apply(lambda x: x.replace("No phone service", "No"))

df.apply(lambda x: x.unique())

df.drop(columns=["customerID"], axis=1, inplace=True)

no=df[df["Churn"]=="No"]["tenure"]
yes=df[df["Churn"]=="Yes"]["tenure"]

print("NO:", df[df["Churn"]=="No"]["tenure"].sort_values().sum())
print("YES:",df[df["Churn"]=="Yes"]["tenure"].sort_values().sum())

df.apply(lambda x: x.unique())

#  In a new df I will replace no with 0, yest with 1
#  InternetService will not be touched at this moment

# 
dfx=df.copy()
dfx.drop("InternetService", axis=1, inplace=True)
dfx.columns

dfx.replace("No", 0, inplace=True)
dfx.replace("Yes", 1, inplace=True)

dfx.apply(lambda x: x.unique())
dfx["InternetService"] = df["InternetService"] 
dfx["gender"].replace("Female", 0, inplace=True)
dfx["gender"].replace("Male", 1, inplace=True)

# Label Encoding


# I will Use LabelEncoder instead of the most common pd.get_dummies() because i will have less features at the end
from sklearn.preprocessing import LabelEncoder
le=LabelEncoder()


for col in dfx.columns:
    if dfx[col].dtypes == "object":
        dfx[col]=le.fit_transform(dfx[col])
        
# dfx.head()

dfx.apply(lambda x: x.unique())

# Float columns must be scaled

from sklearn.preprocessing import MinMaxScaler
mms=MinMaxScaler()

dfx["TotalCharges"] = mms.fit_transform(np.array(dfx["TotalCharges"]).reshape(-1, 1))
dfx["MonthlyCharges"] = mms.fit_transform(np.array(dfx["MonthlyCharges"]).reshape(-1, 1))
dfx["tenure"] = mms.fit_transform(np.array(dfx["tenure"]).reshape(-1, 1))

#  Split the df for ML
#  I'm looking to predict the Churn colum
from sklearn.model_selection import train_test_split

X = dfx.drop("Churn", axis=1)
y = dfx["Churn"]


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = .25, random_state = 101)

#to save it
with open("/data/train.pkl", "wb") as f:
    pkl.dump([X_train, y_train], f)

with open("/data/test.pkl", "wb") as f:
    pkl.dump([X_test, y_test], f)