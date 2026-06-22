# Define categorical and numerical columns
categorical_features = ['Gender']  # Add more categorical features if needed
numerical_features = ['Age', 'Height (cm)', 'Weight (kg)', 'FVC (L)', 'FEV1 (L)', 'FEV1/FVC (%)', 'PEFR (L/min)', 'DLCO (ml/min/mmHg)', 'BMI']

# Create a column transformer that applies OneHotEncoder to categorical data and StandardScaler to numerical data
preprocessor = ColumnTransformer(
    transformers=[
        ('num', StandardScaler(), numerical_features),
        ('cat', OneHotEncoder(), categorical_features)
    ])

# Create a pipeline that includes the preprocessor and a classifier (e.g., logistic regression)
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', LogisticRegression(class_weight='balanced', random_state=42))  # You can also use other classifiers like RandomForest
])

# Split data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train the model
pipeline.fit(X_train, y_train)

# Make predictions
y_pred = pipeline.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.2f}')
print("\nClassification Report:")
print(classification_report(y_test, y_pred))


# Plot confusion matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()
