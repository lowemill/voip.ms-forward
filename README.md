# VoIP.MS forwarding manager

Flask app that interacts with the VoIP.MS API to allow otherwise unprivileged
users to cause a specific predefined DID to be forwarded/unforwarded.

This app doesn't authenticate users; it's expected that you're running it behind
`nginx` or a similar reverse proxy that can do authentication (by IP address,
with Basic auth, or otherwise) for you.

## Requirements

Create "Call Forwarding" entries in the VoIP.MS web management portal. Make sure
to set the "Description" field; this is displayed in our UI.

Enable the API on the [VoIP.MS API](https://voip.ms/m/api.php) settings. Allow
the IP this app will be making requests from. Set the API password.

Run the app with the following environment variables:

* `VOIPMS_API_USERNAME` is the email address you use to log in to VoIP.MS.
* `VOIPMS_API_PASSWORD` is the API password you set earlier.
* `VOIPMS_FORWARD_DID` is the DID number that will be managed by this app.
* `VOIPMS_FORWARD_DEFAULT_ROUTING` is the desired "not forwarded" routing for
  this number. If you want to route to subaccount `123456_test`, use
  `account:123456_test` for this value. More possible values are on the
  "setDIDRouting" section of the [API docs](https://voip.ms/m/apidocs.php).

## Simple server

In a virtualenv, run `./setup.py develop`. You can run the server on port 5050
with `python -m voipms_forward`.

## gunicorn

You can use gunicorn to serve the app in production by running the WSGI
applicaiton `voipms_forward:get_app()`.
