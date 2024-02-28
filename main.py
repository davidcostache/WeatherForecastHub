import requests
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application and the SQLAlchemy ORM.
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Define the Weather model with all required fields.
class Weather(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(50), nullable=False)
    max_temperature = db.Column(db.Float, nullable=True)
    min_temperature = db.Column(db.Float, nullable=True)
    precipitation = db.Column(db.Float, nullable=True)
    sunrise = db.Column(db.String(50), nullable=True)
    sunset = db.Column(db.String(50), nullable=True)
    temperature = db.Column(db.Float, nullable=False)
    condition = db.Column(db.String(50), nullable=False)


# Create the database tables.
with app.app_context():
    db.create_all()


# Define the route for the home page.
@app.route('/', methods=['GET', 'POST'])
def index():
    error_message = None
    if request.method == 'POST':
        city_name = request.form['city']
        weather_data = get_weather_data(city_name)
        if weather_data:
            save_weather_data(city_name, weather_data)
        else:
            error_message = "City not found. Please try again."
    weather_records = Weather.query.all()
    return render_template('index.html', weather_records=weather_records, error_message=error_message)


# Function to get weather data from the API.
def get_weather_data(city_name):
    api_key = '4b60f0e86372476aa0e134143242802'
    url = f"http://api.weatherapi.com/v1/forecast.json?key={api_key}&q={city_name}&days=3"
    response = requests.get(url)
    data = response.json()
    if 'error' in data:
        return None
    return data


# Function to save or update weather data in the database.
def save_weather_data(city_name, weather_data):
    for forecast in weather_data['forecast']['forecastday']:
        record = Weather.query.filter_by(city=city_name, date=forecast['date']).first()
        if record:
            update_record(record, forecast)
        else:
            create_new_record(city_name, forecast)
    db.session.commit()


# Helper function to update an existing weather record.
def update_record(record, forecast):
    record.max_temperature = forecast['day']['maxtemp_c']
    record.min_temperature = forecast['day']['mintemp_c']
    record.precipitation = forecast['day']['totalprecip_mm']
    record.sunrise = forecast['astro']['sunrise']
    record.sunset = forecast['astro']['sunset']
    record.temperature = forecast['day']['avgtemp_c']
    record.condition = forecast['day']['condition']['text']


# Helper function to create a new weather record.
def create_new_record(city_name, forecast):
    new_record = Weather(
        city=city_name,
        date=forecast['date'],
        max_temperature=forecast['day']['maxtemp_c'],
        min_temperature=forecast['day']['mintemp_c'],
        precipitation=forecast['day']['totalprecip_mm'],
        sunrise=forecast['astro']['sunrise'],
        sunset=forecast['astro']['sunset'],
        temperature=forecast['day']['avgtemp_c'],
        condition=forecast['day']['condition']['text']
    )
    db.session.add(new_record)


# Run the Flask application in debug mode.
if __name__ == '__main__':
    app.run(debug=True)
