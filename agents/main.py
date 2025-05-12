from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import schemas
from agent_config import execute, follow_up
import joblib
import pandas as pd

app = FastAPI()

# CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = joblib.load("linear_model.pkl")


@app.post("/predict")
async def housing_analyze(request: schemas.UserInput):

    district_name = request.DistrictName.strip().lower()  # normalize input
    station_name = request.NearestStation.strip().lower()

    user_input = {
    "DistrictName": district_name,
    "NearestStation": station_name,
    "MinTimeToNearestStation": request.MinTimeToNearestStation,
    "Area": request.Area,
    "BuildingYear": request.BuildingYear,
    "Renovation": request.Renovation,
    "FloorPlan": request.FloorPlan
    }

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

    features = [
    "DistrictName", "NearestStation", "MinTimeToNearestStation", "Area",
    "BuildingAge", "BuildingAgeGroup", "Renovated", "NumRooms",
    "HasL", "HasD", "HasK", "HasS",
    "Area_x_NumRooms", "MinTime_x_Area"
    ]

    X_user = df[features]
    predicted_price = model.predict(X_user)[0]
    async def stream():
        # context = ""
        agent_result = execute(
            predicted_price=predicted_price,
            user_provided_price=request.TradePrice
        )
        async for chunk in agent_result:
            yield chunk
    return StreamingResponse(stream(), media_type="text/plain")

@app.post("/conversation")
def conversation(request: schemas.UserQuery):
    async def stream():
        agent_result = follow_up(prompt=request.query)
        async for chunk in agent_result:
            yield chunk
    return StreamingResponse(stream(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
