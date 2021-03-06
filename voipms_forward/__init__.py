import os
import secrets
import sys

from flask import Flask, g, render_template, session, request, redirect, url_for, flash
from .voipms import VoIPMSAPI

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", os.urandom(32))


@app.before_request
def inject_config():
    g.api = VoIPMSAPI(
        api_username=os.getenv("VOIPMS_API_USERNAME"),
        api_password=os.getenv("VOIPMS_API_PASSWORD"),
    )

    g.did = os.getenv("VOIPMS_FORWARD_DID")
    g.default_routing = os.getenv("VOIPMS_FORWARD_DEFAULT_ROUTING")


@app.before_request
def check_login():
    if (request.authorization and
            request.authorization.password == os.getenv("LOGIN_PASSWORD")):
        return

    if request.cookies.get("auth") == os.getenv("LOGIN_PASSWORD"):
        return

    return "", 401, {"WWW-Authenticate": "Basic realm=Please log in"}


@app.before_request
def inject_csrf_prevention_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)


@app.after_request
def cleanup_api_session(resp):
    g.api.sess.close()
    return resp


def get_voipms_info():
    forwards = g.api.call("getForwardings")["forwardings"]

    did_info = g.api.call("getDIDsInfo", did=g.did)["dids"][0]
    current_routing = did_info["routing"]

    current_routing_description = f"Unknown routing ({current_routing})"
    for forward in forwards:
        if current_routing == f"fwd:{forward['forwarding']}":
            current_routing_description = forward["description"]
    else:
        if current_routing == g.default_routing:
            current_routing_description = "Not forwarded"

    return forwards, current_routing_description


@app.route("/")
def index():
    forwards, current_routing_description = get_voipms_info()

    return render_template(
        "index.html", forwards=forwards, current=current_routing_description,
    )


@app.route("/forward/", methods=["POST"])
def do_forward():
    if request.form["csrf"] != session["csrf"]:
        flash("Sorry, that didn't work. Please try again. (CSRF check failed)")
        return redirect(url_for("index"))

    forward_ids = {
        i["forwarding"] for i in g.api.call("getForwardings")["forwardings"]}

    if request.form["forward"] in forward_ids:
        result = g.api.call("setDIDRouting", did=g.did,
                          routing=f"fwd:{request.form['forward']}")

    elif request.form["forward"] == "default":
        result = g.api.call("setDIDRouting", did=g.did,
                          routing=g.default_routing)

    else:
        flash("Sorry, that didn't work. (Invalid forwarding requested)")
        return redirect(url_for("index"))

    if result["status"] == "success":
        flash("Forwarding set.")
    else:
        flash(f"Sorry, that didn't work. (VoIP.MS said {result['status']})")

    return redirect(url_for("index"))


@app.route("/add/", methods=["POST"])
def do_add():
    if request.form["csrf"] != session["csrf"]:
        flash("Sorry, that didn't work. Please try again. (CSRF check failed)")
        return redirect(url_for("index"))

    result = g.api.call("setForwarding",
                        phone_number=request.form["destination"],
                        description=request.form["description"])

    if result["status"] == "success":
        flash("New forwarding option added.")

    else:
        flash(f"Sorry, that didn't work. (VoIP.MS said {result['status']})")

    return redirect(url_for("index"))


@app.route("/cisco/")
def do_cisco():
    if "Cisco" not in request.headers["User-Agent"]:
        return "You're not a phone!", 400, {}

    result = None
    if "set" in request.args:
        result = g.api.call("setDIDRouting", did=g.did,
                            routing=f"fwd:{request.args['set']}")

    elif "unset" in request.args:
        result = g.api.call("setDIDRouting", did=g.did,
                            routing=g.default_routing)

    forwards, current_routing_description = get_voipms_info()

    if result is not None:
        if result["status"] != "success":
            msg = "Forwarding failed :("
        else:
            return render_template(
                "cisco-done.xml",
                msg=f"The new destination is: {current_routing_description}"
            )

    else:
        msg = f"Current: {current_routing_description}"

    return render_template(
        "cisco.xml", msg=msg, forwards=forwards,
        current=current_routing_description,
    )


def get_app():
    for key in ["VOIPMS_API_USERNAME", "VOIPMS_API_PASSWORD",
                "VOIPMS_FORWARD_DID", "VOIPMS_FORWARD_DEFAULT_ROUTING"]:
        if not os.getenv(key):
            raise ValueError(f"Missing config {key}")

    return app
