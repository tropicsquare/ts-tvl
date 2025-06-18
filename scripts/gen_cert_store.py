#!/usr/bin/env python3
import argparse
import pathlib
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.primitives.serialization import Encoding
import base64

def is_file_and_exists(arg) -> pathlib.Path:
    p = pathlib.Path(arg)
    if p.is_file() and p.exists():
        return p
    raise argparse.ArgumentTypeError(f"Argument is not a valid file: {arg}.")

def load_cert(cert: pathlib.Path) -> bytes:
    """Load x509 certificate and convert to ASN.1 DER-TLV."""
    if cert.suffix == ".pem":
        return load_pem_x509_certificate(cert.read_bytes()).public_bytes(
            Encoding.DER
        )
    if cert.suffix == ".der":
        return cert.read_bytes()
    raise argparse.ArgumentTypeError("Certificate not in DER nor PEM format.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "gen_cert_store.py",
        description = "Creates TROPIC01 Device Certificate Store from input certificates and encodes it as base64."
    )

    parser.add_argument(
        "--store-version",
        help="Certificate store version (from the Certificate Store Header).",
        type=int,
        default=1
    )

    parser.add_argument(
        "--certs",
        help="Files with the certificates in PEM or DER format.",
        type=is_file_and_exists,
        nargs="+",
        required=True
    )

    args = parser.parse_args()

    cert_store_header = args.store_version.to_bytes(1, 'big')
    cert_store_header += len(args.certs).to_bytes(1, 'big')
    cert_store_body = b''
    for c in args.certs:
        cert_der = load_cert(c)
        cert_store_header += len(cert_der).to_bytes(2, 'big')
        cert_store_body += cert_der

    
    output = base64.b64encode(cert_store_header+cert_store_body)
    print(f"TROPIC01 Device Certificate Store:\n{output}")