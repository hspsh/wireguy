import json
import logging
import os
from datetime import datetime

from flask import (
    Flask,
    flash,
    render_template,
    redirect,
    url_for,
    request,
    jsonify,
    abort,
)
from flask_login import (
    LoginManager,
    login_required,
    current_user,
    login_user,
    logout_user,
)
from authlib.integrations.flask_client import OAuth

from whois import settings
from whois.database import db, Device, User
from whois.helpers import (
    owners_from_devices,
    filter_hidden,
    unclaimed_devices,
    filter_anon_names,
    ip_range,
    in_space_required,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object("whois.settings")
login_manager = LoginManager()
login_manager.init_app(app)

if settings.oidc_enabled:
    oauth = OAuth(app)
    oauth.register(
        "sso",
        server_metadata_url=app.config.SSO_OPENID_CONFIG_URL,
        client_kwargs={"scope": app.config.SSO_OPENID_SCOPE},
    )

common_vars_tpl = {
    "app": app.config.get_namespace('APP_')
}

#TODO(critbit) might need to change auth handling to flask JWT or something
@login_manager.user_loader
def load_user(user_id):
    try:
        return User.get_by_id(user_id)
    except User.DoesNotExist as exc:
        app.logger.error("{}".format(exc))
        return None


@app.before_request
def before_request():
    app.logger.debug("connecting to db")
    db.connect()

    if request.headers.getlist("X-Forwarded-For"):
        ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        logger.info(
            "forward from %s to %s",
            request.remote_addr,
            request.headers.getlist("X-Forwarded-For")[0],
        )
    else:
        ip_addr = request.remote_addr

    #TODO(critbit): remove if local connection not needed, for sure it will not be need
    if not ip_range(settings.ip_mask, ip_addr):
        app.logger.error("%s", request.headers)
        flash("Outside local network, some functions forbidden!", "outside-warning")


@app.teardown_appcontext
def after_request(error):
    app.logger.debug("closing db")
    db.close()
    if error:
        app.logger.error(error)


@app.route("/")
def index():
    """Serve list of people in hs, show panel for logged users"""
    recent = Device.get_recent(**settings.recent_time)
    visible_devices = filter_hidden(recent)
    users = filter_hidden(owners_from_devices(visible_devices))

    return render_template(
        "landing.html",
        users=filter_anon_names(users),
        headcount=len(users),
        unknowncount=len(unclaimed_devices(recent)),
        **common_vars_tpl
    )


@login_required
@app.route("/devices")
def devices():
    recent = Device.get_recent(**settings.recent_time)
    visible_devices = filter_hidden(recent)
    users = filter_hidden(owners_from_devices(visible_devices))

    if current_user.is_authenticated:
        unclaimed = unclaimed_devices(recent)
        mine = current_user.devices
        return render_template(
            "devices.html",
            unclaimed=unclaimed,
            recent=recent,
            my_devices=mine,
            users=filter_anon_names(users),
            headcount=len(users),
            **common_vars_tpl
        )


#TODO(critbit): example enpoint, how to handle details or sth, idc
@app.route("/device/<mac_address>", methods=["GET"])
@login_required
@in_space_required()
def device_view(mac_address):
    """Get info about device, claim device, release device"""

    try:
        device = Device.get(Device.mac_address == mac_address)
    except Device.DoesNotExist as exc:
        app.logger.error("{}".format(exc))
        return abort(404)

    return render_template("device.html", device=device, **common_vars_tpl)

#TODO(critbit): I guess we don't need it
@app.route("/register", methods=["GET", "POST"])
@in_space_required()
def register():
    """Registration form"""
    if current_user.is_authenticated:
        app.logger.error("Shouldn't register when auth")
        flash("Shouldn't register when auth", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        # TODO: WTF forms for safety
        display_name = request.form["display_name"]
        username = request.form["username"]
        password = request.form["password"]

        try:
            user = User.register(username, password, display_name)
        except Exception as exc:
            if exc.args[0] == "too_short":
                flash("Password too short, minimum length is 3")
            else:
                print(exc)
        else:
            user.save()
            app.logger.info("registered new user: {}".format(user.username))
            flash("Registered.", "info")

        return redirect(url_for("login"))

    return render_template("register.html", **common_vars_tpl)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Login using query to DB or SSO"""
    if current_user.is_authenticated:
        app.logger.error("Shouldn't login when auth")
        flash("You are already logged in", "error")
        return redirect(url_for("devices"))

    if request.method == "POST":
        try:
            user = User.get(User.username == request.form["username"])
        except User.DoesNotExist:
            user = None

        if user is not None and user.auth(request.form["password"]) is True:
            login_user(user)
            app.logger.info("logged in: {}".format(user.username))
            flash(
                "Hello {}! You can now claim and manage your devices.".format(
                    current_user.username
                ),
                "success",
            )
            return redirect(url_for("devices"))
        else:
            app.logger.info("failed log in: {}".format(request.form["username"]))
            flash("Invalid credentials", "error")

    return render_template(
        "login.html", oauth_enabled=settings.oidc_enabled, **common_vars_tpl
    )


@app.route("/login/oauth")
def login_oauth():
    redirect_uri = url_for("callback", _external=True)
    return oauth.sso.authorize_redirect(redirect_uri)


@app.route("/login/callback")
def callback():
    token = oauth.sso.authorize_access_token()
    user_info = oauth.sso.parse_id_token(token)
    if user_info:
        print(user_info)
        try:
            user = User.get(User.username == user_info["preferred_username"])
        except User.DoesNotExist:
            user = None
            app.logger.warning("no user: {}".format(user_info["preferred_username"]))

        if user is not None:
            login_user(user)
            app.logger.info("logged in: {}".format(user.username))
            flash(
                "Hello {}! You can now claim and manage your devices.".format(
                    current_user.username
                ),
                "success",
            )
            return redirect(url_for("devices"))
        else:
            app.logger.info("failed log in: {}".format(user_info["preferred_username"]))
            flash("Invalid credentials", "error")
    return redirect(url_for("login"))
    


@app.route("/logout")
@login_required
def logout():
    username = current_user.username
    logout_user()
    app.logger.info("logged out: {}".format(username))
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile_edit():
    # TODO: logging
    if request.method == "POST":
        if current_user.auth(request.values.get("password", None)) is True:
            try:
                if (
                    request.form["new_password"] is not None
                    and len(request.form["new_password"]) > 0
                ):
                    current_user.password = request.form["new_password"]
            except Exception as exc:
                if exc.args[0] == "too_short":
                    flash("Password too short, minimum length is 3", "warning")
                else:
                    app.logger.error(exc)
            else:
                current_user.display_name = request.form["display_name"]
                new_flags = request.form.getlist("flags")
                current_user.is_hidden = "hidden" in new_flags
                current_user.is_name_anonymous = "anonymous for public" in new_flags
                app.logger.info(
                    "flags: got {} set {:b}".format(new_flags, current_user.flags)
                )
                current_user.save()
                flash("Saved", "success")
        else:
            flash("Invalid password", "error")

    return render_template("profile.html", user=current_user, **common_vars_tpl)
