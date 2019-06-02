from flask import Flask
from apis import api
import os
port = int(os.getenv('PORT', 8080))
app = Flask(__name__)
api.init_app(app)
if __name__=="__main__":
    app.run(host="0.0.0.0",port=port,debug=False)