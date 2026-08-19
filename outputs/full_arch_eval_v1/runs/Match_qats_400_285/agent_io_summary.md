# Agent IO summary: `Match:qats_400:285`

- Architecture pred: `C` (success=True)
- model_calls=12, tool_calls=5, latency=109.4s

## Planner — `planner`

tokens prompt=1081 completion=378 latency=13.55s

### INPUT (system)

```
You are a Planner Agent for a hierarchical time-series analysis system.
You do NOT call tools and do NOT compute statistics.
Your only job is to understand the question and produce an evidence-gathering plan.

Available analytical agents:

Homogeneous agents examine the task from a temporal-scale perspective:
- short: localized events, abrupt changes, short-term variation
- medium: repeated patterns, regimes, and intermediate structure
- long: global trend, long-range dependence, and overall structure

Heterogeneous agents examine the task from a functional perspective:
- structure: quantify structural and statistical properties
- reasoning: evaluate deductive, inductive, causal, analogical, or counterfactual claims
- matching: compare, locate, transform, or rank numerical sequences
- alignment: evaluate relationships between numerical series and semantic descriptions

These are capabilities, not keyword labels. Infer agents from the full meaning of the
question and candidates. Do not select an agent merely because one word resembles its name.
Select only agents that have a distinct evidence-gathering responsibility.

Division of labor:
- Homogeneous agents collect scale-specific observations and candidate measurements.
- Heterogeneous agents reconcile those observations and produce the evidence needed for
  target_output (including the final numerical value or candidate choice when applicable).
- Homo alone is never sufficient when an answer must be produced. Always include at least
  one hetero_assignment that owns the final measurement or decision.

Selection policy:
- Prefer the smallest sufficient agent set, but never omit the hetero agent responsible
  for target_output.
- If a measurement appears in homo_assignments (for example seasonal_period), the
  corresponding hetero_assignment must also list that measurement or an explicit
  reconciliation of it. Do not use generic placeholders such as task_relevant_evidence.
- hetero_assignments must be non-empty.

Planning process:
1. Read <question>, <candidates>, and <metadata>.
2. Restate the analytical intent and the exact output that must be returned.
3. Decide which temporal perspectives are needed and write one homo_assignment each.
4. Decide which functional roles are needed and write one hetero_assignment each.
5. For every assignment, specify:
   - objective: what that agent must accomplish
   - required_measurements: abstract evidence goals (not tool names)
   - validation_requirements: how to check reliability or resolve conflicts
   - target_series / focus_intervals when known from metadata
6. Ensure the union of assignments is sufficient for target_output.
7. Self-check: no tool names; no invented numbers; no unused agents;
   hetero_assignments is non-empty; every measurement needed for target_output appears
   in at least one hetero_assignment.

Critical constraints:
- Do NOT invent or mention tool names.
- required_measurements describe evidence goals, not implementations.
  Examples: seasonal_period, seasonal_strength, persistence, residual_noise_ratio,
  endpoint_slope, step_level_count, pairwise_similarity, reverse_similarity,
  caption_claim_support, change_location.
- Metadata provides structural context (counts, intervals, mappings). Do not treat
  category-like fields as hard routing instructions that override the question.
- Do not predict the answer.

Output ONLY valid JSON with this schema (AgentPlan):
{
  "reasoning": "string",
  "task_summary": "string",
  "target_output": "string",
  "answer_type": "choice|numerical|binary|unknown",
  "capability": "string",
  "scope": "local|overall|unknown",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short|medium|long",
      "objective": "string",
      "required_measurements": ["string"],
      "validation_requirements": ["string"],
      "target_series": [1],
      "focus_intervals": [[0, 99]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "structure|reasoning|matching|alignment",
      "objective": "string",
      "required_measurements": ["string"],
      "validation_requirements": ["string"],
      "target_series": [1],
      "focus_intervals": [[0, 99]]
    }
  ],
  "success_criteria": ["string"],
  "notes": "string"
}

```

### INPUT (user)

```
<question>
Which of the following four candidate sequences, each the same length as Time Series 1, has the most similar pattern to Time Series 1?
</question>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires comparing Time Series 1 against four candidate series to find the most similar one based on pattern. This involves examining patterns from a short-term variation perspective and using a matching approach to quantify similarity.",
  "task_summary": "Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.",
  "target_output": "A|B|C|D",
  "answer_type": "choice",
  "capability": "matching",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Analyze local variations and changes in Time Series 1 and each candidate sequence.",
      "required_measurements": ["endpoint_slope", "step_level_count", "persistence", "residual_noise_ratio"],
      "validation_requirements": ["Recheck consistency across all short-term measurements."],
      "target_series": [1, 2, 3, 4, 5],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Identify the candidate Time Series with the highest similarity to Time Series 1.",
      "required_measurements": ["pairwise_similarity"],
      "validation_requirements": ["Ensure comparison is made only between Time Series 1 and its candidates."],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["All four candidate series are compared against Time Series 1", "Each pairwise comparison measure is computed and considered", "The candidate with the highest similarity score is selected as the answer"],
  "notes": "Pattern similarity should be evaluated holistically by combining insights from short-term analysis."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4048 completion=439 latency=16.93s

### INPUT (system)

```
You are a short-scale Homogeneous Temporal Understanding Agent.
Stage: Evidence Planning + Capability Selection (S1+S2 merged).
You do NOT answer the multiple-choice question. You do NOT invent tool argument formats.

Scale focus:
- short: local changes, short cycles, abrupt shifts, recent volatility
- medium: seasonality, staged regimes, mid-scale change points
- long: global trend, non-stationarity, long-range structure

Your job in this stage:
1. Parse the Planner assignment into claims that need measurable evidence
   (NOT a paraphrase of the objective; each claim needs required_evidence items).
2. Read the tool capability library below and select tools whose capabilities
   can produce that evidence (semantic reasoning, not keyword/measurement hard-match).
3. If no new tools are needed, set selected_tools to [] and fill no_tool_decision
   with reason + evidence_sources. Do not skip tools lazily when evidence gaps remain.

Critical:
- required_evidence must be observable fact types, never tool names.
- Do NOT invent tools absent from the capability library.
- Do NOT output final answer letters or fabricated numbers.

Tool capability library:
Tool capability library (for selection only; do NOT invent argument formats here):

- describe_series: Descriptive stats for EVERY series: mean/std/min/max/median/range/p50/p90/p99/slope (preferred multi-series overview).
  produces: series
  use_when: Need an initial global statistical overview or exact basic statistics.
  avoid_when: The requested fact is local to a window or concerns temporal ordering only.
  limitations: Global summaries can hide local regimes, timing, and waveform shape.
- sliding_stats: Sliding-window mean/std for local volatility.
  produces: series
  use_when: Local volatility or rolling level variation must be measured.
  avoid_when: An exact point value, global extremum, or discrete event count is requested.
  limitations: Results depend on window size and summarize rather than return every rolling value.
- diff_stats: First-difference stats and sign changes.
  produces: series
  use_when: Changes, roughness, direction switches, or increment variability are relevant.
  avoid_when: The task asks only for level statistics without temporal differences.
  limitations: Differencing removes level information and can amplify measurement noise.
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  produces: series
  use_when: Turning-point counts or local peak/trough locations are required.
  avoid_when: Counting plateaus/step levels, or only global extrema, is requested.
  limitations: Prominence filtering may omit weak extrema; not a substitute for step_levels.
- global_extrema: Global max/min indices and values; optional index classifies a point as global/local peak/trough (Base index tasks).
  produces: series
  use_when: Global extrema values/locations or classification of one index is required.
  avoid_when: All local turning points or anomaly scores are requested.
  limitations: Tie breaking uses earliest maximum and latest minimum.
- segment_trend: Linear slope and direction (upward/downward/flat) for a segment.
  produces: series
  use_when: Direction or slope over a specified segment is the target.
  avoid_when: Nonlinear trend shape or internal regime changes are the primary target.
  limitations: Endpoint/linear summaries can miss mid-segment fluctuations.
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  produces: series
  use_when: Discrete steps, staircase levels, or plateau runs must be counted.
  avoid_when: Turning points in a continuously varying signal are requested.
  limitations: Level counts depend on adaptive tolerance; not interchangeable with local_extrema.
- value_at_index: Return the numeric value at a specific index (0-based by default).
  produces: series
  use_when: An exact value at a known index is required.
  avoid_when: The index is unknown or a neighborhood statistic is needed.
  limitations: Index base must match the question; out-of-range indices fail.
- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  produces: series
  use_when: Point spikes or z-score outliers must be detected in a window.
  avoid_when: Contextual/collective anomalies or mean-shift change points are intended.
  limitations: Sensitive to z_threshold and distribution assumptions.
- autocorr: Autocorrelation up to max_lag (full ACF list). Optional lags=[...] returns acf_at_lags for specific lags.
  produces: best_lag, autocorrelation, acf_at_lags
  use_when: Lag dependence or periodic repetition needs independent evidence.
  avoid_when: A single seasonal lag seas_acf1 is the only needed metric — prefer seas_acf.; Strong trend has not been considered or max_lag cannot cover the expected period.
  limitations: Trend can dominate low lags; ACF alone does not establish waveform type.; Pass lags=[m] when only specific lags are needed.
  often_combined_with: seas_acf, fft_period, stl_strength
- seas_acf: MMTS seas_acf1: seasonal autocorrelation ρ_m=γ_m/γ_0 at lag m (e.g. lag=26 for weekly half-year frequency).
  produces: seas_acf1, strength_hint
  use_when: InWild seas_acf1 questions with an explicit seasonal lag/frequency (e.g. 26 weeks).
  avoid_when: You need a full ACF curve rather than one seasonal lag.
  limitations: Requires lag < series length; strength_hint is heuristic.
  often_combined_with: autocorr, stl_strength, fft_period
- nonlinearity_terasvirta: MMTS nonlinearity via Terasvirta NN test: returns 10*T_stat/N (larger ⇒ stronger nonlinear structure).
  produces: nonlinearity, terasvirta_stat
  use_when: InWild nonlinearity / Terasvirta questions.
  avoid_when: Only linear trend or basic stats are requested.
  limitations: Uses Nixtla/tsfeatures Terasvirta NN test; short series may fail.
  often_combined_with: advanced_features, adf_stationarity
- index_calendar_map: Map indices to weekday/hour using an hourly calendar anchor (MMTS InWild default: index 0 = Thursday 00:00).
  produces: weekday, hour, is_weekend
  use_when: Questions map indices to weekday/hour (InWild hourly series starting Thursday 00:00).
  avoid_when: No calendar/weekday semantics appear in the question.
  limitations: Defaults match MMTS generator (anchor Thursday, 1H); override from question text.
  often_combined_with: interval_compare, segment_trend, value_at_index
- fft_period: Dominant period via FFT.
  produces: dominant_period, spectral_strength, period_trusted
  use_when: A dominant spectral period candidate is needed.
  avoid_when: A full-series-length period or weak peak would be accepted without validation.
  limitations: Trend/leakage can select very long periods; validate weak or boundary estimates.; spectral_strength is NOT seasonal_strength.; period_trusted=false when dominant_period is near series length or half-length.; FFT period alone does not identify waveform type (sine/square/triangle/sawtooth).
  often_combined_with: stl_strength, autocorr, waveform_features
- stl_strength: STL seasonal/trend strength.
  produces: period, seasonal_strength, season_strength_bin, trend_strength, period_trusted
  use_when: A candidate period must be tested for seasonal/trend decomposition strength.
  avoid_when: An automatically selected period would be treated as ground truth without validation.
  limitations: Depends on STL assumptions; automatic period is capped to avoid half-length overfitting.; Untrusted period yields misleading seasonal_strength — check period_trusted.
  often_combined_with: fft_period, autocorr
- hurst_exponent: Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), matching MMTS label generation. Returns persistence_hint at 0.45/0.55.
  produces: hurst, persistence_hint
  use_when: Long-memory or persistence is the requested measurement (MMTS Hurst bins).
  avoid_when: The series is shorter than ~20 points or dominated by deterministic trend.
  limitations: Uses hurst.compute_Hc(kind=random_walk) to match MMTS labels; trend can still bias.
- noise_decomposition: MMTS-style residual noise strength: Var(residual)/Var(series) after STL (conservative vs high-pass), with bins none/low/medium/high at 0.1/0.33/0.66 and a heuristic noise_type_hint.
  produces: noise_ratio, noise_level, noise_type_hint
  use_when: Residual noise strength / noise level bins are required (MMTS noise questions).
  avoid_when: A known ground-truth noise component is expected but unavailable.
  limitations: Approximates MMTS Var(n)/Var(ts) via STL/high-pass residuals; noise_type_hint is heuristic.
- waveform_features: Classify waveform shape (sine/square/triangle/sawtooth/ambiguous) using jump ratio, plateau clustering, harmonic structure, and folded-template match. Do NOT treat FFT period alone as evidence of a sine wave.
  produces: waveform_hint, jump_ratio, template_match
  use_when: The question asks which waveform type (sine/square/triangle/sawtooth) a series resembles.; Shape discrimination is needed beyond period or seasonal strength.
  avoid_when: Only period/seasonal strength is needed without shape type.; Matching across candidate series (use pairwise/robust matching instead).
  limitations: periodicity_is_not_waveform_type: FFT period alone never implies sine.; Hints can be ambiguous under heavy noise or non-periodic shapes.
  often_combined_with: fft_period, step_levels, diff_stats
- adf_stationarity: ADF stationarity test.
  produces: series
  use_when: Statistical unit-root stationarity evidence is required.
  avoid_when: Stationarity is meant only as visual constancy or the window is too short.
  limitations: Sensitive to specification and structural breaks.
- change_points: Mean-shift change-point candidates.
  produces: series
  use_when: Potential level/regime transitions must be localized.
  avoid_when: Exact guaranteed change points or variance-only shifts are required.
  limitations: Candidates are heuristic mean-shift locations.
- interval_compare: Compare left/right interval statistics on one series (mean/std/max/min/n_peaks/trend per side).
  produces: left/right
  use_when: Two intervals within one series must be compared quantitatively.
  avoid_when: The intervals belong to different series.
  limitations: Bounds may be clamped/reordered; adjusted results must be qualified.
- crossing_points: Count crossings inside an optional window using a whole-series median/mean by default; threshold_scope='window' opts into a window-derived threshold.
  produces: series
  use_when: Crossings of zero, mean, median, or an explicit threshold are requested.
  avoid_when: Peaks/troughs or change points are intended instead of threshold crossings.
  limitations: Counts depend on threshold and threshold_scope.
- advanced_features: Advanced basic/volatility features: IQR, skewness, excess kurtosis, spectral and histogram entropy, stability, lumpiness, ARCH LM/R², and median crossings.
  produces: series
  use_when: Higher-order distribution or volatility summaries are needed.
  avoid_when: A simple exact statistic or localized event is sufficient.
  limitations: Several outputs are proxies and depend on bin/chunk/lag parameters.
- counterfactual_simulate: Apply counterfactual edits to a copied series and compare before/after statistics. Supports set_value, replace_segment, shift, scale_values, scale_std, cap, and extrapolate_slope.
  produces: before, after, deltas, status
  use_when: The question asks about an explicit edit and its consequences on the same series.
  avoid_when: Inferring causal effects on another series or answering from the unedited series.
  limitations: Edits are deterministic simulations, not causal models.
- cross_series_compare: Compare windows across TWO series (analogical / multi-series segment tasks). Returns per-series segment stats, trend match, distance, correlation.
  produces: correlation, distance, trend_agreement
  use_when: Aligned or specified windows from two series must be compared.
  avoid_when: More than two candidates need ranking or one-series intervals are compared.
  limitations: Correlation/distance require compatible overlap and do not prove causality.
  often_combined_with: lag_corr, pairwise_distance
- extrema_align: Align peaks/troughs across two series or intervals; returns normalized event-position deltas, best event lag, and global-extrema index deltas.
  produces: alignment
  use_when: Peak/trough event timing across two series or intervals must be aligned.
  avoid_when: Amplitude similarity or dense pointwise matching is the objective.
  limitations: Reliability depends on detected event coverage and prominence filtering.
- lag_corr: Auto or cross lag correlation. Use series_index_1/2 ints, or 'all' for all pairs.
  produces: lag_correlation
  use_when: Correlation at one specified lag is required.
  avoid_when: The best lag is unknown or causal direction must be established.
  limitations: Association is not causation; large lags reduce overlap.
  often_combined_with: lag_corr_scan, cross_series_compare
- lag_corr_scan: Scan cross-correlation over positive and negative lags and report the strongest lead-lag association; association is not causal proof.
  produces: best_lag/best_corr, lags, warnings
  use_when: The strongest lead-lag association over a bounded lag range is required.
  avoid_when: Causal proof is requested or overlap is insufficient.
  limitations: Multiple-lag search can find spurious associations; inspect overlap.
- window_shape_compare: Compare two or more windows on one series (analogical pattern similarity) via z-euclidean or DTW distance.
  produces: pairs, nearest_pair
  use_when: Analogical / pattern-similarity questions comparing two intervals on one series.
  avoid_when: Cross-series comparison is required (use cross_series_compare).
  limitations: Unequal window lengths are truncated for z-euclidean; DTW handles unequal lengths.
  often_combined_with: subsequence_locate, interval_compare
- joint_threshold_events: Count timesteps where multiple series jointly satisfy threshold rules (e.g. series1>20 and series2<78).
  produces: n_events, indices
  use_when: Multi-series simultaneous threshold conditions (e.g. TS1>a while TS2<b).
  avoid_when: Single-series peak counting is enough.
  limitations: Pointwise logic only; no event duration merging.
  often_combined_with: peaks_above_threshold, cross_series_compare
- peaks_above_threshold: Count local peaks/troughs optionally filtered by absolute height threshold (InWild peak-above-value style questions).
  produces: series
  use_when: Count peaks/troughs above/below an absolute value threshold.
  avoid_when: Unfiltered local extrema counts are sufficient.
  limitations: Uses the same prominence filter as local_extrema then applies threshold.
- bimodal_detect: Detect amplitude bimodality via histogram peak/valley heuristic.
  produces: series
  use_when: Questions ask whether the amplitude distribution is bimodal.
  avoid_when: Only mean/std summaries are needed.
  limitations: Histogram heuristic; sensitive to binning.

Output ONLY JSON (EvidenceCapabilityPlan):
{
  "reasoning": "string",
  "evidence_plan": {
    "objective": "string",
    "claims_to_support": [
      {"claim": "string", "required_evidence": ["string"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["string"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "string", "supports_evidence": ["string"]}
    ],
    "no_tool_decision": null
  }
}
When skipping tools:
"no_tool_decision": {"skip_tools": true, "reason": "string", "evidence_sources": [{"type": "upstream_observation", "ref": "string", "field": "string"}]}

```

### INPUT (user)

```
<assignment>
{"scale":"short","objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","required_measurements":["endpoint_slope","step_level_count","persistence","residual_noise_ratio"],"validation_requirements":["Recheck consistency across all short-term measurements."],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires comparing Time Series 1 against four candidate series to find the most similar one based on pattern. This involves examining patterns from a short-term variation perspective and using a matching approach to quantify similarity.","task_summary":"Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.","target_output":"A|B|C|D","answer_type":"choice","capability":"matching","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","required_measurements":["endpoint_slope","step_level_count","persistence","residual_noise_ratio"],"validation_requirements":["Recheck consistency across all short-term measurements."],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All four candidate series are compared against Time Series 1","Each pairwise comparison measure is computed and considered","The candidate with the highest similarity score is selected as the answer"],"notes":"Pattern similarity should be evaluated holistically by combining insights from short-term analysis."}
</plan_context>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The task requires analyzing short-term characteristics of Time Series 1 and its candidates, focusing on local variations, step-level changes, persistence, and residual noise ratio. These metrics will help identify similarities among the series.",
  "evidence_plan": {
    "objective": "Analyze local variations and changes in Time Series 1 and each candidate sequence.",
    "claims_to_support": [
      {"claim": "Time Series 1 has a specific endpoint slope indicative of its short-term behavior.", "required_evidence": ["slope"]},
      {"claim": "Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.", "required_evidence": ["discrete step level counts"]},
      {"claim": "Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.", "required_evidence": ["hurst exponent"]},
      {"claim": "Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.", "required_evidence": ["noise ratio"]}
    ],
    "analysis_scope": {"target_series": [1,2,3,4,5], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["Recheck consistency across all short-term measurements."]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "segment_trend", "reason": "To capture the endpoint slope indicative of short-term behavior.", "supports_evidence": ["slope"]},
      {"tool": "step_levels", "reason": "To count the discrete step levels representing distinct changes in levels.", "supports_evidence": ["discrete step level counts"]},
      {"tool": "hurst_exponent", "reason": "To measure the persistence or long-memory properties of the time series.", "supports_evidence": ["hurst exponent"]},
      {"tool": "noise_decomposition", "reason": "To decompose the series and calculate the residual noise ratio.", "supports_evidence": ["noise ratio"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=982 completion=270 latency=9.64s

### INPUT (system)

```
You are a short-scale Homogeneous Agent at Stage 3: Tool Workflow Planning.
Design an ordered analysis pipeline for the selected tools.
You do NOT fill concrete argument literals (except bindings like $step1.field).
You do NOT invent tools outside the selected set.

Rules:
1. Order tools so dependencies run first (e.g. fft_period before stl_strength).
2. Use input_binding ONLY for dependent parameters from prior steps, e.g.
   {"period": "$step1.dominant_period"} or {"period": "$fft_period.dominant_period"}.
   The referenced field MUST exist in that prior tool's outputs (fft_period→dominant_period;
   never bind period to describe_series / hurst_exponent / change_points).
3. Do NOT bind series / series_index in input_binding. Stage 4 supplies series_index literals.
   Never write "$tool.series", "$step1.series", "$series....", or "$candidate_series_indices[...]".
4. Leave input_binding empty {} for the first step when it has no prior dependency.
5. Read IO concepts below for input/output concepts and dependency hints.
6. If selected_tools is empty, return workflow: [].

Output ONLY JSON (ToolWorkflow):
{
  "reasoning": "string",
  "workflow": [
    {
      "step": 1,
      "tool": "fft_period",
      "output_key": "candidate_period",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "stl_strength",
      "output_key": "seasonal_result",
      "input_binding": {"period": "$step1.dominant_period"}
    }
  ]
}

```

### INPUT (user)

```
<evidence_capability_plan>
{"evidence_plan":{"objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","claims_to_support":[{"claim":"Time Series 1 has a specific endpoint slope indicative of its short-term behavior.","required_evidence":["slope"]},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","required_evidence":["discrete step level counts"]},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","required_evidence":["hurst exponent"]},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","required_evidence":["noise ratio"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"short"},"validation_needs":["Recheck consistency across all short-term measurements."]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To capture the endpoint slope indicative of short-term behavior.","supports_evidence":["slope"]},{"tool":"step_levels","reason":"To count the discrete step levels representing distinct changes in levels.","supports_evidence":["discrete step level counts"]},{"tool":"hurst_exponent","reason":"To measure the persistence or long-memory properties of the time series.","supports_evidence":["hurst exponent"]},{"tool":"noise_decomposition","reason":"To decompose the series and calculate the residual noise ratio.","supports_evidence":["noise ratio"]}],"no_tool_decision":null},"reasoning":"The task requires analyzing short-term characteristics of Time Series 1 and its candidates, focusing on local variations, step-level changes, persistence, and residual noise ratio. These metrics will help identify similarities among the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
- hurst_exponent
  inputs: series
  outputs: hurst, persistence_hint
- noise_decomposition
  inputs: series, period(optional)
  outputs: noise_ratio, noise_level, noise_type_hint
</io_concepts>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "trend_series",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "step_levels",
      "output_key": "level_counts",
      "input_binding": {"series_index": "$step1.series_index"}
    },
    {
      "step": 3,
      "tool": "hurst_exponent",
      "output_key": "persistence_measurement",
      "input_binding": {"series": "$step1.series"}
    },
    {
      "step": 4,
      "tool": "noise_decomposition",
      "output_key": "residual_noise",
      "input_binding": {"series": "$step1.series"}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=1246 completion=204 latency=7.40s

### INPUT (system)

```
You are a short-scale Homogeneous Agent at Stage 4: Tool Invocation.
Fill concrete arguments for each workflow step using the invocation spec.
Do NOT change the workflow order or add/remove tools.
calls[].step and calls[].tool MUST match the workflow one-to-one (same step numbers and tool names).
Dependent values must use $stepN.field references ONLY when that field exists in step N's tool output
(see invocation returns / IO concepts). Example: period ← $stepK.dominant_period only if step K is fft_period.
Never invent metadata refs like $candidate_series_indices[i] or $query_series_index — use literal ints.
Optional fields: omit the key; never JSON null.
Never paste raw numeric arrays; use series_index from metadata/assignment.

Output ONLY JSON (InvocationPlan):
{
  "reasoning": "string",
  "calls": [
    {"step": 1, "tool": "fft_period", "args": {"series_index": 1}},
    {"step": 2, "tool": "stl_strength", "args": {"series_index": 1, "period": "$step1.dominant_period"}}
  ]
}

```

### INPUT (user)

```
<workflow>
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_counts","input_binding":{"series_index":"$step1.series_index"}},{"step":3,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":4,"tool":"noise_decomposition","output_key":"residual_noise","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio."}
</workflow>

<tool_invocation_spec>
Runtime tool invocation protocol:
- Tools read pipeline-bound series; NEVER paste raw numeric arrays into arguments.
- Optional parameters: omit the key; never JSON null.
- Multi-round / workflow: pass numeric literals OR $stepN.field references resolved by Runtime.
- Placeholders/strings naming other tools are not valid argument values.
- Use series_index (1-based): int, list like [1,2,3], 'Time Series 2', or 'all'.
- If n_series>1 and series_index is omitted, tools fan out over ALL series.
- lag_corr is pairwise: use series_index_1/2 as ints, or set either to 'all' for all pairs.
- Optional window args: start/end (inclusive indices), window (alias window_size).

- segment_trend: Linear slope and direction (upward/downward/flat) for a segment.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series slope/direction for a segment}
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
- hurst_exponent: Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), matching MMTS label generation. Returns persistence_hint at 0.45/0.55.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=Hurst via compute_Hc, persistence_hint, estimator metadata}
- noise_decomposition: MMTS-style residual noise strength: Var(residual)/Var(series) after STL (conservative vs high-pass), with bins none/low/medium/high at 0.1/0.33/0.66 and a heuristic noise_type_hint.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, period=optional int}
  returns: {series=noise_ratio=Var(resid)/Var(series), noise_level bins none/low/medium/high, type hint}
</tool_invocation_spec>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<assignment>
{"scale":"short","objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","required_measurements":["endpoint_slope","step_level_count","persistence","residual_noise_ratio"],"validation_requirements":["Recheck consistency across all short-term measurements."],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio.",
  "calls": [
    {"step": 1, "tool": "segment_trend", "args": {"series_index": 1}},
    {"step": 2, "tool": "step_levels", "args": {"series_index": 1}},
    {"step": 3, "tool": "hurst_exponent", "args": {"series_index": 1}},
    {"step": 4, "tool": "noise_decomposition", "args": {"series_index": 1}}
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=2675 completion=823 latency=30.23s

### INPUT (system)

```
You are a short-scale Homogeneous Agent at Stage 5: Evidence Integration.
Turn executed tool results (system-owned) into structured observations with provenance.
You do NOT call tools. You do NOT invent numbers not present in executed_steps.
You do NOT output the final multiple-choice answer letter.

Coverage confidence must be one of:
- tool_supported: value comes from a successful executed_steps call_id
- context_supported: value comes from upstream/context (only when no local tools)
- unresolved: missing evidence
- qualified: degraded/adjusted tool result

When executed_steps is empty, only context_supported or unresolved are allowed.
Never mark tool_supported without a successful call_id.

Output ONLY JSON (ScaleObservation body; scale will be set by runtime):
{
  "reasoning": "string",
  "scale": "short",
  "observations": ["human-readable summary strings"],
  "evidence_intervals": ["string"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "string",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.0,
          "source_tool": "stl_strength",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "seasonal_strength"
    }
  ],
  "coverage": {"seasonal_strength": "tool_supported"},
  "unresolved_claims": []
}

```

### INPUT (user)

```
<evidence_capability_plan>
{"evidence_plan":{"objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","claims_to_support":[{"claim":"Time Series 1 has a specific endpoint slope indicative of its short-term behavior.","required_evidence":["slope"]},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","required_evidence":["discrete step level counts"]},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","required_evidence":["hurst exponent"]},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","required_evidence":["noise ratio"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"short"},"validation_needs":["Recheck consistency across all short-term measurements."]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To capture the endpoint slope indicative of short-term behavior.","supports_evidence":["slope"]},{"tool":"step_levels","reason":"To count the discrete step levels representing distinct changes in levels.","supports_evidence":["discrete step level counts"]},{"tool":"hurst_exponent","reason":"To measure the persistence or long-memory properties of the time series.","supports_evidence":["hurst exponent"]},{"tool":"noise_decomposition","reason":"To decompose the series and calculate the residual noise ratio.","supports_evidence":["noise ratio"]}],"no_tool_decision":null},"reasoning":"The task requires analyzing short-term characteristics of Time Series 1 and its candidates, focusing on local variations, step-level changes, persistence, and residual noise ratio. These metrics will help identify similarities among the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "slope": 37.492,
      "direction": "upward",
      "direction_class": "upward",
      "trend_method": "endpoint",
      "mean": 1547.3769230769233,
      "std": 495.0841749002753,
      "start_value": 996.5,
      "end_value": 1933.8
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "step_levels",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "n_unique_levels": 17,
      "n_plateau_runs": 26,
      "levels": [
        996.5,
        927.9,
        969.0,
        905.2,
        863.0,
        1132.7,
        1813.2,
        1459.5,
        1855.6,
        1633.2,
        2000.0,
        2261.2,
        1893.6,
        2226.3,
        2191.4,
        2061.6,
        1933.8
      ],
      "plateau_runs": [
        996.5,
        927.9,
        969.0,
        905.2,
        1003.7,
        929.1,
        990.0,
        863.0,
        1132.7,
        944.0,
        1813.2,
        1459.5,
        1855.6,
        1474.2,
        1633.2,
        2000.0,
        2261.2,
        1893.6,
        2226.3,
        1986.9,
        2191.4,
        1881.1,
        2061.6,
        1886.7,
        2012.4,
        1933.8
      ],
      "plateau_lengths": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1
      ],
      "tolerance": 20.165
    },
    "error": null,
    "args_fingerprint": "9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"
  },
  {
    "call_id": "short:step3",
    "step": 3,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "hurst": 0.22606695057982257,
      "persistence_hint": "anti_persistent",
      "estimator": "fallback_lag_diff",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 26,
      "kind": "fallback",
      "simplified": true,
      "warnings": [
        "strong_endpoint_trend_may_bias_hurst",
        "compute_Hc_failed_used_fallback:Series length must be greater or equal to 100"
      ]
    },
    "error": null,
    "args_fingerprint": "5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"
  },
  {
    "call_id": "short:step4",
    "step": 4,
    "tool_name": "noise_decomposition",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "period": 6,
      "residual_std": 181.23646428852527,
      "residual_rmse": 197.9878576035802,
      "series_std": 495.0841749002753,
      "residual_var": 32846.65598780589,
      "series_var": 245108.34023668637,
      "stl_noise_ratio": 0.134008724289381,
      "highpass_noise_ratio": 0.1926347599384566,
      "noise_ratio": 0.1926347599384566,
      "noise_level": "low",
      "metric_definition": "Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high",
      "estimator": "STL_residual_variance_ratio",
      "seasonal_strength": 0.15640392537936798,
      "trend_strength": 0.8647207235988733,
      "noise_type_hint": "gauss_like",
      "acf_lag1": 0.8325574770146307,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "909854aa026a467bebd5ecbc24b3a7475254db9c"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","required_measurements":["endpoint_slope","step_level_count","persistence","residual_noise_ratio"],"validation_requirements":["Recheck consistency across all short-term measurements."],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes evaluating the endpoint slope of Time Series 1 as an indicator of its short-term behavior, counting the distinct step levels, measuring the Hurst exponent for persistence, and calculating the residual noise ratio.",
  "scale": "short",
  "observations": [
    "Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth.",
    "There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series.",
    "The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion.",
    "The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality."
  ],
  "evidence_intervals": [
    "From the execution of the segment_trend tool, we found the endpoint slope of Time Series 1.",
    "Using the step_levels tool, we identified the number of unique step levels in Time Series 1.",
    "The hurst_exponent tool provided the Hurst exponent, giving us information about the persistence of the series.",
    "The noise_decomposition tool calculated the residual noise ratio for Time Series 1."
  ],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Time Series 1 has an endpoint slope indicative of its short-term behavior.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 37.492,
          "source_tool": "segment_trend",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "endpoint_slope"
    },
    {
      "claim": "Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.",
      "evidence": [
        {
          "type": "discrete step level counts",
          "value": 17,
          "source_tool": "step_levels",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "discrete step level counts"
    },
    {
      "claim": "Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.",
      "evidence": [
        {
          "type": "hurst exponent",
          "value": 0.22606695057982257,
          "source_tool": "hurst_exponent",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "hurst exponent"
    },
    {
      "claim": "Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.",
      "evidence": [
        {
          "type": "noise ratio",
          "value": 0.1926347599384566,
          "source_tool": "noise_decomposition",
          "call_id": "short:step4",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "noise ratio"
    }
  ],
  "coverage": {
    "endpoint_slope": "tool_supported",
    "discrete step level counts": "tool_supported",
    "hurst exponent": "tool_supported",
    "noise ratio": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=6679 completion=235 latency=10.42s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=matching.
Stage: Evidence Planning + Capability Selection (S1+S2 merged).
You reconcile upstream Temporal Profile / prior evidence for your assignment.
You do NOT invent tool argument formats. You do NOT make the irrevocable final system answer.

Role focus:
- structure: structural awareness and feature analysis
- reasoning: temporal reasoning; causal claims are statistical clues only
- matching: sequence similarity / localization / reverse / robust matching
- alignment: time-series <-> semantic description alignment

Your job:
1. Restate what claims need evidence given the assignment and what Homo already provided.
2. Select tools only for gaps or validation needs; otherwise selected_tools=[] with no_tool_decision.
3. Semantic capability matching against the library below — not keyword hard-routing.

Tool capability library:
Tool capability library (for selection only; do NOT invent argument formats here):

- describe_series: Descriptive stats for EVERY series: mean/std/min/max/median/range/p50/p90/p99/slope (preferred multi-series overview).
  produces: series
  use_when: Need an initial global statistical overview or exact basic statistics.
  avoid_when: The requested fact is local to a window or concerns temporal ordering only.
  limitations: Global summaries can hide local regimes, timing, and waveform shape.
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  produces: series
  use_when: Turning-point counts or local peak/trough locations are required.
  avoid_when: Counting plateaus/step levels, or only global extrema, is requested.
  limitations: Prominence filtering may omit weak extrema; not a substitute for step_levels.
- global_extrema: Global max/min indices and values; optional index classifies a point as global/local peak/trough (Base index tasks).
  produces: series
  use_when: Global extrema values/locations or classification of one index is required.
  avoid_when: All local turning points or anomaly scores are requested.
  limitations: Tie breaking uses earliest maximum and latest minimum.
- fft_period: Dominant period via FFT.
  produces: dominant_period, spectral_strength, period_trusted
  use_when: A dominant spectral period candidate is needed.
  avoid_when: A full-series-length period or weak peak would be accepted without validation.
  limitations: Trend/leakage can select very long periods; validate weak or boundary estimates.; spectral_strength is NOT seasonal_strength.; period_trusted=false when dominant_period is near series length or half-length.; FFT period alone does not identify waveform type (sine/square/triangle/sawtooth).
  often_combined_with: stl_strength, autocorr, waveform_features
- waveform_features: Classify waveform shape (sine/square/triangle/sawtooth/ambiguous) using jump ratio, plateau clustering, harmonic structure, and folded-template match. Do NOT treat FFT period alone as evidence of a sine wave.
  produces: waveform_hint, jump_ratio, template_match
  use_when: The question asks which waveform type (sine/square/triangle/sawtooth) a series resembles.; Shape discrimination is needed beyond period or seasonal strength.
  avoid_when: Only period/seasonal strength is needed without shape type.; Matching across candidate series (use pairwise/robust matching instead).
  limitations: periodicity_is_not_waveform_type: FFT period alone never implies sine.; Hints can be ambiguous under heavy noise or non-periodic shapes.
  often_combined_with: fft_period, step_levels, diff_stats
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  produces: distances, nearest, method
  use_when: One query series must be ranked against multiple candidate series.
  avoid_when: Reverse, subsequence, or robust-outlier matching semantics are required.
  limitations: Distance meaning depends on normalization/method; unequal lengths may be truncated.
- reverse_match: Reverse each candidate series and rank candidates against the query using length-normalized z-DTW or Euclidean distance.
  produces: ranking
  use_when: Candidates must be reversed before comparison with a query.
  avoid_when: Ordinary forward matching or trend direction alone is requested.
  limitations: Winner reliability depends on distance margin and method fallback.
- robust_shape_match: Robust candidate ranking using winsorization, smoothing, z-distance, correlation distance, and DTW with an explicit winner margin.
  produces: ranking
  use_when: Candidate ranking must tolerate spikes, scaling, and moderate noise.
  avoid_when: Exact raw-value equality or explicit reverse matching is required.
  limitations: Depends on smoothing/winsorization; small margins can be ambiguous.
- smooth_reverse_stats: Smoothing and reverse-direction stats.
  produces: series
  use_when: Auxiliary direction summaries before and after reversal are needed.
  avoid_when: A winning candidate or similarity ranking is required.
  limitations: Does not compare a query or identify a winner.
- smooth_shape_match: MMTS smooth-it matching: apply centered moving-average (default window=3) to candidates, then rank by DTW/euclidean distance to the query series.
  produces: nearest, ranking
  use_when: MMTS smooth-it: rank candidates after moving-average smoothing.
  avoid_when: Candidates must not be smoothed or reverse matching is required.
  limitations: Default window=3 matches MMTS SmoothitProcessor; distance depends on method.
  often_combined_with: pairwise_distance, robust_shape_match
- subsequence_locate: Locate best matching subsequence of a query inside a longer series. Default method=dtw (MMTS find-it); method=euclidean uses z-normalized L2.
  produces: best_start, best_end, distance
  use_when: MMTS find-it: locate a short query inside a longer series (prefer method=dtw).
  avoid_when: Whole-series candidate ranking is required.
  limitations: Default method=dtw via dtaidistance; euclidean is a faster fallback.
- subsequence_rank: Match find-it multi-candidate ranking: sliding-window DTW of a short query against each longer candidate; returns nearest by distance.
  produces: nearest, ranking
  use_when: Match find-it: rank several longer candidates against one short query via sliding DTW.
  avoid_when: Whole-series choose-it ranking (use pairwise_distance) or single long series locate.
  limitations: Calls sliding DTW per candidate; expensive on long series.
  often_combined_with: subsequence_locate, pairwise_distance

Output ONLY JSON (EvidenceCapabilityPlan):
{
  "reasoning": "string",
  "evidence_plan": {
    "objective": "string",
    "claims_to_support": [
      {"claim": "string", "required_evidence": ["string"]}
    ],
    "analysis_scope": {"target_series": [1], "role": "matching"},
    "validation_needs": ["string"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "string",
      "evidence_sources": [{"type": "upstream_observation", "ref": "string", "field": "string"}]
    }
  }
}
When tools are needed, put them in selected_tools and set no_tool_decision to null.

```

### INPUT (user)

```
<assignment>
{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires comparing Time Series 1 against four candidate series to find the most similar one based on pattern. This involves examining patterns from a short-term variation perspective and using a matching approach to quantify similarity.","task_summary":"Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.","target_output":"A|B|C|D","answer_type":"choice","capability":"matching","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","required_measurements":["endpoint_slope","step_level_count","persistence","residual_noise_ratio"],"validation_requirements":["Recheck consistency across all short-term measurements."],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All four candidate series are compared against Time Series 1","Each pairwise comparison measure is computed and considered","The candidate with the highest similarity score is selected as the answer"],"notes":"Pattern similarity should be evaluated holistically by combining insights from short-term analysis."}
</plan_context>

<task_summary>
Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The analysis includes evaluating the endpoint slope of Time Series 1 as an indicator of its short-term behavior, counting the distinct step levels, measuring the Hurst exponent for persistence, and calculating the residual noise ratio.","scale":"short","observations":["Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth.","There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series.","The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion.","The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality."],"evidence_intervals":["From the execution of the segment_trend tool, we found the endpoint slope of Time Series 1.","Using the step_levels tool, we identified the number of unique step levels in Time Series 1.","The hurst_exponent tool provided the Hurst exponent, giving us information about the persistence of the series.","The noise_decomposition tool calculated the residual noise ratio for Time Series 1."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 37.492, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 1547.3769230769233, \"std\": 495.0841749002753, \"start_value\": 996.5, \"end_value\": 1933.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 17, \"n_plateau_runs\": 26, \"levels\": [996.5, 927.9, 969.0, 905.2, 863.0, 1132.7, 1813.2, 1459.5, 1855.6, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 2191.4, 2061.6, 1933.8], \"plateau_runs\": [996.5, 927.9, 969.0, 905.2, 1003.7, 929.1, 990.0, 863.0, 1132.7, 944.0, 1813.2, 1459.5, 1855.6, 1474.2, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 1986.9, 2191.4, 1881.1, 2061.6, 1886.7, 2012.4, 1933.8], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 20.165}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.22606695057982257, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"fallback_lag_diff\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 26, \"kind\": \"fallback\", \"simplified\": true, \"warnings\": [\"strong_endpoint_trend_may_bias_hurst\", \"compute_Hc_failed_used_fallback:Series length must be greater or equal to 100\"]}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 6, \"residual_std\": 181.23646428852527, \"residual_rmse\": 197.9878576035802, \"series_std\": 495.0841749002753, \"residual_var\": 32846.65598780589, \"series_var\": 245108.34023668637, \"stl_noise_ratio\": 0.134008724289381, \"highpass_noise_ratio\": 0.1926347599384566, \"noise_ratio\": 0.1926347599384566, \"noise_level\": \"low\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.15640392537936798, \"trend_strength\": 0.8647207235988733, \"noise_type_hint\": \"gauss_like\", \"acf_lag1\": 0.8325574770146307, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"909854aa026a467bebd5ecbc24b3a7475254db9c\"}"],"evidence_plan":{"objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","claims_to_support":[{"claim":"Time Series 1 has a specific endpoint slope indicative of its short-term behavior.","required_evidence":["slope"]},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","required_evidence":["discrete step level counts"]},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","required_evidence":["hurst exponent"]},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","required_evidence":["noise ratio"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"short"},"validation_needs":["Recheck consistency across all short-term measurements."]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To capture the endpoint slope indicative of short-term behavior.","supports_evidence":["slope"]},{"tool":"step_levels","reason":"To count the discrete step levels representing distinct changes in levels.","supports_evidence":["discrete step level counts"]},{"tool":"hurst_exponent","reason":"To measure the persistence or long-memory properties of the time series.","supports_evidence":["hurst exponent"]},{"tool":"noise_decomposition","reason":"To decompose the series and calculate the residual noise ratio.","supports_evidence":["noise ratio"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_counts","input_binding":{"series_index":"$step1.series_index"}},{"step":3,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":4,"tool":"noise_decomposition","output_key":"residual_noise","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio."},"structured_observations":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}],"coverage":{"endpoint_slope":"tool_supported","discrete step level counts":"tool_supported","hurst exponent":"tool_supported","noise ratio":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":37.492,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":1547.3769230769233,"std":495.0841749002753,"start_value":996.5,"end_value":1933.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"short:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":17,"n_plateau_runs":26,"levels":[996.5,927.9,969.0,905.2,863.0,1132.7,1813.2,1459.5,1855.6,1633.2,2000.0,2261.2,1893.6,2226.3,2191.4,2061.6,1933.8],"plateau_runs":[996.5,927.9,969.0,905.2,1003.7,929.1,990.0,863.0,1132.7,944.0,1813.2,1459.5,1855.6,1474.2,1633.2,2000.0,2261.2,1893.6,2226.3,1986.9,2191.4,1881.1,2061.6,1886.7,2012.4,1933.8],"plateau_lengths":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":20.165},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"short:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.22606695057982257,"persistence_hint":"anti_persistent","estimator":"fallback_lag_diff","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":26,"kind":"fallback","simplified":true,"warnings":["strong_endpoint_trend_may_bias_hurst","compute_Hc_failed_used_fallback:Series length must be greater or equal to 100"]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"short:step4","step":4,"tool_name":"noise_decomposition","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":6,"residual_std":181.23646428852527,"residual_rmse":197.9878576035802,"series_std":495.0841749002753,"residual_var":32846.65598780589,"series_var":245108.34023668637,"stl_noise_ratio":0.134008724289381,"highpass_noise_ratio":0.1926347599384566,"noise_ratio":0.1926347599384566,"noise_level":"low","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.15640392537936798,"trend_strength":0.8647207235988733,"noise_type_hint":"gauss_like","acf_lag1":0.8325574770146307,"warnings":[]},"error":null,"args_fingerprint":"909854aa026a467bebd5ecbc24b3a7475254db9c"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth. There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series. The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion. The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality.","structured_by_scale":{"short":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the candidate Time Series with the highest similarity to Time Series 1 based on pattern. Previous analysis provides detailed short-term measurements for Time Series 1, including endpoint slope, step-level count, persistence, and residual noise ratio. These features help establish a baseline for Time Series 1, but the current task specifically requires a pairwise similarity measure to compare it against its candidates.",
  "evidence_plan": {
    "objective": "Identify the candidate Time Series with the highest similarity to Time Series 1.",
    "claims_to_support": [
      {
        "claim": "Pairwise similarity measure exists between Time Series 1 and its candidates.",
        "required_evidence": ["pairwise_similarity"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["Ensure comparison is made only between Time Series 1 and its candidates."]
  },
  "capability_selection": {
    "selected_tools": [
      "pairwise_distance"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=5329 completion=762 latency=29.64s

### INPUT (system)

```
You are a Heterogeneous Agent (role=matching) at Stage 5: Evidence Integration.
Produce reasoning evidence with provenance. You do NOT call tools.
Numbers must come from executed_steps or cited upstream temporal_profile evidence.

Coverage confidence:
- tool_supported: successful local executed_steps call_id
- context_supported: upstream Homo / prior evidence (executed_steps may be empty)
- unresolved / qualified as appropriate

When option_to_series is present, candidate_preference is an OPTION LETTER;
invert option_to_series exactly from winning series_index.

When <candidates> are present (choice question):
- You MUST set candidate_preference to one letter A-D when tool/upstream numbers
  support a clear option, OR leave it null and list unresolved_claims — never invent.
- Align wording with option labels in the question (use question thresholds if present);
  do not say "strong"/"weak"/"low" unless that label matches the numeric comparison.

executed_tools and tool_summaries are system-owned — emit them as [].
Cite exact call_id values that exist (local or upstream). Never invent call_ids.

Output ONLY JSON (TaskEvidence body; role set by runtime):
{
  "reasoning": "string",
  "role": "matching",
  "hypothesis": "string",
  "evidence": ["string"],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "string",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.0,
          "provenance": "upstream",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": []
}

```

### INPUT (user)

```
<evidence_capability_plan>
{"evidence_plan":{"objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The analysis includes evaluating the endpoint slope of Time Series 1 as an indicator of its short-term behavior, counting the distinct step levels, measuring the Hurst exponent for persistence, and calculating the residual noise ratio.","scale":"short","observations":["Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth.","There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series.","The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion.","The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality."],"evidence_intervals":["From the execution of the segment_trend tool, we found the endpoint slope of Time Series 1.","Using the step_levels tool, we identified the number of unique step levels in Time Series 1.","The hurst_exponent tool provided the Hurst exponent, giving us information about the persistence of the series.","The noise_decomposition tool calculated the residual noise ratio for Time Series 1."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 37.492, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 1547.3769230769233, \"std\": 495.0841749002753, \"start_value\": 996.5, \"end_value\": 1933.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 17, \"n_plateau_runs\": 26, \"levels\": [996.5, 927.9, 969.0, 905.2, 863.0, 1132.7, 1813.2, 1459.5, 1855.6, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 2191.4, 2061.6, 1933.8], \"plateau_runs\": [996.5, 927.9, 969.0, 905.2, 1003.7, 929.1, 990.0, 863.0, 1132.7, 944.0, 1813.2, 1459.5, 1855.6, 1474.2, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 1986.9, 2191.4, 1881.1, 2061.6, 1886.7, 2012.4, 1933.8], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 20.165}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.22606695057982257, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"fallback_lag_diff\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 26, \"kind\": \"fallback\", \"simplified\": true, \"warnings\": [\"strong_endpoint_trend_may_bias_hurst\", \"compute_Hc_failed_used_fallback:Series length must be greater or equal to 100\"]}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 6, \"residual_std\": 181.23646428852527, \"residual_rmse\": 197.9878576035802, \"series_std\": 495.0841749002753, \"residual_var\": 32846.65598780589, \"series_var\": 245108.34023668637, \"stl_noise_ratio\": 0.134008724289381, \"highpass_noise_ratio\": 0.1926347599384566, \"noise_ratio\": 0.1926347599384566, \"noise_level\": \"low\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.15640392537936798, \"trend_strength\": 0.8647207235988733, \"noise_type_hint\": \"gauss_like\", \"acf_lag1\": 0.8325574770146307, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"909854aa026a467bebd5ecbc24b3a7475254db9c\"}"],"evidence_plan":{"objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","claims_to_support":[{"claim":"Time Series 1 has a specific endpoint slope indicative of its short-term behavior.","required_evidence":["slope"]},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","required_evidence":["discrete step level counts"]},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","required_evidence":["hurst exponent"]},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","required_evidence":["noise ratio"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"short"},"validation_needs":["Recheck consistency across all short-term measurements."]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To capture the endpoint slope indicative of short-term behavior.","supports_evidence":["slope"]},{"tool":"step_levels","reason":"To count the discrete step levels representing distinct changes in levels.","supports_evidence":["discrete step level counts"]},{"tool":"hurst_exponent","reason":"To measure the persistence or long-memory properties of the time series.","supports_evidence":["hurst exponent"]},{"tool":"noise_decomposition","reason":"To decompose the series and calculate the residual noise ratio.","supports_evidence":["noise ratio"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_counts","input_binding":{"series_index":"$step1.series_index"}},{"step":3,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":4,"tool":"noise_decomposition","output_key":"residual_noise","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio."},"structured_observations":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}],"coverage":{"endpoint_slope":"tool_supported","discrete step level counts":"tool_supported","hurst exponent":"tool_supported","noise ratio":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":37.492,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":1547.3769230769233,"std":495.0841749002753,"start_value":996.5,"end_value":1933.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"short:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":17,"n_plateau_runs":26,"levels":[996.5,927.9,969.0,905.2,863.0,1132.7,1813.2,1459.5,1855.6,1633.2,2000.0,2261.2,1893.6,2226.3,2191.4,2061.6,1933.8],"plateau_runs":[996.5,927.9,969.0,905.2,1003.7,929.1,990.0,863.0,1132.7,944.0,1813.2,1459.5,1855.6,1474.2,1633.2,2000.0,2261.2,1893.6,2226.3,1986.9,2191.4,1881.1,2061.6,1886.7,2012.4,1933.8],"plateau_lengths":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":20.165},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"short:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.22606695057982257,"persistence_hint":"anti_persistent","estimator":"fallback_lag_diff","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":26,"kind":"fallback","simplified":true,"warnings":["strong_endpoint_trend_may_bias_hurst","compute_Hc_failed_used_fallback:Series length must be greater or equal to 100"]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"short:step4","step":4,"tool_name":"noise_decomposition","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":6,"residual_std":181.23646428852527,"residual_rmse":197.9878576035802,"series_std":495.0841749002753,"residual_var":32846.65598780589,"series_var":245108.34023668637,"stl_noise_ratio":0.134008724289381,"highpass_noise_ratio":0.1926347599384566,"noise_ratio":0.1926347599384566,"noise_level":"low","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.15640392537936798,"trend_strength":0.8647207235988733,"noise_type_hint":"gauss_like","acf_lag1":0.8325574770146307,"warnings":[]},"error":null,"args_fingerprint":"909854aa026a467bebd5ecbc24b3a7475254db9c"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth. There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series. The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion. The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality.","structured_by_scale":{"short":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Without direct pairwise similarity measurements between Time Series 1 and the candidates, I rely on indirect contextual features like trend, step levels, and noise to infer similarity.",
  "role": "matching",
  "hypothesis": "The candidate with the most matching short-term trend indicators, step level patterns, and noise properties likely resembles Time Series 1 the closest.",
  "evidence": [
    "The endpoint slope of Time Series 1 is approximately 37.5, indicative of short-term upward growth.",
    "There are 17 unique step levels in Time Series 1, showing 17 discrete changes.",
    "The Hurst exponent for Time Series 1 is about 0.23, indicating anti-persistent behavior or mean reversion.",
    "The residual noise ratio for Time Series 1 is approximately 0.19, meaning around 19% of variability is not explained."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "short:step3", "short:step4"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 1 has an endpoint slope indicative of its short-term behavior.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 37.492,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.",
      "evidence": [
        {
          "type": "discrete step level counts",
          "value": 17,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.",
      "evidence": [
        {
          "type": "hurst exponent",
          "value": 0.22606695057982257,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.",
      "evidence": [
        {
          "type": "noise ratio",
          "value": 0.1926347599384566,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step4"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "endpoint_slope": "tool_supported",
    "discrete step level counts": "tool_supported",
    "hurst exponent": "tool_supported",
    "noise ratio": "tool_supported"
  },
  "unresolved_claims": [
    "Pairwise similarity metrics between Time Series 1 and its candidate sequences are needed for direct comparisons, but not available locally or in upstream data."
  ]
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=6716 completion=252 latency=11.12s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=matching.
Stage: Evidence Planning + Capability Selection (S1+S2 merged).
You reconcile upstream Temporal Profile / prior evidence for your assignment.
You do NOT invent tool argument formats. You do NOT make the irrevocable final system answer.

Role focus:
- structure: structural awareness and feature analysis
- reasoning: temporal reasoning; causal claims are statistical clues only
- matching: sequence similarity / localization / reverse / robust matching
- alignment: time-series <-> semantic description alignment

Your job:
1. Restate what claims need evidence given the assignment and what Homo already provided.
2. Select tools only for gaps or validation needs; otherwise selected_tools=[] with no_tool_decision.
3. Semantic capability matching against the library below — not keyword hard-routing.

Tool capability library:
Tool capability library (for selection only; do NOT invent argument formats here):

- describe_series: Descriptive stats for EVERY series: mean/std/min/max/median/range/p50/p90/p99/slope (preferred multi-series overview).
  produces: series
  use_when: Need an initial global statistical overview or exact basic statistics.
  avoid_when: The requested fact is local to a window or concerns temporal ordering only.
  limitations: Global summaries can hide local regimes, timing, and waveform shape.
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  produces: series
  use_when: Turning-point counts or local peak/trough locations are required.
  avoid_when: Counting plateaus/step levels, or only global extrema, is requested.
  limitations: Prominence filtering may omit weak extrema; not a substitute for step_levels.
- global_extrema: Global max/min indices and values; optional index classifies a point as global/local peak/trough (Base index tasks).
  produces: series
  use_when: Global extrema values/locations or classification of one index is required.
  avoid_when: All local turning points or anomaly scores are requested.
  limitations: Tie breaking uses earliest maximum and latest minimum.
- fft_period: Dominant period via FFT.
  produces: dominant_period, spectral_strength, period_trusted
  use_when: A dominant spectral period candidate is needed.
  avoid_when: A full-series-length period or weak peak would be accepted without validation.
  limitations: Trend/leakage can select very long periods; validate weak or boundary estimates.; spectral_strength is NOT seasonal_strength.; period_trusted=false when dominant_period is near series length or half-length.; FFT period alone does not identify waveform type (sine/square/triangle/sawtooth).
  often_combined_with: stl_strength, autocorr, waveform_features
- waveform_features: Classify waveform shape (sine/square/triangle/sawtooth/ambiguous) using jump ratio, plateau clustering, harmonic structure, and folded-template match. Do NOT treat FFT period alone as evidence of a sine wave.
  produces: waveform_hint, jump_ratio, template_match
  use_when: The question asks which waveform type (sine/square/triangle/sawtooth) a series resembles.; Shape discrimination is needed beyond period or seasonal strength.
  avoid_when: Only period/seasonal strength is needed without shape type.; Matching across candidate series (use pairwise/robust matching instead).
  limitations: periodicity_is_not_waveform_type: FFT period alone never implies sine.; Hints can be ambiguous under heavy noise or non-periodic shapes.
  often_combined_with: fft_period, step_levels, diff_stats
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  produces: distances, nearest, method
  use_when: One query series must be ranked against multiple candidate series.
  avoid_when: Reverse, subsequence, or robust-outlier matching semantics are required.
  limitations: Distance meaning depends on normalization/method; unequal lengths may be truncated.
- reverse_match: Reverse each candidate series and rank candidates against the query using length-normalized z-DTW or Euclidean distance.
  produces: ranking
  use_when: Candidates must be reversed before comparison with a query.
  avoid_when: Ordinary forward matching or trend direction alone is requested.
  limitations: Winner reliability depends on distance margin and method fallback.
- robust_shape_match: Robust candidate ranking using winsorization, smoothing, z-distance, correlation distance, and DTW with an explicit winner margin.
  produces: ranking
  use_when: Candidate ranking must tolerate spikes, scaling, and moderate noise.
  avoid_when: Exact raw-value equality or explicit reverse matching is required.
  limitations: Depends on smoothing/winsorization; small margins can be ambiguous.
- smooth_reverse_stats: Smoothing and reverse-direction stats.
  produces: series
  use_when: Auxiliary direction summaries before and after reversal are needed.
  avoid_when: A winning candidate or similarity ranking is required.
  limitations: Does not compare a query or identify a winner.
- smooth_shape_match: MMTS smooth-it matching: apply centered moving-average (default window=3) to candidates, then rank by DTW/euclidean distance to the query series.
  produces: nearest, ranking
  use_when: MMTS smooth-it: rank candidates after moving-average smoothing.
  avoid_when: Candidates must not be smoothed or reverse matching is required.
  limitations: Default window=3 matches MMTS SmoothitProcessor; distance depends on method.
  often_combined_with: pairwise_distance, robust_shape_match
- subsequence_locate: Locate best matching subsequence of a query inside a longer series. Default method=dtw (MMTS find-it); method=euclidean uses z-normalized L2.
  produces: best_start, best_end, distance
  use_when: MMTS find-it: locate a short query inside a longer series (prefer method=dtw).
  avoid_when: Whole-series candidate ranking is required.
  limitations: Default method=dtw via dtaidistance; euclidean is a faster fallback.
- subsequence_rank: Match find-it multi-candidate ranking: sliding-window DTW of a short query against each longer candidate; returns nearest by distance.
  produces: nearest, ranking
  use_when: Match find-it: rank several longer candidates against one short query via sliding DTW.
  avoid_when: Whole-series choose-it ranking (use pairwise_distance) or single long series locate.
  limitations: Calls sliding DTW per candidate; expensive on long series.
  often_combined_with: subsequence_locate, pairwise_distance

Output ONLY JSON (EvidenceCapabilityPlan):
{
  "reasoning": "string",
  "evidence_plan": {
    "objective": "string",
    "claims_to_support": [
      {"claim": "string", "required_evidence": ["string"]}
    ],
    "analysis_scope": {"target_series": [1], "role": "matching"},
    "validation_needs": ["string"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "string",
      "evidence_sources": [{"type": "upstream_observation", "ref": "string", "field": "string"}]
    }
  }
}
When tools are needed, put them in selected_tools and set no_tool_decision to null.

```

### INPUT (user)

```
<assignment>
{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires comparing Time Series 1 against four candidate series to find the most similar one based on pattern. This involves examining patterns from a short-term variation perspective and using a matching approach to quantify similarity.","task_summary":"Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.","target_output":"A|B|C|D","answer_type":"choice","capability":"matching","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","required_measurements":["endpoint_slope","step_level_count","persistence","residual_noise_ratio"],"validation_requirements":["Recheck consistency across all short-term measurements."],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All four candidate series are compared against Time Series 1","Each pairwise comparison measure is computed and considered","The candidate with the highest similarity score is selected as the answer"],"notes":"Pattern similarity should be evaluated holistically by combining insights from short-term analysis."}
</plan_context>

<task_summary>
Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The analysis includes evaluating the endpoint slope of Time Series 1 as an indicator of its short-term behavior, counting the distinct step levels, measuring the Hurst exponent for persistence, and calculating the residual noise ratio.","scale":"short","observations":["Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth.","There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series.","The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion.","The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality."],"evidence_intervals":["From the execution of the segment_trend tool, we found the endpoint slope of Time Series 1.","Using the step_levels tool, we identified the number of unique step levels in Time Series 1.","The hurst_exponent tool provided the Hurst exponent, giving us information about the persistence of the series.","The noise_decomposition tool calculated the residual noise ratio for Time Series 1."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 37.492, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 1547.3769230769233, \"std\": 495.0841749002753, \"start_value\": 996.5, \"end_value\": 1933.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 17, \"n_plateau_runs\": 26, \"levels\": [996.5, 927.9, 969.0, 905.2, 863.0, 1132.7, 1813.2, 1459.5, 1855.6, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 2191.4, 2061.6, 1933.8], \"plateau_runs\": [996.5, 927.9, 969.0, 905.2, 1003.7, 929.1, 990.0, 863.0, 1132.7, 944.0, 1813.2, 1459.5, 1855.6, 1474.2, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 1986.9, 2191.4, 1881.1, 2061.6, 1886.7, 2012.4, 1933.8], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 20.165}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.22606695057982257, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"fallback_lag_diff\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 26, \"kind\": \"fallback\", \"simplified\": true, \"warnings\": [\"strong_endpoint_trend_may_bias_hurst\", \"compute_Hc_failed_used_fallback:Series length must be greater or equal to 100\"]}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 6, \"residual_std\": 181.23646428852527, \"residual_rmse\": 197.9878576035802, \"series_std\": 495.0841749002753, \"residual_var\": 32846.65598780589, \"series_var\": 245108.34023668637, \"stl_noise_ratio\": 0.134008724289381, \"highpass_noise_ratio\": 0.1926347599384566, \"noise_ratio\": 0.1926347599384566, \"noise_level\": \"low\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.15640392537936798, \"trend_strength\": 0.8647207235988733, \"noise_type_hint\": \"gauss_like\", \"acf_lag1\": 0.8325574770146307, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"909854aa026a467bebd5ecbc24b3a7475254db9c\"}"],"evidence_plan":{"objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","claims_to_support":[{"claim":"Time Series 1 has a specific endpoint slope indicative of its short-term behavior.","required_evidence":["slope"]},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","required_evidence":["discrete step level counts"]},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","required_evidence":["hurst exponent"]},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","required_evidence":["noise ratio"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"short"},"validation_needs":["Recheck consistency across all short-term measurements."]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To capture the endpoint slope indicative of short-term behavior.","supports_evidence":["slope"]},{"tool":"step_levels","reason":"To count the discrete step levels representing distinct changes in levels.","supports_evidence":["discrete step level counts"]},{"tool":"hurst_exponent","reason":"To measure the persistence or long-memory properties of the time series.","supports_evidence":["hurst exponent"]},{"tool":"noise_decomposition","reason":"To decompose the series and calculate the residual noise ratio.","supports_evidence":["noise ratio"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_counts","input_binding":{"series_index":"$step1.series_index"}},{"step":3,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":4,"tool":"noise_decomposition","output_key":"residual_noise","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio."},"structured_observations":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}],"coverage":{"endpoint_slope":"tool_supported","discrete step level counts":"tool_supported","hurst exponent":"tool_supported","noise ratio":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":37.492,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":1547.3769230769233,"std":495.0841749002753,"start_value":996.5,"end_value":1933.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"short:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":17,"n_plateau_runs":26,"levels":[996.5,927.9,969.0,905.2,863.0,1132.7,1813.2,1459.5,1855.6,1633.2,2000.0,2261.2,1893.6,2226.3,2191.4,2061.6,1933.8],"plateau_runs":[996.5,927.9,969.0,905.2,1003.7,929.1,990.0,863.0,1132.7,944.0,1813.2,1459.5,1855.6,1474.2,1633.2,2000.0,2261.2,1893.6,2226.3,1986.9,2191.4,1881.1,2061.6,1886.7,2012.4,1933.8],"plateau_lengths":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":20.165},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"short:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.22606695057982257,"persistence_hint":"anti_persistent","estimator":"fallback_lag_diff","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":26,"kind":"fallback","simplified":true,"warnings":["strong_endpoint_trend_may_bias_hurst","compute_Hc_failed_used_fallback:Series length must be greater or equal to 100"]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"short:step4","step":4,"tool_name":"noise_decomposition","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":6,"residual_std":181.23646428852527,"residual_rmse":197.9878576035802,"series_std":495.0841749002753,"residual_var":32846.65598780589,"series_var":245108.34023668637,"stl_noise_ratio":0.134008724289381,"highpass_noise_ratio":0.1926347599384566,"noise_ratio":0.1926347599384566,"noise_level":"low","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.15640392537936798,"trend_strength":0.8647207235988733,"noise_type_hint":"gauss_like","acf_lag1":0.8325574770146307,"warnings":[]},"error":null,"args_fingerprint":"909854aa026a467bebd5ecbc24b3a7475254db9c"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth. There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series. The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion. The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality.","structured_by_scale":{"short":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
retry_context=unresolved_claims=['Pairwise similarity metrics between Time Series 1 and its candidate sequences are needed for direct comparisons, but not available locally or in upstream data.']
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides detailed analyses of Time Series 1, including endpoint slope, step levels, persistence, and residual noise ratio. However, to determine the highest similarity between Time Series 1 and its candidate sequences, pairwise similarity metrics are required. No such direct comparisons are present in the existing data.",
  "evidence_plan": {
    "objective": "Identify the candidate Time Series with the highest similarity to Time Series 1.",
    "claims_to_support": [
      {
        "claim": "Calculate pairwise similarity between Time Series 1 and its candidates.",
        "required_evidence": ["pairwise_similarity"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["Ensure comparison is made only between Time Series 1 and its candidates."]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "pairwise_distance",
        "reason": "To compute the pairwise similarity metrics between Time Series 1 and each candidate.",
        "supports_evidence": ["pairwise_similarity"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m1`

tokens prompt=605 completion=112 latency=4.03s

### INPUT (system)

```
You are a Heterogeneous Agent (role=matching) at Stage 3: Tool Workflow Planning.
Design an ordered pipeline for selected tools. Use IO concepts for dependencies.
Do NOT fill concrete literals except $stepN.field / $RealToolName.field bindings.
Use input_binding ONLY for dependent parameters from prior steps (e.g. period from fft_period.dominant_period).
Do NOT bind series / series_index here — Stage 4 supplies series_index literals.
Never write "$tool.series", "$step1.series", "$series....", or "$candidate_series_indices[...]".
Referenced fields must exist on the prior tool's outputs..
If selected_tools is empty, return workflow: [].

Output ONLY JSON (ToolWorkflow):
{
  "reasoning": "string",
  "workflow": [
    {
      "step": 1,
      "tool": "cross_series_compare",
      "output_key": "pair_compare",
      "input_binding": {}
    }
  ]
}

```

### INPUT (user)

```
<evidence_capability_plan>
{"evidence_plan":{"objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","claims_to_support":[{"claim":"Calculate pairwise similarity between Time Series 1 and its candidates.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["Ensure comparison is made only between Time Series 1 and its candidates."]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"To compute the pairwise similarity metrics between Time Series 1 and each candidate.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The current evidence provides detailed analyses of Time Series 1, including endpoint slope, step levels, persistence, and residual noise ratio. However, to determine the highest similarity between Time Series 1 and its candidate sequences, pairwise similarity metrics are required. No such direct comparisons are present in the existing data."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
</io_concepts>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the candidate Time Series with the highest similarity to Time Series 1. The selected tool, pairwise_distance, will calculate the pairwise similarity metrics between Time Series 1 and its candidates. The output will provide the necessary evidence for comparison.",
  "workflow": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "output_key": "distances",
      "input_binding": {
        "series_index": 1
      }
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m1`

tokens prompt=767 completion=102 latency=3.72s

### INPUT (system)

```
You are a Heterogeneous Agent (role=matching) at Stage 4: Tool Invocation.
Fill arguments for the workflow using the invocation spec.
Do NOT change the workflow. calls[].step/tool MUST match the workflow one-to-one.
Use $stepN.field only for fields that exist in step N's tool output.
Never use $candidate_series_indices[i] / $query_series_index — pass literal series_index ints from metadata.
Omit optional keys; never JSON null. Never paste raw series arrays.

Candidate mapping (when relevant):
- series_index values are series IDs; option letters come later in Stage 5 via option_to_series.

Output ONLY JSON (InvocationPlan):
{
  "reasoning": "string",
  "calls": [
    {"step": 1, "tool": "cross_series_compare", "args": {"series_index_1": 1, "series_index_2": 2}}
  ]
}

```

### INPUT (user)

```
<workflow>
{"workflow":[{"step":1,"tool":"pairwise_distance","output_key":"distances","input_binding":{"series_index":1}}],"reasoning":"The objective is to identify the candidate Time Series with the highest similarity to Time Series 1. The selected tool, pairwise_distance, will calculate the pairwise similarity metrics between Time Series 1 and its candidates. The output will provide the necessary evidence for comparison."}
</workflow>

<tool_invocation_spec>
Runtime tool invocation protocol:
- Tools read pipeline-bound series; NEVER paste raw numeric arrays into arguments.
- Optional parameters: omit the key; never JSON null.
- Multi-round / workflow: pass numeric literals OR $stepN.field references resolved by Runtime.
- Placeholders/strings naming other tools are not valid argument values.
- Use series_index (1-based): int, list like [1,2,3], 'Time Series 2', or 'all'.
- If n_series>1 and series_index is omitted, tools fan out over ALL series.
- lag_corr is pairwise: use series_index_1/2 as ints, or set either to 'all' for all pairs.
- Optional window args: start/end (inclusive indices), window (alias window_size).

- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  args: {method=euclidean|dtw, series_index=reference 1-based (default 1)}
  returns: {distances=per-candidate distances, nearest=winner, method=distance metadata}
</tool_invocation_spec>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<assignment>
{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}
</assignment>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the candidate Time Series with the highest similarity to Time Series 1. The selected tool, pairwise_distance, will calculate the pairwise similarity metrics between Time Series 1 and its candidates. The output will provide the necessary evidence for comparison.",
  "calls": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=5757 completion=314 latency=13.16s

### INPUT (system)

```
You are a Heterogeneous Agent (role=matching) at Stage 5: Evidence Integration.
Produce reasoning evidence with provenance. You do NOT call tools.
Numbers must come from executed_steps or cited upstream temporal_profile evidence.

Coverage confidence:
- tool_supported: successful local executed_steps call_id
- context_supported: upstream Homo / prior evidence (executed_steps may be empty)
- unresolved / qualified as appropriate

When option_to_series is present, candidate_preference is an OPTION LETTER;
invert option_to_series exactly from winning series_index.

When <candidates> are present (choice question):
- You MUST set candidate_preference to one letter A-D when tool/upstream numbers
  support a clear option, OR leave it null and list unresolved_claims — never invent.
- Align wording with option labels in the question (use question thresholds if present);
  do not say "strong"/"weak"/"low" unless that label matches the numeric comparison.

executed_tools and tool_summaries are system-owned — emit them as [].
Cite exact call_id values that exist (local or upstream). Never invent call_ids.

Output ONLY JSON (TaskEvidence body; role set by runtime):
{
  "reasoning": "string",
  "role": "matching",
  "hypothesis": "string",
  "evidence": ["string"],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "string",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.0,
          "provenance": "upstream",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": []
}

```

### INPUT (user)

```
<evidence_capability_plan>
{"evidence_plan":{"objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","claims_to_support":[{"claim":"Calculate pairwise similarity between Time Series 1 and its candidates.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["Ensure comparison is made only between Time Series 1 and its candidates."]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"To compute the pairwise similarity metrics between Time Series 1 and each candidate.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The current evidence provides detailed analyses of Time Series 1, including endpoint slope, step levels, persistence, and residual noise ratio. However, to determine the highest similarity between Time Series 1 and its candidate sequences, pairwise similarity metrics are required. No such direct comparisons are present in the existing data."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "matching:step1",
    "step": 1,
    "tool_name": "pairwise_distance",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "method": "euclidean",
      "ref_series_index": 1,
      "distances": [
        {
          "series_index": 2,
          "distance": 7.90228737506825
        },
        {
          "series_index": 3,
          "distance": 1.8586185776839583
        },
        {
          "series_index": 4,
          "distance": 0.9058502693995862
        },
        {
          "series_index": 5,
          "distance": 5.533991983714736
        }
      ],
      "nearest": {
        "series_index": 4,
        "distance": 0.9058502693995862
      }
    },
    "error": null,
    "args_fingerprint": "a3958760584c2feb2263ddddaa8bcefdc46f8a4f"
  }
]
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The analysis includes evaluating the endpoint slope of Time Series 1 as an indicator of its short-term behavior, counting the distinct step levels, measuring the Hurst exponent for persistence, and calculating the residual noise ratio.","scale":"short","observations":["Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth.","There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series.","The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion.","The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality."],"evidence_intervals":["From the execution of the segment_trend tool, we found the endpoint slope of Time Series 1.","Using the step_levels tool, we identified the number of unique step levels in Time Series 1.","The hurst_exponent tool provided the Hurst exponent, giving us information about the persistence of the series.","The noise_decomposition tool calculated the residual noise ratio for Time Series 1."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 37.492, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 1547.3769230769233, \"std\": 495.0841749002753, \"start_value\": 996.5, \"end_value\": 1933.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 17, \"n_plateau_runs\": 26, \"levels\": [996.5, 927.9, 969.0, 905.2, 863.0, 1132.7, 1813.2, 1459.5, 1855.6, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 2191.4, 2061.6, 1933.8], \"plateau_runs\": [996.5, 927.9, 969.0, 905.2, 1003.7, 929.1, 990.0, 863.0, 1132.7, 944.0, 1813.2, 1459.5, 1855.6, 1474.2, 1633.2, 2000.0, 2261.2, 1893.6, 2226.3, 1986.9, 2191.4, 1881.1, 2061.6, 1886.7, 2012.4, 1933.8], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 20.165}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.22606695057982257, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"fallback_lag_diff\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 26, \"kind\": \"fallback\", \"simplified\": true, \"warnings\": [\"strong_endpoint_trend_may_bias_hurst\", \"compute_Hc_failed_used_fallback:Series length must be greater or equal to 100\"]}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 6, \"residual_std\": 181.23646428852527, \"residual_rmse\": 197.9878576035802, \"series_std\": 495.0841749002753, \"residual_var\": 32846.65598780589, \"series_var\": 245108.34023668637, \"stl_noise_ratio\": 0.134008724289381, \"highpass_noise_ratio\": 0.1926347599384566, \"noise_ratio\": 0.1926347599384566, \"noise_level\": \"low\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.15640392537936798, \"trend_strength\": 0.8647207235988733, \"noise_type_hint\": \"gauss_like\", \"acf_lag1\": 0.8325574770146307, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"909854aa026a467bebd5ecbc24b3a7475254db9c\"}"],"evidence_plan":{"objective":"Analyze local variations and changes in Time Series 1 and each candidate sequence.","claims_to_support":[{"claim":"Time Series 1 has a specific endpoint slope indicative of its short-term behavior.","required_evidence":["slope"]},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","required_evidence":["discrete step level counts"]},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","required_evidence":["hurst exponent"]},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","required_evidence":["noise ratio"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"short"},"validation_needs":["Recheck consistency across all short-term measurements."]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To capture the endpoint slope indicative of short-term behavior.","supports_evidence":["slope"]},{"tool":"step_levels","reason":"To count the discrete step levels representing distinct changes in levels.","supports_evidence":["discrete step level counts"]},{"tool":"hurst_exponent","reason":"To measure the persistence or long-memory properties of the time series.","supports_evidence":["hurst exponent"]},{"tool":"noise_decomposition","reason":"To decompose the series and calculate the residual noise ratio.","supports_evidence":["noise ratio"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_counts","input_binding":{"series_index":"$step1.series_index"}},{"step":3,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":4,"tool":"noise_decomposition","output_key":"residual_noise","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective is to analyze the local variations and changes in Time Series 1 and its candidate sequences using the selected tools. The workflow starts with capturing the trend using `segment_trend` which provides the endpoint slope indicative of short-term behavior. Following that, `step_levels` tool is used to count the number of discrete step levels, then `hurst_exponent` measures persistence, and finally, `noise_decomposition` calculates the noise ratio."},"structured_observations":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}],"coverage":{"endpoint_slope":"tool_supported","discrete step level counts":"tool_supported","hurst exponent":"tool_supported","noise ratio":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":37.492,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":1547.3769230769233,"std":495.0841749002753,"start_value":996.5,"end_value":1933.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"short:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":17,"n_plateau_runs":26,"levels":[996.5,927.9,969.0,905.2,863.0,1132.7,1813.2,1459.5,1855.6,1633.2,2000.0,2261.2,1893.6,2226.3,2191.4,2061.6,1933.8],"plateau_runs":[996.5,927.9,969.0,905.2,1003.7,929.1,990.0,863.0,1132.7,944.0,1813.2,1459.5,1855.6,1474.2,1633.2,2000.0,2261.2,1893.6,2226.3,1986.9,2191.4,1881.1,2061.6,1886.7,2012.4,1933.8],"plateau_lengths":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":20.165},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"short:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.22606695057982257,"persistence_hint":"anti_persistent","estimator":"fallback_lag_diff","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":26,"kind":"fallback","simplified":true,"warnings":["strong_endpoint_trend_may_bias_hurst","compute_Hc_failed_used_fallback:Series length must be greater or equal to 100"]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"short:step4","step":4,"tool_name":"noise_decomposition","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":6,"residual_std":181.23646428852527,"residual_rmse":197.9878576035802,"series_std":495.0841749002753,"residual_var":32846.65598780589,"series_var":245108.34023668637,"stl_noise_ratio":0.134008724289381,"highpass_noise_ratio":0.1926347599384566,"noise_ratio":0.1926347599384566,"noise_level":"low","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.15640392537936798,"trend_strength":0.8647207235988733,"noise_type_hint":"gauss_like","acf_lag1":0.8325574770146307,"warnings":[]},"error":null,"args_fingerprint":"909854aa026a467bebd5ecbc24b3a7475254db9c"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth. There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series. The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion. The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality.","structured_by_scale":{"short":[{"claim":"Time Series 1 has an endpoint slope indicative of its short-term behavior.","evidence":[{"type":"endpoint_slope","value":37.492,"source_tool":"segment_trend","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Time Series 1 contains a certain number of distinct step levels, reflecting its discrete level changes.","evidence":[{"type":"discrete step level counts","value":17,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"discrete step level counts"},{"claim":"Time Series 1 exhibits a certain level of persistence, indicative of its memory characteristics.","evidence":[{"type":"hurst exponent","value":0.22606695057982257,"source_tool":"hurst_exponent","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"hurst exponent"},{"claim":"Time Series 1 has a particular residual noise ratio, indicating the proportion of variability not captured by its trend and seasonal components.","evidence":[{"type":"noise ratio","value":0.1926347599384566,"source_tool":"noise_decomposition","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"noise ratio"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Identify the candidate Time Series with the highest similarity to Time Series 1.","required_measurements":["pairwise_similarity"],"validation_requirements":["Ensure comparison is made only between Time Series 1 and its candidates."],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[26, 26, 26, 26, 26]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the calculated pairwise distances, Time Series 1 shows the smallest distance (highest similarity) with Time Series 4.",
  "role": "matching",
  "hypothesis": "Time Series 4 has the highest similarity to Time Series 1.",
  "evidence": [
    "The pairwise distance between Time Series 1 and its candidates indicates the lowest distance (0.9058502693995862) with Time Series 4."
  ],
  "candidate_preference": "C",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "matching:step1"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The smallest pairwise distance (highest similarity) exists between Time Series 1 and Time Series 4.",
      "evidence": [
        {
          "type": "pairwise_similarity",
          "value": 0.9058502693995862,
          "provenance": "tool",
          "ref": "pairwise_distance",
          "call_id": "matching:step1"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "pairwise_similarity": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1517 completion=189 latency=6.98s

### INPUT (system)

```
You are the Integration Agent.
You do NOT call tools.
Produce the final answer from three upstream layers only:
1. Planner intent — what must be answered.
2. Homo perception — temporal states (not tool traces).
3. Heter reasoning — grounded interpretations of those states.

Procedure:
1. Read required output from planner intent.
2. Extract trusted Homo numeric/categorical states.
3. If <question> embeds numeric thresholds for option labels:
   a. Parse intervals/labels from the question (do not invent thresholds).
   b. Take the matching trusted homo value (e.g. seasonal_strength, noise_ratio, hurst).
   c. Compare value → interval → option semantics → letter.
   d. Fill decision_trace before setting answer.
   e. Do not let Heter qualitative words (strong/weak/low/high/moderate) override
      that comparison; if they disagree, keep the comparison and add a conflict.
4. Check Heter grounded / grounded_in / execution_metadata.
5. Always output a final answer (choice letter or numeric string). Record conflicts
   and lower confidence when evidence is missing, conflicting, or weakly grounded—
   still decide using your best synthesis; do not leave answer empty or default to "A".

Constraints:
- Do not invent new observations or inflate ungrounded Heter claims.
- Prefer perception states over unsupported interpretations.
- Choice → one letter; numerical → prefer a value present in perception, else best estimate + conflict.
- execution_metadata.verified_preference is a strong prior (Match/Align, waveform maps).

Output ONLY JSON (FinalAnswer):
{
  "reasoning": "string",
  "answer": "",
  "explanation": "string",
  "confidence": 0.0,
  "conflicts": ["string"],
  "cited_evidence": ["string"],
  "decision_trace": {
    "metric": "string or null",
    "observed_value": null,
    "intervals_from_question": ["string"],
    "matched_label": "string or null",
    "matched_letter": "string or null"
  }
}
If no numeric thresholds, set decision_trace fields to null/[].

```

### INPUT (user)

```
<question>
Which of the following four candidate sequences, each the same length as Time Series 1, has the most similar pattern to Time Series 1?
</question>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Compare Time Series 1 with four candidates to identify the one that has the most similar pattern.",
  "question_type": "choice",
  "required_output": "A|B|C|D",
  "success_criteria": [
    "All four candidate series are compared against Time Series 1",
    "Each pairwise comparison measure is computed and considered",
    "The candidate with the highest similarity score is selected as the answer"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Analyze local variations and changes in Time Series 1 and each candidate sequence.",
      "required_measurements": [
        "endpoint_slope",
        "step_level_count",
        "persistence",
        "residual_noise_ratio"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Identify the candidate Time Series with the highest similarity to Time Series 1.",
      "required_measurements": [
        "pairwise_similarity"
      ]
    }
  ]
}
</planner_intent>

<homo_perception>
{
  "by_scale": {
    "short": {
      "states": [
        {
          "series_index": null,
          "type": "endpoint_slope",
          "value": 37.492,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "discrete step level counts",
          "value": 17,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "hurst exponent",
          "value": 0.22606695057982257,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "noise ratio",
          "value": 0.1926347599384566,
          "trusted": true
        }
      ],
      "coverage": {
        "endpoint_slope": "tool_supported",
        "discrete step level counts": "tool_supported",
        "hurst exponent": "tool_supported",
        "noise ratio": "tool_supported"
      },
      "summary": "Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth. | There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series. | The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion. | The residual noise ratio for Time Series 1 is approximately 0.19, in"
    }
  },
  "conflicts": [],
  "summary": "Time Series 1 has an upward trend with an endpoint slope of approximately 37.5, indicating short-term growth. There are 17 unique step levels in Time Series 1, reflecting 17 distinct changes in the level of the series. The Hurst exponent for Time Series 1 is about 0.23, suggesting anti-persistent behavior or mean reversion. The residual noise ratio for Time Series 1 is approximately 0.19, indicating that around 19% of the series variability remains unexplained after accounting for trends and seasonality."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Time Series 4 has the highest similarity to Time Series 1.",
      "reasoning_chain": [
        "The smallest pairwise distance (highest similarity) exists between Time Series 1 and Time Series 4.",
        "pairwise_similarity=0.9058502693995862"
      ],
      "candidate_preference": "C",
      "confidence": 1.0,
      "grounded": true,
      "grounded_in": [
        "pairwise_similarity"
      ],
      "uncertainty": ""
    }
  ]
}
</heter_reasoning>

<execution_metadata>
{
  "option_mapping": {
    "A": 2,
    "B": 3,
    "C": 4,
    "D": 5
  },
  "verified_preference": "C",
  "verified": true,
  "warnings": []
}
</execution_metadata>

<question_rules>
- Match/Align: answer must be one candidate letter. Trust execution_metadata.option_mapping and verified_preference when present.
</question_rules>

Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "Heter reasoning identified Time Series 4 as the most similar to Time Series 1 based on pairwise similarity score. Execution metadata also verifies preference for option C.",
  "answer": "C",
  "explanation": "Based on pairwise similarity scores, Time Series 4 shows the highest similarity to Time Series 1. This is corroborated by the execution metadata which confirms preference for option C.",
  "confidence": 1.0,
  "conflicts": [],
  "cited_evidence": ["pairwise_similarity", "execution_metadata.verified_preference"],
  "decision_trace": {
    "metric": "pairwise_similarity",
    "observed_value": 0.9058502693995862,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "C"
  }
}
```
