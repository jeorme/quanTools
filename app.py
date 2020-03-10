from quantools.apis import api
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')
api.init_app(app)


if __name__=="__main__":
    import os
    port =os.getenv('PORT')
    print(port)
    portID = 8080 if port is None else int(port)
    print(portID)
    app.run(host='0.0.0.0',port=portID,debug=True)