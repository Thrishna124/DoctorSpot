import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.compose import ColumnTransformer
import joblib

# Load the dataset (replace 'diabetes.csv' with your actual dataset file)
df_train = pd.read_csv('/Users/thrishna/Desktop/PythonProject/PI/diabetes/Dataset of Diabetes .csv')
print(df_train.columns)
print(df_train[df_train.isnull()].count())
df_train = df_train.iloc[:,2:]
df_train['CLASS'] = df_train['CLASS'].str.strip()
print(df_train['CLASS'].value_counts())
df_train['CLASS'] = df_train['CLASS'].replace('P', 'Y')

df_train.rename(columns={
    'Gender': 'sex',
    'AGE': 'age',
    'Urea': 'urea',
    'Cr': 'creatinine',
    'HbA1c': 'hba1c',  # Assuming you want to rename this as well
    'Chol': 'cholesterol',
    'TG': 'triglycerides',
    'CLASS':'diagnosis',
}, inplace=True)

#df_train['diagnosis']=df_train['CLASS'].apply(lambda z:'diabetes' if z=='Y' else ('pre-diabetes' if z=='P' else 'normal'))
df_train['prediction'] = df_train['diagnosis'].apply(lambda x: 1 if x=='Y' or x=='P' else 0)
df_train['diagnosis'] = df_train['diagnosis'].apply(lambda z:'Diabetic' if z=='Y' else ('Pre-Diabetic' if z=='P' else 'Normal'))
print(df_train.columns)

categorical_features = ['sex']
numeric_features = ['age', 'urea', 'creatinine', 'hba1c', 'cholesterol',
       'triglycerides', 'HDL', 'LDL', 'VLDL', 'BMI']

# Define features and target variable
X = df_train[numeric_features + categorical_features]
y = df_train['prediction']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Encode categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(), categorical_features)
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

joblib.dump(model, '/Users/thrishna/Desktop/Critical_Django_project/docspot/pancreas/data/diabetes_prediction_model.pkl')
joblib.dump(preprocessor, '/Users/thrishna/Desktop/Critical_Django_project/docspot/pancreas/data/diabetes_preprocessor.pkl')


# Define features and target variable
X = df_train[numeric_features + categorical_features]
y = df_train['diagnosis']

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

joblib.dump(model,'/Users/thrishna/Desktop/Critical_Django_project/docspot/pancreas/data/diabetes_diagnosis_model.pkl')