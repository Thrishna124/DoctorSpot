from django.shortcuts import render
import pandas as pd
from .forms import PatientDataForm, FormVitalsForm, FitnessForm
from main_page.models import PatientData, PredictionData, FormVitals,DQScore
from heart.views import missing_data,data_quality_percentage
from django.contrib.auth.decorators import login_required
import logging
import joblib

logger = logging.getLogger(__name__)

from django.core.cache import cache
cache.clear()

# Load the trained models and preprocessor (ensure paths are correct)
fitness_prediction_model = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/fitness/data/fitness_model.pkl')
fitness_preprocessor = joblib.load('/Users/thrishna/Desktop/Critical_Django_project/docspot/fitness/data/fitness_preprocessor.pkl')

def daily_calories_needed(bmr, activity_level):
    activity_multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'super_active': 1.9
    }
    return round(bmr * activity_multipliers.get(activity_level, 1.2), 2)

def calculate_bmr(weight, height, age, gender):
    if gender == 'Male':
        return round((10 * weight) + (6.25 * height) - (5 * age) + 5, 2)
    else:
        return round((10 * weight) + (6.25 * height) - (5 * age) - 161, 2)
    

def classify_bmi(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 24.9:
        return 'Healthy Weight'
    elif 25 <= bmi < 29.9:
        return 'Over Weight'
    else:
        return 'Obese'


def process_fitness_data(data):
    # Define categorical and numeric features
    categorical_features = ['sex', 'activity_level']
    numeric_features = ['age', 'height', 'weight', 'total_steps', 'calories_burned', 'daily_calories_needed']

    # Convert the input data (which is likely a dictionary) to a DataFrame
    df = pd.DataFrame([data])

    # Ensure all expected columns exist, adding missing ones as NA
    expected_columns = numeric_features + categorical_features
    for col in expected_columns:
        if col not in df.columns:
            df[col] = pd.NA

    # Convert numeric columns to the correct type
    for col in numeric_features:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Select only the expected columns (in the correct order)
    df = df[expected_columns]
    print(df.head())
    # Fill missing values
    df_filled = df.fillna(0)
    print(df_filled.dtypes)
    # Apply the preprocessor (e.g., one-hot encoding, scaling, etc.)
    return fitness_preprocessor.transform(df_filled)


@login_required
def fitness_calculator(request):
    patient_data = PatientData.objects.filter(user=request.user).first()
    vitals_data = FormVitals.objects.filter(pid=patient_data).order_by('-id').first()

    logger.debug(f"Vitals Data: {vitals_data}")

    if request.method == 'POST':
        form = FitnessForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if not vitals_data:  # Ensure vitals_data is present
                logger.error("No vitals data found.")
                return render(request, 'fitness/predict.html', {'form': form, 'error': 'No vitals data found.'})

            try:
                # Prepare data for prediction
                BMR = calculate_bmr(vitals_data.weight, vitals_data.height, patient_data.age, patient_data.sex)
                daily_calories = daily_calories_needed(BMR, patient_data.lifestyle)
                bmi_category = classify_bmi(vitals_data.BMI)

                data_for_prediction = {
                    'age': patient_data.age,
                    'sex': patient_data.sex,
                    'height': vitals_data.height,
                    'weight': vitals_data.weight,
                    'total_steps': data['total_steps'],
                    'calories_burned': data['calories_burned'],
                    'daily_calories_needed': daily_calories,
                    'activity_level':patient_data.lifestyle
                }

                # Preprocess the input data
                input_data_transformed = process_fitness_data(data_for_prediction)

                # Predict fitness status
                fitness_prediction = fitness_prediction_model.predict(input_data_transformed)

                # Save data to the PredictionData table
                prediction_result = PredictionData(
                    BMR=BMR,
                    daily_calories_needed=daily_calories,
                    total_steps=data['total_steps'],
                    calories_burned=data['calories_burned'],
                    prediction='yes' if fitness_prediction[0] == 1 else 'no',
                    prediction_type='fitness',
                    pid=patient_data
                )

                fitness_dq_score = DQScore(
                    prediction_type='fitness',
                    pid=patient_data,
                    data_quality_value = data_quality_percentage(data_for_prediction),
                    total_features_count = len(data_for_prediction.keys()),
                    missing_features_count = sum(1 for value in data_for_prediction.values() if value is None or pd.isna(value)),
                    missing_features = missing_data(data_for_prediction)
                )
                prediction_result.save()
                fitness_dq_score.save()
                logger.info("Fitness data saved successfully.")

                context = {
                    'BMI': vitals_data.BMI,
                    'bmi_category':bmi_category,
                    'BMR': BMR,
                    'Daily_Calories': daily_calories,
                    'Fitness_Prediction': 'Good Fitness Score' if fitness_prediction[0] == 1 else 'Fitness score is low',
                    'data_quality_report' : fitness_dq_score.data_quality_value,
                    'missing_columns' : fitness_dq_score.missing_features
                }

                return render(request, 'fitness/result.html', context)

            except Exception as e:
                logger.error(f"Error during calculations or saving data: {e}")
                return render(request, 'fitness/predict.html', {'form': form, 'error': f"Error: {str(e)}"})

    else:
        form = FitnessForm()

    return render(request, 'fitness/predict.html', {'form': form})


def result(request):
    return render(request, 'fitness/result.html')
