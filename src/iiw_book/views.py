import base64
import io
import os
import re
import json

import qrcode
import requests


from django.http import (
    HttpResponse,
    HttpResponseRedirect,
    HttpResponseNotFound,
    HttpResponseBadRequest,
)
from django.template import loader
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

import logging

logger = logging.getLogger(__name__)

AGENT_URL = os.environ.get("AGENT_URL")


def index(request):
    template = loader.get_template("index.html")
    return HttpResponse(template.render(), request)


def invite(request):
    response = requests.post(f"{AGENT_URL}/connections/create-invitation")
    invite = response.json()

    streetcred_url = re.sub(
        r"^https?:\/\/\S*\?", "id.streetcred://invite?", invite["invitation_url"]
    )

    template = loader.get_template("invite.html")

    stream = io.BytesIO()
    qr_png = qrcode.make(invite["invitation_url"])
    qr_png.save(stream, "PNG")
    qr_png_b64 = base64.b64encode(stream.getvalue()).decode("utf-8")

    return HttpResponse(
        template.render(
            {"qr_png": qr_png_b64, "streetcred_url": streetcred_url}, request
        )
    )


@csrf_exempt
def webhooks(request, topic):

    message = json.loads(request.body)
    logger.info(f"webhook recieved - topic: {topic} body: {request.body}")

    # Handle new invites, send presentation request
    if topic == "connections" and message["state"] == "response":
        credential_definition_id = os.environ.get("VERIFIED_EMAIL_CRED_DEF_ID")
        connection_id = message["connection_id"]
        assert credential_definition_id is not None
        assert connection_id is not None

        logger.info(
            f"Sending presentation request for connection {message['connection_id']}"
        )

        request_body = {
            "requested_predicates": [],
            "requested_attributes": [
                {
                    "name": "email",
                    "restrictions": [{"cred_def_id": credential_definition_id}],
                },
            ],
            "connection_id": connection_id,
        }
        response = requests.post(
            f"{AGENT_URL}/presentation_exchange/send_request", json=request_body
        )

        return HttpResponse()

    # TODO: Handle presentation, verify
    if topic == "presentations" and message["state"] == "presentation_received":
        pass

    # Handle verify, save state in db
    if topic == "presentations" and message["state"] == "request_sent":
        pass
    # if topic == "presentations" and message["state"] == "verified":
        # credential_definition_id = os.environ.get("VERIFIED_EMAIL_CRED_DEF_ID")
        # connection_id = message["connection_id"]
        # assert credential_definition_id is not None
        # assert connection_id is not None

        # logger.info(
        #     f"Sending presentation request for connection {message['connection_id']}"
        # )

        # request_body = {
        #     "requested_predicates": [],
        #     "requested_attributes": [
        #         {
        #             "name": "email",
        #             "restrictions": [{"cred_def_id": credential_definition_id}],
        #         },
        #     ],
        #     "connection_id": connection_id,
        # }
        # response = requests.post(
        #     f"{AGENT_URL}/presentation_exchange/send_request", json=request_body
        # )

        # return HttpResponse()


    return HttpResponse()
