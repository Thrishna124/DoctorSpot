from django.shortcuts import render, redirect
from main_page.models import PatientData, FormVitals, PredictionData,DQScore
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from heart.views import missing_data,data_quality_percentage
from .forms import LungsPredictionForm
import pandas as pd
import joblib
import logging

logger = logging.getLogger(__name__)

from django.core.cache import cache
cache.clear()

# Load the trained models and preprocessor (ensure paths are correct)
lungs_predition_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/lung_prediction_model.pkl')
lungs_diagnosis_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/lung_diagnosis_model.pkl')
lungs_preprocessor = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/lungs/data/lung_preprocessor.pkl')


def process_lungs_data(data):
    # Define categorical and numeric features
    categorical_features = ['sex']
    numeric_features = ['age', 'height', 'weight', 'predicted_FEV1', 'predicted_VC',
       'actual_FEV1', 'actual_VC', 'fev1_vc_ratio']

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
    return lungs_preprocessor.transform(df_filled)

@login_required
def predict_lung_disease(request):
    # Fetch the patient data from PatientData and FormVitals tables
    patient_data = PatientData.objects.filter(user=request.user).first()
    # Get the latest vital records for each patient

    vitals_data = FormVitals.objects.filter(pid=patient_data).order_by('-id').first()
    logger.debug(f"Vitals Data: {vitals_data}")  # Ensure vitals_data is correctly populated

    if request.method == 'POST':
        form = LungsPredictionForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            # Prepare data for prediction
            data_for_prediction = {
                'age': patient_data.age,
                'sex': patient_data.sex,
                'height':vitals_data.height,
                'weight':vitals_data.weight,
                'predicted_FEV1': data['predicted_FEV1'],
                'predicted_VC': data['predicted_VC'],
                'actual_FEV1': data['actual_FEV1'],
                'actual_VC': data['actual_VC'],
                'fev1_vc_ratio': data['fev1_vc_ratio'],
            }
            
            try:
                # Preprocess the input data
                input_data_transformed = process_lungs_data(data_for_prediction)

                # Predict diabetes status and diagnosis
                lungs_prediction = lungs_predition_model.predict(input_data_transformed)
                lungs_diagnosis = lungs_diagnosis_model.predict(input_data_transformed)
                
                # Save data to the PredictionData table
                prediction_result = PredictionData(
                    predicted_FEV1=data['predicted_FEV1'],
                    predicted_VC=data['predicted_VC'],
                    actual_FEV1=data['actual_FEV1'],
                    actual_VC=data['actual_VC'],
                    fev1_vc_ratio=data['fev1_vc_ratio'],
                    prediction="Yes" if lungs_prediction == 1 else "No",
                    prediction_type='lungs',
                    diagnosis=lungs_diagnosis[0],
                    pid=patient_data
                )

                lungs_dq_score = DQScore(
                    prediction_type='lungs',
                    pid=patient_data,
                    data_quality_value = data_quality_percentage(data_for_prediction),
                    total_features_count = len(data_for_prediction.keys()),
                    missing_features_count = len(missing_data(data_for_prediction)),
                    missing_features = missing_data(data_for_prediction)
                )

                prediction_result.save()
                lungs_dq_score.save()

                # Render the result page with the prediction and diagnosis
                return render(request, 'lungs/result.html', {
                    'patient': patient_data,
                    #'vitals': vitals_data,
                    'prediction': "Might have Lung disorder" if lungs_prediction == 1 else "Do not have any Lung disorder",
                    'diagnosis': lungs_diagnosis[0],
                    'data_quality_report' : lungs_dq_score.data_quality_value,
                    'missing_columns' : lungs_dq_score.missing_features
                })

            except Exception as e:
                logger.error(f"An error occurred: {e}")
                return render(request, 'lungs/predict.html', 
                              {'form': form, 'error': f'An error occurred while processing your request.{e}'})

    else:
        form = LungsPredictionForm()
        
    return render(request, 'lungs/predict.html', {'form': form})

def result(request):
    return render(request, 'lungs/result.html')
