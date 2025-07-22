from flask import Flask, render_template, request, jsonify
import os, requests
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("message", "")
    print("Received question:", question)
    reply = ask_perplexity(question)
    print("Reply:", reply)
    return jsonify({"reply": reply})

def calculate_attendance(total, attended):
    percentage = (attended / total) * 100
    eligible = percentage >= 75
    needed = 0
    while ((attended + needed) / (total + needed)) * 100 < 75:
        needed += 1
    return round(percentage, 2), eligible, needed

@app.route("/", methods=["GET", "POST"])
def index():
    percent = None
    eligible = None
    needed = None
    response = ""
    question = ""

    if request.method == "POST":
        if "total_classes" in request.form:
            total = int(request.form['total_classes'])
            attended = int(request.form['attended_classes'])
            percent, eligible, needed = calculate_attendance(total, attended)
        elif "query" in request.form:
            question = request.form['query']
            response = ask_perplexity(question)

    return render_template("index.html", percent=percent, eligible=eligible, needed=needed, response=response, question=question)

def ask_perplexity(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "sonar"
,  # valid model
        "messages": [
            {"role": "system", "content": "You are Attendance Buddy, an AI assistant that helps students track and improve their attendance. You give actionable tips, motivational advice, and practical suggestions to help them stay above 75% attendance."},
            {"role": "user", "content": prompt}
        ]
    }
    try:
        res = requests.post(url, headers=headers, json=data, timeout=10)
        print("Perplexity API status:", res.status_code)
        print("Perplexity API response:", res.text)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
        else:
            return f"API Error: {res.status_code} - {res.text}"
    except Exception as e:
        print("Exception:", e)
        return f"Request failed: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)
