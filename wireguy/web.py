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
from authlib.integrations.flask_client import OAuth

from wireguy import settings
from wireguy.database import db, User, Peer


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object("wireguy.settings")

#if settings.oidc_enabled:

#oauth = OAuth(app)
#oauth.register(
#    "sso",
#    server_metadata_url=app.config.SSO_OPENID_CONFIG_URL,
#    client_kwargs={"scope": app.config.SSO_OPENID_SCOPE},
#)

common_vars_tpl = {
    "app": app.config.get_namespace('APP_')
}


@app.before_request
def before_request():
    app.logger.debug("connecting to db")
    db.connect()

@app.teardown_appcontext
def after_request(error):
    app.logger.debug("closing db")
    db.close()
    if error:
        app.logger.error(error)


@app.route("/")
def index():

    return render_template(
        "index.html",
        **common_vars_tpl
    )




@app.route("/login", methods=["GET", "POST"])
def login():
    """Login using SSO"""

    redirect_uri = url_for("callback", _external=True)
    return oauth.sso.authorize_redirect(redirect_uri)
    #if current_user.is_authenticated:
    #    app.logger.error("Shouldn't login when auth")
    #    flash("You are already logged in", "error")
    #    return redirect(url_for("devices"))

    #return render_template(
    #    "login.html", **common_vars_tpl
    #)


#@app.route("/login/oauth")
#def login_oauth():
#    redirect_uri = url_for("callback", _external=True)
#    return oauth.sso.authorize_redirect(redirect_uri)


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
            return redirect(url_for("devices"))
        else:
            app.logger.info("failed log in: {}".format(user_info["preferred_username"]))
            flash("Invalid credentials", "error")
    return redirect(url_for("index"))
    


@app.route("/logout")
def logout():
    
    return redirect(url_for("index"))


@app.route("/peers")
def peer_list():

    peers_list = Peer.get_active()
    #Peer.get_by_user_id()

    
    return 

@app.route("/peers/{XD}")
    def peer_list_filtered(XD:str):
        Peer.get_by_user_id()

