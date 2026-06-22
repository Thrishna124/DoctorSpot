import pandas as pd
import numpy as np
from sklearn.model_selection import StratifiedShuffleSplit

# Set the random seed for reproducibility
np.random.seed(42)

# Define the number of samples for each class
num_samples_per_class = 250  # 1000 records, balanced over 4 classes

# Define the total number of samples
num_samples = num_samples_per_class * 4

# Generate synthetic data for age, height, weight, and gender
ages = np.random.randint(18, 80, size=num_samples)
heights = np.random.normal(170, 10, size=num_samples)  # in cm
weights = np.random.normal(70, 15, size=num_samples)   # in kg
genders = np.random.choice(['Male', 'Female'], size=num_samples)


# Define placeholder coefficients (extracted from the article)
coefficients = {
    'Male': {
        'FEV1': {'a': -4.6899, 'b': -0.0286, 'c': 0.0533},
        'VC': {'f': -2.5370, 'g': -0.0211, 'h': 0.0418},
    },
    'Female': {
        'FEV1': {'a': -0.254, 'b': -0.027, 'c': 0.021},
        'VC': {'f': -0.902, 'g': -0.025, 'h': 0.027},
    }
}

# Function to calculate predicted FEV1 and VC
def calculate_predicted_values(age, height, gender):
    coeff = coefficients[gender]
    predicted_FEV1 = coeff['FEV1']['a'] + coeff['FEV1']['b'] * age + coeff['FEV1']['c'] * height
    predicted_VC = coeff['VC']['f'] + coeff['VC']['g'] * age + coeff['VC']['h'] * height
    return predicted_FEV1, predicted_VC

# Calculate predicted FEV1 and VC values
predicted_fev1_values = []
predicted_vc_values = []

for age, height, gender in zip(ages, heights, genders):
    fev1_pred, vc_pred = calculate_predicted_values(age, height, gender)
    predicted_fev1_values.append(fev1_pred)
    predicted_vc_values.append(vc_pred)

# Convert to numpy arrays
predicted_fev1_values = np.array(predicted_fev1_values)
predicted_vc_values = np.array(predicted_vc_values)

# Generate actual FEV1 and VC values around the predicted values
actual_fev1_values = predicted_fev1_values * np.random.normal(1, 0.1, size=num_samples)
actual_vc_values = predicted_vc_values * np.random.normal(1, 0.1, size=num_samples)

# Calculate FEV1/VC ratio
fev1_vc_ratios = actual_fev1_values / actual_vc_values

# Define LLN for FEV1/VC (arbitrary value for illustration)
fev1_vc_lln = 0.7

# Functions to get FEV1 and VC range for LLN calculations
def fev1_range(age, gender):
    if gender == 'Male':
        return (5.5 - 0.03*age, 4.75 - 0.025*age)
    else:
        return (3.75 - 0.02*age, 3.25 - 0.02*age)

def vc_range(age, gender):
    if gender == 'Male':
        return (4.5 - 0.02*age, 3.5 - 0.02*age)
    else:
        return (3.25 - 0.015*age, 2.5 - 0.015*age)

# Classify the data using the flowchart
def classify_spirometry(fev1, vc, fev1_vc_ratio, gender, age):
    fev1_lln = fev1_range(age, gender)[1]  # Use the LLN threshold
    vc_lln = vc_range(age, gender)[1]
    
    if fev1_vc_ratio < fev1_vc_lln:
        if fev1 < fev1_lln and vc < vc_lln:
            return 'Obstructive or Mixed'
        else:
            return 'Obstructive'
    else:
        if vc < vc_lln:
            return 'Restrictive'
        else:
            return 'Normal'


# Classify the data
classifications = [classify_spirometry(fev1, vc, ratio, gender, age) for fev1, vc, ratio, gender, age in zip(actual_fev1_values, actual_vc_values, fev1_vc_ratios, genders, ages)]
# Create the DataFrame
df = pd.DataFrame({
    'age': ages,
    'height': heights,
    'weight': weights,
    'sex': genders,
    'predicted_FEV1': predicted_fev1_values,
    'predicted_VC': predicted_vc_values,
    'actual_FEV1': actual_fev1_values,
    'actual_VC': actual_vc_values,
    'fev1_vc_ratios': fev1_vc_ratios,
    'classification': classifications,
    'prediction': [0 if cls == 'Normal' else 1 for cls in classifications]
})

# Check the number of records per classification
#class_counts = df['prediction'].value_counts()
#print(class_counts)

# Balance the dataset
#balanced_df_list = []
#for cls in class_counts.index:
#    sample_size = min(num_samples_per_class, class_counts[cls])
#    balanced_df_list.append(df[df['prediction'] == cls].sample(sample_size, random_state=42))

#balanced_df = pd.concat(balanced_df_list).sample(frac=1, random_state=42)  # Shuffle the combined DataFrame

#print(balanced_df.head())

# Save to CSV
#balanced_df.to_csv('synthetic_lung_data.csv', index=False)

# Set the random seed for reproducibility
#np.random.seed(42)

# Define the total number of samples you want for your dataset
#total_samples = 900  # Adjust this value as needed
# Initialize StratifiedShuffleSplit with the desired number of splits and test size
#split = StratifiedShuffleSplit(n_splits=1, test_size=None, train_size=total_samples, random_state=42)

# Stratify based on the 'Classification' column to ensure class balance
#for train_index, _ in split.split(df, df['prediction']):
#    stratified_sample = df.iloc[train_index]

# Shuffle the dataset
#stratified_sample = stratified_sample.sample(frac=1, random_state=42)

# Check the distribution of classes after stratified sampling
#print(stratified_sample['Classification'].value_counts())

# Save to CSV
#stratified_sample.to_csv('stratified_synthetic_lung_data.csv', index=False)
df.to_csv('syn_lung_dataset.csv',index=False)