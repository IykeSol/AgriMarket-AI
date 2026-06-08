import pandas as pd
import numpy as np

np.random.seed(42)

def generate_historical_data():
    records = []
    
    # Historical Baselines - 50kg bag of Rice equivalent (source: NBS + market surveys)
    # Based on actual market prices, NOT NBS averages which skew high (imported rice)
    baselines = {
        2020: {'usd': 380,  'fuel': 160,  'fert': 8000,  'Rice': 18000,  'Tomato': 5000,  'Maize': 9000,  'Yam': 3500,  'Groundnut Oil': 8000},
        2021: {'usd': 450,  'fuel': 165,  'fert': 10000, 'Rice': 22000,  'Tomato': 7000,  'Maize': 11000, 'Yam': 4500,  'Groundnut Oil': 10000},
        2022: {'usd': 600,  'fuel': 195,  'fert': 15000, 'Rice': 28000,  'Tomato': 11000, 'Maize': 16000, 'Yam': 6000,  'Groundnut Oil': 15000},
        2023: {'usd': 850,  'fuel': 600,  'fert': 22000, 'Rice': 42000,  'Tomato': 18000, 'Maize': 25000, 'Yam': 11000, 'Groundnut Oil': 23000},
        2024: {'usd': 1500, 'fuel': 850,  'fert': 35000, 'Rice': 58000,  'Tomato': 30000, 'Maize': 38000, 'Yam': 18000, 'Groundnut Oil': 40000},
        2025: {'usd': 1600, 'fuel': 1200, 'fert': 45000, 'Rice': 68000,  'Tomato': 45000, 'Maize': 50000, 'Yam': 25000, 'Groundnut Oil': 58000},
        2026: {'usd': 1380, 'fuel': 1500, 'fert': 50000, 'Rice': 60000,  'Tomato': 55000, 'Maize': 58000, 'Yam': 30000, 'Groundnut Oil': 68000},
    }
    
    # Producer states sell cheaper (farm gate) vs consumer cities
    # Applied as a multiplier on the base price
    location_price_factor = {
        # South East - producer states
        'Abakaliki': 0.65, 'Owerri': 0.75, 'Aba': 0.80, 'Enugu': 0.82, 'Onitsha': 0.85,
        # South South
        'Port Harcourt': 0.95, 'Calabar': 0.88, 'Uyo': 0.88, 'Asaba': 0.85, 'Warri': 0.90,
        # South West - major consumer markets
        'Lagos': 1.10, 'Ibadan': 0.95, 'Abeokuta': 0.92, 'Akure': 0.90,
        # North West - Kebbi is major producer
        'Kano': 0.90, 'Kaduna': 0.88, 'Birnin Kebbi': 0.60, 'Sokoto': 0.75, 'Zaria': 0.85,
        # North Central - producer belt
        'Abuja': 1.05, 'Minna': 0.78, 'Bida': 0.72, 'Makurdi': 0.80, 'Lafia': 0.78,
        # North East
        'Jos': 0.85, 'Maiduguri': 0.88, 'Jalingo': 0.80, 'Gombe': 0.82
    }

    units = {
        'Rice': ['50kg Bag', '25kg Bag'],
        'Groundnut Oil': ['25 Litres', '5 Litres'],
        'Tomato': ['Big Basket', 'Small Basket'],
        'Maize': ['50kg Bag'],
        'Yam': ['100 Tubers', 'Single Tuber']
    }

    locations = [
        # South East (major rice hubs)
        'Aba', 'Owerri', 'Onitsha', 'Enugu', 'Abakaliki',  # Ebonyi - famous Abakaliki rice
        # South South
        'Port Harcourt', 'Calabar', 'Uyo', 'Asaba', 'Warri',
        # South West
        'Lagos', 'Ibadan', 'Abeokuta', 'Akure',
        # North West (Kebbi - #1 rice producing state)
        'Kano', 'Kaduna', 'Birnin Kebbi', 'Sokoto', 'Zaria',
        # North Central (Benue, Niger, Nassarawa - major rice belts)
        'Abuja', 'Minna', 'Bida', 'Makurdi', 'Lafia',
        # North East
        'Jos', 'Maiduguri', 'Jalingo', 'Gombe'
    ]

    for year in range(2020, 2027):
        # Determine max month for the year
        max_month = 5 if year == 2026 else 12 # Jan to May 2026 as requested
        
        base_data = baselines[year]
        
        for month in range(1, max_month + 1):
            # Generate multiple samples per month across locations and items
            for _ in range(80): # 80 records per month = ~6000 records total
                item = np.random.choice(list(units.keys()))
                unit = np.random.choice(units[item])
                loc = np.random.choice(locations)
                
                # Base economic indicators with slight monthly noise
                usd_rate = base_data['usd'] * np.random.uniform(0.95, 1.05)
                fuel = base_data['fuel'] * np.random.uniform(0.95, 1.05)
                fert = base_data['fert'] * np.random.uniform(0.9, 1.1)
                demand = np.random.choice(['Low', 'Medium', 'High'], p=[0.2, 0.5, 0.3])
                
                # Weather simulation based on month
                if month in [5, 6, 7, 8, 9]: # Rainy season
                    rain = np.random.uniform(100, 300)
                    temp = np.random.uniform(22, 28)
                elif month in [12, 1, 2]: # Harmattan/Dry
                    rain = np.random.uniform(0, 20)
                    temp = np.random.uniform(20, 35)
                else: # Transitional
                    rain = np.random.uniform(20, 100)
                    temp = np.random.uniform(25, 32)

                # Base Price for the item in this year
                price = base_data[item]
                
                # Unit adjustments
                if unit == '25kg Bag': price *= 0.52
                elif unit == '5 Litres': price *= 0.22
                elif unit == 'Small Basket': price *= 0.35
                elif unit == 'Single Tuber': price *= 0.015

                # Seasonality impacts
                if item == 'Tomato' and month in [5, 6, 7, 8]:
                    price *= 1.4 # Rots easily in rain
                elif item == 'Yam' and month in [9, 10, 11]:
                    price *= 0.7 # Harvest time
                elif item == 'Maize' and month in [8, 9, 10]:
                    price *= 0.8
                
                # Festive Surge (December)
                if month == 12:
                    if item in ['Rice', 'Groundnut Oil', 'Tomato']:
                        price *= 1.45
                    elif item == 'Yam':
                        price *= 1.15

                # Apply location factor (producer states are cheaper)
                loc_factor = location_price_factor.get(loc, 0.90)  # default 0.90 for unknown
                price *= loc_factor

                # Demand multiplier
                if demand == 'High': price *= 1.15
                elif demand == 'Low': price *= 0.85
                
                # Apply realistic noise (10-20% random noise for real-world variance)
                noise = np.random.uniform(0.88, 1.12)
                final_price = price * noise

                records.append({
                    'Year': year,
                    'Month': month,
                    'Crop_Type': item,
                    'Unit_Measure': unit,
                    'Location': loc,
                    'Rainfall_mm': round(rain, 1),
                    'Temperature_C': round(temp, 1),
                    'USD_NGN_Rate': round(usd_rate, 2),
                    'Fuel_Price_NGN': round(fuel, 2),
                    'Fertilizer_Price_NGN': round(fert, 2),
                    'Market_Demand': demand,
                    'Price_NGN': round(final_price, 2)
                })
                
    df = pd.DataFrame(records)
    df.to_csv('market_data.csv', index=False)
    print(f"Historical market_data.csv generated successfully with {len(df)} records (2020-2026).")

if __name__ == "__main__":
    generate_historical_data()
