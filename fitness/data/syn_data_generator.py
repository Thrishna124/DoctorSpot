import pandas as pd
import random

# Function to generate random fitness data
def generate_fitness_data(num_records):
    data = []
    for _ in range(num_records):
        age = random.randint(18, 65)
        gender = random.choice(['Male', 'Female'])
        height = random.randint(150, 190)  # cm
        weight = random.randint(50, 100)    # kg
        activity_level = random.choice(['Sedentary', 'Light', 'Moderate', 'Active', 'Very Active'])
        
        # Calculate total steps based on activity level
        if activity_level == 'Sedentary':
            total_steps = random.randint(1000, 3000)
        elif activity_level == 'Light':
            total_steps = random.randint(3000, 6000)
        elif activity_level == 'Moderate':
            total_steps = random.randint(6000, 9000)
        elif activity_level == 'Active':
            total_steps = random.randint(9000, 12000)
        else:  # Very Active
            total_steps = random.randint(12000, 15000)

        # Estimate calories burned (simple model)
        calories_burned = round(total_steps * 0.05)  # Rough estimate: 0.05 calories per step
        
        # Daily calories needed (basic estimation)
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + (5 if gender == 'Male' else -161)
        daily_calories_needed = round(bmr * (1.2 if activity_level == 'Sedentary' else
                                              1.375 if activity_level == 'Light' else
                                              1.55 if activity_level == 'Moderate' else
                                              1.725 if activity_level == 'Active' else
                                              1.9))

        # Fitness score (randomly generated for simplicity)
        fitness_score = round(random.uniform(0, 100))
        prediction = 'Yes' if fitness_score >= 70 else 'No'

        # Append generated record
        data.append([age, gender, height, weight, activity_level, total_steps,
                      calories_burned, daily_calories_needed, fitness_score, prediction])

    return data

# Generate data
num_records = 1000
fitness_data = generate_fitness_data(num_records)

# Create a DataFrame
columns = ['age', 'sex', 'height', 'weight', 'activity_level',
           'total_steps', 'calories_burned', 'daily_calories_needed',
           'fitness_score', 'prediction']
df = pd.DataFrame(fitness_data, columns=columns)

# Save to CSV
df.to_csv('synthetic_fitness_data.csv', index=False)

print("Synthetic fitness data generated and saved to 'synthetic_fitness_data.csv'")
