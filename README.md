# Ahimsa in Agentic AI: companion programs

Companion code for **Ahimsa in Agentic AI: Algorithmic Non-Violence and the Architecture of Compassionate Code** by Dr. Sri Amit Ray (Compassionate AI Lab, 2026). ISBN 978-81-69641-29-6 (First Edition, 2026).

Every number printed in the book's worked examples is produced by `models_ahimsa_in_agentic_ai.py` and checked by `test_models.py`. The reference simulation of the book's Appendix D, an individual-agent execution gate, is in `safety_runtime.py` with 39 acceptance tests in `test_runtime.py`.

## Run

Python 3.10 or newer; standard library only.

```
python models_ahimsa_in_agentic_ai.py      # prints every worked-example result
python -m unittest test_models.py         # 24 tests: book numbers + gate contract tests
python -m unittest test_runtime.py        # 39 tests: Appendix D reference simulation
```

`expected_output.txt` holds the output of the first command for comparison.

## Files

| File | Contents |
|---|---|
| `models_ahimsa_in_agentic_ai.py` | one function per worked example (Chapters 1-18, Appendix D) and the componentwise gate `within_ceilings` |
| `test_models.py` | checks every printed number; contract tests: non-finite, negative or missing values never pass, a missing or out-of-range confidence takes the protective branch, the tool filter never permits a breach, floors cannot be removed by reweighting |
| `safety_runtime.py` | deterministic, single-process model of an execution gateway: typed actions, ceilings, consent, evidence age and version, expiring authorizations bound to an intent digest, idempotent commit |
| `test_runtime.py` | 39 acceptance tests for the gateway and the joint coordinator, including NaN and infinite values, invalid configuration, stale evidence, changed arguments, policy changes and duplicate requests |

The inputs are small illustrative values chosen so that each step can be checked by hand. Replace them with values measured in your own deployment before using any function for planning. The runtime has no live messaging, credentials, records or clinical inference.

The companion volume, *No-Harm Principles in AI Architectures: Ahimsa-Driven Multi-Agent AI Systems* (ISBN 978-81-69641-30-2), extends the same approach to systems of many agents: <https://github.com/compassionate-ai-lab/no-harm-principles>.

## Related published books

1. Ray, Amit. *Human-Centered Compassionate AI*. Compassionate AI Lab, 2026. ISBN: 978-8169641050.
2. Ray, Amit. *Compassionate Artificial Intelligence: Frameworks and Algorithms*. Compassionate AI Lab, 2018. ISBN: 978-9382123460.
3. Ray, Amit. *Compassionate Artificial Superintelligence AI 5.0*. Compassionate AI Lab, 2018. ISBN: 978-9382123446.
4. Ray, Sri Amit. *Compassionate Superintelligence: Architecture, Alignment, and the Future of Intelligence That Cares*. 2nd ed., Compassionate AI Lab, 2026. ISBN 978-81-69641-22-7.
5. Ray, Sri Amit. *No-Harm Principles in AI Architectures: Ahimsa-Driven Multi-Agent AI Systems*. Compassionate AI Lab, 2026. ISBN 978-81-69641-30-2.

## Cite as

Ray, Sri Amit. *Ahimsa in Agentic AI: Algorithmic Non-Violence and the Architecture of Compassionate Code*. Compassionate AI Lab, 2026. ISBN 978-81-69641-29-6.

## Licence

MIT, see `LICENSE`.
