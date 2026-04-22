# Rotación single-user PostgreSQL en Secrets Manager
# (createSecret/setSecret/testSecret/finishSecret).
from __future__ import annotations

import json
import logging
import os

import boto3
import pg8000  # Python puro, no requiere compilar para el paquete Lambda

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
        raise ValueError(f"Rotacion no habilitada en {arn}")

    versions = metadata["VersionIdsToStages"]
    if token not in versions:
        raise ValueError(f"Version {token} no existe en {arn}")
    if "AWSCURRENT" in versions[token]:
        logger.info("Version %s ya es AWSCURRENT, nada que hacer", token)
        return
    if "AWSPENDING" not in versions[token]:
        raise ValueError(f"Version {token} no esta en AWSPENDING")

    if step == "createSecret":
        create_secret(client, arn, token)
    elif step == "setSecret":
        set_secret(client, arn, token)
    elif step == "testSecret":
        test_secret(client, arn, token)
    elif step == "finishSecret":
        finish_secret(client, arn, token)
    else:
        raise ValueError(f"Paso desconocido: {step}")


def _get_secret_dict(client, arn, stage, token=None):
    kwargs = {"SecretId": arn, "VersionStage": stage}
    if token:
        kwargs["VersionId"] = token
    resp = client.get_secret_value(**kwargs)
    return json.loads(resp["SecretString"])


def create_secret(client, arn, token):
    current = _get_secret_dict(client, arn, "AWSCURRENT")
    try:
        _get_secret_dict(client, arn, "AWSPENDING", token)
        logger.info("AWSPENDING ya existe, reusando")
        return
    except client.exceptions.ResourceNotFoundException:
        pass

    new_password = client.get_random_password(
        PasswordLength=32, ExcludeCharacters="/@\"'\\ "
    )["RandomPassword"]
    new_secret = dict(current)
    new_secret["password"] = new_password

    client.put_secret_value(
        SecretId=arn,
        ClientRequestToken=token,
        SecretString=json.dumps(new_secret),
        VersionStages=["AWSPENDING"],
    )


def _connect(creds):
    return pg8000.connect(
        user=creds["username"],
        password=creds["password"],
        host=creds["host"],
        port=int(creds["port"]),
        database=creds["dbname"],
        ssl_context=True,
    )


def set_secret(client, arn, token):
    pending = _get_secret_dict(client, arn, "AWSPENDING", token)
    current = _get_secret_dict(client, arn, "AWSCURRENT")

    # Aplica la nueva contraseña al usuario único (single-user rotation).
    conn = _connect(current)
    try:
        with conn.cursor() as cur:
            cur.execute(
                f"ALTER USER {pending['username']} WITH PASSWORD %s", (pending["password"],)
            )
        conn.commit()
    finally:
        conn.close()
    logger.info("Password actualizado para %s", pending["username"])


def test_secret(client, arn, token):
    pending = _get_secret_dict(client, arn, "AWSPENDING", token)
    conn = _connect(pending)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()
    finally:
        conn.close()
    logger.info("Nuevo password valida conexion OK")


def finish_secret(client, arn, token):
    metadata = client.describe_secret(SecretId=arn)
    current_version = None
    for version, stages in metadata["VersionIdsToStages"].items():
        if "AWSCURRENT" in stages:
            if version == token:
                return
            current_version = version
            break

    client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
    logger.info("AWSCURRENT movido a %s", token)
