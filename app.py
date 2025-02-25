import streamlit as st
import requests
import sqlite3
import plotly.express as px
from datetime import datetime
import pandas as pd

# 🌟 Set Page Config with Wide Layout
st.set_page_config(page_title="AI-Powered Weather Dashboard", layout="wide", initial_sidebar_state="collapsed")


st.markdown("""
    <style>
        /* Sidebar Background */
        [data-testid="stSidebar"] {
            background-color: #1E3A5F;
        }
        
        /* Sidebar Title and Input Text */
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] label, [data-testid="stSidebar"] span {
            color: white;
            font-size: 20px;
        }

        /* Main Content Background */
        [data-testid="stAppViewContainer"] {
            background-color: #E3F2FD;
            color: #1E3A5F;
        }

        /* Responsive Footer */
        footer {visibility: hidden;}
        .footer {
            position: relative;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: #555;
            padding: 10px;
        }

        /* Mobile Adjustments */
        @media (max-width: 768px) {
            [data-testid="stSidebar"] h1 {
                font-size: 18px;
            }
        }
             @media (max-width: 768px) {
        iframe {
            height: 300px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# ✅ API Configuration
API_KEY = "51007ccfc3f09db4e63de3fa3c2d7fbd"

# ✅ SQLite Database Connection
conn = sqlite3.connect("weather_history.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature REAL,
        humidity TEXT,
        weather TEXT,
        wind_speed TEXT,
        visibility TEXT,
        pressure TEXT,
        sunrise TEXT,
        sunset TEXT,
        timestamp TEXT
    )
""")
conn.commit()
st.header("🌤️ AI-Powered Weather Dashboard "); 
# AI-Based Weather Insights Function
def ai_weather_insights(temp, humidity, wind_speed):
    insights = ""
    if temp > 30:
        insights += "🔥 It's quite hot! Stay hydrated and avoid direct sun exposure. "
    elif temp < 10:
        insights += "❄️ It's cold outside! Dress warmly. "
    else:
        insights += "🌤️ The weather is moderate, great for outdoor activities! "
    
    if float(humidity) > 80:  # Ensure humidity is treated correctly
        insights += "💦 High humidity levels detected. It might feel warmer than it actually is. "
    
    if float(wind_speed) > 10:  # Ensure wind speed is a valid float
        insights += "🌬️ Strong winds detected. Be cautious while traveling. "
    
    return insights

# Travel Recommendations Function
def travel_recommendation(weather):
    recommendations = {
        "Clear": "Great day for a picnic or a walk in the park! ☀️",
        "Clouds": "Mild weather! A good day for outdoor photography or hiking. ☁️",
        "Rain": "Carry an umbrella! 🌧️",
        "Snow": "Perfect weather for a cozy indoor day! ❄️",
        "Thunderstorm": "Better to stay indoors. 🌩️"
    }
    return recommendations.get(weather, "Check weather updates before planning your day! 🏕️")


# ✅ Function to Fetch Current Weather Data
def get_weather(city_name):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    try:
        response.raise_for_status()  # This raises an error if status_code is not 200
        data = response.json()
        return {
            "City": data["name"],
            "Temperature": float(data["main"]["temp"]),
            "Humidity": float(data['main']['humidity']),
            "Weather": data["weather"][0]["description"].title(),
            "Wind Speed": float(data['wind']['speed']),
            "Visibility": f"{data['visibility'] / 1000} km" if 'visibility' in data else "N/A",
            "Pressure": float(data['main']['pressure']),
            "Sunrise": datetime.utcfromtimestamp(data["sys"]["sunrise"]).strftime('%H:%M:%S'),
            "Sunset": datetime.utcfromtimestamp(data["sys"]["sunset"]).strftime('%H:%M:%S'),
            "Country": data["sys"]["country"]
        }
    except requests.exceptions.RequestException as e:
        st.error("⚠️ Error fetching data from the API. Please try again later.")
        st.write(f"Debug Info: {e}")
        return None

# ✅ Function to Fetch 5-Day Weather Forecast
def get_forecast(city_name):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_name}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        forecast_list = []
        for forecast in data['list']:
            forecast_list.append({
                "DateTime": forecast['dt_txt'],
                "Temperature": forecast['main']['temp'],
                "Weather": forecast['weather'][0]['description'].title()
            })
        return forecast_list
    else:
        return None

# ✅ Sidebar - City Search
st.sidebar.title("🌎 Weather Search")
city = st.sidebar.text_input("Enter city name:", placeholder="E.g. Karachi, London, New York")

if st.sidebar.button("🔍 Get Weather"):
    if city:
        weather = get_weather(city)
        forecast = get_forecast(city)
        if weather:
            # Save search history
            c.execute(
                "INSERT INTO history (city, temperature, humidity, weather, wind_speed, visibility, pressure, sunrise, sunset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (weather["City"], weather["Temperature"], weather["Humidity"], weather["Weather"], weather["Wind Speed"],
                 weather["Visibility"], weather["Pressure"], weather["Sunrise"], weather["Sunset"], datetime.now())
            )
            conn.commit()
            
            # ✅ Display Weather Data
            st.markdown(f"## 🌤️ Weather in {weather['City']}, {weather['Country']}")

            # 🔹 Responsive Columns
            col1, col2 = st.columns([1, 1])
            with col1:
                st.write(f"🌡️ **Temperature:** {weather['Temperature']}°C")
                st.write(f"💧 **Humidity:** {weather['Humidity']}%")
                st.write(f"🌬️ **Wind Speed:** {weather['Wind Speed']} m/s")
            with col2:
                st.write(f"🔭 **Visibility:** {weather['Visibility']}")
                st.write(f"📊 **Pressure:** {weather['Pressure']} hPa")
                st.write(f"☁️ **Condition:** {weather['Weather']}")

            st.write(f"🌅 **Sunrise:** {weather['Sunrise']} UTC")
            st.write(f"🌇 **Sunset:** {weather['Sunset']} UTC")
              
            # AI-Based Weather Insights
            insights = ai_weather_insights(weather['Temperature'], weather['Humidity'], weather['Wind Speed'])
            st.info(f"💡 AI Insight: {insights}")
            
            # Travel Recommendations
            travel_suggestion = travel_recommendation(weather['Weather'])
            st.success(f"🏝️ Travel Tip: {travel_suggestion}")
            

            # ✅ Interactive Weather Metrics Chart
            df = pd.DataFrame({
                "Metric": ["Temperature", "Humidity", "Wind Speed", "Pressure"],
                "Value": [weather["Temperature"], weather["Humidity"], weather["Wind Speed"], weather["Pressure"]]
            })
            fig = px.line(df, x="Metric", y="Value", markers=True, title="📈 Weather Metrics Overview",
                          color_discrete_sequence=px.colors.qualitative.Vivid)
            fig.update_traces(line=dict(width=3))
            fig.update_layout(xaxis_title="Metrics", yaxis_title="Value", template="plotly_dark")
            st.plotly_chart(fig)
            
            # ✅ Weather Forecast Display with Expander
            if forecast:
                with st.expander("📅 View 5-Day Weather Forecast"):
                    forecast_df = pd.DataFrame(forecast)
                    fig_forecast = px.line(forecast_df, x="DateTime", y="Temperature", markers=True,
                                           title="📅 Temperature Forecast",
                                           color_discrete_sequence=["#FFA07A"])
                    fig_forecast.update_traces(line=dict(width=3))
                    fig_forecast.update_layout(xaxis_title="DateTime", yaxis_title="Temperature (°C)", template="plotly_dark")
                    st.plotly_chart(fig_forecast)

            # ✅ Weather Map Integration
            st.markdown("### 🌍 Weather Map")

            map_url = f"https://www.google.com/maps?q={city}&output=embed"

            # Responsive iframe with better layout handling
            st.markdown(
                f"""
                <div style="display: flex; justify-content: center;">
                    <iframe src="{map_url}" 
                        style="width: 90%; max-width: 800px; height: 450px; border:0; border-radius: 10px;" 
                        allowfullscreen="" loading="lazy">
                    </iframe>
                </div>
                """, 
                unsafe_allow_html=True
            )

        else:
            st.error("❌ City not found")
            # ✅ Footer
st.markdown("---")
st.markdown("<p class='footer'>Made with ❤️ using Streamlit by Huma Mohsin</p>", unsafe_allow_html=True)
