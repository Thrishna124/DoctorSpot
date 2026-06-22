import numpy as np
import tensorflow as tf
from django.shortcuts import render, redirect
from .forms import LungCancerPredictionForm
from main_page.models import PredictionData, PatientData, FormVitals,DQScore
from django.contrib.auth.decorators import login_required
from tensorflow.keras.preprocessing import image
import logging
import os

logger = logging.getLogger(__name__)

from django.core.cache import cache
cache.clear()

# Load the model
lung_cancer_prediction_model = tf.keras.models.load_model('/Users/thrishna/Desktop/Critical_Django_project/docspot/lung_cancer/data/lung_cancer_normal_model.keras')
#lung_cancer_model = tf.keras.models.load_model('/Users/thrishna/Desktop/Critical_Django_project/docspot/lung_cancer/data/lung_cancer_model.keras')
lung_cancer_diagnosis_model = tf.keras.models.load_model('/Users/thrishna/Desktop/Critical_Django_project/docspot/lung_cancer/data/lung_cancer_model.h5')
def ensure_media_directory():
    media_root = os.path.join('/Users/thrishna/Desktop/Critical_Django_project/docspot/media', 'lung_cancer/data/uploads')
    if not os.path.exists(media_root):
        os.makedirs(media_root)
        print(f"Created media directory: {media_root}")
    else:
        print(f"Media directory already exists: {media_root}")

def predict_lung_cancer_fct(img_path):
    try:
        img = image.load_img(img_path, target_size=(150, 150))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize
        predictions = lung_cancer_prediction_model.predict(img_array)
        return np.argmax(predictions)
    except Exception as e:
        logger.error(f"Error predicting lung cancer: {e}")
        return None
    
def diagnose_lung_cancer_fct(img_path):
    try:
        img = image.load_img(img_path, target_size=(150, 150))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize
        diagnosis = lung_cancer_diagnosis_model.predict(img_array)
        return np.argmax(diagnosis)
    except Exception as e:
        logger.error(f"Error diagnosing lung cancer: {e}")
        return None



@login_required
def predict_lung_cancer(request):
    patient_data = PatientData.objects.filter(user=request.user).first()

    if request.method == 'POST':
        form = LungCancerPredictionForm(request.POST, request.FILES)
        if form.is_valid():
            ensure_media_directory()  # Ensure the media directory exists

            # Save the prediction instance to create the image path
            prediction_instance = form.save(commit=False)
            prediction_instance.pid = patient_data  # Link the prediction to the patient
            prediction_instance.prediction_type = 'lung_cancer'
            prediction_instance.save()  # Save the instance to get the correct image path
            
            img_path = prediction_instance.image.path  # Get the image path after saving
            logger.info(f"Image path for prediction: {img_path}")  # Log the path
            
            # Check if the image file actually exists
            if not os.path.exists(img_path):
                logger.error(f"File does not exist for prediction: {img_path}")
                return render(request, 'lung_cancer/predict.html', {'form': form, 'error': 'Uploaded file not found. Please try again.'})

            predicted_class = predict_lung_cancer_fct(img_path)

            class_labels = ['normal', 'benign', 'malignant']
            
            if predicted_class is not None:
                #prediction_instance.diagnosis = class_labels[predicted_class]
                prediction_instance.prediction = 'yes' if class_labels[predicted_class] in ['malignant', 'benign'] else 'no'

            diagnosis_class = diagnose_lung_cancer_fct(img_path)

            class_labels = ['normal', 'benign', 'malignant']

            if diagnosis_class is not None:
                prediction_instance.diagnosis = class_labels[diagnosis_class]
                
                prediction_instance.save()  # Save any additional updates


                lung_cancer_dq_score = DQScore(
                    prediction_type=prediction_instance.prediction_type,
                    pid=prediction_instance.pid,
                    data_quality_value=100 if os.path.exists(img_path) else 0,
                    total_features_count=1,
                    missing_features_count=0 if os.path.exists(img_path) else 1,
                    missing_features=None if os.path.exists(img_path) else 'Image'
                )
                lung_cancer_dq_score.save()  # Ensure to save the DQ score

                logger.info(f"Prediction saved for user {request.user}: {prediction_instance.diagnosis}")
                return redirect('lung_cancer:lung_cancer_result', pk=prediction_instance.pk)
            else:
                logger.error("Prediction could not be made.")
                return render(request, 'lung_cancer/predict.html', {'form': form, 'error': 'Prediction failed. Please try again.'})
    else:
        form = LungCancerPredictionForm()

    return render(request, 'lung_cancer/predict.html', {'form': form})


def result(request, pk):
    try:
        prediction_instance = PredictionData.objects.get(pk=pk)
        lung_cancer_dq_scores = DQScore.objects.filter(pid=prediction_instance.pid, prediction_type='lung_cancer')
        
        if lung_cancer_dq_scores.exists():
            lung_cancer_dq_score = lung_cancer_dq_scores.first()
            missing_features = lung_cancer_dq_score.missing_features
            
            # Change this to a more user-friendly representation if needed
            if isinstance(missing_features, str):
                if missing_features.lower() == 'image':
                    missing_features = "Image feature is missing"
                else:
                    missing_features = "Missing features: " + missing_features
            
        else:
            logger.error(f"No DQScore found for prediction with id {pk}.")
            lung_cancer_dq_score = None
            missing_features = "No missing features."
        
        context = {
            'patient': prediction_instance.pid,
            'prediction': "Might have Lung disorder" if prediction_instance.prediction == 'yes' else "Do not have any Lung disorder",
            'diagnosis': prediction_instance.diagnosis,
            'data_quality_report': lung_cancer_dq_score.data_quality_value if lung_cancer_dq_score else None,
            'missing_columns': missing_features
        }

        return render(request, 'lung_cancer/result.html', context)

    except PredictionData.DoesNotExist:
        logger.error(f"PredictionData with id {pk} does not exist.")
        return render(request, 'lung_cancer/predict.html', {'message': 'Prediction not found.'})
