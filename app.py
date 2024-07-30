from flask import Flask
from routers import routers

app = Flask(__name__)
app.secret_key = "supersecretkey"

routers.init_app(app)

if __name__ == '__main__':
    #app.run()
    app.run(host='10.20.202.155', port=5000, ssl_context=('cert.pem', 'key.pem'))
    #app.run(host='0.0.0.0', port=5000, ssl_context=('/app/app/cert.pem', '/app/app/key.pem'))
    #app.run(host='0.0.0.0', port=5000)
