import base64
import io
import os
import re
import json
from datetime import datetime

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

from django.db.utils import IntegrityError

from .models import Attendee

import logging

logger = logging.getLogger(__name__)

AGENT_URL = os.environ.get("AGENT_URL")
VERIFIED_EMAIL_CRED_DEF_ID = os.environ.get("VERIFIED_EMAIL_CRED_DEF_ID")

if not AGENT_URL:
    raise Exception("AGENT_URL is not set")
if not VERIFIED_EMAIL_CRED_DEF_ID:
    raise Exception("VERIFIED_EMAIL_CRED_DEF_ID is not set")


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


def backend(request):
    template = loader.get_template("backend.html")
    attendees = Attendee.objects.filter(approved=False, denied=False)
    return HttpResponse(template.render({"attendees": attendees}, request))


def backend_denied(request):
    template = loader.get_template("backend_denied.html")
    attendees = Attendee.objects.filter(approved=False, denied=True)
    return HttpResponse(template.render({"attendees": attendees}, request))


def backend_approved(request):
    template = loader.get_template("backend_approved.html")
    attendees = Attendee.objects.filter(approved=True)
    return HttpResponse(template.render({"attendees": attendees}, request))


def attendees_submit(request):
    if request.method == "POST":
        email = request.POST.get("email")
        full_name = request.POST.get("full_name")
        approved = request.POST.get("approve")
        denied = request.POST.get("deny")

        attendee = Attendee.objects.get(email=email)
        attendee.full_name = full_name
        if approved:
            attendee.approved = True
        elif denied:
            attendee.denied = True

        attendee.save()

        # attendance cred def id
        credential_definition_id = cache.get("credential_definition_id")
        assert credential_definition_id is not None

        request_body = {
            "connection_id": str(attendee.connection_id),
            "credential_definition_id": credential_definition_id,
        }

        response = requests.post(
            f"{AGENT_URL}/credential_exchange/send-offer", json=request_body
        )

        return HttpResponseRedirect("/backend")

    return HttpResponseNotFound()


@csrf_exempt
def webhooks(request, topic):

    message = json.loads(request.body)
    logger.info(f"webhook recieved - topic: {topic} body: {request.body}")

    # Handle new invites, send presentation request
    if topic == "connections" and message["state"] == "response":
        connection_id = message["connection_id"]
        assert connection_id is not None

        logger.info(
            f"Sending presentation request for connection {message['connection_id']}"
        )

        request_body = {
            "name": "BC Gov Verified Email",
            "version": "1.0.0",
            "requested_predicates": [],
            "requested_attributes": [
                {
                    "name": "email",
                    "restrictions": [{"cred_def_id": VERIFIED_EMAIL_CRED_DEF_ID}],
                }
            ],
            "connection_id": connection_id,
        }
        response = requests.post(
            f"{AGENT_URL}/presentation_exchange/send_request", json=request_body
        )

        return HttpResponse()

    # TODO: Handle presentation, verify
    if topic == "presentations" and message["state"] == "presentation_received":
        presentation_exchange_id = message["presentation_exchange_id"]
        assert presentation_exchange_id is not None

        logger.info(
            f"Verifying presentation for presentation id {message['presentation_exchange_id']}"
        )

        response = requests.post(
            f"{AGENT_URL}/presentation_exchange/{presentation_exchange_id}/verify_presentation"
        )

        logger.info(response.text)

        return HttpResponse()

    # Handle verify, save state in db
    if topic == "presentations" and message["state"] == "verified":
        connection_id = message["connection_id"]

        # HACK: we need a better way to pull values out of presentations
        revealed_attrs = message["presentation"]["requested_proof"]["revealed_attrs"]
        for revealed_attr in revealed_attrs.values():
            email = revealed_attr["raw"]

        attendee = Attendee(connection_id=connection_id, email=email)

        try:
            attendee.save()
        except IntegrityError:
            logger.warn(f"Duplicate email '{email}', ignoring.")
            return HttpResponse()
        
        return HttpResponse()

    # Handle cred request, issue cred
    if topic == "credentials" and message["state"] == "request_received":
        credential_exchange_id = message["credential_exchange_id"]
        connection_id = message["connection_id"]

        logger.info(
            "Sending credential issue for credential exchange "
            + f"{credential_exchange_id} and connection {connection_id}"
        )

        attendee = get_object_or_404(Attendee, connection_id=connection_id)
        request_body = {
            "credential_values": {
                "email": attendee.email,
                "full_name": attendee.full_name,
                "time": str(datetime.utcnow()),
            }
        }

        response = requests.post(
            f"{AGENT_URL}/credential_exchange/{credential_exchange_id}/issue",
            json=request_body,
        )

        return HttpResponse()

    return HttpResponse()
