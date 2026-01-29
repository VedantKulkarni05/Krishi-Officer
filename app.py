# Main entry point of the Flask app
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    """Serve the landing page"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Serve the dashboard page"""
    return render_template('dashboard.html')


@app.route('/pest-detection')
def pest_detection():
    """Serve the pest detection page"""
    return render_template('pest-detection.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')