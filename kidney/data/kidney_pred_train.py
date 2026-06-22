import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
import joblib
# Load the dataset
data = pd.read_csv('/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_disease.csv')

# Drop unwanted columns
data.drop(columns=['id'], inplace=True)

# Replace unwanted characters
def replace_fct(data):
    for column in data.columns:
        data[column] = data[column].replace(['?', '\t','\t?'], np.nan)
    return data

data = replace_fct(data)

# Handle missing values
data.dropna(thresh=data.shape[1] - 3, inplace=True)
data.fillna(data.mode().iloc[0], inplace=True)
data['classification'].replace("ckd\t","ckd",inplace=True)

#for column in data.columns:
#    print('****************',column,'********************')
#    print(set(data[column].to_list()))

data['pcv'] = pd.to_numeric(data['pcv'], errors='coerce')
data['wc'] = pd.to_numeric(data['wc'], errors='coerce')
data['rc'] = pd.to_numeric(data['rc'], errors='coerce')
data['sg'] = data['sg'].astype('object')
data['al'] = data['al'].astype('object')
data['su'] = data['su'].astype('object')
data.rename(columns={'classification':'prediction'},inplace=True)
print(data.head())

def diagnose_kidney_conditions(row):
    # Chronic Kidney Disease (CKD)
    if (row['age'] > 60 and (row['bu'] > 20 or row['sc'] > 1.2)) and (row['htn'] == 'yes' and row['dm'] == 'yes'):
        return "Chronic Kidney Disease (CKD)"
    
    # Acute Kidney Injury (AKI) based on more accurate thresholds
    elif (row['bu'] > 35) and (row['sc'] > 1.5 and row['rc'] < 3.5):
        return "Acute Kidney Injury (AKI)"
    
    # Diabetic Nephropathy
    elif row['dm'] == 'yes' and (row['bu'] > 20 or row['sc'] > 1.2):
        return "Diabetic Nephropathy"
    
    # Hypertensive Nephropathy
    elif row['htn'] == 'yes' and (row['bu'] > 20 or row['sc'] > 1.2):
        return "Hypertensive Nephropathy"
    
    # Urinary Tract Infection (UTI)
    elif row['pcc'] == 'present' and (row['wc'] > 11 and row['rbc'] == 'normal'):
        return "Urinary Tract Infection (UTI)"
    
    # Nephrotic Syndrome
    elif row['al'] == 4 and (row['su'] == 3 and row['rbc'] == 'abnormal'):
        return "Nephrotic Syndrome"
    
    # Normal condition
    else:
        return "Normal"
        
data['diagnosis'] = data.apply(diagnose_kidney_conditions, axis=1)

# Define numeric and categorical features
numerical_features = ['age', 'bp','bgr','bu','sc','sod','pot','hemo','pcv','wc','rc']
categorical_features = ['al', 'su','sg','rbc','pc','pcc','ba','htn','dm','cad','appet','pe','ane']

# Encode categorical features
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])


# Split the data into features (X) and target (y)
X = data[numerical_features + categorical_features]
y = data['prediction']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit and transform the data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

# Train the Random Forest Classifier model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_transformed, y_train)

# Make predictions
y_pred = model.predict(X_test_transformed)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.2f}')

# Save models
joblib.dump(model, '/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_prediction_model.pkl')
joblib.dump(preprocessor, '/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_preprocessor.pkl') 

# Define features and target variable
X = data[numerical_features + categorical_features]
y = data['diagnosis']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Fit and transform the training data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = RandomForestClassifier(class_weight='balanced')
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

joblib.dump(model,'/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_diagnosis_model.pkl')