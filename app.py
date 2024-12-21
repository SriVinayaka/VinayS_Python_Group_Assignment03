from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
import pickle
import numpy as np
import warnings

# Ignore all warnings
warnings.filterwarnings("ignore")


# Initialize Flask application
app = Flask(__name__)
app.secret_key = 'secret_key'  # Use a secret key for session management

db_password = ""
# Connect to MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=db_password,
        database="loan_eligibility"
    )


# Load the saved machine learning model
loan_model = "./models/loan_eligibility_model.pkl"
model = pickle.load(open(loan_model, 'rb'))


# Home page
@app.route('/')
def home():
    return render_template('home.html')


# Register page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Insert user into the MySQL database
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")
        db.commit()
        db.close()

        return redirect(url_for('login'))
    return render_template('register.html')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if user exists in the database
        db = connect_db()
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM users WHERE username='{username}' AND password='{password}'")
        user = cursor.fetchone()
        db.close()

        if user:
            session['user'] = username
            return redirect(url_for('predict'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')


# Predict page
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Extract user inputs
        gender = int(request.form['gender'])
        married = int(request.form['married'])
        dependents = int(request.form['dependents'])
        self_employed = int(request.form['self_employed'])
        education = int(request.form['education'])
        income = float(request.form['income'])
        co_income = float(request.form['co_income'])
        loan_amount = float(request.form['loan_amount'])
        loan_term = int(request.form['loan_term'])
        credit_history = int(request.form['credit_history'])
        property_area = int(request.form['property_area'])

        # Prepare the input data for prediction
        user_input = np.array([[gender, married, dependents, self_employed, education, income, co_income, loan_amount,
                                loan_term, credit_history, property_area]])

        # Predict the loan eligibility
        #prediction = model.predict(user_input)
        prediction = model.predict_proba(user_input)
        print(prediction[0][1])
        # Display the result
        if prediction[0][1] > 0.3:
            result = "Loan Approved"
        else:
            result = "Loan Denied"

        return render_template('result.html', result=result)

    return render_template('predict.html')


# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)
