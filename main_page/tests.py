import os
import django
import sys

# Add the project directory to the Python path
sys.path.append('/Users/thrishna/Desktop/Critical_Django_project')

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docspot.settings')

# Initialize Django
django.setup()

# Now you can import models
from django.contrib.auth.models import User

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docspot.settings')

# Initialize Django
django.setup()

# Now you can import Django models
from django.contrib.auth.models import User

# Rest of your code for tests goes here


user = User.objects.get(email='thrish@email.com')
print(user.password)  # This should match the hashed password in the database
# Verify the password
user.check_password('thrish123')  # This should return True