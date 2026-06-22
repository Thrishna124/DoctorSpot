from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RegisterForm, PatientDataForm, VitalDetailsForm,PatientDataUpdateForm,VitalDetailsUpdateForm
from .models import PatientData, FormVitals,PredictionData,DQScore
from django.contrib.auth.forms import AuthenticationForm
from .forms import calculate_bmi,calculate_bmi_status
from django.db.models import OuterRef, Subquery, F, Window
from django.db.models.functions import Trunc,RowNumber,TruncSecond
import logging

logger = logging.getLogger('main_page')

from django.core.cache import cache
cache.clear()


# Registration View
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            messages.success(request, f"Account created for {user.username}!")
            return redirect('main_page:login_view')
    else:
        form = RegisterForm()
    
    return render(request, 'main_page/register.html', {'form': form})

# Login View
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                #messages.success(request, f"Welcome, {username}!")
                
                # Check if patient and vitals data exist
                patient_data = PatientData.objects.filter(user=request.user).first()
                if patient_data is None:
                    messages.info(request, 'No patient data found. Please add your information.')
                    return redirect('main_page:enter_patient_data')

                # Now that we know patient_data is not None, we can safely get vitals_data
                vitals_data = FormVitals.objects.filter(pid=patient_data)

                if not vitals_data.exists():  # Check if vitals_data is empty
                    messages.info(request, 'No vitals data found. Please enter your vitals.')
                    return redirect('main_page:enter_form_vitals')
                
                else:
                    return redirect('main_page:home')
    else:
        form = AuthenticationForm()
    return render(request, 'main_page/login.html', {'form': form})

# Logout View
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('main_page:login_view')  # Redirect to login page after logout

#@login_required
# Home View
#def home(request):
#    patient_data = PatientData.objects.get(user=request.user)
#    return render(request, 'main_page/home.html', {'patient': patient_data})

# View Vital Info
def view_vital_info(request):
    if request.user.is_authenticated:
        patient_data = PatientData.objects.get(user=request.user)
        vitals = FormVitals.objects.filter(pid=patient_data.pid)
        return render(request, 'main_page/view_vital_info.html', {'vitals': vitals,'patient_data':patient_data})
    return redirect('main_page:login_view')  # Redirect if not authenticated


# update Vital Info
@login_required
def update_form_vitals(request):
        patient_data = PatientData.objects.get(user=request.user)
        vitals_data = FormVitals.objects.filter(pid=patient_data.pid).first()

        if vitals_data is None:
            messages.info(request, 'No vitals data found. Please add your health information.')
            return redirect('main_page:enter_form_vitals')

        if request.method == 'POST':
            form = VitalDetailsUpdateForm(request.POST, instance=vitals_data)
            if form.is_valid():
                old_data = vitals_data
                new_vitals_data = FormVitals(
                    pid=old_data.pid,  # Assuming pid is a primary key or unique identifier
                    height=old_data.height,
                # Only update the specified fields
                    weight = form.cleaned_data['weight'] if form.cleaned_data['weight'] else old_data.weight,
                    heart_rate = form.cleaned_data['heart_rate'] if form.cleaned_data['heart_rate'] else old_data.heart_rate,
                    temperature = form.cleaned_data['temperature'] if form.cleaned_data['temperature'] else old_data.temperature,
                    respiration_rate = form.cleaned_data['respiration_rate'] if form.cleaned_data['respiration_rate'] else old_data.respiration_rate,
            )
            
            new_vitals_data.BMI = calculate_bmi(new_vitals_data.weight,new_vitals_data.height) if form.cleaned_data['weight'] else old_data.BMI
            new_vitals_data.BMI_status = calculate_bmi_status(new_vitals_data.BMI)
            new_vitals_data.save()

            messages.success(request, 'Your data has been updated successfully.')
            return redirect('main_page:view_vital_info')  # Redirect to home after success

        else:
                    form = VitalDetailsUpdateForm(instance=vitals_data)  # Populate the form with existing data

        return render(request, 'main_page/update_form_vitals.html', {'form': form})

#update patient data
@login_required
def update_patient_data(request):
    patient_data = PatientData.objects.filter(user=request.user).first()
    
    if patient_data is None:
        messages.info(request, 'No patient data found. Please add your information.')
        return redirect('main_page:enter_patient_data')

    if request.method == 'POST':
        form = PatientDataUpdateForm(request.POST, instance=patient_data)
        if form.is_valid():
            if form.is_valid():
                form.save()  # Save the updated data directly
                messages.success(request, 'Your patient data has been updated successfully.')
            return redirect('main_page:home')
    else:
        form = PatientDataUpdateForm(instance=patient_data)  # Populate the form with existing data
    return render(request, 'main_page/update_patient_data.html', {'form': form})

@login_required
def enter_patient_data(request):
    if request.method == 'POST':
        form = PatientDataForm(request.POST)
        if form.is_valid():
            patient_data = form.save(commit=False)
            patient_data.user = request.user
            patient_data.save()
            messages.success(request, 'Patient data added successfully.')
            return redirect('main_page:enter_form_vitals')
    else:
        form = PatientDataForm()
    
    return render(request, 'main_page/enter_patient_data.html', {'form': form})

@login_required
def enter_form_vitals(request):
    patient_data = PatientData.objects.filter(user=request.user).first()
    vitals_data = FormVitals.objects.filter(pid=patient_data).first()

    if request.method == 'POST':
        form = VitalDetailsForm(request.POST, instance=vitals_data)
        if form.is_valid():
            vitals_instance = form.save(commit=False)
            vitals_instance.pid = patient_data  # Assign the patient data
            vitals_instance.save()
            messages.success(request, 'Vital details updated successfully.')
            return redirect('main_page:home')
    else:
        form = VitalDetailsForm(instance=patient_data)

    return render(request, 'main_page/enter_form_vitals.html', {'form': form})


@login_required
def view_prediction_data(request):
    # Get the first patient data for the logged-in user
    patient_data = PatientData.objects.filter(user=request.user).first()

    # If no patient data is found, show a warning
    if not patient_data:
        messages.warning(request, "No patient data found.")
        return render(request, 'main_page/view_prediction_data.html', {
            'latest_results': [],
        })

    # Get all prediction data for the patient
    prediction_data = PredictionData.objects.filter(pid=patient_data)

    # If no prediction data is found, show a warning
    if not prediction_data.exists():
        messages.warning(request, "No prediction results found.")
        return render(request, 'main_page/view_prediction_data.html', {
            'latest_results': [],
        })

@login_required
def view_prediction_data(request):
    # Get the first patient data for the logged-in user
    patient_data = PatientData.objects.filter(user=request.user).first()

    if not patient_data:
        messages.warning(request, "No patient data found.")
        return render(request, 'main_page/view_prediction_data.html', {
            'latest_results': [],
        })

    # Get all prediction data for the patient
    prediction_data = PredictionData.objects.filter(pid=patient_data)

    if not prediction_data.exists():
        messages.warning(request, "No prediction results found.")
        return render(request, 'main_page/view_prediction_data.html', {
            'latest_results': [],
        })

    # Group DQScore data by timestamp to the second
    dq_scores = DQScore.objects.filter(pid=patient_data).annotate(
        timestamp_rounded=TruncSecond('timestamp')
    ).values('timestamp_rounded', 'prediction_type', 'missing_features_count', 'total_features_count')

    # Combine prediction data with DQ scores based on matching timestamp and prediction type
    combined_data = (
        prediction_data
        .annotate(timestamp_rounded=TruncSecond('timestamp'))
        .values('prediction_type', 'prediction', 'diagnosis', 'timestamp_rounded', 'pid', 'timestamp')
    )

    results = []

    for prediction in combined_data:
        # Get corresponding DQScore for the current prediction
        dq_score = dq_scores.filter(
            prediction_type=prediction['prediction_type'],
            timestamp_rounded=prediction['timestamp_rounded']
        ).order_by('missing_features_count').first()

        if dq_score:
            results.append({
                'prediction_type': prediction['prediction_type'],
                'prediction': prediction['prediction'],
                'timestamp': prediction['timestamp'],
                'diagnosis': prediction['diagnosis'],
                'missing_features_count': dq_score['missing_features_count'],
                'total_features_count': dq_score['total_features_count'],
                'predtime': prediction['timestamp_rounded'],
            })

    # Filter results to keep the one with the least missing columns for each prediction type
    final_results = []
    seen_prediction_types = {}

    for result in results:
        pred_type = result['prediction_type']
        if pred_type not in seen_prediction_types or result['missing_features_count'] < seen_prediction_types[pred_type]['missing_features_count']:
            seen_prediction_types[pred_type] = result

    final_results = list(seen_prediction_types.values())

    return render(request, 'main_page/view_prediction_data.html', {
        'latest_results': final_results,
    })

@login_required
def home(request):
    #logger.debug("view_summary function called for user: %s", request.user)

    # Get the first patient data for the logged-in user
    patient_data = PatientData.objects.filter(user=request.user).first()
    #logger.debug("Retrieved patient data: %s", patient_data)

    if not patient_data:
        logger.warning("No patient data found for user: %s", request.user)
        messages.warning(request, "No patient data found.")
        return render(request, 'main_page/home.html', {
            'latest_results': [],
            'patient': None,
        })

    # Get all prediction data for the patient
    prediction_data = PredictionData.objects.filter(pid=patient_data)
    #logger.debug("Retrieved prediction data: %s", prediction_data)

    if not prediction_data.exists():
        #logger.warning("No prediction results found for patient: %s", patient_data)
        messages.warning(request, "No prediction results found.")
        return render(request, 'main_page/home.html', {
            'latest_results': [],
            'patient': patient_data,
        })

    # Group DQScore data by timestamp to the second
    dq_scores = DQScore.objects.filter(pid=patient_data).annotate(
        timestamp_rounded=TruncSecond('timestamp')
    ).values('timestamp_rounded', 'prediction_type', 'missing_features_count', 'total_features_count')

    # Combine prediction data with DQ scores based on matching timestamp and prediction type
    combined_data = (
        prediction_data
        .annotate(timestamp_rounded=TruncSecond('timestamp'))
        .values('prediction_type', 'prediction', 'diagnosis', 'timestamp_rounded', 'pid', 'timestamp')
    )

    # Initialize a dictionary to hold the best (least missing) predictions
    best_predictions = {}

    for prediction in combined_data:
        # Get corresponding DQScore for the current prediction
        dq_score = dq_scores.filter(
            prediction_type=prediction['prediction_type'],
            timestamp_rounded=prediction['timestamp_rounded']
        ).order_by('missing_features_count').first()

        if dq_score:
            # Check if this prediction type has been recorded
            if prediction['prediction_type'] not in best_predictions:
                best_predictions[prediction['prediction_type']] = {
                    'prediction': prediction,
                    'dq_score': dq_score,
                }
            else:
                # Compare and keep the one with fewer missing features
                if dq_score['missing_features_count'] < best_predictions[prediction['prediction_type']]['dq_score']['missing_features_count']:
                    best_predictions[prediction['prediction_type']] = {
                        'prediction': prediction,
                        'dq_score': dq_score,
                    }

    # Initialize results
    results = {
        'count_green': 0,
        'count_yellow': 0,
        'count_red': 0,
        'total_predictions': len(best_predictions),  # Total distinct prediction types
        'health_score':0
    }

    # Calculate health scores based on the best predictions
    for entry in best_predictions.values():
        prediction = entry['prediction']
        dq_score = entry['dq_score']

        if prediction['diagnosis'] is not None:
        # Calculate health scores based on prediction and diagnosis
            count_green = 1 if prediction['prediction'].lower() == 'no' and prediction['diagnosis'].lower() in ['normal', 'none'] else 0
            count_yellow = 1 if prediction['prediction'].lower() == 'no' and prediction['diagnosis'].lower() not in ['normal', 'none'] else 0
            count_red = 1 if prediction['prediction'].lower() == 'yes' and prediction['diagnosis'].lower() not in ['normal', 'none'] else 0
        
        else:
            count_green = 1 if prediction['prediction'].lower() == 'no' else 0
            count_red = 1 if prediction['prediction'].lower() == 'yes' else 0

        # Update aggregated results
        results['count_green'] += count_green
        results['count_yellow'] += count_yellow
        results['count_red'] += count_red
        results['health_score'] = 1* results['count_green'] + 0.5*results['count_yellow'] + 0*results['count_red']

    # Log the results before passing them to the template
    logger.debug("Aggregated results: %s", results)

    # Pass the patient data and aggregated results to the home template
    return render(request, 'main_page/home.html', {
        'latest_results': [results],  # Wrap the results in a list
        'patient': patient_data,
    })
