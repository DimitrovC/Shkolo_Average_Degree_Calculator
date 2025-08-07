from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os

app = Flask(__name__)

SUBJECTS_FILE = os.path.join('static', 'data', 'subjects.json')

os.makedirs(os.path.join('static', 'data'), exist_ok=True)

def init_subjects_file():
    if not os.path.exists(SUBJECTS_FILE):
        with open(SUBJECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "subjects": [
                    "Български език и литература",
                    "Математика"
                ]
            }, f, ensure_ascii=False, indent=2)

def load_subjects():
    with open(SUBJECTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_subjects(data):
    with open(SUBJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return render_template('Shkolo_Calculator.html')

@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/api/subjects', methods=['GET'])
def get_subjects():
    return jsonify(load_subjects())

@app.route('/api/subjects', methods=['POST'])
def update_subjects():
    data = request.get_json()
    save_subjects(data)
    return jsonify({"success": True})

@app.route('/api/subjects/add', methods=['POST'])
def add_subject():
    data = request.get_json()
    subjects_data = load_subjects()
    
    if 'subject' not in data:
        return jsonify({"success": False, "error": "No subject provided"}), 400
    
    subject_name = data['subject']
    
    if subject_name in subjects_data['subjects']:
        return jsonify({"success": False, "error": "Subject already exists"}), 400
    
    subjects_data['subjects'].append(subject_name)
    save_subjects(subjects_data)
    
    return jsonify({"success": True})

@app.route('/api/subjects/delete/<int:index>', methods=['DELETE'])
def delete_subject(index):
    subjects_data = load_subjects()
    
    if index < 0 or index >= len(subjects_data['subjects']):
        return jsonify({"success": False, "error": "Invalid subject index"}), 400
    
    del subjects_data['subjects'][index]
    save_subjects(subjects_data)
    
    return jsonify({"success": True})

@app.route('/api/subjects/move', methods=['POST'])
def move_subject():
    try:
        data = request.get_json()
        from_index = data.get('from')
        to_index = data.get('to')
        
        if from_index is None or to_index is None:
            return jsonify({'error': 'Missing from/to indexes'}), 400
        
        with open(SUBJECTS_FILE, 'r', encoding='utf-8') as f:
            subjects_data = json.load(f)
        
        subjects = subjects_data.get('subjects', [])
        
        if not (0 <= from_index < len(subjects)) or not (0 <= to_index < len(subjects)):
            return jsonify({'error': 'Invalid indexes'}), 400
        
        subject = subjects.pop(from_index)
        subjects.insert(to_index, subject)
        
        with open(SUBJECTS_FILE, 'w', encoding='utf-8') as f:
            json.dump({'subjects': subjects}, f, ensure_ascii=False, indent=4)
        
        return jsonify({'message': 'Subject moved successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_subjects_file()
    app.run(debug=True)