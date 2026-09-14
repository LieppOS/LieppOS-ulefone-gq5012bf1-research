# GQ5012BF1 tkcore Phase 3E — function-set acceptance

This is a name-set comparison of the project-defined comparable ELF `STT_FUNC` population, not a count-only claim.

| Measure | Phase 3D | Phase 3E |
|---|---:|---:|
| stock function population | 122 | 122 |
| stock names present | 117 | **122** |
| missing stock names | 5 | **0** |
| island-only names | 0 | **0** |
| raw-byte-identical bodies | 47 | **54** |

```text
STOCK_MINUS_ISLAND = []
ISLAND_MINUS_STOCK = []
```

Exactly the five RED targets were added. No function was removed and no compiler-generated island-only helper appeared. All five new bodies are raw-byte identical to stock; repaired `init_module` and `cleanup_module` are also newly byte-identical, explaining 47→54.

Result: **122/122 SET EQUALITY PASS**.
