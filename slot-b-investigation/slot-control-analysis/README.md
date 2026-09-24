# Slot Control Investigation

This directory tracks investigation into Ulefone GQ5012BF1 slot handling.

Finding:

The phone has A/B partition characteristics but does not support standard fastboot A/B commands.

The normal Android boot path remains slot A.

Research direction:

Find MediaTek-specific slot selection mechanism before modifying any boot metadata.
