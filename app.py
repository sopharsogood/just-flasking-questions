from Flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "This is a placeholder for the site's index"
