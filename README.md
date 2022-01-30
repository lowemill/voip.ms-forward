# VoIP.MS forwarding manager

Flask app that interacts with the VoIP.MS API to allow otherwise unprivileged
users to cause a specific predefined DID to be forwarded/unforwarded.

This app doesn't authenticate users; it's expected that you're running it behind
`nginx` or a similar reverse proxy that can do authentication (by IP address,
with Basic auth, or otherwise) for you.

## Building, configuring, and deploying

Build a container image with `pack`. You only need to do these steps once:

* Follow the instructions at https://buildpacks.io/docs/tools/pack/ to install
  the buildpack utilities.
* `pack config default-builder paketobuildpacks/builder:base`

Configure the app on your destination host. Create a text file anywhere (we use
`/opt/environments/forwarding.env`) following this template:

```
LOGIN_PASSWORD=hunter2
VOIPMS_API_USERNAME=yourvoipmsaccount@gmail.com
VOIPMS_API_PASSWORD=apipassword
VOIPMS_FORWARD_DID=2565121024
VOIPMS_FORWARD_DEFAULT_ROUTING=account:292123_subaccountname
```

The "Requirements" section describes each variable in more detail.

Every time you make a change to the app, use these steps to rebuild the
container image. You'll get a Docker image with the name
`lowemill-voipms-forward`:

* `pack build lowemill-voipms-forward`

To deploy the app, export the image from your local machine, use `sftp` or `scp`
to get it to your destination host, import the image, and stop/start the
container:

* `docker image save lowemill-voipms-forward -o image.tar`
* `scp image.tar dest:`

On `dest`:

* `docker image load -i image.tar`
* `docker container stop lowemill-voipms-forward`
* `docker container rm lowemill-voipms-forward`

To restart the container, run the following command, substituting for your
environment as needed:

```
docker run \
    --publish 9097:8000 \
    --env-file /opt/environments/forwarding.env \
    -d --restart=always --name lowemill-voipms-forward \
    lowemill-voipms-forward
```

This will configure the container to run on host / Docker daemon restart.

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

