import pandas as pd
import joblib

# Load trained model
model = joblib.load("linear_model.pkl")

# Example user input (replace with chatbot-collected values)
user_input = {
    "DistrictName": "shibuya",
    "NearestStation": "shibuya",
    "MinTimeToNearestStation": 8,
    "Area": 45.0,
    "BuildingYear": 2005,
    "Renovation": None,
    "FloorPlan": "2LDK"
}

# Create a single-row DataFrame
df = pd.DataFrame([user_input])

# Feature engineering for prediction
df["BuildingAge"] = 2024 - df["BuildingYear"]
df["Renovated"] = df["Renovation"].notnull().astype(int)
df["NumRooms"] = pd.to_numeric(df["FloorPlan"].str.extract(r'(\d+)')[0], errors='coerce').fillna(1)
df["HasL"] = df["FloorPlan"].str.contains("L").astype(int)
df["HasD"] = df["FloorPlan"].str.contains("D").astype(int)
df["HasK"] = df["FloorPlan"].str.contains("K").astype(int)
df["HasS"] = df["FloorPlan"].str.contains("S").astype(int)
df["Area_x_NumRooms"] = df["Area"] * df["NumRooms"]
df["MinTime_x_Area"] = df["MinTimeToNearestStation"] * df["Area"]
df["BuildingAgeGroup"] = pd.cut(df["BuildingAge"], bins=[0, 10, 20, 30, 50, 100], labels=False)

# Select model features
features = [
    "DistrictName", "NearestStation", "MinTimeToNearestStation", "Area",
    "BuildingAge", "BuildingAgeGroup", "Renovated", "NumRooms",
    "HasL", "HasD", "HasK", "HasS",
    "Area_x_NumRooms", "MinTime_x_Area"
]

X_user = df[features]

# Predict using the model
predicted_price = model.predict(X_user)[0]

# Show result
print(f"Predicted Apartment Price: ¥{predicted_price:,.0f}")
