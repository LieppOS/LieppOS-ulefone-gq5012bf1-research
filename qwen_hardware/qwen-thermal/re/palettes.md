# Palettes

The APK contains eleven 768-byte LUTs: Aurora, Black Hot, Glory Hot, Ironbow, Jungle, Medical, Night, Rainbow, Red Hot, Sepia and White Hot. 768 bytes is exactly 256 RGB888 entries. Black Hot is a descending near-monochrome RGB triplet ramp, confirming layout.

`libcolormapping.so` exports RGB/RGBA mapping, standalone file-based mapping, temperature clamp, gray/stretch and clamp/stretch variants, plus `nativeColorMappingGetRGBTable`. This allows fixed or scene-derived min/max, grayscale, clamped temperature windows and external LUTs.

Pseudo-color command enums also exist for module-side coloring. The safer architecture is host-side rendering from the corrected uint16 plane: it preserves radiometry, permits deterministic range locking and avoids coupling measurement to AGC/palette output.
