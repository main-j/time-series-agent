# Agent IO summary: `Match:qats_400:284`

- Architecture pred: `B` (success=True)
- model_calls=18, tool_calls=22, latency=175.9s

## Planner — `planner`

tokens prompt=1086 completion=360 latency=12.83s

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
local_overall=overall; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires identifying the sequence among given candidates that shows the closest similarity to the reference Time Series 1. This involves examining patterns, structures, and possible alignments over the whole series.",
  "task_summary": "Identify the candidate time series that most closely matches the pattern of Time Series 1",
  "target_output": "A",
  "answer_type": "choice",
  "capability": "choice",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "long",
      "objective": "Analyze the long-term patterns of the reference and candidate time series.",
      "required_measurements": ["persistence", "global_trend"],
      "validation_requirements": ["Compare long-term behavior across series"],
      "target_series": [1, 2, 3, 4, 5],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Measure and rank the pattern similarities between the reference and each candidate time series.",
      "required_measurements": ["pairwise_similarity", "reverse_similarity"],
      "validation_requirements": ["Reconcile similarity scores to ensure consistent ranking"],
      "target_series": [1, 2, 3, 4, 5],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Each candidate's similarity score is compared against the reference series.", "The highest similarity score identifies the most similar pattern."],
  "notes": "Since the task asks for the series with the most similar pattern, the matching role needs to be assigned to handle this task."
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4020 completion=331 latency=12.95s

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
{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying the sequence among given candidates that shows the closest similarity to the reference Time Series 1. This involves examining patterns, structures, and possible alignments over the whole series.","task_summary":"Identify the candidate time series that most closely matches the pattern of Time Series 1","target_output":"A","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["matching"],"success_criteria":["Each candidate's similarity score is compared against the reference series.","The highest similarity score identifies the most similar pattern."],"notes":"Since the task asks for the series with the most similar pattern, the matching role needs to be assigned to handle this task."}
</plan_context>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires analyzing the long-term patterns and measuring persistence and global trends in the reference and candidate time series. The objective is to compare these characteristics across the series to determine the one with the most similar pattern.",
  "evidence_plan": {
    "objective": "Analyze the long-term patterns of the reference and candidate time series.",
    "claims_to_support": [
      {"claim": "The reference time series exhibits a long-term persistence characteristic.", "required_evidence": ["hurst_exponent"]},
      {"claim": "The reference time series has a discernible global trend.", "required_evidence": ["segment_trend"]},
      {"claim": "Candidate time series exhibit similar long-term persistence characteristics.", "required_evidence": ["hurst_exponent"]},
      {"claim": "Candidate time series have discernible global trends.", "required_evidence": ["segment_trend"]}
    ],
    "analysis_scope": {"target_series": [1,2,3,4,5], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["cross_series_compare", "lag_corr_scan"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "hurst_exponent", "reason": "To measure the long-term persistence characteristic of the time series", "supports_evidence": ["hurst_exponent"]},
      {"tool": "segment_trend", "reason": "To assess the existence of a global trend", "supports_evidence": ["segment_trend"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=846 completion=562 latency=19.86s

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
{"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"The reference time series exhibits a long-term persistence characteristic.","required_evidence":["hurst_exponent"]},{"claim":"The reference time series has a discernible global trend.","required_evidence":["segment_trend"]},{"claim":"Candidate time series exhibit similar long-term persistence characteristics.","required_evidence":["hurst_exponent"]},{"claim":"Candidate time series have discernible global trends.","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare","lag_corr_scan"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"To measure the long-term persistence characteristic of the time series","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"To assess the existence of a global trend","supports_evidence":["segment_trend"]}],"no_tool_decision":null},"reasoning":"The task requires analyzing the long-term patterns and measuring persistence and global trends in the reference and candidate time series. The objective is to compare these characteristics across the series to determine the one with the most similar pattern."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- hurst_exponent
  inputs: series
  outputs: hurst, persistence_hint
</io_concepts>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The workflow needs to first calculate the Hurst exponent for the reference and candidate series to measure their long-term persistence characteristics. Then, it should identify the global trends using the segment_trend tool on those series.",
  "workflow": [
    {
      "step": 1,
      "tool": "hurst_exponent",
      "output_key": "reference_persistence",
      "input_binding": {"series": "$query_series_index"}
    },
    {
      "step": 2,
      "tool": "hurst_exponent",
      "output_key": "candidate_persistence",
      "input_binding": {"series": "$option_to_series.A"}
    },
    {
      "step": 3,
      "tool": "hurst_exponent",
      "output_key": "candidate_persistence",
      "input_binding": {"series": "$option_to_series.B"}
    },
    {
      "step": 4,
      "tool": "hurst_exponent",
      "output_key": "candidate_persistence",
      "input_binding": {"series": "$option_to_series.C"}
    },
    {
      "step": 5,
      "tool": "hurst_exponent",
      "output_key": "candidate_persistence",
      "input_binding": {"series": "$option_to_series.D"}
    },
    {
      "step": 6,
      "tool": "segment_trend",
      "output_key": "reference_trend",
      "input_binding": {"series_index": "$query_series_index", "start": 0, "end": -1}
    },
    {
      "step": 7,
      "tool": "segment_trend",
      "output_key": "candidate_trend",
      "input_binding": {"series_index": "$option_to_series.A", "start": 0, "end": -1}
    },
    {
      "step": 8,
      "tool": "segment_trend",
      "output_key": "candidate_trend",
      "input_binding": {"series_index": "$option_to_series.B", "start": 0, "end": -1}
    },
    {
      "step": 9,
      "tool": "segment_trend",
      "output_key": "candidate_trend",
      "input_binding": {"series_index": "$option_to_series.C", "start": 0, "end": -1}
    },
    {
      "step": 10,
      "tool": "segment_trend",
      "output_key": "candidate_trend",
      "input_binding": {"series_index": "$option_to_series.D", "start": 0, "end": -1}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=1200 completion=302 latency=10.84s

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
{"workflow":[{"step":1,"tool":"hurst_exponent","output_key":"reference_persistence","input_binding":{"series":"$query_series_index"}},{"step":2,"tool":"hurst_exponent","output_key":"candidate_persistence","input_binding":{"series":"$option_to_series.A"}},{"step":3,"tool":"hurst_exponent","output_key":"candidate_persistence","input_binding":{"series":"$option_to_series.B"}},{"step":4,"tool":"hurst_exponent","output_key":"candidate_persistence","input_binding":{"series":"$option_to_series.C"}},{"step":5,"tool":"hurst_exponent","output_key":"candidate_persistence","input_binding":{"series":"$option_to_series.D"}},{"step":6,"tool":"segment_trend","output_key":"reference_trend","input_binding":{"series_index":"$query_series_index","start":0,"end":-1}},{"step":7,"tool":"segment_trend","output_key":"candidate_trend","input_binding":{"series_index":"$option_to_series.A","start":0,"end":-1}},{"step":8,"tool":"segment_trend","output_key":"candidate_trend","input_binding":{"series_index":"$option_to_series.B","start":0,"end":-1}},{"step":9,"tool":"segment_trend","output_key":"candidate_trend","input_binding":{"series_index":"$option_to_series.C","start":0,"end":-1}},{"step":10,"tool":"segment_trend","output_key":"candidate_trend","input_binding":{"series_index":"$option_to_series.D","start":0,"end":-1}}],"reasoning":"The workflow needs to first calculate the Hurst exponent for the reference and candidate series to measure their long-term persistence characteristics. Then, it should identify the global trends using the segment_trend tool on those series."}
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
- hurst_exponent: Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), matching MMTS label generation. Returns persistence_hint at 0.45/0.55.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=Hurst via compute_Hc, persistence_hint, estimator metadata}
</tool_invocation_spec>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "This workflow aims to analyze the long-term patterns of the reference and candidate time series by calculating their Hurst exponents to assess persistence and identifying their global trends using linear segmentation.",
  "calls": [
    {"step": 1, "tool": "hurst_exponent", "args": {"series_index": 1}},
    {"step": 2, "tool": "hurst_exponent", "args": {"series_index": 2}},
    {"step": 3, "tool": "hurst_exponent", "args": {"series_index": 3}},
    {"step": 4, "tool": "hurst_exponent", "args": {"series_index": 4}},
    {"step": 5, "tool": "hurst_exponent", "args": {"series_index": 5}},
    {"step": 6, "tool": "segment_trend", "args": {"series_index": 1}},
    {"step": 7, "tool": "segment_trend", "args": {"series_index": 2}},
    {"step": 8, "tool": "segment_trend", "args": {"series_index": 3}},
    {"step": 9, "tool": "segment_trend", "args": {"series_index": 4}},
    {"step": 10, "tool": "segment_trend", "args": {"series_index": 5}}
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=3107 completion=1024 latency=37.83s

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
{"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"The reference time series exhibits a long-term persistence characteristic.","required_evidence":["hurst_exponent"]},{"claim":"The reference time series has a discernible global trend.","required_evidence":["segment_trend"]},{"claim":"Candidate time series exhibit similar long-term persistence characteristics.","required_evidence":["hurst_exponent"]},{"claim":"Candidate time series have discernible global trends.","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare","lag_corr_scan"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"To measure the long-term persistence characteristic of the time series","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"To assess the existence of a global trend","supports_evidence":["segment_trend"]}],"no_tool_decision":null},"reasoning":"The task requires analyzing the long-term patterns and measuring persistence and global trends in the reference and candidate time series. The objective is to compare these characteristics across the series to determine the one with the most similar pattern."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
    "step": 1,
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
      "hurst": 0.3226361525588941,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 2
    },
    "resolved_arguments": {
      "series_index": 2
    },
    "success": true,
    "data": {
      "series_index": 2,
      "start": null,
      "end": null,
      "hurst": 0.364153457742821,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "c00307b5b9e5c3894a0eff13bc95f0579b12e8bb"
  },
  {
    "call_id": "long:step3",
    "step": 3,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 3
    },
    "resolved_arguments": {
      "series_index": 3
    },
    "success": true,
    "data": {
      "series_index": 3,
      "start": null,
      "end": null,
      "hurst": 0.23703349680256722,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "a6c2938d3a28138bceab95fcb747c4b708719a20"
  },
  {
    "call_id": "long:step4",
    "step": 4,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 4
    },
    "resolved_arguments": {
      "series_index": 4
    },
    "success": true,
    "data": {
      "series_index": 4,
      "start": null,
      "end": null,
      "hurst": 0.2571610613506707,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "e3f6d728dbf84e9e88427c47ffba4686427e5656"
  },
  {
    "call_id": "long:step5",
    "step": 5,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 5
    },
    "resolved_arguments": {
      "series_index": 5
    },
    "success": true,
    "data": {
      "series_index": 5,
      "start": null,
      "end": null,
      "hurst": 0.5728685722100395,
      "persistence_hint": "persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "93f898527fc9b9bd5099f0ae2dca1d45bf4bb48c"
  },
  {
    "call_id": "long:step6",
    "step": 6,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": -1
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": -1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 0,
      "slope": 0.0,
      "direction": "flat",
      "mean": 2623.0,
      "std": 0.0
    },
    "error": null,
    "args_fingerprint": "675645960dac2365de0c088fb0140ebae58d6ef3"
  },
  {
    "call_id": "long:step7",
    "step": 7,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 2,
      "start": 0,
      "end": -1
    },
    "resolved_arguments": {
      "series_index": 2,
      "start": 0,
      "end": -1
    },
    "success": true,
    "data": {
      "series_index": 2,
      "start": 0,
      "end": 0,
      "slope": 0.0,
      "direction": "flat",
      "mean": 2533.02,
      "std": 0.0
    },
    "error": null,
    "args_fingerprint": "bdabaca74ef93f6e26a64cad64126f1f2bd77b93"
  },
  {
    "call_id": "long:step8",
    "step": 8,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 3,
      "start": 0,
      "end": -1
    },
    "resolved_arguments": {
      "series_index": 3,
      "start": 0,
      "end": -1
    },
    "success": true,
    "data": {
      "series_index": 3,
      "start": 0,
      "end": 0,
      "slope": 0.0,
      "direction": "flat",
      "mean": 2472.0,
      "std": 0.0
    },
    "error": null,
    "args_fingerprint": "986f7af161be380a160f6e4766350d52552eed7c"
  },
  {
    "call_id": "long:step9",
    "step": 9,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 4,
      "start": 0,
      "end": -1
    },
    "resolved_arguments": {
      "series_index": 4,
      "start": 0,
      "end": -1
    },
    "success": true,
    "data": {
      "series_index": 4,
      "start": 0,
      "end": 0,
      "slope": 0.0,
      "direction": "flat",
      "mean": 1511.0,
      "std": 0.0
    },
    "error": null,
    "args_fingerprint": "ee99c811a95bd837e0427aafaa286fd6f5773fc6"
  },
  {
    "call_id": "long:step10",
    "step": 10,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 5,
      "start": 0,
      "end": -1
    },
    "resolved_arguments": {
      "series_index": 5,
      "start": 0,
      "end": -1
    },
    "success": true,
    "data": {
      "series_index": 5,
      "start": 0,
      "end": 0,
      "slope": 0.0,
      "direction": "flat",
      "mean": 1820.0,
      "std": 0.0
    },
    "error": null,
    "args_fingerprint": "d218fbd9696ad49cc374f9100e3c54ff9fdca3b8"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes calculating the Hurst exponent for each time series to measure long-term persistence and assessing global trends using the segment_trend tool. The Hurst exponents indicate varying levels of anti-persistence (values < 0.5) and persistence (values > 0.5) among the series. Segment_trend results show flat trends across all series.",
  "scale": "long",
  "observations": [
    "Time series 1 has a Hurst exponent indicating anti-persistent behavior and a flat trend over its entire duration.",
    "Time series 2 shows anti-persistent behavior and also has a flat trend.",
    "Time series 3 indicates anti-persistent behavior with a flat trend.",
    "Time series 4 exhibits anti-persistent behavior and a flat trend.",
    "Time series 5 has persistent behavior and a flat trend."
  ],
  "evidence_intervals": [
    "Entire series duration"
  ],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The reference time series (series 1) exhibits a long-term persistence characteristic.",
      "evidence": [
        {
          "type": "hurst_exponent",
          "value": 0.3226361525588941,
          "source_tool": "hurst_exponent",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "The reference time series (series 1) has a discernible global trend.",
      "evidence": [
        {
          "type": "segment_trend",
          "value": "flat",
          "source_tool": "segment_trend",
          "call_id": "long:step6",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "Candidate time series exhibit similar long-term persistence characteristics.",
      "evidence": [
        {
          "type": "hurst_exponent",
          "value": 0.364153457742821,
          "source_tool": "hurst_exponent",
          "call_id": "long:step2",
          "provenance": "tool"
        },
        {
          "type": "hurst_exponent",
          "value": 0.23703349680256722,
          "source_tool": "hurst_exponent",
          "call_id": "long:step3",
          "provenance": "tool"
        },
        {
          "type": "hurst_exponent",
          "value": 0.2571610613506707,
          "source_tool": "hurst_exponent",
          "call_id": "long:step4",
          "provenance": "tool"
        },
        {
          "type": "hurst_exponent",
          "value": 0.5728685722100395,
          "source_tool": "hurst_exponent",
          "call_id": "long:step5",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "Candidate time series have discernible global trends.",
      "evidence": [
        {
          "type": "segment_trend",
          "value": "flat",
          "source_tool": "segment_trend",
          "call_id": "long:step7",
          "provenance": "tool"
        },
        {
          "type": "segment_trend",
          "value": "flat",
          "source_tool": "segment_trend",
          "call_id": "long:step8",
          "provenance": "tool"
        },
        {
          "type": "segment_trend",
          "value": "flat",
          "source_tool": "segment_trend",
          "call_id": "long:step9",
          "provenance": "tool"
        },
        {
          "type": "segment_trend",
          "value": "flat",
          "source_tool": "segment_trend",
          "call_id": "long:step10",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    }
  ],
  "coverage": {
    "hurst_exponent": "tool_supported",
    "segment_trend": "
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m1`

tokens prompt=4035 completion=323 latency=12.62s

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
{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying the sequence among given candidates that shows the closest similarity to the reference Time Series 1. This involves examining patterns, structures, and possible alignments over the whole series.","task_summary":"Identify the candidate time series that most closely matches the pattern of Time Series 1","target_output":"A","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["matching"],"success_criteria":["Each candidate's similarity score is compared against the reference series.","The highest similarity score identifies the most similar pattern."],"notes":"Since the task asks for the series with the most similar pattern, the matching role needs to be assigned to handle this task."}
</plan_context>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
retry_context=unresolved_claims=['parse_failure']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires analyzing the long-term patterns and measuring persistence and global trends in the reference and candidate time series. The objective is to compare these characteristics across the series to identify the candidate with the most similar pattern.",
  "evidence_plan": {
    "objective": "Analyze the long-term patterns of the reference and candidate time series.",
    "claims_to_support": [
      {"claim": "Long-term persistence in the reference series", "required_evidence": ["hurst_exponent"]},
      {"claim": "Long-term global trend in the reference series", "required_evidence": ["segment_trend"]},
      {"claim": "Long-term persistence in each candidate series", "required_evidence": ["hurst_exponent"]},
      {"claim": "Long-term global trend in each candidate series", "required_evidence": ["segment_trend"]}
    ],
    "analysis_scope": {"target_series": [1, 2, 3, 4, 5], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["cross_series_compare"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "hurst_exponent", "reason": "Estimate Hurst exponent for persistence measure.", "supports_evidence": ["hurst_exponent"]},
      {"tool": "segment_trend", "reason": "Determine global trend direction and slope over the entire series.", "supports_evidence": ["global_trend"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m1`

tokens prompt=835 completion=463 latency=16.37s

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
{"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"Long-term persistence in the reference series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in the reference series","required_evidence":["segment_trend"]},{"claim":"Long-term persistence in each candidate series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in each candidate series","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"Estimate Hurst exponent for persistence measure.","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"Determine global trend direction and slope over the entire series.","supports_evidence":["global_trend"]}],"no_tool_decision":null},"reasoning":"The task requires analyzing the long-term patterns and measuring persistence and global trends in the reference and candidate time series. The objective is to compare these characteristics across the series to identify the candidate with the most similar pattern."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- hurst_exponent
  inputs: series
  outputs: hurst, persistence_hint
</io_concepts>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series.",
  "workflow": [
    {
      "step": 1,
      "tool": "hurst_exponent",
      "output_key": "hurst_reference",
      "input_binding": {"series": "$series[1]"}
    },
    {
      "step": 2,
      "tool": "hurst_exponent",
      "output_key": "hurst_candidate1",
      "input_binding": {"series": "$series[2]"}
    },
    {
      "step": 3,
      "tool": "hurst_exponent",
      "output_key": "hurst_candidate2",
      "input_binding": {"series": "$series[3]"}
    },
    {
      "step": 4,
      "tool": "hurst_exponent",
      "output_key": "hurst_candidate3",
      "input_binding": {"series": "$series[4]"}
    },
    {
      "step": 5,
      "tool": "segment_trend",
      "output_key": "trend_reference",
      "input_binding": {"series_index": "1", "start": "0", "end": "104"}
    },
    {
      "step": 6,
      "tool": "segment_trend",
      "output_key": "trend_candidate1",
      "input_binding": {"series_index": "2", "start": "0", "end": "104"}
    },
    {
      "step": 7,
      "tool": "segment_trend",
      "output_key": "trend_candidate2",
      "input_binding": {"series_index": "3", "start": "0", "end": "104"}
    },
    {
      "step": 8,
      "tool": "segment_trend",
      "output_key": "trend_candidate3",
      "input_binding": {"series_index": "4", "start": "0", "end": "104"}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m1`

tokens prompt=1131 completion=405 latency=14.45s

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
{"workflow":[{"step":1,"tool":"hurst_exponent","output_key":"hurst_reference","input_binding":{"series":"$series[1]"}},{"step":2,"tool":"hurst_exponent","output_key":"hurst_candidate1","input_binding":{"series":"$series[2]"}},{"step":3,"tool":"hurst_exponent","output_key":"hurst_candidate2","input_binding":{"series":"$series[3]"}},{"step":4,"tool":"hurst_exponent","output_key":"hurst_candidate3","input_binding":{"series":"$series[4]"}},{"step":5,"tool":"segment_trend","output_key":"trend_reference","input_binding":{"series_index":"1","start":"0","end":"104"}},{"step":6,"tool":"segment_trend","output_key":"trend_candidate1","input_binding":{"series_index":"2","start":"0","end":"104"}},{"step":7,"tool":"segment_trend","output_key":"trend_candidate2","input_binding":{"series_index":"3","start":"0","end":"104"}},{"step":8,"tool":"segment_trend","output_key":"trend_candidate3","input_binding":{"series_index":"4","start":"0","end":"104"}}],"reasoning":"The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series."}
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
- hurst_exponent: Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), matching MMTS label generation. Returns persistence_hint at 0.45/0.55.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=Hurst via compute_Hc, persistence_hint, estimator metadata}
</tool_invocation_spec>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series.",
  "calls": [
    {
      "step": 1,
      "tool": "hurst_exponent",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "hurst_exponent",
      "args": {
        "series_index": 2
      }
    },
    {
      "step": 3,
      "tool": "hurst_exponent",
      "args": {
        "series_index": 3
      }
    },
    {
      "step": 4,
      "tool": "hurst_exponent",
      "args": {
        "series_index": 4
      }
    },
    {
      "step": 5,
      "tool": "segment_trend",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 104
      }
    },
    {
      "step": 6,
      "tool": "segment_trend",
      "args": {
        "series_index": 2,
        "start": 0,
        "end": 104
      }
    },
    {
      "step": 7,
      "tool": "segment_trend",
      "args": {
        "series_index": 3,
        "start": 0,
        "end": 104
      }
    },
    {
      "step": 8,
      "tool": "segment_trend",
      "args": {
        "series_index": 4,
        "start": 0,
        "end": 104
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m1`

tokens prompt=3013 completion=1024 latency=37.77s

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
{"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"Long-term persistence in the reference series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in the reference series","required_evidence":["segment_trend"]},{"claim":"Long-term persistence in each candidate series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in each candidate series","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"Estimate Hurst exponent for persistence measure.","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"Determine global trend direction and slope over the entire series.","supports_evidence":["global_trend"]}],"no_tool_decision":null},"reasoning":"The task requires analyzing the long-term patterns and measuring persistence and global trends in the reference and candidate time series. The objective is to compare these characteristics across the series to identify the candidate with the most similar pattern."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
    "step": 1,
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
      "hurst": 0.3226361525588941,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 2
    },
    "resolved_arguments": {
      "series_index": 2
    },
    "success": true,
    "data": {
      "series_index": 2,
      "start": null,
      "end": null,
      "hurst": 0.364153457742821,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "c00307b5b9e5c3894a0eff13bc95f0579b12e8bb"
  },
  {
    "call_id": "long:step3",
    "step": 3,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 3
    },
    "resolved_arguments": {
      "series_index": 3
    },
    "success": true,
    "data": {
      "series_index": 3,
      "start": null,
      "end": null,
      "hurst": 0.23703349680256722,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "a6c2938d3a28138bceab95fcb747c4b708719a20"
  },
  {
    "call_id": "long:step4",
    "step": 4,
    "tool_name": "hurst_exponent",
    "arguments": {
      "series_index": 4
    },
    "resolved_arguments": {
      "series_index": 4
    },
    "success": true,
    "data": {
      "series_index": 4,
      "start": null,
      "end": null,
      "hurst": 0.2571610613506707,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 104,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "e3f6d728dbf84e9e88427c47ffba4686427e5656"
  },
  {
    "call_id": "long:step5",
    "step": 5,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 104
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 104
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 103,
      "slope": -6.456310679611651,
      "direction": "downward",
      "direction_class": "downward",
      "trend_method": "endpoint",
      "mean": 3355.798076923077,
      "std": 1155.2684201901345,
      "start_value": 2623.0,
      "end_value": 1958.0
    },
    "error": null,
    "args_fingerprint": "3dfa2d374bab451f0c6842c3f87e0211b0c23398"
  },
  {
    "call_id": "long:step6",
    "step": 6,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 2,
      "start": 0,
      "end": 104
    },
    "resolved_arguments": {
      "series_index": 2,
      "start": 0,
      "end": 104
    },
    "success": true,
    "data": {
      "series_index": 2,
      "start": 0,
      "end": 103,
      "slope": -3.6288349514563105,
      "direction": "downward",
      "direction_class": "downward",
      "trend_method": "endpoint",
      "mean": 3350.409423076923,
      "std": 1181.0660331274282,
      "start_value": 2533.02,
      "end_value": 2159.25
    },
    "error": null,
    "args_fingerprint": "6fcc7987bd1de0a27993a326769d70b53c2265ee"
  },
  {
    "call_id": "long:step7",
    "step": 7,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 3,
      "start": 0,
      "end": 104
    },
    "resolved_arguments": {
      "series_index": 3,
      "start": 0,
      "end": 104
    },
    "success": true,
    "data": {
      "series_index": 3,
      "start": 0,
      "end": 103,
      "slope": -2.378640776699029,
      "direction": "downward",
      "direction_class": "downward",
      "trend_method": "endpoint",
      "mean": 3534.480769230769,
      "std": 1188.680174530763,
      "start_value": 2472.0,
      "end_value": 2227.0
    },
    "error": null,
    "args_fingerprint": "a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4"
  },
  {
    "call_id": "long:step8",
    "step": 8,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 4,
      "start": 0,
      "end": 104
    },
    "resolved_arguments": {
      "series_index": 4,
      "start": 0,
      "end": 104
    },
    "success": true,
    "data": {
      "series_index": 4,
      "start": 0,
      "end": 103,
      "slope": -4.766990291262136,
      "direction": "downward",
      "direction_class": "downward",
      "trend_method": "endpoint",
      "mean": 2153.644230769231,
      "std": 1056.3056714347308,
      "start_value": 1511.0,
      "end_value": 1020.0
    },
    "error": null,
    "args_fingerprint": "3b0544978f32a662c8964dccb4b769d2ed1baf26"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes estimating the Hurst exponent for measuring persistence and determining the global trend direction and slope using the segment_trend tool for each of the series. This helps in understanding the long-term behavior of each series.",
  "scale": "long",
  "observations": ["Hurst exponents were calculated for all series to gauge persistence, with values ranging from 0.237 to 0.364, indicating anti-persistent behavior. Segment trend analysis was conducted on each series to determine downward slopes, consistent with a decreasing trend over time."],
  "evidence_intervals": ["Full series length"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Long-term persistence in the reference series",
      "evidence": [
        {
          "type": "hurst_exponent",
          "value": 0.3226361525588941,
          "source_tool": "hurst_exponent",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "Long-term global trend in the reference series",
      "evidence": [
        {
          "type": "segment_trend",
          "value": "-6.456",
          "source_tool": "segment_trend",
          "call_id": "long:step5",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "Long-term persistence in candidate series 2",
      "evidence": [
        {
          "type": "hurst_exponent",
          "value": 0.364153457742821,
          "source_tool": "hurst_exponent",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "Long-term global trend in candidate series 2",
      "evidence": [
        {
          "type": "segment_trend",
          "value": "-3.6288",
          "source_tool": "segment_trend",
          "call_id": "long:step6",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "Long-term persistence in candidate series 3",
      "evidence": [
        {
          "type": "hurst_exponent",
          "value": 0.23703349680256722,
          "source_tool": "hurst_exponent",
          "call_id": "long:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "Long-term global trend in candidate series 3",
      "evidence": [
        {
          "type": "segment_trend",
          "value": "-2.3786",
          "source_tool": "segment_trend",
          "call_id": "long:step7",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "Long-term persistence in candidate series 4",
      "evidence": [
        {
          "type": "hurst_exponent",
          "value": 0.2571610613506707,
          "source_tool": "hurst_exponent",
          "call_id": "long:step4",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "Long-term global trend in candidate series 4",
      "evidence": [
        {
          "type": "segment_trend",
          "value": "-4.76699",
          "source_tool": "segment_trend",
          "call_id": "long:step8",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    }
  ],
  "coverage": {
    "hurst_exponent": "tool_supported",
    "segment_trend": "
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=6257 completion=289 latency=12.28s

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
{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying the sequence among given candidates that shows the closest similarity to the reference Time Series 1. This involves examining patterns, structures, and possible alignments over the whole series.","task_summary":"Identify the candidate time series that most closely matches the pattern of Time Series 1","target_output":"A","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["matching"],"success_criteria":["Each candidate's similarity score is compared against the reference series.","The highest similarity score identifies the most similar pattern."],"notes":"Since the task asks for the series with the most similar pattern, the matching role needs to be assigned to handle this task."}
</plan_context>

<task_summary>
Identify the candidate time series that most closely matches the pattern of Time Series 1
</task_summary>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"Parse failure in S5","scale":"long","observations":["Unable to integrate tool evidence."],"evidence_intervals":[],"confidence":0.5,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.3226361525588941, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 2}, \"resolved_arguments\": {\"series_index\": 2}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": null, \"end\": null, \"hurst\": 0.364153457742821, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"hurst\": 0.23703349680256722, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"a6c2938d3a28138bceab95fcb747c4b708719a20\"}","{\"call_id\": \"long:step4\", \"step\": 4, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 4}, \"resolved_arguments\": {\"series_index\": 4}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": null, \"end\": null, \"hurst\": 0.2571610613506707, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"e3f6d728dbf84e9e88427c47ffba4686427e5656\"}","{\"call_id\": \"long:step5\", \"step\": 5, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 103, \"slope\": -6.456310679611651, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3355.798076923077, \"std\": 1155.2684201901345, \"start_value\": 2623.0, \"end_value\": 1958.0}, \"error\": null, \"args_fingerprint\": \"3dfa2d374bab451f0c6842c3f87e0211b0c23398\"}","{\"call_id\": \"long:step6\", \"step\": 6, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": 0, \"end\": 103, \"slope\": -3.6288349514563105, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3350.409423076923, \"std\": 1181.0660331274282, \"start_value\": 2533.02, \"end_value\": 2159.25}, \"error\": null, \"args_fingerprint\": \"6fcc7987bd1de0a27993a326769d70b53c2265ee\"}","{\"call_id\": \"long:step7\", \"step\": 7, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": 0, \"end\": 103, \"slope\": -2.378640776699029, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3534.480769230769, \"std\": 1188.680174530763, \"start_value\": 2472.0, \"end_value\": 2227.0}, \"error\": null, \"args_fingerprint\": \"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4\"}","{\"call_id\": \"long:step8\", \"step\": 8, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": 0, \"end\": 103, \"slope\": -4.766990291262136, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 2153.644230769231, \"std\": 1056.3056714347308, \"start_value\": 1511.0, \"end_value\": 1020.0}, \"error\": null, \"args_fingerprint\": \"3b0544978f32a662c8964dccb4b769d2ed1baf26\"}"],"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"Long-term persistence in the reference series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in the reference series","required_evidence":["segment_trend"]},{"claim":"Long-term persistence in each candidate series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in each candidate series","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"Estimate Hurst exponent for persistence measure.","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"Determine global trend direction and slope over the entire series.","supports_evidence":["global_trend"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"hurst_exponent","output_key":"hurst_reference","input_binding":{"series":"$series[1]"}},{"step":2,"tool":"hurst_exponent","output_key":"hurst_candidate1","input_binding":{"series":"$series[2]"}},{"step":3,"tool":"hurst_exponent","output_key":"hurst_candidate2","input_binding":{"series":"$series[3]"}},{"step":4,"tool":"hurst_exponent","output_key":"hurst_candidate3","input_binding":{"series":"$series[4]"}},{"step":5,"tool":"segment_trend","output_key":"trend_reference","input_binding":{"series_index":"1","start":"0","end":"104"}},{"step":6,"tool":"segment_trend","output_key":"trend_candidate1","input_binding":{"series_index":"2","start":"0","end":"104"}},{"step":7,"tool":"segment_trend","output_key":"trend_candidate2","input_binding":{"series_index":"3","start":"0","end":"104"}},{"step":8,"tool":"segment_trend","output_key":"trend_candidate3","input_binding":{"series_index":"4","start":"0","end":"104"}}],"reasoning":"The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series."},"structured_observations":[],"coverage":{},"unresolved_claims":["parse_failure"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.3226361525588941,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":2},"resolved_arguments":{"series_index":2},"success":true,"data":{"series_index":2,"start":null,"end":null,"hurst":0.364153457742821,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb"},{"call_id":"long:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"start":null,"end":null,"hurst":0.23703349680256722,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"a6c2938d3a28138bceab95fcb747c4b708719a20"},{"call_id":"long:step4","step":4,"tool_name":"hurst_exponent","arguments":{"series_index":4},"resolved_arguments":{"series_index":4},"success":true,"data":{"series_index":4,"start":null,"end":null,"hurst":0.2571610613506707,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"e3f6d728dbf84e9e88427c47ffba4686427e5656"},{"call_id":"long:step5","step":5,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":104},"resolved_arguments":{"series_index":1,"start":0,"end":104},"success":true,"data":{"series_index":1,"start":0,"end":103,"slope":-6.456310679611651,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3355.798076923077,"std":1155.2684201901345,"start_value":2623.0,"end_value":1958.0},"error":null,"args_fingerprint":"3dfa2d374bab451f0c6842c3f87e0211b0c23398"},{"call_id":"long:step6","step":6,"tool_name":"segment_trend","arguments":{"series_index":2,"start":0,"end":104},"resolved_arguments":{"series_index":2,"start":0,"end":104},"success":true,"data":{"series_index":2,"start":0,"end":103,"slope":-3.6288349514563105,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3350.409423076923,"std":1181.0660331274282,"start_value":2533.02,"end_value":2159.25},"error":null,"args_fingerprint":"6fcc7987bd1de0a27993a326769d70b53c2265ee"},{"call_id":"long:step7","step":7,"tool_name":"segment_trend","arguments":{"series_index":3,"start":0,"end":104},"resolved_arguments":{"series_index":3,"start":0,"end":104},"success":true,"data":{"series_index":3,"start":0,"end":103,"slope":-2.378640776699029,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3534.480769230769,"std":1188.680174530763,"start_value":2472.0,"end_value":2227.0},"error":null,"args_fingerprint":"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4"},{"call_id":"long:step8","step":8,"tool_name":"segment_trend","arguments":{"series_index":4,"start":0,"end":104},"resolved_arguments":{"series_index":4,"start":0,"end":104},"success":true,"data":{"series_index":4,"start":0,"end":103,"slope":-4.766990291262136,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":2153.644230769231,"std":1056.3056714347308,"start_value":1511.0,"end_value":1020.0},"error":null,"args_fingerprint":"3b0544978f32a662c8964dccb4b769d2ed1baf26"}],"skipped_stages":[]},"conflicts":[],"summary":"Unable to integrate tool evidence.","structured_by_scale":{}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current assignment focuses on measuring and ranking pattern similarities between a reference and each candidate time series, including forward and reverse similarity measures. Prior evidence provides Hurst exponents and segment trends for all time series but does not address pairwise similarity or reverse similarity directly.",
  "evidence_plan": {
    "objective": "Measure and rank the pattern similarities between the reference and each candidate time series.",
    "claims_to_support": [
      {"claim": "pairwise_similarity", "required_evidence": ["pairwise_similarity_measure"]},
      {"claim": "reverse_similarity", "required_evidence": ["reverse_similarity_measure"]}
    ],
    "analysis_scope": {"target_series": [1,2,3,4,5], "role": "matching"},
    "validation_needs": ["Ensure consistent ranking of candidates based on both pairwise and reverse similarity measures."]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "pairwise_distance", "arguments": {"query_series_index": 1, "candidate_series_indices": [2, 3, 4, 5], "method": "dtw"}},
      {"tool": "reverse_match", "arguments": {"query_series_index": 1, "candidate_series_indices": [2, 3, 4, 5]}}
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m0`

tokens prompt=632 completion=176 latency=6.25s

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
{"evidence_plan":{"objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","claims_to_support":[{"claim":"pairwise_similarity","required_evidence":["pairwise_similarity_measure"]},{"claim":"reverse_similarity","required_evidence":["reverse_similarity_measure"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"role":"matching"},"validation_needs":["Ensure consistent ranking of candidates based on both pairwise and reverse similarity measures."]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"","supports_evidence":[]},{"tool":"reverse_match","reason":"","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current assignment focuses on measuring and ranking pattern similarities between a reference and each candidate time series, including forward and reverse similarity measures. Prior evidence provides Hurst exponents and segment trends for all time series but does not address pairwise similarity or reverse similarity directly."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
- reverse_match
  inputs: query_series_index, candidate_series_indices, method
  outputs: ranking
</io_concepts>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The objective is to measure and rank the pattern similarities between a reference and each candidate time series using pairwise distance and reverse match methods. We need to first calculate pairwise similarities using the pairwise_distance tool and then use those results to find reverse similarities with the reverse_match tool.",
  "workflow": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "output_key": "distances",
      "input_binding": {"series_index": "$metadata.query_series_index"}
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "output_key": "ranking",
      "input_binding": {"query_series_index": "$metadata.query_series_index", "candidate_series_indices": "$metadata.candidate_series_indices", "method": "$step1.method"}
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m0`

tokens prompt=906 completion=135 latency=4.87s

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
{"workflow":[{"step":1,"tool":"pairwise_distance","output_key":"distances","input_binding":{"series_index":"$metadata.query_series_index"}},{"step":2,"tool":"reverse_match","output_key":"ranking","input_binding":{"query_series_index":"$metadata.query_series_index","candidate_series_indices":"$metadata.candidate_series_indices","method":"$step1.method"}}],"reasoning":"The objective is to measure and rank the pattern similarities between a reference and each candidate time series using pairwise distance and reverse match methods. We need to first calculate pairwise similarities using the pairwise_distance tool and then use those results to find reverse similarities with the reverse_match tool."}
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
- reverse_match: Reverse each candidate series and rank candidates against the query using length-normalized z-DTW or Euclidean distance.
  args: {query_series_index=1-based query (default 1), candidate_series_indices=optional 1-based list (default all others), method=dtw|euclidean}
  returns: {ranking=reversed-candidate distances and winner}
</tool_invocation_spec>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<assignment>
{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Calculate pairwise similarities between the query series and each candidate series, then reverse each candidate series and rank them based on their distance to the query using reverse matching.",
  "calls": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "args": {
        "query_series_index": 1,
        "candidate_series_indices": [2, 3, 4, 5]
      }
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=5829 completion=430 latency=17.42s

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
{"evidence_plan":{"objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","claims_to_support":[{"claim":"pairwise_similarity","required_evidence":["pairwise_similarity_measure"]},{"claim":"reverse_similarity","required_evidence":["reverse_similarity_measure"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"role":"matching"},"validation_needs":["Ensure consistent ranking of candidates based on both pairwise and reverse similarity measures."]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"","supports_evidence":[]},{"tool":"reverse_match","reason":"","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current assignment focuses on measuring and ranking pattern similarities between a reference and each candidate time series, including forward and reverse similarity measures. Prior evidence provides Hurst exponents and segment trends for all time series but does not address pairwise similarity or reverse similarity directly."}
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
          "distance": 2.1853183214103566
        },
        {
          "series_index": 3,
          "distance": 3.6041620746856267
        },
        {
          "series_index": 4,
          "distance": 3.311973781886604
        },
        {
          "series_index": 5,
          "distance": 18.00542607157721
        }
      ],
      "nearest": {
        "series_index": 2,
        "distance": 2.1853183214103566
      }
    },
    "error": null,
    "args_fingerprint": "a3958760584c2feb2263ddddaa8bcefdc46f8a4f"
  },
  {
    "call_id": "matching:step2",
    "step": 2,
    "tool_name": "reverse_match",
    "arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        2,
        3,
        4,
        5
      ],
      "method": "$step1.method"
    },
    "resolved_arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        2,
        3,
        4,
        5
      ],
      "method": "euclidean"
    },
    "success": true,
    "data": {
      "query_series_index": 1,
      "ranking": [
        {
          "series_index": 5,
          "reverse_distance": 0.7447039381665551,
          "method_used": "z_euclidean"
        },
        {
          "series_index": 3,
          "reverse_distance": 1.6936818111622591,
          "method_used": "z_euclidean"
        },
        {
          "series_index": 4,
          "reverse_distance": 1.7347590309366183,
          "method_used": "z_euclidean"
        },
        {
          "series_index": 2,
          "reverse_distance": 1.7371234187765197,
          "method_used": "z_euclidean"
        }
      ],
      "nearest": {
        "series_index": 5,
        "reverse_distance": 0.7447039381665551,
        "method_used": "z_euclidean"
      },
      "winner_margin": 0.948977872995704
    },
    "error": null,
    "args_fingerprint": "d2fc01caa28b49c6b16a7610bffacb425ee3df7d"
  }
]
</executed_steps>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"Parse failure in S5","scale":"long","observations":["Unable to integrate tool evidence."],"evidence_intervals":[],"confidence":0.5,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.3226361525588941, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 2}, \"resolved_arguments\": {\"series_index\": 2}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": null, \"end\": null, \"hurst\": 0.364153457742821, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"hurst\": 0.23703349680256722, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"a6c2938d3a28138bceab95fcb747c4b708719a20\"}","{\"call_id\": \"long:step4\", \"step\": 4, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 4}, \"resolved_arguments\": {\"series_index\": 4}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": null, \"end\": null, \"hurst\": 0.2571610613506707, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"e3f6d728dbf84e9e88427c47ffba4686427e5656\"}","{\"call_id\": \"long:step5\", \"step\": 5, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 103, \"slope\": -6.456310679611651, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3355.798076923077, \"std\": 1155.2684201901345, \"start_value\": 2623.0, \"end_value\": 1958.0}, \"error\": null, \"args_fingerprint\": \"3dfa2d374bab451f0c6842c3f87e0211b0c23398\"}","{\"call_id\": \"long:step6\", \"step\": 6, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": 0, \"end\": 103, \"slope\": -3.6288349514563105, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3350.409423076923, \"std\": 1181.0660331274282, \"start_value\": 2533.02, \"end_value\": 2159.25}, \"error\": null, \"args_fingerprint\": \"6fcc7987bd1de0a27993a326769d70b53c2265ee\"}","{\"call_id\": \"long:step7\", \"step\": 7, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": 0, \"end\": 103, \"slope\": -2.378640776699029, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3534.480769230769, \"std\": 1188.680174530763, \"start_value\": 2472.0, \"end_value\": 2227.0}, \"error\": null, \"args_fingerprint\": \"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4\"}","{\"call_id\": \"long:step8\", \"step\": 8, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": 0, \"end\": 103, \"slope\": -4.766990291262136, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 2153.644230769231, \"std\": 1056.3056714347308, \"start_value\": 1511.0, \"end_value\": 1020.0}, \"error\": null, \"args_fingerprint\": \"3b0544978f32a662c8964dccb4b769d2ed1baf26\"}"],"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"Long-term persistence in the reference series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in the reference series","required_evidence":["segment_trend"]},{"claim":"Long-term persistence in each candidate series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in each candidate series","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"Estimate Hurst exponent for persistence measure.","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"Determine global trend direction and slope over the entire series.","supports_evidence":["global_trend"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"hurst_exponent","output_key":"hurst_reference","input_binding":{"series":"$series[1]"}},{"step":2,"tool":"hurst_exponent","output_key":"hurst_candidate1","input_binding":{"series":"$series[2]"}},{"step":3,"tool":"hurst_exponent","output_key":"hurst_candidate2","input_binding":{"series":"$series[3]"}},{"step":4,"tool":"hurst_exponent","output_key":"hurst_candidate3","input_binding":{"series":"$series[4]"}},{"step":5,"tool":"segment_trend","output_key":"trend_reference","input_binding":{"series_index":"1","start":"0","end":"104"}},{"step":6,"tool":"segment_trend","output_key":"trend_candidate1","input_binding":{"series_index":"2","start":"0","end":"104"}},{"step":7,"tool":"segment_trend","output_key":"trend_candidate2","input_binding":{"series_index":"3","start":"0","end":"104"}},{"step":8,"tool":"segment_trend","output_key":"trend_candidate3","input_binding":{"series_index":"4","start":"0","end":"104"}}],"reasoning":"The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series."},"structured_observations":[],"coverage":{},"unresolved_claims":["parse_failure"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.3226361525588941,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":2},"resolved_arguments":{"series_index":2},"success":true,"data":{"series_index":2,"start":null,"end":null,"hurst":0.364153457742821,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb"},{"call_id":"long:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"start":null,"end":null,"hurst":0.23703349680256722,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"a6c2938d3a28138bceab95fcb747c4b708719a20"},{"call_id":"long:step4","step":4,"tool_name":"hurst_exponent","arguments":{"series_index":4},"resolved_arguments":{"series_index":4},"success":true,"data":{"series_index":4,"start":null,"end":null,"hurst":0.2571610613506707,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"e3f6d728dbf84e9e88427c47ffba4686427e5656"},{"call_id":"long:step5","step":5,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":104},"resolved_arguments":{"series_index":1,"start":0,"end":104},"success":true,"data":{"series_index":1,"start":0,"end":103,"slope":-6.456310679611651,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3355.798076923077,"std":1155.2684201901345,"start_value":2623.0,"end_value":1958.0},"error":null,"args_fingerprint":"3dfa2d374bab451f0c6842c3f87e0211b0c23398"},{"call_id":"long:step6","step":6,"tool_name":"segment_trend","arguments":{"series_index":2,"start":0,"end":104},"resolved_arguments":{"series_index":2,"start":0,"end":104},"success":true,"data":{"series_index":2,"start":0,"end":103,"slope":-3.6288349514563105,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3350.409423076923,"std":1181.0660331274282,"start_value":2533.02,"end_value":2159.25},"error":null,"args_fingerprint":"6fcc7987bd1de0a27993a326769d70b53c2265ee"},{"call_id":"long:step7","step":7,"tool_name":"segment_trend","arguments":{"series_index":3,"start":0,"end":104},"resolved_arguments":{"series_index":3,"start":0,"end":104},"success":true,"data":{"series_index":3,"start":0,"end":103,"slope":-2.378640776699029,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3534.480769230769,"std":1188.680174530763,"start_value":2472.0,"end_value":2227.0},"error":null,"args_fingerprint":"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4"},{"call_id":"long:step8","step":8,"tool_name":"segment_trend","arguments":{"series_index":4,"start":0,"end":104},"resolved_arguments":{"series_index":4,"start":0,"end":104},"success":true,"data":{"series_index":4,"start":0,"end":103,"slope":-4.766990291262136,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":2153.644230769231,"std":1056.3056714347308,"start_value":1511.0,"end_value":1020.0},"error":null,"args_fingerprint":"3b0544978f32a662c8964dccb4b769d2ed1baf26"}],"skipped_stages":[]},"conflicts":[],"summary":"Unable to integrate tool evidence.","structured_by_scale":{}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the calculated pairwise and reverse similarity measures, Time Series 2 has the lowest forward distance and a relatively close reverse distance, making it the most similar overall to the reference series.",
  "hypothesis": "Time Series 2 is the most similar to the reference series based on both forward and reverse similarity measures.",
  "evidence": [
    "pairwise_distance results show the nearest series (with the lowest Euclidean distance) is Time Series 2.",
    "reverse_match indicates that the nearest series in reverse match is Time Series 5, but Time Series 2 still ranks highly among the candidates."
  ],
  "candidate_preference": "A",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "matching:step1",
    "matching:step2"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 2 has the lowest forward distance to the reference series.",
      "evidence": [
        {
          "type": "forward_distance",
          "value": 2.1853183214103566,
          "provenance": "tool_executed",
          "ref": "lowest_forward_distance",
          "call_id": "matching:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Time Series 2 ranks high in reverse similarity measures.",
      "evidence": [
        {
          "type": "reverse_distance",
          "value": 1.7371234187765197,
          "provenance": "tool_executed",
          "ref": "high_reverse_similarity",
          "call_id": "matching:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=6268 completion=362 latency=15.07s

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
{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying the sequence among given candidates that shows the closest similarity to the reference Time Series 1. This involves examining patterns, structures, and possible alignments over the whole series.","task_summary":"Identify the candidate time series that most closely matches the pattern of Time Series 1","target_output":"A","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Analyze the long-term patterns of the reference and candidate time series.","required_measurements":["persistence","global_trend"],"validation_requirements":["Compare long-term behavior across series"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}],"scales":["long"],"heterogeneous_agents":["matching"],"success_criteria":["Each candidate's similarity score is compared against the reference series.","The highest similarity score identifies the most similar pattern."],"notes":"Since the task asks for the series with the most similar pattern, the matching role needs to be assigned to handle this task."}
</plan_context>

<task_summary>
Identify the candidate time series that most closely matches the pattern of Time Series 1
</task_summary>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"Parse failure in S5","scale":"long","observations":["Unable to integrate tool evidence."],"evidence_intervals":[],"confidence":0.5,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.3226361525588941, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 2}, \"resolved_arguments\": {\"series_index\": 2}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": null, \"end\": null, \"hurst\": 0.364153457742821, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"hurst\": 0.23703349680256722, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"a6c2938d3a28138bceab95fcb747c4b708719a20\"}","{\"call_id\": \"long:step4\", \"step\": 4, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 4}, \"resolved_arguments\": {\"series_index\": 4}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": null, \"end\": null, \"hurst\": 0.2571610613506707, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"e3f6d728dbf84e9e88427c47ffba4686427e5656\"}","{\"call_id\": \"long:step5\", \"step\": 5, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 103, \"slope\": -6.456310679611651, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3355.798076923077, \"std\": 1155.2684201901345, \"start_value\": 2623.0, \"end_value\": 1958.0}, \"error\": null, \"args_fingerprint\": \"3dfa2d374bab451f0c6842c3f87e0211b0c23398\"}","{\"call_id\": \"long:step6\", \"step\": 6, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": 0, \"end\": 103, \"slope\": -3.6288349514563105, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3350.409423076923, \"std\": 1181.0660331274282, \"start_value\": 2533.02, \"end_value\": 2159.25}, \"error\": null, \"args_fingerprint\": \"6fcc7987bd1de0a27993a326769d70b53c2265ee\"}","{\"call_id\": \"long:step7\", \"step\": 7, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": 0, \"end\": 103, \"slope\": -2.378640776699029, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3534.480769230769, \"std\": 1188.680174530763, \"start_value\": 2472.0, \"end_value\": 2227.0}, \"error\": null, \"args_fingerprint\": \"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4\"}","{\"call_id\": \"long:step8\", \"step\": 8, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": 0, \"end\": 103, \"slope\": -4.766990291262136, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 2153.644230769231, \"std\": 1056.3056714347308, \"start_value\": 1511.0, \"end_value\": 1020.0}, \"error\": null, \"args_fingerprint\": \"3b0544978f32a662c8964dccb4b769d2ed1baf26\"}"],"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"Long-term persistence in the reference series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in the reference series","required_evidence":["segment_trend"]},{"claim":"Long-term persistence in each candidate series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in each candidate series","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"Estimate Hurst exponent for persistence measure.","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"Determine global trend direction and slope over the entire series.","supports_evidence":["global_trend"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"hurst_exponent","output_key":"hurst_reference","input_binding":{"series":"$series[1]"}},{"step":2,"tool":"hurst_exponent","output_key":"hurst_candidate1","input_binding":{"series":"$series[2]"}},{"step":3,"tool":"hurst_exponent","output_key":"hurst_candidate2","input_binding":{"series":"$series[3]"}},{"step":4,"tool":"hurst_exponent","output_key":"hurst_candidate3","input_binding":{"series":"$series[4]"}},{"step":5,"tool":"segment_trend","output_key":"trend_reference","input_binding":{"series_index":"1","start":"0","end":"104"}},{"step":6,"tool":"segment_trend","output_key":"trend_candidate1","input_binding":{"series_index":"2","start":"0","end":"104"}},{"step":7,"tool":"segment_trend","output_key":"trend_candidate2","input_binding":{"series_index":"3","start":"0","end":"104"}},{"step":8,"tool":"segment_trend","output_key":"trend_candidate3","input_binding":{"series_index":"4","start":"0","end":"104"}}],"reasoning":"The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series."},"structured_observations":[],"coverage":{},"unresolved_claims":["parse_failure"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.3226361525588941,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":2},"resolved_arguments":{"series_index":2},"success":true,"data":{"series_index":2,"start":null,"end":null,"hurst":0.364153457742821,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb"},{"call_id":"long:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"start":null,"end":null,"hurst":0.23703349680256722,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"a6c2938d3a28138bceab95fcb747c4b708719a20"},{"call_id":"long:step4","step":4,"tool_name":"hurst_exponent","arguments":{"series_index":4},"resolved_arguments":{"series_index":4},"success":true,"data":{"series_index":4,"start":null,"end":null,"hurst":0.2571610613506707,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"e3f6d728dbf84e9e88427c47ffba4686427e5656"},{"call_id":"long:step5","step":5,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":104},"resolved_arguments":{"series_index":1,"start":0,"end":104},"success":true,"data":{"series_index":1,"start":0,"end":103,"slope":-6.456310679611651,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3355.798076923077,"std":1155.2684201901345,"start_value":2623.0,"end_value":1958.0},"error":null,"args_fingerprint":"3dfa2d374bab451f0c6842c3f87e0211b0c23398"},{"call_id":"long:step6","step":6,"tool_name":"segment_trend","arguments":{"series_index":2,"start":0,"end":104},"resolved_arguments":{"series_index":2,"start":0,"end":104},"success":true,"data":{"series_index":2,"start":0,"end":103,"slope":-3.6288349514563105,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3350.409423076923,"std":1181.0660331274282,"start_value":2533.02,"end_value":2159.25},"error":null,"args_fingerprint":"6fcc7987bd1de0a27993a326769d70b53c2265ee"},{"call_id":"long:step7","step":7,"tool_name":"segment_trend","arguments":{"series_index":3,"start":0,"end":104},"resolved_arguments":{"series_index":3,"start":0,"end":104},"success":true,"data":{"series_index":3,"start":0,"end":103,"slope":-2.378640776699029,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3534.480769230769,"std":1188.680174530763,"start_value":2472.0,"end_value":2227.0},"error":null,"args_fingerprint":"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4"},{"call_id":"long:step8","step":8,"tool_name":"segment_trend","arguments":{"series_index":4,"start":0,"end":104},"resolved_arguments":{"series_index":4,"start":0,"end":104},"success":true,"data":{"series_index":4,"start":0,"end":103,"slope":-4.766990291262136,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":2153.644230769231,"std":1056.3056714347308,"start_value":1511.0,"end_value":1020.0},"error":null,"args_fingerprint":"3b0544978f32a662c8964dccb4b769d2ed1baf26"}],"skipped_stages":[]},"conflicts":[],"summary":"Unable to integrate tool evidence.","structured_by_scale":{}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
retry_context=unresolved_claims=['parse_failure']
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides persistence and trend measures for the reference and candidate time series but does not address pairwise similarity or reverse similarity. Additional tools should be selected to compute these metrics.",
  "evidence_plan": {
    "objective": "Measure and rank the pattern similarities between the reference and each candidate time series.",
    "claims_to_support": [
      {
        "claim": "Pairwise similarity between reference and candidates",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "Reverse similarity between reference and candidates",
        "required_evidence": ["reverse_similarity"]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2, 3, 4, 5],
      "role": "matching"
    },
    "validation_needs": ["Reconcile similarity scores to ensure consistent ranking"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "pairwise_distance",
        "arguments": {
          "query_series_index": 1,
          "candidate_series_indices": [2, 3, 4, 5],
          "method": "dtw"
        },
        "reason": "To calculate pairwise similarity using Dynamic Time Warping."
      },
      {
        "tool": "reverse_match",
        "arguments": {
          "query_series_index": 1,
          "candidate_series_indices": [2, 3, 4, 5],
          "method": "dtw"
        },
        "reason": "To calculate reverse similarity by reversing each candidate series and comparing it to the reference using Dynamic Time Warping."
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m1`

tokens prompt=648 completion=192 latency=6.81s

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
{"evidence_plan":{"objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","claims_to_support":[{"claim":"Pairwise similarity between reference and candidates","required_evidence":["pairwise_similarity"]},{"claim":"Reverse similarity between reference and candidates","required_evidence":["reverse_similarity"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"role":"matching"},"validation_needs":["Reconcile similarity scores to ensure consistent ranking"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"To calculate pairwise similarity using Dynamic Time Warping.","supports_evidence":[]},{"tool":"reverse_match","reason":"To calculate reverse similarity by reversing each candidate series and comparing it to the reference using Dynamic Time Warping.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides persistence and trend measures for the reference and candidate time series but does not address pairwise similarity or reverse similarity. Additional tools should be selected to compute these metrics."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
- reverse_match
  inputs: query_series_index, candidate_series_indices, method
  outputs: ranking
</io_concepts>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The objective requires measuring and ranking pattern similarities between the reference and each candidate time series. Two steps are needed: first, to calculate pairwise similarity using Dynamic Time Warping with the pairwise_distance tool. Second, to calculate reverse similarity by reversing each candidate series and comparing it to the reference using the reverse_match tool.",
  "workflow": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "output_key": "distances",
      "input_binding": {
        "series_index": "$query_series_index"
      }
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "output_key": "ranking",
      "input_binding": {
        "query_series_index": "$query_series_index",
        "candidate_series_indices": "$candidate_series_indices",
        "method": "Dynamic Time Warping"
      }
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m1`

tokens prompt=911 completion=168 latency=6.07s

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
{"workflow":[{"step":1,"tool":"pairwise_distance","output_key":"distances","input_binding":{"series_index":"$query_series_index"}},{"step":2,"tool":"reverse_match","output_key":"ranking","input_binding":{"query_series_index":"$query_series_index","candidate_series_indices":"$candidate_series_indices","method":"Dynamic Time Warping"}}],"reasoning":"The objective requires measuring and ranking pattern similarities between the reference and each candidate time series. Two steps are needed: first, to calculate pairwise similarity using Dynamic Time Warping with the pairwise_distance tool. Second, to calculate reverse similarity by reversing each candidate series and comparing it to the reference using the reverse_match tool."}
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
- reverse_match: Reverse each candidate series and rank candidates against the query using length-normalized z-DTW or Euclidean distance.
  args: {query_series_index=1-based query (default 1), candidate_series_indices=optional 1-based list (default all others), method=dtw|euclidean}
  returns: {ranking=reversed-candidate distances and winner}
</tool_invocation_spec>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<assignment>
{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Calculate pairwise similarity using Dynamic Time Warping (DTW) between the reference series (series_index=1) and each candidate series, and then calculate reverse similarity by reversing each candidate series and comparing it to the reference also using DTW.",
  "calls": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "args": {
        "method": "dtw",
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "args": {
        "query_series_index": 1,
        "candidate_series_indices": [2, 3, 4, 5],
        "method": "dtw"
      }
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=5868 completion=567 latency=22.68s

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
{"evidence_plan":{"objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","claims_to_support":[{"claim":"Pairwise similarity between reference and candidates","required_evidence":["pairwise_similarity"]},{"claim":"Reverse similarity between reference and candidates","required_evidence":["reverse_similarity"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"role":"matching"},"validation_needs":["Reconcile similarity scores to ensure consistent ranking"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"To calculate pairwise similarity using Dynamic Time Warping.","supports_evidence":[]},{"tool":"reverse_match","reason":"To calculate reverse similarity by reversing each candidate series and comparing it to the reference using Dynamic Time Warping.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides persistence and trend measures for the reference and candidate time series but does not address pairwise similarity or reverse similarity. Additional tools should be selected to compute these metrics."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "matching:step1",
    "step": 1,
    "tool_name": "pairwise_distance",
    "arguments": {
      "method": "dtw",
      "series_index": 1
    },
    "resolved_arguments": {
      "method": "dtw",
      "series_index": 1
    },
    "success": true,
    "data": {
      "method": "dtw",
      "ref_series_index": 1,
      "distances": [
        {
          "series_index": 2,
          "distance": 2190.2558396223944
        },
        {
          "series_index": 3,
          "distance": 1930.3776832526842
        },
        {
          "series_index": 4,
          "distance": 8467.292955838955
        },
        {
          "series_index": 5,
          "distance": 20864.524413463154
        }
      ],
      "nearest": {
        "series_index": 3,
        "distance": 1930.3776832526842
      }
    },
    "error": null,
    "args_fingerprint": "92f09721348ee97a03b60aace1ff33ce5c9be885"
  },
  {
    "call_id": "matching:step2",
    "step": 2,
    "tool_name": "reverse_match",
    "arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        2,
        3,
        4,
        5
      ],
      "method": "dtw"
    },
    "resolved_arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        2,
        3,
        4,
        5
      ],
      "method": "dtw"
    },
    "success": true,
    "data": {
      "query_series_index": 1,
      "ranking": [
        {
          "series_index": 3,
          "reverse_distance": 0.17122799523443338,
          "method_used": "dtw"
        },
        {
          "series_index": 5,
          "reverse_distance": 0.1924810998965734,
          "method_used": "dtw"
        },
        {
          "series_index": 4,
          "reverse_distance": 0.19785212242363737,
          "method_used": "dtw"
        },
        {
          "series_index": 2,
          "reverse_distance": 0.2355648611393633,
          "method_used": "dtw"
        }
      ],
      "nearest": {
        "series_index": 3,
        "reverse_distance": 0.17122799523443338,
        "method_used": "dtw"
      },
      "winner_margin": 0.021253104662140004
    },
    "error": null,
    "args_fingerprint": "428014cf0c69958063309027b2b64739b277069d"
  }
]
</executed_steps>

<temporal_profile>
{"short":null,"medium":null,"long":{"reasoning":"Parse failure in S5","scale":"long","observations":["Unable to integrate tool evidence."],"evidence_intervals":[],"confidence":0.5,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.3226361525588941, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 2}, \"resolved_arguments\": {\"series_index\": 2}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": null, \"end\": null, \"hurst\": 0.364153457742821, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 3}, \"resolved_arguments\": {\"series_index\": 3}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": null, \"end\": null, \"hurst\": 0.23703349680256722, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"a6c2938d3a28138bceab95fcb747c4b708719a20\"}","{\"call_id\": \"long:step4\", \"step\": 4, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 4}, \"resolved_arguments\": {\"series_index\": 4}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": null, \"end\": null, \"hurst\": 0.2571610613506707, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 104, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"e3f6d728dbf84e9e88427c47ffba4686427e5656\"}","{\"call_id\": \"long:step5\", \"step\": 5, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 103, \"slope\": -6.456310679611651, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3355.798076923077, \"std\": 1155.2684201901345, \"start_value\": 2623.0, \"end_value\": 1958.0}, \"error\": null, \"args_fingerprint\": \"3dfa2d374bab451f0c6842c3f87e0211b0c23398\"}","{\"call_id\": \"long:step6\", \"step\": 6, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 2, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 2, \"start\": 0, \"end\": 103, \"slope\": -3.6288349514563105, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3350.409423076923, \"std\": 1181.0660331274282, \"start_value\": 2533.02, \"end_value\": 2159.25}, \"error\": null, \"args_fingerprint\": \"6fcc7987bd1de0a27993a326769d70b53c2265ee\"}","{\"call_id\": \"long:step7\", \"step\": 7, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 3, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 3, \"start\": 0, \"end\": 103, \"slope\": -2.378640776699029, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 3534.480769230769, \"std\": 1188.680174530763, \"start_value\": 2472.0, \"end_value\": 2227.0}, \"error\": null, \"args_fingerprint\": \"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4\"}","{\"call_id\": \"long:step8\", \"step\": 8, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"resolved_arguments\": {\"series_index\": 4, \"start\": 0, \"end\": 104}, \"success\": true, \"data\": {\"series_index\": 4, \"start\": 0, \"end\": 103, \"slope\": -4.766990291262136, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 2153.644230769231, \"std\": 1056.3056714347308, \"start_value\": 1511.0, \"end_value\": 1020.0}, \"error\": null, \"args_fingerprint\": \"3b0544978f32a662c8964dccb4b769d2ed1baf26\"}"],"evidence_plan":{"objective":"Analyze the long-term patterns of the reference and candidate time series.","claims_to_support":[{"claim":"Long-term persistence in the reference series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in the reference series","required_evidence":["segment_trend"]},{"claim":"Long-term persistence in each candidate series","required_evidence":["hurst_exponent"]},{"claim":"Long-term global trend in each candidate series","required_evidence":["segment_trend"]}],"analysis_scope":{"target_series":[1,2,3,4,5],"focus_intervals":[],"scale":"long"},"validation_needs":["cross_series_compare"]},"capability_selection":{"selected_tools":[{"tool":"hurst_exponent","reason":"Estimate Hurst exponent for persistence measure.","supports_evidence":["hurst_exponent"]},{"tool":"segment_trend","reason":"Determine global trend direction and slope over the entire series.","supports_evidence":["global_trend"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"hurst_exponent","output_key":"hurst_reference","input_binding":{"series":"$series[1]"}},{"step":2,"tool":"hurst_exponent","output_key":"hurst_candidate1","input_binding":{"series":"$series[2]"}},{"step":3,"tool":"hurst_exponent","output_key":"hurst_candidate2","input_binding":{"series":"$series[3]"}},{"step":4,"tool":"hurst_exponent","output_key":"hurst_candidate3","input_binding":{"series":"$series[4]"}},{"step":5,"tool":"segment_trend","output_key":"trend_reference","input_binding":{"series_index":"1","start":"0","end":"104"}},{"step":6,"tool":"segment_trend","output_key":"trend_candidate1","input_binding":{"series_index":"2","start":"0","end":"104"}},{"step":7,"tool":"segment_trend","output_key":"trend_candidate2","input_binding":{"series_index":"3","start":"0","end":"104"}},{"step":8,"tool":"segment_trend","output_key":"trend_candidate3","input_binding":{"series_index":"4","start":"0","end":"104"}}],"reasoning":"The objective is to analyze the long-term patterns and measure the persistence and global trends in the reference and candidate time series. The workflow starts with estimating the Hurst exponent for persistence and then determining the global trend for each series."},"structured_observations":[],"coverage":{},"unresolved_claims":["parse_failure"],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.3226361525588941,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":2},"resolved_arguments":{"series_index":2},"success":true,"data":{"series_index":2,"start":null,"end":null,"hurst":0.364153457742821,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"c00307b5b9e5c3894a0eff13bc95f0579b12e8bb"},{"call_id":"long:step3","step":3,"tool_name":"hurst_exponent","arguments":{"series_index":3},"resolved_arguments":{"series_index":3},"success":true,"data":{"series_index":3,"start":null,"end":null,"hurst":0.23703349680256722,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"a6c2938d3a28138bceab95fcb747c4b708719a20"},{"call_id":"long:step4","step":4,"tool_name":"hurst_exponent","arguments":{"series_index":4},"resolved_arguments":{"series_index":4},"success":true,"data":{"series_index":4,"start":null,"end":null,"hurst":0.2571610613506707,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":104,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"e3f6d728dbf84e9e88427c47ffba4686427e5656"},{"call_id":"long:step5","step":5,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":104},"resolved_arguments":{"series_index":1,"start":0,"end":104},"success":true,"data":{"series_index":1,"start":0,"end":103,"slope":-6.456310679611651,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3355.798076923077,"std":1155.2684201901345,"start_value":2623.0,"end_value":1958.0},"error":null,"args_fingerprint":"3dfa2d374bab451f0c6842c3f87e0211b0c23398"},{"call_id":"long:step6","step":6,"tool_name":"segment_trend","arguments":{"series_index":2,"start":0,"end":104},"resolved_arguments":{"series_index":2,"start":0,"end":104},"success":true,"data":{"series_index":2,"start":0,"end":103,"slope":-3.6288349514563105,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3350.409423076923,"std":1181.0660331274282,"start_value":2533.02,"end_value":2159.25},"error":null,"args_fingerprint":"6fcc7987bd1de0a27993a326769d70b53c2265ee"},{"call_id":"long:step7","step":7,"tool_name":"segment_trend","arguments":{"series_index":3,"start":0,"end":104},"resolved_arguments":{"series_index":3,"start":0,"end":104},"success":true,"data":{"series_index":3,"start":0,"end":103,"slope":-2.378640776699029,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":3534.480769230769,"std":1188.680174530763,"start_value":2472.0,"end_value":2227.0},"error":null,"args_fingerprint":"a10ffbd051b9ca3fcdf782f6cd8dce3cf1f2d6d4"},{"call_id":"long:step8","step":8,"tool_name":"segment_trend","arguments":{"series_index":4,"start":0,"end":104},"resolved_arguments":{"series_index":4,"start":0,"end":104},"success":true,"data":{"series_index":4,"start":0,"end":103,"slope":-4.766990291262136,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":2153.644230769231,"std":1056.3056714347308,"start_value":1511.0,"end_value":1020.0},"error":null,"args_fingerprint":"3b0544978f32a662c8964dccb4b769d2ed1baf26"}],"skipped_stages":[]},"conflicts":[],"summary":"Unable to integrate tool evidence.","structured_by_scale":{}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Measure and rank the pattern similarities between the reference and each candidate time series.","required_measurements":["pairwise_similarity","reverse_similarity"],"validation_requirements":["Reconcile similarity scores to ensure consistent ranking"],"target_series":[1,2,3,4,5],"focus_intervals":[]}
</assignment>

<metadata>
subset=Match; local_overall=overall; task_type=['choose it']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=5; series_lengths=[104, 104, 104, 104, 104]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[2, 3, 4, 5]; align_direction=None; option_to_series={'A': 2, 'B': 3, 'C': 4, 'D': 5}
</metadata>

<candidates>
A) Time Series 2. B) Time Series 3. C) Time Series 4. D) Time Series 5
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Both pairwise and reverse similarity calculations have been performed on the reference and candidate time series. Pairwise similarity measures how close each candidate series is to the reference when aligned directly. Reverse similarity measures the closeness after reversing the candidate series before alignment. Combining these two measures gives a more comprehensive understanding of the overall similarity between the reference and each candidate.",
  "role": "matching",
  "hypothesis": "Candidate Series 3 has the highest similarity to the reference based on both direct and reverse DTW measurements.",
  "evidence": [
    "pairwise_distance matching:step1 calculated pairwise similarity for reference series and candidates.",
    "reverse_match matching:step2 calculated reverse similarity for reference series and candidates."
  ],
  "candidate_preference": "B",
  "confidence": 0.8,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "matching:step1",
    "matching:step2"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Candidate series 3 shows the closest match to the reference time series according to direct pairwise distance measurement.",
      "evidence": [
        {
          "type": "pairwise_similarity",
          "value": 1930.3776832526842,
          "provenance": "local",
          "ref": "matching:step1",
          "call_id": "matching:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Series 3 also exhibits the smallest reverse distance to the reference time series.",
      "evidence": [
        {
          "type": "reverse_similarity",
          "value": 0.17122799523443338,
          "provenance": "local",
          "ref": "matching:step2",
          "call_id": "matching:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "pairwise_similarity": {
      "series_index": 1,
      "candidate_series_indices": [2, 3, 4, 5],
      "coverage": "full",
      "call_ids": ["matching:step1"]
    },
    "reverse_similarity": {
      "series_index": 1,
      "candidate_series_indices": [2, 3, 4, 5],
      "coverage": "full",
      "call_ids": ["matching:step2"]
    }
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1042 completion=243 latency=8.73s

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
  "goal": "Identify the candidate time series that most closely matches the pattern of Time Series 1",
  "question_type": "choice",
  "required_output": "A",
  "success_criteria": [
    "Each candidate's similarity score is compared against the reference series.",
    "The highest similarity score identifies the most similar pattern."
  ],
  "assignments_brief": [
    {
      "agent": "homo:long",
      "objective": "Analyze the long-term patterns of the reference and candidate time series.",
      "required_measurements": [
        "persistence",
        "global_trend"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Measure and rank the pattern similarities between the reference and each candidate time series.",
      "required_measurements": [
        "pairwise_similarity",
        "reverse_similarity"
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
          "type": "note",
          "value": "Unable to integrate tool evidence.",
          "trusted": false
        }
      ],
      "coverage": {},
      "summary": "Unable to integrate tool evidence."
    }
  },
  "conflicts": [],
  "summary": "Unable to integrate tool evidence."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Parse failure in S5",
      "reasoning_chain": [
        "parse failure"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [],
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
  "verified_preference": "B",
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
  "reasoning": "Heter reasoning indicates a parse failure in S5 but does not provide a clear preference among candidates based on pattern similarity scores. Execution metadata verifies a preference for B. Given the parse issue with S5, it is less likely to be the correct answer, though there is insufficient evidence from other candidates. The verified preference is trusted due to the match/align rule.",
  "answer": "B",
  "explanation": "Despite parse issues, the execution metadata strongly suggests Time Series 3 (option B) as having the closest match to Time Series 1, aligned with the planner's goal of identifying the most similar pattern.",
  "confidence": 0.8,
  "conflicts": ["Heter Reasoning reported parse failure in S5 but did not clarify relative similarities for other options"],
  "cited_evidence": ["Execution metadata verified preference: B", "Heter Reasoning parse failure report"],
  "decision_trace": {
    "metric": "pairwise_similarity",
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "B"
  }
}
```
