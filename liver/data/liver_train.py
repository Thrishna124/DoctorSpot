import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.svm import SVC
import joblib
import warnings

warnings.filterwarnings('ignore')

# Load CSV file
df = pd.read_csv('/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/indian_liver_patient.csv')
print(df.columns)

# Rename columns for clarity
df.rename(columns={
    'Alkaline_Phosphotase': 'alkaline_phosphotase_ALP',
    'Total_Bilirubin': 'total_bilirubin',
    'Alamine_Aminotransferase': 'alamine_aminotransferase_ALT',
    'Direct_Bilirubin': 'direct_bilirubin',
    'Aspartate_Aminotransferase': 'aspartate_aminotransferase_AST',
    'Albumin': 'albumin',
    'Albumin_and_Globulin_Ratio': 'albumin_globulin_ratio',
    'Total_Protiens': 'total_proteins',
    'Dataset': 'prediction',
    'Gender': 'sex',
    'Age': 'age'
}, inplace=True)

# Convert prediction values
df['prediction'] = df['prediction'].replace({2: 0})

# Diagnosis function based on some simple rules
def liver_disease_diagnosis(row):
    if row['total_bilirubin'] > 1.2 or row['direct_bilirubin'] > 0.3:
        return 'Possible Liver Disease'
    elif row['alkaline_phosphotase_ALP'] > 120:
        return 'Possible Bile Duct Obstruction or Liver Disease'
    elif (row['alamine_aminotransferase_ALT'] > 40 or row['aspartate_aminotransferase_AST'] > 40):
        return 'Possible Hepatitis or Liver Damage'
    elif row['albumin'] < 3.5:
        return 'Possible Chronic Liver Disease'
    elif row['albumin_globulin_ratio'] < 1.0:
        return 'Possible Liver Disease'
    else:
        return 'Normal'

# Apply the diagnosis function
df['diagnosis'] = df.apply(liver_disease_diagnosis, axis=1)


categorical_features = ['sex']
numerical_features = ['age','total_bilirubin', 'direct_bilirubin',
       'alkaline_phosphotase_ALP', 'alamine_aminotransferase_ALT',
       'aspartate_aminotransferase_AST', 'total_proteins', 'albumin',
       'albumin_globulin_ratio']

# Remove outliers using IQR
Q1 = df[numerical_features].quantile(0.25)
Q3 = df[numerical_features].quantile(0.75)
IQR = Q3 - Q1

# Filter out rows outside of 1.5*IQR
df_no_outliers = df[~((df[numerical_features] < (Q1 - 1.5 * IQR)) | (df[numerical_features] > (Q3 + 1.5 * IQR))).any(axis=1)]

print(f"Shape of original data: {df.shape}")
print(f"Shape after removing outliers: {df_no_outliers.shape}")

df = df_no_outliers.dropna()

print(df.shape)

# Define features and target variable
X = df[numerical_features + categorical_features]
y = df['prediction']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=52)

preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])


# Fit and transform the training data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = RandomForestClassifier(class_weight='balanced',random_state=31)
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

joblib.dump(model, '/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/liver_prediction_model.pkl')
joblib.dump(preprocessor, '/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/liver_preprocessor.pkl')

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

joblib.dump(model,'/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/liver_diagnosis_model.pkl')