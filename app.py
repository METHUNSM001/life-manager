from flask import Flask, render_template, request, redirect, url_for, session, flash
import pandas as pd
import os
import requests
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "super_secret_key"

# ===============================
# DATA SETUP
# ===============================
DATA_DIR = "data"
USERS_FILE = os.path.join(DATA_DIR, "users.xlsx")
os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(USERS_FILE):
    pd.DataFrame(columns=["name", "email", "password"]).to_excel(USERS_FILE, index=False)

# ===============================
# GROQ API
# ===============================
GROQ_API_KEY = #add your Groq API key here
# ===============================
# LANGUAGE MAP
# ===============================
language_map = {
    "en-US": "English",
    "ta-IN": "Tamil",
    "hi-IN": "Hindi",
    "ml-IN": "Malayalam"
}

# ===============================
# LOGIN
# ===============================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        df = pd.read_excel(USERS_FILE)
        user = df[df["email"] == request.form["email"]]

        if not user.empty and check_password_hash(
            user.iloc[0]["password"], request.form["password"]
        ):
            session["user"] = user.iloc[0]["name"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password", "error")

    return render_template("login.html")

# ===============================
# REGISTER
# ===============================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        df = pd.read_excel(USERS_FILE)
        if email in df["email"].values:
            flash("Email already registered", "error")
            return render_template("register.html")

        hashed = generate_password_hash(password)
        df = pd.concat(
            [df, pd.DataFrame([{"name": name, "email": email, "password": hashed}])],
            ignore_index=True
        )
        df.to_excel(USERS_FILE, index=False)

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# ===============================
# DASHBOARD
# ===============================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

# ===============================
# AI HELPER
# ===============================
def generate_ai(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30
    )
    data = response.json()
    if "choices" in data:
        return data["choices"][0]["message"]["content"]
    return "Unable to generate response."

# ===============================
# DIET SCHEDULER
# ===============================
@app.route("/diet", methods=["GET", "POST"])
def diet():
    if "user" not in session:
        return redirect(url_for("login"))

    diet_plan = None
    if request.method == "POST":
        lang = request.form.get("language", "en-US")
        prompt = f"""
        Create a concise daily diet plan in {language_map.get(lang)}.
        Height: {request.form['height']} cm
        Weight: {request.form['weight']} kg
        Goal: {request.form['goal']}
        """
        diet_plan = generate_ai(prompt)

    return render_template("diet_scheduler.html", diet_plan=diet_plan)

# ===============================
# CROP ADVISOR
# ===============================
@app.route("/crop_advisor", methods=["GET", "POST"])
def crop_advisor():
    if "user" not in session:
        return redirect(url_for("login"))

    recommendation = None
    if request.method == "POST":
        lang = request.form.get("language", "en-US")
        prompt = f"""
        Recommend best crops in {language_map.get(lang)}.
        Soil: {request.form['soil_type']}
        Water: {request.form['water_level']}
        Location: {request.form['location']}
        Season: {request.form['season']}
        Previous Crop: {request.form.get('previous_crop','')}
        Area: {request.form.get('area_size','')}
        """
        recommendation = generate_ai(prompt)

    return render_template("crop_advisor.html", recommendation=recommendation)

# ===============================
# TRIP PLANNER (FIXED)
# ===============================
@app.route("/trip", methods=["GET", "POST"])
def trip():
    if "user" not in session:
        return redirect(url_for("login"))

    trip_plan = None
    budget = duration = month = None

    if request.method == "POST":
        budget = request.form.get("budget")
        duration = request.form.get("duration")
        month = request.form.get("month")
        lang = request.form.get("language", "en-US")

        prompt = f"""
        Create a concise trip plan in {language_map.get(lang)}.
        Budget: {budget}
        Trip Type: {request.form['trip_type']}
        From: {request.form['from_location']}
        Duration: {duration} days
        Travel Style: {request.form['style']}
        Interests: {request.form['interests']}
        Month: {month}
        """

        trip_plan = generate_ai(prompt)

    return render_template(
        "trip_planner.html",
        trip_plan=trip_plan,
        budget=budget,
        duration=duration,
        month=month
    )

# ===============================
# LOGOUT
# ===============================
@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.clear()
    return redirect(url_for("login"))

# ===============================
# RUN APP
# ===============================
if __name__ == "__main__":
    app.run(debug=True)
