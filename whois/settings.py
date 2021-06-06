import os

#w labello lepiej

SECRET_KEY = os.environ["SECRET_KEY"]
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")
# mikrtotik ip, or other reporting devices
name = "kto hakuje"
base_url = "https://whois.at.hsp.sh"
whitelist = ["192.168.88.1"]
host = "0.0.0.0"
user_flags = {1: "hidden", 2: "name_anonymous"}
device_flags = {1: "hidden", 2: "new", 4: "infrastructure", 8: "esp", 16: "laptop"}

recent_time = {"minutes": 20}

oidc_enabled = True
# OAuth settings
SSO_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
SSO_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
SSO_AUTH_URL = os.environ.get("OAUTH_AUTH_URL")
SSO_TOKEN_URL = os.environ.get("OAUTH_TOKEN_URL")
SSO_USERINFO_URL = os.environ.get("OAUTH_USERINFO_URL")

# production
ip_mask = "192.168.88.1-255"
# TODO: better way for handling dev env
# ip_mask = "127.0.0.1"
