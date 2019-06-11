#!/bin/env python

from flask import *

import config
import util

app = Flask(__name__)
app.debug = True
app.secret_key = config.SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/auth/init")
def auth_init():
    http = util.init_http_api(session)

    req = {
        "userHash": config.USERHASH,
        "redirectUrl": "http://localhost:5000/auth/complete",
        "language": "en",
    }

    j = http.post("v1/authentication/initialize", json=req).json()
    if "authUrl" not in j:
        session.errorMessage = "Authentication failed. Check you credentials in config.py"
        return render_template("error.html")
    return redirect(j["authUrl"])


@app.route("/auth/complete")
def auth_complete():
    http = util.init_http_api(session)

    req = {
        "code": request.args.get("code")
    }

    j = http.post("v1/authentication/tokens", json=req).json()
    return complete_login(j)


@app.route("/auth/unattended", methods=["GET", "POST"])
def auth_unattended():

    if request.method == "POST":
        http = util.init_http_api(session)

        req = {
            "userHash": config.USERHASH,
            "loginToken": request.form["loginToken"],
        }

        j = http.post("v1/authentication/unattended", json=req).json()
        return complete_login(j)

    return render_template("login_with_token.html")


@app.route("/auth/logout")
def auth_logout():
    del session["accessToken"]
    return redirect(url_for("index"))


@app.route("/query/accounts")
def query_accounts():
    http = util.init_http_api(session)
    j = http.get("v2/accounts").json()
    return jsonify(j)


@app.route("/query/accounts/<account_id>/transactions")
def query_transactions(account_id):
    http = util.init_http_api(session)
    j = http.get("v2/accounts/%s/transactions" % account_id).json()
    return jsonify(j)


def complete_login(j):
    # long lived access
    session["loginToken"] = j["login"]["loginToken"]
    session["label"] = j["login"]["label"]

    # short lived access
    session["accessToken"] = j["session"]["accessToken"]
    session["sessionExpires"] = j["session"]["expires"]

    return redirect(url_for("index"))


if __name__ == '__main__':
    app.run()
