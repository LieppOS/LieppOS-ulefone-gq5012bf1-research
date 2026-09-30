# Safe LieppOS integration design

## Components
- `thermal-powerd` privileged broker owns the two sysfs switches and serialized lifecycle.
- `thermal-usbd` opens only the measured internal thermal USB device, negotiates UVC and performs allowlisted read-only/vendor-safe controls.
- unprivileged UI receives shared-memory image and corrected radiometric planes plus typed metadata.
- calibration vault service performs read-only backup and hash verification; no normal UI write path.

## State machine
`OFF -> ROUTING -> RAILS_ON -> WAIT_ENUM -> USB_OPEN -> STREAMING -> STOPPING -> USB_RELEASED -> RAILS_OFF`. Errors always cancel transfers/release interfaces before power-off. Only one owner; suspend, detach and app death trigger cleanup.

## MVP
Reuse the stock signed SDK/app, preserve package identity, add launcher/system integration and ensure vendor sepolicy/mounts survive GSI. Validate chip ID `0x4c59`, calibration flag/readback and output temperature against stock.

## Independent implementation
After passive descriptor/frame capture, implement UVC stream parsing and the verified vdcmd subset. Render palettes host-side; expose point/line/rectangle/circle/global measurements; support emissivity, distance, humidity, ambient/reflected temperature with sane ranges. Keep manual FFC behind an expert control and omit firmware/flash/calibration writes.

## Validation
Compare the same blackbody/reference targets and scenes to stock across temperatures, gain transitions and FFC events. Reject integration if calibration hashes differ, frame metadata is inconsistent or error exceeds the established stock baseline.
