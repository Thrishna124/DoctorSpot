# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression,LinearRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

# Load the dataset
df = pd.read_csv("/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/syn_lung_dataset.csv")
print(df.columns)
df.rename(columns={'classification':'diagnosis','fev1_vc_ratios':'fev1_vc_ratio'},inplace=True)

#numeric and categoric data

categorical_features = ['sex']
numerical_features = ['age', 'height', 'weight', 'predicted_FEV1', 'predicted_VC',
       'actual_FEV1', 'actual_VC', 'fev1_vc_ratio']

# Remove outliers using IQR
Q1 = df[numerical_features].quantile(0.15)
Q3 = df[numerical_features].quantile(0.85)
IQR = Q3 - Q1

# Filter out rows outside of 1.5*IQR
df_no_outliers = df[~((df[numerical_features] < (Q1 - 1.5 * IQR)) | (df[numerical_features] > (Q3 + 1.5 * IQR))).any(axis=1)]

print(f"Shape of original data: {df.shape}")
print(f"Shape after removing outliers: {df_no_outliers.shape}")

df = df_no_outliers.copy()

print(df.shape)
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# Define features and target variable
X = df[numerical_features + categorical_features]
y = df['prediction']

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

print(f'Prediction: Accuracy: {accuracy:.4f}')
print('Confusion Matrix:')
print(conf_matrix)

joblib.dump(model, '/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/lung_prediction_model.pkl')
joblib.dump(preprocessor, '/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/lung_preprocessor.pkl')


# Define features and target variable
X = df[numerical_features + categorical_features]
y = df['diagnosis']

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

joblib.dump(model,'/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/lung_diagnosis_model.pkl')