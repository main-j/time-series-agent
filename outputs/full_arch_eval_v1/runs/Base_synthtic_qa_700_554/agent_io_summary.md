# Agent IO summary: `Base:synthtic_qa_700:554`

- Architecture pred: `B` (success=True)
- model_calls=16, tool_calls=4, latency=166.8s

## Planner — `planner`

tokens prompt=1033 completion=537 latency=19.07s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 129 present a global maximum or minimum value or neither? (The index starts from 0)
</question>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

<metadata>
local_overall=local; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "To determine if point 129 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point as well as compare its value with the entire dataset.",
  "task_summary": "Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.",
  "target_output": "The classification of point 129 (whether it is a global maximum, minimum, or neither) based on the comparison with all other points in the series.",
  "answer_type": "choice",
  "capability": "hierarchical time-series analysis",
  "scope": "local",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Identify immediate neighborhood characteristics of point 129 in Time Series 1.",
      "required_measurements": ["change_location", "endpoint_slope"],
      "validation_requirements": ["Compare slopes and levels immediately preceding and following point 129"],
      "target_series": [1],
      "focus_intervals": [[128, 130]]
    },
    {
      "scale": "long",
      "objective": "Analyze the entire range of values in Time Series 1 to determine overall extremum points.",
      "required_measurements": ["global_extremum"],
      "validation_requirements": ["Confirm by comparing point 129's value against all other data points"],
      "target_series": [1],
      "focus_intervals": [[0, 788]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.",
      "required_measurements": ["global_extremum", "change_location", "endpoint_slope"],
      "validation_requirements": ["Cross-check the classification against the identified extremum value and its relative position in the series"],
      "target_series": [1],
      "focus_intervals": [[0, 788], [128, 130]]
    }
  ],
  "success_criteria": ["Point 129 correctly classified as global max, min, or neither according to evidence gathered from its immediate surroundings and the whole dataset."],
  "notes": "The short-term analysis captures local behavior, while the long-term view ensures the point's extremity status across the entire series."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4140 completion=291 latency=11.52s

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
{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 129 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point as well as compare its value with the entire dataset.","task_summary":"Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.","target_output":"The classification of point 129 (whether it is a global maximum, minimum, or neither) based on the comparison with all other points in the series.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]},{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}],"hetero_assignments":[{"role":"matching","objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","required_measurements":["global_extremum","change_location","endpoint_slope"],"validation_requirements":["Cross-check the classification against the identified extremum value and its relative position in the series"],"target_series":[1],"focus_intervals":[[0,788],[128,130]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Point 129 correctly classified as global max, min, or neither according to evidence gathered from its immediate surroundings and the whole dataset."],"notes":"The short-term analysis captures local behavior, while the long-term view ensures the point's extremity status across the entire series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, specifically focusing on the location of change and endpoint slopes around the specified point. Validation is needed by comparing slopes and levels immediately preceding and following point 129.",
  "evidence_plan": {
    "objective": "Identify immediate neighborhood characteristics of point 129 in Time Series 1.",
    "claims_to_support": [
      {
        "claim": "Point 129 has an identifiable location of change.",
        "required_evidence": ["change_location"]
      },
      {
        "claim": "Endpoint slopes before and after point 129 are measurable.",
        "required_evidence": ["endpoint_slope"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[128,130]],
      "scale": "short"
    },
    "validation_needs": ["Compare slopes and levels immediately preceding and following point 129"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "diff_stats",
        "reason": "To detect changes and endpoint slope shifts around point 129.",
        "supports_evidence": ["change_location", "endpoint_slope"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=729 completion=108 latency=3.90s

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
{"evidence_plan":{"objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","claims_to_support":[{"claim":"Point 129 has an identifiable location of change.","required_evidence":["change_location"]},{"claim":"Endpoint slopes before and after point 129 are measurable.","required_evidence":["endpoint_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[128,130]],"scale":"short"},"validation_needs":["Compare slopes and levels immediately preceding and following point 129"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To detect changes and endpoint slope shifts around point 129.","supports_evidence":["change_location","endpoint_slope"]}],"no_tool_decision":null},"reasoning":"The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, specifically focusing on the location of change and endpoint slopes around the specified point. Validation is needed by comparing slopes and levels immediately preceding and following point 129."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- diff_stats
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, using diff_stats to detect changes and endpoint slope shifts around the specified point.",
  "workflow": [
    {
      "step": 1,
      "tool": "diff_stats",
      "output_key": "series_with_change_details",
      "input_binding": {"series_index": 0, "start": 128, "end": 130}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=749 completion=116 latency=4.18s

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
{"workflow":[{"step":1,"tool":"diff_stats","output_key":"series_with_change_details","input_binding":{"series_index":0,"start":128,"end":130}}],"reasoning":"The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, using diff_stats to detect changes and endpoint slope shifts around the specified point."}
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
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1. The diff_stats tool will be used with a specified interval [128,130] to identify change locations and endpoint slope shifts.",
  "calls": [
    {
      "step": 1,
      "tool": "diff_stats",
      "args": {
        "series_index": 1,
        "start": 128,
        "end": 130
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1023 completion=365 latency=12.99s

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
{"evidence_plan":{"objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","claims_to_support":[{"claim":"Point 129 has an identifiable location of change.","required_evidence":["change_location"]},{"claim":"Endpoint slopes before and after point 129 are measurable.","required_evidence":["endpoint_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[128,130]],"scale":"short"},"validation_needs":["Compare slopes and levels immediately preceding and following point 129"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To detect changes and endpoint slope shifts around point 129.","supports_evidence":["change_location","endpoint_slope"]}],"no_tool_decision":null},"reasoning":"The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, specifically focusing on the location of change and endpoint slopes around the specified point. Validation is needed by comparing slopes and levels immediately preceding and following point 129."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "diff_stats",
    "arguments": {
      "series_index": 1,
      "start": 128,
      "end": 130
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 128,
      "end": 130
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 128,
      "end": 130,
      "mean_diff": -1.0449999999999982,
      "std_diff": 11.404999999999998,
      "max_abs_diff": 12.449999999999996,
      "n_sign_changes": 1
    },
    "error": null,
    "args_fingerprint": "d629608c66d97db8eaafff8227e646b2e8a75c37"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Executed diff_stats tool to analyze immediate neighborhood characteristics of point 129 in Time Series 1. Identified mean difference, standard deviation, max absolute difference, and number of sign changes as indicators of change location and potential endpoint slope shift.",
  "scale": "short",
  "observations": ["Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point."],
  "evidence_intervals": ["[128, 130]"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Point 129 has an identifiable location of change.",
      "evidence": [
        {
          "type": "change_location",
          "value": 1,
          "source_tool": "diff_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_location"
    },
    {
      "claim": "Endpoint slopes before and after point 129 are measurable.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": -1.045,
          "source_tool": "diff_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "endpoint_slope"
    }
  ],
  "coverage": {"change_location": "tool_supported", "endpoint_slope": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4141 completion=321 latency=12.63s

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
{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 129 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point as well as compare its value with the entire dataset.","task_summary":"Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.","target_output":"The classification of point 129 (whether it is a global maximum, minimum, or neither) based on the comparison with all other points in the series.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]},{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}],"hetero_assignments":[{"role":"matching","objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","required_measurements":["global_extremum","change_location","endpoint_slope"],"validation_requirements":["Cross-check the classification against the identified extremum value and its relative position in the series"],"target_series":[1],"focus_intervals":[[0,788],[128,130]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Point 129 correctly classified as global max, min, or neither according to evidence gathered from its immediate surroundings and the whole dataset."],"notes":"The short-term analysis captures local behavior, while the long-term view ensures the point's extremity status across the entire series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima across the whole series and specifically confirming if point 129 represents a global extremum.",
  "evidence_plan": {
    "objective": "Analyze the entire range of values in Time Series 1 to determine overall extremum points.",
    "claims_to_support": [
      {"claim": "Point 129 in Time Series 1 is a global extremum.", "required_evidence": ["global_extremum"]},
      {"claim": "The value of point 129 is confirmed as a global maximum or minimum by comparing it against all other data points.", "required_evidence": ["value_at_index"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[0,788]], "scale": "long"},
    "validation_needs": ["global_extremum", "value_at_index"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "global_extrema", "reason": "To identify the global maximum and minimum points across the entire series.", "supports_evidence": ["global_extremum"]},
      {"tool": "value_at_index", "reason": "To retrieve the exact value at index 129 for direct comparison.", "supports_evidence": ["value_at_index"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=804 completion=189 latency=6.77s

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
{"evidence_plan":{"objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","claims_to_support":[{"claim":"Point 129 in Time Series 1 is a global extremum.","required_evidence":["global_extremum"]},{"claim":"The value of point 129 is confirmed as a global maximum or minimum by comparing it against all other data points.","required_evidence":["value_at_index"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,788]],"scale":"long"},"validation_needs":["global_extremum","value_at_index"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"To identify the global maximum and minimum points across the entire series.","supports_evidence":["global_extremum"]},{"tool":"value_at_index","reason":"To retrieve the exact value at index 129 for direct comparison.","supports_evidence":["value_at_index"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima across the whole series and specifically confirming if point 129 represents a global extremum."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- global_extrema
  inputs: series_index, start, end, index, index_base
  outputs: series
- value_at_index
  inputs: series_index, start, end, index, index_base
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima across the whole series and specifically confirming if point 129 represents a global extremum. Therefore, the workflow will first use the global_extrema tool to find the global extremum points, and then the value_at_index tool to confirm the value at index 129.",
  "workflow": [
    {
      "step": 1,
      "tool": "global_extrema",
      "output_key": "global_extremum_points",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "value_at_index",
      "output_key": "value_at_129",
      "input_binding": {"index": 129}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=963 completion=200 latency=7.17s

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
{"workflow":[{"step":1,"tool":"global_extrema","output_key":"global_extremum_points","input_binding":{}},{"step":2,"tool":"value_at_index","output_key":"value_at_129","input_binding":{"index":129}}],"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima across the whole series and specifically confirming if point 129 represents a global extremum. Therefore, the workflow will first use the global_extrema tool to find the global extremum points, and then the value_at_index tool to confirm the value at index 129."}
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
- value_at_index: Return the numeric value at a specific index (0-based by default).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, index=required int index, index_base=0 (default) or 1 if question uses 1-based indices}
  returns: {series=selected series, requested index/position, and exact value}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima across the whole series and specifically confirming if point 129 represents a global extremum. Therefore, the workflow will first use the global_extrema tool to find the global extremum points, and then the value_at_index tool to confirm the value at index 129.",
  "calls": [
    {
      "step": 1,
      "tool": "global_extrema",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 788
      }
    },
    {
      "step": 2,
      "tool": "value_at_index",
      "args": {
        "series_index": 1,
        "index": 129
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1602 completion=419 latency=15.21s

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
{"evidence_plan":{"objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","claims_to_support":[{"claim":"Point 129 in Time Series 1 is a global extremum.","required_evidence":["global_extremum"]},{"claim":"The value of point 129 is confirmed as a global maximum or minimum by comparing it against all other data points.","required_evidence":["value_at_index"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,788]],"scale":"long"},"validation_needs":["global_extremum","value_at_index"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"To identify the global maximum and minimum points across the entire series.","supports_evidence":["global_extremum"]},{"tool":"value_at_index","reason":"To retrieve the exact value at index 129 for direct comparison.","supports_evidence":["value_at_index"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima across the whole series and specifically confirming if point 129 represents a global extremum."}
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
      "end": 788
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 788
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 788,
      "max_index": 756,
      "min_index": 129,
      "max_value": 303.49,
      "min_value": 33.71,
      "n_peaks": 66,
      "n_troughs": 66,
      "peak_indices": [
        118,
        120,
        122,
        124,
        126,
        128,
        132,
        134,
        136,
        138,
        140,
        142,
        144,
        146,
        276,
        278,
        280,
        282,
        284,
        288,
        290,
        292,
        294,
        296,
        298,
        300,
        302,
        432,
        434,
        436
      ],
      "trough_indices": [
        117,
        119,
        121,
        123,
        125,
        127,
        129,
        133,
        135,
        137,
        139,
        141,
        143,
        145,
        275,
        277,
        279,
        281,
        283,
        285,
        289,
        291,
        293,
        295,
        297,
        299,
        301,
        431,
        433,
        435
      ]
    },
    "error": null,
    "args_fingerprint": "9b05a6c75c3b205f30b69b706dd1b577cde90008"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "value_at_index",
    "arguments": {
      "series_index": 1,
      "index": 129
    },
    "resolved_arguments": {
      "series_index": 1,
      "index": 129
    },
    "success": true,
    "data": {
      "series_index": 1,
      "index": 129,
      "position": 129,
      "value": 33.71
    },
    "error": null,
    "args_fingerprint": "360d9f93c467ceaea19a2df59ddea43b008b9810"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis was conducted over the entire range of values in Time Series 1, focusing on intervals from index 0 to 788. The global extremum was identified using the 'global_extrema' tool which found that the minimum value occurred at index 129. This aligns with the claim that point 129 in Time Series 1 is a global extremum. Additionally, the exact value at index 129 was confirmed to be 33.71 through the 'value_at_index' tool.",
  "scale": "long",
  "observations": ["The analysis confirms that point 129 in Time Series 1 is indeed a global extremum, and its value is 33.71, which is the lowest value in the analyzed range."],
  "evidence_intervals": ["[0,788]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Point 129 in Time Series 1 is a global extremum.",
      "evidence": [
        {
          "type": "global_extremum",
          "value": 33.71,
          "source_tool": "global_extrema",
          "call_id": "long:step1",
          "provenance": "tool"
        },
        {
          "type": "value_at_index",
          "value": 33.71,
          "source_tool": "value_at_index",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_extremum"
    }
  ],
  "coverage": {"seasonal_strength": "unresolved", "global_extremum": "tool_supported", "value_at_index": "tool_supported"},
  "unresolved_claims": ["seasonal_strength"]
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m1`

tokens prompt=4157 completion=268 latency=10.72s

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
{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 129 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point as well as compare its value with the entire dataset.","task_summary":"Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.","target_output":"The classification of point 129 (whether it is a global maximum, minimum, or neither) based on the comparison with all other points in the series.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]},{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}],"hetero_assignments":[{"role":"matching","objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","required_measurements":["global_extremum","change_location","endpoint_slope"],"validation_requirements":["Cross-check the classification against the identified extremum value and its relative position in the series"],"target_series":[1],"focus_intervals":[[0,788],[128,130]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Point 129 correctly classified as global max, min, or neither according to evidence gathered from its immediate surroundings and the whole dataset."],"notes":"The short-term analysis captures local behavior, while the long-term view ensures the point's extremity status across the entire series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['seasonal_strength']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima. We also need to confirm if point 129's value stands as a global extremum by comparing it against all other data points.",
  "evidence_plan": {
    "objective": "Analyze the entire range of values in Time Series 1 to determine overall extremum points.",
    "claims_to_support": [
      {
        "claim": "Time Series 1 contains global extremum points.",
        "required_evidence": ["global_extremum"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "long"
    },
    "validation_needs": ["global_extremum"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "global_extrema",
        "reason": "To identify global maximum and minimum values and their positions in the series, which will help in confirming the extremum status of point 129.",
        "supports_evidence": ["global_extremum"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m1`

tokens prompt=721 completion=98 latency=3.56s

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
{"evidence_plan":{"objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","claims_to_support":[{"claim":"Time Series 1 contains global extremum points.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["global_extremum"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"To identify global maximum and minimum values and their positions in the series, which will help in confirming the extremum status of point 129.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima. We also need to confirm if point 129's value stands as a global extremum by comparing it against all other data points."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- global_extrema
  inputs: series_index, start, end, index, index_base
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. Given the selected tool, we should use global_extrema to identify global maximum and minimum values and their positions in the series.",
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

## Homogeneous (long, s4) — `homogeneous:long:s4:m1`

tokens prompt=791 completion=109 latency=3.98s

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
{"workflow":[{"step":1,"tool":"global_extrema","output_key":"series","input_binding":{}}],"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. Given the selected tool, we should use global_extrema to identify global maximum and minimum values and their positions in the series."}
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
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. Using the global_extrema tool on the full range of the series will provide the necessary information.",
  "calls": [
    {
      "step": 1,
      "tool": "global_extrema",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 788
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m1`

tokens prompt=1365 completion=320 latency=11.56s

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
{"evidence_plan":{"objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","claims_to_support":[{"claim":"Time Series 1 contains global extremum points.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["global_extremum"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"To identify global maximum and minimum values and their positions in the series, which will help in confirming the extremum status of point 129.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. This requires identifying global maxima and minima. We also need to confirm if point 129's value stands as a global extremum by comparing it against all other data points."}
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
      "end": 788
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 788
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 788,
      "max_index": 756,
      "min_index": 129,
      "max_value": 303.49,
      "min_value": 33.71,
      "n_peaks": 66,
      "n_troughs": 66,
      "peak_indices": [
        118,
        120,
        122,
        124,
        126,
        128,
        132,
        134,
        136,
        138,
        140,
        142,
        144,
        146,
        276,
        278,
        280,
        282,
        284,
        288,
        290,
        292,
        294,
        296,
        298,
        300,
        302,
        432,
        434,
        436
      ],
      "trough_indices": [
        117,
        119,
        121,
        123,
        125,
        127,
        129,
        133,
        135,
        137,
        139,
        141,
        143,
        145,
        275,
        277,
        279,
        281,
        283,
        285,
        289,
        291,
        293,
        295,
        297,
        299,
        301,
        431,
        433,
        435
      ]
    },
    "error": null,
    "args_fingerprint": "9b05a6c75c3b205f30b69b706dd1b577cde90008"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis was conducted over the entire range of values in Time Series 1 to determine the overall extremum points. The tool 'global_extrema' identified the global maximum value as 303.49 at index 756 and the global minimum value as 33.71 at index 129.",
  "scale": "long",
  "observations": [
    "Time Series 1 has been analyzed, identifying the global maximum and minimum points."
  ],
  "evidence_intervals": [
    "[0, 788]"
  ],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Time Series 1 contains global extremum points.",
      "evidence": [
        {
          "type": "global_extremum",
          "value": {
            "max_index": 756,
            "min_index": 129,
            "max_value": 303.49,
            "min_value": 33.71
          },
          "source_tool": "global_extrema",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_extremum"
    }
  ],
  "coverage": {
    "global_extremum": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=5009 completion=383 latency=15.27s

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
{"role":"matching","objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","required_measurements":["global_extremum","change_location","endpoint_slope"],"validation_requirements":["Cross-check the classification against the identified extremum value and its relative position in the series"],"target_series":[1],"focus_intervals":[[0,788],[128,130]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 129 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point as well as compare its value with the entire dataset.","task_summary":"Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.","target_output":"The classification of point 129 (whether it is a global maximum, minimum, or neither) based on the comparison with all other points in the series.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","required_measurements":["change_location","endpoint_slope"],"validation_requirements":["Compare slopes and levels immediately preceding and following point 129"],"target_series":[1],"focus_intervals":[[128,130]]},{"scale":"long","objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","required_measurements":["global_extremum"],"validation_requirements":["Confirm by comparing point 129's value against all other data points"],"target_series":[1],"focus_intervals":[[0,788]]}],"hetero_assignments":[{"role":"matching","objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","required_measurements":["global_extremum","change_location","endpoint_slope"],"validation_requirements":["Cross-check the classification against the identified extremum value and its relative position in the series"],"target_series":[1],"focus_intervals":[[0,788],[128,130]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Point 129 correctly classified as global max, min, or neither according to evidence gathered from its immediate surroundings and the whole dataset."],"notes":"The short-term analysis captures local behavior, while the long-term view ensures the point's extremity status across the entire series."}
</plan_context>

<task_summary>
Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed diff_stats tool to analyze immediate neighborhood characteristics of point 129 in Time Series 1. Identified mean difference, standard deviation, max absolute difference, and number of sign changes as indicators of change location and potential endpoint slope shift.","scale":"short","observations":["Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point."],"evidence_intervals":["[128, 130]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 128, \"end\": 130}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 128, \"end\": 130}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 128, \"end\": 130, \"mean_diff\": -1.0449999999999982, \"std_diff\": 11.404999999999998, \"max_abs_diff\": 12.449999999999996, \"n_sign_changes\": 1}, \"error\": null, \"args_fingerprint\": \"d629608c66d97db8eaafff8227e646b2e8a75c37\"}"],"evidence_plan":{"objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","claims_to_support":[{"claim":"Point 129 has an identifiable location of change.","required_evidence":["change_location"]},{"claim":"Endpoint slopes before and after point 129 are measurable.","required_evidence":["endpoint_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[128,130]],"scale":"short"},"validation_needs":["Compare slopes and levels immediately preceding and following point 129"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To detect changes and endpoint slope shifts around point 129.","supports_evidence":["change_location","endpoint_slope"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"series_with_change_details","input_binding":{"series_index":0,"start":128,"end":130}}],"reasoning":"The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, using diff_stats to detect changes and endpoint slope shifts around the specified point."},"structured_observations":[{"claim":"Point 129 has an identifiable location of change.","evidence":[{"type":"change_location","value":1,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Endpoint slopes before and after point 129 are measurable.","evidence":[{"type":"endpoint_slope","value":-1.045,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"}],"coverage":{"change_location":"tool_supported","endpoint_slope":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":128,"end":130},"resolved_arguments":{"series_index":1,"start":128,"end":130},"success":true,"data":{"series_index":1,"start":128,"end":130,"mean_diff":-1.0449999999999982,"std_diff":11.404999999999998,"max_abs_diff":12.449999999999996,"n_sign_changes":1},"error":null,"args_fingerprint":"d629608c66d97db8eaafff8227e646b2e8a75c37"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The analysis was conducted over the entire range of values in Time Series 1 to determine the overall extremum points. The tool 'global_extrema' identified the global maximum value as 303.49 at index 756 and the global minimum value as 33.71 at index 129.","scale":"long","observations":["Time Series 1 has been analyzed, identifying the global maximum and minimum points."],"evidence_intervals":["[0, 788]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 788}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 788}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 788, \"max_index\": 756, \"min_index\": 129, \"max_value\": 303.49, \"min_value\": 33.71, \"n_peaks\": 66, \"n_troughs\": 66, \"peak_indices\": [118, 120, 122, 124, 126, 128, 132, 134, 136, 138, 140, 142, 144, 146, 276, 278, 280, 282, 284, 288, 290, 292, 294, 296, 298, 300, 302, 432, 434, 436], \"trough_indices\": [117, 119, 121, 123, 125, 127, 129, 133, 135, 137, 139, 141, 143, 145, 275, 277, 279, 281, 283, 285, 289, 291, 293, 295, 297, 299, 301, 431, 433, 435]}, \"error\": null, \"args_fingerprint\": \"9b05a6c75c3b205f30b69b706dd1b577cde90008\"}"],"evidence_plan":{"objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","claims_to_support":[{"claim":"Time Series 1 contains global extremum points.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["global_extremum"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"To identify global maximum and minimum values and their positions in the series, which will help in confirming the extremum status of point 129.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"global_extrema","output_key":"series","input_binding":{}}],"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. Given the selected tool, we should use global_extrema to identify global maximum and minimum values and their positions in the series."},"structured_observations":[{"claim":"Time Series 1 contains global extremum points.","evidence":[{"type":"global_extremum","value":{"max_index":756,"min_index":129,"max_value":303.49,"min_value":33.71},"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}],"coverage":{"global_extremum":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":788},"resolved_arguments":{"series_index":1,"start":0,"end":788},"success":true,"data":{"series_index":1,"start":0,"end":788,"max_index":756,"min_index":129,"max_value":303.49,"min_value":33.71,"n_peaks":66,"n_troughs":66,"peak_indices":[118,120,122,124,126,128,132,134,136,138,140,142,144,146,276,278,280,282,284,288,290,292,294,296,298,300,302,432,434,436],"trough_indices":[117,119,121,123,125,127,129,133,135,137,139,141,143,145,275,277,279,281,283,285,289,291,293,295,297,299,301,431,433,435]},"error":null,"args_fingerprint":"9b05a6c75c3b205f30b69b706dd1b577cde90008"}],"skipped_stages":[]},"conflicts":[],"summary":"Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point. Time Series 1 has been analyzed, identifying the global maximum and minimum points.","structured_by_scale":{"short":[{"claim":"Point 129 has an identifiable location of change.","evidence":[{"type":"change_location","value":1,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Endpoint slopes before and after point 129 are measurable.","evidence":[{"type":"endpoint_slope","value":-1.045,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"}],"long":[{"claim":"Time Series 1 contains global extremum points.","evidence":[{"type":"global_extremum","value":{"max_index":756,"min_index":129,"max_value":303.49,"min_value":33.71},"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile and prior evidence provided, the analysis shows that point 129 in the time series corresponds to the global minimum value of 33.71. This conclusion is supported by the global extrema analysis conducted on the entire series. The short-term analysis also indicates a change location near point 129 with varying endpoint slopes, which further corroborates that this point marks a significant change. Validation confirms that point 129 is indeed a global minimum.",
  "evidence_plan": {
    "objective": "Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.",
    "claims_to_support": [
      {
        "claim": "Point 129 corresponds to a global minimum.",
        "required_evidence": ["global_extremum", "change_location", "endpoint_slope"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[0, 788]],
      "role": "matching"
    },
    "validation_needs": ["Cross-check the classification against the identified extremum value and its relative position in the series"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "Prior analysis already identifies global extrema and change location for point 129.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_extremum"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step1",
          "field": "change_location"
        }
      ]
    }
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=3718 completion=505 latency=19.15s

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
{"evidence_plan":{"objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","claims_to_support":[{"claim":"Point 129 corresponds to a global minimum.","required_evidence":["global_extremum","change_location","endpoint_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,788]],"role":"matching"},"validation_needs":["Cross-check the classification against the identified extremum value and its relative position in the series"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Prior analysis already identifies global extrema and change location for point 129.","evidence_sources":[{"type":"upstream_observation","ref":"long:step1","field":"global_extremum"},{"type":"upstream_observation","ref":"short:step1","field":"change_location"}]}},"reasoning":"Based on the temporal profile and prior evidence provided, the analysis shows that point 129 in the time series corresponds to the global minimum value of 33.71. This conclusion is supported by the global extrema analysis conducted on the entire series. The short-term analysis also indicates a change location near point 129 with varying endpoint slopes, which further corroborates that this point marks a significant change. Validation confirms that point 129 is indeed a global minimum."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed diff_stats tool to analyze immediate neighborhood characteristics of point 129 in Time Series 1. Identified mean difference, standard deviation, max absolute difference, and number of sign changes as indicators of change location and potential endpoint slope shift.","scale":"short","observations":["Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point."],"evidence_intervals":["[128, 130]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 128, \"end\": 130}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 128, \"end\": 130}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 128, \"end\": 130, \"mean_diff\": -1.0449999999999982, \"std_diff\": 11.404999999999998, \"max_abs_diff\": 12.449999999999996, \"n_sign_changes\": 1}, \"error\": null, \"args_fingerprint\": \"d629608c66d97db8eaafff8227e646b2e8a75c37\"}"],"evidence_plan":{"objective":"Identify immediate neighborhood characteristics of point 129 in Time Series 1.","claims_to_support":[{"claim":"Point 129 has an identifiable location of change.","required_evidence":["change_location"]},{"claim":"Endpoint slopes before and after point 129 are measurable.","required_evidence":["endpoint_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[128,130]],"scale":"short"},"validation_needs":["Compare slopes and levels immediately preceding and following point 129"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To detect changes and endpoint slope shifts around point 129.","supports_evidence":["change_location","endpoint_slope"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"series_with_change_details","input_binding":{"series_index":0,"start":128,"end":130}}],"reasoning":"The objective requires identifying immediate neighborhood characteristics of point 129 in Time Series 1, using diff_stats to detect changes and endpoint slope shifts around the specified point."},"structured_observations":[{"claim":"Point 129 has an identifiable location of change.","evidence":[{"type":"change_location","value":1,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Endpoint slopes before and after point 129 are measurable.","evidence":[{"type":"endpoint_slope","value":-1.045,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"}],"coverage":{"change_location":"tool_supported","endpoint_slope":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":128,"end":130},"resolved_arguments":{"series_index":1,"start":128,"end":130},"success":true,"data":{"series_index":1,"start":128,"end":130,"mean_diff":-1.0449999999999982,"std_diff":11.404999999999998,"max_abs_diff":12.449999999999996,"n_sign_changes":1},"error":null,"args_fingerprint":"d629608c66d97db8eaafff8227e646b2e8a75c37"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The analysis was conducted over the entire range of values in Time Series 1 to determine the overall extremum points. The tool 'global_extrema' identified the global maximum value as 303.49 at index 756 and the global minimum value as 33.71 at index 129.","scale":"long","observations":["Time Series 1 has been analyzed, identifying the global maximum and minimum points."],"evidence_intervals":["[0, 788]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 788}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 788}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 788, \"max_index\": 756, \"min_index\": 129, \"max_value\": 303.49, \"min_value\": 33.71, \"n_peaks\": 66, \"n_troughs\": 66, \"peak_indices\": [118, 120, 122, 124, 126, 128, 132, 134, 136, 138, 140, 142, 144, 146, 276, 278, 280, 282, 284, 288, 290, 292, 294, 296, 298, 300, 302, 432, 434, 436], \"trough_indices\": [117, 119, 121, 123, 125, 127, 129, 133, 135, 137, 139, 141, 143, 145, 275, 277, 279, 281, 283, 285, 289, 291, 293, 295, 297, 299, 301, 431, 433, 435]}, \"error\": null, \"args_fingerprint\": \"9b05a6c75c3b205f30b69b706dd1b577cde90008\"}"],"evidence_plan":{"objective":"Analyze the entire range of values in Time Series 1 to determine overall extremum points.","claims_to_support":[{"claim":"Time Series 1 contains global extremum points.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["global_extremum"]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"To identify global maximum and minimum values and their positions in the series, which will help in confirming the extremum status of point 129.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"global_extrema","output_key":"series","input_binding":{}}],"reasoning":"The objective is to analyze the entire range of values in Time Series 1 to determine the overall extremum points. Given the selected tool, we should use global_extrema to identify global maximum and minimum values and their positions in the series."},"structured_observations":[{"claim":"Time Series 1 contains global extremum points.","evidence":[{"type":"global_extremum","value":{"max_index":756,"min_index":129,"max_value":303.49,"min_value":33.71},"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}],"coverage":{"global_extremum":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":788},"resolved_arguments":{"series_index":1,"start":0,"end":788},"success":true,"data":{"series_index":1,"start":0,"end":788,"max_index":756,"min_index":129,"max_value":303.49,"min_value":33.71,"n_peaks":66,"n_troughs":66,"peak_indices":[118,120,122,124,126,128,132,134,136,138,140,142,144,146,276,278,280,282,284,288,290,292,294,296,298,300,302,432,434,436],"trough_indices":[117,119,121,123,125,127,129,133,135,137,139,141,143,145,275,277,279,281,283,285,289,291,293,295,297,299,301,431,433,435]},"error":null,"args_fingerprint":"9b05a6c75c3b205f30b69b706dd1b577cde90008"}],"skipped_stages":[]},"conflicts":[],"summary":"Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point. Time Series 1 has been analyzed, identifying the global maximum and minimum points.","structured_by_scale":{"short":[{"claim":"Point 129 has an identifiable location of change.","evidence":[{"type":"change_location","value":1,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"Endpoint slopes before and after point 129 are measurable.","evidence":[{"type":"endpoint_slope","value":-1.045,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"}],"long":[{"claim":"Time Series 1 contains global extremum points.","evidence":[{"type":"global_extremum","value":{"max_index":756,"min_index":129,"max_value":303.49,"min_value":33.71},"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.","required_measurements":["global_extremum","change_location","endpoint_slope"],"validation_requirements":["Cross-check the classification against the identified extremum value and its relative position in the series"],"target_series":[1],"focus_intervals":[[0,788],[128,130]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[789]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Point 129 is classified based on the global extremum analysis and the change location detection from the temporal profile. The long-term analysis reveals that point 129 is the global minimum value within the time series, as indicated by the 'global_extrema' tool. Additionally, the short-term diff_stats analysis supports this classification by detecting a change near point 129, suggesting that the slopes before and after this point vary.",
  "role": "matching",
  "hypothesis": "Point 129 corresponds to a global minimum value compared to the entire series.",
  "evidence": ["Time Series 1 has been analyzed using global_extrema, identifying the global minimum value at index 129. Short-term diff_stats analysis confirmed the location of change near point 129, supporting the extremum classification."],
  "candidate_preference": "B",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["long:step1", "short:step1"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Point 129 corresponds to a global minimum.",
      "evidence": [
        {
          "type": "global_extremum",
          "value": {
            "min_index": 129,
            "min_value": 33.71
          },
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        },
        {
          "type": "change_location",
          "value": 1,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        },
        {
          "type": "endpoint_slope",
          "value": -1.045,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "global_extremum": "tool_supported",
    "change_location": "tool_supported",
    "endpoint_slope": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1423 completion=248 latency=8.98s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 129 present a global maximum or minimum value or neither? (The index starts from 0)
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
  "goal": "Determine whether point 129 in the univariate time series represents a global maximum, minimum, or neither.",
  "question_type": "choice",
  "required_output": "The classification of point 129 (whether it is a global maximum, minimum, or neither) based on the comparison with all other points in the series.",
  "success_criteria": [
    "Point 129 correctly classified as global max, min, or neither according to evidence gathered from its immediate surroundings and the whole dataset."
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Identify immediate neighborhood characteristics of point 129 in Time Series 1.",
      "required_measurements": [
        "change_location",
        "endpoint_slope"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Analyze the entire range of values in Time Series 1 to determine overall extremum points.",
      "required_measurements": [
        "global_extremum"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Classify whether point 129 corresponds to a global maximum, minimum, or neither compared to the entire series.",
      "required_measurements": [
        "global_extremum",
        "change_location",
        "endpoint_slope"
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
          "value": 1,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "endpoint_slope",
          "value": -1.045,
          "trusted": true
        }
      ],
      "coverage": {
        "change_location": "tool_supported",
        "endpoint_slope": "tool_supported"
      },
      "summary": "Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_extremum",
          "value": {
            "max_index": 756,
            "min_index": 129,
            "max_value": 303.49,
            "min_value": 33.71
          },
          "trusted": true
        }
      ],
      "coverage": {
        "global_extremum": "tool_supported"
      },
      "summary": "Time Series 1 has been analyzed, identifying the global maximum and minimum points."
    }
  },
  "conflicts": [],
  "summary": "Identifiable change location detected with one sign change near point 129. Mean difference and standard deviation suggest varying endpoint slopes around the point. Time Series 1 has been analyzed, identifying the global maximum and minimum points."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Point 129 corresponds to a global minimum value compared to the entire series.",
      "reasoning_chain": [
        "Point 129 corresponds to a global minimum.",
        "global_extremum={'min_index': 129, 'min_value': 33.71}",
        "change_location=1",
        "endpoint_slope=-1.045"
      ],
      "candidate_preference": "B",
      "confidence": 1.0,
      "grounded": true,
      "grounded_in": [
        "global_extremum",
        "change_location",
        "endpoint_slope"
      ],
      "uncertainty": ""
    }
  ]
}
</heter_reasoning>

<execution_metadata>
{
  "option_mapping": {},
  "verified_preference": "B",
  "verified": true,
  "warnings": []
}
</execution_metadata>



Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "Heter reasoning clearly matches the hypothesis to the candidate preference B (Min) given that point 129 is identified as the global minimum by the long scale homo perception. The endpoint slope and change location information further support this conclusion by indicating an identifiable change near point 129 with a negative slope.",
  "answer": "B",
  "explanation": "Based on the analysis provided by homo perception and heter reasoning, point 129 is identified as the global minimum value in the time series. The perception data confirms the index of the global minimum is 129 with a value of 33.71.",
  "confidence": 1.0,
  "conflicts": [],
  "cited_evidence": ["global_extremum", "change_location", "endpoint_slope"],
  "decision_trace": {
    "metric": "global_extremum",
    "observed_value": {
      "min_index": 129,
      "min_value": 33.71
    },
    "intervals_from_question": [],
    "matched_label": "Min",
    "matched_letter": "B"
  }
}
```
