import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LinearRegression

# Load dataset
df = pd.read_csv("japan_real_estate.csv")

# Filter only 2019 records
df = df[df['Year'].isin([2018, 2019])]

# Drop rows with missing essential values
df.dropna(subset=["MinTimeToNearestStation", "Area", "BuildingYear", "TradePrice", "FloorPlan"], inplace=True)
df = df.reset_index(drop=True)

# ========================
# Feature Engineering
# ========================

# Building year to age
df["BuildingYear"] = pd.to_numeric(df["BuildingYear"].astype(str).str.extract(r'(\d{4})')[0], errors='coerce')
df["BuildingAge"] = 2024 - df["BuildingYear"]
df["BuildingAge"].fillna(df["BuildingAge"].median(), inplace=True)

# Normalize text
df['DistrictName'] = df['DistrictName'].str.lower()

# Ensure numeric values
df['MinTimeToNearestStation'] = pd.to_numeric(df['MinTimeToNearestStation'], errors='coerce')

# Create Renovated flag
df["Renovated"] = df["Renovation"].notnull().astype(int)

df["NumRooms"] = pd.to_numeric(df["FloorPlan"].str.extract(r'(\d+)')[0], errors='coerce')
df["NumRooms"].fillna(df["NumRooms"].median(), inplace=True)

df["HasL"] = df["FloorPlan"].str.contains("L").astype(int)
df["HasD"] = df["FloorPlan"].str.contains("D").astype(int)
df["HasK"] = df["FloorPlan"].str.contains("K").astype(int)
df["HasS"] = df["FloorPlan"].str.contains("S").astype(int)

# Remove outliers based on TradePrice
q1 = df["TradePrice"].quantile(0.01)
q99 = df["TradePrice"].quantile(0.99)
df = df[(df["TradePrice"] >= q1) & (df["TradePrice"] <= q99)]
df = df.reset_index(drop=True)

# Create interaction features
df["Area_x_NumRooms"] = df["Area"] * df["NumRooms"]
df["MinTime_x_Area"] = df["MinTimeToNearestStation"] * df["Area"]

# Create building age group
df["BuildingAgeGroup"] = pd.cut(df["BuildingAge"], bins=[0, 10, 20, 30, 50, 100], labels=False)



# ========================
# Feature Selection
# ========================

features = [
    "DistrictName", "NearestStation", "MinTimeToNearestStation", "Area",
    "BuildingAge", "BuildingAgeGroup", "Renovated", "NumRooms", "HasL", "HasD", "HasK", "HasS",
    "Area_x_NumRooms", "MinTime_x_Area"
]

X = df[features]
y = df["TradePrice"]

# ========================
# Preprocessing
# ========================

categorical_features = ["DistrictName", "NearestStation", "BuildingAgeGroup"]
numerical_features = [
    "MinTimeToNearestStation", "Area", "BuildingAge", "NumRooms",
    "HasL", "HasD", "HasK", "HasS", "Renovated",
    "Area_x_NumRooms", "MinTime_x_Area"
]

categorical_transformer = OneHotEncoder(handle_unknown="ignore")
numerical_transformer = StandardScaler()

preprocessor = ColumnTransformer([
    ("cat", categorical_transformer, categorical_features),
    ("num", numerical_transformer, numerical_features)
])

# ========================
# Train/Test Split
# ========================

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ========================
# Pipeline and Model
# ========================

pipeline = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", LinearRegression())
])

pipeline.fit(X_train, y_train)

# ========================
# Evaluation
# ========================

y_pred = pipeline.predict(X_test)

print("Linear Regression Results:")
print("R² Score       :", r2_score(y_test, y_pred))
print("MAE            :", mean_absolute_error(y_test, y_pred))
print("RMSE           :", np.sqrt(mean_squared_error(y_test, y_pred)))

# ========================
# Save the Model
# ========================

joblib.dump(pipeline, "linear_model.pkl")

