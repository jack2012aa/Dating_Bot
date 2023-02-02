from flask import Flask
import routes

app = Flask(__name__)
routes.init_app(app)

if __name__ == "__main__":
    app.run()