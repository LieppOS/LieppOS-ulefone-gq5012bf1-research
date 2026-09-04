# Stock KMI requirement split

- raw import records: 26111
- unique imported symbols: 5207
- CRC-conflicting imported symbols: 0
- stock-module-provided symbols: 2261
- kernel/builtin-required symbols: 2946

## Published Nothing symbol-list coverage

- kernel_base: 2 symbols (`kernel/android/abi_gki_aarch64`)
- kernel_mtk: 3411 symbols (`kernel/android/abi_gki_aarch64_mtk`)
- kernel_nothing: 213 symbols (`kernel/android/abi_gki_aarch64_nothing`)
- device_base: 2 symbols (`device_modules/android/abi_gki_aarch64`)
- device_mtk: 2550 symbols (`device_modules/android/abi_gki_aarch64_mtk`)

- device MTK union (device_base + device_mtk): 2550
- kernel Nothing union (kernel_base + kernel_mtk + kernel_nothing): 3542
- all published-list union: 3721

## Stock kernel/builtin requirement coverage by symbol name

- required symbols: 2946
- covered by device MTK union: 2139
- missing from device MTK union: 807
- covered by kernel Nothing union: 2913
- missing from kernel Nothing union: 33
- covered by any published Nothing list: 2913
- missing from all published Nothing lists: 33

Name coverage does not prove CRC compatibility. A Nothing build's `Module.symvers` (or equivalent built artifacts) is required for an exact CRC-to-CRC comparison.
