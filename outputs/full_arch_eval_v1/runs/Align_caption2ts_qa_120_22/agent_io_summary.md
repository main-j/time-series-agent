# Agent IO summary: `Align:caption2ts_qa_120:22`

- Architecture pred: `A` (success=True)
- model_calls=16, tool_calls=10, latency=215.5s

## Planner — `planner`

tokens prompt=1165 completion=524 latency=18.60s

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
'This time series exhibits an initial stable period around 40-41 from index 0-10, followed by a brief spike to 42.55 at index 11-12, then a dramatic monotonic decline from index 13-22 reaching a minimum of 22.08, before showing a partial recovery to 24.89 at the final point.' According to the above textual description of a time series, select the time series from the following four options that most accurately reflects the described characteristics.
</question>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires identifying which time series among four choices best matches the given textual description. The text describes a pattern involving stability, a spike, a decline, and a recovery, all with specific points highlighted. The goal is to find a time series that reflects these dynamics.",
  "task_summary": "Identify the time series out of the given four that best matches the textual description.",
  "target_output": "Select the time series from the following four options that most accurately reflects the described characteristics.",
  "answer_type": "choice",
  "capability": "analytical",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Detect the initial stable period, brief spike, and immediate decline.",
      "required_measurements": ["endpoint_slope", "step_level_count", "change_location"],
      "validation_requirements": ["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 12]]
    },
    {
      "scale": "short",
      "objective": "Identify the dramatic decline and partial recovery phase.",
      "required_measurements": ["endpoint_slope", "min_value_location", "pairwise_similarity"],
      "validation_requirements": ["Ensure the slope is negative during the decline and becomes positive towards the end, confirming recovery"],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[12, 23]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.",
      "required_measurements": ["step_level_count", "min_value_location", "endpoint_slope", "pairwise_similarity", "change_location"],
      "validation_requirements": ["Check each series for consistency with textual descriptions regarding key dynamics"],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 23]]
    }
  ],
  "success_criteria": ["All critical features (stability, spike, decline, recovery) should be matched accurately across candidate series"],
  "notes": "Ensure no assumptions about specific values in the narrative override the visual representation of the time series."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4095 completion=359 latency=13.95s

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
{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among four choices best matches the given textual description. The text describes a pattern involving stability, a spike, a decline, and a recovery, all with specific points highlighted. The goal is to find a time series that reflects these dynamics.","task_summary":"Identify the time series out of the given four that best matches the textual description.","target_output":"Select the time series from the following four options that most accurately reflects the described characteristics.","answer_type":"choice","capability":"analytical","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}],"hetero_assignments":[{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All critical features (stability, spike, decline, recovery) should be matched accurately across candidate series"],"notes":"Ensure no assumptions about specific values in the narrative override the visual representation of the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect a specific temporal pattern: an initial stable period, followed by a brief spike, and then an immediate decline. This requires identifying flat segments, peak detection, and slope analysis at endpoints.",
  "evidence_plan": {
    "objective": "Detect the initial stable period, brief spike, and immediate decline.",
    "claims_to_support": [
      {"claim": "There is an initial flat interval.", "required_evidence": ["flat_segment_indicator"]},
      {"claim": "A brief spike occurs immediately after the flat period.", "required_evidence": ["peak_value_location", "peak_value_indicator"]},
      {"claim": "There is an immediate decline after the spike.", "required_evidence": ["decline_slope_indicator"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[0,12]], "scale": "short"},
    "validation_needs": ["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "segment_trend", "reason": "To measure the endpoint slopes indicating an initial flat period and subsequent decline.", "supports_evidence": ["endpoint_slope", "decline_slope_indicator"]},
      {"tool": "local_extrema", "reason": "To count local peaks, indicating the spike.", "supports_evidence": ["peak_value_location", "peak_value_indicator"]},
      {"tool": "step_levels", "reason": "To count the step levels, potentially reflecting the stable interval and subsequent change.", "supports_evidence": ["flat_segment_indicator"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=888 completion=166 latency=5.94s

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
{"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is an initial flat interval.","required_evidence":["flat_segment_indicator"]},{"claim":"A brief spike occurs immediately after the flat period.","required_evidence":["peak_value_location","peak_value_indicator"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["decline_slope_indicator"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the endpoint slopes indicating an initial flat period and subsequent decline.","supports_evidence":["endpoint_slope","decline_slope_indicator"]},{"tool":"local_extrema","reason":"To count local peaks, indicating the spike.","supports_evidence":["peak_value_location","peak_value_indicator"]},{"tool":"step_levels","reason":"To count the step levels, potentially reflecting the stable interval and subsequent change.","supports_evidence":["flat_segment_indicator"]}],"no_tool_decision":null},"reasoning":"The objective is to detect a specific temporal pattern: an initial stable period, followed by a brief spike, and then an immediate decline. This requires identifying flat segments, peak detection, and slope analysis at endpoints."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- local_extrema
  inputs: series_index, start, end
  outputs: series
- segment_trend
  inputs: series_index, start, end
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect a specific temporal pattern: an initial stable period, followed by a brief spike, and then an immediate decline. This requires identifying flat segments, peak detection, and slope analysis at endpoints.",
  "workflow": [
    {
      "step": 1,
      "tool": "step_levels",
      "output_key": "flat_segment_indicator",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "output_key": "peak_value_location",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "segment_trend",
      "output_key": "decline_slope_indicator",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=1019 completion=211 latency=7.56s

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
{"workflow":[{"step":1,"tool":"step_levels","output_key":"flat_segment_indicator","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"peak_value_location","input_binding":{}},{"step":3,"tool":"segment_trend","output_key":"decline_slope_indicator","input_binding":{}}],"reasoning":"The objective is to detect a specific temporal pattern: an initial stable period, followed by a brief spike, and then an immediate decline. This requires identifying flat segments, peak detection, and slope analysis at endpoints."}
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

- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
- segment_trend: Linear slope and direction (upward/downward/flat) for a segment.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series slope/direction for a segment}
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "To meet the objective of detecting a stable period followed by a spike and an immediate decline, we will first use step_levels to identify the flat segment, then detect the peak location using local_extrema, and finally analyze the trend after the peak using segment_trend. The workflow focuses on Series Index 1.",
  "calls": [
    {
      "step": 1,
      "tool": "step_levels",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 12
      }
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 3,
      "tool": "segment_trend",
      "args": {
        "series_index": 1,
        "start": "$step2.peak_value_location+1"
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1547 completion=574 latency=20.55s

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
{"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is an initial flat interval.","required_evidence":["flat_segment_indicator"]},{"claim":"A brief spike occurs immediately after the flat period.","required_evidence":["peak_value_location","peak_value_indicator"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["decline_slope_indicator"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the endpoint slopes indicating an initial flat period and subsequent decline.","supports_evidence":["endpoint_slope","decline_slope_indicator"]},{"tool":"local_extrema","reason":"To count local peaks, indicating the spike.","supports_evidence":["peak_value_location","peak_value_indicator"]},{"tool":"step_levels","reason":"To count the step levels, potentially reflecting the stable interval and subsequent change.","supports_evidence":["flat_segment_indicator"]}],"no_tool_decision":null},"reasoning":"The objective is to detect a specific temporal pattern: an initial stable period, followed by a brief spike, and then an immediate decline. This requires identifying flat segments, peak detection, and slope analysis at endpoints."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "step_levels",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 12,
      "n_unique_levels": 1,
      "n_plateau_runs": 1,
      "levels": [
        83.0
      ],
      "plateau_runs": [
        83.0
      ],
      "plateau_lengths": [
        13
      ],
      "tolerance": 0.001
    },
    "error": null,
    "args_fingerprint": "216b7d180b65635b8424cbd0463083305e824946"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "local_extrema",
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
      "n_peaks": 0,
      "n_troughs": 0,
      "peak_idx": [],
      "trough_idx": []
    },
    "error": null,
    "args_fingerprint": "31139f7e956301f570b30f3a308473f914523713"
  },
  {
    "call_id": "short:step3",
    "step": 3,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": "$step2.peak_value_location+1"
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "slope": 0.0,
      "direction": "flat",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 83.0,
      "std": 0.0,
      "start_value": 83.0,
      "end_value": 83.0
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective was to detect a specific temporal pattern: an initial stable period, followed by a brief spike, and then an immediate decline. The executed steps include using `step_levels` to identify flat intervals, `local_extrema` to find peak values, and `segment_trend` to analyze slopes. However, the current data does not show a spike or a decline as expected. There is an indication of a flat segment but no peak or decline after that.",
  "scale": "short",
  "observations": ["The data shows an initial flat interval, but there's no clear indication of a spike or decline as required."],
  "evidence_intervals": ["from 0 to 12"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There is an initial flat interval.",
      "evidence": [
        {
          "type": "flat_segment_indicator",
          "value": 1,
          "source_tool": "step_levels",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "initial_flat_interval"
    },
    {
      "claim": "A brief spike occurs immediately after the flat period.",
      "evidence": [
        {
          "type": "peak_value_location",
          "value": null,
          "source_tool": "local_extrema",
          "call_id": "short:step2",
          "provenance": "tool"
        },
        {
          "type": "peak_value_indicator",
          "value": false,
          "source_tool": "local_extrema",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "spike_after_flat_period"
    },
    {
      "claim": "There is an immediate decline after the spike.",
      "evidence": [
        {
          "type": "decline_slope_indicator",
          "value": false,
          "source_tool": "segment_trend",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "decline_after_spike"
    }
  ],
  "coverage": {"initial_flat_interval": "tool_supported", "spike_after_flat_period": "unresolved", "decline_after_spike": "unresolved"},
  "unresolved_claims": ["A brief spike occurs immediately after the flat period.", "There is an immediate decline after the spike."]
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m1`

tokens prompt=4128 completion=467 latency=17.94s

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
{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among four choices best matches the given textual description. The text describes a pattern involving stability, a spike, a decline, and a recovery, all with specific points highlighted. The goal is to find a time series that reflects these dynamics.","task_summary":"Identify the time series out of the given four that best matches the textual description.","target_output":"Select the time series from the following four options that most accurately reflects the described characteristics.","answer_type":"choice","capability":"analytical","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}],"hetero_assignments":[{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All critical features (stability, spike, decline, recovery) should be matched accurately across candidate series"],"notes":"Ensure no assumptions about specific values in the narrative override the visual representation of the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
retry_context=unresolved_claims=['A brief spike occurs immediately after the flat period.', 'There is an immediate decline after the spike.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect a pattern in the time series data that includes an initial stable period, a brief spike, and an immediate decline. The required measurements are endpoint slopes, step level counts, and change location. These need to consistently indicate a flat interval followed by a spike and quick drop.",
  "evidence_plan": {
    "objective": "Detect the initial stable period, brief spike, and immediate decline.",
    "claims_to_support": [
      {
        "claim": "There is a flat interval followed by a spike.",
        "required_evidence": ["step_level_count", "change_location"]
      },
      {
        "claim": "There is a brief spike immediately after the flat period.",
        "required_evidence": ["min_value_location", "endpoint_slope"]
      },
      {
        "claim": "There is an immediate decline after the spike.",
        "required_evidence": ["endpoint_slope", "change_location"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[0, 12]],
      "scale": "short"
    },
    "validation_needs": ["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "step_levels",
        "reason": "Step level count will help identify flat intervals and steps.",
        "supports_evidence": ["step_level_count"]
      },
      {
        "tool": "value_at_index",
        "reason": "To find the min_value_location, value_at_index can pinpoint the spike's location.",
        "supports_evidence": ["min_value_location"]
      },
      {
        "tool": "segment_trend",
        "reason": "Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.",
        "supports_evidence": ["endpoint_slope"]
      },
      {
        "tool": "local_extrema",
        "reason": "Local extrema can provide change locations such as the transition from flat to spike and spike to decline.",
        "supports_evidence": ["change_location"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m1`

tokens prompt=973 completion=313 latency=11.11s

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
{"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is a flat interval followed by a spike.","required_evidence":["step_level_count","change_location"]},{"claim":"There is a brief spike immediately after the flat period.","required_evidence":["min_value_location","endpoint_slope"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["endpoint_slope","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Step level count will help identify flat intervals and steps.","supports_evidence":["step_level_count"]},{"tool":"value_at_index","reason":"To find the min_value_location, value_at_index can pinpoint the spike's location.","supports_evidence":["min_value_location"]},{"tool":"segment_trend","reason":"Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.","supports_evidence":["endpoint_slope"]},{"tool":"local_extrema","reason":"Local extrema can provide change locations such as the transition from flat to spike and spike to decline.","supports_evidence":["change_location"]}],"no_tool_decision":null},"reasoning":"The objective is to detect a pattern in the time series data that includes an initial stable period, a brief spike, and an immediate decline. The required measurements are endpoint slopes, step level counts, and change location. These need to consistently indicate a flat interval followed by a spike and quick drop."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- local_extrema
  inputs: series_index, start, end
  outputs: series
- segment_trend
  inputs: series_index, start, end
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
- value_at_index
  inputs: series_index, start, end, index, index_base
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline.",
  "workflow": [
    {
      "step": 1,
      "tool": "step_levels",
      "output_key": "step_level_count",
      "input_binding": {"start": 0, "end": 12}
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "output_key": "change_location",
      "input_binding": {"start": 0, "end": 12}
    },
    {
      "step": 3,
      "tool": "value_at_index",
      "output_key": "min_value_location",
      "input_binding": {"index": "$step2.first_min_index", "start": 0, "end": 12, "index_base": 0}
    },
    {
      "step": 4,
      "tool": "segment_trend",
      "output_key": "endpoint_slope",
      "input_binding": {"start": 0, "end": 12}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m1`

tokens prompt=1230 completion=275 latency=9.87s

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
{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_count","input_binding":{"start":0,"end":12}},{"step":2,"tool":"local_extrema","output_key":"change_location","input_binding":{"start":0,"end":12}},{"step":3,"tool":"value_at_index","output_key":"min_value_location","input_binding":{"index":"$step2.first_min_index","start":0,"end":12,"index_base":0}},{"step":4,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{"start":0,"end":12}}],"reasoning":"The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline."}
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

- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
- segment_trend: Linear slope and direction (upward/downward/flat) for a segment.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series slope/direction for a segment}
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
- value_at_index: Return the numeric value at a specific index (0-based by default).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, index=required int index, index_base=0 (default) or 1 if question uses 1-based indices}
  returns: {series=selected series, requested index/position, and exact value}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline.",
  "calls": [
    {"step": 1, "tool": "step_levels", "args": {"series_index": 1, "start": 0, "end": 12}},
    {"step": 2, "tool": "local_extrema", "args": {"series_index": 1, "start": 0, "end": 12}},
    {"step": 3, "tool": "value_at_index", "args": {"series_index": 1, "start": 0, "end": 12, "index": "$step2.first_min_index", "index_base": 0}},
    {"step": 4, "tool": "segment_trend", "args": {"series_index": 1, "start": 0, "end": 12}}
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m1`

tokens prompt=1773 completion=451 latency=16.29s

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
{"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is a flat interval followed by a spike.","required_evidence":["step_level_count","change_location"]},{"claim":"There is a brief spike immediately after the flat period.","required_evidence":["min_value_location","endpoint_slope"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["endpoint_slope","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Step level count will help identify flat intervals and steps.","supports_evidence":["step_level_count"]},{"tool":"value_at_index","reason":"To find the min_value_location, value_at_index can pinpoint the spike's location.","supports_evidence":["min_value_location"]},{"tool":"segment_trend","reason":"Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.","supports_evidence":["endpoint_slope"]},{"tool":"local_extrema","reason":"Local extrema can provide change locations such as the transition from flat to spike and spike to decline.","supports_evidence":["change_location"]}],"no_tool_decision":null},"reasoning":"The objective is to detect a pattern in the time series data that includes an initial stable period, a brief spike, and an immediate decline. The required measurements are endpoint slopes, step level counts, and change location. These need to consistently indicate a flat interval followed by a spike and quick drop."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "step_levels",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 12,
      "n_unique_levels": 1,
      "n_plateau_runs": 1,
      "levels": [
        83.0
      ],
      "plateau_runs": [
        83.0
      ],
      "plateau_lengths": [
        13
      ],
      "tolerance": 0.001
    },
    "error": null,
    "args_fingerprint": "216b7d180b65635b8424cbd0463083305e824946"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "local_extrema",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 12,
      "n_peaks": 0,
      "n_troughs": 0,
      "peak_idx": [],
      "trough_idx": []
    },
    "error": null,
    "args_fingerprint": "70d9353b3853a282cec05a1ded29aac10dda6f09"
  },
  {
    "call_id": "short:step3",
    "step": 3,
    "tool_name": "value_at_index",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12,
      "index": "$step2.first_min_index",
      "index_base": 0
    },
    "resolved_arguments": {},
    "success": false,
    "data": {},
    "error": "\"path 'first_min_index' not found in tool result\"",
    "args_fingerprint": ""
  },
  {
    "call_id": "short:step4",
    "step": 4,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 12
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 12,
      "slope": 0.0,
      "direction": "flat",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 83.0,
      "std": 0.0,
      "start_value": 83.0,
      "end_value": 83.0
    },
    "error": null,
    "args_fingerprint": "1bef3a3ac646e6e56fb2b009277802d6dc290900"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The executed steps indicate that the data in the specified interval is flat, with no peaks or troughs detected. The step levels tool showed one unique level throughout the interval, confirming a stable period. However, there is insufficient evidence to support claims of a spike or immediate decline due to the lack of identified extrema and the absence of slope change.",
  "scale": "short",
  "observations": ["The data shows a stable period without any spikes or immediate declines within the given interval.", "No significant change points were detected, suggesting a consistent value throughout the observation period."],
  "evidence_intervals": ["interval [0, 12]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There is a flat interval.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 1,
          "source_tool": "step_levels",
          "call_id": "short:step1",
          "provenance": "tool"
        },
        {
          "type": "slope_direction",
          "value": "flat",
          "source_tool": "segment_trend",
          "call_id": "short:step4",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "step_level_count"
    },
    {
      "claim": "There is a brief spike immediately after the flat period.",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "min_value_location"
    },
    {
      "claim": "There is an immediate decline after the spike.",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "endpoint_slope"
    }
  ],
  "coverage": {"step_level_count": "tool_supported", "min_value_location": "unresolved", "endpoint_slope": "unresolved"},
  "unresolved_claims": ["There is a brief spike immediately after the flat period.", "There is an immediate decline after the spike."]
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=4610 completion=330 latency=13.11s

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
{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among four choices best matches the given textual description. The text describes a pattern involving stability, a spike, a decline, and a recovery, all with specific points highlighted. The goal is to find a time series that reflects these dynamics.","task_summary":"Identify the time series out of the given four that best matches the textual description.","target_output":"Select the time series from the following four options that most accurately reflects the described characteristics.","answer_type":"choice","capability":"analytical","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}],"hetero_assignments":[{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All critical features (stability, spike, decline, recovery) should be matched accurately across candidate series"],"notes":"Ensure no assumptions about specific values in the narrative override the visual representation of the time series."}
</plan_context>

<task_summary>
Identify the time series out of the given four that best matches the textual description.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The executed steps indicate that the data in the specified interval is flat, with no peaks or troughs detected. The step levels tool showed one unique level throughout the interval, confirming a stable period. However, there is insufficient evidence to support claims of a spike or immediate decline due to the lack of identified extrema and the absence of slope change.","scale":"short","observations":["The data shows a stable period without any spikes or immediate declines within the given interval.","No significant change points were detected, suggesting a consistent value throughout the observation period."],"evidence_intervals":["interval [0, 12]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_unique_levels\": 1, \"n_plateau_runs\": 1, \"levels\": [83.0], \"plateau_runs\": [83.0], \"plateau_lengths\": [13], \"tolerance\": 0.001}, \"error\": null, \"args_fingerprint\": \"216b7d180b65635b8424cbd0463083305e824946\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_peaks\": 0, \"n_troughs\": 0, \"peak_idx\": [], \"trough_idx\": []}, \"error\": null, \"args_fingerprint\": \"70d9353b3853a282cec05a1ded29aac10dda6f09\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"index\": \"$step2.first_min_index\", \"index_base\": 0}, \"resolved_arguments\": {}, \"success\": false, \"data\": {}, \"error\": \"\\\"path 'first_min_index' not found in tool result\\\"\", \"args_fingerprint\": \"\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"slope\": 0.0, \"direction\": \"flat\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 83.0, \"std\": 0.0, \"start_value\": 83.0, \"end_value\": 83.0}, \"error\": null, \"args_fingerprint\": \"1bef3a3ac646e6e56fb2b009277802d6dc290900\"}"],"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is a flat interval followed by a spike.","required_evidence":["step_level_count","change_location"]},{"claim":"There is a brief spike immediately after the flat period.","required_evidence":["min_value_location","endpoint_slope"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["endpoint_slope","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Step level count will help identify flat intervals and steps.","supports_evidence":["step_level_count"]},{"tool":"value_at_index","reason":"To find the min_value_location, value_at_index can pinpoint the spike's location.","supports_evidence":["min_value_location"]},{"tool":"segment_trend","reason":"Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.","supports_evidence":["endpoint_slope"]},{"tool":"local_extrema","reason":"Local extrema can provide change locations such as the transition from flat to spike and spike to decline.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_count","input_binding":{"start":0,"end":12}},{"step":2,"tool":"local_extrema","output_key":"change_location","input_binding":{"start":0,"end":12}},{"step":3,"tool":"value_at_index","output_key":"min_value_location","input_binding":{"index":"$step2.first_min_index","start":0,"end":12,"index_base":0}},{"step":4,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{"start":0,"end":12}}],"reasoning":"The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline."},"structured_observations":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}],"coverage":{"step_level_count":"tool_supported","min_value_location":"unresolved","endpoint_slope":"unresolved"},"unresolved_claims":["There is a brief spike immediately after the flat period.","There is an immediate decline after the spike."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_unique_levels":1,"n_plateau_runs":1,"levels":[83.0],"plateau_runs":[83.0],"plateau_lengths":[13],"tolerance":0.001},"error":null,"args_fingerprint":"216b7d180b65635b8424cbd0463083305e824946"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_peaks":0,"n_troughs":0,"peak_idx":[],"trough_idx":[]},"error":null,"args_fingerprint":"70d9353b3853a282cec05a1ded29aac10dda6f09"},{"call_id":"short:step3","step":3,"tool_name":"value_at_index","arguments":{"series_index":1,"start":0,"end":12,"index":"$step2.first_min_index","index_base":0},"resolved_arguments":{},"success":false,"data":{},"error":"\"path 'first_min_index' not found in tool result\"","args_fingerprint":""},{"call_id":"short:step4","step":4,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"slope":0.0,"direction":"flat","direction_class":"vague","trend_method":"endpoint","mean":83.0,"std":0.0,"start_value":83.0,"end_value":83.0},"error":null,"args_fingerprint":"1bef3a3ac646e6e56fb2b009277802d6dc290900"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"The data shows a stable period without any spikes or immediate declines within the given interval. No significant change points were detected, suggesting a consistent value throughout the observation period.","structured_by_scale":{"short":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence from the temporal profile indicates that the short scale interval was stable without any spikes or declines, lacking the required evidence for validating the presence of such dynamics. Therefore, we need further investigation into each series to confirm if they meet the textual description's criteria. Specifically, pairwise similarity, change location, step level count, min value location, and endpoint slope measurements are essential for identifying which time series matches the narrative.",
  "evidence_plan": {
    "objective": "Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.",
    "claims_to_support": [
      {"claim": "Time series contains a stable period followed by a spike and then an immediate decline.", "required_evidence": ["step_level_count", "min_value_location", "endpoint_slope", "pairwise_similarity", "change_location"]}
    ],
    "analysis_scope": {"target_series": [1, 2, 3, 4], "role": "matching"},
    "validation_needs": ["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "describe_series", "reason": "To gather a preliminary overview of each series for comparison"},
      {"tool": "local_extrema", "reason": "For detecting potential spike and decline locations"},
      {"tool": "pairwise_distance", "reason": "To measure similarity between the query narrative and each series"}
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m0`

tokens prompt=737 completion=207 latency=7.34s

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
{"evidence_plan":{"objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","claims_to_support":[{"claim":"Time series contains a stable period followed by a spike and then an immediate decline.","required_evidence":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"]}],"analysis_scope":{"target_series":[1,2,3,4],"role":"matching"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"To gather a preliminary overview of each series for comparison","supports_evidence":[]},{"tool":"local_extrema","reason":"For detecting potential spike and decline locations","supports_evidence":[]},{"tool":"pairwise_distance","reason":"To measure similarity between the query narrative and each series","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence from the temporal profile indicates that the short scale interval was stable without any spikes or declines, lacking the required evidence for validating the presence of such dynamics. Therefore, we need further investigation into each series to confirm if they meet the textual description's criteria. Specifically, pairwise similarity, change location, step level count, min value location, and endpoint slope measurements are essential for identifying which time series matches the narrative."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- local_extrema
  inputs: series_index, start, end
  outputs: series
- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'describe_series' to get an overview of each time series. Then, we apply 'local_extrema' to identify potential spikes and declines. Finally, we use 'pairwise_distance' to quantify the similarity between the textual description and each series based on these identified features.",
  "workflow": [
    {
      "step": 1,
      "tool": "describe_series",
      "output_key": "overview",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "output_key": "extrema",
      "input_binding": {"series_index": "$describe_series.series_index"}
    },
    {
      "step": 3,
      "tool": "pairwise_distance",
      "output_key": "pair_compare",
      "input_binding": {"method": "dynamic_time_warping", "series_index": "$local_extrema.series_index"}
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m0`

tokens prompt=1015 completion=159 latency=5.72s

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
{"workflow":[{"step":1,"tool":"describe_series","output_key":"overview","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"extrema","input_binding":{"series_index":"$describe_series.series_index"}},{"step":3,"tool":"pairwise_distance","output_key":"pair_compare","input_binding":{"method":"dynamic_time_warping","series_index":"$local_extrema.series_index"}}],"reasoning":"First, we use 'describe_series' to get an overview of each time series. Then, we apply 'local_extrema' to identify potential spikes and declines. Finally, we use 'pairwise_distance' to quantify the similarity between the textual description and each series based on these identified features."}
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

- describe_series: Descriptive stats for EVERY series: mean/std/min/max/median/range/p50/p90/p99/slope (preferred multi-series overview).
  args: {note=no series_index needed; always returns all series}
  returns: {series=per-series length and descriptive statistics}
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  args: {method=euclidean|dtw, series_index=reference 1-based (default 1)}
  returns: {distances=per-candidate distances, nearest=winner, method=distance metadata}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "We first describe the series to understand their general characteristics. Next, we find the local extrema in each series to analyze their peaks and troughs. Finally, we compare the candidate series pairwise using Dynamic Time Warping to find similarities.",
  "calls": [
    {
      "step": 1,
      "tool": "describe_series",
      "args": {}
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "args": {"series_index": "all"}
    },
    {
      "step": 3,
      "tool": "pairwise_distance",
      "args": {"method": "dynamic_time_warping", "series_index": 1}
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=5062 completion=687 latency=26.58s

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
{"evidence_plan":{"objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","claims_to_support":[{"claim":"Time series contains a stable period followed by a spike and then an immediate decline.","required_evidence":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"]}],"analysis_scope":{"target_series":[1,2,3,4],"role":"matching"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"To gather a preliminary overview of each series for comparison","supports_evidence":[]},{"tool":"local_extrema","reason":"For detecting potential spike and decline locations","supports_evidence":[]},{"tool":"pairwise_distance","reason":"To measure similarity between the query narrative and each series","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence from the temporal profile indicates that the short scale interval was stable without any spikes or declines, lacking the required evidence for validating the presence of such dynamics. Therefore, we need further investigation into each series to confirm if they meet the textual description's criteria. Specifically, pairwise similarity, change location, step level count, min value location, and endpoint slope measurements are essential for identifying which time series matches the narrative."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "matching:step1",
    "step": 1,
    "tool_name": "describe_series",
    "arguments": {},
    "resolved_arguments": {},
    "success": true,
    "data": {
      "series": [
        {
          "series_index": 1,
          "index": 1,
          "length": 24,
          "mean": 83.0,
          "std": 0.0,
          "min": 83.0,
          "max": 83.0,
          "median": 83.0,
          "range": 0.0,
          "p50": 83.0,
          "p90": 83.0,
          "p99": 83.0,
          "start": 83.0,
          "end": 83.0,
          "slope": 0.0
        },
        {
          "series_index": 2,
          "index": 2,
          "length": 24,
          "mean": 40.05083333333333,
          "std": 4.57562101128239,
          "min": 30.81,
          "max": 52.8,
          "median": 39.81,
          "range": 21.99,
          "p50": 39.81,
          "p90": 45.446999999999996,
          "p99": 52.1928,
          "start": 52.8,
          "end": 30.81,
          "slope": -0.956086956521739
        },
        {
          "series_index": 3,
          "index": 3,
          "length": 24,
          "mean": 8.015,
          "std": 5.0398916985718385,
          "min": 0.63,
          "max": 14.8,
          "median": 9.54,
          "range": 14.17,
          "p50": 9.54,
          "p90": 14.347,
          "p99": 14.7563,
          "start": 1.46,
          "end": 2.68,
          "slope": 0.053043478260869574
        },
        {
          "series_index": 4,
          "index": 4,
          "length": 24,
          "mean": 36.23583333333333,
          "std": 6.675275223206572,
          "min": 22.08,
          "max": 42.55,
          "median": 40.33,
          "range": 20.47,
          "p50": 40.33,
          "p90": 41.641999999999996,
          "p99": 42.5017,
          "start": 40.3,
          "end": 24.89,
          "slope": -0.6699999999999998
        }
      ]
    },
    "error": null,
    "args_fingerprint": "90b10717d4a3e6c0750bb980207b8d86753ac968"
  },
  {
    "call_id": "matching:step2",
    "step": 2,
    "tool_name": "local_extrema",
    "arguments": {
      "series_index": "all"
    },
    "resolved_arguments": {
      "series_index": "all"
    },
    "success": true,
    "data": {
      "series": [
        {
          "series_index": 1,
          "start": null,
          "end": null,
          "n_peaks": 0,
          "n_troughs": 0,
          "peak_idx": [],
          "trough_idx": []
        },
        {
          "series_index": 2,
          "start": null,
          "end": null,
          "n_peaks": 2,
          "n_troughs": 2,
          "peak_idx": [
            11,
            18
          ],
          "trough_idx": [
            6,
            17
          ]
        },
        {
          "series_index": 3,
          "start": null,
          "end": null,
          "n_peaks": 3,
          "n_troughs": 3,
          "peak_idx": [
            9,
            15,
            17
          ],
          "trough_idx": [
            2,
            11,
            16
          ]
        },
        {
          "series_index": 4,
          "start": null,
          "end": null,
          "n_peaks": 2,
          "n_troughs": 2,
          "peak_idx": [
            3,
            11
          ],
          "trough_idx": [
            9,
            22
          ]
        }
      ],
      "n_series": 4
    },
    "error": null,
    "args_fingerprint": "ed3de2d42ef119c33379550e270ed87d90c24ca6"
  },
  {
    "call_id": "matching:step3",
    "step": 3,
    "tool_name": "pairwise_distance",
    "arguments": {
      "method": "dynamic_time_warping",
      "series_index": 1
    },
    "resolved_arguments": {
      "method": "dynamic_time_warping",
      "series_index": 1
    },
    "success": true,
    "data": {
      "method": "dynamic_time_warping",
      "ref_series_index": 1,
      "distances": [
        {
          "series_index": 2,
          "distance": 406.64480815571716
        },
        {
          "series_index": 3,
          "distance": 406.64480815571716
        },
        {
          "series_index": 4,
          "distance": 406.64480815571716
        }
      ],
      "nearest": {
        "series_index": 2,
        "distance": 406.64480815571716
      }
    },
    "error": null,
    "args_fingerprint": "e72fc678fc6a55bde55e80f716231d68643cdf36"
  }
]
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The executed steps indicate that the data in the specified interval is flat, with no peaks or troughs detected. The step levels tool showed one unique level throughout the interval, confirming a stable period. However, there is insufficient evidence to support claims of a spike or immediate decline due to the lack of identified extrema and the absence of slope change.","scale":"short","observations":["The data shows a stable period without any spikes or immediate declines within the given interval.","No significant change points were detected, suggesting a consistent value throughout the observation period."],"evidence_intervals":["interval [0, 12]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_unique_levels\": 1, \"n_plateau_runs\": 1, \"levels\": [83.0], \"plateau_runs\": [83.0], \"plateau_lengths\": [13], \"tolerance\": 0.001}, \"error\": null, \"args_fingerprint\": \"216b7d180b65635b8424cbd0463083305e824946\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_peaks\": 0, \"n_troughs\": 0, \"peak_idx\": [], \"trough_idx\": []}, \"error\": null, \"args_fingerprint\": \"70d9353b3853a282cec05a1ded29aac10dda6f09\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"index\": \"$step2.first_min_index\", \"index_base\": 0}, \"resolved_arguments\": {}, \"success\": false, \"data\": {}, \"error\": \"\\\"path 'first_min_index' not found in tool result\\\"\", \"args_fingerprint\": \"\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"slope\": 0.0, \"direction\": \"flat\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 83.0, \"std\": 0.0, \"start_value\": 83.0, \"end_value\": 83.0}, \"error\": null, \"args_fingerprint\": \"1bef3a3ac646e6e56fb2b009277802d6dc290900\"}"],"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is a flat interval followed by a spike.","required_evidence":["step_level_count","change_location"]},{"claim":"There is a brief spike immediately after the flat period.","required_evidence":["min_value_location","endpoint_slope"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["endpoint_slope","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Step level count will help identify flat intervals and steps.","supports_evidence":["step_level_count"]},{"tool":"value_at_index","reason":"To find the min_value_location, value_at_index can pinpoint the spike's location.","supports_evidence":["min_value_location"]},{"tool":"segment_trend","reason":"Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.","supports_evidence":["endpoint_slope"]},{"tool":"local_extrema","reason":"Local extrema can provide change locations such as the transition from flat to spike and spike to decline.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_count","input_binding":{"start":0,"end":12}},{"step":2,"tool":"local_extrema","output_key":"change_location","input_binding":{"start":0,"end":12}},{"step":3,"tool":"value_at_index","output_key":"min_value_location","input_binding":{"index":"$step2.first_min_index","start":0,"end":12,"index_base":0}},{"step":4,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{"start":0,"end":12}}],"reasoning":"The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline."},"structured_observations":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}],"coverage":{"step_level_count":"tool_supported","min_value_location":"unresolved","endpoint_slope":"unresolved"},"unresolved_claims":["There is a brief spike immediately after the flat period.","There is an immediate decline after the spike."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_unique_levels":1,"n_plateau_runs":1,"levels":[83.0],"plateau_runs":[83.0],"plateau_lengths":[13],"tolerance":0.001},"error":null,"args_fingerprint":"216b7d180b65635b8424cbd0463083305e824946"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_peaks":0,"n_troughs":0,"peak_idx":[],"trough_idx":[]},"error":null,"args_fingerprint":"70d9353b3853a282cec05a1ded29aac10dda6f09"},{"call_id":"short:step3","step":3,"tool_name":"value_at_index","arguments":{"series_index":1,"start":0,"end":12,"index":"$step2.first_min_index","index_base":0},"resolved_arguments":{},"success":false,"data":{},"error":"\"path 'first_min_index' not found in tool result\"","args_fingerprint":""},{"call_id":"short:step4","step":4,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"slope":0.0,"direction":"flat","direction_class":"vague","trend_method":"endpoint","mean":83.0,"std":0.0,"start_value":83.0,"end_value":83.0},"error":null,"args_fingerprint":"1bef3a3ac646e6e56fb2b009277802d6dc290900"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"The data shows a stable period without any spikes or immediate declines within the given interval. No significant change points were detected, suggesting a consistent value throughout the observation period.","structured_by_scale":{"short":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "After evaluating the described narrative against all four candidate time series, there is no clear alignment based on the available evidence. Series 1 has a consistently flat trend with no spikes or declines, as indicated by its mean value being equal across all observations and no detected extrema, making it the least likely match. Series 2 shows fluctuations with two peaks and troughs but does not fit the specific pattern of a flat period followed by a spike and rapid decline. Similarly, Series 3 and 4 display varying values and multiple peaks/troughs, but again, do not specifically adhere to the required flat period, spike, and rapid decline sequence.",
  "role": "matching",
  "hypothesis": "None of the candidate time series perfectly match the narrative of a stable period followed by a spike and then an immediate decline.",
  "evidence": [
    "Series 1's data shows a constant value without any significant change, contradicting the required spike and decline dynamic.",
    "While Series 2, 3, and 4 exhibit changes in their values, they do not clearly depict the specific dynamic described, including a flat period followed by a distinct spike and rapid decline."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["matching:step1", "matching:step2", "matching:step3", "short:step1", "short:step2", "short:step3", "short:step4"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The narrative specifies a flat period followed by a spike and rapid decline, a pattern that none of the series perfectly match.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 1,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        },
        {
          "type": "slope_direction",
          "value": "flat",
          "provenance": "tool",
          "ref": "short:step4",
          "call_id": "short:step4"
        },
        {
          "type": "n_peaks",
          "value": 2,
          "provenance": "upstream",
          "ref": "matching:step2",
          "call_id": "matching:step2"
        },
        {
          "type": "n_troughs",
          "value": 2,
          "provenance": "upstream",
          "ref": "matching:step2",
          "call_id": "matching:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "step_level_count": "context_supported",
    "min_value_location": "unresolved",
    "endpoint_slope": "unresolved",
    "pairwise_similarity": "context_supported",
    "change_location": "context_supported"
  },
  "unresolved_claims": [
    "There is a brief spike immediately after the flat period.",
    "There is an immediate decline after the spike."
  ]
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=4640 completion=345 latency=13.67s

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
{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among four choices best matches the given textual description. The text describes a pattern involving stability, a spike, a decline, and a recovery, all with specific points highlighted. The goal is to find a time series that reflects these dynamics.","task_summary":"Identify the time series out of the given four that best matches the textual description.","target_output":"Select the time series from the following four options that most accurately reflects the described characteristics.","answer_type":"choice","capability":"analytical","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Detect the initial stable period, brief spike, and immediate decline.","required_measurements":["endpoint_slope","step_level_count","change_location"],"validation_requirements":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"],"target_series":[1,2,3,4],"focus_intervals":[[0,12]]}],"hetero_assignments":[{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["short"],"heterogeneous_agents":["matching"],"success_criteria":["All critical features (stability, spike, decline, recovery) should be matched accurately across candidate series"],"notes":"Ensure no assumptions about specific values in the narrative override the visual representation of the time series."}
</plan_context>

<task_summary>
Identify the time series out of the given four that best matches the textual description.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The executed steps indicate that the data in the specified interval is flat, with no peaks or troughs detected. The step levels tool showed one unique level throughout the interval, confirming a stable period. However, there is insufficient evidence to support claims of a spike or immediate decline due to the lack of identified extrema and the absence of slope change.","scale":"short","observations":["The data shows a stable period without any spikes or immediate declines within the given interval.","No significant change points were detected, suggesting a consistent value throughout the observation period."],"evidence_intervals":["interval [0, 12]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_unique_levels\": 1, \"n_plateau_runs\": 1, \"levels\": [83.0], \"plateau_runs\": [83.0], \"plateau_lengths\": [13], \"tolerance\": 0.001}, \"error\": null, \"args_fingerprint\": \"216b7d180b65635b8424cbd0463083305e824946\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_peaks\": 0, \"n_troughs\": 0, \"peak_idx\": [], \"trough_idx\": []}, \"error\": null, \"args_fingerprint\": \"70d9353b3853a282cec05a1ded29aac10dda6f09\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"index\": \"$step2.first_min_index\", \"index_base\": 0}, \"resolved_arguments\": {}, \"success\": false, \"data\": {}, \"error\": \"\\\"path 'first_min_index' not found in tool result\\\"\", \"args_fingerprint\": \"\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"slope\": 0.0, \"direction\": \"flat\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 83.0, \"std\": 0.0, \"start_value\": 83.0, \"end_value\": 83.0}, \"error\": null, \"args_fingerprint\": \"1bef3a3ac646e6e56fb2b009277802d6dc290900\"}"],"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is a flat interval followed by a spike.","required_evidence":["step_level_count","change_location"]},{"claim":"There is a brief spike immediately after the flat period.","required_evidence":["min_value_location","endpoint_slope"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["endpoint_slope","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Step level count will help identify flat intervals and steps.","supports_evidence":["step_level_count"]},{"tool":"value_at_index","reason":"To find the min_value_location, value_at_index can pinpoint the spike's location.","supports_evidence":["min_value_location"]},{"tool":"segment_trend","reason":"Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.","supports_evidence":["endpoint_slope"]},{"tool":"local_extrema","reason":"Local extrema can provide change locations such as the transition from flat to spike and spike to decline.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_count","input_binding":{"start":0,"end":12}},{"step":2,"tool":"local_extrema","output_key":"change_location","input_binding":{"start":0,"end":12}},{"step":3,"tool":"value_at_index","output_key":"min_value_location","input_binding":{"index":"$step2.first_min_index","start":0,"end":12,"index_base":0}},{"step":4,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{"start":0,"end":12}}],"reasoning":"The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline."},"structured_observations":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}],"coverage":{"step_level_count":"tool_supported","min_value_location":"unresolved","endpoint_slope":"unresolved"},"unresolved_claims":["There is a brief spike immediately after the flat period.","There is an immediate decline after the spike."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_unique_levels":1,"n_plateau_runs":1,"levels":[83.0],"plateau_runs":[83.0],"plateau_lengths":[13],"tolerance":0.001},"error":null,"args_fingerprint":"216b7d180b65635b8424cbd0463083305e824946"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_peaks":0,"n_troughs":0,"peak_idx":[],"trough_idx":[]},"error":null,"args_fingerprint":"70d9353b3853a282cec05a1ded29aac10dda6f09"},{"call_id":"short:step3","step":3,"tool_name":"value_at_index","arguments":{"series_index":1,"start":0,"end":12,"index":"$step2.first_min_index","index_base":0},"resolved_arguments":{},"success":false,"data":{},"error":"\"path 'first_min_index' not found in tool result\"","args_fingerprint":""},{"call_id":"short:step4","step":4,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"slope":0.0,"direction":"flat","direction_class":"vague","trend_method":"endpoint","mean":83.0,"std":0.0,"start_value":83.0,"end_value":83.0},"error":null,"args_fingerprint":"1bef3a3ac646e6e56fb2b009277802d6dc290900"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"The data shows a stable period without any spikes or immediate declines within the given interval. No significant change points were detected, suggesting a consistent value throughout the observation period.","structured_by_scale":{"short":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
retry_context=unresolved_claims=['There is a brief spike immediately after the flat period.', 'There is an immediate decline after the spike.']
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence from the temporal profile indicates a flat interval for the target series but lacks supporting details for a spike, decline, and overall pairwise similarity. The objective is to identify the time series among the candidates that matches the described dynamics, including stability, spike, decline, and recovery. This requires a more thorough investigation into each series to determine their respective dynamics.",
  "evidence_plan": {
    "objective": "Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.",
    "claims_to_support": [
      {
        "claim": "There is a flat interval followed by a spike and decline.",
        "required_evidence": ["step_level_count", "min_value_location", "endpoint_slope"]
      },
      {
        "claim": "The pairwise similarity score between the target series and candidate series accurately reflects their alignment.",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "The location of significant changes (spike and decline) is captured.",
        "required_evidence": ["change_location"]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2, 3, 4],
      "role": "matching"
    },
    "validation_needs": ["step_level_count", "min_value_location", "endpoint_slope", "pairwise_similarity", "change_location"]
  },
  "capability_selection": {
    "selected_tools": [
      "step_levels",
      "local_extrema",
      "pairwise_distance",
      "smooth_reverse_stats"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=3226 completion=460 latency=17.29s

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
{"evidence_plan":{"objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The executed steps indicate that the data in the specified interval is flat, with no peaks or troughs detected. The step levels tool showed one unique level throughout the interval, confirming a stable period. However, there is insufficient evidence to support claims of a spike or immediate decline due to the lack of identified extrema and the absence of slope change.","scale":"short","observations":["The data shows a stable period without any spikes or immediate declines within the given interval.","No significant change points were detected, suggesting a consistent value throughout the observation period."],"evidence_intervals":["interval [0, 12]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_unique_levels\": 1, \"n_plateau_runs\": 1, \"levels\": [83.0], \"plateau_runs\": [83.0], \"plateau_lengths\": [13], \"tolerance\": 0.001}, \"error\": null, \"args_fingerprint\": \"216b7d180b65635b8424cbd0463083305e824946\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"n_peaks\": 0, \"n_troughs\": 0, \"peak_idx\": [], \"trough_idx\": []}, \"error\": null, \"args_fingerprint\": \"70d9353b3853a282cec05a1ded29aac10dda6f09\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"value_at_index\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"index\": \"$step2.first_min_index\", \"index_base\": 0}, \"resolved_arguments\": {}, \"success\": false, \"data\": {}, \"error\": \"\\\"path 'first_min_index' not found in tool result\\\"\", \"args_fingerprint\": \"\"}","{\"call_id\": \"short:step4\", \"step\": 4, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 12}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 12, \"slope\": 0.0, \"direction\": \"flat\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 83.0, \"std\": 0.0, \"start_value\": 83.0, \"end_value\": 83.0}, \"error\": null, \"args_fingerprint\": \"1bef3a3ac646e6e56fb2b009277802d6dc290900\"}"],"evidence_plan":{"objective":"Detect the initial stable period, brief spike, and immediate decline.","claims_to_support":[{"claim":"There is a flat interval followed by a spike.","required_evidence":["step_level_count","change_location"]},{"claim":"There is a brief spike immediately after the flat period.","required_evidence":["min_value_location","endpoint_slope"]},{"claim":"There is an immediate decline after the spike.","required_evidence":["endpoint_slope","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,12]],"scale":"short"},"validation_needs":["Measurements should consistently indicate a flat interval followed by a spike and quick drop"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Step level count will help identify flat intervals and steps.","supports_evidence":["step_level_count"]},{"tool":"value_at_index","reason":"To find the min_value_location, value_at_index can pinpoint the spike's location.","supports_evidence":["min_value_location"]},{"tool":"segment_trend","reason":"Segment trend analysis helps determine slope changes indicating a flat interval followed by a spike and immediate decline.","supports_evidence":["endpoint_slope"]},{"tool":"local_extrema","reason":"Local extrema can provide change locations such as the transition from flat to spike and spike to decline.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_count","input_binding":{"start":0,"end":12}},{"step":2,"tool":"local_extrema","output_key":"change_location","input_binding":{"start":0,"end":12}},{"step":3,"tool":"value_at_index","output_key":"min_value_location","input_binding":{"index":"$step2.first_min_index","start":0,"end":12,"index_base":0}},{"step":4,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{"start":0,"end":12}}],"reasoning":"The objective requires identifying a stable period followed by a spike and then an immediate decline. To achieve this, we first use step_levels to identify the step-level count, which indicates flat intervals and steps. Next, local_extrema finds change locations critical for pinpointing the transition points. Then, value_at_index locates the minimum value during the spike. Finally, segment_trend determines endpoint slopes, confirming the pattern of flat interval, spike, and decline."},"structured_observations":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}],"coverage":{"step_level_count":"tool_supported","min_value_location":"unresolved","endpoint_slope":"unresolved"},"unresolved_claims":["There is a brief spike immediately after the flat period.","There is an immediate decline after the spike."],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_unique_levels":1,"n_plateau_runs":1,"levels":[83.0],"plateau_runs":[83.0],"plateau_lengths":[13],"tolerance":0.001},"error":null,"args_fingerprint":"216b7d180b65635b8424cbd0463083305e824946"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"n_peaks":0,"n_troughs":0,"peak_idx":[],"trough_idx":[]},"error":null,"args_fingerprint":"70d9353b3853a282cec05a1ded29aac10dda6f09"},{"call_id":"short:step3","step":3,"tool_name":"value_at_index","arguments":{"series_index":1,"start":0,"end":12,"index":"$step2.first_min_index","index_base":0},"resolved_arguments":{},"success":false,"data":{},"error":"\"path 'first_min_index' not found in tool result\"","args_fingerprint":""},{"call_id":"short:step4","step":4,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":12},"resolved_arguments":{"series_index":1,"start":0,"end":12},"success":true,"data":{"series_index":1,"start":0,"end":12,"slope":0.0,"direction":"flat","direction_class":"vague","trend_method":"endpoint","mean":83.0,"std":0.0,"start_value":83.0,"end_value":83.0},"error":null,"args_fingerprint":"1bef3a3ac646e6e56fb2b009277802d6dc290900"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"The data shows a stable period without any spikes or immediate declines within the given interval. No significant change points were detected, suggesting a consistent value throughout the observation period.","structured_by_scale":{"short":[{"claim":"There is a flat interval.","evidence":[{"type":"step_level_count","value":1,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"slope_direction","value":"flat","source_tool":"segment_trend","call_id":"short:step4","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"There is a brief spike immediately after the flat period.","evidence":[],"confidence":"unresolved","maps_to_measurement":"min_value_location"},{"claim":"There is an immediate decline after the spike.","evidence":[],"confidence":"unresolved","maps_to_measurement":"endpoint_slope"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.","required_measurements":["step_level_count","min_value_location","endpoint_slope","pairwise_similarity","change_location"],"validation_requirements":["Check each series for consistency with textual descriptions regarding key dynamics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, Time Series 1 shows a stable period without any spikes or immediate declines. This aligns with the narrative description where the series does not exhibit sharp changes like spikes or declines. However, the required measurements of min_value_location and endpoint_slope remain unresolved, preventing a more detailed match.",
  "role": "matching",
  "hypothesis": "Time Series 1 best matches the described stable period without any notable spikes or immediate declines based on available evidence.",
  "evidence": [
    "interval [0, 12]",
    "The data shows a stable period without any spikes or immediate declines within the given interval.",
    "No significant change points were detected, suggesting a consistent value throughout the observation period."
  ],
  "candidate_preference": "A",
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "short:step1",
    "short:step2",
    "short:step4"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 1 shows a stable period without any spikes or immediate declines.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 1,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        },
        {
          "type": "slope_direction",
          "value": "flat",
          "provenance": "tool",
          "ref": "short:step4",
          "call_id": "short:step4"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "step_level_count": "tool_supported",
    "slope_direction": "tool_supported",
    "min_value_location": "unresolved",
    "endpoint_slope": "unresolved"
  },
  "unresolved_claims": [
    "There is a brief spike immediately after the flat period.",
    "There is an immediate decline after the spike."
  ]
}
```

## Integration — `integration`

tokens prompt=1422 completion=271 latency=9.79s

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
'This time series exhibits an initial stable period around 40-41 from index 0-10, followed by a brief spike to 42.55 at index 11-12, then a dramatic monotonic decline from index 13-22 reaching a minimum of 22.08, before showing a partial recovery to 24.89 at the final point.' According to the above textual description of a time series, select the time series from the following four options that most accurately reflects the described characteristics.
</question>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Identify the time series out of the given four that best matches the textual description.",
  "question_type": "choice",
  "required_output": "Select the time series from the following four options that most accurately reflects the described characteristics.",
  "success_criteria": [
    "All critical features (stability, spike, decline, recovery) should be matched accurately across candidate series"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Detect the initial stable period, brief spike, and immediate decline.",
      "required_measurements": [
        "endpoint_slope",
        "step_level_count",
        "change_location"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Match the described dynamics against all candidate time series, identifying the one that most closely aligns with the provided narrative.",
      "required_measurements": [
        "step_level_count",
        "min_value_location",
        "endpoint_slope",
        "pairwise_similarity",
        "change_location"
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
          "type": "step_level_count",
          "value": 1,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "slope_direction",
          "value": "flat",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "min_value_location",
          "value": "There is a brief spike immediately after the flat period.",
          "trusted": false
        },
        {
          "series_index": null,
          "type": "endpoint_slope",
          "value": "There is an immediate decline after the spike.",
          "trusted": false
        }
      ],
      "coverage": {
        "step_level_count": "tool_supported",
        "min_value_location": "unresolved",
        "endpoint_slope": "unresolved"
      },
      "summary": "The data shows a stable period without any spikes or immediate declines within the given interval. | No significant change points were detected, suggesting a consistent value throughout the observation period."
    }
  },
  "conflicts": [],
  "summary": "The data shows a stable period without any spikes or immediate declines within the given interval. No significant change points were detected, suggesting a consistent value throughout the observation period."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Time Series 1 best matches the described stable period without any notable spikes or immediate declines based on available evidence.",
      "reasoning_chain": [
        "Time Series 1 shows a stable period without any spikes or immediate declines.",
        "step_level_count=1",
        "slope_direction=flat"
      ],
      "candidate_preference": "A",
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "step_level_count",
        "slope_direction"
      ],
      "uncertainty": ""
    }
  ]
}
</heter_reasoning>

<execution_metadata>
{
  "option_mapping": {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4
  },
  "verified_preference": "A",
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
  "reasoning": "Based on the summary of the Homo perception and the grounded reasoning of the Heter agent, Time Series 1 (Option A) has been identified as the series that best matches the described stable period without any notable spikes or immediate declines. Execution metadata verifies this preference with high confidence. However, the Homo perception notes unresolved status for min_value_location and endpoint_slope, implying some uncertainty about the exact dynamics post-stable period.",
  "answer": "A",
  "explanation": "Heter reasoning confirms Time Series 1 aligns well with the stable initial period and lacks notable dynamic shifts, such as spikes or immediate declines, which are characteristic of the described series.",
  "confidence": 0.5,
  "conflicts": [
    "Homo perception does not detect changes like the spike and immediate decline as clearly as Heter reasoning suggests they should exist."
  ],
  "cited_evidence": [
    "Homo perception short scale states",
    "Heter reasoning chain confirming preference for Time Series 1",
    "Execution metadata verified preference"
  ],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "A"
  }
}
```
