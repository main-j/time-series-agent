# Agent IO summary: `Base:synthtic_qa_700:590`

- Architecture pred: `C` (success=True)
- model_calls=16, tool_calls=8, latency=237.3s

## Planner — `planner`

tokens prompt=1033 completion=471 latency=16.76s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 493 present a global maximum or minimum value or neither? (The index starts from 0)
</question>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

<metadata>
local_overall=local; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "To determine if point 493 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity (to confirm local extremeness) and the entire series (to confirm global extremeness).",
  "task_summary": "Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.",
  "target_output": "choice",
  "answer_type": "choice",
  "capability": "time-series analysis",
  "scope": "local",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Check the immediate neighborhood of point 493 for local extrema",
      "required_measurements": ["endpoint_slope", "pairwise_similarity"],
      "validation_requirements": ["Symmetry in comparison metrics"],
      "target_series": [1],
      "focus_intervals": [[491, 495]]
    },
    {
      "scale": "long",
      "objective": "Evaluate the entire time series to identify any potential global maxima or minima",
      "required_measurements": ["global_maximum_value", "global_minimum_value"],
      "validation_requirements": ["Consistency across series endpoints"],
      "target_series": [1],
      "focus_intervals": [[0, 703]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses",
      "required_measurements": ["endpoint_slope", "pairwise_similarity", "global_maximum_value", "global_minimum_value"],
      "validation_requirements": ["Agreement between short and long term perspectives"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Correct classification of point 493 based on comprehensive time series analysis"],
  "notes": "Ensure that point 493 is appropriately classified according to the criteria established by both short-term and long-term examination of the time series."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4066 completion=354 latency=13.83s

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
{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 493 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity (to confirm local extremeness) and the entire series (to confirm global extremeness).","task_summary":"Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]},{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","required_measurements":["endpoint_slope","pairwise_similarity","global_maximum_value","global_minimum_value"],"validation_requirements":["Agreement between short and long term perspectives"],"target_series":[1],"focus_intervals":[]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correct classification of point 493 based on comprehensive time series analysis"],"notes":"Ensure that point 493 is appropriately classified according to the criteria established by both short-term and long-term examination of the time series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity for verification of symmetry.",
  "evidence_plan": {
    "objective": "Check the immediate neighborhood of point 493 for local extrema",
    "claims_to_support": [
      {"claim": "Point 493 is a local extremum.", "required_evidence": ["local peak/trough"]},
      {"claim": "Endpoint slopes indicate consistent trend behavior around point 493.", "required_evidence": ["slope at 491", "slope at 495"]},
      {"claim": "Pairwise similarity metrics show symmetry around point 493.", "required_evidence": ["symmetric comparison"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[491,495]], "scale": "short"},
    "validation_needs": ["Symmetry in comparison metrics"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "local_extrema", "reason": "To determine local extrema near point 493.", "supports_evidence": ["local peak/trough"]},
      {"tool": "segment_trend", "reason": "To measure endpoint slopes indicating local behavior.", "supports_evidence": ["slope at 491", "slope at 495"]},
      {"tool": "interval_compare", "reason": "To assess symmetric comparison metrics around point 493.", "supports_evidence": ["symmetric comparison"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=845 completion=370 latency=13.16s

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
{"evidence_plan":{"objective":"Check the immediate neighborhood of point 493 for local extrema","claims_to_support":[{"claim":"Point 493 is a local extremum.","required_evidence":["local peak/trough"]},{"claim":"Endpoint slopes indicate consistent trend behavior around point 493.","required_evidence":["slope at 491","slope at 495"]},{"claim":"Pairwise similarity metrics show symmetry around point 493.","required_evidence":["symmetric comparison"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[491,495]],"scale":"short"},"validation_needs":["Symmetry in comparison metrics"]},"capability_selection":{"selected_tools":[{"tool":"local_extrema","reason":"To determine local extrema near point 493.","supports_evidence":["local peak/trough"]},{"tool":"segment_trend","reason":"To measure endpoint slopes indicating local behavior.","supports_evidence":["slope at 491","slope at 495"]},{"tool":"interval_compare","reason":"To assess symmetric comparison metrics around point 493.","supports_evidence":["symmetric comparison"]}],"no_tool_decision":null},"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity for verification of symmetry."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- local_extrema
  inputs: series_index, start, end
  outputs: series
- segment_trend
  inputs: series_index, start, end
  outputs: series
- interval_compare
  inputs: series_index, start, end, left_interval, right_interval, start/mid/end
  outputs: left/right
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'local_extrema' to find the local extrema near point 493. Then, 'segment_trend' is applied to measure the slopes at points 491 and 495, indicating the trend behavior around point 493. Finally, 'interval_compare' assesses symmetry by comparing intervals around point 493.",
  "workflow": [
    {
      "step": 1,
      "tool": "local_extrema",
      "output_key": "local_extrema_results",
      "input_binding": {"series_index": 1, "start": 491, "end": 495}
    },
    {
      "step": 2,
      "tool": "segment_trend",
      "output_key": "trend_at_491",
      "input_binding": {"series_index": 1, "start": 490, "end": 492}
    },
    {
      "step": 3,
      "tool": "segment_trend",
      "output_key": "trend_at_495",
      "input_binding": {"series_index": 1, "start": 494, "end": 496}
    },
    {
      "step": 4,
      "tool": "interval_compare",
      "output_key": "symmetry_metrics",
      "input_binding": {"series_index": 1, "start": 491, "end": 495, "left_interval": [491, 493], "right_interval": [493, 495], "start/mid/end": "mid"}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=1128 completion=329 latency=11.79s

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
{"workflow":[{"step":1,"tool":"local_extrema","output_key":"local_extrema_results","input_binding":{"series_index":1,"start":491,"end":495}},{"step":2,"tool":"segment_trend","output_key":"trend_at_491","input_binding":{"series_index":1,"start":490,"end":492}},{"step":3,"tool":"segment_trend","output_key":"trend_at_495","input_binding":{"series_index":1,"start":494,"end":496}},{"step":4,"tool":"interval_compare","output_key":"symmetry_metrics","input_binding":{"series_index":1,"start":491,"end":495,"left_interval":[491,493],"right_interval":[493,495],"start/mid/end":"mid"}}],"reasoning":"First, we use 'local_extrema' to find the local extrema near point 493. Then, 'segment_trend' is applied to measure the slopes at points 491 and 495, indicating the trend behavior around point 493. Finally, 'interval_compare' assesses symmetry by comparing intervals around point 493."}
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
- interval_compare: Compare left/right interval statistics on one series (mean/std/max/min/n_peaks/trend per side).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, left_interval=[start,end] inclusive, right_interval=[start,end] inclusive, start/mid/end=alt split mode}
  returns: {left/right=interval statistics, trends, extrema counts, and deltas}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to check the immediate neighborhood of point 493 for local extrema. The workflow involves finding local extrema near point 493, measuring trends at points 491 and 495, and then assessing symmetry between two intervals centered around point 493.",
  "calls": [
    {
      "step": 1,
      "tool": "local_extrema",
      "args": {
        "series_index": 1,
        "start": 491,
        "end": 495
      }
    },
    {
      "step": 2,
      "tool": "segment_trend",
      "args": {
        "series_index": 1,
        "start": 490,
        "end": 492
      }
    },
    {
      "step": 3,
      "tool": "segment_trend",
      "args": {
        "series_index": 1,
        "start": 494,
        "end": 496
      }
    },
    {
      "step": 4,
      "tool": "interval_compare",
      "args": {
        "series_index": 1,
        "start": 491,
        "end": 495,
        "left_interval": [491, 493],
        "right_interval": [493, 495],
        "start/mid/end": "mid"
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=2288 completion=612 latency=22.40s

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
{"evidence_plan":{"objective":"Check the immediate neighborhood of point 493 for local extrema","claims_to_support":[{"claim":"Point 493 is a local extremum.","required_evidence":["local peak/trough"]},{"claim":"Endpoint slopes indicate consistent trend behavior around point 493.","required_evidence":["slope at 491","slope at 495"]},{"claim":"Pairwise similarity metrics show symmetry around point 493.","required_evidence":["symmetric comparison"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[491,495]],"scale":"short"},"validation_needs":["Symmetry in comparison metrics"]},"capability_selection":{"selected_tools":[{"tool":"local_extrema","reason":"To determine local extrema near point 493.","supports_evidence":["local peak/trough"]},{"tool":"segment_trend","reason":"To measure endpoint slopes indicating local behavior.","supports_evidence":["slope at 491","slope at 495"]},{"tool":"interval_compare","reason":"To assess symmetric comparison metrics around point 493.","supports_evidence":["symmetric comparison"]}],"no_tool_decision":null},"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity for verification of symmetry."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "local_extrema",
    "arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "n_peaks": 1,
      "n_troughs": 0,
      "peak_idx": [
        493
      ],
      "trough_idx": []
    },
    "error": null,
    "args_fingerprint": "3ddebc3290090f861ef7500bb7db290a1204bfa8"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": 490,
      "end": 492
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 490,
      "end": 492
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 490,
      "end": 492,
      "slope": 0.120000000000001,
      "direction": "upward",
      "direction_class": "upward",
      "trend_method": "endpoint",
      "mean": 43.626666666666665,
      "std": 0.09843215373489013,
      "start_value": 43.5,
      "end_value": 43.74
    },
    "error": null,
    "args_fingerprint": "532a2d61a6faa5cc298e43178dda1aed3a5651a2"
  },
  {
    "call_id": "short:step3",
    "step": 3,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": 494,
      "end": 496
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 494,
      "end": 496
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 494,
      "end": 496,
      "slope": -0.09999999999999787,
      "direction": "downward",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 43.669999999999995,
      "std": 0.08286535263103845,
      "start_value": 43.76,
      "end_value": 43.56
    },
    "error": null,
    "args_fingerprint": "ebc1355a63ac37c392a9c73b2365db643fe5e2e7"
  },
  {
    "call_id": "short:step4",
    "step": 4,
    "tool_name": "interval_compare",
    "arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "left_interval": [
        491,
        493
      ],
      "right_interval": [
        493,
        495
      ],
      "start/mid/end": "mid"
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "left_interval": [
        491,
        493
      ],
      "right_interval": [
        493,
        495
      ],
      "start/mid/end": "mid"
    },
    "success": true,
    "data": {
      "series_index": 1,
      "mode": "pair",
      "left_interval": [
        491,
        493
      ],
      "right_interval": [
        493,
        495
      ],
      "left_mean": 43.72333333333333,
      "right_mean": 43.74666666666667,
      "left_std": 0.06236095644623198,
      "right_std": 0.041899350299922304,
      "left_max": 43.79,
      "right_max": 43.79,
      "left_min": 43.64,
      "right_min": 43.69,
      "left_max_index": 493,
      "right_max_index": 493,
      "left_n_peaks": 0,
      "right_n_peaks": 0,
      "left_n_troughs": 0,
      "right_n_troughs": 0,
      "left_direction": "upward",
      "right_direction": "downward",
      "left_slope": 0.07499999999999929,
      "right_slope": -0.05000000000000071,
      "mean_delta": 0.023333333333340533,
      "max_delta": 0.0,
      "same_trend_direction": false
    },
    "error": null,
    "args_fingerprint": "af64fdd6e045bac1d2cc63ff46acbe0cf69cea40"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Local extrema analysis around point 493 identified a single peak at that point. Endpoint slope measurements indicate an upward trend before and a vague downward trend after, which does not strongly support consistent behavior around the point. Pairwise comparison metrics reveal asymmetry in mean, standard deviation, and slope trends between intervals on either side of point 493.",
  "scale": "short",
  "observations": ["A peak was detected at point 493.", "Endpoint trends show weak symmetry.", "Metrics for comparison between intervals on each side of point 493 do not meet symmetry requirements."],
  "evidence_intervals": ["[491, 495]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Point 493 is a local extremum.",
      "evidence": [
        {
          "type": "local_peak",
          "value": 493,
          "source_tool": "local_extrema",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "local_peak"
    },
    {
      "claim": "Endpoint slopes indicate consistent trend behavior around point 493.",
      "evidence": [
        {
          "type": "slope_at_endpoint",
          "value": 0.12,
          "source_tool": "segment_trend",
          "call_id": "short:step2",
          "provenance": "tool"
        },
        {
          "type": "slope_at_endpoint",
          "value": -0.1,
          "source_tool": "segment_trend",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "qualified",
      "maps_to_measurement": "slope_at_endpoint"
    },
    {
      "claim": "Pairwise similarity metrics show symmetry around point 493.",
      "evidence": [
        {
          "type": "pairwise_comparisons",
          "value": {
            "same_trend_direction": false,
            "mean_delta": 0.023333333333340533
          },
          "source_tool": "interval_compare",
          "call_id": "short:step4",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {"local_peak": "tool_supported", "slope_at_endpoint": "tool_supported", "pairwise_similarity": "unresolved"},
  "unresolved_claims": ["Pairwise similarity metrics show symmetry around point 493."]
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m1`

tokens prompt=4092 completion=351 latency=13.71s

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
{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 493 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity (to confirm local extremeness) and the entire series (to confirm global extremeness).","task_summary":"Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]},{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","required_measurements":["endpoint_slope","pairwise_similarity","global_maximum_value","global_minimum_value"],"validation_requirements":["Agreement between short and long term perspectives"],"target_series":[1],"focus_intervals":[]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correct classification of point 493 based on comprehensive time series analysis"],"notes":"Ensure that point 493 is appropriately classified according to the criteria established by both short-term and long-term examination of the time series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['Pairwise similarity metrics show symmetry around point 493.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. Validation will ensure symmetry in comparison metrics.",
  "evidence_plan": {
    "objective": "Check the immediate neighborhood of point 493 for local extrema",
    "claims_to_support": [
      {"claim": "Point 493 has local extrema", "required_evidence": ["local_extrema_count"]},
      {"claim": "Endpoint slopes indicate behavior around point 493", "required_evidence": ["endpoint_slope"]},
      {"claim": "Pairwise similarity metrics show symmetry around point 493", "required_evidence": ["pairwise_similarity"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[491,495]], "scale": "short"},
    "validation_needs": ["Symmetry in comparison metrics"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "local_extrema", "reason": "Detect local peak/trough locations in the immediate neighborhood of point 493.", "supports_evidence": ["local_extrema_count"]},
      {"tool": "diff_stats", "reason": "Measure the first-difference statistics to infer endpoint slopes around point 493.", "supports_evidence": ["endpoint_slope"]},
      {"tool": "interval_compare", "reason": "Compare left/right interval statistics around point 493 to ensure symmetry in pairwise similarity metrics.", "supports_evidence": ["pairwise_similarity"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m1`

tokens prompt=843 completion=305 latency=10.84s

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
{"evidence_plan":{"objective":"Check the immediate neighborhood of point 493 for local extrema","claims_to_support":[{"claim":"Point 493 has local extrema","required_evidence":["local_extrema_count"]},{"claim":"Endpoint slopes indicate behavior around point 493","required_evidence":["endpoint_slope"]},{"claim":"Pairwise similarity metrics show symmetry around point 493","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[491,495]],"scale":"short"},"validation_needs":["Symmetry in comparison metrics"]},"capability_selection":{"selected_tools":[{"tool":"local_extrema","reason":"Detect local peak/trough locations in the immediate neighborhood of point 493.","supports_evidence":["local_extrema_count"]},{"tool":"diff_stats","reason":"Measure the first-difference statistics to infer endpoint slopes around point 493.","supports_evidence":["endpoint_slope"]},{"tool":"interval_compare","reason":"Compare left/right interval statistics around point 493 to ensure symmetry in pairwise similarity metrics.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. Validation will ensure symmetry in comparison metrics."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- diff_stats
  inputs: series_index, start, end
  outputs: series
- local_extrema
  inputs: series_index, start, end
  outputs: series
- interval_compare
  inputs: series_index, start, end, left_interval, right_interval, start/mid/end
  outputs: left/right
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. First, we detect local extrema using 'local_extrema', then measure first-difference statistics using 'diff_stats' to infer endpoint slopes, and finally compare left/right interval statistics around point 493 with 'interval_compare'. This ensures symmetry in comparison metrics.",
  "workflow": [
    {
      "step": 1,
      "tool": "local_extrema",
      "output_key": "local_extrema_result",
      "input_binding": {"series_index": 1, "start": 491, "end": 495}
    },
    {
      "step": 2,
      "tool": "diff_stats",
      "output_key": "endpoint_slope_result",
      "input_binding": {"series_index": 1, "start": 491, "end": 495}
    },
    {
      "step": 3,
      "tool": "interval_compare",
      "output_key": "pairwise_similarity_result",
      "input_binding": {"series_index": 1, "start": 491, "end": 495, "left_interval": [491, 492], "right_interval": [494, 495], "mid": 493}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m1`

tokens prompt=1078 completion=273 latency=9.94s

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
{"workflow":[{"step":1,"tool":"local_extrema","output_key":"local_extrema_result","input_binding":{"series_index":1,"start":491,"end":495}},{"step":2,"tool":"diff_stats","output_key":"endpoint_slope_result","input_binding":{"series_index":1,"start":491,"end":495}},{"step":3,"tool":"interval_compare","output_key":"pairwise_similarity_result","input_binding":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493}}],"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. First, we detect local extrema using 'local_extrema', then measure first-difference statistics using 'diff_stats' to infer endpoint slopes, and finally compare left/right interval statistics around point 493 with 'interval_compare'. This ensures symmetry in comparison metrics."}
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

- diff_stats: First-difference stats and sign changes.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series first-difference mean/std/range and sign changes}
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
- interval_compare: Compare left/right interval statistics on one series (mean/std/max/min/n_peaks/trend per side).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, left_interval=[start,end] inclusive, right_interval=[start,end] inclusive, start/mid/end=alt split mode}
  returns: {left/right=interval statistics, trends, extrema counts, and deltas}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Check the immediate neighborhood of point 493 for local extrema and perform required measurements such as endpoint slope and pairwise similarity as specified in the assignment. The workflow involves detecting local extrema, calculating first difference statistics to infer endpoint slopes, and comparing left-right interval statistics around point 493.",
  "calls": [
    {
      "step": 1,
      "tool": "local_extrema",
      "args": {
        "series_index": 1,
        "start": 491,
        "end": 495
      }
    },
    {
      "step": 2,
      "tool": "diff_stats",
      "args": {
        "series_index": 1,
        "start": 491,
        "end": 495
      }
    },
    {
      "step": 3,
      "tool": "interval_compare",
      "args": {
        "series_index": 1,
        "start": 491,
        "end": 495,
        "left_interval": [491, 492],
        "right_interval": [494, 495],
        "mid": 493
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m1`

tokens prompt=1946 completion=654 latency=23.82s

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
{"evidence_plan":{"objective":"Check the immediate neighborhood of point 493 for local extrema","claims_to_support":[{"claim":"Point 493 has local extrema","required_evidence":["local_extrema_count"]},{"claim":"Endpoint slopes indicate behavior around point 493","required_evidence":["endpoint_slope"]},{"claim":"Pairwise similarity metrics show symmetry around point 493","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[491,495]],"scale":"short"},"validation_needs":["Symmetry in comparison metrics"]},"capability_selection":{"selected_tools":[{"tool":"local_extrema","reason":"Detect local peak/trough locations in the immediate neighborhood of point 493.","supports_evidence":["local_extrema_count"]},{"tool":"diff_stats","reason":"Measure the first-difference statistics to infer endpoint slopes around point 493.","supports_evidence":["endpoint_slope"]},{"tool":"interval_compare","reason":"Compare left/right interval statistics around point 493 to ensure symmetry in pairwise similarity metrics.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. Validation will ensure symmetry in comparison metrics."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "local_extrema",
    "arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "n_peaks": 1,
      "n_troughs": 0,
      "peak_idx": [
        493
      ],
      "trough_idx": []
    },
    "error": null,
    "args_fingerprint": "3ddebc3290090f861ef7500bb7db290a1204bfa8"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "diff_stats",
    "arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "mean_diff": 0.01249999999999929,
      "std_diff": 0.066473679001542,
      "max_abs_diff": 0.10000000000000142,
      "n_sign_changes": 1
    },
    "error": null,
    "args_fingerprint": "e3e11213c76dba0c44ab99adc3d19bb69f82bc50"
  },
  {
    "call_id": "short:step3",
    "step": 3,
    "tool_name": "interval_compare",
    "arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "left_interval": [
        491,
        492
      ],
      "right_interval": [
        494,
        495
      ],
      "mid": 493
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 491,
      "end": 495,
      "left_interval": [
        491,
        492
      ],
      "right_interval": [
        494,
        495
      ],
      "mid": 493
    },
    "success": true,
    "data": {
      "series_index": 1,
      "mode": "pair",
      "left_interval": [
        491,
        492
      ],
      "right_interval": [
        494,
        495
      ],
      "left_mean": 43.69,
      "right_mean": 43.724999999999994,
      "left_std": 0.05000000000000071,
      "right_std": 0.03500000000000014,
      "left_max": 43.74,
      "right_max": 43.76,
      "left_min": 43.64,
      "right_min": 43.69,
      "left_max_index": 492,
      "right_max_index": 494,
      "left_n_peaks": 0,
      "right_n_peaks": 0,
      "left_n_troughs": 0,
      "right_n_troughs": 0,
      "left_direction": "upward",
      "right_direction": "downward",
      "left_slope": 0.10000000000000142,
      "right_slope": -0.07000000000000028,
      "mean_delta": 0.03499999999999659,
      "max_delta": 0.01999999999999602,
      "same_trend_direction": false
    },
    "error": null,
    "args_fingerprint": "70647c6221d7fce3f835da379bbf2e361a35e25d"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective was to check the immediate neighborhood of point 493 for local extrema, measure endpoint slopes, and evaluate pairwise similarity metrics to ensure symmetry. Local extrema analysis confirmed that point 493 has a peak, but there are no troughs within the specified range. Endpoint slopes show different trends on either side of the midpoint, indicating an asymmetry which contradicts the expected validation requirement of symmetry.",
  "scale": "short",
  "observations": ["Point 493 is identified as having a local peak.", "Endpoint slopes differ, suggesting asymmetry around point 493.", "Pairwise comparison metrics also indicate asymmetry around point 493."],
  "evidence_intervals": ["The neighborhood of point 493 includes points 491 to 495."],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Point 493 has a local peak.",
      "evidence": [
        {
          "type": "local_extrema_count",
          "value": 1,
          "source_tool": "local_extrema",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "local_extrema_count"
    },
    {
      "claim": "Endpoint slopes are asymmetric around point 493.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": {
            "left_slope": 0.10000000000000142,
            "right_slope": -0.07000000000000028,
            "same_trend_direction": false
          },
          "source_tool": "diff_stats",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "endpoint_slope"
    },
    {
      "claim": "Pairwise similarity metrics show asymmetry around point 493.",
      "evidence": [
        {
          "type": "pairwise_similarity",
          "value": {
            "mean_delta": 0.03499999999999659,
            "max_delta": 0.01999999999999602,
            "same_trend_direction": false
          },
          "source_tool": "interval_compare",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {"local_extrema_count": "tool_supported", "endpoint_slope": "tool_supported", "pairwise_similarity": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4066 completion=296 latency=11.72s

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
{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 493 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity (to confirm local extremeness) and the entire series (to confirm global extremeness).","task_summary":"Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]},{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","required_measurements":["endpoint_slope","pairwise_similarity","global_maximum_value","global_minimum_value"],"validation_requirements":["Agreement between short and long term perspectives"],"target_series":[1],"focus_intervals":[]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correct classification of point 493 based on comprehensive time series analysis"],"notes":"Ensure that point 493 is appropriately classified according to the criteria established by both short-term and long-term examination of the time series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to evaluate the entire time series to identify any potential global maxima or minima, with a focus on ensuring consistency across series endpoints. To achieve this, we need to retrieve the global maximum and minimum values from the entire series.",
  "evidence_plan": {
    "objective": "Evaluate the entire time series to identify any potential global maxima or minima",
    "claims_to_support": [
      {
        "claim": "Identify the global maximum value in the entire series",
        "required_evidence": ["global_maximum_value"]
      },
      {
        "claim": "Identify the global minimum value in the entire series",
        "required_evidence": ["global_minimum_value"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[0, 703]],
      "scale": "long"
    },
    "validation_needs": ["Consistency across series endpoints"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "global_extrema",
        "reason": "This tool is used to identify global extrema values and their locations, which is necessary for validating the global maximum and minimum values across the series endpoints.",
        "supports_evidence": ["global_maximum_value", "global_minimum_value"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=739 completion=110 latency=3.97s

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
{"evidence_plan":{"objective":"Evaluate the entire time series to identify any potential global maxima or minima","claims_to_support":[{"claim":"Identify the global maximum value in the entire series","required_evidence":["global_maximum_value"]},{"claim":"Identify the global minimum value in the entire series","required_evidence":["global_minimum_value"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,703]],"scale":"long"},"validation_needs":["Consistency across series endpoints"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"This tool is used to identify global extrema values and their locations, which is necessary for validating the global maximum and minimum values across the series endpoints.","supports_evidence":["global_maximum_value","global_minimum_value"]}],"no_tool_decision":null},"reasoning":"The objective is to evaluate the entire time series to identify any potential global maxima or minima, with a focus on ensuring consistency across series endpoints. To achieve this, we need to retrieve the global maximum and minimum values from the entire series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- global_extrema
  inputs: series_index, start, end, index, index_base
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "Given the objective of identifying global maxima and minima values in the entire series, the 'global_extrema' tool is chosen as it provides the necessary functionality to detect these points. Since there are no other tools involved, the workflow will consist of a single step utilizing 'global_extrema'.",
  "workflow": [
    {
      "step": 1,
      "tool": "global_extrema",
      "output_key": "series",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=793 completion=115 latency=4.16s

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
{"workflow":[{"step":1,"tool":"global_extrema","output_key":"series","input_binding":{}}],"reasoning":"Given the objective of identifying global maxima and minima values in the entire series, the 'global_extrema' tool is chosen as it provides the necessary functionality to detect these points. Since there are no other tools involved, the workflow will consist of a single step utilizing 'global_extrema'."}
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

- global_extrema: Global max/min indices and values; optional index classifies a point as global/local peak/trough (Base index tasks).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, index=optional int; if set, classify that index (global_extrema), index_base=0 (default) or 1}
  returns: {series=per-series max/min values and indices plus optional queried-index flags}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to evaluate the entire time series to identify any potential global maxima or minima. Given the single-step workflow specified, we use the 'global_extrema' tool with appropriate parameters.",
  "calls": [
    {
      "step": 1,
      "tool": "global_extrema",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 703,
        "index_base": 1
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1087 completion=414 latency=14.79s

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
{"evidence_plan":{"objective":"Evaluate the entire time series to identify any potential global maxima or minima","claims_to_support":[{"claim":"Identify the global maximum value in the entire series","required_evidence":["global_maximum_value"]},{"claim":"Identify the global minimum value in the entire series","required_evidence":["global_minimum_value"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,703]],"scale":"long"},"validation_needs":["Consistency across series endpoints"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"This tool is used to identify global extrema values and their locations, which is necessary for validating the global maximum and minimum values across the series endpoints.","supports_evidence":["global_maximum_value","global_minimum_value"]}],"no_tool_decision":null},"reasoning":"The objective is to evaluate the entire time series to identify any potential global maxima or minima, with a focus on ensuring consistency across series endpoints. To achieve this, we need to retrieve the global maximum and minimum values from the entire series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
    "step": 1,
    "tool_name": "global_extrema",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 703,
      "index_base": 1
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 703,
      "index_base": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 703,
      "max_index": 584,
      "min_index": 145,
      "max_value": 65.87,
      "min_value": -70.6,
      "n_peaks": 5,
      "n_troughs": 6,
      "peak_indices": [
        99,
        195,
        493,
        584,
        676
      ],
      "trough_indices": [
        56,
        145,
        234,
        526,
        634,
        637
      ]
    },
    "error": null,
    "args_fingerprint": "441770107ed0c461a234a5dcdc3b6438b2ff29c4"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective was to evaluate the entire time series to identify any potential global maxima or minima. Using the 'global_extrema' tool, we identified the global maximum value as 65.87 at index 584 and the global minimum value as -70.6 at index 145. This data provides evidence to support the claims of identifying global extrema values.",
  "scale": "long",
  "observations": ["Global maximum value in the series is 65.87 at index 584.", "Global minimum value in the series is -70.6 at index 145."],
  "evidence_intervals": ["[0, 703]"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Identify the global maximum value in the entire series",
      "evidence": [
        {
          "type": "global_maximum_value",
          "value": 65.87,
          "source_tool": "global_extrema",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_maximum_value"
    },
    {
      "claim": "Identify the global minimum value in the entire series",
      "evidence": [
        {
          "type": "global_minimum_value",
          "value": -70.6,
          "source_tool": "global_extrema",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_minimum_value"
    }
  ],
  "coverage": {"global_maximum_value": "tool_supported", "global_minimum_value": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=8829 completion=615 latency=26.06s

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
{"role":"reasoning","objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","required_measurements":["endpoint_slope","pairwise_similarity","global_maximum_value","global_minimum_value"],"validation_requirements":["Agreement between short and long term perspectives"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 493 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity (to confirm local extremeness) and the entire series (to confirm global extremeness).","task_summary":"Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Check the immediate neighborhood of point 493 for local extrema","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Symmetry in comparison metrics"],"target_series":[1],"focus_intervals":[[491,495]]},{"scale":"long","objective":"Evaluate the entire time series to identify any potential global maxima or minima","required_measurements":["global_maximum_value","global_minimum_value"],"validation_requirements":["Consistency across series endpoints"],"target_series":[1],"focus_intervals":[[0,703]]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","required_measurements":["endpoint_slope","pairwise_similarity","global_maximum_value","global_minimum_value"],"validation_requirements":["Agreement between short and long term perspectives"],"target_series":[1],"focus_intervals":[]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correct classification of point 493 based on comprehensive time series analysis"],"notes":"Ensure that point 493 is appropriately classified according to the criteria established by both short-term and long-term examination of the time series."}
</plan_context>

<task_summary>
Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The objective was to check the immediate neighborhood of point 493 for local extrema, measure endpoint slopes, and evaluate pairwise similarity metrics to ensure symmetry. Local extrema analysis confirmed that point 493 has a peak, but there are no troughs within the specified range. Endpoint slopes show different trends on either side of the midpoint, indicating an asymmetry which contradicts the expected validation requirement of symmetry.","scale":"short","observations":["Point 493 is identified as having a local peak.","Endpoint slopes differ, suggesting asymmetry around point 493.","Pairwise comparison metrics also indicate asymmetry around point 493."],"evidence_intervals":["The neighborhood of point 493 includes points 491 to 495."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"n_peaks\": 1, \"n_troughs\": 0, \"peak_idx\": [493], \"trough_idx\": []}, \"error\": null, \"args_fingerprint\": \"3ddebc3290090f861ef7500bb7db290a1204bfa8\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"mean_diff\": 0.01249999999999929, \"std_diff\": 0.066473679001542, \"max_abs_diff\": 0.10000000000000142, \"n_sign_changes\": 1}, \"error\": null, \"args_fingerprint\": \"e3e11213c76dba0c44ab99adc3d19bb69f82bc50\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"interval_compare\", \"arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"left_interval\": [491, 492], \"right_interval\": [494, 495], \"mid\": 493}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"left_interval\": [491, 492], \"right_interval\": [494, 495], \"mid\": 493}, \"success\": true, \"data\": {\"series_index\": 1, \"mode\": \"pair\", \"left_interval\": [491, 492], \"right_interval\": [494, 495], \"left_mean\": 43.69, \"right_mean\": 43.724999999999994, \"left_std\": 0.05000000000000071, \"right_std\": 0.03500000000000014, \"left_max\": 43.74, \"right_max\": 43.76, \"left_min\": 43.64, \"right_min\": 43.69, \"left_max_index\": 492, \"right_max_index\": 494, \"left_n_peaks\": 0, \"right_n_peaks\": 0, \"left_n_troughs\": 0, \"right_n_troughs\": 0, \"left_direction\": \"upward\", \"right_direction\": \"downward\", \"left_slope\": 0.10000000000000142, \"right_slope\": -0.07000000000000028, \"mean_delta\": 0.03499999999999659, \"max_delta\": 0.01999999999999602, \"same_trend_direction\": false}, \"error\": null, \"args_fingerprint\": \"70647c6221d7fce3f835da379bbf2e361a35e25d\"}"],"evidence_plan":{"objective":"Check the immediate neighborhood of point 493 for local extrema","claims_to_support":[{"claim":"Point 493 has local extrema","required_evidence":["local_extrema_count"]},{"claim":"Endpoint slopes indicate behavior around point 493","required_evidence":["endpoint_slope"]},{"claim":"Pairwise similarity metrics show symmetry around point 493","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[491,495]],"scale":"short"},"validation_needs":["Symmetry in comparison metrics"]},"capability_selection":{"selected_tools":[{"tool":"local_extrema","reason":"Detect local peak/trough locations in the immediate neighborhood of point 493.","supports_evidence":["local_extrema_count"]},{"tool":"diff_stats","reason":"Measure the first-difference statistics to infer endpoint slopes around point 493.","supports_evidence":["endpoint_slope"]},{"tool":"interval_compare","reason":"Compare left/right interval statistics around point 493 to ensure symmetry in pairwise similarity metrics.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"local_extrema","output_key":"local_extrema_result","input_binding":{"series_index":1,"start":491,"end":495}},{"step":2,"tool":"diff_stats","output_key":"endpoint_slope_result","input_binding":{"series_index":1,"start":491,"end":495}},{"step":3,"tool":"interval_compare","output_key":"pairwise_similarity_result","input_binding":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493}}],"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. First, we detect local extrema using 'local_extrema', then measure first-difference statistics using 'diff_stats' to infer endpoint slopes, and finally compare left/right interval statistics around point 493 with 'interval_compare'. This ensures symmetry in comparison metrics."},"structured_observations":[{"claim":"Point 493 has a local peak.","evidence":[{"type":"local_extrema_count","value":1,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_extrema_count"},{"claim":"Endpoint slopes are asymmetric around point 493.","evidence":[{"type":"endpoint_slope","value":{"left_slope":0.10000000000000142,"right_slope":-0.07000000000000028,"same_trend_direction":false},"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity metrics show asymmetry around point 493.","evidence":[{"type":"pairwise_similarity","value":{"mean_delta":0.03499999999999659,"max_delta":0.01999999999999602,"same_trend_direction":false},"source_tool":"interval_compare","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"coverage":{"local_extrema_count":"tool_supported","endpoint_slope":"tool_supported","pairwise_similarity":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"local_extrema","arguments":{"series_index":1,"start":491,"end":495},"resolved_arguments":{"series_index":1,"start":491,"end":495},"success":true,"data":{"series_index":1,"start":491,"end":495,"n_peaks":1,"n_troughs":0,"peak_idx":[493],"trough_idx":[]},"error":null,"args_fingerprint":"3ddebc3290090f861ef7500bb7db290a1204bfa8"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1,"start":491,"end":495},"resolved_arguments":{"series_index":1,"start":491,"end":495},"success":true,"data":{"series_index":1,"start":491,"end":495,"mean_diff":0.01249999999999929,"std_diff":0.066473679001542,"max_abs_diff":0.10000000000000142,"n_sign_changes":1},"error":null,"args_fingerprint":"e3e11213c76dba0c44ab99adc3d19bb69f82bc50"},{"call_id":"short:step3","step":3,"tool_name":"interval_compare","arguments":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493},"resolved_arguments":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493},"success":true,"data":{"series_index":1,"mode":"pair","left_interval":[491,492],"right_interval":[494,495],"left_mean":43.69,"right_mean":43.724999999999994,"left_std":0.05000000000000071,"right_std":0.03500000000000014,"left_max":43.74,"right_max":43.76,"left_min":43.64,"right_min":43.69,"left_max_index":492,"right_max_index":494,"left_n_peaks":0,"right_n_peaks":0,"left_n_troughs":0,"right_n_troughs":0,"left_direction":"upward","right_direction":"downward","left_slope":0.10000000000000142,"right_slope":-0.07000000000000028,"mean_delta":0.03499999999999659,"max_delta":0.01999999999999602,"same_trend_direction":false},"error":null,"args_fingerprint":"70647c6221d7fce3f835da379bbf2e361a35e25d"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The objective was to evaluate the entire time series to identify any potential global maxima or minima. Using the 'global_extrema' tool, we identified the global maximum value as 65.87 at index 584 and the global minimum value as -70.6 at index 145. This data provides evidence to support the claims of identifying global extrema values.","scale":"long","observations":["Global maximum value in the series is 65.87 at index 584.","Global minimum value in the series is -70.6 at index 145."],"evidence_intervals":["[0, 703]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 703, \"index_base\": 1}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 703, \"index_base\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 703, \"max_index\": 584, \"min_index\": 145, \"max_value\": 65.87, \"min_value\": -70.6, \"n_peaks\": 5, \"n_troughs\": 6, \"peak_indices\": [99, 195, 493, 584, 676], \"trough_indices\": [56, 145, 234, 526, 634, 637]}, \"error\": null, \"args_fingerprint\": \"441770107ed0c461a234a5dcdc3b6438b2ff29c4\"}"],"evidence_plan":{"objective":"Evaluate the entire time series to identify any potential global maxima or minima","claims_to_support":[{"claim":"Identify the global maximum value in the entire series","required_evidence":["global_maximum_value"]},{"claim":"Identify the global minimum value in the entire series","required_evidence":["global_minimum_value"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,703]],"scale":"long"},"validation_needs":["Consistency across series endpoints"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"This tool is used to identify global extrema values and their locations, which is necessary for validating the global maximum and minimum values across the series endpoints.","supports_evidence":["global_maximum_value","global_minimum_value"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"global_extrema","output_key":"series","input_binding":{}}],"reasoning":"Given the objective of identifying global maxima and minima values in the entire series, the 'global_extrema' tool is chosen as it provides the necessary functionality to detect these points. Since there are no other tools involved, the workflow will consist of a single step utilizing 'global_extrema'."},"structured_observations":[{"claim":"Identify the global maximum value in the entire series","evidence":[{"type":"global_maximum_value","value":65.87,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum_value"},{"claim":"Identify the global minimum value in the entire series","evidence":[{"type":"global_minimum_value","value":-70.6,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum_value"}],"coverage":{"global_maximum_value":"tool_supported","global_minimum_value":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":703,"index_base":1},"resolved_arguments":{"series_index":1,"start":0,"end":703,"index_base":1},"success":true,"data":{"series_index":1,"start":0,"end":703,"max_index":584,"min_index":145,"max_value":65.87,"min_value":-70.6,"n_peaks":5,"n_troughs":6,"peak_indices":[99,195,493,584,676],"trough_indices":[56,145,234,526,634,637]},"error":null,"args_fingerprint":"441770107ed0c461a234a5dcdc3b6438b2ff29c4"}],"skipped_stages":[]},"conflicts":[],"summary":"Point 493 is identified as having a local peak. Endpoint slopes differ, suggesting asymmetry around point 493. Pairwise comparison metrics also indicate asymmetry around point 493. Global maximum value in the series is 65.87 at index 584. Global minimum value in the series is -70.6 at index 145.","structured_by_scale":{"short":[{"claim":"Point 493 has a local peak.","evidence":[{"type":"local_extrema_count","value":1,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_extrema_count"},{"claim":"Endpoint slopes are asymmetric around point 493.","evidence":[{"type":"endpoint_slope","value":{"left_slope":0.10000000000000142,"right_slope":-0.07000000000000028,"same_trend_direction":false},"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity metrics show asymmetry around point 493.","evidence":[{"type":"pairwise_similarity","value":{"mean_delta":0.03499999999999659,"max_delta":0.01999999999999602,"same_trend_direction":false},"source_tool":"interval_compare","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"Identify the global maximum value in the entire series","evidence":[{"type":"global_maximum_value","value":65.87,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum_value"},{"claim":"Identify the global minimum value in the entire series","evidence":[{"type":"global_minimum_value","value":-70.6,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum_value"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
```json
{
  "reasoning": "To determine if point 493 qualifies as a global maximum, minimum, or neither, we have evidence of a local maximum around point 493 based on the short-term analysis. However, the long-term analysis shows that the global maximum is at index 584 with a value of 65.87, and the global minimum is at index 145 with a value of -70.6. Therefore, point 493 is a local maximum but not a global maximum or minimum.",
  "evidence_plan": {
    "objective": "Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses",
    "claims_to_support": [
      {
        "claim": "Point 493 has a local maximum",
        "required_evidence": ["local_extrema_count"]
      },
      {
        "claim": "Endpoint slopes differ around point 493",
        "required_evidence": ["endpoint_slope"]
      },
      {
        "claim": "Pairwise similarity metrics show asymmetry around point 493",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "Global maximum is at index 584 with value 65.87",
        "required_evidence": ["global_maximum_value"]
      },
      {
        "claim": "Global minimum is at index 145 with value -70.6",
        "required_evidence": ["global_minimum_value"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "reasoning"
    },
    "validation_needs": ["Agreement between short and long term perspectives"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All required evidence for the claims has been provided by the previous tools (local_extrema, diff_stats, interval_compare, global_extrema)",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "short:step1",
          "field": "local_extrema_count"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step2",
          "field": "endpoint_slope"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step3",
          "field": "pairwise_similarity"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_maximum_value"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_minimum_value"
        }
      ]
    }
  }
}
```
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=5648 completion=751 latency=29.59s

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
{"evidence_plan":{"objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","claims_to_support":[{"claim":"Point 493 has a local maximum","required_evidence":["local_extrema_count"]},{"claim":"Endpoint slopes differ around point 493","required_evidence":["endpoint_slope"]},{"claim":"Pairwise similarity metrics show asymmetry around point 493","required_evidence":["pairwise_similarity"]},{"claim":"Global maximum is at index 584 with value 65.87","required_evidence":["global_maximum_value"]},{"claim":"Global minimum is at index 145 with value -70.6","required_evidence":["global_minimum_value"]}],"analysis_scope":{"target_series":[1],"role":"reasoning"},"validation_needs":["Agreement between short and long term perspectives"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All required evidence for the claims has been provided by the previous tools (local_extrema, diff_stats, interval_compare, global_extrema)","evidence_sources":[{"type":"upstream_observation","ref":"short:step1","field":"local_extrema_count"},{"type":"upstream_observation","ref":"short:step2","field":"endpoint_slope"},{"type":"upstream_observation","ref":"short:step3","field":"pairwise_similarity"},{"type":"upstream_observation","ref":"long:step1","field":"global_maximum_value"},{"type":"upstream_observation","ref":"long:step1","field":"global_minimum_value"}]}},"reasoning":"To determine if point 493 qualifies as a global maximum, minimum, or neither, we have evidence of a local maximum around point 493 based on the short-term analysis. However, the long-term analysis shows that the global maximum is at index 584 with a value of 65.87, and the global minimum is at index 145 with a value of -70.6. Therefore, point 493 is a local maximum but not a global maximum or minimum."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The objective was to check the immediate neighborhood of point 493 for local extrema, measure endpoint slopes, and evaluate pairwise similarity metrics to ensure symmetry. Local extrema analysis confirmed that point 493 has a peak, but there are no troughs within the specified range. Endpoint slopes show different trends on either side of the midpoint, indicating an asymmetry which contradicts the expected validation requirement of symmetry.","scale":"short","observations":["Point 493 is identified as having a local peak.","Endpoint slopes differ, suggesting asymmetry around point 493.","Pairwise comparison metrics also indicate asymmetry around point 493."],"evidence_intervals":["The neighborhood of point 493 includes points 491 to 495."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"n_peaks\": 1, \"n_troughs\": 0, \"peak_idx\": [493], \"trough_idx\": []}, \"error\": null, \"args_fingerprint\": \"3ddebc3290090f861ef7500bb7db290a1204bfa8\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"mean_diff\": 0.01249999999999929, \"std_diff\": 0.066473679001542, \"max_abs_diff\": 0.10000000000000142, \"n_sign_changes\": 1}, \"error\": null, \"args_fingerprint\": \"e3e11213c76dba0c44ab99adc3d19bb69f82bc50\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"interval_compare\", \"arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"left_interval\": [491, 492], \"right_interval\": [494, 495], \"mid\": 493}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 491, \"end\": 495, \"left_interval\": [491, 492], \"right_interval\": [494, 495], \"mid\": 493}, \"success\": true, \"data\": {\"series_index\": 1, \"mode\": \"pair\", \"left_interval\": [491, 492], \"right_interval\": [494, 495], \"left_mean\": 43.69, \"right_mean\": 43.724999999999994, \"left_std\": 0.05000000000000071, \"right_std\": 0.03500000000000014, \"left_max\": 43.74, \"right_max\": 43.76, \"left_min\": 43.64, \"right_min\": 43.69, \"left_max_index\": 492, \"right_max_index\": 494, \"left_n_peaks\": 0, \"right_n_peaks\": 0, \"left_n_troughs\": 0, \"right_n_troughs\": 0, \"left_direction\": \"upward\", \"right_direction\": \"downward\", \"left_slope\": 0.10000000000000142, \"right_slope\": -0.07000000000000028, \"mean_delta\": 0.03499999999999659, \"max_delta\": 0.01999999999999602, \"same_trend_direction\": false}, \"error\": null, \"args_fingerprint\": \"70647c6221d7fce3f835da379bbf2e361a35e25d\"}"],"evidence_plan":{"objective":"Check the immediate neighborhood of point 493 for local extrema","claims_to_support":[{"claim":"Point 493 has local extrema","required_evidence":["local_extrema_count"]},{"claim":"Endpoint slopes indicate behavior around point 493","required_evidence":["endpoint_slope"]},{"claim":"Pairwise similarity metrics show symmetry around point 493","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[491,495]],"scale":"short"},"validation_needs":["Symmetry in comparison metrics"]},"capability_selection":{"selected_tools":[{"tool":"local_extrema","reason":"Detect local peak/trough locations in the immediate neighborhood of point 493.","supports_evidence":["local_extrema_count"]},{"tool":"diff_stats","reason":"Measure the first-difference statistics to infer endpoint slopes around point 493.","supports_evidence":["endpoint_slope"]},{"tool":"interval_compare","reason":"Compare left/right interval statistics around point 493 to ensure symmetry in pairwise similarity metrics.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"local_extrema","output_key":"local_extrema_result","input_binding":{"series_index":1,"start":491,"end":495}},{"step":2,"tool":"diff_stats","output_key":"endpoint_slope_result","input_binding":{"series_index":1,"start":491,"end":495}},{"step":3,"tool":"interval_compare","output_key":"pairwise_similarity_result","input_binding":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493}}],"reasoning":"The objective requires checking the immediate neighborhood of point 493 for local extrema and measuring endpoint slopes and pairwise similarity. First, we detect local extrema using 'local_extrema', then measure first-difference statistics using 'diff_stats' to infer endpoint slopes, and finally compare left/right interval statistics around point 493 with 'interval_compare'. This ensures symmetry in comparison metrics."},"structured_observations":[{"claim":"Point 493 has a local peak.","evidence":[{"type":"local_extrema_count","value":1,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_extrema_count"},{"claim":"Endpoint slopes are asymmetric around point 493.","evidence":[{"type":"endpoint_slope","value":{"left_slope":0.10000000000000142,"right_slope":-0.07000000000000028,"same_trend_direction":false},"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity metrics show asymmetry around point 493.","evidence":[{"type":"pairwise_similarity","value":{"mean_delta":0.03499999999999659,"max_delta":0.01999999999999602,"same_trend_direction":false},"source_tool":"interval_compare","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"coverage":{"local_extrema_count":"tool_supported","endpoint_slope":"tool_supported","pairwise_similarity":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"local_extrema","arguments":{"series_index":1,"start":491,"end":495},"resolved_arguments":{"series_index":1,"start":491,"end":495},"success":true,"data":{"series_index":1,"start":491,"end":495,"n_peaks":1,"n_troughs":0,"peak_idx":[493],"trough_idx":[]},"error":null,"args_fingerprint":"3ddebc3290090f861ef7500bb7db290a1204bfa8"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1,"start":491,"end":495},"resolved_arguments":{"series_index":1,"start":491,"end":495},"success":true,"data":{"series_index":1,"start":491,"end":495,"mean_diff":0.01249999999999929,"std_diff":0.066473679001542,"max_abs_diff":0.10000000000000142,"n_sign_changes":1},"error":null,"args_fingerprint":"e3e11213c76dba0c44ab99adc3d19bb69f82bc50"},{"call_id":"short:step3","step":3,"tool_name":"interval_compare","arguments":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493},"resolved_arguments":{"series_index":1,"start":491,"end":495,"left_interval":[491,492],"right_interval":[494,495],"mid":493},"success":true,"data":{"series_index":1,"mode":"pair","left_interval":[491,492],"right_interval":[494,495],"left_mean":43.69,"right_mean":43.724999999999994,"left_std":0.05000000000000071,"right_std":0.03500000000000014,"left_max":43.74,"right_max":43.76,"left_min":43.64,"right_min":43.69,"left_max_index":492,"right_max_index":494,"left_n_peaks":0,"right_n_peaks":0,"left_n_troughs":0,"right_n_troughs":0,"left_direction":"upward","right_direction":"downward","left_slope":0.10000000000000142,"right_slope":-0.07000000000000028,"mean_delta":0.03499999999999659,"max_delta":0.01999999999999602,"same_trend_direction":false},"error":null,"args_fingerprint":"70647c6221d7fce3f835da379bbf2e361a35e25d"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The objective was to evaluate the entire time series to identify any potential global maxima or minima. Using the 'global_extrema' tool, we identified the global maximum value as 65.87 at index 584 and the global minimum value as -70.6 at index 145. This data provides evidence to support the claims of identifying global extrema values.","scale":"long","observations":["Global maximum value in the series is 65.87 at index 584.","Global minimum value in the series is -70.6 at index 145."],"evidence_intervals":["[0, 703]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 703, \"index_base\": 1}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 703, \"index_base\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 703, \"max_index\": 584, \"min_index\": 145, \"max_value\": 65.87, \"min_value\": -70.6, \"n_peaks\": 5, \"n_troughs\": 6, \"peak_indices\": [99, 195, 493, 584, 676], \"trough_indices\": [56, 145, 234, 526, 634, 637]}, \"error\": null, \"args_fingerprint\": \"441770107ed0c461a234a5dcdc3b6438b2ff29c4\"}"],"evidence_plan":{"objective":"Evaluate the entire time series to identify any potential global maxima or minima","claims_to_support":[{"claim":"Identify the global maximum value in the entire series","required_evidence":["global_maximum_value"]},{"claim":"Identify the global minimum value in the entire series","required_evidence":["global_minimum_value"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,703]],"scale":"long"},"validation_needs":["Consistency across series endpoints"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"This tool is used to identify global extrema values and their locations, which is necessary for validating the global maximum and minimum values across the series endpoints.","supports_evidence":["global_maximum_value","global_minimum_value"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"global_extrema","output_key":"series","input_binding":{}}],"reasoning":"Given the objective of identifying global maxima and minima values in the entire series, the 'global_extrema' tool is chosen as it provides the necessary functionality to detect these points. Since there are no other tools involved, the workflow will consist of a single step utilizing 'global_extrema'."},"structured_observations":[{"claim":"Identify the global maximum value in the entire series","evidence":[{"type":"global_maximum_value","value":65.87,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum_value"},{"claim":"Identify the global minimum value in the entire series","evidence":[{"type":"global_minimum_value","value":-70.6,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum_value"}],"coverage":{"global_maximum_value":"tool_supported","global_minimum_value":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":703,"index_base":1},"resolved_arguments":{"series_index":1,"start":0,"end":703,"index_base":1},"success":true,"data":{"series_index":1,"start":0,"end":703,"max_index":584,"min_index":145,"max_value":65.87,"min_value":-70.6,"n_peaks":5,"n_troughs":6,"peak_indices":[99,195,493,584,676],"trough_indices":[56,145,234,526,634,637]},"error":null,"args_fingerprint":"441770107ed0c461a234a5dcdc3b6438b2ff29c4"}],"skipped_stages":[]},"conflicts":[],"summary":"Point 493 is identified as having a local peak. Endpoint slopes differ, suggesting asymmetry around point 493. Pairwise comparison metrics also indicate asymmetry around point 493. Global maximum value in the series is 65.87 at index 584. Global minimum value in the series is -70.6 at index 145.","structured_by_scale":{"short":[{"claim":"Point 493 has a local peak.","evidence":[{"type":"local_extrema_count","value":1,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_extrema_count"},{"claim":"Endpoint slopes are asymmetric around point 493.","evidence":[{"type":"endpoint_slope","value":{"left_slope":0.10000000000000142,"right_slope":-0.07000000000000028,"same_trend_direction":false},"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity metrics show asymmetry around point 493.","evidence":[{"type":"pairwise_similarity","value":{"mean_delta":0.03499999999999659,"max_delta":0.01999999999999602,"same_trend_direction":false},"source_tool":"interval_compare","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"Identify the global maximum value in the entire series","evidence":[{"type":"global_maximum_value","value":65.87,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum_value"},{"claim":"Identify the global minimum value in the entire series","evidence":[{"type":"global_minimum_value","value":-70.6,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum_value"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses","required_measurements":["endpoint_slope","pairwise_similarity","global_maximum_value","global_minimum_value"],"validation_requirements":["Agreement between short and long term perspectives"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[704]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Based on the evidence gathered, point 493 is identified as having a local maximum. The short-term analysis confirms this through detection of a local peak and measurement of endpoint slopes showing asymmetry around point 493. However, the long-term analysis identifies the global maximum value as 65.87 at index 584, and the global minimum as -70.6 at index 145. Thus, point 493 does not qualify as a global maximum or minimum.",
  "role": "reasoning",
  "hypothesis": "Point 493 is a local maximum but not a global maximum or minimum.",
  "evidence": [
    "Point 493 has a local maximum based on the short-term analysis.",
    "Endpoint slopes around point 493 show different trends, indicating asymmetry.",
    "The global maximum value is identified at index 584 with value 65.87.",
    "The global minimum value is identified at index 145 with value -70.6."
  ],
  "candidate_preference": null,
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "short:step3", "long:step1"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Point 493 has a local maximum based on the short-term analysis",
      "evidence": [
        {
          "type": "local_extrema_count",
          "value": 1,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Endpoint slopes around point 493 show different trends, indicating asymmetry",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": {
            "left_slope": 0.10000000000000142,
            "right_slope": -0.07000000000000028,
            "same_trend_direction": false
          },
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The global maximum value is identified at index 584 with value 65.87",
      "evidence": [
        {
          "type": "global_maximum_value",
          "value": 65.87,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The global minimum value is identified at index 145 with value -70.6",
      "evidence": [
        {
          "type": "global_minimum_value",
          "value": -70.6,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1754 completion=289 latency=10.57s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 493 present a global maximum or minimum value or neither? (The index starts from 0)
</question>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Identify whether point 493 in a given time series represents a global maximum, minimum, or neither.",
  "question_type": "choice",
  "required_output": "choice",
  "success_criteria": [
    "Correct classification of point 493 based on comprehensive time series analysis"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Check the immediate neighborhood of point 493 for local extrema",
      "required_measurements": [
        "endpoint_slope",
        "pairwise_similarity"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Evaluate the entire time series to identify any potential global maxima or minima",
      "required_measurements": [
        "global_maximum_value",
        "global_minimum_value"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Determine if point 493 qualifies as a global maximum, minimum, or neither based on local and global analyses",
      "required_measurements": [
        "endpoint_slope",
        "pairwise_similarity",
        "global_maximum_value",
        "global_minimum_value"
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
          "type": "local_extrema_count",
          "value": 1,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "endpoint_slope",
          "value": {
            "left_slope": 0.10000000000000142,
            "right_slope": -0.07000000000000028,
            "same_trend_direction": false
          },
          "trusted": true
        },
        {
          "series_index": null,
          "type": "pairwise_similarity",
          "value": {
            "mean_delta": 0.03499999999999659,
            "max_delta": 0.01999999999999602,
            "same_trend_direction": false
          },
          "trusted": true
        }
      ],
      "coverage": {
        "local_extrema_count": "tool_supported",
        "endpoint_slope": "tool_supported",
        "pairwise_similarity": "tool_supported"
      },
      "summary": "Point 493 is identified as having a local peak. | Endpoint slopes differ, suggesting asymmetry around point 493. | Pairwise comparison metrics also indicate asymmetry around point 493."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_maximum_value",
          "value": 65.87,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "global_minimum_value",
          "value": -70.6,
          "trusted": true
        }
      ],
      "coverage": {
        "global_maximum_value": "tool_supported",
        "global_minimum_value": "tool_supported"
      },
      "summary": "Global maximum value in the series is 65.87 at index 584. | Global minimum value in the series is -70.6 at index 145."
    }
  },
  "conflicts": [],
  "summary": "Point 493 is identified as having a local peak. Endpoint slopes differ, suggesting asymmetry around point 493. Pairwise comparison metrics also indicate asymmetry around point 493. Global maximum value in the series is 65.87 at index 584. Global minimum value in the series is -70.6 at index 145."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
      "hypothesis": "Point 493 is a local maximum but not a global maximum or minimum.",
      "reasoning_chain": [
        "Point 493 has a local maximum based on the short-term analysis",
        "local_extrema_count=1",
        "Endpoint slopes around point 493 show different trends, indicating asymmetry",
        "endpoint_slope={'left_slope': 0.10000000000000142, 'right_slope': -0.07000000000000028, 'same_trend_direction': False}",
        "The global maximum value is identified at index 584 with value 65.87",
        "global_maximum_value=65.87",
        "The global minimum value is identified at index 145 with value -70.6",
        "global_minimum_value=-70.6"
      ],
      "candidate_preference": null,
      "confidence": 1.0,
      "grounded": true,
      "grounded_in": [
        "local_extrema_count",
        "endpoint_slope",
        "global_maximum_value",
        "global_minimum_value"
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



Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "Heter reasoning concludes that Point 493 is a local maximum but not a global maximum or minimum. This is based on short-term analysis identifying a local extrema count of 1 and endpoint slopes showing different trends, as well as long-term analysis showing that the global maximum value occurs at a different index (584 with value 65.87), and global minimum at another index (145 with value -70.6).",
  "answer": "C",
  "explanation": "Point 493 is identified as having a local peak. Endpoint slopes and pairwise similarity metrics confirm asymmetry around point 493, supporting the identification of a local maximum. However, this does not qualify as a global maximum since the highest value in the series occurs at index 584. Similarly, it is not a global minimum as the lowest value in the series is observed at index 145.",
  "confidence": 1.0,
  "conflicts": [],
  "cited_evidence": ["local_extrema_count", "endpoint_slope", "global_maximum_value", "global_minimum_value"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "C"
  }
}
```
