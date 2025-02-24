from flask import Flask, request, render_template
import pandas as pd
import os

app = Flask(__name__)

# Load the CSV with buy links
medicine_data = pd.read_csv('medical data.csv')  # Ensure correct file name

def find_medicine(symptoms_list):
    symptoms_input = [s.strip().lower() for s in symptoms_list.split(',')]
    symptoms_input_set = set(symptoms_input)
    
    best_match = None
    max_matched_symptoms = 0
    
    for _, row in medicine_data.iterrows():
        dataset_symptoms = [s.strip().lower() for s in row['Symptoms Treated'].split('|')]
        dataset_symptoms_set = set(dataset_symptoms)
        
        matched_symptoms = symptoms_input_set.intersection(dataset_symptoms_set)
        num_matched = len(matched_symptoms)
        
        if num_matched > 0 and num_matched > max_matched_symptoms:
            dosages = row['Dosages'].split('|') if pd.notna(row['Dosages']) else []
            notes = row['Notes'].split('|') if pd.notna(row['Notes']) else []
            symptom_details = {}

            for i, dataset_symptom in enumerate(dataset_symptoms):
                if dataset_symptom in matched_symptoms:
                    symptom_details[dataset_symptom] = {
                        'dosage': dosages[i] if i < len(dosages) else 'N/A',
                        'note': notes[i] if i < len(notes) else 'N/A'
                    }
            
            best_match = {
                'medicine': row['Medicine'],
                'details': symptom_details,
                'matched_symptoms': list(matched_symptoms),
                'links': {
                    'Amazon': row.get('Amazon_Link', None),
                    '1mg': row.get('1mg_Link', None),
                    'Apollo': row.get('Apollo_Link', None)
                }
            }
            max_matched_symptoms = num_matched
    
    return best_match

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendation = None
    
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        if symptoms:
            recommendation = find_medicine(symptoms)
    
    return render_template('index.html', recommendation=recommendation)

if not os.path.exists('templates'):
    os.makedirs('templates')

if __name__ == '__main__':
    app.run(debug=True)