# AI-Powered Healthcare Analytics Platform

### DoctorSpot

A full-stack healthcare analytics platform that integrates machine learning models for disease prediction and patient health monitoring.

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue?logo=mysql)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.16-orange?logo=tensorflow)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Supported Disease Prediction Models](#-supported-disease-prediction-models)
- [Application Screenshots](#-application-screenshots)
- [Installation](#-installation)
- [Project Structure](#-project-structure)
- [System Architecture](#-system-architecture)
- [Project Highlights](#-project-highlights)
- [Project Statistics](#-project-statistics)
- [Future Enhancements](#future-enhancements)

## Overview

DoctorSpot is an AI-powered healthcare analytics platform developed using Django, Python, MySQL, and Machine Learning. The application enables secure patient management, clinical data collection, health monitoring, and disease risk prediction through multiple trained machine learning models.

The platform provides healthcare professionals and users with an integrated dashboard for managing patient information, recording vital signs, generating predictive insights, and tracking historical health records, making it a comprehensive clinical decision-support solution.

  
## ✨ Features

### 👤 User Management
- Secure registration and login
- Session-based authentication
- Profile management

### 🩺 Patient Health Management
- Patient demographic records
- Vital signs tracking
- Automatic BMI calculation
- Health history management

### 🤖 AI Disease Prediction
- Heart Disease
- Diabetes
- Kidney Disease
- Liver Disease
- Lung Disease
- Lung Cancer
- Fitness Assessment

### 📊 Analytics
- Health score generation
- Prediction history
- Data quality scoring

## 🛠 Technology Stack

### Backend
- Python
- Django 5

### Machine Learning
- TensorFlow
- Keras
- Scikit-learn
- Pandas
- NumPy

### Database
- MySQL

### Frontend
- HTML5
- CSS3
- Bootstrap
- JavaScript

### Tools
- Git
- GitHub

## 🤖 Supported Disease Prediction Models

- Heart Disease Prediction
- Diabetes Prediction
- Kidney Disease Prediction
- Liver Disease Prediction
- Lung Disease Prediction
- Lung Cancer Prediction
- Fitness Assessment

## 📸 Application Screenshots

| Login | Dashboard |
|--------|-----------|
| ![](screenshots/Login.png) | ![](screenshots/Dashboard.png) |

| Prediction History |
|--------------------|
| ![](screenshots/Prediction_history.png) |

## 🚀 Installation

```bash
git clone https://github.com/Thrishna124/DoctorSpot.git

cd DoctorSpot/docspot

python -m venv .venv

source .venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

## 📂 Project Structure

```
DoctorSpot
│
├── docspot/                # Django project configuration
├── main_page/              # Authentication and patient management
├── heart/                  # Heart disease prediction
├── kidney/                 # Kidney disease prediction
├── liver/                  # Liver disease prediction
├── lungs/                  # Lung disease prediction
├── lung_cancer/            # Lung cancer prediction
├── pancreas/               # Diabetes prediction
├── fitness/                # Fitness assessment
├── media/
├── screenshots/
└── requirements.txt
```

## 🏗 System Architecture

![](docs/architecture.png)


## 🌟 Project Highlights

- Built a modular Django application with separate apps for each disease prediction model.
- Integrated multiple TensorFlow and Scikit-learn models for AI-assisted healthcare predictions.
- Designed a normalized MySQL database for secure patient record management.
- Implemented authentication, authorization, and session management using Django Authentication.
- Developed an intelligent health scoring system based on disease prediction outcomes.
- Created a scalable backend architecture that supports the addition of future prediction modules.

  ## 📈 Project Statistics

| Metric | Value |
|---------|------|
| Framework | Django 5.1 |
| Programming Language | Python |
| Database | MySQL |
| Machine Learning Models | 7 |
| Authentication | Django Authentication |
| Prediction History | ✔ |
| Health Dashboard | ✔ |
| BMI Calculation | ✔ |
| Patient Management | ✔ |


## 🚀 Future Enhancements

- Develop REST APIs using Django REST Framework
- Integrate Swagger/OpenAPI documentation
- Containerize the application using Docker and Docker Compose
- Deploy to Google Cloud Platform or Render
- Implement JWT Authentication
- Add Redis caching
- Introduce Celery for background processing
- Configure CI/CD using GitHub Actions


## 👨‍💻 Author

**Thrishna Balakrishnan**

- GitHub: https://github.com/Thrishna124
- LinkedIn: https://www.linkedin.com/in/thrishna-balakrishnan
  

  ## 📄 License

This project is licensed under the MIT License.

  ## 📌 Repository

⭐ If you found this project interesting, feel free to star the repository.
