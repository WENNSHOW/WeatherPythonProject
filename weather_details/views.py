# Importing Third Party Packages
from django.shortcuts import render
from geopy.geocoders import Nominatim

# Importing Python Modules
import datetime
import requests as rq

# API End Points для бесплатного тарифа OpenWeatherMap
API_END_PT_CURRENT = "https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}&units=metric"
API_END_PT_FORECAST = "https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}&units=metric"

# Open Weather Maps API KEY
API_KEY = "${key}"

# Open Weather Maps Image URL (принимает код иконки)
IMAGE_URL = "http://openweathermap.org/img/wn/{}@2x.png"

# Locator (Преобразует название локации в координаты)
locator = Nominatim(user_agent="weatherManGeoCoder")

# Home Page Rendering
def home(request):
    return render(request, 'core/home.html', {"page": "Home"})

# About Page Rendering
def about(request):
    return render(request, 'core/about.html', {"page": "About"})

# Error Page Rendering
def error(request, data):
    if data == "Location":
        error_data = "Похоже, вы ввели неверное название локации."
    elif data == "Server":
        error_data = "Сервер не отвечает. Попробуйте позже."
    return render(request, 'core/error.html', {"page": "Error", "cause": data, "error": error_data})

# Weather Details Page Rendering
def details(request):
    # Получаем название локации из GET-параметра
    location = request.GET.get('search_input', '').strip()
    if not location:
        return error(request, "Location")
    
    # Получаем координаты локации
    location_details = locator.geocode(location)
    if location_details is None:
        return error(request, "Location")
    latitude = location_details.latitude
    longitude = location_details.longitude
    
    # Получаем текущие данные о погоде
    try:
        url_current = API_END_PT_CURRENT.format(latitude, longitude, API_KEY)
        response_current = rq.get(url=url_current)
        if response_current.status_code != 200:
            print(f"Error fetching current weather data: {response_current.status_code}, {response_current.text}")
            return error(request, "Server")
        data_current = response_current.json()
    except Exception as e:
        print(f"Exception during current weather API call: {e}")
        return error(request, "Server")
    
    try:
        curr_temp = data_current["main"]["temp"]
        curr_humidity = data_current["main"]["humidity"]
        curr_status = data_current["weather"][0]["main"]
        curr_icon = IMAGE_URL.format(data_current["weather"][0]["icon"])
        curr_precipitation = data_current.get("rain", {}).get("1h", 0)
    except KeyError as e:
        print(f"Missing key in current weather data: {e}")
        return error(request, "Server")
    
    # Получаем прогноз (5 дней с интервалом 3 часа)
    try:
        url_forecast = API_END_PT_FORECAST.format(latitude, longitude, API_KEY)
        response_forecast = rq.get(url=url_forecast)
        if response_forecast.status_code != 200:
            print(f"Error fetching forecast data: {response_forecast.status_code}, {response_forecast.text}")
            return error(request, "Server")
        data_forecast = response_forecast.json()
    except Exception as e:
        print(f"Exception during forecast API call: {e}")
        return error(request, "Server")
    
    # Группируем данные прогноза по датам (формат: YYYY-MM-DD)
    forecast_by_date = {}
    for entry in data_forecast.get("list", []):
        dt_txt = entry["dt_txt"]  # Пример: "2025-03-05 12:00:00"
        date_str = dt_txt.split()[0]  # Берём только дату
        forecast_by_date.setdefault(date_str, []).append(entry)
    
    # Определяем прогноз на следующие 3 дня (исключаем сегодняшнюю дату)
    today_str = datetime.date.today().isoformat()
    sorted_dates = sorted(forecast_by_date.keys())
    future_dates = [d for d in sorted_dates if d > today_str][:3]
    
    forecast_data = []
    for date in future_dates:
        day_entries = forecast_by_date[date]
        max_temp = max(entry["main"]["temp_max"] for entry in day_entries)
        min_temp = min(entry["main"]["temp_min"] for entry in day_entries)
        avg_humidity = sum(entry["main"]["humidity"] for entry in day_entries) / len(day_entries)
        total_rain = sum(entry.get("rain", {}).get("3h", 0) for entry in day_entries)
        # Выбираем иконку из записи, расположенной в середине списка
        icon = IMAGE_URL.format(day_entries[len(day_entries)//2]["weather"][0]["icon"])
        forecast_data.append((max_temp, min_temp, avg_humidity, total_rain, icon))
    
    # Форматируем даты прогноза в формат dd/mm
    forecast_dates = []
    for date in future_dates:
        date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        forecast_dates.append(date_obj.strftime("%d/%m"))
    
    forecast = list(zip(forecast_data, forecast_dates))
    
    # Готовим данные для графиков (используем прогноз на следующие 3 дня)
    days = forecast_dates
    temp_high = [item[0] for item in forecast_data]
    temp_low = [item[1] for item in forecast_data]
    precipitation = [item[3] for item in forecast_data]
    humidity = [item[2] for item in forecast_data]
    
    return render(request, 'weather/weatherdetail.html', {
        "curr_temp": curr_temp,
        "curr_precipitation": curr_precipitation,
        "curr_humidity": curr_humidity,
        "forecast": forecast,
        "page": "Detail", 
        "location": location,
        "curr_icon": curr_icon, 
        "curr_status": curr_status,
        # Передаём данные для графиков
        "days": days,
        "temp_high": temp_high,
        "temp_low": temp_low,
        "precipitation": precipitation,
        "humidity": humidity
    })
