## Geo Weather Dashboard


A multi-tab weather data dashboard using Dash and WeatherAPI.


## 🌐 API Setup

1. Copy the `.env.example` file:
   ```bash
   mv .env.example .env
    ````

2. Open `.env` and replace with your API key and URLs:

   ```env
   API_KEY=your_api_key_here
   BASE_URL_CURRENT=http://api.weatherapi.com/v1/current.json
   BASE_URL_FORECAST=http://api.weatherapi.com/v1/forecast.json
   ```

---

## ⚙️ Installation

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/weather-dashboard.git
cd weather-dashboard
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate       # On Linux/macOS
# OR
venv\Scripts\activate          # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

---

## 📁 File Structure

---

## ✅ Features

* World, continent, country, region, and city-level weather views
* Progress indicators
* Live data from WeatherAPI

