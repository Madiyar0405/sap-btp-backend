from flask import Flask, request, jsonify
import psycopg2
import os
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={
    r"/*": {
         "origins": "*",
        "allow_headers": [
            "Origin", 
            "Content-Type", 
            "Accept", 
            "Authorization", 
            "Access-Control-Allow-Origin"
        ],
        "expose_headers": [
            "Access-Control-Allow-Origin", 
            "Access-Control-Allow-Credentials"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        "supports_credentials": True
    }
})

app.secret_key = os.urandom(24)



def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('SUPABASE_HOST'),
        database=os.getenv('SUPABASE_DB'),
        user=os.getenv('SUPABASE_USER'),
        password=os.getenv('SUPABASE_PASSWORD'),
        port=os.getenv('SUPABASE_PORT', 5432)
    )
    return conn

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accidents')
    incidents = cursor.fetchall()
    cursor.close()
    conn.close()

    incidents_list = []
    for incident in incidents:
        incident_dict = {
            'id': incident[0],
            'request_service': incident[1],
            'request_type': incident[2],
            'location': incident[3],
            'floor_office_cabinet': incident[4],
            'description': incident[5],
            'administrative_object': incident[6],
            'production_object': incident[7],
            'cable_line_name': incident[8],
            'cable_line_type': incident[9],
            'horizon': incident[10],
            'cable_brand': incident[11],
            'number_of_fibers': incident[12],
            'cable_length': incident[13],
            'laying_method': incident[14],
            'labels': incident[15]
        }
        incidents_list.append(incident_dict)

    return jsonify(incidents_list)


@app.route('/api/incidents', methods=['POST'])
def create_incident():
    data = request.get_json()
    
    if isinstance(data, list):
        responses = []
        for item in data:
            response = process_single_incident(item)
            responses.append(response)
        return jsonify(responses), 201
    
    return process_single_incident(data)

def process_single_incident(data):
    try:
        request_service = data.get('request_service')
        request_type = data.get('request_type')
        location = data.get('location')
        floor_office_cabinet = data.get('floor_office_cabinet')
        description = data.get('description')
        administrative_object = data.get('administrative_object')
        production_object = data.get('production_object')
        cable_line_name = data.get('cable_line_name')
        cable_line_type = data.get('cable_line_type')
        horizon = data.get('horizon')
        cable_brand = data.get('cable_brand')
        number_of_fibers = data.get('number_of_fibers')
        cable_length = data.get('cable_length')
        laying_method = data.get('laying_method')
        labels = data.get('labels')

        if not all([request_service, request_type, location]):
            return {'error': 'Please fill in all required fields!'}, 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO accidents (request_service, request_type, location, floor_office_cabinet, description, 
                       administrative_object, production_object, cable_line_name, cable_line_type, horizon, 
                       cable_brand, number_of_fibers, cable_length, laying_method, labels)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (request_service, request_type, location, floor_office_cabinet, description, administrative_object,
             production_object, cable_line_name, cable_line_type, horizon, cable_brand, number_of_fibers,
             cable_length, laying_method, labels)
        )
        
        new_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()

        return {'message': 'Incident report submitted successfully!', 'id': new_id}, 201
    
    except Exception as e:
        return {'error': f'Error processing incident: {str(e)}'}, 500

@app.route('/api/incidents/<int:id>', methods=['GET'])
def get_incident(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM accidents WHERE id = %s', (id,))
    incident = cursor.fetchone()
    cursor.close()
    conn.close()

    if incident is None:
        return jsonify({'error': 'Incident not found'}), 404

    incident_data = {
        'id': incident[0],
        'request_service': incident[1],
        'request_type': incident[2],
        'location': incident[3],
        'floor_office_cabinet': incident[4],
        'description': incident[5],
        'administrative_object': incident[6],
        'production_object': incident[7],
        'cable_line_name': incident[8],
        'cable_line_type': incident[9],
        'horizon': incident[10],
        'cable_brand': incident[11],
        'number_of_fibers': incident[12],
        'cable_length': incident[13],
        'laying_method': incident[14],
        'labels': incident[15]
    }

    return jsonify(incident_data)

if __name__ == '__main__':
    app.run(debug=True)