# Rotación custom de la llave de firma JWT. setSecret es no-op
# porque no hay sistema externo que reconfigurar.
from __future__ import annotations

import json
import logging
import os

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def _client():
    return boto3.client(
        "secretsmanager",
        endpoint_url=os.environ.get("SECRETS_MANAGER_ENDPOINT"),
    )


def lambda_handler(event, context):
    arn = event["SecretId"]
    token = event["ClientRequestToken"]
    step = event["Step"]

    client = _client()
    metadata = client.describe_secret(SecretId=arn)
    if not metadata.get("RotationEnabled", False):
        raise ValueError("Rotacion no habilitada")
    versions = metadata["VersionIdsToStages"]
    if token not in versions:
        raise ValueError("ClientRequestToken desconocido")
    if "AWSCURRENT" in versions[token]:
        return
    if "AWSPENDING" not in versions[token]:
        raise ValueError("Token no esta en AWSPENDING")

    if step == "createSecret":
        _create(client, arn, token)
    elif step == "setSecret":
        logger.info("setSecret: no-op")
    elif step == "testSecret":
        _test(client, arn, token)
    elif step == "finishSecret":
        _finish(client, arn, token)
    else:
        raise ValueError(f"Paso desconocido: {step}")


def _create(client, arn, token):
    try:
        client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")
        return
    except client.exceptions.ResourceNotFoundException:
        pass

    current = json.loads(
        client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")["SecretString"]
    )
    new_key = client.get_random_password(
        PasswordLength=64, ExcludePunctuation=True, IncludeSpace=False
    )["RandomPassword"]
    new_secret = {"SECRET_KEY": new_key, "ALGORITHM": current.get("ALGORITHM", "HS256")}

    client.put_secret_value(
        SecretId=arn,
        ClientRequestToken=token,
        SecretString=json.dumps(new_secret),
        VersionStages=["AWSPENDING"],
    )


def _test(client, arn, token):
    raw = client.get_secret_value(SecretId=arn, VersionId=token, VersionStage="AWSPENDING")
    payload = json.loads(raw["SecretString"])
    assert payload.get("SECRET_KEY"), "SECRET_KEY ausente"
    assert payload.get("ALGORITHM"), "ALGORITHM ausente"


def _finish(client, arn, token):
    metadata = client.describe_secret(SecretId=arn)
    current_version = None
    for v, stages in metadata["VersionIdsToStages"].items():
        if "AWSCURRENT" in stages:
            if v == token:
                return
            current_version = v
            break
    client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
