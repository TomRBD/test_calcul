from flask import Flask, request, jsonify, render_template, send_from_directory
import calcul  # Assurez-vous que cela correspond au nom de votre module Python

app = Flask(__name__)

@app.route('/')
def home():
    # Nous servons maintenant votre fichier HTML séparément
    return render_template('index.html')

@app.route('/riot.txt')
def serve_riot_file():
    return send_from_directory('static', 'riot.txt')

@app.route('/get_time_played', methods=['POST'])
def get_time_played():
    data = request.json  # Utiliser les données JSON envoyées par le client
    user_name = data['user_name']
    region = data['region']
    puuid = calcul.get_puuid(region, user_name)
    if puuid:
        match_history = calcul.get_match_history(region, puuid)
        if match_history:
            total_time = calcul.calculate_total_time(region, match_history)
            return jsonify({'time_played': total_time})
        else:
            return jsonify({'error': 'No matches found for this user.'}), 404
    else:
        return jsonify({'error': 'Could not retrieve PUUID for this user.'}), 404

if __name__ == '__main__':
    app.run(debug=True)
