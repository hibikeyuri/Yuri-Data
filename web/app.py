from flask import *

app = Flask()
app.secret_key = "nozomizore_is_the_best"

@app.route("/")
def index():
    pass

app.run()
