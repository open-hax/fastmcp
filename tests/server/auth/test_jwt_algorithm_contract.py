# OpenHAX modification notice (2026-10-29): compatibility adaptation.
# OpenHAX-authored changes: LGPL-3.0-or-later; upstream portions retain Apache-2.0.
# See NOTICE and LICENSING.md for provenance and the modification boundary.
"""Public JWTVerifier contract checks for the compatibility fork."""

import time
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from joserfc import jwk, jwt
from pytest_httpx import HTTPXMock

from fastmcp.server.auth.providers.jwt import JWTVerifier

ALGORITHMS = [
    "HS256",
    "HS384",
    "HS512",
    "RS256",
    "RS384",
    "RS512",
    "ES256",
    "ES384",
    "ES512",
    "PS256",
    "PS384",
    "PS512",
]


def material(algorithm: str) -> tuple[Any, str]:
    if algorithm.startswith("HS"):
        secret = "candidate-contract-key-" * 6
        return jwk.import_key(secret, "oct"), secret
    if algorithm.startswith("ES"):
        curve = {"ES256": ec.SECP256R1, "ES384": ec.SECP384R1, "ES512": ec.SECP521R1}[
            algorithm
        ]()
        key = ec.generate_private_key(curve)
        family = "EC"
    else:
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        family = "RSA"
    private = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    public = (
        key.public_key()
        .public_bytes(
            serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
        )
        .decode()
    )
    return jwk.import_key(private, family), public


def claims(**delta: Any) -> dict[str, Any]:
    return {
        "iss": "https://issuer.example.invalid",
        "aud": "contract-api",
        "sub": "owner-contract",
        "client_id": "contract-client",
        "scope": "openid",
        "exp": int(time.time()) + 300,
        **delta,
    }


def token(
    algorithm: str,
    key: Any,
    payload: dict[str, Any] | None = None,
    kid: str | None = None,
) -> str:
    return jwt.encode(
        {"alg": algorithm, **({"kid": kid} if kid else {})},
        payload or claims(),
        key,
        algorithms=[algorithm],
    )


@pytest.mark.parametrize("algorithm", ALGORITHMS)
async def test_advertised_algorithm_verifies_and_rejects_wrong_signature_and_claims(
    algorithm: str,
) -> None:
    private, public = material(algorithm)
    verifier = JWTVerifier(
        public_key=public,
        issuer="https://issuer.example.invalid",
        audience="contract-api",
        algorithm=algorithm,
        required_scopes=["openid"],
    )
    accepted = await verifier.load_access_token(token(algorithm, private))
    assert accepted is not None
    assert accepted.client_id == "contract-client"
    assert accepted.scopes == ["openid"]
    wrong, _ = material(algorithm)
    if algorithm.startswith("HS"):
        wrong = jwk.import_key("independent-wrong-key-" * 6, "oct")
    assert await verifier.load_access_token(token(algorithm, wrong)) is None
    assert (
        await verifier.load_access_token(
            token(algorithm, private, claims(iss="https://wrong.example.invalid"))
        )
        is None
    )
    assert (
        await verifier.load_access_token(
            token(algorithm, private, claims(aud="wrong-api"))
        )
        is None
    )
    assert (
        await verifier.load_access_token(
            token(algorithm, private, claims(exp=int(time.time()) - 60))
        )
        is None
    )


async def test_jwks_cached_key_then_new_kid_fetches_rotation(
    httpx_mock: HTTPXMock,
) -> None:
    first, _ = material("RS256")
    second, _ = material("RS256")

    def public(key: Any, kid: str) -> dict[str, Any]:
        return {**key.as_dict(private=False), "kid": kid, "use": "sig", "alg": "RS256"}

    uri = "https://issuer.example.invalid/jwks"
    httpx_mock.add_response(url=uri, json={"keys": [public(first, "first")]})
    httpx_mock.add_response(url=uri, json={"keys": [public(second, "second")]})
    verifier = JWTVerifier(
        jwks_uri=uri,
        issuer="https://issuer.example.invalid",
        audience="contract-api",
        algorithm="RS256",
    )
    assert (
        await verifier.load_access_token(token("RS256", first, kid="first")) is not None
    )
    assert (
        await verifier.load_access_token(token("RS256", first, kid="first")) is not None
    )
    assert len(httpx_mock.get_requests()) == 1
    assert (
        await verifier.load_access_token(token("RS256", second, kid="second"))
        is not None
    )
    assert len(httpx_mock.get_requests()) == 2
