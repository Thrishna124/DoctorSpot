from django.shortcuts import render, redirect
from main_page.models import PatientData, FormVitals, PredictionData,DQScore
from django.contrib.auth.decorators import login_required
from main_page.forms import PredictionDataForm
from heart.forms import HeartPredictionForm
import pandas as pd
import joblib
import logging

logger = logging.getLogger(__name__)

from django.core.cache import cache
cache.clear()


heart_predition_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/heart/data/heart_prediction_model.pkl')
heart_diagnosis_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/heart/data/heart_diagnosis_model.pkl')
heart_preprocessor = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/heart/data/heart_preprocessor.pkl')

def process_heart_data(data):
    numeric_features = ['age', 'restingBP', 'cholesterol', 'fastingbloodsugar', 
            'maxheartrate', 'oldpeak']
    categorical_features = ['sex','chestpain','restingrelectro','exerciseangia','slope','noofmajorvessels']
    
    # Convert the input data (which is likely a dictionary) to a DataFrame
    df = pd.DataFrame([data])

    # Drop column 0 if it exists
    if 0 in df.columns:
        df.drop(columns=0, inplace=True)

    # Log the DataFrame before transformation
    logger.debug(f"DataFrame before transformation: {df}")

    # Ensure all expected columns exist, adding missing ones as NA
    expected_columns = numeric_features + categorical_features
    for col in expected_columns:
        if col not in df.columns:
            df[col] = pd.NA

    # Select only the expected columns (in the correct order)
    df = df[expected_columns]

    # Fill missing values (here we use 0, but you can use other strategies if needed)
    df_filled = df.fillna(0)
    

    # Log the filled DataFrame
    logger.debug(f"Filled DataFrame: {df_filled}")
    print(f"Filled DataFrame: {df_filled}")

     # Apply the preprocessor (e.g., one-hot encoding, scaling, etc.)
    return heart_preprocessor.transform(df_filled)

def data_quality_percentage(data_values):

                # Calculate the number of valid entries (not None or 'None')
    valid_count = sum(1 for value in data_values.values() if value is not None and value != 'None')
    total_columns = len(data_values)
     

    # Calculate the percentage of valid data
    data_quality_value = (valid_count / total_columns) * 100 if total_columns > 0 else 0
    return round(data_quality_value,1)

def missing_data (data):
    output = []
    for key, value in data.items():  # Iterate over the key-value pairs
        if value is None:  # Check if the value is None
            output.append(key)  # Add the key (column name) to the output list
    return output

@login_required
def predict_heart_disease(request):
    # Fetch the patient data from PatientData and FormVitals tables
    patient_data = PatientData.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = HeartPredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # Prepare data for prediction
            data_for_prediction = {
                'age': patient_data.age,
                'sex': '0' if patient_data.sex == 'Female' else '1',
                'chestpain': data['chestpain'],
                'restingBP': data['restingBP'],
                'cholesterol': data['cholesterol'],
                'fastingbloodsugar': data['fastingbloodsugar'],
                'restingrelectro': data['restingrelectro'],
                'maxheartrate': data['maxheartrate'],
                'exerciseangia': data['exerciseangia'],
                'oldpeak': data['oldpeak'],
                'slope': data['slope'],
                'noofmajorvessels': data['noofmajorvessels']
            }
            try:
                # Preprocess the input data
                input_data_transformed = process_heart_data(data_for_prediction)
                print(data_for_prediction)
                # Predict diabetes status and diagnosis
                heart_prediction = heart_predition_model.predict(input_data_transformed)
                heart_diagnosis = heart_diagnosis_model.predict(input_data_transformed)
                
                # Save data to the PredictionData table
                prediction_result = PredictionData(
                    chestpain=data['chestpain'],
                    restingBP=data['restingBP'],
                    cholesterol=data['cholesterol'],
                    fastingbloodsugar=data['fastingbloodsugar'],
                    restingrelectro=data['restingrelectro'],
                    maxheartrate=data['maxheartrate'],
                    exerciseangia=data['exerciseangia'],
                    oldpeak=data['oldpeak'],
                    slope=data['slope'],
                    noofmajorvessels=data['noofmajorvessels'],
                    prediction="Yes" if heart_prediction == 1 else "No",
                    prediction_type='heart',
                    diagnosis=heart_diagnosis[0],
                    pid=patient_data
                )
                

                heart_dq_score = DQScore(
                    prediction_type='heart',
                    pid=patient_data,
                    data_quality_value = data_quality_percentage(data_for_prediction),
                    total_features_count = len(data_for_prediction.keys()),
                    missing_features_count = len(missing_data(data_for_prediction)),
                    missing_features = missing_data(data_for_prediction)
                )
                prediction_result.save()
                heart_dq_score.save()

                # Render the result page with the prediction and diagnosis
                return render(request, 'heart/result.html', {
                    'patient': patient_data,
                    'prediction': "Might have heart problem" if heart_prediction == 1 else "Does Not Have heart problem",
                    'diagnosis': heart_diagnosis[0],
                    'data_quality_report' : heart_dq_score.data_quality_value,
                    'missing_columns' : heart_dq_score.missing_features
                })

            except Exception as e:
                logger.error(f"An error occurred: {e}")
                return render(request, 'heart/predict.html', 
                              {'form': form, 'error': f'An error occurred while processing your request.{e}'})
    else:
        form = HeartPredictionForm()
    
    return render(request, 'heart/predict.html', {'form': form})


def result(request):
    # You can add logic here for the result view
    return render(request, 'heart/result.html')

