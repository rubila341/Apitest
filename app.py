from flask import Flask, request, jsonify, render_template, send_from_directory
import requests
import folium
import os

app = Flask(__name__)

FSQ_API_KEY = 'fsq3DxoK59F/a06C5DTwalY1GL3YXptg/scffENJZYcQNEM='
MAPS_FOLDER = 'maps'
os.makedirs(MAPS_FOLDER, exist_ok=True)

def get_foursquare_places(location, query):
    url = "https://api.foursquare.com/v3/places/search"
    headers = {'Authorization': FSQ_API_KEY}
    params = {'ll': location, 'query': query, 'limit': 50}
    response = requests.get(url, headers=headers, params=params)
    results = response.json().get('results', [])
    places = [{'name': place['name'],
               'location': place['geocodes']['main'],
               'rating': place.get('rating', 'Нет рейтинга')}
              for place in results]
    return places

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_route', methods=['POST'])
def get_route():
    data = request.json
    location = data.get('location')
    interests = data.get('interests')

    all_places = []
    for interest in interests:
        places = get_foursquare_places(location, interest)
        all_places.extend(places)

    lat, lng = map(float, location.split(','))
    m = folium.Map(location=[lat, lng], zoom_start=13)

    for place in all_places:
        popup_content = f"{place['name']}<br>Рейтинг: {place['rating']}"
        folium.Marker(
            [place['location']['latitude'], place['location']['longitude']],
            popup=popup_content,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    map_filename = f'map_{lat}_{lng}.html'
    map_path = os.path.join(MAPS_FOLDER, map_filename)
    m.save(map_path)

    return jsonify({'map': map_filename})

@app.route('/maps/<filename>')
def download_file(filename):
    return send_from_directory(MAPS_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
