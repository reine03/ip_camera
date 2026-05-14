from flask import Blueprint, render_template, session, redirect, url_for
from database.models import LoginLog, CameraLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.home"))

    login_logs = LoginLog.query.order_by(LoginLog.timestamp.desc()).limit(20).all()
    camera_logs = CameraLog.query.order_by(CameraLog.timestamp.desc()).limit(20).all()

    return render_template("dashboard.html",
                           user=session["user"],
                           login_logs=login_logs,
                           camera_logs=camera_logs)