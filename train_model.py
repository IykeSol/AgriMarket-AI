import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
def train_and_save_model():
    # Load dataset
    df = pd.read_csv('market_data.csv')
    
    # Features and target
    X = df.drop('Price_NGN', axis=1)
    y = df['Price_NGN']
    
    # Define categorical and numerical columns based on generate_data.py output
    categorical_cols = ['Crop_Type', 'Unit_Measure', 'Location', 'Market_Demand']
    numerical_cols = ['Year', 'Month', 'Rainfall_mm', 'Temperature_C', 'Fertilizer_Price_NGN', 'Fuel_Price_NGN', 'USD_NGN_Rate']
    
    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_cols),
            ('cat', OneHotEncoder(drop='first', handle_unknown='ignore'), categorical_cols)
        ])
    
    # Model pipeline
    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42))
    ])
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"Model trained successfully!")
    print(f"R² Score: {r2:.4f}")
    print(f"Mean Absolute Error: {mae:.2f} NGN")
    
    # Generate Plots
    os.makedirs('static/plots', exist_ok=True)
    
    # 1. Actual vs Predicted Plot
    plt.figure(figsize=(10, 6))
    plt.scatter(y_test, y_pred, alpha=0.5, color='blue')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
    plt.xlabel('Actual Price (NGN)')
    plt.ylabel('Predicted Price (NGN)')
    plt.title('Actual vs Predicted Prices')
    plt.tight_layout()
    plt.savefig('static/plots/actual_vs_predicted.png')
    plt.close()
    
    # 2. Residuals Plot
    residuals = y_test - y_pred
    plt.figure(figsize=(10, 6))
    sns.histplot(residuals, kde=True, color='purple')
    plt.xlabel('Residual Error (NGN)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Residuals')
    plt.tight_layout()
    plt.savefig('static/plots/residuals_dist.png')
    plt.close()
    
    # 3. Feature Importance
    try:
        cat_encoder = preprocessor.named_transformers_['cat']
        cat_feature_names = cat_encoder.get_feature_names_out(categorical_cols)
        feature_names = np.concatenate([numerical_cols, cat_feature_names])
        importances = model.named_steps['regressor'].feature_importances_
        
        indices = np.argsort(importances)[::-1][:15]
        top_features = feature_names[indices]
        top_importances = importances[indices]
        
        plt.figure(figsize=(12, 8))
        sns.barplot(x=top_importances, y=top_features, color='teal')
        plt.xlabel('Relative Importance')
        plt.ylabel('Feature')
        plt.title('Top 15 Feature Importances')
        plt.tight_layout()
        plt.savefig('static/plots/feature_importance.png')
        plt.close()
    except Exception as e:
        print(f"Could not generate feature importance plot: {e}")
        
    print("Regression plots generated and saved to static/plots/")
    
    # Save model
    with open('model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("Model saved as model.pkl")

if __name__ == "__main__":
    train_and_save_model()
