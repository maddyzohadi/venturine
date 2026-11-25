# Rejected by the calculator (exit code 2)

Command:

```bash
python3 scripts/calculate.py break-even-loaded 1200 49 9 150
```

Verbatim output:

```text
Exit code 2
usage: calculate.py [-h]
                    {break-even,break-even-loaded,cac,contribution-margin,gross-margin,operating-profit,revenue,runway,subscription-ltv}
                    [values ...]
calculate.py: error: Break-even requires positive contribution margin after customer acquisition cost.
```
