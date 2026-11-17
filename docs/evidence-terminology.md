# Evidence Terminology

Every Venturine skill and agent uses the same labels. This page is the reference. Skills and agents repeat the labels so they work without this file, and a test checks that they agree.

## The labels

| Label | Meaning | Use it when |
|---|---|---|
| `VERIFIED` | A fact directly supported by an accessible, relevant source that was actually examined in this session. | You read the source and it says what the claim says, for the right place and period. |
| `PARTIALLY_SUPPORTED` | Some evidence exists, but the claim is broader, newer, or from a different scope than the evidence. | The source supports part of the claim, or only a search summary was seen. |
| `UNVERIFIED` | A specific claim was made, but no examined source confirms it. | A founder, competitor or page asserts something you could not check. |
| `CONTRADICTED` | Credible evidence conflicts with the claim. | A reliable source says otherwise. State both. |
| `FOUNDER_PROVIDED` | An input the founder supplied. Not checked. | Prices, volumes and costs given in the conversation. |
| `DERIVED` | Calculated from documented inputs. It is only as reliable as those inputs. | The result of a formula or a calculator run. |
| `ASSUMPTION` | A hypothetical value or planning hypothesis, not an established fact. | You chose a value to make the model run. |
| `UNKNOWN` | Missing or not supported by enough information. | A needed input does not exist yet. Do not fill it in. |
| `NOT_APPLICABLE` | An opinion, recommendation or decision rather than a checkable fact. Used by the auditor. | The statement cannot be true or false. |

The four distinctions that matter most:

1. **Verified facts** are `VERIFIED`.
2. **Partially supported claims** are `PARTIALLY_SUPPORTED`.
3. **Assumptions** are `ASSUMPTION`, and `FOUNDER_PROVIDED` inputs stay separate from facts until checked.
4. **Unknown information** is `UNKNOWN` (nothing is known) or `UNVERIFIED` (a claim exists, but nothing confirms it).

## Rules

- Never label a claim `VERIFIED` unless the supporting source was examined. A search snippet, a competitor's own marketing page, or a third-party comparison site does not make a claim verified.
- A calculation can be `DERIVED` and correct while its inputs are `ASSUMPTION`. A correct calculation does not verify its inputs.
- "Independent review" means the `evidence-auditor` agent was actually run. It is another AI pass over the work, not a human audit or a guarantee. If it did not run, say no audit took place.
- Record the source title, URL, publication date and access date for every `VERIFIED` or `PARTIALLY_SUPPORTED` claim.
- Do not invent sources, quotes, statistics or calculator output.
