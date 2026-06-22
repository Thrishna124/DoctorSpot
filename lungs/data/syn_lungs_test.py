import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder

# Load the pre-trained model
import joblib

# Load the trained model and preprocessor from pickle files
rf_model = joblib.load('/Users/thrishna/Desktop/PythonProject/PI/lungs/lung_rf_model.pkl')
preprocessor = joblib.load('/Users/thrishna/Desktop/PythonProject/PI/lungs/lung_rf_preprocessor.pkl')

# Load the new data (test data)
# Example test data as a dictionary
test_data_dict = {
    'Height': [170, 160],  # in cm
    'Weight': [70, 60],    # in kg
    'Age': [45, 55],
    'FEV1': [2.5, 3.0],    # FEV1 in liters
    'FVC': [3.0, 4.0],     # FVC in liters
    'FEV1_FVC': [80, 75],  # FEV1/FVC ratio
    'PEFR': [400, 500],    # PEFR in L/min
    'DLCO': [20, 22],      # DLCO in ml/min/mmHg
    'PaO2': [95, 90],      # PaO2 in mmHg
    'PaCO2': [40, 38],     # PaCO2 in mmHg
    'Gender': ['Male', 'Female'],
}

# Convert dictionary to DataFrame
df_test = pd.DataFrame(test_data_dict)

# Print the DataFrame to verify
print(df_test)
# Preprocess the new data similar to how you did with training data

# Assuming you have similar preprocessing as the training step:
df_test['Height_m'] = df_test['Height'] / 100  # Convert height from cm to meters
df_test['BMI'] = df_test['Weight'] / (df_test['Height_m'] ** 2)

# Adjust FEV1 and FVC for age
df_test['FEV1_Age_Adjusted'] = df_test['FEV1'] / df_test['Age']
df_test['FVC_Age_Adjusted'] = df_test['FVC'] / df_test['Age']

# Create a ratio between PaO2 and PaCO2
df_test['PaO2_PaCO2_Ratio'] = df_test['PaO2'] / df_test['PaCO2']

# Binning Age, PaO2, and FVC into categories
df_test['Age_Binned'] = pd.cut(df_test['Age'], bins=[0, 30, 50, 70, 100], labels=['<30', '30-50', '50-70', '>70'])
df_test['PaO2_Binned'] = pd.cut(df_test['PaO2'], bins=[0, 60, 80, 100, 200], labels=['Low', 'Normal', 'High', 'Very High'])
df_test['FVC_Binned'] = pd.cut(df_test['FVC'], bins=[0, 2.0, 3.0, 4.0, 5.0], labels=['Very Low', 'Low', 'Normal', 'High'])

# Define categorical and numerical columns (same as in training)
categorical_features = ['Gender', 'Age_Binned', 'PaO2_Binned', 'FVC_Binned']
numerical_features = ['BMI', 'FEV1_FVC', 'PEFR', 'DLCO', 'FVC_Age_Adjusted', 'PaO2_PaCO2_Ratio']

# Create a column transformer to handle preprocessing (just like in training)

# Preprocess the test data
X_test_preprocessed = preprocessor.transform(df_test)

# Apply preprocessing to the test features
X_test = preprocessor.transform(df_test)

# Make predictions
predictions = rf_model.predict(X_test)

df_test['Result']= 0 if predictions[0] == 0 else 1

# Print predictions
print("Predictions for the test data:")
# Print predictions
print(predictions)
# If you want the predicted probabilities (for some models like Logistic Regression, Random Forest, etc.)
if hasattr(rf_model, 'predict_proba'):
    y_pred_proba = rf_model.predict_proba(X_test_preprocessed)[:, 1]
    print("Predicted probabilities:")
    print(y_pred_proba)
