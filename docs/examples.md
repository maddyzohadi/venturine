# Examples

Every example here uses a hypothetical business and illustrative numbers. None of it is real market data, and the prompts are starting points, not guaranteed scripts. Claude's wording will vary, so the calculator outputs below are the only literal outputs shown.

## 1. Validate an idea

**Prompt**

```text
Use the Venturine idea-validator skill on this hypothetical idea: a US business
selling niche AI automation workflow kits to small accounting firms, with a
$15,000 startup budget. State your assumptions and ask only for facts that
change the answer.
```

**What to look for**

- Assumptions listed explicitly, separated from facts.
- Claims about demand or competitors marked with an evidence label (see [evidence terminology](evidence-terminology.md)), and "unverified" where no source was examined.
- Top risks, each with a validation experiment you could run cheaply.
- One of four decisions, with its limits stated.
- No invented market statistics or citations. If you see a statistic with no source, treat it as unverified and ask where it came from.

## 2. Break-even that includes acquisition cost

**Scenario.** One-time purchase kit priced at $149, with $19.37 variable cost per sale (payment fees and support), $1,500 of monthly fixed costs that exclude marketing, and an assumed $60 customer acquisition cost.

**Prompt**

```text
Use the Venturine unit-economics skill and calculator. Compare break-even with
and without acquisition cost for: price $149, variable cost $19.37, monthly
fixed costs $1,500 excluding marketing, CAC $60 (an assumption).
```

**Calculator, acquisition left out**

```bash
python3 scripts/calculate.py break-even 1500 149 19.37
```

```json
{
  "engine": "venturine",
  "version": "0.2.1",
  "operation": "break-even",
  "inputs": ["1500", "149", "19.37"],
  "result": 12,
  "status": "calculated",
  "acquisition_included": false,
  "warning": "Operating break-even only. Customer acquisition costs are not included; use break-even-loaded when acquisition spending is relevant."
}
```

**Calculator, acquisition included**

```bash
python3 scripts/calculate.py break-even-loaded 1500 149 19.37 60
```

```json
{
  "engine": "venturine",
  "version": "0.2.1",
  "operation": "break-even-loaded",
  "inputs": ["1500", "149", "19.37", "60"],
  "result": {
    "break_even_units": 22,
    "loaded_contribution_per_unit": "69.63",
    "acquisition_included": true,
    "assumes_one_purchase_per_customer": true,
    "fixed_costs_exclude_acquisition": true
  },
  "status": "calculated"
}
```

(The JSON is shown on fewer lines than the tool prints it.)

**Reading it.** Without acquisition cost the business appears to break even at 12 sales a month, but with a $60 CAC it needs 22. The $60 is an assumption, so the answer is only as good as that input. Test it with a small ad experiment before relying on it.

**Do not double count.** If you instead model a fixed $600 monthly ad budget, add it to the fixed costs and set CAC to 0. Do not do both.

## 3. Operating profit with explicit cost categories

**Scenario.** One month with 100 sales at $149, which is $14,900 revenue, $1,937 of variable operating cost, $6,000 of acquisition spend and $1,500 of fixed operating cost.

```bash
python3 scripts/calculate.py operating-profit 14900 0 1937 6000 1500
```

Result: `total_costs` of `9437.00` and `operating_profit` of `5463.00`. The output lists each category and says what is excluded: taxes, interest, capital expenditures, and owner compensation unless you entered it as a fixed operating cost.

The four categories are mutually exclusive, so each cost goes in exactly one: cost of goods sold, variable operating, acquisition, or fixed operating. All five inputs are required, so pass `0` for an empty category.

Decimal results are printed in plain notation and rounded for display (here the operating margin is `36.66`), and the output includes a `display_rounding` note. The underlying arithmetic is exact, so rounding in the output does not change the break-even or profit logic.

## 4. Ask the auditor to challenge the result

```text
Ask the evidence-auditor agent to independently review the claims,
assumptions and calculations in this analysis, and list what remains
unverified or unsupported.
```

Expect a list of claims with their evidence status. If the agent could not run, it should say no audit took place rather than implying one did.

## 5. Intake, handoff, audit and red team (unreleased)

These components are built but not yet in a release. The scenario is hypothetical: a weekend market stall that sells sourdough loaves.

**Start with an intake.**

```text
Use venture-intake on this hypothetical idea: a weekend market stall selling
sourdough loaves for about $8 each, $1,500 to start. Ask me only what changes
the analysis, label what I tell you, and give me a handoff.
```

Expect a venture profile, an input ledger where what you said is `FOUNDER_PROVIDED` and what you guessed is `ASSUMPTION`, a prioritized list of missing information (for example, fixed costs and how many loaves you could sell), and a readiness check for each skill. The skill does not research or calculate. It ends with a `venturine-handoff/v1` JSON block.

**Pass the handoff on.** Paste the handoff into your next request, for example to `unit-economics`, so the labeled inputs travel with it. A complete hypothetical handoff, with a calculation, is in [handoff-v1.example.json](handoff-v1.example.json), and the format is described in [handoff-v1.md](handoff-v1.md). To check one, save it as a `.json` file and run the validator by file path:

```bash
python3 scripts/validate_handoff.py docs/handoff-v1.example.json
```

The result lists `valid`, `errors` and `warnings`. A valid handoff is well formed and consistent. It is not verified.

**Audit before you commit.**

```text
Use evidence-audit on the analysis above before I decide. Run the
evidence-auditor, tell me what changed, and say whether the result is
AUDITED or PRELIMINARY.
```

The skill prepares the claims, sources and calculations, asks the `evidence-auditor` agent for an independent pass, and reports corrections and remaining gaps. If the auditor could not run, it says so and marks the result PRELIMINARY. For a decision to commit money or time it may offer a red-team review.

**Challenge a conclusion.**

```text
Ask the red-team-reviewer agent for the strongest case against this
recommendation, a premortem, and any evidence that contradicts it.
```

Expect a verdict of `STANDS`, `STANDS WITH WEAKNESSES`, `DOES NOT STAND` or `NOT ENOUGH INFORMATION`, with ranked failure paths, assumption stress tests and a statement of what evidence would change its mind. It does not invent counter-evidence, and finding none is not proof that the claim is right.

## Tips

- Name the skill in your prompt so it is used.
- Give your own numbers where you have them, and label guesses as assumptions.
- Never include real customer data, credentials or trade secrets.
- Treat every output as a hypothesis generator, not a verdict.
