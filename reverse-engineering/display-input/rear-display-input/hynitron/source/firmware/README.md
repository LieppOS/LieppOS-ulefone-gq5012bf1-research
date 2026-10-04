# Private firmware boundary

This directory intentionally contains no controller firmware bytes. Run
`../extract-firmware.py /path/to/stock/hynitron.ko` locally to regenerate the
two ignored headers required for parity builds. The script verifies the
published size and SHA-256 boundaries before writing anything.
