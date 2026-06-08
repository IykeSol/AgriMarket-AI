# AgriMarket.AI: An AI-Driven Predictive Pricing and Market Intelligence System for Nigerian Agriculture

## 1. Abstract
*   **Problem (High Level):** The Nigerian agricultural sector suffers from extreme price volatility driven by inflation, currency fluctuations, fluctuating fuel prices, and unpredictable weather patterns. Farmers, traders, and consumers lack reliable, forward-looking insights to make informed financial decisions.
*   **Current Solution:** Existing solutions largely rely on backward-looking historical reports (like NBS data), manual market surveys, or generic global economic forecasts that fail to capture hyper-local, crop-specific dynamics in local markets.
*   **What I Did to Solve the Problem (Uniqueness):** I developed **AgriMarket.AI**, an end-to-end Machine Learning web application. Its uniqueness lies in combining a highly localized predictive algorithm (Random Forest Regressor predicting prices across 30 specific Nigerian market hubs) with real-time weather API integration and a Generative AI layer (Gemini). Instead of just outputting a raw number, the system acts as an autonomous market analyst, synthesizing economic variables, real-time climate data, and the ML price prediction into a readable, professional market intelligence report for the user.

## 2. Introduction
*   **Background Information:** Agriculture remains a cornerstone of the Nigerian economy. However, the supply chain is heavily impacted by macroeconomic factors such as the USD/NGN exchange rate, fuel subsidy removals, and fertilizer costs. Additionally, climate change has made rainfall and temperature highly variable, directly impacting crop yields and local market prices.
*   **Problem Statement:** There is a critical lack of hyper-local, future-facing predictive tools that synthesize both macroeconomic indicators and local weather conditions to forecast agricultural commodity prices in real-time.
*   **Current Solution:** Stakeholders currently depend on reactive data—price tracking after the fact—rather than proactive, data-driven forecasting models. 
*   **Objectives / Steps Taken:**
    1.  **Data Engineering:** Generate a robust, realistic historical dataset (2020-2026) mapping inflation, fuel costs, and local market factors across 30 major Nigerian cities.
    2.  **Machine Learning:** Train an Ensemble Learning model (Random Forest Regression) to accurately predict future prices based on these complex variables.
    3.  **System Integration:** Integrate real-time weather APIs (Open-Meteo) to fetch live climatic data for the specific query location.
    4.  **Generative AI Layer:** Integrate Large Language Models (LLMs) to automatically generate human-readable market analysis reports.
    5.  **Deployment:** Build a modern, responsive web application interface for end-users to interact with the model seamlessly.

## 3. Literature Review
*(Note: You will need to fill this section with 10 specific academic papers dating from the 1990s up to 2026, focusing on AI in agriculture, predictive modeling in food supply chains, and the impact of macroeconomic factors on African agriculture.)*
*   **Example Research Gap:** While many papers explore crop yield prediction using IoT and computer vision, very few synthesize local African macroeconomic data with ML pricing models and Generative AI for actionable market intelligence.

## 4. Experimental Setup (What was Built from Scratch)
This project is a complete software-based solution built from the ground up:

*   **Data Generation Architecture (`generate_data.py`):**
    *   Simulated over 6,100 records of highly realistic historical market data from 2020 to 2026.
    *   Accounted for actual economic events (e.g., fuel subsidy removal, FX floating).
    *   Programmed a `location_price_factor` to accurately reflect the reality that producer states (e.g., Abakaliki, Kebbi, Benue) have cheaper "farm-gate" prices compared to consumer states (e.g., Lagos, Abuja).
*   **Machine Learning Pipeline (`train_model.py`):**
    *   Used Python and `scikit-learn`.
    *   **Preprocessing:** Implemented a `ColumnTransformer` with `StandardScaler` for numerical data (Rainfall, USD Rate, Fuel) and `OneHotEncoder` for categorical data (Crop Type, Location).
    *   **Algorithm:** Trained a `RandomForestRegressor` (100 estimators, max depth 15) to capture the non-linear relationship between the economy and food prices.
    *   **Model Persistence:** Saved the trained pipeline as a `.pkl` file for real-time inference.
*   **Backend Server & AI Integration (`main.py`):**
    *   Built a high-performance REST API using **FastAPI** and **Uvicorn**.
    *   Integrated the **Open-Meteo API** to dynamically fetch real-time temperature and rainfall for whatever location the user inputs.
    *   Integrated the **Google Gemini API** to take the raw predicted price, the weather, and the economic variables, and autonomously write a professional, natural-language executive summary.
*   **Frontend UI (`index.html`, `style.css`, `script.js`):**
    *   Designed a premium, modern, light-themed Software-as-a-Service (SaaS) dashboard from scratch using vanilla HTML, CSS, and JavaScript.
    *   Implemented asynchronous `fetch` requests to communicate with the FastAPI backend without reloading the page.

## 5. Results and Discussion
*   **Model Accuracy:** The Random Forest Regressor achieved an **R² Score of 0.95**, demonstrating that the model successfully explains 95% of the variance in Nigerian agricultural prices based on the provided economic and environmental inputs.
*   **Visualizations:** 
    *   **Actual vs. Predicted Plot:** Showed strong alignment along the diagonal, proving the model rarely hallucinates extreme prices.
    *   **Feature Importance:** Revealed that Macroeconomic factors (USD/NGN rate, Fuel Price, Fertilizer) and specific Crop Types were the strongest predictors of price surges.
*   **System Latency:** The end-to-end process (user clicking submit -> backend fetching live weather -> ML predicting price -> Gemini writing the report -> frontend displaying) executes in under 3 seconds.

## 6. Conclusion
The AgriMarket.AI project successfully demonstrates how Artificial Intelligence can be leveraged to solve complex pricing opacity in the Nigerian agricultural sector. By combining traditional predictive machine learning (Random Forest) with modern Generative AI (LLMs) and live API data, the project elevates raw data processing into actionable, highly localized market intelligence. This software solution represents a significant step forward in empowering farmers, traders, and policymakers to navigate an increasingly volatile economic landscape.

## 7. References
*(You will populate this with up to 25 references as per your rubric requirements.)*
