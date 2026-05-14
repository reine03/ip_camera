from flask import Flask
from flask_bcrypt import Bcrypt
from database.models import db
from routes.auth import auth
from routes.dashboard import dashboard_bp
from routes.camera import camera_bp
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)

app.register_blueprint(auth)
app.register_blueprint(dashboard_bp)
app.register_blueprint(camera_bp)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)