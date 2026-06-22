import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression,LinearRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.svm import SVC
import joblib
import warnings

warnings.filterwarnings('ignore')

# Load CSV file
df = pd.read_csv('/Users/thrishna/Desktop/Critical_Django_project/docspot/fitness/data/synthetic_fitness_data.csv')
print(df.columns)

categorical_features = ['sex','activity_level']
numerical_features = ['age','height', 'weight',
       'total_steps', 'calories_burned',
       'daily_calories_needed']

# Define features and target variable
X = df[numerical_features + categorical_features]
y = df['prediction']

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=52)

# Create the preprocessor
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
    ])


# Fit and transform the training data
X_train_transformed = preprocessor.fit_transform(X_train)
X_test_transformed = preprocessor.transform(X_test)

model = RandomForestClassifier(class_weight='balanced',random_state=37)
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

joblib.dump(model, '/Users/thrishna/Desktop/Critical_Django_project/docspot/fitness/data/fitness_model.pkl')
joblib.dump(preprocessor, '/Users/thrishna/Desktop/Critical_Django_project/docspot/fitness/data/fitness_preprocessor.pkl')