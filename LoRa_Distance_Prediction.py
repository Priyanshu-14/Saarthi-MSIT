
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor, GradientBoostingClassifier
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.pipeline import Pipeline

# More accurate data manually created
data = pd.DataFrame({
    'RSSI_Vehicle1': [-45, -50, -55, -60, -65, -70, -75, -80, -85, -90,
                      -47, -52, -57, -62, -67, -72, -77, -82, -87, -92,
                      -49, -54, -59, -64, -69, -74, -79, -84, -89, -94],
    'RSSI_Vehicle2': [-46, -51, -56, -61, -66, -71, -76, -81, -86, -91,
                      -48, -53, -58, -63, -68, -73, -78, -83, -88, -93,
                      -50, -55, -60, -65, -70, -75, -80, -85, -90, -95],
    'Speed_Vehicle1': [25, 35, 45, 55, 65, 75, 85, 95, 105, 115,
                       28, 38, 48, 58, 68, 78, 88, 98, 108, 118,
                       30, 40, 50, 60, 70, 80, 90, 100, 110, 120],
    'Speed_Vehicle2': [26, 36, 46, 56, 66, 76, 86, 96, 106, 116,
                       29, 39, 49, 59, 69, 79, 89, 99, 109, 119,
                       31, 41, 51, 61, 71, 81, 91, 101, 111, 121],
    'Environment': ['Urban', 'Urban', 'Urban', 'Urban', 'Urban', 'Urban', 'Urban', 'Urban', 'Urban', 'Urban',
                     'Suburban', 'Suburban', 'Suburban', 'Suburban', 'Suburban', 'Suburban', 'Suburban', 'Suburban', 'Suburban', 'Suburban',
                     'Free Space', 'Free Space', 'Free Space', 'Free Space', 'Free Space', 'Free Space', 'Free Space', 'Free Space', 'Free Space', 'Free Space'],
    'Distance': [30, 40, 50, 60, 70, 80, 90, 100, 110, 120,
                 70, 90, 110, 130, 150, 170, 190, 210, 230, 250,
                 120, 140, 160, 180, 200, 220, 240, 260, 280, 300]
})

# Encode the environment labels
data['Environment'] = data['Environment'].map({'Free Space': 0, 'Urban': 1, 'Suburban': 2})

# Features and targets
X = data[['RSSI_Vehicle1', 'RSSI_Vehicle2', 'Speed_Vehicle1', 'Speed_Vehicle2']]
y_distance = data['Distance']
y_environment = data['Environment']

# Split the data for environment classification
X_train_env, X_test_env, y_train_env, y_test_env = train_test_split(
    X, y_environment, test_size=0.3, random_state=42
)

# Split the data for distance prediction
X_train_dist, X_test_dist, y_train_dist, y_test_dist = train_test_split(
    X, y_distance, test_size=0.3, random_state=42
)

# Feature Engineering: Polynomial features for distance prediction
poly_features = PolynomialFeatures(include_bias=False)
X_poly_train_dist = poly_features.fit_transform(X_train_dist)
X_poly_test_dist = poly_features.transform(X_test_dist)

# Standardize features
scaler_dist = StandardScaler()
X_train_scaled_dist = scaler_dist.fit_transform(X_poly_train_dist)
X_test_scaled_dist = scaler_dist.transform(X_poly_test_dist)

# Environment Classification Pipeline
env_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', GradientBoostingClassifier(n_estimators=100, random_state=42))
])

# Distance Prediction Pipeline
distance_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', GradientBoostingRegressor(n_estimators=100, random_state=42))
])

# Train the environment classification model
env_pipeline.fit(X_train_env, y_train_env)
y_pred_env = env_pipeline.predict(X_test_env)
accuracy = accuracy_score(y_test_env, y_pred_env)
print(f"Accuracy of Environment Inference: {accuracy:.2f}")

# Train the distance prediction model
distance_pipeline.fit(X_train_scaled_dist, y_train_dist)
y_pred_distance = distance_pipeline.predict(X_test_scaled_dist)
mse = mean_squared_error(y_test_dist, y_pred_distance)
print(f"Mean Squared Error of Distance Prediction: {mse:.2f}")

# Function to predict distance and environment with actual comparison
def predict_and_compare(rssi1, rssi2, speed1, speed2, actual_env, actual_distance):
    # Encode the actual environment
    env_code = {'Free Space': 0, 'Urban': 1, 'Suburban': 2}
    env_mapping = {0: 'Free Space', 1: 'Urban', 2: 'Suburban'}
    
    # Predict environment
    env_prob = env_pipeline.predict_proba([[rssi1, rssi2, speed1, speed2]])
    inferred_env_code = np.argmax(env_prob)
    inferred_env = env_mapping[inferred_env_code]
    
    # Predict distance
    input_data = np.array([[rssi1, rssi2, speed1, speed2]])
    input_data_poly = poly_features.transform(input_data)
    input_data_scaled = scaler_dist.transform(input_data_poly)  # Scale the input data
    predicted_distance = distance_pipeline.predict(input_data_scaled)[0]
    
    # Display the results
    print(f"Actual Environment: {actual_env}")
    print(f"Actual Distance: {actual_distance:.2f} meters")
    print(f"Inferred Environment: {inferred_env}")
    print(f"Predicted Distance: {predicted_distance:.2f} meters")

# Example for comparison
rssi1 = -55
rssi2 = -60
speed1 = 80
speed2 = 90
actual_env = 'Urban'  # Use the actual environment for comparison
actual_distance = 150  # Use the actual distance for comparison
predict_and_compare(rssi1, rssi2, speed1, speed2, actual_env, actual_distance)






