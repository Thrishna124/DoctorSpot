#########################################################
#code by Thrishna Balakrishnan
#dataset: https://www.kaggle.com/datasets/jocelyndumlao/cardiovascular-disease-dataset
#########################################################
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

# Load the dataset
filepath = "/Users/thrishna/Desktop/PythonProject/PI/heart/Cardiovascular_Disease_Dataset.csv"
dataset = pd.read_csv(filepath)
# dataset summary
#Index(['patientid', 'age', 'gender', 'chestpain', 'restingBP',
#       'serumcholestrol', 'fastingbloodsugar', 'restingrelectro',
#       'maxheartrate', 'exerciseangia', 'oldpeak', 'slope', 'noofmajorvessels',
#       'target']

#print(dataset.isna().sum())
dataset.drop(columns=['patientid'],inplace=True)
dataset.rename(columns={'gender':'sex','target':'prediction','serumcholestrol':'cholesterol'},inplace=True)

numeric_features = ['age', 'restingBP', 'cholesterol', 'fastingbloodsugar', 
            'maxheartrate', 'oldpeak']
categorical_features = ['sex','chestpain','restingrelectro','exerciseangia','slope','noofmajorvessels']

dataset[categorical_features] = dataset[categorical_features].apply(lambda x: x.astype(str))

def heart_disease_diagnosis(row):
    # Check for high-risk condition
    if row['slope'] == '3' and row['restingBP'] > 140:
        return 'High Risk of Heart Disease'
    
    # Check for congestive heart failure
    elif row['oldpeak'] > 2 and row['slope'] == '3' and row['maxheartrate'] < 100:
        return 'Congestive Heart Failure'
    
    # Check for arrhythmia
    elif row['restingrelectro'] in ['1', '2']:
        return 'Arrhythmia'
    
    # Check for exercise-induced angina
    elif row['exerciseangia'] == '1':  # '1' corresponds to 'yes'
        return 'Possible Exercise-Induced Angina'
    
    # Check for angina symptoms
    elif row['chestpain'] in ['0', '1']:  # Typical or atypical angina
       return 'Angina Symptoms Detected'

    else:
    # Return all identified diagnoses or 'Normal' if none
        return 'Normal'

# Apply diagnosis function to each row
dataset['diagnosis'] = dataset.apply(heart_disease_diagnosis, axis=1)

# Define features and target variable
X = dataset[numeric_features + categorical_features]
y = dataset['prediction']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])

# Fit and transform the training data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = LogisticRegression(class_weight='balanced')
model.fit(X_train_transformed, y_train)

# Make predictions
y_pred = model.predict(X_test_transformed)

# Evaluate the model
print('Classification Report:')
print(classification_report(y_test, y_pred))

# Calculate and print evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print(f'Prediction: Accuracy: {accuracy:.4f}')
print('Confusion Matrix:')
print(conf_matrix)

joblib.dump(model, '/Users/thrishna/Desktop/Critical_Django_project/docspot/heart/data/heart_prediction_model.pkl')
joblib.dump(preprocessor, '/Users/thrishna/Desktop/Critical_Django_project/docspot/heart/data/heart_preprocessor.pkl')

# Define features and target variable
X = dataset[numeric_features + categorical_features]
y = dataset['diagnosis']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit and transform the training data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = LogisticRegression(class_weight='balanced')
model.fit(X_train_transformed, y_train)

# Make predictions
y_pred = model.predict(X_test_transformed)

# Evaluate the model
print('Classification Report:')
print(classification_report(y_test, y_pred))



# Calculate and print evaluation metrics
accuracy = accuracy_score(y_test, y_pred)
conf_matrix = confusion_matrix(y_test, y_pred)

print(f'Diagnosis: Accuracy: {accuracy:.4f}')
print('Confusion Matrix:') 
print(conf_matrix)

joblib.dump(model,'/Users/thrishna/Desktop/Critical_Django_project/docspot/heart/data/heart_diagnosis_model.pkl')
