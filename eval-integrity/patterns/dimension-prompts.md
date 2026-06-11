# Dimension Audit Briefs — eval-integrity

Seven paste-ready briefs, one per audit dimension. Fill the bracketed slots before spawning. Spawn all chosen subagents in a single tool-call batch so they run in parallel.

Every brief:
- Names the repo path and HEAD SHA.
- Carries grep patterns as *starting points* — the auditor must read the hits, not pattern-match blindly.
- States the severity rule for its dimension (which gaps are INVALIDATING vs HARDENING).
- Returns the same report contract: rating + evidence (`file:line` or "searched X,Y,Z — nothing") + concrete fix.

Shared header for every brief:

```
Repo: [absolute path]
HEAD commit: [sha]
Scoring entry point(s): [from Step 1]
Results / leaderboard dir: [from Step 1]
Methodology / governance docs: [from Step 1]

Rate this dimension PRESENT (implemented AND enforced in code or a test),
PARTIAL (documented or half-built, not enforced), or ABSENT (no evidence).
Evidence is mandatory: a file:line for each claim, or an explicit list of
what you searched and found nothing. A rating with no evidence is rejected.

Report (cap ~400 words):
1. Rating: PRESENT | PARTIAL | ABSENT.
2. Evidence: file:line for each sub-check below.
3. Severity of any gap: INVALIDATING (a reviewer can throw out a published
   number) or HARDENING (weakens credibility, doesn't invalidate).
4. Fix: a concrete change per gap — file to add, guard to write, test to add.
   Never "consider improving"; never "add more scenarios" unless low N is the
   actual finding.
```

---

## 1. Pre-registration

```
[shared header]

You audit PRE-REGISTRATION. The question: is the run's definition fixed on disk
BEFORE any result exists, so the maintainer cannot re-run until the numbers look
good, or silently retract an unflattering run?

Sub-checks:
- Is there a pre-registration artifact (a file written before the eval loop)
  recording: models under test, the EXACT corpus (ideally a sha256 over the
  canonical serialized scenario set, not just per-file hashes), the judge panel,
  seeds, and temperatures?
- Is it written BEFORE the first model/judge call — and is that ordering enforced
  by a test, not just by where the call happens to sit in the code?
- Is there a no-silent-retraction / append-only-correction policy, and is a
  published run timestamped and self-describing (a manifest linking back to the
  pre-registration by path + hash)?

Grep starting points:
  rg -i "pre.?regist|preregist" .
  rg -n "sha256|hashlib|canonical|sorted_keys|sort_keys" .
  rg -ni "retract|append-only|never deleted|re-run|rerun|immutable" .
  rg -ln "manifest|run_manifest" .

Good looks like: a pre_registration.json written at the top of the run with a
corpus sha256 + scenario index; a test asserting the file exists on disk at the
moment the first model is dispatched; a governance section stating runs are never
silently re-run, corrections are a new dated run. (cot-bench:
eval/pre_registration.py, tests/test_pre_registration.py, docs/governance.md §1,§3.)

Severity: no pre-registration at all, or one written AFTER results, is
INVALIDATING (the run can be cherry-picked). Pre-registration present but no
corpus-level hash (only per-file) is HARDENING.
```

---

## 2. Contamination

```
[shared header]

You audit CONTAMINATION. The question: can a model that helped build the exam sit
for it, and is there a defense against the corpus leaking into future training?

Sub-checks:
- Are corpus/scenario authors barred from being contestants? Is the guard
  FAMILY-AWARE (a different snapshot of a contestant is still that contestant),
  and enforced in CODE (a hard assert at generation), not by convention?
- Is per-scenario authorship recorded (an author_model field stamped at
  generation) and treated as immutable?
- Is the corpus synthetic or scraped? If scraped, is there a contamination check
  against known training sets? If public on GitHub, is there a PRIVATE HOLDOUT
  run alongside the public set, with the public-vs-holdout GAP published per model
  as an overfitting tripwire?

Grep starting points:
  rg -ni "contaminat|author.?model|authorship|assert_author|never a contestant" .
  rg -ni "MODELS_UNDER_TEST|contestant|under_test" .
  rg -ni "holdout|hold-out|held-out" .
  rg -ni "family|prefix|snapshot" eval scripts

Good looks like: assert_author_allowed that blocks generation when the author ID
prefix-matches any contestant; an authorship block per scenario; a holdout pulled
from outside the repo at run time, with a per-model public/holdout/gap row on the
leaderboard. (cot-bench: scripts/generate_data.py assert_author_allowed,
docs/governance.md §4, tests/test_same_lab.py for family-matching.)

Severity: no author-is-contestant guard is INVALIDATING. No holdout when the
corpus is public is INVALIDATING for an overfitting claim, HARDENING otherwise.
Authorship not recorded is HARDENING.
```

---

## 3. Holdout hygiene

```
[shared header]

You audit HOLDOUT HYGIENE. The question: granting that a private holdout exists,
can its CONTENT leak out anywhere?

Sub-checks:
- Are full transcripts / per-evaluation artifacts gitignored, never committable?
- Does CI ever set the holdout dir/env in a PUBLIC workflow? If a workflow uploads
  artifacts or logs, is there an explicit guard REFUSING to run when the holdout
  is configured?
- In the pre-registration, is the holdout recorded as hash + COUNT ONLY — with NO
  scenario IDs and NO per-scenario index (unlike the public set)?
- Do any published outputs (leaderboard.json, latest.csv) carry holdout scenario
  IDs, text, ground truth, or per-scenario scores — or only per-model aggregates?
- Could holdout content surface in an error message or a committed sample?

Grep starting points:
  rg -ni "holdout|HOLDOUT_DIR" .github .gitignore
  rg -n "upload-artifact|actions/upload" .github
  rg -ni "artifacts/|transcripts|traces" .gitignore
  rg -ni "holdout" data scripts eval | rg -ni "id|index|text|ground_truth"

Good looks like: artifacts/ and traces/ gitignored with a comment naming the
holdout-leak reason; a CI step that exits non-zero if COT_BENCH_HOLDOUT_DIR is set
because the artifact upload would publish transcripts; a holdout_set block with
sha256 + n_scenarios only. (cot-bench: .gitignore data/results/artifacts/,
.github/workflows/weekly-eval.yml "Assert no private holdout in CI",
eval/pre_registration.py holdout_set_hash returns hash+count only.)

Severity: holdout reachable via a public CI artifact upload, or holdout IDs in a
published file, is INVALIDATING (the holdout is no longer private). Artifacts not
gitignored is INVALIDATING. No CI guard but holdout is local-only by construction
is HARDENING.
```

---

## 4. Judge validity

```
[shared header]

You audit JUDGE VALIDITY (for LLM-as-judge evals; if there is no LLM judge, say
so and rate N/A). The question: is the judge a trustworthy, pinned, unbiased
measuring instrument?

Sub-checks:
- Is the judge model PINNED to the model the provider ACTUALLY SERVED (a
  resolved_model recorded per call), not just the requested ID? Hosted slugs get
  silently re-pointed; a requested ID alone misses that drift.
- Multi-judge panel? If so, are inter-judge AGREEMENT stats reported, and are they
  CHANCE-CORRECTED (Krippendorff's alpha / kappa), not a raw within-X rate?
- Judge-family-vs-contestant conflict: when a contestant shares a lab with a
  judge, is there a same-lab robustness check (recompute the ranking with that
  judge excluded)?
- Length / verbosity bias: any control or regression for "longer answer scores
  higher"?
- Halo effect: are rubric criteria ATOMIC (scored independently) rather than one
  global "how good was it" score that lets one strong dimension inflate the rest?

Grep starting points:
  rg -n "resolved_model" .
  rg -ni "krippendorff|alpha|kappa|agreement|inter.?rater|reliability" .
  rg -ni "same.?lab|same_lab|judge.?family|exclude.?judge" .
  rg -ni "length.?bias|verbosity|word.?count|token.?count|ols|slope" .
  rg -ni "rubric|atomic|dimension|criteria|halo" .

Good looks like: resolved_model serialized into every judge artifact AND the flat
results row; Krippendorff's alpha published per dimension and per model; a
same-lab check that recomputes the board with the same-lab judge dropped; a
length-bias OLS regression; atomic per-dimension rubrics. (cot-bench:
eval/scoring/judge.py resolved_model, eval/scoring/agreement.py krippendorff_alpha,
scripts/aggregate_results.py compute_same_lab_check + compute_length_bias,
tests/test_same_lab.py, tests/test_length_bias.py.)

Severity: judge not pinned to the served model is INVALIDATING (silent drift).
Multi-judge with no agreement stat is INVALIDATING. Single judge sharing a lab
with a contestant and no same-lab check is INVALIDATING for that contestant.
Length bias unmeasured, or non-chance-corrected agreement, is HARDENING.
```

---

## 5. Statistical honesty

```
[shared header]

You audit STATISTICAL HONESTY. The question: are the headline numbers presented
with their uncertainty, or is sampling noise sold as signal?

Sub-checks:
- Do headline numbers (efficacy, composite, ranking) carry CONFIDENCE INTERVALS,
  ideally a bootstrap with a FIXED seed? Is the resampling unit correct (resample
  SCENARIOS, not correlated per-run rows)?
- Is aggregation MICRO vs MACRO stated (per-scenario mean vs per-row mean — they
  differ when scenarios have unequal run counts)?
- If reliability is reported, is pass@k vs pass^k DISAMBIGUATED (at-least-one vs
  all-k-succeed), with the semantics stated?
- Are seeds fixed and recorded (and is non-reproducibility, e.g. unseeded
  simulators at temp > 0, stated honestly rather than implied away)?
- With many models x dimensions, is MULTIPLE-COMPARISON risk acknowledged (rank
  bands by CI overlap, or a minimum-N gate before publishing a ranking)?

Grep starting points:
  rg -ni "bootstrap|confidence|ci_low|ci_high|percentile|interval" .
  rg -n "seed|SEED|random_state|np.random" .
  rg -ni "micro|macro|aggregat|per.?scenario|per.?row" .
  rg -ni "pass@|pass\^|pass_at|pass_hat|tau-bench|at least one|all.?k" .
  rg -ni "rank.?band|minimum.*scenario|multiple comparison|statistical_note" .

Good looks like: a bootstrap (B replicates, fixed seed) resampling scenarios, with
ci_low/ci_high on efficacy and the composite; a paired bootstrap when the
composite is field-normalized; rank bands clustering models whose CIs overlap; a
minimum scenario count before a ranking publishes; pass^k published alongside
pass@k with the semantics documented. (cot-bench: docs/methodology.md statistics
section, tests/test_bootstrap.py, tests/test_pass_hat_k_aggregate.py.)

Severity: no CIs on a headline ranking built from few scenarios is INVALIDATING.
pass@k / pass^k conflated is INVALIDATING (different claims). Micro/macro
unstated, or multiple-comparison risk unacknowledged on an otherwise CI'd board,
is HARDENING.
```

---

## 6. Reproducibility

```
[shared header]

You audit REPRODUCIBILITY. The question: can an independent party re-run this and
get the same (or honestly-bounded) numbers?

Sub-checks:
- Is there a documented deterministic re-run path (a single command, pinned
  inputs)? Where determinism is impossible (temp > 0 simulators), is that stated
  rather than implied?
- For expensive runs, are there COST CAPS and/or RESUME so a crash mid-run doesn't
  force a full re-pay (which pressures cutting corners)?
- Is the ENVIRONMENT pinned (lockfile, pinned deps, pinned Python/runtime), not
  just "pip install"?

Grep starting points:
  rg -n "seed|temperature|deterministic" eval scripts
  rg -ni "resume|checkpoint|cost.?cap|max.?cost|budget|--resume" .
  rg -l "requirements.*\.txt|poetry.lock|uv.lock|pyproject.toml|Pipfile.lock|package-lock" .
  rg -n "python-version|python_requires|setup-python" .github pyproject.toml

Good looks like: a run command with pinned scenario set + seeds; a resume module
and a cost module for long paid runs; pinned deps and a pinned Python in CI; an
explicit "not bit-for-bit reproducible" caveat where simulators are unseeded.
(cot-bench: eval/resume.py, eval/cost.py, pyproject.toml, the reproducibility_note
in eval/pre_registration.py.)

Severity: no re-run path at all is INVALIDATING. No cost cap/resume on an
expensive run, or environment pinned only in prose, is HARDENING.
```

---

## 7. Leaderboard exclusions

```
[shared header]

You audit LEADERBOARD EXCLUSIONS. The question: are things that would distort the
public board kept out of it — and is that ENFORCED BY A TEST, not just intended?

Sub-checks:
- Is there a NULL-AGENT baseline (a deterministic do-nothing agent) proving a
  trivial agent scores near zero on BOTH judges and any deterministic checks — and
  is it EXCLUDED from the published leaderboard?
- Are HOLDOUT rows split out before public aggregation (headline computed over the
  public corpus only)?
- Are non-default configs (smoke runs, partial runs, alternate judge panels) kept
  out of the public aggregate?
- Critically: are these exclusions guarded by TRIPWIRE TESTS that fail if an
  excluded row reaches the board — or only by a comment / good intention?
- Is there a completeness gate blocking a partial leaderboard (some models failed)
  from publishing silently?

Grep starting points:
  rg -ni "null.?agent|do-nothing|baseline" .
  rg -ni "exclude|exclusion|drop.*row|non-contestant|not.*leaderboard" scripts eval
  rg -ln "test_null|test_check_publish|test_holdout|exclude" tests
  rg -ni "allow.?partial|completeness|models_failed|check_publish" .

Good looks like: a null-agent provider deliberately kept out of MODELS_UNDER_TEST
and dropped at the single aggregation entry point; a test asserting it never
appears on the board; holdout rows tagged and split before aggregation; a publish
gate reading models_failed to block a partial board. (cot-bench:
eval/providers/null_agent.py, scripts/aggregate_results.py exclude_non_contestants,
tests/test_null_agent.py, scripts/check_publish_ready.py, tests/test_check_publish_ready.py.)

Severity: a null-agent / holdout / non-default row reaching the public board with
no tripwire test is INVALIDATING (the board can silently include what it
shouldn't). No null-agent baseline at all is INVALIDATING for a gameability claim.
Exclusion done in code but with no test guarding it is HARDENING.
```
