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


@app.post("/predict")
async def housing_analyze(request: schemas.UserInput):
    model = joblib.load("test_model.pkl")  # Ensure path is correct
    le_district = joblib.load("district_encoder.pkl")

    district_name = request.DistrictName.strip().lower()  # normalize input
    district_encoded = le_district.transform([district_name])[0]

    input_data = pd.DataFrame([{
        "Area": request.Area,
        "BuildingYear": request.BuildingYear,
        "TimeToNearestStation": request.TimeToNearestStation,
        "DistrictEncoded": district_encoded,
        "RenovationEncoded": request.RenovationEncoded
    }])

    prediction = model.predict(input_data)[0]
    async def stream():
        # context = ""
        agent_result = execute(
            predicted_price=prediction,
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
