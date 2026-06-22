from django.shortcuts import render
from .forms import KidneyPredictionForm
from main_page.models import PatientData, FormVitals, PredictionData,DQScore
from heart.views import missing_data,data_quality_percentage
from django.contrib.auth.decorators import login_required
import joblib
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

from django.core.cache import cache
cache.clear()

kidney_prediction_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_prediction_model.pkl')
kidney_preprocessor = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_preprocessor.pkl')
kidney_diagnosis_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/kidney/data/kidney_diagnosis_model.pkl')

def process_kidney_data(data):
    
    # Define numeric and categorical features
    numeric_features = ['age', 'bp', 'bgr', 'bu', 'sc', 'sod', 'pot', 'hemo', 'pcv', 'wc', 'rc']
    categorical_features = ['sg','al', 'su', 'rbc', 'pc', 'pcc', 'ba', 'htn', 'dm', 'cad', 'appet', 'pe', 'ane']

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
    return kidney_preprocessor.transform(df_filled)
# Function to get user input for prediction

@login_required
def predict_kidney_disease(request):
    # Fetch the patient data from PatientData and FormVitals tables
    patient_data = PatientData.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = KidneyPredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # Prepare data for prediction
            data_for_prediction = {
                'age': patient_data.age,
                'bp': data['bp'],
                'sg': data['sg'],
                'al': data['al'],
                'su':data['su'],
                'bu': data['bu'],
                'rbc': data['rbc'],
                'pc': data['pc'],
                'pcc': data['pcc'],
                'ba': data['ba'],
                'bgr': data['bgr'],
                'sc': data['sc'],
                'sod': data['sod'],
                'pot': data['pot'],
                'hemo': data['hemo'],
                'pcv': data['pcv'],
                'wc': data['wc'],
                'rc': data['rc'],
                'htn': data['htn'],
                'dm': data['dm'],
                'cad': data['cad'],
                'appet': data['appet'],
                'pe': data['pe'],
                'ane': data['ane'],
            }
            try:
                input_data_transformed = process_kidney_data(data_for_prediction)

                #print("after transform\n")
                #print(input_data_transformed)
                print(data_for_prediction)
                # Make prediction
                kidney_prediction = kidney_prediction_model.predict(input_data_transformed)
                kidney_diagnosis = kidney_diagnosis_model.predict(input_data_transformed)
        
                # Save data to the UnifiedPrediction table
                prediction_result = PredictionData(
                    pid=patient_data,
                    bp=data['bp'],
                    sg=data['sg'],
                    al=data['al'],
                    su=data['su'],
                    bu=data['bu'],
                    rbc=data['rbc'],
                    pc=data['pc'],
                    pcc=data['pcc'],
                    ba=data['ba'],
                    bgr=data['bgr'],
                    sc=data['sc'],
                    sod=data['sod'],
                    pot=data['pot'],
                    hemo=data['hemo'],
                    pcv=data['pcv'],
                    wc=data['wc'],
                    rc=data['rc'],
                    htn=data['htn'],
                    dm=data['dm'],
                    cad=data['cad'],
                    appet=data['appet'],
                    pe=data['pe'],
                    ane=data['ane'],
                    prediction="Yes" if kidney_prediction[0] == 1 else "No",
                    prediction_type='kidney' , # Set prediction type to 'kidney'
                    diagnosis = kidney_diagnosis[0]
                )

                kidney_dq_score = DQScore(
                    prediction_type='kidney',
                    pid=patient_data,
                    data_quality_value = data_quality_percentage(data_for_prediction),
                    total_features_count = len(data_for_prediction.keys()),
                    missing_features_count = len(missing_data(data_for_prediction)),
                    missing_features = missing_data(data_for_prediction)
                )
                try:
                    prediction_result.save()
                    kidney_dq_score.save()
                except Exception as e:
                    logger.error(f"Error saving data: {e}")

                # Prepare context for rendering
                context = {
                    'form': form,
                    'patient': patient_data,
                    'prediction': 'Might have kidney problem' if kidney_prediction[0] == 1 else 'Do Not Have kidney problem',
                    'diagnosis':kidney_diagnosis[0],
                    'data_quality_report' : kidney_dq_score.data_quality_value,
                    'missing_columns' : kidney_dq_score.missing_features
                }

                return render(request, 'kidney/result.html', context)
            except Exception as e:
                logger.error(f"An error occurred: {e}")
        else:
            return render(request, 'kidney/predict.html', {'form': form, 'error': 'Invalid data. Please correct the errors and try again.'})
    else:
        form = KidneyPredictionForm()

    return render(request, 'kidney/predict.html', {'form': form})



def result(request):
    # You can add logic here for the result view
    return render(request, 'kidney/result.html')


