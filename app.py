from flask import Flask, render_template, request, jsonify, Response
from agents import *
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream', methods=['POST'])
def stream():

    data = request.json

    def generate():

        symptoms = data['symptoms']
        treatment = data['treatment']
        cost = int(data['cost'])
        plan = data['plan']

        # 🩺 Step 1
        yield f"data: {json.dumps({'step': 'Symptom Agent', 'status': 'loading'})}\n\n"
        time.sleep(1)

        symptom = symptom_agent(symptoms)
        yield f"data: {json.dumps({'step': 'Symptom Agent', 'status': 'done', 'data': symptom})}\n\n"

        # 🧪 Step 2
        yield f"data: {json.dumps({'step': 'Diagnostic Agent', 'status': 'loading'})}\n\n"
        time.sleep(1)

        diagnostic = diagnostic_agent(symptom)
        yield f"data: {json.dumps({'step': 'Diagnostic Agent', 'status': 'done', 'data': diagnostic})}\n\n"

        # 💊 Step 3
        yield f"data: {json.dumps({'step': 'Treatment Agent', 'status': 'loading'})}\n\n"
        time.sleep(1)

        treatment_res = treatment_agent(symptom, treatment)
        yield f"data: {json.dumps({'step': 'Treatment Agent', 'status': 'done', 'data': treatment_res})}\n\n"

        # 💰 Step 4
        yield f"data: {json.dumps({'step': 'Claim Agent', 'status': 'loading'})}\n\n"
        time.sleep(1)

        claim = claim_agent(plan, cost, treatment, diagnostic)
        yield f"data: {json.dumps({'step': 'Claim Agent', 'status': 'done', 'data': claim})}\n\n"

        # 📄 Step 5
        yield f"data: {json.dumps({'step': 'Explanation Agent', 'status': 'loading'})}\n\n"
        time.sleep(1)

        explanation = explanation_agent(symptom, diagnostic, treatment_res, claim)
        yield f"data: {json.dumps({'step': 'Explanation Agent', 'status': 'done', 'data': explanation})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

@app.route('/result')
def result():
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)