import os
import pickle
import pandas as pd
import requests
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Agri Market SaaS Predictor")

# Load model at startup
model = None

@app.on_event("startup")
def load_model():
    global model
    try:
        with open('model.pkl', 'rb') as f:
            model = pickle.load(f)
        print("Model loaded successfully.")
    except FileNotFoundError:
        print("WARNING: model.pkl not found. Run generate_data.py then train_model.py first.")
        model = None

# Set up Gemini
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key and gemini_api_key != "your_gemini_api_key_here":
    client = genai.Client(api_key=gemini_api_key)
else:
    client = None

WEATHER_API_KEY = "a6de1b185e04e9dd876a3c77587f996f"

# Historical average fallback for Nigeria (Rainfall mm, Temp C)
NIGERIA_MONTHLY_AVERAGES = {
    1: (10, 32), 2: (20, 34), 3: (50, 34), 4: (100, 32),
    5: (150, 31), 6: (200, 29), 7: (250, 28), 8: (250, 28),
    9: (200, 29), 10: (100, 30), 11: (20, 32), 12: (10, 32)
}

def get_weather(location: str, target_month: int):
    current_month = datetime.now().month
    
    # If the user is asking for a future/different month, use historical averages
    if target_month != current_month:
        rain, temp = NIGERIA_MONTHLY_AVERAGES.get(target_month, (100, 30))
        return temp, rain, f"Used historical seasonal averages for month {target_month}."

    # Otherwise fetch live weather
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location},ng&appid={WEATHER_API_KEY}&units=metric"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            temp = data['main']['temp']
            # OWM provides rain in the last 1h, we'll scale it roughly to a monthly approximation for the model
            # This is a very rough heuristic to fit the model's expectations (0-300mm)
            rain_1h = data.get('rain', {}).get('1h', 0)
            rain_monthly_proxy = min(300, rain_1h * 24 * 5) # Scale up to monthly proxy
            
            if rain_monthly_proxy == 0:
                # Fallback to seasonal average if currently not raining
                rain_monthly_proxy = NIGERIA_MONTHLY_AVERAGES.get(target_month, (100, 30))[0]
                
            return temp, rain_monthly_proxy, f"Live weather fetched for {location}."
    except Exception as e:
        pass
        
    # Complete fallback
    rain, temp = NIGERIA_MONTHLY_AVERAGES.get(target_month, (100, 30))
    return temp, rain, "Weather API failed, used historical averages."


class PredictionRequest(BaseModel):
    Item: str
    Unit: str
    Location: str
    Year: int = Field(default_factory=lambda: datetime.now().year)
    Month: int = Field(..., ge=1, le=12)
    USD_NGN_Rate: float
    Fuel_Price_NGN: float
    Fertilizer_Price_NGN: float
    Market_Demand: str

@app.post("/predict")
def predict_price(request: PredictionRequest):
    if not model:
        raise HTTPException(status_code=500, detail="Model not found. Please train the model first.")
    
    # Normalize location to title case so 'aba', 'ABA', 'Aba' all match
    request.Location = request.Location.strip().title()
    
    # Get Weather
    temp, rain, weather_source = get_weather(request.Location, request.Month)
    
    # Create DataFrame for prediction
    data = {
        'Crop_Type': [request.Item],
        'Unit_Measure': [request.Unit],
        'Location': [request.Location],
        'Month': [request.Month],
        'Year': [request.Year],
        'Rainfall_mm': [rain],
        'Temperature_C': [temp],
        'Fertilizer_Price_NGN': [request.Fertilizer_Price_NGN],
        'Fuel_Price_NGN': [request.Fuel_Price_NGN],
        'USD_NGN_Rate': [request.USD_NGN_Rate],
        'Market_Demand': [request.Market_Demand]
    }
    df = pd.DataFrame(data)
    
    # Predict
    try:
        predicted_price = model.predict(df)[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    summary = "Summary generation failed or API key not set."
    if client:
        try:
            current_year = datetime.now().year
            prompt = f"""Act as a highly sophisticated AI Market Analyst built into an enterprise SaaS dashboard. The current year is {current_year}.
The user manually ran a prediction with these parameters:
- Crop: {request.Item} ({request.Unit})
- Location: {request.Location} (Temp: {temp:.1f}C, Rain: {rain:.1f}mm)
- Target Year: {request.Year}
- Target Month: {request.Month}
- USD/NGN Rate: ₦{request.USD_NGN_Rate}
- Fuel Price: ₦{request.Fuel_Price_NGN} / L
- Fertilizer Price: ₦{request.Fertilizer_Price_NGN}
- Demand: {request.Market_Demand}

Our ML model predicted the price will be ₦{predicted_price:,.2f}.

Write a concise, highly professional market analysis. Do NOT invent or mention any specific dates, report dates, or document dates. The analysis period is {request.Year}, Month {request.Month}. Do not use emojis. Use a modern, executive tone."""
            
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.7)
            )
            summary = response.text.strip()
        except Exception as e:
            summary = f"Error generating summary: {str(e)}"
            
    return {
        "predicted_price_ngn": round(predicted_price, 2),
        "temperature_c": round(temp, 1),
        "rainfall_mm": round(rain, 1),
        "weather_source": weather_source,
        "analysis_summary": summary
    }

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    if not client:
        raise HTTPException(status_code=500, detail="Gemini API Key missing.")
    if not model:
        raise HTTPException(status_code=500, detail="Model not found.")
        
    current_month = datetime.now().month
    
    # Step 1: Extract parameters from query
    extraction_prompt = f"""Extract the following agricultural market parameters from the user's query.
    Return ONLY a valid JSON object. Do not include markdown formatting or backticks.
    
    Required keys and allowed values:
    - "Item": "Rice", "Groundnut Oil", "Tomato", "Maize", or "Yam"
    - "Unit": "50kg Bag", "25kg Bag", "25 Litres", "5 Litres", "Big Basket", "Small Basket", "100 Tubers", "Single Tuber"
    - "Location": e.g. "Lagos", "Kano", "Abuja" (default "Abuja" if not specified)
    - "Year": integer (default 2026 if not specified)
    - "Month": integer 1-12 (default {current_month} if not specified)
    - "Fuel_Price_NGN": float (default 850 if not specified)
    - "USD_NGN_Rate": float (default 1500 if not specified)
    - "Fertilizer_Price_NGN": float (default 22000 if not specified)
    - "Market_Demand": "Low", "Medium", "High" (default "Medium" if not specified)
    
    User Query: "{request.query}"
    """
    
    try:
        extraction_res = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=extraction_prompt,
            config=types.GenerateContentConfig(temperature=0)
        )
        # Parse JSON
        text = extraction_res.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        params = json.loads(text.strip())
    except Exception as e:
        return {"response": "I couldn't clearly understand the crop and location from your query. Could you please specify them?"}

    # Step 2: Fetch weather and run model
    try:
        temp, rain, w_source = get_weather(params.get("Location", "Abuja"), params.get("Month", current_month))
        
        df = pd.DataFrame({
            'Crop_Type': [params.get('Item', 'Rice')],
            'Unit_Measure': [params.get('Unit', '50kg Bag')],
            'Location': [params.get('Location', 'Abuja')],
            'Month': [params.get('Month', current_month)],
            'Year': [params.get('Year', 2026)],
            'Rainfall_mm': [rain],
            'Temperature_C': [temp],
            'Fertilizer_Price_NGN': [params.get('Fertilizer_Price_NGN', 22000)],
            'Fuel_Price_NGN': [params.get('Fuel_Price_NGN', 850)],
            'USD_NGN_Rate': [params.get('USD_NGN_Rate', 1500)],
            'Market_Demand': [params.get('Market_Demand', 'Medium')]
        })
        
        predicted_price = model.predict(df)[0]
    except Exception as e:
        return {"response": f"Encountered an issue running the prediction model. Make sure to specify a valid item and unit (e.g., Rice 50kg Bag)."}

    # Step 3: Generate Chat Response
    current_year = datetime.now().year
    chat_prompt = f"""Act as a highly sophisticated AI Market Analyst built into an enterprise SaaS dashboard. The current year is {current_year}.
The user asked: "{request.query}"

We extracted these assumptions:
- Crop: {params.get('Item')} ({params.get('Unit')})
- Location: {params.get('Location')} (Temp: {temp:.1f}C, Rain: {rain:.1f}mm)
- USD/NGN Rate: ₦{params.get('USD_NGN_Rate')}
- Fuel Price: ₦{params.get('Fuel_Price_NGN')} / L

Our ML model predicted the price will be ₦{predicted_price:,.2f}.

Write a concise, highly professional response. State the predicted price clearly and explain why it makes sense. Do NOT invent or add any dates, document headers, or report titles. Do not use emojis. Use a modern, executive tone."""

    try:
        chat_res = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=chat_prompt,
            config=types.GenerateContentConfig(temperature=0.7)
        )
        final_answer = chat_res.text.strip()
    except Exception as e:
        final_answer = f"The predicted price is ₦{predicted_price:,.2f}. I couldn't generate a summary due to an API error."

    return {
        "response": final_answer,
        "extracted_params": params,
        "prediction": round(predicted_price, 2)
    }

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse('static/index.html')
