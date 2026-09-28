# Fonts, media, and WebView

## Fonts

The final product retains 209 font files totaling 89,783,020 bytes:

| Location/family | Bytes | Decision |
|---|---:|---|
| `/system/fonts` (208 files) | 85785872 | KEEP |
| `NotoSansCJK-Regular.ttc` | 32355424 | KEEP—CJK sans coverage |
| `NotoSerifCJK-Regular.ttc` | 26273008 | KEEP—CJK serif coverage |
| `NotoColorEmoji.ttf` | 2992136 | KEEP—emoji |
| `NotoColorEmojiFlags.ttf` | 872756 | KEEP—flag emoji |
| `/product/fonts/GoogleSansFlex-Regular.ttf` | 3997148 | KEEP—Lineage UI family |

The board uses the same `SMALLER_FONT_FOOTPRINT` and
`MINIMAL_FONT_FOOTPRINT` flags as the successfully measured generic arm64
reference. Even under those flags the build retains broad Noto script coverage.
No language family was randomly removed. The two CJK collections account for
58,628,432 bytes, but trimming them requires an explicit supported-language
policy and is not justified after fit succeeded.

## Media

The final product retains 39,465,716 bytes of ringtone/alarm/notification
content and 1,979,221 bytes of light/dark boot animation files. The audio set
includes normal AOSP, classic Lineage, and Plasma choices. It is not required
for boot, but it provides normal phone behavior and the product already has
12.281% headroom, so no catalog was removed.

No demo/sample media was found in the frozen reference. Wallpapers are mainly
packaged applications (`Backgrounds`, ThemePicker/live-wallpaper support) and
are listed in `OPTIONAL-PACKAGES.tsv`.

## WebView

Exactly one WebView provider exists:

```text
/product/app/webview/webview.apk  267276869 bytes
package                           com.android.webview
```

Supporting platform libraries total about 2.3 MB. There is no Trichrome,
Chrome, second provider, or debug WebView APK. Both 32-bit and 64-bit support
must remain because the captured vendor has ELF32 components and the product
supports 32-bit apps. WebView was retained unchanged.
