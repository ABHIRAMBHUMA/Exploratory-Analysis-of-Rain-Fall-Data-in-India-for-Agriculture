from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# =====================================
# LOAD MODEL & SCALER
# =====================================
model = pickle.load(open("models/rainfall_model.pkl", "rb"))
scaler = pickle.load(open("models/scaler.pkl", "rb"))

# =====================================
# LOAD DATASET FOR DASHBOARD
# =====================================
data = pd.read_csv("dataset/WeatherAUS.csv")

# Basic preprocessing
data = data.dropna()
data['RainTomorrow'] = data['RainTomorrow'].map({'No': 0, 'Yes': 1})

# =====================================
# HOME PAGE
# =====================================
@app.route('/')
def home():
    return render_template("index.html")


# =====================================
# PREDICTION ROUTE
# =====================================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form values
        features = [
            float(request.form['MinTemp']),
            float(request.form['MaxTemp']),
            float(request.form['Rainfall']),
            float(request.form['Humidity9am']),
            float(request.form['Pressure9am'])
        ]

        # Scale input
        scaled_features = scaler.transform([features])

        # Predict
        prediction = model.predict(scaled_features)[0]
        probability = model.predict_proba(scaled_features)[0][1]

        if prediction == 1:
            return render_template(
                "result_rain.html",
                probability=round(probability * 100, 2)
            )
        else:
            return render_template(
                "result_no_rain.html",
                probability=round((1 - probability) * 100, 2)
            )

    except Exception as e:
        return f"Error: {e}"


# =====================================
# DASHBOARD ROUTE
# =====================================
@app.route('/dashboard')
def dashboard():

    # Create plots folder if not exists
    if not os.path.exists("static/plots"):
        os.makedirs("static/plots")

    # 1️⃣ Rain vs No Rain Distribution
    plt.figure(figsize=(6,4))
    sns.countplot(x='RainTomorrow', data=data)
    plt.title("Rain vs No Rain Distribution")
    plt.savefig("static/plots/rain_distribution.png")
    plt.close()

    # 2️⃣ Correlation Heatmap
    plt.figure(figsize=(8,6))
    sns.heatmap(
        data[['MinTemp','MaxTemp','Rainfall',
              'Humidity9am','Pressure9am','RainTomorrow']].corr(),
        annot=True
    )
    plt.title("Correlation Heatmap")
    plt.savefig("static/plots/heatmap.png")
    plt.close()

    # 3️⃣ Rainfall Distribution
    plt.figure(figsize=(6,4))
    sns.histplot(data['Rainfall'], bins=30)
    plt.title("Rainfall Distribution")
    plt.savefig("static/plots/rainfall_dist.png")
    plt.close()

    # Summary
    total_records = len(data)
    rain_count = int(data['RainTomorrow'].sum())
    no_rain_count = total_records - rain_count

    return render_template(
        "dashboard.html",
        total=total_records,
        rain=rain_count,
        no_rain=no_rain_count
    )


# =====================================
# RUN APP
# =====================================
if __name__ == "__main__":
    app.run(debug=True)
