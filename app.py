import streamlit as st
import requests
from datetime import datetime

# ✅ API KEY FROM STREAMLIT SECRETS
API_KEY = st.secrets["API_KEY"]

st.set_page_config(page_title="WeatherApp", layout="wide")

# ---------------- CSS ----------------
st.markdown("""
<style>
header {visibility: hidden;}
footer {visibility: hidden;}
.block-container { padding-top: 1rem; }

.stApp {
    background: linear-gradient(180deg, #3f4f99, #2a2f5a);
    color: white;
}

/* welcome card */
.welcome-card {
    margin-top: 80px;
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(18px);
    border-radius: 22px;
    padding: 50px;
    text-align: center;
    width: 60%;
    margin-left: auto;
    margin-right: auto;
}

/* main weather card */
.main-card {
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(18px);
    border-radius: 22px;
    padding: 25px;
    display: flex;
    align-items: center;
    gap: 30px;
}

/* icons */
.big-icon {
    width: 120px;
    filter: drop-shadow(0px 4px 12px rgba(255,255,255,0.3));
}

.small-icon {
    width: 48px;
}

/* hourly & daily cards */
.hour-card, .day-card {
    background: rgba(255,255,255,0.10);
    backdrop-filter: blur(14px);
    border-radius: 16px;
    padding: 14px;
    text-align: center;
}
.subtext { color:#dcdcff; }
</style>
""", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def get_forecast(city):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def get_city_suggestions(q):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={q}&limit=5&appid={API_KEY}"
    r = requests.get(url)
    return r.json() if r.status_code == 200 else []

# ---------- ANIMATED ICON SELECTOR ----------
def animated_icon(main):
    main = main.lower()
    if "clear" in main:
        return "https://cdn-icons-png.flaticon.com/512/869/869869.png"
    if "cloud" in main:
        return "https://cdn-icons-png.flaticon.com/512/414/414825.png"
    if "rain" in main or "drizzle" in main:
        return "https://cdn-icons-png.flaticon.com/512/3076/3076129.png"
    if "thunder" in main:
        return "https://cdn-icons-png.flaticon.com/512/1146/1146869.png"
    if "mist" in main or "haze" in main or "fog" in main:
        return "https://cdn-icons-png.flaticon.com/512/1779/1779940.png"
    return "https://cdn-icons-png.flaticon.com/512/869/869869.png"

# ---------------- TOP BAR ----------------
c1, c2 = st.columns([1.5, 4])

with c1:
    st.markdown("## 🌦️ WeatherApp")

with c2:
    typed = st.text_input("", placeholder="Search city...", label_visibility="collapsed")

# ---------------- AUTO SUGGEST ----------------
city = ""
if typed:
    s = get_city_suggestions(typed)
    if s:
        options = [f"{x['name']}, {x.get('state','')}, {x['country']}" for x in s]
        city = st.selectbox("Suggestions", options, label_visibility="collapsed").split(",")[0]
    else:
        city = typed

# ---------------- WELCOME ----------------
if not city:
    st.markdown("""
    <div class="welcome-card">
        <h2>🌤️ Every day is a good day to check the weather</h2>
        <div class="subtext">Search for your city above to get started</div>
    </div>
    """, unsafe_allow_html=True)

# ---------------- MAIN WEATHER ----------------
if city:
    data = get_weather(city)
    forecast = get_forecast(city)

    if not data or data.get("cod") != 200:
        st.error("City not found")
        st.stop()

    main_weather = data["weather"][0]["main"]
    desc = data["weather"][0]["description"].title()
    icon_url = animated_icon(main_weather)

    st.markdown(f"""
    <div class="main-card">
        <img class="big-icon" src="{icon_url}">
        <div>
            <h2>{city.title()}, {data['sys']['country']}</h2>
            <h1>{int(data['main']['temp'])}°C</h1>
            <div class="subtext">{desc}</div>
            <div class="subtext">
                🌬️ {data['wind']['speed']} m/s &nbsp;&nbsp;
                💧 {data['main']['humidity']}% &nbsp;&nbsp;
                ☁️ {data['clouds']['all']}%
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- HOURLY ----------------
    st.markdown("### ⏰ Hourly Forecast")

    hours = forecast["list"][:8]
    h_idx = st.slider("Scroll", 0, len(hours)-1, 0, label_visibility="collapsed")

    h = hours[h_idx]
    h_time = datetime.strptime(h["dt_txt"], "%Y-%m-%d %H:%M:%S").strftime("%I %p")
    h_icon = animated_icon(h["weather"][0]["main"])

    st.markdown(f"""
    <div class="hour-card">
        <h4>{h_time}</h4>
        <img class="small-icon" src="{h_icon}">
        <h3>{int(h['main']['temp'])}°C</h3>
        <div class="subtext">{h['weather'][0]['description'].title()}</div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------- DAILY ----------------
    daily = {}
    for i in forecast["list"]:
        d = i["dt_txt"].split(" ")[0]
        if d not in daily:
            daily[d] = i

    st.markdown("### 📅 4 Day Forecast")

    cols = st.columns(4)
    i = 0
    for d, item in daily.items():
        if i == 4:
            break
        day = datetime.strptime(d, "%Y-%m-%d").strftime("%A")
        d_icon = animated_icon(item["weather"][0]["main"])

        with cols[i]:
            st.markdown(f"""
            <div class="day-card">
                <h5>{day}</h5>
                <img class="small-icon" src="{d_icon}">
                <h4>{int(item['main']['temp'])}°C</h4>
                <div class="subtext">{item['weather'][0]['description'].title()}</div>
            </div>
            """, unsafe_allow_html=True)
        i += 1
