# coding=utf-8
from __future__ import absolute_import

from uuid import uuid4
import sys
import os
import subprocess
import requests
import json

# AUTHENTISE_CLIENT_PATH = 'authentise-streaming-client'
AUTHENTISE_CLIENT_PATH = '/Applications/Authentise.app/Contents/Resources/streamus-client'
AUTHENTISE_PRINT_API = 'https://print.dev-auth.com'
AUTHENTISE_USER_API = 'https://users.dev-auth.com'

def run_client(arg, logger):
    command = (
        AUTHENTISE_CLIENT_PATH, '--logging-level', 'error',
        '-c',
        '/Applications/Authentise.app/Contents/Resources/client.conf',
        arg,
    )

    try:
        return subprocess.check_output(command).strip()
        #return subprocess.check_output((AUTHENTISE_CLIENT_PATH, '--logging-level', 'error') + arg).strip()
    except Exception as e:
        logger.error("Error running client command `%s` using parameters: %s", e, args)
        return

def claim_node(node_uuid, api_key, api_secret, logger):
    if not node_uuid:
        logger.error("No node uuid available to claim")
        return False

    if not api_key:
        logger.error("No API Key available to claim node")
        return False

    if not api_secret:
        logger.error("No API secret available to claim node")
        return False

    claim_code = run_client('--connection-code', logger)
    if claim_code:
        logger.info("Got claim code: %s", claim_code)
    else:
        logger.error("Could not get a claim code from Authentise")
        return False

    url = "{}/client/claim/{}/".format(AUTHENTISE_PRINT_API, claim_code)
    response = requests.put(url, auth=(api_key, api_secret))
    logger.info("Response from - POST %s - %s - %s", url, response.status_code, response.text)

    if response.ok:
        logger.info("Claimed node: %s", node_uuid)
        return True

    logger.error("Could not use claim code %s for node %s", claim_code, node_uuid)
    return False

def login(username, password, logger):
    url = '{}/sessions/'.format(AUTHENTISE_USER_API)
    payload = {
        "username": username,
        "password": password,
    }
    response = requests.post(url, json=payload)
    logger.info("Response from - POST %s - %s - %s", url, response.status_code, response.text)

    if response.ok:
        logger.info("Successfully logged in to user service: %s", username)
        return response.status_code, json.loads(response.text), response.cookies
    elif response.status_code == 400:
        logger.warning("Failed to log in to user service for user %s", username)
    else:
        logger.error("Error logging in to user service for user %s", username)

    return response.status_code, json.loads(response.text), None

def create_api_token(cookies, logger):
    if not cookies:
        logger.warning("Cannot create api token without a valid session cookie")
        return None, None

    url = '{}/api_tokens/'.format(AUTHENTISE_USER_API)
    payload = { "name": "Octoprint Token - {}".format(str(uuid4())) }
    response = requests.post(url, json=payload, cookies=cookies)
    logger.info("Response from - POST %s - %s - %s", url, response.status_code, response.text)

    if response.ok:
        logger.info("Successfully created api token: %s", response.text)
    elif response.status_code == 400:
        logger.warning("Failed to create api token for user %s", username)
    else:
        logger.error("Error creating api token for user")

    return response.status_code, json.loads(response.text)