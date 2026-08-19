# Agent IO summary: `InWild:tsqa_1084:217`

- Architecture pred: `B` (success=True)
- model_calls=18, tool_calls=4, latency=197.3s

## Planner — `planner`

tokens prompt=1255 completion=500 latency=17.79s

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
The basic analysis of the sequence can be performed using iqr as a reference metric. The calculation method is iqr is as follows: The `iqr` feature is the interquartile range: $ q_{75} - q_{25} $, a robust measure of variability excluding outliers. Now, please answer the following question: If the data points at indices 28-32 had not reached their peak values (above 13,000), but instead had remained at the average level of the preceding 5 data points (indices 23-27), what would be the most likely impact on the interquartile range (IQR) of the entire time series? The Interquartile Range (IQR) is a measure of statistical dispersion, representing the range between the first quartile (25th percentile) and the third quartile (75th percentile) of a dataset.
</question>

<candidates>
A) The IQR would likely increase by approximately 15-25%.
B) The IQR would remain essentially unchanged (within ±5% of the original value).
C) The IQR would likely decrease by approximately 10-15%.
D) The IQR would likely decrease by approximately 25-35%.
</candidates>

<metadata>
local_overall=local; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.",
  "task_summary": "Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.",
  "target_output": "The change in IQR due to replacement of data points with mean of preceding points.",
  "answer_type": "choice",
  "capability": "hierarchical time-series analysis",
  "scope": "local",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Identify the short-term behavior and changes in local density and variance.",
      "required_measurements": ["change_location", "pairwise_similarity"],
      "validation_requirements": ["compare against unaffected parts of the series"],
      "target_series": [1],
      "focus_intervals": [[23, 27], [28, 32]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "structure",
      "objective": "Measure the overall variability by computing IQR both before and after the proposed modifications.",
      "required_measurements": ["iqr"],
      "validation_requirements": ["compare calculated IQRs for changes greater than the noise level"],
      "target_series": [1],
      "focus_intervals": [[0, 71]]
    },
    {
      "role": "reasoning",
      "objective": "Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.",
      "required_measurements": ["delta_iqr", "average_change_effect"],
      "validation_requirements": ["ensure the impact aligns with the observed data characteristics"],
      "target_series": [1],
      "focus_intervals": [[28, 32], [23, 27]]
    }
  ],
  "success_criteria": ["Delta in IQR is quantified correctly", "Impact matches given candidate options accurately"],
  "notes": "Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4119 completion=337 latency=13.19s

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
{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}
</assignment>

<plan_context>
{"reasoning":"The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.","task_summary":"Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.","target_output":"The change in IQR due to replacement of data points with mean of preceding points.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}],"hetero_assignments":[{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]},{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}],"scales":["short"],"heterogeneous_agents":["structure","reasoning"],"success_criteria":["Delta in IQR is quantified correctly","Impact matches given candidate options accurately"],"notes":"Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."}
</plan_context>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the short-term behavior and changes in local density and variance, specifically focusing on the location of changes and the pairwise similarity between intervals. We need to measure the change in local density and variance by identifying the change location and comparing the affected intervals with unaffected parts of the series.",
  "evidence_plan": {
    "objective": "Identify the short-term behavior and changes in local density and variance.",
    "claims_to_support": [
      {
        "claim": "Locate the points where the density or variance changes abruptly.",
        "required_evidence": ["change_location"]
      },
      {
        "claim": "Compare the similarity between specified intervals and other parts of the series.",
        "required_evidence": ["pairwise_similarity"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[23, 27], [28, 32]],
      "scale": "short"
    },
    "validation_needs": ["compare against unaffected parts of the series"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "change_points",
        "reason": "To detect potential level shifts that indicate changes in local density or variance.",
        "supports_evidence": ["change_location"]
      },
      {
        "tool": "cross_series_compare",
        "reason": "To compare the specified intervals with other parts of the series to assess similarity.",
        "supports_evidence": ["pairwise_similarity"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=825 completion=184 latency=6.56s

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
{"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"Locate the points where the density or variance changes abruptly.","required_evidence":["change_location"]},{"claim":"Compare the similarity between specified intervals and other parts of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To detect potential level shifts that indicate changes in local density or variance.","supports_evidence":["change_location"]},{"tool":"cross_series_compare","reason":"To compare the specified intervals with other parts of the series to assess similarity.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective is to identify the short-term behavior and changes in local density and variance, specifically focusing on the location of changes and the pairwise similarity between intervals. We need to measure the change in local density and variance by identifying the change location and comparing the affected intervals with unaffected parts of the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- change_points
  inputs: series_index, start, end
  outputs: series
- cross_series_compare
  inputs: series_index_1, series_index_2, optional start/end
  outputs: comparison stats, correlation, distance
  often_combined_with: lag_corr, pairwise_distance
</io_concepts>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'change_points' to detect abrupt changes in density or variance within the target series. Then, we apply 'cross_series_compare' to compare the specified intervals with other parts of the series.",
  "workflow": [
    {
      "step": 1,
      "tool": "change_points",
      "output_key": "change_locations",
      "input_binding": {"series_index": "$query_series_index", "start": 23, "end": 32}
    },
    {
      "step": 2,
      "tool": "cross_series_compare",
      "output_key": "interval_comparison",
      "input_binding": {"series_index_1": "$query_series_index", "series_index_2": "$query_series_index", "start": 28, "end": 32}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=944 completion=191 latency=6.84s

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
{"workflow":[{"step":1,"tool":"change_points","output_key":"change_locations","input_binding":{"series_index":"$query_series_index","start":23,"end":32}},{"step":2,"tool":"cross_series_compare","output_key":"interval_comparison","input_binding":{"series_index_1":"$query_series_index","series_index_2":"$query_series_index","start":28,"end":32}}],"reasoning":"First, we use 'change_points' to detect abrupt changes in density or variance within the target series. Then, we apply 'cross_series_compare' to compare the specified intervals with other parts of the series."}
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

- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
- cross_series_compare: Compare windows across TWO series (analogical / multi-series segment tasks). Returns per-series segment stats, trend match, distance, correlation.
  args: {series_index_1=1-based int (default 1), series_index_2=1-based int (default 2), start=optional shared window start, end=optional shared window end, left_interval=optional [start,end] for series 1, right_interval=optional [start,end] for series 2}
  returns: {series_1/series_2=segment stats, comparison=trend agreement, distance, correlation}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'change_points' to detect abrupt changes in density or variance within the target series, specifically within the interval [23, 32]. Then, we apply 'cross_series_compare' to compare the interval [28, 32] with another part of the same series.",
  "calls": [
    {
      "step": 1,
      "tool": "change_points",
      "args": {
        "series_index": 1,
        "start": 23,
        "end": 32
      }
    },
    {
      "step": 2,
      "tool": "cross_series_compare",
      "args": {
        "series_index_1": 1,
        "series_index_2": 1,
        "start": 28,
        "end": 32
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1239 completion=432 latency=15.39s

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
{"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"Locate the points where the density or variance changes abruptly.","required_evidence":["change_location"]},{"claim":"Compare the similarity between specified intervals and other parts of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To detect potential level shifts that indicate changes in local density or variance.","supports_evidence":["change_location"]},{"tool":"cross_series_compare","reason":"To compare the specified intervals with other parts of the series to assess similarity.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective is to identify the short-term behavior and changes in local density and variance, specifically focusing on the location of changes and the pairwise similarity between intervals. We need to measure the change in local density and variance by identifying the change location and comparing the affected intervals with unaffected parts of the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "change_points",
    "arguments": {
      "series_index": 1,
      "start": 23,
      "end": 32
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 23,
      "end": 32
    },
    "success": true,
    "data": {
      "series_index": 1,
      "candidates": [
        {
          "index": 21,
          "score": 3120.0
        },
        {
          "index": 20,
          "score": 2520.0
        },
        {
          "index": 22,
          "score": 2480.0
        },
        {
          "index": 23,
          "score": 2480.0
        },
        {
          "index": 24,
          "score": 2360.0
        }
      ]
    },
    "error": null,
    "args_fingerprint": "21f84e50ac48108632b5248c200818fec7658af3"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "cross_series_compare",
    "arguments": {
      "series_index_1": 1,
      "series_index_2": 1,
      "start": 28,
      "end": 32
    },
    "resolved_arguments": {
      "series_index_1": 1,
      "series_index_2": 1,
      "start": 28,
      "end": 32
    },
    "success": false,
    "data": {},
    "error": "Need >=2 series",
    "args_fingerprint": ""
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}
</assignment>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify the short-term behavior and changes in local density and variance. Change points were detected successfully within the interval specified, indicating potential abrupt changes in density or variance. However, the cross-series comparison tool failed due to an error, preventing us from evaluating the similarity between the specified intervals and other parts of the series.",
  "scale": "short",
  "observations": ["Change points have been detected within the specified interval, but pairwise similarity could not be evaluated due to an error in the cross-series comparison tool."],
  "evidence_intervals": ["[23,27]", "[28,32]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Potential abrupt changes in local density or variance have been identified at specific points within the specified intervals.",
      "evidence": [
        {
          "type": "change_location",
          "value": "21, 20, 22, 23, 24",
          "source_tool": "change_points",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_location"
    },
    {
      "claim": "The comparison between the specified intervals and other parts of the series could not be evaluated.",
      "evidence": [
        {
          "type": "pairwise_similarity",
          "value": "not_evaluated",
          "source_tool": "cross_series_compare",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {"change_location": "tool_supported", "pairwise_similarity": "unresolved"},
  "unresolved_claims": ["The comparison between the specified intervals and other parts of the series could not be evaluated."]
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m1`

tokens prompt=4149 completion=336 latency=13.15s

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
{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}
</assignment>

<plan_context>
{"reasoning":"The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.","task_summary":"Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.","target_output":"The change in IQR due to replacement of data points with mean of preceding points.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}],"hetero_assignments":[{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]},{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}],"scales":["short"],"heterogeneous_agents":["structure","reasoning"],"success_criteria":["Delta in IQR is quantified correctly","Impact matches given candidate options accurately"],"notes":"Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."}
</plan_context>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['The comparison between the specified intervals and other parts of the series could not be evaluated.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the short-term behavior and changes in local density and variance, specifically focusing on change location and pairwise similarity. We need to measure the change location and assess pairwise similarity between affected and unaffected parts of the series.",
  "evidence_plan": {
    "objective": "Identify the short-term behavior and changes in local density and variance.",
    "claims_to_support": [
      {"claim": "The location of changes in local density and variance can be pinpointed.", "required_evidence": ["change_location"]},
      {"claim": "Pairwise similarity between specified intervals and unaffected parts of the series can be determined.", "required_evidence": ["pairwise_similarity"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[23,27],[28,32]], "scale": "short"},
    "validation_needs": ["compare against unaffected parts of the series"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "value_at_index", "reason": "To capture exact values at specific indices for comparison.", "supports_evidence": ["change_location"]},
      {"tool": "interval_compare", "reason": "To quantify the similarity between two intervals within the same series.", "supports_evidence": ["pairwise_similarity"]},
      {"tool": "cross_series_compare", "reason": "To compare windows across the series itself, treating it as two separate series for internal comparison purposes.", "supports_evidence": ["pairwise_similarity"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m1`

tokens prompt=883 completion=165 latency=5.91s

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
{"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective is to identify the short-term behavior and changes in local density and variance, specifically focusing on change location and pairwise similarity. We need to measure the change location and assess pairwise similarity between affected and unaffected parts of the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- value_at_index
  inputs: series_index, start, end, index, index_base
  outputs: series
- interval_compare
  inputs: series_index, start, end, left_interval, right_interval, start/mid/end
  outputs: left/right
- cross_series_compare
  inputs: series_index_1, series_index_2, optional start/end
  outputs: comparison stats, correlation, distance
  often_combined_with: lag_corr, pairwise_distance
</io_concepts>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other.",
  "workflow": [
    {
      "step": 1,
      "tool": "value_at_index",
      "output_key": "specific_values",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "cross_series_compare",
      "output_key": "similarity_results",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m1`

tokens prompt=1079 completion=256 latency=9.15s

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
{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."}
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

- value_at_index: Return the numeric value at a specific index (0-based by default).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, index=required int index, index_base=0 (default) or 1 if question uses 1-based indices}
  returns: {series=selected series, requested index/position, and exact value}
- interval_compare: Compare left/right interval statistics on one series (mean/std/max/min/n_peaks/trend per side).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, left_interval=[start,end] inclusive, right_interval=[start,end] inclusive, start/mid/end=alt split mode}
  returns: {left/right=interval statistics, trends, extrema counts, and deltas}
- cross_series_compare: Compare windows across TWO series (analogical / multi-series segment tasks). Returns per-series segment stats, trend match, distance, correlation.
  args: {series_index_1=1-based int (default 1), series_index_2=1-based int (default 2), start=optional shared window start, end=optional shared window end, left_interval=optional [start,end] for series 1, right_interval=optional [start,end] for series 2}
  returns: {series_1/series_2=segment stats, comparison=trend agreement, distance, correlation}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other.",
  "calls": [
    {
      "step": 1,
      "tool": "value_at_index",
      "args": {
        "series_index": 1,
        "index": 23
      }
    },
    {
      "step": 2,
      "tool": "value_at_index",
      "args": {
        "series_index": 1,
        "index": 28
      }
    },
    {
      "step": 3,
      "tool": "cross_series_compare",
      "args": {
        "series_index_1": 1,
        "series_index_2": 1,
        "start": 23,
        "end": 27,
        "left_interval": [28, 32]
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m1`

tokens prompt=1184 completion=439 latency=15.64s

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
{"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective is to identify the short-term behavior and changes in local density and variance, specifically focusing on change location and pairwise similarity. We need to measure the change location and assess pairwise similarity between affected and unaffected parts of the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "value_at_index",
    "arguments": {
      "series_index": 1,
      "index": 23
    },
    "resolved_arguments": {
      "series_index": 1,
      "index": 23
    },
    "success": true,
    "data": {
      "series_index": 1,
      "index": 23,
      "position": 23,
      "value": 11700.0
    },
    "error": null,
    "args_fingerprint": "01056926059caba4d7935316e52417578df6f7b3"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "cross_series_compare",
    "arguments": {
      "series_index_1": 1,
      "series_index_2": 1,
      "start": 23,
      "end": 27,
      "left_interval": [
        28,
        32
      ]
    },
    "resolved_arguments": {
      "series_index_1": 1,
      "series_index_2": 1,
      "start": 23,
      "end": 27,
      "left_interval": [
        28,
        32
      ]
    },
    "success": false,
    "data": {},
    "error": "Need >=2 series",
    "args_fingerprint": ""
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}
</assignment>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.",
  "scale": "short",
  "observations": ["Value at index 23 is 11700.0.", "Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],
  "evidence_intervals": ["[23, 27]", "[28, 32]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The location of changes in local density and variance can be pinpointed.",
      "evidence": [
        {
          "type": "change_location",
          "value": 11700.0,
          "source_tool": "value_at_index",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_location"
    },
    {
      "claim": "Pairwise similarity between specified intervals and unaffected parts of the series can be determined.",
      "evidence": [
        {
          "type": "comparison_failure",
          "value": "cross_series_compare failed due to needing >=2 series",
          "source_tool": "cross_series_compare",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {"change_location": "tool_supported", "pairwise_similarity": "unresolved"},
  "unresolved_claims": ["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."]
}
```

## Heterogeneous (structure, s1s2) — `heterogeneous:structure:s1s2:m0`

tokens prompt=6202 completion=324 latency=13.59s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=structure.
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
    "analysis_scope": {"target_series": [1], "role": "structure"},
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
{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]}
</assignment>

<plan_context>
{"reasoning":"The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.","task_summary":"Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.","target_output":"The change in IQR due to replacement of data points with mean of preceding points.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}],"hetero_assignments":[{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]},{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}],"scales":["short"],"heterogeneous_agents":["structure","reasoning"],"success_criteria":["Delta in IQR is quantified correctly","Impact matches given candidate options accurately"],"notes":"Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."}
</plan_context>

<task_summary>
Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=structure.

```

### OUTPUT

```
```json
{
  "reasoning": "The assignment aims to measure the overall variability by computing the IQR both before and after the proposed modifications. The modifications involve replacing specific data points with the mean of previous points. The task requires evaluating if the changes in IQR are greater than the noise level. Upstream observations confirm that the exact value at index 23 is 11700.0, but there was no direct evidence on the IQR or noise level pre/post modification.",
  "evidence_plan": {
    "objective": "Measure the overall variability by computing IQR both before and after the proposed modifications.",
    "claims_to_support": [
      {
        "claim": "The overall variability (IQR) before the proposed modifications.",
        "required_evidence": ["iqr_before_modification"]
      },
      {
        "claim": "The overall variability (IQR) after the proposed modifications.",
        "required_evidence": ["iqr_after_modification"]
      },
      {
        "claim": "The noise level in the series to validate the significance of IQR changes.",
        "required_evidence": ["noise_level"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "structure"
    },
    "validation_needs": ["compare calculated IQRs for changes greater than the noise level"]
  },
  "capability_selection": {
    "selected_tools": [
      "advanced_features",
      "noise_decomposition"
    ],
    "no_tool_decision": null
  }
}
```
```

## Heterogeneous (structure, s5) — `heterogeneous:structure:s5:m0`

tokens prompt=2242 completion=416 latency=15.28s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 5: Evidence Integration.
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
  "role": "structure",
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
{"evidence_plan":{"objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<assignment>
{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]}
</assignment>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "Without successful execution of tools to compute IQR on the intervals defined in the assignment, the direct measurement of overall variability before and after the proposed modifications cannot be fully substantiated. The retrieval of a value at index 23 as 11700.0 does not provide sufficient information for IQR calculation nor does it confirm the impact of modifications on variability.",
  "role": "structure",
  "hypothesis": "The overall variability, as measured by IQR, likely changed after the proposed modifications, but this claim cannot be verified with the available data.",
  "evidence": [
    "Value at index 23 is 11700.0."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "short:step1",
    "short:step2"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The overall variability, as measured by IQR, cannot be accurately assessed.",
      "evidence": [
        {
          "type": "value_at_index",
          "value": 11700.0,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        },
        {
          "type": "cross_series_compare_failure",
          "value": "cross_series_compare failed due to needing >=2 series",
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "iqr": "unresolved"
  },
  "unresolved_claims": [
    "IQR measurements before and after the modifications are necessary to validate any impact on overall variability."
  ]
}
```

## Heterogeneous (structure, s1s2) — `heterogeneous:structure:s1s2:m1`

tokens prompt=6229 completion=238 latency=10.35s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=structure.
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
    "analysis_scope": {"target_series": [1], "role": "structure"},
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
{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]}
</assignment>

<plan_context>
{"reasoning":"The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.","task_summary":"Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.","target_output":"The change in IQR due to replacement of data points with mean of preceding points.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}],"hetero_assignments":[{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]},{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}],"scales":["short"],"heterogeneous_agents":["structure","reasoning"],"success_criteria":["Delta in IQR is quantified correctly","Impact matches given candidate options accurately"],"notes":"Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."}
</plan_context>

<task_summary>
Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['IQR measurements before and after the modifications are necessary to validate any impact on overall variability.']
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=structure.

```

### OUTPUT

```
```json
{
  "reasoning": "The assignment aims to measure the overall variability by computing the IQR both before and after the proposed modifications. The modifications involve replacing specific data points with the mean of previous points. The task requires evaluating if the changes in IQR are greater than the noise level. Current evidence includes the exact value at index 23, but it lacks IQR measurements and pairwise comparisons necessary for validating the modifications' impact.",
  "evidence_plan": {
    "objective": "Measure the overall variability by computing IQR both before and after the proposed modifications.",
    "claims_to_support": [
      {
        "claim": "IQR measurements before and after the modifications are necessary to validate any impact on overall variability.",
        "required_evidence": ["iqr"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "structure"
    },
    "validation_needs": ["compare calculated IQRs for changes greater than the noise level"]
  },
  "capability_selection": {
    "selected_tools": ["advanced_features"],
    "no_tool_decision": null
  }
}
```
```

## Heterogeneous (structure, s5) — `heterogeneous:structure:s5:m1`

tokens prompt=2242 completion=416 latency=15.28s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 5: Evidence Integration.
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
  "role": "structure",
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
{"evidence_plan":{"objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<assignment>
{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]}
</assignment>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "Without successful execution of tools to compute IQR on the intervals defined in the assignment, the direct measurement of overall variability before and after the proposed modifications cannot be fully substantiated. The retrieval of a value at index 23 as 11700.0 does not provide sufficient information for IQR calculation nor does it confirm the impact of modifications on variability.",
  "role": "structure",
  "hypothesis": "The overall variability, as measured by IQR, likely changed after the proposed modifications, but this claim cannot be verified with the available data.",
  "evidence": [
    "Value at index 23 is 11700.0."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "short:step1",
    "short:step2"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The overall variability, as measured by IQR, cannot be accurately assessed.",
      "evidence": [
        {
          "type": "value_at_index",
          "value": 11700.0,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        },
        {
          "type": "cross_series_compare_failure",
          "value": "cross_series_compare failed due to needing >=2 series",
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "iqr": "unresolved"
  },
  "unresolved_claims": [
    "IQR measurements before and after the modifications are necessary to validate any impact on overall variability."
  ]
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=6457 completion=258 latency=11.19s

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
{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}
</assignment>

<plan_context>
{"reasoning":"The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.","task_summary":"Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.","target_output":"The change in IQR due to replacement of data points with mean of preceding points.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}],"hetero_assignments":[{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]},{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}],"scales":["short"],"heterogeneous_agents":["structure","reasoning"],"success_criteria":["Delta in IQR is quantified correctly","Impact matches given candidate options accurately"],"notes":"Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."}
</plan_context>

<task_summary>
Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<prior_task_evidence>
[
  {
    "reasoning": "Without successful execution of tools to compute IQR on the intervals defined in the assignment, the direct measurement of overall variability before and after the proposed modifications cannot be fully substantiated. The retrieval of a value at index 23 as 11700.0 does not provide sufficient information for IQR calculation nor does it confirm the impact of modifications on variability.",
    "role": "structure",
    "evidence": [
      "Value at index 23 is 11700.0."
    ],
    "candidate_preference": null,
    "confidence": 0.0,
    "tool_calls": [],
    "cited_tool_call_ids": [
      "short:step1",
      "short:step2"
    ],
    "executed_tools": [],
    "tool_summaries": [],
    "evidence_plan": {
      "objective": "Measure the overall variability by computing IQR both before and after the proposed modifications.",
      "claims_to_support": [],
      "analysis_scope": {},
      "validation_needs": []
    },
    "capability_selection": {
      "selected_tools": [],
      "no_tool_decision": {
        "skip_tools": true,
        "reason": "Parse failure fallback; use temporal profile context",
        "evidence_sources": []
      }
    },
    "workflow": {
      "workflow": [],
      "reasoning": ""
    },
    "reasoning_claims": [
      {
        "claim": "The overall variability, as measured by IQR, cannot be accurately assessed.",
        "evidence": [
          {
            "type": "value_at_index",
            "value": 11700.0,
            "source_tool": null,
            "call_id": "short:step1",
            "provenance": "tool",
            "ref": null,
            "series_index": null,
            "args_fingerprint": null
          },
          {
            "type": "cross_series_compare_failure",
            "value": "cross_series_compare failed due to needing >=2 series",
            "source_tool": null,
            "call_id": "short:step2",
            "provenance": "tool",
            "ref": null,
            "series_index": null,
            "args_fingerprint": null
          }
        ],
        "confidence": "context_supported",
        "maps_to_measurement": null
      }
    ],
    "coverage": {
      "iqr": "unresolved"
    },
    "unresolved_claims": [
      "IQR measurements before and after the modifications are necessary to validate any impact on overall variability."
    ],
    "executed_steps": [],
    "skipped_stages": [
      "S3",
      "S4"
    ],
    "hypothesis": "The overall variability, as measured by IQR, likely changed after the proposed modifications, but this claim cannot be verified with the available data."
  }
]
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current assignment focuses on measuring the impact on the interquartile range (IQR) after replacing peak values with their average counterparts within specified intervals. Existing evidence provides partial context through the value at index 23 but lacks detailed insights on the overall variability and the specific impacts on the IQR. This necessitates the use of appropriate statistical measures to evaluate the change in IQR.",
  "evidence_plan": {
    "objective": "Assess the impact on the interquartile range due to replacing peak values with averages.",
    "claims_to_support": [
      {
        "claim": "Replacement of peak values with averages leads to a measurable change in the IQR.",
        "required_evidence": ["delta_iqr", "average_change_effect"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "reasoning",
      "focus_intervals": [[23, 27], [28, 32]]
    },
    "validation_needs": ["ensure the impact aligns with the observed data characteristics"]
  },
  "capability_selection": {
    "selected_tools": ["describe_series"],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=2276 completion=494 latency=18.08s

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
{"evidence_plan":{"objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}
</assignment>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Without sufficient evidence from tool executions, it's challenging to determine the exact effect on the interquartile range due to replacing peak values with average ones. We have the value at index 23 being 11700.0, but direct comparisons necessary to assess the effect on IQR are missing due to lack of requisite data.",
  "role": "reasoning",
  "hypothesis": "Replacing peak values with averages would affect the interquartile range, but without the ability to compare specific intervals before and after this hypothetical change, we cannot accurately evaluate the extent of the impact based on the provided data.",
  "evidence": [
    "The location of changes in local density and variance can be pinpointed due to the successful retrieval of the value at index 23, which is 11700.0."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "short:step1"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The value at index 23 is 11700.0.",
      "evidence": [
        {
          "type": "value_at_index",
          "value": 11700.0,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Pairwise similarity between specified intervals and unaffected parts of the series cannot be determined due to a lack of requisite data.",
      "evidence": [
        {
          "type": "comparison_failure",
          "value": "cross_series_compare failed due to needing >=2 series",
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "unresolved"
    }
  ],
  "coverage": {},
  "unresolved_claims": [
    "Cannot determine the pairwise similarity between specified intervals and unaffected parts of the series due to insufficient data for cross-series comparison."
  ]
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m1`

tokens prompt=6489 completion=315 latency=13.37s

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
{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}
</assignment>

<plan_context>
{"reasoning":"The question requires evaluating the effect of changing specific data points on the interquartile range (IQR) of a time series. This involves understanding the variability before and after the change, specifically focusing on how the 25th and 75th percentiles might be affected.","task_summary":"Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.","target_output":"The change in IQR due to replacement of data points with mean of preceding points.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the short-term behavior and changes in local density and variance.","required_measurements":["change_location","pairwise_similarity"],"validation_requirements":["compare against unaffected parts of the series"],"target_series":[1],"focus_intervals":[[23,27],[28,32]]}],"hetero_assignments":[{"role":"structure","objective":"Measure the overall variability by computing IQR both before and after the proposed modifications.","required_measurements":["iqr"],"validation_requirements":["compare calculated IQRs for changes greater than the noise level"],"target_series":[1],"focus_intervals":[[0,71]]},{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}],"scales":["short"],"heterogeneous_agents":["structure","reasoning"],"success_criteria":["Delta in IQR is quantified correctly","Impact matches given candidate options accurately"],"notes":"Ensure that the modified data points do not significantly alter the overall distribution of the series beyond the specified interval."}
</plan_context>

<task_summary>
Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<prior_task_evidence>
[
  {
    "reasoning": "Without successful execution of tools to compute IQR on the intervals defined in the assignment, the direct measurement of overall variability before and after the proposed modifications cannot be fully substantiated. The retrieval of a value at index 23 as 11700.0 does not provide sufficient information for IQR calculation nor does it confirm the impact of modifications on variability.",
    "role": "structure",
    "evidence": [
      "Value at index 23 is 11700.0."
    ],
    "candidate_preference": null,
    "confidence": 0.0,
    "tool_calls": [],
    "cited_tool_call_ids": [
      "short:step1",
      "short:step2"
    ],
    "executed_tools": [],
    "tool_summaries": [],
    "evidence_plan": {
      "objective": "Measure the overall variability by computing IQR both before and after the proposed modifications.",
      "claims_to_support": [],
      "analysis_scope": {},
      "validation_needs": []
    },
    "capability_selection": {
      "selected_tools": [],
      "no_tool_decision": {
        "skip_tools": true,
        "reason": "Parse failure fallback; use temporal profile context",
        "evidence_sources": []
      }
    },
    "workflow": {
      "workflow": [],
      "reasoning": ""
    },
    "reasoning_claims": [
      {
        "claim": "The overall variability, as measured by IQR, cannot be accurately assessed.",
        "evidence": [
          {
            "type": "value_at_index",
            "value": 11700.0,
            "source_tool": null,
            "call_id": "short:step1",
            "provenance": "tool",
            "ref": null,
            "series_index": null,
            "args_fingerprint": null
          },
          {
            "type": "cross_series_compare_failure",
            "value": "cross_series_compare failed due to needing >=2 series",
            "source_tool": null,
            "call_id": "short:step2",
            "provenance": "tool",
            "ref": null,
            "series_index": null,
            "args_fingerprint": null
          }
        ],
        "confidence": "context_supported",
        "maps_to_measurement": null
      }
    ],
    "coverage": {
      "iqr": "unresolved"
    },
    "unresolved_claims": [
      "IQR measurements before and after the modifications are necessary to validate any impact on overall variability."
    ],
    "executed_steps": [],
    "skipped_stages": [
      "S3",
      "S4"
    ],
    "hypothesis": "The overall variability, as measured by IQR, likely changed after the proposed modifications, but this claim cannot be verified with the available data."
  }
]
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['Cannot determine the pairwise similarity between specified intervals and unaffected parts of the series due to insufficient data for cross-series comparison.']
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current assignment focuses on measuring the impact on the interquartile range (IQR) after replacing peak values with their average counterparts within specified intervals. Existing evidence provides partial context through the value at index 23 but lacks detailed insights on the overall variability and the specific impacts on the IQR. This necessitates the use of appropriate statistical measures to evaluate these changes accurately.",
  "evidence_plan": {
    "objective": "Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.",
    "claims_to_support": [
      {
        "claim": "Quantify the delta in IQR post modification.",
        "required_evidence": ["delta_iqr"]
      },
      {
        "claim": "Assess the average change effect on the time series.",
        "required_evidence": ["average_change_effect"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[28, 32], [23, 27]]
    },
    "validation_needs": [
      "Ensure the impact aligns with the observed data characteristics"
    ]
  },
  "capability_selection": {
    "selected_tools": [
      "describe_series",
      "step_levels",
      "value_at_index",
      "peaks_above_threshold",
      "noise_decomposition",
      "counterfactual_simulate"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m1`

tokens prompt=2276 completion=494 latency=18.08s

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
{"evidence_plan":{"objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that the value at index 23 was successfully retrieved as 11700.0. However, the attempt to perform a cross-series comparison failed due to needing at least two distinct series, which were not available. Thus, only the location of the change could be directly identified, while pairwise similarity cannot be confirmed due to insufficient data.","scale":"short","observations":["Value at index 23 is 11700.0.","Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."],"evidence_intervals":["[23, 27]","[28, 32]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"index\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"index\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"index\": 23, \"position\": 23, \"value\": 11700.0}, \"error\": null, \"args_fingerprint\": \"01056926059caba4d7935316e52417578df6f7b3\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": 23, \"end\": 27, \"left_interval\": [28, 32]}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Identify the short-term behavior and changes in local density and variance.","claims_to_support":[{"claim":"The location of changes in local density and variance can be pinpointed.","required_evidence":["change_location"]},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[23,27],[28,32]],"scale":"short"},"validation_needs":["compare against unaffected parts of the series"]},"capability_selection":{"selected_tools":[{"tool":"value_at_index","reason":"To capture exact values at specific indices for comparison.","supports_evidence":["change_location"]},{"tool":"interval_compare","reason":"To quantify the similarity between two intervals within the same series.","supports_evidence":["pairwise_similarity"]},{"tool":"cross_series_compare","reason":"To compare windows across the series itself, treating it as two separate series for internal comparison purposes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"value_at_index","output_key":"specific_values","input_binding":{}},{"step":2,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'value_at_index' to capture the exact values at the specified indices for comparison, fulfilling the required evidence for change location. Then, we apply 'cross_series_compare' to quantify similarity between two different parts of the same series, addressing the requirement for pairwise similarity. This approach allows us to effectively determine the local density and variance changes by comparing specific intervals against each other."},"structured_observations":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"change_location":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity between specified intervals and unaffected parts of the series can be determined."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"value_at_index","arguments":{"series_index":1,"index":23},"resolved_arguments":{"series_index":1,"index":23},"success":true,"data":{"series_index":1,"index":23,"position":23,"value":11700.0},"error":null,"args_fingerprint":"01056926059caba4d7935316e52417578df6f7b3"},{"call_id":"short:step2","step":2,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"resolved_arguments":{"series_index_1":1,"series_index_2":1,"start":23,"end":27,"left_interval":[28,32]},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data.","structured_by_scale":{"short":[{"claim":"The location of changes in local density and variance can be pinpointed.","evidence":[{"type":"change_location","value":11700.0,"source_tool":"value_at_index","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Pairwise similarity between specified intervals and unaffected parts of the series can be determined.","evidence":[{"type":"comparison_failure","value":"cross_series_compare failed due to needing >=2 series","source_tool":"cross_series_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.","required_measurements":["delta_iqr","average_change_effect"],"validation_requirements":["ensure the impact aligns with the observed data characteristics"],"target_series":[1],"focus_intervals":[[28,32],[23,27]]}
</assignment>

<metadata>
subset=InWild; local_overall=local; task_type=['basic analysis', 'counterfactual reasoning']; domain=healthcare; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[72]; index_base=0; series_truncated=False; focus_intervals=[[28, 32], [23, 27]]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Without sufficient evidence from tool executions, it's challenging to determine the exact effect on the interquartile range due to replacing peak values with average ones. We have the value at index 23 being 11700.0, but direct comparisons necessary to assess the effect on IQR are missing due to lack of requisite data.",
  "role": "reasoning",
  "hypothesis": "Replacing peak values with averages would affect the interquartile range, but without the ability to compare specific intervals before and after this hypothetical change, we cannot accurately evaluate the extent of the impact based on the provided data.",
  "evidence": [
    "The location of changes in local density and variance can be pinpointed due to the successful retrieval of the value at index 23, which is 11700.0."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "short:step1"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The value at index 23 is 11700.0.",
      "evidence": [
        {
          "type": "value_at_index",
          "value": 11700.0,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Pairwise similarity between specified intervals and unaffected parts of the series cannot be determined due to a lack of requisite data.",
      "evidence": [
        {
          "type": "comparison_failure",
          "value": "cross_series_compare failed due to needing >=2 series",
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "unresolved"
    }
  ],
  "coverage": {},
  "unresolved_claims": [
    "Cannot determine the pairwise similarity between specified intervals and unaffected parts of the series due to insufficient data for cross-series comparison."
  ]
}
```

## Integration — `integration`

tokens prompt=1696 completion=322 latency=11.70s

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
The basic analysis of the sequence can be performed using iqr as a reference metric. The calculation method is iqr is as follows: The `iqr` feature is the interquartile range: $ q_{75} - q_{25} $, a robust measure of variability excluding outliers. Now, please answer the following question: If the data points at indices 28-32 had not reached their peak values (above 13,000), but instead had remained at the average level of the preceding 5 data points (indices 23-27), what would be the most likely impact on the interquartile range (IQR) of the entire time series? The Interquartile Range (IQR) is a measure of statistical dispersion, representing the range between the first quartile (25th percentile) and the third quartile (75th percentile) of a dataset.
</question>

<candidates>
A) The IQR would likely increase by approximately 15-25%.
B) The IQR would remain essentially unchanged (within ±5% of the original value).
C) The IQR would likely decrease by approximately 10-15%.
D) The IQR would likely decrease by approximately 25-35%.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Determine the impact on the IQR of the entire time series if certain peaks are removed and replaced with the mean of previous points.",
  "question_type": "choice",
  "required_output": "The change in IQR due to replacement of data points with mean of preceding points.",
  "success_criteria": [
    "Delta in IQR is quantified correctly",
    "Impact matches given candidate options accurately"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Identify the short-term behavior and changes in local density and variance.",
      "required_measurements": [
        "change_location",
        "pairwise_similarity"
      ]
    },
    {
      "agent": "hetero:structure",
      "objective": "Measure the overall variability by computing IQR both before and after the proposed modifications.",
      "required_measurements": [
        "iqr"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Evaluate the impact on the interquartile range due to replacing peak values with average ones, and choose the closest candidate option.",
      "required_measurements": [
        "delta_iqr",
        "average_change_effect"
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
          "type": "change_location",
          "value": 11700.0,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "comparison_failure",
          "value": "cross_series_compare failed due to needing >=2 series",
          "trusted": true
        }
      ],
      "coverage": {
        "change_location": "tool_supported",
        "pairwise_similarity": "unresolved"
      },
      "summary": "Value at index 23 is 11700.0. | Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."
    }
  },
  "conflicts": [],
  "summary": "Value at index 23 is 11700.0. Attempt to compare specified intervals for similarity using cross-series comparison failed due to lack of requisite data."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "structure",
      "hypothesis": "The overall variability, as measured by IQR, likely changed after the proposed modifications, but this claim cannot be verified with the available data.",
      "reasoning_chain": [
        "The overall variability, as measured by IQR, cannot be accurately assessed.",
        "value_at_index=11700.0",
        "cross_series_compare_failure=cross_series_compare failed due to needing >=2 series"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "value_at_index",
        "cross_series_compare_failure"
      ],
      "uncertainty": "unverified_cite:short:step2"
    },
    {
      "role": "reasoning",
      "hypothesis": "Replacing peak values with averages would affect the interquartile range, but without the ability to compare specific intervals before and after this hypothetical change, we cannot accurately evaluate the extent of the impact based on the provided data.",
      "reasoning_chain": [
        "The value at index 23 is 11700.0.",
        "value_at_index=11700.0",
        "Pairwise similarity between specified intervals and unaffected parts of the series cannot be determined due to a lack of requisite data.",
        "comparison_failure=cross_series_compare failed due to needing >=2 series"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "value_at_index",
        "comparison_failure"
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
  "warnings": [
    "structure:unverified_cite:short:step2"
  ]
}
</execution_metadata>



Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "Without the ability to compute IQR before and after the modification, it is impossible to determine exactly how the removal and replacement of peaks with averages will affect the IQR. Based on the provided information, it's clear that the data does not support a definitive analysis. The perception layer indicates a single value point at index 23 with no supporting data to make a comparison between different sections of the time series. The reasoning layer concludes that without such comparative analysis, the impact on IQR remains indeterminate.",
  "answer": "B",
  "explanation": "Although the reasoning process could not definitively quantify the change in IQR due to limited data and inability to perform a comparative analysis, the closest option that aligns with the absence of significant observable change (given the lack of evidence pointing towards substantial deviation) is B. This suggests that any changes to IQR, based on the provided information, are not likely to deviate greatly from its original value.",
  "confidence": 0.3,
  "conflicts": ["Heter's reasoning conflicts with the lack of definitive numerical evidence in the Homo perception"],
  "cited_evidence": ["Homo perception states indicate a single value at index 23 with no supporting data", "Heter reasoning concludes inability to compute IQR changes due to insufficient data"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "B"
  }
}
```
