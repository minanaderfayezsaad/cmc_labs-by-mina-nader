from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "Hello from Lab 3"

@app.route("/health")
def health():
    return "ok"

if __name__ == "__main__":
    # The host must be 0.0.0.0 to be reachable inside Docker
    app.run(host="0.0.0.0", port=5000)
