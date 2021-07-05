import os


SECRET_KEY = os.environ["SECRET_KEY"]
if not SECRET_KEY:
    raise ValueError("No SECRET_KEY set for Flask application")

APP_VERSION = "0.1.0"
#TODO(critbit) change as you like
APP_TITLE = "🐉 wireguy"
APP_NAME = "wireguy"
APP_BASE_URL = "wireguy.hsp.sh"

#TODO(critbit): footer links
APP_HOME_URL = "//hsp.sh"
APP_WIKI_URL = "//wiki.hsp.sh/wireguy"
APP_REPO_URL = "//github.com/hspsh/wireguy"

DB_PATH = os.environ.get("DB_PATH", "{}.db".format(APP_NAME))

# OAuth settings
SSO_CLIENT_ID = os.environ.get("OAUTH_CLIENT_ID")
SSO_CLIENT_SECRET = os.environ.get("OAUTH_CLIENT_SECRET")
SSO_AUTH_URL = os.environ.get("OAUTH_AUTH_URL")
SSO_TOKEN_URL = os.environ.get("OAUTH_TOKEN_URL")
SSO_USERINFO_URL = os.environ.get("OAUTH_USERINFO_URL")

oidc_enabled = SSO_CLIENT_ID is not None
