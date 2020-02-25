from quantools.apis import api
from flask import Flask
app = Flask(__name__)

api.init_app(app)
if __name__=="__main__":
    import os
    port = int(os.getenv('PORT', 8080))
    app.run(host="localhost",port=port,debug=True)