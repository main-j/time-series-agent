# Agent IO summary: `InWild:tsqa_1084:913`

- Architecture pred: `A` (success=True)
- model_calls=16, tool_calls=5, latency=173.8s

## Planner — `planner`

tokens prompt=1315 completion=450 latency=16.07s

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
The seasonality analysis of the sequence can be performed using seasonal_strength & seas_acf1 as a reference metric. The calculation method is seasonal_strength: The `seasonal_strength` feature quantifies seasonality strength as $ 1 - \frac{\mathrm{Var}(R_t)}{\mathrm{Var}(S_t + R_t)} $, where $ S_t $ and $ R_t $ are the seasonal and remainder components. Higher values indicate stronger seasonal patterns; seas_acf1: The `seas_acf1` feature captures seasonal autocorrelation at lag $ m $: $ \rho_m(x) = \frac{\gamma_m(x)}{\gamma_0(x)} $, where $ \gamma_k(x) $ is the autocovariance and $ \gamma_0(x) $ is the variance. Values near ±1 imply strong seasonal correlation; near 0 implies weak seasonality. Now, please answer the following question: Based on the conclusions that a sequence with seas_acf1 close to ±1 and seasonal_strength close to 1 indicates strong and significant seasonality, and a sequence with seas_acf1 close to 0 and seasonal_strength close to 1 indicates strong but irregular or unstable seasonality, which of the following types does the sequence Time Series 3 belong to?
</question>

<candidates>
A) The periodic structure exists but is weak in explanatory power.
B) The seasonality is significant and strong.
C) The overall fluctuations appear to be seasonally strong but are unstable or irregular.
D) There is no clear seasonality.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires evaluating seasonality characteristics in a specific time series (Time Series 3) based on two metrics: seasonal_strength and seas_acf1. These metrics help determine if the seasonality is significant, stable, or irregular.",
  "task_summary": "Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.",
  "target_output": "The type of seasonality for Time Series 3 based on provided categories.",
  "answer_type": "choice",
  "capability": "Seasonality analysis using multiple metrics and comparison with predefined criteria.",
  "scope": "overall",
  "univariate": false,
  "homo_assignments": [
    {
      "scale": "long",
      "objective": "Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.",
      "required_measurements": ["seasonal_strength", "seas_acf1"],
      "validation_requirements": ["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],
      "target_series": [3],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.",
      "required_measurements": ["seasonal_strength", "seas_acf1"],
      "validation_requirements": ["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],
      "target_series": [3],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Accurate determination of seasonality type based on provided metrics and consistent with stated rules.", "Clear association of Time Series 3 with the correct categorical description of its seasonality characteristics."],
  "notes": "This plan leverages the long-scale view to encompass potential periodicities in Time Series 3 while utilizing reasoning to interpret these in light of given options."
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4108 completion=259 latency=10.31s

### INPUT (system)

```
You are a long-scale Homogeneous Temporal Understanding Agent.
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
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "long"},
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
{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating seasonality characteristics in a specific time series (Time Series 3) based on two metrics: seasonal_strength and seas_acf1. These metrics help determine if the seasonality is significant, stable, or irregular.","task_summary":"Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.","target_output":"The type of seasonality for Time Series 3 based on provided categories.","answer_type":"choice","capability":"Seasonality analysis using multiple metrics and comparison with predefined criteria.","scope":"overall","univariate":false,"homo_assignments":[{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Accurate determination of seasonality type based on provided metrics and consistent with stated rules.","Clear association of Time Series 3 with the correct categorical description of its seasonality characteristics."],"notes":"This plan leverages the long-scale view to encompass potential periodicities in Time Series 3 while utilizing reasoning to interpret these in light of given options."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires evaluating seasonality characteristics in Time Series 3 based on two metrics: seasonal_strength and seas_acf1. These metrics will help determine the significance, stability, or irregularity of the seasonality.",
  "evidence_plan": {
    "objective": "Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.",
    "claims_to_support": [
      {"claim": "Time Series 3 exhibits significant seasonality", "required_evidence": ["seasonal_strength"]},
      {"claim": "Time Series 3 has a strong seasonal autocorrelation", "required_evidence": ["seas_acf1"]}
    ],
    "analysis_scope": {"target_series": [3], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "seas_acf", "reason": "Measure seasonal autocorrelation and assess seasonality strength in the long term.", "supports_evidence": ["seas_acf1"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=771 completion=95 latency=3.45s

### INPUT (system)

```
You are a long-scale Homogeneous Agent at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measure seasonal autocorrelation and assess seasonality strength in the long term.","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"reasoning":"The task requires evaluating seasonality characteristics in Time Series 3 based on two metrics: seasonal_strength and seas_acf1. These metrics will help determine the significance, stability, or irregularity of the seasonality."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- seas_acf
  inputs: series_window, lag
  outputs: seas_acf1, strength_hint
  often_combined_with: autocorr, stl_strength, fft_period
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify global seasonality trends in Time Series 3 through long-range temporal inspection using the selected tools. The chosen tools should provide evidence of seasonality strength and seasonal autocorrelation.",
  "workflow": [
    {
      "step": 1,
      "tool": "seas_acf",
      "output_key": "seas_acf1",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=822 completion=118 latency=4.25s

### INPUT (system)

```
You are a long-scale Homogeneous Agent at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{}}],"reasoning":"The objective is to identify global seasonality trends in Time Series 3 through long-range temporal inspection using the selected tools. The chosen tools should provide evidence of seasonality strength and seasonal autocorrelation."}
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

- seas_acf: MMTS seas_acf1: seasonal autocorrelation ρ_m=γ_m/γ_0 at lag m (e.g. lag=26 for weekly half-year frequency).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, lag=required seasonal lag m (aliases: m, frequency, period)}
  returns: {series=seas_acf1 at lag m with strength_hint}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "To identify global seasonality trends in Time Series 3, we need to perform a seasonal autocorrelation (seas_acf) analysis on this specific series. Given the objective and the assignment details, we will use a seasonal lag appropriate for time series analysis that captures long-range temporal patterns.",
  "calls": [
    {
      "step": 1,
      "tool": "seas_acf",
      "args": {
        "series_index": 3,
        "lag": "auto"
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=889 completion=261 latency=9.26s

### INPUT (system)

```
You are a long-scale Homogeneous Agent at Stage 5: Evidence Integration.
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
  "scale": "long",
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
{"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measure seasonal autocorrelation and assess seasonality strength in the long term.","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"reasoning":"The task requires evaluating seasonality characteristics in Time Series 3 based on two metrics: seasonal_strength and seas_acf1. These metrics will help determine the significance, stability, or irregularity of the seasonality."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
    "step": 1,
    "tool_name": "seas_acf",
    "arguments": {
      "series_index": 3,
      "lag": "auto"
    },
    "resolved_arguments": {
      "series_index": 3,
      "lag": "auto"
    },
    "success": false,
    "data": {},
    "error": "invalid literal for int() with base 10: 'auto'",
    "args_fingerprint": ""
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "An attempt was made to measure the seasonal strength and autocorrelation of Time Series 3 using the seas_acf tool. However, the execution failed due to an error with setting the lag parameter.",
  "scale": "long",
  "observations": ["Failed to execute seas_acf tool due to invalid argument input for lag parameter."],
  "evidence_intervals": ["global"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Time Series 3 exhibits significant seasonality",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "seasonal_strength"
    },
    {
      "claim": "Time Series 3 has a strong seasonal autocorrelation",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "seas_acf1"
    }
  ],
  "coverage": {"seasonal_strength": "unresolved", "seas_acf1": "unresolved"},
  "unresolved_claims": [
    "Time Series 3 exhibits significant seasonality",
    "Time Series 3 has a strong seasonal autocorrelation"
  ]
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m1`

tokens prompt=4142 completion=330 latency=12.92s

### INPUT (system)

```
You are a long-scale Homogeneous Temporal Understanding Agent.
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
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "long"},
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
{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating seasonality characteristics in a specific time series (Time Series 3) based on two metrics: seasonal_strength and seas_acf1. These metrics help determine if the seasonality is significant, stable, or irregular.","task_summary":"Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.","target_output":"The type of seasonality for Time Series 3 based on provided categories.","answer_type":"choice","capability":"Seasonality analysis using multiple metrics and comparison with predefined criteria.","scope":"overall","univariate":false,"homo_assignments":[{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Accurate determination of seasonality type based on provided metrics and consistent with stated rules.","Clear association of Time Series 3 with the correct categorical description of its seasonality characteristics."],"notes":"This plan leverages the long-scale view to encompass potential periodicities in Time Series 3 while utilizing reasoning to interpret these in light of given options."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['Time Series 3 exhibits significant seasonality', 'Time Series 3 has a strong seasonal autocorrelation']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires evaluating seasonality characteristics in Time Series 3 based on two metrics: seasonal_strength and seas_acf1. These metrics will help determine the significance and consistency of seasonality across different intervals, taking into account potential noise and outliers.",
  "evidence_plan": {
    "objective": "Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.",
    "claims_to_support": [
      {
        "claim": "Time Series 3 exhibits significant seasonality",
        "required_evidence": ["seasonal_strength"]
      },
      {
        "claim": "Time Series 3 has a strong seasonal autocorrelation",
        "required_evidence": ["seas_acf1"]
      }
    ],
    "analysis_scope": {
      "target_series": [3],
      "focus_intervals": [],
      "scale": "long"
    },
    "validation_needs": ["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "stl_strength",
        "reason": "To measure the seasonal_strength of Time Series 3",
        "supports_evidence": ["seasonal_strength"]
      },
      {
        "tool": "seas_acf",
        "reason": "To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag",
        "supports_evidence": ["seas_acf1"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m1`

tokens prompt=859 completion=205 latency=7.30s

### INPUT (system)

```
You are a long-scale Homogeneous Agent at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"stl_strength","reason":"To measure the seasonal_strength of Time Series 3","supports_evidence":["seasonal_strength"]},{"tool":"seas_acf","reason":"To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"reasoning":"The task requires evaluating seasonality characteristics in Time Series 3 based on two metrics: seasonal_strength and seas_acf1. These metrics will help determine the significance and consistency of seasonality across different intervals, taking into account potential noise and outliers."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- seas_acf
  inputs: series_window, lag
  outputs: seas_acf1, strength_hint
  often_combined_with: autocorr, stl_strength, fft_period
- stl_strength
  inputs: series, period(optional; omit→auto capped FFT)
  outputs: period, seasonal_strength, season_strength_bin, trend_strength
  depends: period often bound from fft_period.dominant_period when trusted
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation.",
  "workflow": [
    {
      "step": 1,
      "tool": "fft_period",
      "output_key": "dominant_period",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "stl_strength",
      "output_key": "seasonal_strength",
      "input_binding": {"period": "$step1.dominant_period"}
    },
    {
      "step": 3,
      "tool": "seas_acf",
      "output_key": "seas_acf1",
      "input_binding": {"series_window": "$series", "lag": "$step1.dominant_period"}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m1`

tokens prompt=989 completion=197 latency=7.05s

### INPUT (system)

```
You are a long-scale Homogeneous Agent at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}},{"step":3,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"series_window":"$series","lag":"$step1.dominant_period"}}],"reasoning":"First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation."}
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

- seas_acf: MMTS seas_acf1: seasonal autocorrelation ρ_m=γ_m/γ_0 at lag m (e.g. lag=26 for weekly half-year frequency).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, lag=required seasonal lag m (aliases: m, frequency, period)}
  returns: {series=seas_acf1 at lag m with strength_hint}
- stl_strength: STL seasonal/trend strength.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, period=optional positive int | omit → auto via fft_period; never null/placeholder strings}
  returns: {series=period, period_trusted, seasonal_strength, season_strength_bin, trend_strength}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation.",
  "calls": [
    {
      "step": 1,
      "tool": "fft_period",
      "args": {
        "series_index": 3
      }
    },
    {
      "step": 2,
      "tool": "stl_strength",
      "args": {
        "series_index": 3,
        "period": "$step1.dominant_period"
      }
    },
    {
      "step": 3,
      "tool": "seas_acf",
      "args": {
        "series_index": 3,
        "lag": "$step1.dominant_period"
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m1`

tokens prompt=1574 completion=418 latency=15.02s

### INPUT (system)

```
You are a long-scale Homogeneous Agent at Stage 5: Evidence Integration.
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
  "scale": "long",
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
{"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"stl_strength","reason":"To measure the seasonal_strength of Time Series 3","supports_evidence":["seasonal_strength"]},{"tool":"seas_acf","reason":"To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"reasoning":"The task requires evaluating seasonality characteristics in Time Series 3 based on two metrics: seasonal_strength and seas_acf1. These metrics will help determine the significance and consistency of seasonality across different intervals, taking into account potential noise and outliers."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
    "step": 1,
    "tool_name": "fft_period",
    "arguments": {
      "series_index": 3
    },
    "resolved_arguments": {
      "series_index": 3
    },
    "success": true,
    "data": {
      "series_index": 3,
      "dominant_period": 720.0,
      "spectral_strength": 0.1298976066102109,
      "period_trusted": false,
      "warnings": [
        "dominant_period_near_series_length"
      ]
    },
    "error": null,
    "args_fingerprint": "2d03e2fbcc4f68587c50271d6bad3d182ff8a286"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "stl_strength",
    "arguments": {
      "series_index": 3,
      "period": "$step1.dominant_period"
    },
    "resolved_arguments": {
      "series_index": 3,
      "period": 720.0
    },
    "success": true,
    "data": {
      "series_index": 3,
      "start": null,
      "end": null,
      "period": 120,
      "period_trusted": true,
      "period_source": "requested",
      "seasonal_strength": 0.30664932020892677,
      "season_strength_bin": "weak",
      "trend_strength": 0.8363804637406759,
      "metric_definition": "seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong",
      "warnings": [
        "requested_period=720 capped to 120 to avoid STL overfitting"
      ]
    },
    "error": null,
    "args_fingerprint": "f1cb0003046985a0f6e48e8e9ba48d7f364c9835"
  },
  {
    "call_id": "long:step3",
    "step": 3,
    "tool_name": "seas_acf",
    "arguments": {
      "series_index": 3,
      "lag": "$step1.dominant_period"
    },
    "resolved_arguments": {
      "series_index": 3,
      "lag": 720.0
    },
    "success": true,
    "data": {
      "series_index": 3,
      "start": null,
      "end": null,
      "lag": 720,
      "seas_acf1": null,
      "strength_hint": "unavailable",
      "note": "lag 720 invalid for length 720"
    },
    "error": null,
    "args_fingerprint": "42a720aba56ad95b3581c990a821f6682a394e1a"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify global seasonality trends in Time Series 3 through long-range temporal inspection using seasonal strength and seasonal autocorrelation measures. The STL strength tool execution provided a seasonal strength measurement of 0.3066, categorized as 'weak'. However, there were issues with calculating the seasonal autocorrelation due to the invalid lag input.",
  "scale": "long",
  "observations": ["Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."],
  "evidence_intervals": ["long-range temporal inspection"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Time Series 3 exhibits significant seasonality",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.30664932020892677,
          "source_tool": "stl_strength",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "seasonal_strength"
    },
    {
      "claim": "Time Series 3 has a strong seasonal autocorrelation",
      "evidence": [
        {
          "type": "seas_acf1",
          "value": null,
          "source_tool": "seas_acf",
          "call_id": "long:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "seas_acf1"
    }
  ],
  "coverage": {"seasonal_strength": "tool_supported", "seas_acf1": "unresolved"},
  "unresolved_claims": ["Time Series 3 has a strong seasonal autocorrelation"]
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=6507 completion=299 latency=12.75s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=reasoning.
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
    "analysis_scope": {"target_series": [1], "role": "reasoning"},
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
{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating seasonality characteristics in a specific time series (Time Series 3) based on two metrics: seasonal_strength and seas_acf1. These metrics help determine if the seasonality is significant, stable, or irregular.","task_summary":"Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.","target_output":"The type of seasonality for Time Series 3 based on provided categories.","answer_type":"choice","capability":"Seasonality analysis using multiple metrics and comparison with predefined criteria.","scope":"overall","univariate":false,"homo_assignments":[{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Accurate determination of seasonality type based on provided metrics and consistent with stated rules.","Clear association of Time Series 3 with the correct categorical description of its seasonality characteristics."],"notes":"This plan leverages the long-scale view to encompass potential periodicities in Time Series 3 while utilizing reasoning to interpret these in light of given options."}
</plan_context>

<task_summary>
Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.
</task_summary>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"The objective was to identify global seasonality trends in Time Series 3 through long-range temporal inspection using seasonal strength and seasonal autocorrelation measures. The STL strength tool execution provided a seasonal strength measurement of 0.3066, categorized as 'weak'. However, there were issues with calculating the seasonal autocorrelation due to the invalid lag input.","scale":"long","observations":["Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."],"evidence_intervals":["long-range temporal inspection"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"dominant_period\": 720.0, \"spectral_strength\": 0.1298976066102109, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"2d03e2fbcc4f68587c50271d6bad3d182ff8a286\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 3, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"period\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"period\": 120, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.30664932020892677, \"season_strength_bin\": \"weak\", \"trend_strength\": 0.8363804637406759, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": [\"requested_period=720 capped to 120 to avoid STL overfitting\"]}, \"error\": null, \"args_fingerprint\": \"f1cb0003046985a0f6e48e8e9ba48d7f364c9835\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 3, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"lag\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"lag\": 720, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 720 invalid for length 720\"}, \"error\": null, \"args_fingerprint\": \"42a720aba56ad95b3581c990a821f6682a394e1a\"}"],"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"stl_strength","reason":"To measure the seasonal_strength of Time Series 3","supports_evidence":["seasonal_strength"]},{"tool":"seas_acf","reason":"To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}},{"step":3,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"series_window":"$series","lag":"$step1.dominant_period"}}],"reasoning":"First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation."},"structured_observations":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}],"coverage":{"seasonal_strength":"tool_supported","seas_acf1":"unresolved"},"unresolved_claims":["Time Series 3 has a strong seasonal autocorrelation"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"dominant_period":720.0,"spectral_strength":0.1298976066102109,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"2d03e2fbcc4f68587c50271d6bad3d182ff8a286"},{"call_id":"long:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":3,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"period":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"period":120,"period_trusted":true,"period_source":"requested","seasonal_strength":0.30664932020892677,"season_strength_bin":"weak","trend_strength":0.8363804637406759,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":["requested_period=720 capped to 120 to avoid STL overfitting"]},"error":null,"args_fingerprint":"f1cb0003046985a0f6e48e8e9ba48d7f364c9835"},{"call_id":"long:step3","step":3,"tool_name":"seas_acf","arguments":{"series_index":3,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"lag":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"lag":720,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 720 invalid for length 720"},"error":null,"args_fingerprint":"42a720aba56ad95b3581c990a821f6682a394e1a"}],"skipped_stages":[]},"conflicts":[],"summary":"Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value.","structured_by_scale":{"long":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides a seasonal strength measurement for Time Series 3 as 'weak' (0.3066) but lacks a valid seas_acf1 metric due to an issue with the lag parameter. Since the required evidence for seas_acf1 is unresolved, we need to recompute it with an appropriate lag value that fits within the series length.",
  "evidence_plan": {
    "objective": "Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria.",
    "claims_to_support": [
      {
        "claim": "Time Series 3 exhibits a specific type of seasonality based on predefined criteria.",
        "required_evidence": ["seasonal_strength", "seas_acf1"]
      }
    ],
    "analysis_scope": {
      "target_series": [3],
      "focus_intervals": []
    },
    "validation_needs": ["Logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior."]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "seas_acf",
        "arguments": {
          "series_index": 3,
          "lag": 120
        },
        "reason": "Recalculate seas_acf1 with a valid lag to resolve the unresolved claim."
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s3) — `heterogeneous:reasoning:s3:m0`

tokens prompt=641 completion=108 latency=3.86s

### INPUT (system)

```
You are a Heterogeneous Agent (role=reasoning) at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria.","claims_to_support":[{"claim":"Time Series 3 exhibits a specific type of seasonality based on predefined criteria.","required_evidence":["seasonal_strength","seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[]},"validation_needs":["Logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior."]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Recalculate seas_acf1 with a valid lag to resolve the unresolved claim.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides a seasonal strength measurement for Time Series 3 as 'weak' (0.3066) but lacks a valid seas_acf1 metric due to an issue with the lag parameter. Since the required evidence for seas_acf1 is unresolved, we need to recompute it with an appropriate lag value that fits within the series length."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- seas_acf
  inputs: series_window, lag
  outputs: seas_acf1, strength_hint
  often_combined_with: autocorr, stl_strength, fft_period
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "To evaluate the nature of seasonality in Time Series 3, we first need to compute seas_acf1 along with seasonal strength using a valid lag parameter.",
  "workflow": [
    {
      "step": 1,
      "tool": "seas_acf",
      "output_key": "seas_acf1",
      "input_binding": {
        "series_window": "auto",
        "lag": "$RealToolName.lag"
      }
    }
  ]
}
```

## Heterogeneous (reasoning, s4) — `heterogeneous:reasoning:s4:m0`

tokens prompt=801 completion=118 latency=4.25s

### INPUT (system)

```
You are a Heterogeneous Agent (role=reasoning) at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"series_window":"auto","lag":"$RealToolName.lag"}}],"reasoning":"To evaluate the nature of seasonality in Time Series 3, we first need to compute seas_acf1 along with seasonal strength using a valid lag parameter."}
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

- seas_acf: MMTS seas_acf1: seasonal autocorrelation ρ_m=γ_m/γ_0 at lag m (e.g. lag=26 for weekly half-year frequency).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, lag=required seasonal lag m (aliases: m, frequency, period)}
  returns: {series=seas_acf1 at lag m with strength_hint}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}
</assignment>



Produce the InvocationPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "To evaluate the nature of seasonality in Time Series 3, we will compute seas_acf1 with a suitable lag. Since no specific lag was given, we'll use an automatic window selection and set lag='auto'. This will help us assess the seasonal strength and pattern for the series.",
  "calls": [
    {
      "step": 1,
      "tool": "seas_acf",
      "args": {
        "series_index": 3,
        "lag": "auto"
      }
    }
  ]
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=3225 completion=624 latency=23.19s

### INPUT (system)

```
You are a Heterogeneous Agent (role=reasoning) at Stage 5: Evidence Integration.
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
  "role": "reasoning",
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
{"evidence_plan":{"objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria.","claims_to_support":[{"claim":"Time Series 3 exhibits a specific type of seasonality based on predefined criteria.","required_evidence":["seasonal_strength","seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[]},"validation_needs":["Logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior."]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Recalculate seas_acf1 with a valid lag to resolve the unresolved claim.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides a seasonal strength measurement for Time Series 3 as 'weak' (0.3066) but lacks a valid seas_acf1 metric due to an issue with the lag parameter. Since the required evidence for seas_acf1 is unresolved, we need to recompute it with an appropriate lag value that fits within the series length."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "reasoning:step1",
    "step": 1,
    "tool_name": "seas_acf",
    "arguments": {
      "series_index": 3,
      "lag": "auto",
      "series_window": "auto"
    },
    "resolved_arguments": {
      "series_index": 3,
      "lag": "auto",
      "series_window": "auto"
    },
    "success": false,
    "data": {},
    "error": "invalid literal for int() with base 10: 'auto'",
    "args_fingerprint": ""
  }
]
</executed_steps>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"The objective was to identify global seasonality trends in Time Series 3 through long-range temporal inspection using seasonal strength and seasonal autocorrelation measures. The STL strength tool execution provided a seasonal strength measurement of 0.3066, categorized as 'weak'. However, there were issues with calculating the seasonal autocorrelation due to the invalid lag input.","scale":"long","observations":["Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."],"evidence_intervals":["long-range temporal inspection"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"dominant_period\": 720.0, \"spectral_strength\": 0.1298976066102109, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"2d03e2fbcc4f68587c50271d6bad3d182ff8a286\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 3, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"period\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"period\": 120, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.30664932020892677, \"season_strength_bin\": \"weak\", \"trend_strength\": 0.8363804637406759, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": [\"requested_period=720 capped to 120 to avoid STL overfitting\"]}, \"error\": null, \"args_fingerprint\": \"f1cb0003046985a0f6e48e8e9ba48d7f364c9835\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 3, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"lag\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"lag\": 720, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 720 invalid for length 720\"}, \"error\": null, \"args_fingerprint\": \"42a720aba56ad95b3581c990a821f6682a394e1a\"}"],"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"stl_strength","reason":"To measure the seasonal_strength of Time Series 3","supports_evidence":["seasonal_strength"]},{"tool":"seas_acf","reason":"To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}},{"step":3,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"series_window":"$series","lag":"$step1.dominant_period"}}],"reasoning":"First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation."},"structured_observations":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}],"coverage":{"seasonal_strength":"tool_supported","seas_acf1":"unresolved"},"unresolved_claims":["Time Series 3 has a strong seasonal autocorrelation"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"dominant_period":720.0,"spectral_strength":0.1298976066102109,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"2d03e2fbcc4f68587c50271d6bad3d182ff8a286"},{"call_id":"long:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":3,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"period":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"period":120,"period_trusted":true,"period_source":"requested","seasonal_strength":0.30664932020892677,"season_strength_bin":"weak","trend_strength":0.8363804637406759,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":["requested_period=720 capped to 120 to avoid STL overfitting"]},"error":null,"args_fingerprint":"f1cb0003046985a0f6e48e8e9ba48d7f364c9835"},{"call_id":"long:step3","step":3,"tool_name":"seas_acf","arguments":{"series_index":3,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"lag":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"lag":720,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 720 invalid for length 720"},"error":null,"args_fingerprint":"42a720aba56ad95b3581c990a821f6682a394e1a"}],"skipped_stages":[]},"conflicts":[],"summary":"Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value.","structured_by_scale":{"long":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Time Series 3's seasonality is evaluated based on the seasonal strength and the seas_acf1 metric. The seasonal strength for Time Series 3 is identified as 'weak' with a value of 0.3066 from the STL decomposition analysis. However, there is an unresolved issue with calculating seas_acf1 due to an inappropriate lag parameter being used previously. Recalculation with a valid lag is necessary to fully understand the seasonality nature of Time Series 3.",
  "role": "reasoning",
  "hypothesis": "Time Series 3's seasonality can be categorized based on both the seasonal strength and seas_acf1 metrics, but currently, the seas_acf1 remains unresolved due to incorrect usage of the lag parameter.",
  "evidence": ["long:step2", "long:step3"],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["long:step2", "long:step3", "reasoning:step1"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 3 has a weak seasonality strength of 0.3066 based on STL decomposition.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.30664932020892677,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There was an issue with calculating seas_acf1 due to an incorrect lag parameter.",
      "evidence": [
        {
          "type": "seas_acf1",
          "value": null,
          "provenance": "upstream",
          "ref": "long:step3",
          "call_id": "long:step3"
        }
      ],
      "confidence": "unresolved"
    },
    {
      "claim": "A recomputation with an appropriate lag parameter is needed to resolve the seas_acf1 calculation.",
      "evidence": [
        {
          "type": "seas_acf1",
          "value": null,
          "provenance": "unresolved",
          "ref": "reasoning:step1",
          "call_id": "reasoning:step1"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "seasonal_strength": "tool_supported",
    "seas_acf1": "unresolved"
  },
  "unresolved_claims": ["Time Series 3's seas_acf1 needs to be calculated with a proper lag to accurately assess its seasonality."]
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m1`

tokens prompt=6539 completion=261 latency=11.34s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=reasoning.
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
    "analysis_scope": {"target_series": [1], "role": "reasoning"},
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
{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating seasonality characteristics in a specific time series (Time Series 3) based on two metrics: seasonal_strength and seas_acf1. These metrics help determine if the seasonality is significant, stable, or irregular.","task_summary":"Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.","target_output":"The type of seasonality for Time Series 3 based on provided categories.","answer_type":"choice","capability":"Seasonality analysis using multiple metrics and comparison with predefined criteria.","scope":"overall","univariate":false,"homo_assignments":[{"scale":"long","objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."],"target_series":[3],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Accurate determination of seasonality type based on provided metrics and consistent with stated rules.","Clear association of Time Series 3 with the correct categorical description of its seasonality characteristics."],"notes":"This plan leverages the long-scale view to encompass potential periodicities in Time Series 3 while utilizing reasoning to interpret these in light of given options."}
</plan_context>

<task_summary>
Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.
</task_summary>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"The objective was to identify global seasonality trends in Time Series 3 through long-range temporal inspection using seasonal strength and seasonal autocorrelation measures. The STL strength tool execution provided a seasonal strength measurement of 0.3066, categorized as 'weak'. However, there were issues with calculating the seasonal autocorrelation due to the invalid lag input.","scale":"long","observations":["Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."],"evidence_intervals":["long-range temporal inspection"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"dominant_period\": 720.0, \"spectral_strength\": 0.1298976066102109, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"2d03e2fbcc4f68587c50271d6bad3d182ff8a286\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 3, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"period\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"period\": 120, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.30664932020892677, \"season_strength_bin\": \"weak\", \"trend_strength\": 0.8363804637406759, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": [\"requested_period=720 capped to 120 to avoid STL overfitting\"]}, \"error\": null, \"args_fingerprint\": \"f1cb0003046985a0f6e48e8e9ba48d7f364c9835\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 3, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"lag\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"lag\": 720, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 720 invalid for length 720\"}, \"error\": null, \"args_fingerprint\": \"42a720aba56ad95b3581c990a821f6682a394e1a\"}"],"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"stl_strength","reason":"To measure the seasonal_strength of Time Series 3","supports_evidence":["seasonal_strength"]},{"tool":"seas_acf","reason":"To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}},{"step":3,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"series_window":"$series","lag":"$step1.dominant_period"}}],"reasoning":"First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation."},"structured_observations":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}],"coverage":{"seasonal_strength":"tool_supported","seas_acf1":"unresolved"},"unresolved_claims":["Time Series 3 has a strong seasonal autocorrelation"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"dominant_period":720.0,"spectral_strength":0.1298976066102109,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"2d03e2fbcc4f68587c50271d6bad3d182ff8a286"},{"call_id":"long:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":3,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"period":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"period":120,"period_trusted":true,"period_source":"requested","seasonal_strength":0.30664932020892677,"season_strength_bin":"weak","trend_strength":0.8363804637406759,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":["requested_period=720 capped to 120 to avoid STL overfitting"]},"error":null,"args_fingerprint":"f1cb0003046985a0f6e48e8e9ba48d7f364c9835"},{"call_id":"long:step3","step":3,"tool_name":"seas_acf","arguments":{"series_index":3,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"lag":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"lag":720,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 720 invalid for length 720"},"error":null,"args_fingerprint":"42a720aba56ad95b3581c990a821f6682a394e1a"}],"skipped_stages":[]},"conflicts":[],"summary":"Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value.","structured_by_scale":{"long":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=["Time Series 3's seas_acf1 needs to be calculated with a proper lag to accurately assess its seasonality."]
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides a seasonal strength measurement for Time Series 3, but the seas_acf1 calculation has unresolved issues due to an invalid lag value. We need to recalibrate and re-run the seas_acf with a valid lag to complete the assessment.",
  "evidence_plan": {
    "objective": "Reevaluate seasonality for Time Series 3 by obtaining a valid seas_acf1 measurement and comparing it against defined criteria.",
    "claims_to_support": [
      {
        "claim": "Time Series 3 exhibits a weak seasonality strength",
        "required_evidence": ["seasonal_strength"]
      },
      {
        "claim": "Time Series 3's seasonal autocorrelation can be accurately measured",
        "required_evidence": ["seas_acf1"]
      }
    ],
    "analysis_scope": {
      "target_series": [3],
      "role": "reasoning"
    },
    "validation_needs": ["Recalculate seas_acf1 with a valid lag to confirm seasonal autocorrelation"]
  },
  "capability_selection": {
    "selected_tools": [
      "stl_strength",
      "seas_acf"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m1`

tokens prompt=2978 completion=501 latency=18.67s

### INPUT (system)

```
You are a Heterogeneous Agent (role=reasoning) at Stage 5: Evidence Integration.
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
  "role": "reasoning",
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
{"evidence_plan":{"objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"The objective was to identify global seasonality trends in Time Series 3 through long-range temporal inspection using seasonal strength and seasonal autocorrelation measures. The STL strength tool execution provided a seasonal strength measurement of 0.3066, categorized as 'weak'. However, there were issues with calculating the seasonal autocorrelation due to the invalid lag input.","scale":"long","observations":["Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."],"evidence_intervals":["long-range temporal inspection"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"dominant_period\": 720.0, \"spectral_strength\": 0.1298976066102109, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"2d03e2fbcc4f68587c50271d6bad3d182ff8a286\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 3, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"period\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"period\": 120, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.30664932020892677, \"season_strength_bin\": \"weak\", \"trend_strength\": 0.8363804637406759, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": [\"requested_period=720 capped to 120 to avoid STL overfitting\"]}, \"error\": null, \"args_fingerprint\": \"f1cb0003046985a0f6e48e8e9ba48d7f364c9835\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 3, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 3, \"lag\": 720.0}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"lag\": 720, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 720 invalid for length 720\"}, \"error\": null, \"args_fingerprint\": \"42a720aba56ad95b3581c990a821f6682a394e1a\"}"],"evidence_plan":{"objective":"Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.","claims_to_support":[{"claim":"Time Series 3 exhibits significant seasonality","required_evidence":["seasonal_strength"]},{"claim":"Time Series 3 has a strong seasonal autocorrelation","required_evidence":["seas_acf1"]}],"analysis_scope":{"target_series":[3],"focus_intervals":[],"scale":"long"},"validation_needs":["Cross-validation by checking consistency across different intervals and ensuring robustness against noise and outliers."]},"capability_selection":{"selected_tools":[{"tool":"stl_strength","reason":"To measure the seasonal_strength of Time Series 3","supports_evidence":["seasonal_strength"]},{"tool":"seas_acf","reason":"To detect the seasonal autocorrelation (seas_acf1) at an appropriate lag","supports_evidence":["seas_acf1"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}},{"step":3,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"series_window":"$series","lag":"$step1.dominant_period"}}],"reasoning":"First, we use fft_period to estimate the dominant period for Time Series 3. Then, we leverage this period to evaluate the seasonal strength using stl_strength. Finally, we use seas_acf with the estimated period to measure the seasonal autocorrelation."},"structured_observations":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}],"coverage":{"seasonal_strength":"tool_supported","seas_acf1":"unresolved"},"unresolved_claims":["Time Series 3 has a strong seasonal autocorrelation"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"dominant_period":720.0,"spectral_strength":0.1298976066102109,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"2d03e2fbcc4f68587c50271d6bad3d182ff8a286"},{"call_id":"long:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":3,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"period":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"period":120,"period_trusted":true,"period_source":"requested","seasonal_strength":0.30664932020892677,"season_strength_bin":"weak","trend_strength":0.8363804637406759,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":["requested_period=720 capped to 120 to avoid STL overfitting"]},"error":null,"args_fingerprint":"f1cb0003046985a0f6e48e8e9ba48d7f364c9835"},{"call_id":"long:step3","step":3,"tool_name":"seas_acf","arguments":{"series_index":3,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":3,"lag":720.0},"success":true,"data":{"series_index":3,"start":null,"end":null,"lag":720,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 720 invalid for length 720"},"error":null,"args_fingerprint":"42a720aba56ad95b3581c990a821f6682a394e1a"}],"skipped_stages":[]},"conflicts":[],"summary":"Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value.","structured_by_scale":{"long":[{"claim":"Time Series 3 exhibits significant seasonality","evidence":[{"type":"seasonal_strength","value":0.30664932020892677,"source_tool":"stl_strength","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"},{"claim":"Time Series 3 has a strong seasonal autocorrelation","evidence":[{"type":"seas_acf1","value":null,"source_tool":"seas_acf","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seas_acf1"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.","required_measurements":["seasonal_strength","seas_acf1"],"validation_requirements":["Use logical deduction based on definitions to reconcile observed metrics with expected seasonal behavior and choose the closest match from the candidates."],"target_series":[3],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'inductive reasoning']; domain=climate; qa_type=a multiple choice question; question_type=choice; is_univariate=False; n_series=4; series_lengths=[720, 720, 720, 720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2, 3, 4]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, Time Series 3 shows weak seasonality as indicated by its seasonal strength score. There's no valid evidence to support the claim of strong seasonal autocorrelation due to an invalid lag value that caused issues in the calculation.",
  "role": "reasoning",
  "hypothesis": "Time Series 3 exhibits weak seasonality and has unresolved seasonal autocorrelation measurement due to methodological limitations.",
  "evidence": ["Time Series 3 exhibits weak seasonality based on the seasonal strength score calculated from STL decomposition (value: 0.30664932020892677, categorized as 'weak').", "There are unresolved claims regarding the presence of strong seasonal autocorrelation due to issues in the seas_acf calculation related to an invalid lag input."],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["long:step2", "long:step3"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 3 exhibits weak seasonality based on seasonal strength",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.30664932020892677,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There is an unresolved claim regarding the presence of strong seasonal autocorrelation due to methodological limitations",
      "evidence": [
        {
          "type": "seas_acf1",
          "value": null,
          "provenance": "upstream",
          "ref": "long:step3",
          "call_id": "long:step3"
        }
      ],
      "confidence": "unresolved"
    }
  ],
  "coverage": {
    "seasonal_strength": "tool_supported",
    "seas_acf1": "unresolved"
  },
  "unresolved_claims": ["Time Series 3 has a strong seasonal autocorrelation"]
}
```

## Integration — `integration`

tokens prompt=1587 completion=379 latency=13.64s

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
The seasonality analysis of the sequence can be performed using seasonal_strength & seas_acf1 as a reference metric. The calculation method is seasonal_strength: The `seasonal_strength` feature quantifies seasonality strength as $ 1 - \frac{\mathrm{Var}(R_t)}{\mathrm{Var}(S_t + R_t)} $, where $ S_t $ and $ R_t $ are the seasonal and remainder components. Higher values indicate stronger seasonal patterns; seas_acf1: The `seas_acf1` feature captures seasonal autocorrelation at lag $ m $: $ \rho_m(x) = \frac{\gamma_m(x)}{\gamma_0(x)} $, where $ \gamma_k(x) $ is the autocovariance and $ \gamma_0(x) $ is the variance. Values near ±1 imply strong seasonal correlation; near 0 implies weak seasonality. Now, please answer the following question: Based on the conclusions that a sequence with seas_acf1 close to ±1 and seasonal_strength close to 1 indicates strong and significant seasonality, and a sequence with seas_acf1 close to 0 and seasonal_strength close to 1 indicates strong but irregular or unstable seasonality, which of the following types does the sequence Time Series 3 belong to?
</question>

<candidates>
A) The periodic structure exists but is weak in explanatory power.
B) The seasonality is significant and strong.
C) The overall fluctuations appear to be seasonally strong but are unstable or irregular.
D) There is no clear seasonality.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Analyze Time Series 3's seasonality using seasonal_strength and seas_acf1 to categorize it among given options.",
  "question_type": "choice",
  "required_output": "The type of seasonality for Time Series 3 based on provided categories.",
  "success_criteria": [
    "Accurate determination of seasonality type based on provided metrics and consistent with stated rules.",
    "Clear association of Time Series 3 with the correct categorical description of its seasonality characteristics."
  ],
  "assignments_brief": [
    {
      "agent": "homo:long",
      "objective": "Identify the global seasonality trends of Time Series 3 through long-range temporal inspection.",
      "required_measurements": [
        "seasonal_strength",
        "seas_acf1"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Evaluate the nature of the seasonality for Time Series 3 by comparing seasonal_strength and seas_acf1 against defined criteria, then select the appropriate category from the provided options.",
      "required_measurements": [
        "seasonal_strength",
        "seas_acf1"
      ]
    }
  ]
}
</planner_intent>

<homo_perception>
{
  "by_scale": {
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "seasonal_strength",
          "value": 0.30664932020892677,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "seas_acf1",
          "value": null,
          "trusted": true
        }
      ],
      "coverage": {
        "seasonal_strength": "tool_supported",
        "seas_acf1": "unresolved"
      },
      "summary": "Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."
    }
  },
  "conflicts": [],
  "summary": "Time Series 3 exhibits a weak seasonality strength based on STL decomposition, but seasonal autocorrelation calculation faced issues due to invalid lag value."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
      "hypothesis": "Time Series 3 exhibits weak seasonality and has unresolved seasonal autocorrelation measurement due to methodological limitations.",
      "reasoning_chain": [
        "Time Series 3 exhibits weak seasonality based on seasonal strength",
        "seasonal_strength=0.30664932020892677",
        "There is an unresolved claim regarding the presence of strong seasonal autocorrelation due to methodological limitations"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "seasonal_strength",
        "seas_acf1"
      ],
      "uncertainty": ""
    }
  ]
}
</heter_reasoning>

<execution_metadata>
{
  "option_mapping": {},
  "verified_preference": null,
  "verified": false,
  "warnings": []
}
</execution_metadata>

<question_rules>
- Threshold labels: parse intervals from <question> only. Compare trusted homo_perception numeric states to those intervals, fill decision_trace, then choose the matching option letter. Do not copy Heter qualitative words (strong/weak/low/high) over the numeric comparison; if they disagree, keep the numeric match and add a conflict.
</question_rules>

Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "Time Series 3's seasonality is assessed through its seasonal_strength and seas_acf1 metrics. Given the observed seasonal_strength of 0.3066, this falls into the weaker end of the seasonality spectrum as per the guidelines. There are no specific seas_acf1 values reported, implying unresolved measurement issues. This data points towards a weak seasonality pattern rather than strong or significant seasonality. Considering the candidate descriptions, option A fits best as it describes a scenario with existing periodicity but weak explanatory power, which aligns with the low seasonal_strength seen.",
  "answer": "A",
  "explanation": "Based on the observed seasonal_strength of 0.3066 and unresolved seas_acf1 measurement due to methodological issues, the seasonality in Time Series 3 is deemed weak despite potential periodic structure. Option A most accurately reflects this scenario.",
  "confidence": 0.5,
  "conflicts": [
    "The hetero reasoning includes uncertainty about seas_acf1 due to methodological limitations, which contrasts with the need for a definitive categorization based on available metrics."
  ],
  "cited_evidence": [
    "Homo Perception reports a seasonal_strength of 0.3066 indicating weak seasonality.",
    "Seas_acf1 could not be calculated leading to unresolved methodological issues."
  ],
  "decision_trace": {
    "metric": "seasonal_strength",
    "observed_value": 0.30664932020892677,
    "intervals_from_question": ["close to ±1", "close to 1", "near 0", "null"],
    "matched_label": "near 0",
    "matched_letter": "A"
  }
}
```
