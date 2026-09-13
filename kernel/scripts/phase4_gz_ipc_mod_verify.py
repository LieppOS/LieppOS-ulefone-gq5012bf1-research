#!/usr/bin/env python3
"""Fail-closed verifier for the GQ5012BF1 gz_ipc_mod closure."""
from phase4_gz_transport_verify_common import verify_module

if __name__ == "__main__":
    raise SystemExit(verify_module("gz_ipc_mod").finish())
