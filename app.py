from quantools.apis import api
from flask import Flask
app = Flask(__name__)

api.init_app(app)
if __name__=="__main__":
    import os
    port =os.getenv('PORT')
    print(port)
    portID = 5000 if port is None else int(port)
    print(portID)
    app.run(host='0.0.0.0',port=portID,debug=True)