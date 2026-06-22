from django.shortcuts import render, redirect
from main_page.models import PatientData, FormVitals, PredictionData,DQScore
from django.contrib.auth.decorators import login_required
from heart.views import missing_data,data_quality_percentage
from .forms import LiverPredictionForm
import pandas as pd
import numpy as np
import joblib
import logging

logger = logging.getLogger('liver')

from django.core.cache import cache
cache.clear()

# Load the trained models and preprocessor (ensure paths are correct)
liver_predition_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/liver_prediction_model.pkl')
liver_diagnosis_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/liver_diagnosis_model.pkl')
liver_preprocessor = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/liver/data/liver_preprocessor.pkl')


def process_liver_data(data):
    # Define categorical and numeric features
    categorical_features = ['sex']
    numeric_features = ['age','total_bilirubin', 'direct_bilirubin',
       'alkaline_phosphotase_ALP', 'alamine_aminotransferase_ALT',
       'aspartate_aminotransferase_AST', 'total_proteins', 'albumin',
       'albumin_globulin_ratio']

    # Convert the input data (which is likely a dictionary) to a DataFrame
    df = pd.DataFrame([data])

    # Ensure all expected columns exist, adding missing ones as NA
    expected_columns = numeric_features + categorical_features
    for col in expected_columns:
        if col not in df.columns:
            df[col] = pd.NA

    # Select only the expected columns (in the correct order)
    df = df[expected_columns]

    # Fill missing values (here we use 0, but you can use other strategies if needed)
    df_filled = df.fillna(0)

    # Apply the preprocessor (e.g., one-hot encoding, scaling, etc.)
    return liver_preprocessor.transform(df_filled)

@login_required
def predict_liver_disease(request):

    # Fetch the patient data from PatientData and FormVitals tables
    patient_data = PatientData.objects.filter(user=request.user).first()
    #vitals_data = FormVitals.objects.filter(pid=patient_data).first()
    #vitals_data = FormVitals.objects.filter(pid=patient_data).order_by('-id').first()

    #logger.debug(f"Vitals Data: {vitals_data}")  # Ensure vitals_data is correctly populated

    if request.method == 'POST':
        form = LiverPredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Prepare data for prediction
            data_for_prediction = {
                'age': patient_data.age,
                'sex': patient_data.sex,
                'total_bilirubin': data['total_bilirubin'],
                'direct_bilirubin': data['direct_bilirubin'],
                'alkaline_phosphotase_ALP': data['alkaline_phosphotase_ALP'],
                'alamine_aminotransferase_ALT': data['alamine_aminotransferase_ALT'],
                'aspartate_aminotransferase_AST': data['aspartate_aminotransferase_AST'],
                'total_proteins': data['total_proteins'],
                'albumin': data['albumin'],
                'albumin_globulin_ratio': data['albumin_globulin_ratio']
            }
            
            try:
                logger.debug(f"Data for prediction: {data_for_prediction}")

                # Preprocess the input data
                input_data_transformed = process_liver_data(data_for_prediction)
                
                logger.debug(f"Transformed input data: {input_data_transformed}")

                # Predict diabetes status and diagnosis
                logger.info("Predicting liver status.")

                liver_prediction = liver_predition_model.predict(input_data_transformed)
                logger.debug(f"Liver prediction result: {liver_prediction}")

                logger.info("Predicting liver diagnosis.")

                liver_diagnosis = liver_diagnosis_model.predict(input_data_transformed)
                logger.debug(f"Liver diagnosis result: {liver_diagnosis}")

                # Save data to the PredictionData table
                prediction_result = PredictionData(
                    total_bilirubin=data['total_bilirubin'],
                    direct_bilirubin=data['direct_bilirubin'],
                    alkaline_phosphotase_ALP=data['alkaline_phosphotase_ALP'],
                    alamine_aminotransferase_ALT=data['alamine_aminotransferase_ALT'],
                    aspartate_aminotransferase_AST=data['aspartate_aminotransferase_AST'],
                    total_proteins=data['total_proteins'],
                    albumin=data['albumin'],
                    albumin_globulin_ratio=data['albumin_globulin_ratio'],
                    prediction="Yes" if liver_prediction == 1 else "No",
                    prediction_type='liver',
                    diagnosis=liver_diagnosis[0],
                    pid=patient_data
                )

                liver_dq_score = DQScore(
                    prediction_type='liver',
                    pid=patient_data,
                    data_quality_value = data_quality_percentage(data_for_prediction),
                    total_features_count = len(data_for_prediction.keys()),
                    missing_features_count = len(missing_data(data_for_prediction)),
                    missing_features = missing_data(data_for_prediction)
                )
                try:
                    prediction_result.save()
                    liver_dq_score.save()
                except Exception as e:
                    logger.error(f"Error saving data: {e}")

                # Render the result page with the prediction and diagnosis
                return render(request, 'liver/result.html', {
                    'patient': patient_data,
                    #'vitals': vitals_data,
                    'prediction': "Might have Liver disorder" if liver_prediction == 1 else "Do not have any Liver disorder",
                    'diagnosis': liver_diagnosis[0],
                    'data_quality_report' : liver_dq_score.data_quality_value,
                    'missing_columns' : liver_dq_score.missing_features
                })

            except Exception as e:
                logger.error(f"An error occurred: {e}")
                return render(request, 'liver/predict.html', 
                              {'form': form, 'error': f'An error occurred while processing your request.{e}'})

    else:
        form = LiverPredictionForm()
        
    return render(request, 'liver/predict.html', {'form': form})

def result(request):
    return render(request, 'liver/result.html')