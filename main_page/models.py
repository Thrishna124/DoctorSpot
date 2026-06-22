from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,Group, Permission
from django.core.validators import EmailValidator
from django.contrib.auth.models import User


# Model for Patient Data
class PatientData(models.Model):
    ACTIVITY_LEVEL_CHOICES = [
        ('sedentary', 'Sedentary (little or no exercise)'),
        ('light', 'Lightly active (light exercise 1-3 days/week)'),
        ('moderate', 'Moderately active (moderate exercise 3-5 days/week)'),
        ('active', 'Very active (hard exercise 6-7 days/week)'),
        ('super_active', 'Super active (very hard exercise/physical job)'),
    ]

    pid = models.BigIntegerField(null=True, blank=True, unique=True)  # Patient ID
    fname = models.CharField(max_length=100, blank=True)
    mname = models.CharField(max_length=100, blank=True, null=True)
    lname = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField()
    DOB = models.DateField("Date of Birth")
    sex = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    phone_cell = models.CharField(max_length=20, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country_code = models.CharField(max_length=5, null=True, blank=True)
    pincode = models.CharField(max_length=6, null=True, blank=True)
    date = models.DateField(auto_now_add=True)  # Today's date
    lifestyle = models.CharField(max_length=100, choices=ACTIVITY_LEVEL_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'patient_data'

    def __str__(self):
        return f"Patient {self.pid or 'N/A'} - {self.fname} {self.lname}"

# Model for Vitals
class FormVitals(models.Model):    
    pid = models.ForeignKey(PatientData, to_field='pid', on_delete=models.CASCADE)  # Reference to 'pid' field, not 'id'
    height = models.FloatField(help_text="Height in cm")
    weight = models.FloatField(help_text="Weight in kg")
    heart_rate = models.IntegerField(help_text="Heart rate in bpm",null=True,blank=True)
    temperature = models.FloatField(help_text="Temperature in °C",null=True,blank=True)
    respiration_rate = models.IntegerField(help_text="Respiration rate per minute",null=True,blank=True)
    BMI = models.FloatField(null=True, blank=True)
    BMI_status = models.CharField(max_length=40, null=True, blank=True)
    date = models.DateField(auto_now_add=True)  # Today's date

    class Meta:
        db_table = 'form_vitals'

    def __str__(self):
        return f"Vitals for Patient {self.pid.pid}"  # Patient ID

# Model for Prediction Data
class PredictionData(models.Model):
    # Diabetes
    urea = models.FloatField(null=True, blank=True)
    creatinine = models.IntegerField(null=True, blank=True)
    hba1c = models.FloatField(null=True, blank=True)
    cholesterol = models.IntegerField(null=True, blank=True)
    triglycerides = models.FloatField(null=True, blank=True)
    HDL = models.FloatField(null=True, blank=True)
    LDL = models.FloatField(null=True, blank=True)
    VLDL = models.FloatField(null=True, blank=True)
    
    # Heart
    chestpain = models.CharField(max_length=1, choices=[('0','typical angina'), 
                                                           ('1','atypical angina'),
                                                           ('2','non-anginal pain'),
                                                           ('3','asymptomatic')],
                                  null=True, blank=True)
    restingBP = models.IntegerField(null=True, blank=True)
    fastingbloodsugar = models.CharField(max_length=1, choices=[('0', '<= 120mg/dl'), 
                                                                ('1', '> 120mg/dl')],
                                         null=True, blank=True)
    restingrelectro = models.CharField(max_length=1, choices=[('0','normal'), 
                                                               ('1','ST-T wave abnormality'),
                                                               ('2','probable or definite left ventricular hypertrophy')],
                                        null=True, blank=True)
    maxheartrate = models.IntegerField(null=True, blank=True)
    exerciseangia = models.CharField(max_length=1, choices=[('0','no'),('1','yes')],
                                      null=True, blank=True)
    oldpeak = models.FloatField(null=True, blank=True)
    slope = models.CharField(max_length=1, choices=[('1','upsloping'), ('2','flat'), ('3','downsloping')],
                             null=True, blank=True)
    noofmajorvessels = models.CharField(max_length=1, null=True, blank=True)

    # Liver-specific fields
    total_bilirubin = models.FloatField(null=True, blank=True)
    direct_bilirubin = models.FloatField(null=True, blank=True)
    alkaline_phosphotase_ALP = models.FloatField(null=True, blank=True)
    alamine_aminotransferase_ALT = models.FloatField(null=True, blank=True)
    total_proteins = models.FloatField(null=True, blank=True)
    albumin = models.FloatField(null=True, blank=True)
    albumin_globulin_ratio = models.FloatField(null=True, blank=True)
    aspartate_aminotransferase_AST = models.FloatField(null=True, blank=True)

    # Kidney-specific fields
    bp = models.FloatField(null=True, blank=True)
    sg = models.CharField(max_length=3, choices=[('1','1.005'), ('2','1.010'), ('3','1.015'), 
                                                  ('4','1.020'), ('5','1.025')],
                          null=True, blank=True)
    al = models.CharField(max_length=3, choices=[('0','Normal - 0 mg/dL'), ('1','Trace - 0 to 10 mg/dL'), 
                                                  ('2','Mild - 10 to 30 mg/dL'), ('3','Moderate - 30 to 100 mg/dL'),
                                                  ('4','severe - 100 to 300 mg/dL'), 
                                                  ('5','very severe - Greater than 300 mg/dL')],
                          null=True, blank=True)
    su = models.CharField(max_length=3, choices=[('0','None - 0 mg/dL'), ('1','Trace - 0 to 100 mg/dL'), 
                                                  ('2','Mild - 100 to 250 mg/dL'), ('3','Moderate - 250 to 500 mg/dL'),
                                                  ('4','Severe - 500 to 1000 mg/dL'), 
                                                  ('5','Very severe - Greater than 1000 mg/dL')],
                          null=True, blank=True)
    rbc = models.CharField(max_length=10, choices=[('normal','normal'), ('abnormal','abnormal')],
                           null=True, blank=True)
    pc = models.CharField(max_length=10, choices=[('normal','normal'), ('abnormal','abnormal')],
                          null=True, blank=True)
    pcc = models.CharField(max_length=10, choices=[('present','present'), ('notpresent','not present')],
                           null=True, blank=True)
    ba = models.CharField(max_length=10, choices=[('present','present'), ('notpresent','not present')],
                          null=True, blank=True)
    bgr = models.FloatField(null=True, blank=True)
    bu = models.FloatField(null=True, blank=True)
    sc = models.FloatField(null=True, blank=True)
    sod = models.FloatField(null=True, blank=True)
    pot = models.FloatField(null=True, blank=True)
    hemo = models.FloatField(null=True, blank=True)
    pcv = models.FloatField(null=True, blank=True)
    wc = models.FloatField(null=True, blank=True)
    rc = models.FloatField(null=True, blank=True)
    htn = models.CharField(max_length=4, choices=[('no','no'),('yes','yes')], null=True, blank=True)
    dm = models.CharField(max_length=4, choices=[('no','no'),('yes','yes')], null=True, blank=True)
    cad = models.CharField(max_length=4, choices=[('no','no'),('yes','yes')], null=True, blank=True)
    appet = models.CharField(max_length=4, choices=[('good','good'),('poor','poor')], null=True, blank=True)
    pe = models.CharField(max_length=4, choices=[('no','no'),('yes','yes')], null=True, blank=True)
    ane = models.CharField(max_length=4, choices=[('no','no'),('yes','yes')], null=True, blank=True)

    #lungs specific fields

    predicted_FEV1 = models.FloatField(null=True, blank=True)
    predicted_VC = models.FloatField(null=True, blank=True)
    actual_FEV1 = models.FloatField(null=True, blank=True)
    actual_VC = models.FloatField(null=True, blank=True)
    fev1_vc_ratio = models.FloatField(null=True, blank=True)

    #fitness specific fields
    total_steps = models.IntegerField(null=True, blank=True)
    calories_burned = models.FloatField(null=True, blank=True)
    BMR = models.FloatField(null=True, blank=True)
    daily_calories_needed = models.FloatField(null=True, blank=True)

    #lung cancer fields
    image = models.ImageField(upload_to='lung_cancer/data/uploads/')

    #parkinsons related fields
    #fundamental_frequency_Hz = models.FloatField(null=True, blank=True)
    #jitter_percent = models.FloatField(null=True, blank=True)
    #shimmer_percent = models.FloatField(null=True, blank=True)
    #HNR = models.FloatField(null=True, blank=True)
    #RPDE = models.FloatField(null=True, blank=True)
    #DFA = models.FloatField(null=True, blank=True)
    #PPE = models.FloatField(null=True, blank=True)

    #common fields
    pid = models.ForeignKey(PatientData, to_field='pid', on_delete=models.CASCADE)  # Reference to 'pid' field, not 'id'
    PREDICTION_CHOICES = [
        ('pancreas', 'pancreas'),
        ('heart', 'Heart'),
        ('liver', 'Liver'),
        ('kidney','Kidney'),
        ('lungs','lungs'),
        ('fitness','fitness'),
        ('lung_cancer','lung_cancer'),
    ]

    prediction = models.CharField(max_length=50, blank=True, null=True)  # Generalized result to handle different formats
    diagnosis = models.CharField(max_length=200, blank=True, null=True)  #
    timestamp = models.DateTimeField(auto_now_add=True)
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_CHOICES)

    class Meta:
        db_table = 'prediction_data'

    def __str__(self):
        return f"Prediction Data for Patient {self.pid.pid if self.pid else 'N/A'}"

# Model for Prediction Data
class DQScore(models.Model):
    pid = models.ForeignKey(PatientData, to_field='pid', on_delete=models.CASCADE)  # Reference to 'pid' field, not 'id'
    PREDICTION_CHOICES = [
        ('pancreas', 'pancreas'),
        ('heart', 'Heart'),
        ('liver', 'liver'),
        ('kidney','kidney'),
        ('lungs','lungs'),
        ('fitness','fitness'),
        ('lung_cancer','lung_cancer'),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)
    prediction_type = models.CharField(max_length=50, choices=PREDICTION_CHOICES)
    total_features_count = models.IntegerField(null=True, blank=True)
    missing_features_count = models.IntegerField(null=True, blank=True)
    missing_features = models.CharField(max_length=255,null=True, blank=True)
    data_quality_value = models.FloatField(null=True, blank=True)


    class Meta:
        db_table = 'DQ_score'

    def __str__(self):
        return f"DQ value of  {self.pid.pid if self.pid else 'N/A'}"
