import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load dataset
data = pd.read_csv("dataset/WeatherAUS.csv")

print("Dataset Loaded Successfully")
print(data.head())

# Check Null Values
print("Null values:\n", data.isnull().sum())

# Drop missing values
data = data.dropna()

# Convert Target Variable
data['RainTomorrow'] = data['RainTomorrow'].map({'No':0, 'Yes':1})

# Select Important Features
X = data[['MinTemp','MaxTemp','Rainfall','Humidity9am','Pressure9am']]
y = data['RainTomorrow']

# Feature Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Train Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42)

# Model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Accuracy
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# Save Model
pickle.dump(model, open("models/rainfall_model.pkl", "wb"))
pickle.dump(scaler, open("models/scaler.pkl", "wb"))

print("Model Saved Successfully")
