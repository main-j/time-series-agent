# Agent IO summary: `Base:synthtic_qa_700:223`

- Architecture pred: `D` (success=True)
- model_calls=28, tool_calls=13, latency=312.9s

## Planner — `planner`

tokens prompt=1031 completion=500 latency=17.87s

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
Here is a list of values in the Time Series 1. Based on the Time Series 1 data provided, what type of waveform does the Time Series 1 most resemble?
</question>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.",
  "task_summary": "Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.",
  "target_output": "The type of waveform Time Series 1 most resembles.",
  "answer_type": "choice",
  "capability": "Hierarchical time-series analysis",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Analyze local behavior for pattern recognition and anomaly detection.",
      "required_measurements": ["local_behavior", "anomaly_detection"],
      "validation_requirements": ["compare multiple small segments"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "medium",
      "objective": "Identify repeated patterns and periodicity to support waveform classification.",
      "required_measurements": ["repeated_patterns", "seasonal_period"],
      "validation_requirements": ["periodicity across various sections"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "long",
      "objective": "Analyze the overall structure for global trends and dependencies.",
      "required_measurements": ["global_trends", "long_term_dependence"],
      "validation_requirements": ["analyze the complete sequence"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.",
      "required_measurements": ["pairwise_similarity", "change_location"],
      "validation_requirements": ["cross-check all four candidate types"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Time Series 1 is accurately matched to one of the candidate waveforms.", "All possible waveform comparisons are evaluated and validated."],
  "notes": "Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4066 completion=257 latency=10.26s

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
{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale data. It requires detecting local patterns and anomalies and validating findings through multiple small segment comparisons.",
  "evidence_plan": {
    "objective": "Analyze local behavior for pattern recognition and anomaly detection.",
    "claims_to_support": [
      {"claim": "Local patterns can be recognized.", "required_evidence": ["sliding_window_statistics"]},
      {"claim": "Anomalies can be detected.", "required_evidence": ["outliers_in_local_windows"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["compare_multiple_small_segments"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "sliding_stats", "reason": "To measure local volatility and rolling level variation.", "supports_evidence": ["sliding_window_statistics"]},
      {"tool": "anomaly_detect", "reason": "To detect point spikes or z-score outliers in local windows.", "supports_evidence": ["outliers_in_local_windows"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=735 completion=166 latency=5.96s

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
{"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local patterns can be recognized.","required_evidence":["sliding_window_statistics"]},{"claim":"Anomalies can be detected.","required_evidence":["outliers_in_local_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare_multiple_small_segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"To measure local volatility and rolling level variation.","supports_evidence":["sliding_window_statistics"]},{"tool":"anomaly_detect","reason":"To detect point spikes or z-score outliers in local windows.","supports_evidence":["outliers_in_local_windows"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale data. It requires detecting local patterns and anomalies and validating findings through multiple small segment comparisons."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- sliding_stats
  inputs: series_index, start, end, window
  outputs: series
- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale data. It requires detecting local patterns and anomalies and validating findings through multiple small segment comparisons. The first step involves measuring local volatility and rolling level variation using sliding_stats, followed by detecting point spikes or z-score outliers in local windows with anomaly_detect.",
  "workflow": [
    {
      "step": 1,
      "tool": "sliding_stats",
      "output_key": "local_pattern",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "output_key": "anomalies",
      "input_binding": {"z_threshold": "$step1.stats.z_score_threshold"}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=865 completion=167 latency=6.00s

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
{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_pattern","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"z_threshold":"$step1.stats.z_score_threshold"}}],"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale data. It requires detecting local patterns and anomalies and validating findings through multiple small segment comparisons. The first step involves measuring local volatility and rolling level variation using sliding_stats, followed by detecting point spikes or z-score outliers in local windows with anomaly_detect."}
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

- sliding_stats: Sliding-window mean/std for local volatility.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, window=int (alias window_size)}
  returns: {series=per-series windowed mean/std aggregates and max_local_std}
- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, z_threshold=float (default 3.0)}
  returns: {series=anomaly count/indices and max absolute z-score}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale data. It requires detecting local patterns and anomalies and validating findings through multiple small segment comparisons. The first step involves measuring local volatility and rolling level variation using sliding_stats, followed by detecting point spikes or z-score outliers in local windows with anomaly_detect.",
  "calls": [
    {
      "step": 1,
      "tool": "sliding_stats",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "args": {
        "series_index": 1,
        "z_threshold": "$step1.stats.z_score_threshold"
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1035 completion=357 latency=12.71s

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
{"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local patterns can be recognized.","required_evidence":["sliding_window_statistics"]},{"claim":"Anomalies can be detected.","required_evidence":["outliers_in_local_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare_multiple_small_segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"To measure local volatility and rolling level variation.","supports_evidence":["sliding_window_statistics"]},{"tool":"anomaly_detect","reason":"To detect point spikes or z-score outliers in local windows.","supports_evidence":["outliers_in_local_windows"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale data. It requires detecting local patterns and anomalies and validating findings through multiple small segment comparisons."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "sliding_stats",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "window": 29,
      "mean_of_means": -18.551806872395673,
      "mean_of_stds": 2.777843427701618,
      "max_local_std": 7.5853416277705055
    },
    "error": null,
    "args_fingerprint": "5d90c6e3697596cfb881b17b747f76e320a9ebe9"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "anomaly_detect",
    "arguments": {
      "series_index": 1,
      "z_threshold": "$step1.stats.z_score_threshold"
    },
    "resolved_arguments": {},
    "success": false,
    "data": {},
    "error": "\"path 'stats.z_score_threshold' not found in tool result\"",
    "args_fingerprint": ""
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Analyzed local behavior for pattern recognition and anomaly detection using sliding window statistics but encountered issues with anomaly detection due to missing z-score threshold from previous step.",
  "scale": "short",
  "observations": [
    "Observed mean of means and mean of standard deviations from sliding window statistics."
  ],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Local patterns can be recognized.",
      "evidence": [
        {
          "type": "sliding_window_statistics",
          "value": {
            "mean_of_means": -18.551806872395673,
            "mean_of_stds": 2.777843427701618,
            "max_local_std": 7.5853416277705055
          },
          "source_tool": "sliding_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "local_behavior"
    },
    {
      "claim": "Anomalies can be detected.",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "anomaly_detection"
    }
  ],
  "coverage": {
    "local_behavior": "tool_supported",
    "anomaly_detection": "unresolved"
  },
  "unresolved_claims": [
    "Anomalies can be detected."
  ]
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m1`

tokens prompt=4086 completion=331 latency=12.96s

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
{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['Anomalies can be detected.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns.",
  "evidence_plan": {
    "objective": "Analyze local behavior for pattern recognition and anomaly detection.",
    "claims_to_support": [
      {
        "claim": "Local behavior patterns exist and can be identified.",
        "required_evidence": ["sliding_window_statistics", "local_extrema_counts"]
      },
      {
        "claim": "Anomalies can be detected.",
        "required_evidence": ["outlier_spikes_in_windows"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "short"
    },
    "validation_needs": ["compare multiple small segments"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "sliding_stats",
        "reason": "Measure local volatility and rolling level variations for pattern recognition.",
        "supports_evidence": ["sliding_window_statistics"]
      },
      {
        "tool": "local_extrema",
        "reason": "Count local peaks and troughs to understand local behavior patterns.",
        "supports_evidence": ["local_extrema_counts"]
      },
      {
        "tool": "anomaly_detect",
        "reason": "Detect anomalies via z-score threshold in sliding windows.",
        "supports_evidence": ["outlier_spikes_in_windows"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m1`

tokens prompt=790 completion=162 latency=5.80s

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
{"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local behavior patterns exist and can be identified.","required_evidence":["sliding_window_statistics","local_extrema_counts"]},{"claim":"Anomalies can be detected.","required_evidence":["outlier_spikes_in_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare multiple small segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measure local volatility and rolling level variations for pattern recognition.","supports_evidence":["sliding_window_statistics"]},{"tool":"local_extrema","reason":"Count local peaks and troughs to understand local behavior patterns.","supports_evidence":["local_extrema_counts"]},{"tool":"anomaly_detect","reason":"Detect anomalies via z-score threshold in sliding windows.","supports_evidence":["outlier_spikes_in_windows"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- sliding_stats
  inputs: series_index, start, end, window
  outputs: series
- local_extrema
  inputs: series_index, start, end
  outputs: series
- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns using the selected tools.",
  "workflow": [
    {
      "step": 1,
      "tool": "sliding_stats",
      "output_key": "local_volatility_results",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "output_key": "extrema_count",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "anomaly_detect",
      "output_key": "anomaly_detection_results",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m1`

tokens prompt=932 completion=163 latency=5.86s

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
{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility_results","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"extrema_count","input_binding":{}},{"step":3,"tool":"anomaly_detect","output_key":"anomaly_detection_results","input_binding":{}}],"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns using the selected tools."}
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

- sliding_stats: Sliding-window mean/std for local volatility.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, window=int (alias window_size)}
  returns: {series=per-series windowed mean/std aggregates and max_local_std}
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, z_threshold=float (default 3.0)}
  returns: {series=anomaly count/indices and max absolute z-score}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context, specifically focusing on time series with index 1. This involves calculating local volatility through sliding stats, identifying local extrema, and detecting anomalies based on z-scores.",
  "calls": [
    {
      "step": 1,
      "tool": "sliding_stats",
      "args": {"series_index": 1}
    },
    {
      "step": 2,
      "tool": "local_extrema",
      "args": {"series_index": 1}
    },
    {
      "step": 3,
      "tool": "anomaly_detect",
      "args": {"series_index": 1}
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m1`

tokens prompt=1410 completion=504 latency=18.01s

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
{"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local behavior patterns exist and can be identified.","required_evidence":["sliding_window_statistics","local_extrema_counts"]},{"claim":"Anomalies can be detected.","required_evidence":["outlier_spikes_in_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare multiple small segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measure local volatility and rolling level variations for pattern recognition.","supports_evidence":["sliding_window_statistics"]},{"tool":"local_extrema","reason":"Count local peaks and troughs to understand local behavior patterns.","supports_evidence":["local_extrema_counts"]},{"tool":"anomaly_detect","reason":"Detect anomalies via z-score threshold in sliding windows.","supports_evidence":["outlier_spikes_in_windows"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "sliding_stats",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "window": 29,
      "mean_of_means": -18.551806872395673,
      "mean_of_stds": 2.777843427701618,
      "max_local_std": 7.5853416277705055
    },
    "error": null,
    "args_fingerprint": "5d90c6e3697596cfb881b17b747f76e320a9ebe9"
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
      "n_peaks": 5,
      "n_troughs": 5,
      "peak_idx": [
        88,
        247,
        249,
        385,
        504
      ],
      "trough_idx": [
        87,
        148,
        303,
        386,
        505
      ]
    },
    "error": null,
    "args_fingerprint": "31139f7e956301f570b30f3a308473f914523713"
  },
  {
    "call_id": "short:step3",
    "step": 3,
    "tool_name": "anomaly_detect",
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
      "z_threshold": 3.0,
      "n_anomalies": 0,
      "anomaly_indices": [],
      "max_abs_z": 2.65397557979793
    },
    "error": null,
    "args_fingerprint": "9ee1de07f72732a041d0e186f599357a414ae94b"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Local behavior has been analyzed using sliding window statistics and counts of local extrema. No anomalies were detected within the specified z-score threshold.",
  "scale": "short",
  "observations": ["Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria."],
  "evidence_intervals": ["Entire series"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Local behavior patterns exist and can be identified.",
      "evidence": [
        {
          "type": "sliding_window_statistics",
          "value": {"mean_of_means": -18.551806872395673, "mean_of_stds": 2.777843427701618, "max_local_std": 7.5853416277705055},
          "source_tool": "sliding_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        },
        {
          "type": "local_extrema_counts",
          "value": {"n_peaks": 5, "n_troughs": 5},
          "source_tool": "local_extrema",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "local_behavior"
    },
    {
      "claim": "Anomalies can be detected.",
      "evidence": [
        {
          "type": "outlier_spikes_in_windows",
          "value": {"z_threshold": 3.0, "n_anomalies": 0, "max_abs_z": 2.65397557979793},
          "source_tool": "anomaly_detect",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomaly_detection"
    }
  ],
  "coverage": {"local_behavior": "tool_supported", "anomaly_detection": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4069 completion=258 latency=10.29s

### INPUT (system)

```
You are a medium-scale Homogeneous Temporal Understanding Agent.
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
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
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
{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify repeated patterns and periodicity within a single time series to support waveform classification. This requires measuring periodic structures and validating these measurements across different sections of the series.",
  "evidence_plan": {
    "objective": "Identify repeated patterns and periodicity to support waveform classification.",
    "claims_to_support": [
      {"claim": "The series contains repeated patterns.", "required_evidence": ["periodic_structure"]},
      {"claim": "A seasonal period exists in the series.", "required_evidence": ["dominant_period"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["periodicity across various sections"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "To detect a dominant spectral period that suggests repeated patterns.", "supports_evidence": ["dominant_period"]},
      {"tool": "seas_acf", "reason": "To confirm periodicity and estimate a seasonal period for the identified dominant frequency.", "supports_evidence": ["seasonal_period"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=766 completion=142 latency=5.10s

### INPUT (system)

```
You are a medium-scale Homogeneous Agent at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["periodic_structure"]},{"claim":"A seasonal period exists in the series.","required_evidence":["dominant_period"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect a dominant spectral period that suggests repeated patterns.","supports_evidence":["dominant_period"]},{"tool":"seas_acf","reason":"To confirm periodicity and estimate a seasonal period for the identified dominant frequency.","supports_evidence":["seasonal_period"]}],"no_tool_decision":null},"reasoning":"The objective is to identify repeated patterns and periodicity within a single time series to support waveform classification. This requires measuring periodic structures and validating these measurements across different sections of the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- seas_acf
  inputs: series_window, lag
  outputs: seas_acf1, strength_hint
  often_combined_with: autocorr, stl_strength, fft_period
- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
</io_concepts>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to detect a dominant spectral period that suggests repeated patterns. Then, we apply 'seas_acf' to confirm periodicity and estimate a seasonal period for the identified dominant frequency.",
  "workflow": [
    {
      "step": 1,
      "tool": "fft_period",
      "output_key": "dominant_period",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "seas_acf",
      "output_key": "seasonal_period",
      "input_binding": {"lag": "$step1.dominant_period"}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=867 completion=142 latency=5.13s

### INPUT (system)

```
You are a medium-scale Homogeneous Agent at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"seasonal_period","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to detect a dominant spectral period that suggests repeated patterns. Then, we apply 'seas_acf' to confirm periodicity and estimate a seasonal period for the identified dominant frequency."}
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
- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to detect a dominant spectral period that suggests repeated patterns. Then, we apply 'seas_acf' to confirm periodicity and estimate a seasonal period for the identified dominant frequency.",
  "calls": [
    {
      "step": 1,
      "tool": "fft_period",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "seas_acf",
      "args": {
        "series_index": 1,
        "lag": "$step1.dominant_period"
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=1127 completion=547 latency=19.52s

### INPUT (system)

```
You are a medium-scale Homogeneous Agent at Stage 5: Evidence Integration.
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
  "scale": "medium",
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
{"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["periodic_structure"]},{"claim":"A seasonal period exists in the series.","required_evidence":["dominant_period"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect a dominant spectral period that suggests repeated patterns.","supports_evidence":["dominant_period"]},{"tool":"seas_acf","reason":"To confirm periodicity and estimate a seasonal period for the identified dominant frequency.","supports_evidence":["seasonal_period"]}],"no_tool_decision":null},"reasoning":"The objective is to identify repeated patterns and periodicity within a single time series to support waveform classification. This requires measuring periodic structures and validating these measurements across different sections of the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "medium:step1",
    "step": 1,
    "tool_name": "fft_period",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "dominant_period": 599.0,
      "spectral_strength": 0.17524073250280806,
      "period_trusted": false,
      "warnings": [
        "dominant_period_near_series_length"
      ]
    },
    "error": null,
    "args_fingerprint": "726ee7605c7aac2e5823de42d4c34d3c89859438"
  },
  {
    "call_id": "medium:step2",
    "step": 2,
    "tool_name": "seas_acf",
    "arguments": {
      "series_index": 1,
      "lag": "$step1.dominant_period"
    },
    "resolved_arguments": {
      "series_index": 1,
      "lag": 599.0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "lag": 599,
      "seas_acf1": null,
      "strength_hint": "unavailable",
      "note": "lag 599 invalid for length 599"
    },
    "error": null,
    "args_fingerprint": "2ccd068769598ae281eace53d0f2d13063c05494"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify repeated patterns and periodicity within a single time series to support waveform classification. The FFT analysis found a dominant spectral period of 599.0, which is suspiciously close to the length of the time series, raising concerns about its validity. Subsequent autocorrelation analysis failed due to an invalid lag, further complicating the determination of periodicity. Therefore, there's insufficient trusted evidence to confidently assert the presence of repeated patterns or a reliable seasonal period within this series.",
  "scale": "medium",
  "observations": ["The analysis found a dominant spectral period of 599.0, which raises suspicion due to its proximity to the series length. The autocorrelation analysis failed due to an invalid lag, leaving open questions about the series' periodicity and seasonal structure."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The series contains repeated patterns.",
      "evidence": [
        {
          "type": "periodic_structure",
          "value": "unavailable",
          "source_tool": "seas_acf",
          "call_id": "medium:step2",
          "provenance": "tool"
        },
        {
          "type": "dominant_period",
          "value": 599.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "repeated_patterns"
    },
    {
      "claim": "A seasonal period exists in the series.",
      "evidence": [
        {
          "type": "dominant_period",
          "value": 599.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        },
        {
          "type": "seasonal_period",
          "value": "unavailable",
          "source_tool": "seas_acf",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "seasonal_period"
    }
  ],
  "coverage": {"repeated_patterns": "unresolved", "seasonal_period": "unresolved"},
  "unresolved_claims": ["The series contains repeated patterns.", "A seasonal period exists in the series."]
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m1`

tokens prompt=4097 completion=320 latency=12.61s

### INPUT (system)

```
You are a medium-scale Homogeneous Temporal Understanding Agent.
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
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
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
{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['The series contains repeated patterns.', 'A seasonal period exists in the series.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify repeated patterns and periodicity in a univariate time series to support waveform classification. This involves detecting periodic structures and validating their presence across various sections of the series.",
  "evidence_plan": {
    "objective": "Identify repeated patterns and periodicity to support waveform classification.",
    "claims_to_support": [
      {"claim": "The series contains repeated patterns.", "required_evidence": ["seasonal_period"]},
      {"claim": "A seasonal period exists in the series.", "required_evidence": ["periodicity_across_various_sections"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["periodicity across various sections"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "To detect the dominant period that might represent the repeated patterns.", "supports_evidence": ["seasonal_period"]},
      {"tool": "seas_acf", "reason": "To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.", "supports_evidence": ["periodicity_across_various_sections"]},
      {"tool": "waveform_features", "reason": "To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.", "supports_evidence": ["waveform_classification"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m1`

tokens prompt=862 completion=163 latency=5.86s

### INPUT (system)

```
You are a medium-scale Homogeneous Agent at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["seasonal_period"]},{"claim":"A seasonal period exists in the series.","required_evidence":["periodicity_across_various_sections"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that might represent the repeated patterns.","supports_evidence":["seasonal_period"]},{"tool":"seas_acf","reason":"To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.","supports_evidence":["periodicity_across_various_sections"]},{"tool":"waveform_features","reason":"To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.","supports_evidence":["waveform_classification"]}],"no_tool_decision":null},"reasoning":"The objective is to identify repeated patterns and periodicity in a univariate time series to support waveform classification. This involves detecting periodic structures and validating their presence across various sections of the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- seas_acf
  inputs: series_window, lag
  outputs: seas_acf1, strength_hint
  often_combined_with: autocorr, stl_strength, fft_period
- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
- waveform_features
  inputs: series, optional start/end
  outputs: waveform_hint, jump_ratio, harmonic, template_match
  often_combined_with: fft_period, step_levels, diff_stats
</io_concepts>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series.",
  "workflow": [
    {
      "step": 1,
      "tool": "fft_period",
      "output_key": "dominant_period",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "seas_acf",
      "output_key": "strength_hint",
      "input_binding": {"lag": "$step1.dominant_period"}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m1`

tokens prompt=996 completion=164 latency=5.90s

### INPUT (system)

```
You are a medium-scale Homogeneous Agent at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series."}
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
- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
- waveform_features: Classify waveform shape (sine/square/triangle/sawtooth/ambiguous) using jump ratio, plateau clustering, harmonic structure, and folded-template match. Do NOT treat FFT period alone as evidence of a sine wave.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=waveform_hint plus jump/plateau/harmonic/template-match diagnostics}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series.",
  "calls": [
    {
      "step": 1,
      "tool": "fft_period",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "seas_acf",
      "args": {
        "series_index": 1,
        "lag": "$step1.dominant_period"
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m1`

tokens prompt=1182 completion=440 latency=15.68s

### INPUT (system)

```
You are a medium-scale Homogeneous Agent at Stage 5: Evidence Integration.
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
  "scale": "medium",
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
{"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["seasonal_period"]},{"claim":"A seasonal period exists in the series.","required_evidence":["periodicity_across_various_sections"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that might represent the repeated patterns.","supports_evidence":["seasonal_period"]},{"tool":"seas_acf","reason":"To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.","supports_evidence":["periodicity_across_various_sections"]},{"tool":"waveform_features","reason":"To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.","supports_evidence":["waveform_classification"]}],"no_tool_decision":null},"reasoning":"The objective is to identify repeated patterns and periodicity in a univariate time series to support waveform classification. This involves detecting periodic structures and validating their presence across various sections of the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "medium:step1",
    "step": 1,
    "tool_name": "fft_period",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "dominant_period": 599.0,
      "spectral_strength": 0.17524073250280806,
      "period_trusted": false,
      "warnings": [
        "dominant_period_near_series_length"
      ]
    },
    "error": null,
    "args_fingerprint": "726ee7605c7aac2e5823de42d4c34d3c89859438"
  },
  {
    "call_id": "medium:step2",
    "step": 2,
    "tool_name": "seas_acf",
    "arguments": {
      "series_index": 1,
      "lag": "$step1.dominant_period"
    },
    "resolved_arguments": {
      "series_index": 1,
      "lag": 599.0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "lag": 599,
      "seas_acf1": null,
      "strength_hint": "unavailable",
      "note": "lag 599 invalid for length 599"
    },
    "error": null,
    "args_fingerprint": "2ccd068769598ae281eace53d0f2d13063c05494"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify repeated patterns and periodicity in a univariate time series to support waveform classification. The FFT analysis (fft_period) suggested a dominant period of 599 with a spectral strength of 0.175, which is nearly equal to the length of the series. However, this period is not trusted due to its proximity to the series length. Subsequent seasonal autocorrelation (seas_acf) analysis aimed to validate the existence of a seasonal period, but it failed due to an invalid lag value for the series length.",
  "scale": "medium",
  "observations": ["FFT analysis detected a dominant period close to the series length, but it's not trusted.", "Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The series contains repeated patterns.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 599,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "qualified",
      "maps_to_measurement": "repeated_patterns"
    },
    {
      "claim": "A seasonal period exists in the series.",
      "evidence": [
        {
          "type": "periodicity_across_various_sections",
          "value": "unavailable",
          "source_tool": "seas_acf",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "unresolved",
      "maps_to_measurement": "seasonal_period"
    }
  ],
  "coverage": {"repeated_patterns": "qualified", "seasonal_period": "unresolved"},
  "unresolved_claims": ["A seasonal period exists in the series."]
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4068 completion=260 latency=10.33s

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
{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series.",
  "evidence_plan": {
    "objective": "Analyze the overall structure for global trends and dependencies.",
    "claims_to_support": [
      {"claim": "There exists a global trend in the time series.", "required_evidence": ["slope", "direction"]},
      {"claim": "There are long-term dependencies in the time series.", "required_evidence": ["autocorrelation"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["analyze the complete sequence"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "segment_trend", "reason": "To detect the overall trend direction and slope of the time series.", "supports_evidence": ["slope", "direction"]},
      {"tool": "autocorr", "reason": "To measure long-term dependencies through autocorrelation.", "supports_evidence": ["autocorrelation"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=760 completion=163 latency=5.81s

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
{"evidence_plan":{"objective":"Analyze the overall structure for global trends and dependencies.","claims_to_support":[{"claim":"There exists a global trend in the time series.","required_evidence":["slope","direction"]},{"claim":"There are long-term dependencies in the time series.","required_evidence":["autocorrelation"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["analyze the complete sequence"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To detect the overall trend direction and slope of the time series.","supports_evidence":["slope","direction"]},{"tool":"autocorr","reason":"To measure long-term dependencies through autocorrelation.","supports_evidence":["autocorrelation"]}],"no_tool_decision":null},"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- autocorr
  inputs: series, max_lag or lags[]
  outputs: best_lag, acf, acf_at_lags
  depends: max_lag should cover candidate period when validating fft_period
</io_concepts>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series. We will use segment_trend to detect the overall trend direction and slope of the time series, and then use autocorr to measure long-term dependencies through autocorrelation.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "trend_segment",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "autocorr",
      "output_key": "autocorr_result",
      "input_binding": {"series": "$step1.series"}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=896 completion=130 latency=4.70s

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
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"autocorr","output_key":"autocorr_result","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series. We will use segment_trend to detect the overall trend direction and slope of the time series, and then use autocorr to measure long-term dependencies through autocorrelation."}
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
- autocorr: Autocorrelation up to max_lag (full ACF list). Optional lags=[...] returns acf_at_lags for specific lags.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, max_lag=int, lags=optional list of specific lags}
  returns: {series=best_lag and full autocorrelation values through max_lag; optional acf_at_lags}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "Analyze the overall structure for global trends and dependencies by detecting the overall trend direction and slope of the time series, and then measuring long-term dependencies through autocorrelation.",
  "calls": [
    {
      "step": 1,
      "tool": "segment_trend",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "autocorr",
      "args": {
        "series_index": 1,
        "max_lag": 20
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1604 completion=449 latency=16.15s

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
{"evidence_plan":{"objective":"Analyze the overall structure for global trends and dependencies.","claims_to_support":[{"claim":"There exists a global trend in the time series.","required_evidence":["slope","direction"]},{"claim":"There are long-term dependencies in the time series.","required_evidence":["autocorrelation"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["analyze the complete sequence"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To detect the overall trend direction and slope of the time series.","supports_evidence":["slope","direction"]},{"tool":"autocorr","reason":"To measure long-term dependencies through autocorrelation.","supports_evidence":["autocorrelation"]}],"no_tool_decision":null},"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
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
      "slope": 0.13752508361204013,
      "direction": "upward",
      "direction_class": "upward",
      "trend_method": "endpoint",
      "mean": -16.869799666110183,
      "std": 29.073289239528357,
      "start_value": -21.95,
      "end_value": 60.29
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "autocorr",
    "arguments": {
      "series_index": 1,
      "max_lag": 20
    },
    "resolved_arguments": {
      "series_index": 1,
      "max_lag": 20
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "max_lag": 20,
      "best_lag": 1,
      "acf": [
        0.9933703558016056,
        0.9867055929542156,
        0.9800089578860637,
        0.9732750465749592,
        0.9665066179952697,
        0.9597066979705894,
        0.9528784351666171,
        0.9460161587554587,
        0.9391184156821324,
        0.9321910802236684,
        0.9252397633867561,
        0.9182603830706991,
        0.9112500345243497,
        0.9042072407863354,
        0.8971322520954204,
        0.8900248365731779,
        0.8828861044084975,
        0.8757161328270339,
        0.8685176486212105,
        0.8612920904358338
      ],
      "acf_at_lags": {}
    },
    "error": null,
    "args_fingerprint": "4c5402c38b7224460d6af99a8080d7d8833ea0c9"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective at the long scale is to analyze the overall structure for global trends and dependencies. The executed tools indicate a clear upward trend with a positive slope and significant long-term dependencies based on the high autocorrelation values.",
  "scale": "long",
  "observations": [
    "There is a global upward trend in the time series with a positive slope of approximately 0.138.",
    "The time series exhibits strong long-term dependencies with a maximum lag of 20."
  ],
  "evidence_intervals": [],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There exists a global trend in the time series.",
      "evidence": [
        {
          "type": "slope",
          "value": 0.13752508361204013,
          "source_tool": "segment_trend",
          "call_id": "long:step1",
          "provenance": "tool"
        },
        {
          "type": "direction",
          "value": "upward",
          "source_tool": "segment_trend",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trends"
    },
    {
      "claim": "There are long-term dependencies in the time series.",
      "evidence": [
        {
          "type": "autocorrelation",
          "value": 0.9933703558016056,
          "source_tool": "autocorr",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "long_term_dependence"
    }
  ],
  "coverage": {"global_trends": "tool_supported", "long_term_dependence": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=8358 completion=288 latency=13.06s

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
{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<task_summary>
Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Local behavior has been analyzed using sliding window statistics and counts of local extrema. No anomalies were detected within the specified z-score threshold.","scale":"short","observations":["Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 29, \"mean_of_means\": -18.551806872395673, \"mean_of_stds\": 2.777843427701618, \"max_local_std\": 7.5853416277705055}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 5, \"n_troughs\": 5, \"peak_idx\": [88, 247, 249, 385, 504], \"trough_idx\": [87, 148, 303, 386, 505]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.65397557979793}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local behavior patterns exist and can be identified.","required_evidence":["sliding_window_statistics","local_extrema_counts"]},{"claim":"Anomalies can be detected.","required_evidence":["outlier_spikes_in_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare multiple small segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measure local volatility and rolling level variations for pattern recognition.","supports_evidence":["sliding_window_statistics"]},{"tool":"local_extrema","reason":"Count local peaks and troughs to understand local behavior patterns.","supports_evidence":["local_extrema_counts"]},{"tool":"anomaly_detect","reason":"Detect anomalies via z-score threshold in sliding windows.","supports_evidence":["outlier_spikes_in_windows"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility_results","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"extrema_count","input_binding":{}},{"step":3,"tool":"anomaly_detect","output_key":"anomaly_detection_results","input_binding":{}}],"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns using the selected tools."},"structured_observations":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"coverage":{"local_behavior":"tool_supported","anomaly_detection":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":29,"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":5,"n_troughs":5,"peak_idx":[88,247,249,385,504],"trough_idx":[87,148,303,386,505]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step3","step":3,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.65397557979793},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify repeated patterns and periodicity in a univariate time series to support waveform classification. The FFT analysis (fft_period) suggested a dominant period of 599 with a spectral strength of 0.175, which is nearly equal to the length of the series. However, this period is not trusted due to its proximity to the series length. Subsequent seasonal autocorrelation (seas_acf) analysis aimed to validate the existence of a seasonal period, but it failed due to an invalid lag value for the series length.","scale":"medium","observations":["FFT analysis detected a dominant period close to the series length, but it's not trusted.","Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 599.0, \"spectral_strength\": 0.17524073250280806, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 599.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 599, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 599 invalid for length 599\"}, \"error\": null, \"args_fingerprint\": \"2ccd068769598ae281eace53d0f2d13063c05494\"}"],"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["seasonal_period"]},{"claim":"A seasonal period exists in the series.","required_evidence":["periodicity_across_various_sections"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that might represent the repeated patterns.","supports_evidence":["seasonal_period"]},{"tool":"seas_acf","reason":"To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.","supports_evidence":["periodicity_across_various_sections"]},{"tool":"waveform_features","reason":"To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.","supports_evidence":["waveform_classification"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series."},"structured_observations":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"coverage":{"repeated_patterns":"qualified","seasonal_period":"unresolved"},"unresolved_claims":["A seasonal period exists in the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":599.0,"spectral_strength":0.17524073250280806,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":599.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":599,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 599 invalid for length 599"},"error":null,"args_fingerprint":"2ccd068769598ae281eace53d0f2d13063c05494"}],"skipped_stages":[]},"long":{"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. The executed tools indicate a clear upward trend with a positive slope and significant long-term dependencies based on the high autocorrelation values.","scale":"long","observations":["There is a global upward trend in the time series with a positive slope of approximately 0.138.","The time series exhibits strong long-term dependencies with a maximum lag of 20."],"evidence_intervals":[],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 0.13752508361204013, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": -16.869799666110183, \"std\": 29.073289239528357, \"start_value\": -21.95, \"end_value\": 60.29}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.9933703558016056, 0.9867055929542156, 0.9800089578860637, 0.9732750465749592, 0.9665066179952697, 0.9597066979705894, 0.9528784351666171, 0.9460161587554587, 0.9391184156821324, 0.9321910802236684, 0.9252397633867561, 0.9182603830706991, 0.9112500345243497, 0.9042072407863354, 0.8971322520954204, 0.8900248365731779, 0.8828861044084975, 0.8757161328270339, 0.8685176486212105, 0.8612920904358338], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure for global trends and dependencies.","claims_to_support":[{"claim":"There exists a global trend in the time series.","required_evidence":["slope","direction"]},{"claim":"There are long-term dependencies in the time series.","required_evidence":["autocorrelation"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["analyze the complete sequence"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To detect the overall trend direction and slope of the time series.","supports_evidence":["slope","direction"]},{"tool":"autocorr","reason":"To measure long-term dependencies through autocorrelation.","supports_evidence":["autocorrelation"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"autocorr","output_key":"autocorr_result","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series. We will use segment_trend to detect the overall trend direction and slope of the time series, and then use autocorr to measure long-term dependencies through autocorrelation."},"structured_observations":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}],"coverage":{"global_trends":"tool_supported","long_term_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":0.13752508361204013,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":-16.869799666110183,"std":29.073289239528357,"start_value":-21.95,"end_value":60.29},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.9933703558016056,0.9867055929542156,0.9800089578860637,0.9732750465749592,0.9665066179952697,0.9597066979705894,0.9528784351666171,0.9460161587554587,0.9391184156821324,0.9321910802236684,0.9252397633867561,0.9182603830706991,0.9112500345243497,0.9042072407863354,0.8971322520954204,0.8900248365731779,0.8828861044084975,0.8757161328270339,0.8685176486212105,0.8612920904358338],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria. FFT analysis detected a dominant period close to the series length, but it's not trusted. Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length. There is a global upward trend in the time series with a positive slope of approximately 0.138. The time series exhibits strong long-term dependencies with a maximum lag of 20.","structured_by_scale":{"short":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"medium":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"long":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides insights into the behavior and structure of Time Series 1, including local behavior, a potential dominant period (which is not trusted), and global trends. The objective is to match Time Series 1 against known waveform templates (sine, square, triangle, sawtooth) and determine the most similar pattern. To achieve this, we need to compute pairwise similarity and identify change locations between Time Series 1 and the candidate waveforms.",
  "evidence_plan": {
    "objective": "Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.",
    "claims_to_support": [
      {
        "claim": "Time Series 1 is most similar to one of the provided waveforms.",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "Locations of significant changes or matches have been identified.",
        "required_evidence": ["change_location"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["cross-check all four candidate types"]
  },
  "capability_selection": {
    "selected_tools": [
      "pairwise_distance",
      "waveform_features"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=6925 completion=972 latency=38.82s

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
{"evidence_plan":{"objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Local behavior has been analyzed using sliding window statistics and counts of local extrema. No anomalies were detected within the specified z-score threshold.","scale":"short","observations":["Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 29, \"mean_of_means\": -18.551806872395673, \"mean_of_stds\": 2.777843427701618, \"max_local_std\": 7.5853416277705055}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 5, \"n_troughs\": 5, \"peak_idx\": [88, 247, 249, 385, 504], \"trough_idx\": [87, 148, 303, 386, 505]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.65397557979793}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local behavior patterns exist and can be identified.","required_evidence":["sliding_window_statistics","local_extrema_counts"]},{"claim":"Anomalies can be detected.","required_evidence":["outlier_spikes_in_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare multiple small segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measure local volatility and rolling level variations for pattern recognition.","supports_evidence":["sliding_window_statistics"]},{"tool":"local_extrema","reason":"Count local peaks and troughs to understand local behavior patterns.","supports_evidence":["local_extrema_counts"]},{"tool":"anomaly_detect","reason":"Detect anomalies via z-score threshold in sliding windows.","supports_evidence":["outlier_spikes_in_windows"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility_results","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"extrema_count","input_binding":{}},{"step":3,"tool":"anomaly_detect","output_key":"anomaly_detection_results","input_binding":{}}],"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns using the selected tools."},"structured_observations":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"coverage":{"local_behavior":"tool_supported","anomaly_detection":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":29,"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":5,"n_troughs":5,"peak_idx":[88,247,249,385,504],"trough_idx":[87,148,303,386,505]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step3","step":3,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.65397557979793},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify repeated patterns and periodicity in a univariate time series to support waveform classification. The FFT analysis (fft_period) suggested a dominant period of 599 with a spectral strength of 0.175, which is nearly equal to the length of the series. However, this period is not trusted due to its proximity to the series length. Subsequent seasonal autocorrelation (seas_acf) analysis aimed to validate the existence of a seasonal period, but it failed due to an invalid lag value for the series length.","scale":"medium","observations":["FFT analysis detected a dominant period close to the series length, but it's not trusted.","Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 599.0, \"spectral_strength\": 0.17524073250280806, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 599.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 599, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 599 invalid for length 599\"}, \"error\": null, \"args_fingerprint\": \"2ccd068769598ae281eace53d0f2d13063c05494\"}"],"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["seasonal_period"]},{"claim":"A seasonal period exists in the series.","required_evidence":["periodicity_across_various_sections"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that might represent the repeated patterns.","supports_evidence":["seasonal_period"]},{"tool":"seas_acf","reason":"To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.","supports_evidence":["periodicity_across_various_sections"]},{"tool":"waveform_features","reason":"To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.","supports_evidence":["waveform_classification"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series."},"structured_observations":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"coverage":{"repeated_patterns":"qualified","seasonal_period":"unresolved"},"unresolved_claims":["A seasonal period exists in the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":599.0,"spectral_strength":0.17524073250280806,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":599.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":599,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 599 invalid for length 599"},"error":null,"args_fingerprint":"2ccd068769598ae281eace53d0f2d13063c05494"}],"skipped_stages":[]},"long":{"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. The executed tools indicate a clear upward trend with a positive slope and significant long-term dependencies based on the high autocorrelation values.","scale":"long","observations":["There is a global upward trend in the time series with a positive slope of approximately 0.138.","The time series exhibits strong long-term dependencies with a maximum lag of 20."],"evidence_intervals":[],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 0.13752508361204013, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": -16.869799666110183, \"std\": 29.073289239528357, \"start_value\": -21.95, \"end_value\": 60.29}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.9933703558016056, 0.9867055929542156, 0.9800089578860637, 0.9732750465749592, 0.9665066179952697, 0.9597066979705894, 0.9528784351666171, 0.9460161587554587, 0.9391184156821324, 0.9321910802236684, 0.9252397633867561, 0.9182603830706991, 0.9112500345243497, 0.9042072407863354, 0.8971322520954204, 0.8900248365731779, 0.8828861044084975, 0.8757161328270339, 0.8685176486212105, 0.8612920904358338], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure for global trends and dependencies.","claims_to_support":[{"claim":"There exists a global trend in the time series.","required_evidence":["slope","direction"]},{"claim":"There are long-term dependencies in the time series.","required_evidence":["autocorrelation"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["analyze the complete sequence"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To detect the overall trend direction and slope of the time series.","supports_evidence":["slope","direction"]},{"tool":"autocorr","reason":"To measure long-term dependencies through autocorrelation.","supports_evidence":["autocorrelation"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"autocorr","output_key":"autocorr_result","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series. We will use segment_trend to detect the overall trend direction and slope of the time series, and then use autocorr to measure long-term dependencies through autocorrelation."},"structured_observations":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}],"coverage":{"global_trends":"tool_supported","long_term_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":0.13752508361204013,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":-16.869799666110183,"std":29.073289239528357,"start_value":-21.95,"end_value":60.29},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.9933703558016056,0.9867055929542156,0.9800089578860637,0.9732750465749592,0.9665066179952697,0.9597066979705894,0.9528784351666171,0.9460161587554587,0.9391184156821324,0.9321910802236684,0.9252397633867561,0.9182603830706991,0.9112500345243497,0.9042072407863354,0.8971322520954204,0.8900248365731779,0.8828861044084975,0.8757161328270339,0.8685176486212105,0.8612920904358338],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria. FFT analysis detected a dominant period close to the series length, but it's not trusted. Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length. There is a global upward trend in the time series with a positive slope of approximately 0.138. The time series exhibits strong long-term dependencies with a maximum lag of 20.","structured_by_scale":{"short":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"medium":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"long":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Without direct evidence from tool executions for waveform matching, the temporal profile analysis provides limited insights into pattern similarity with sine, square, triangle, and sawtooth waves. Local behavior shows recognizable patterns but no anomalies, indicating regularity but not specificity to a particular waveform. Medium-scale analysis hints at potential patterns near the series length but lacks conclusive evidence for seasonality. Long-term analysis identifies a global upward trend and strong long-term dependencies, which are more indicative of non-waveform characteristics such as linear growth.",
  "role": "matching",
  "hypothesis": "Time Series 1 does not show clear indicators that match any of the typical waveforms (sine, square, triangle, sawtooth) well, but regular behavior suggests some underlying periodicity.",
  "evidence": ["Local behavior analysis using sliding window statistics and extrema counts indicates recognizable patterns but no anomalies.", "Medium-scale FFT analysis suggests a period near the series length without validation.", "Long-term analysis reveals a global upward trend and strong dependencies indicative of linear growth rather than repetitive waveforms."],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "short:step3", "medium:step1", "medium:step2", "long:step1", "long:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Recognizable local behavior patterns exist in the series.",
      "evidence": [
        {
          "type": "sliding_window_statistics",
          "value": {
            "mean_of_means": -18.551806872395673,
            "mean_of_stds": 2.777843427701618,
            "max_local_std": 7.5853416277705055
          },
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        },
        {
          "type": "local_extrema_counts",
          "value": {
            "n_peaks": 5,
            "n_troughs": 5
          },
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "No anomalies were detected within the series.",
      "evidence": [
        {
          "type": "outlier_spikes_in_windows",
          "value": {
            "z_threshold": 3.0,
            "n_anomalies": 0,
            "max_abs_z": 2.65397557979793
          },
          "provenance": "tool",
          "ref": "short:step3",
          "call_id": "short:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "A dominant period was detected using FFT, but it is near the series length and not trusted.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 599,
          "provenance": "tool",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        }
      ],
      "confidence": "qualified"
    },
    {
      "claim": "Long-term analysis indicates a global upward trend and strong dependencies.",
      "evidence": [
        {
          "type": "slope",
          "value": 0.13752508361204013,
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        },
        {
          "type": "autocorrelation",
          "value": 0.9933703558016056,
          "provenance": "tool",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": ["A seasonal period exists in the series."]
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=8375 completion=326 latency=14.55s

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
{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which waveform (sine, square, triangle, sawtooth) Time Series 1 most closely resembles based on provided data points. This involves visual or mathematical comparison against known waveform templates.","task_summary":"Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.","target_output":"The type of waveform Time Series 1 most resembles.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Analyze local behavior for pattern recognition and anomaly detection.","required_measurements":["local_behavior","anomaly_detection"],"validation_requirements":["compare multiple small segments"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns and periodicity to support waveform classification.","required_measurements":["repeated_patterns","seasonal_period"],"validation_requirements":["periodicity across various sections"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure for global trends and dependencies.","required_measurements":["global_trends","long_term_dependence"],"validation_requirements":["analyze the complete sequence"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Time Series 1 is accurately matched to one of the candidate waveforms.","All possible waveform comparisons are evaluated and validated."],"notes":"Ensure all waveform properties (e.g., peaks, valleys, symmetry) are considered during comparison."}
</plan_context>

<task_summary>
Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Local behavior has been analyzed using sliding window statistics and counts of local extrema. No anomalies were detected within the specified z-score threshold.","scale":"short","observations":["Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 29, \"mean_of_means\": -18.551806872395673, \"mean_of_stds\": 2.777843427701618, \"max_local_std\": 7.5853416277705055}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 5, \"n_troughs\": 5, \"peak_idx\": [88, 247, 249, 385, 504], \"trough_idx\": [87, 148, 303, 386, 505]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.65397557979793}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local behavior patterns exist and can be identified.","required_evidence":["sliding_window_statistics","local_extrema_counts"]},{"claim":"Anomalies can be detected.","required_evidence":["outlier_spikes_in_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare multiple small segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measure local volatility and rolling level variations for pattern recognition.","supports_evidence":["sliding_window_statistics"]},{"tool":"local_extrema","reason":"Count local peaks and troughs to understand local behavior patterns.","supports_evidence":["local_extrema_counts"]},{"tool":"anomaly_detect","reason":"Detect anomalies via z-score threshold in sliding windows.","supports_evidence":["outlier_spikes_in_windows"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility_results","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"extrema_count","input_binding":{}},{"step":3,"tool":"anomaly_detect","output_key":"anomaly_detection_results","input_binding":{}}],"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns using the selected tools."},"structured_observations":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"coverage":{"local_behavior":"tool_supported","anomaly_detection":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":29,"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":5,"n_troughs":5,"peak_idx":[88,247,249,385,504],"trough_idx":[87,148,303,386,505]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step3","step":3,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.65397557979793},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify repeated patterns and periodicity in a univariate time series to support waveform classification. The FFT analysis (fft_period) suggested a dominant period of 599 with a spectral strength of 0.175, which is nearly equal to the length of the series. However, this period is not trusted due to its proximity to the series length. Subsequent seasonal autocorrelation (seas_acf) analysis aimed to validate the existence of a seasonal period, but it failed due to an invalid lag value for the series length.","scale":"medium","observations":["FFT analysis detected a dominant period close to the series length, but it's not trusted.","Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 599.0, \"spectral_strength\": 0.17524073250280806, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 599.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 599, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 599 invalid for length 599\"}, \"error\": null, \"args_fingerprint\": \"2ccd068769598ae281eace53d0f2d13063c05494\"}"],"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["seasonal_period"]},{"claim":"A seasonal period exists in the series.","required_evidence":["periodicity_across_various_sections"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that might represent the repeated patterns.","supports_evidence":["seasonal_period"]},{"tool":"seas_acf","reason":"To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.","supports_evidence":["periodicity_across_various_sections"]},{"tool":"waveform_features","reason":"To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.","supports_evidence":["waveform_classification"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series."},"structured_observations":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"coverage":{"repeated_patterns":"qualified","seasonal_period":"unresolved"},"unresolved_claims":["A seasonal period exists in the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":599.0,"spectral_strength":0.17524073250280806,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":599.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":599,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 599 invalid for length 599"},"error":null,"args_fingerprint":"2ccd068769598ae281eace53d0f2d13063c05494"}],"skipped_stages":[]},"long":{"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. The executed tools indicate a clear upward trend with a positive slope and significant long-term dependencies based on the high autocorrelation values.","scale":"long","observations":["There is a global upward trend in the time series with a positive slope of approximately 0.138.","The time series exhibits strong long-term dependencies with a maximum lag of 20."],"evidence_intervals":[],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 0.13752508361204013, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": -16.869799666110183, \"std\": 29.073289239528357, \"start_value\": -21.95, \"end_value\": 60.29}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.9933703558016056, 0.9867055929542156, 0.9800089578860637, 0.9732750465749592, 0.9665066179952697, 0.9597066979705894, 0.9528784351666171, 0.9460161587554587, 0.9391184156821324, 0.9321910802236684, 0.9252397633867561, 0.9182603830706991, 0.9112500345243497, 0.9042072407863354, 0.8971322520954204, 0.8900248365731779, 0.8828861044084975, 0.8757161328270339, 0.8685176486212105, 0.8612920904358338], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure for global trends and dependencies.","claims_to_support":[{"claim":"There exists a global trend in the time series.","required_evidence":["slope","direction"]},{"claim":"There are long-term dependencies in the time series.","required_evidence":["autocorrelation"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["analyze the complete sequence"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To detect the overall trend direction and slope of the time series.","supports_evidence":["slope","direction"]},{"tool":"autocorr","reason":"To measure long-term dependencies through autocorrelation.","supports_evidence":["autocorrelation"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"autocorr","output_key":"autocorr_result","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series. We will use segment_trend to detect the overall trend direction and slope of the time series, and then use autocorr to measure long-term dependencies through autocorrelation."},"structured_observations":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}],"coverage":{"global_trends":"tool_supported","long_term_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":0.13752508361204013,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":-16.869799666110183,"std":29.073289239528357,"start_value":-21.95,"end_value":60.29},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.9933703558016056,0.9867055929542156,0.9800089578860637,0.9732750465749592,0.9665066179952697,0.9597066979705894,0.9528784351666171,0.9460161587554587,0.9391184156821324,0.9321910802236684,0.9252397633867561,0.9182603830706991,0.9112500345243497,0.9042072407863354,0.8971322520954204,0.8900248365731779,0.8828861044084975,0.8757161328270339,0.8685176486212105,0.8612920904358338],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria. FFT analysis detected a dominant period close to the series length, but it's not trusted. Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length. There is a global upward trend in the time series with a positive slope of approximately 0.138. The time series exhibits strong long-term dependencies with a maximum lag of 20.","structured_by_scale":{"short":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"medium":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"long":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['A seasonal period exists in the series.']
</metadata>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides insights into the behavior and structure of Time Series 1, including local behavior, a potential dominant period (which is not trusted), and global trends. However, it does not explicitly identify the most similar waveform type among the candidates. To achieve the goal of matching Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth), and cross-checking all four candidate types, additional analysis steps are required.",
  "evidence_plan": {
    "objective": "Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.",
    "claims_to_support": [
      {
        "claim": "Time Series 1 is accurately matched to one of the candidate waveforms.",
        "required_evidence": ["pairwise_similarity"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["cross-check all four candidate types"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "pairwise_distance",
        "arguments": {
          "query_series_index": 1,
          "candidate_series_indices": ["Sine", "Square", "Triangle", "Sawtooth"]
        }
      },
      {
        "tool": "waveform_features",
        "arguments": {
          "series_index": 1
        }
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m1`

tokens prompt=634 completion=172 latency=6.10s

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
{"evidence_plan":{"objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","claims_to_support":[{"claim":"Time Series 1 is accurately matched to one of the candidate waveforms.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["cross-check all four candidate types"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"","supports_evidence":[]},{"tool":"waveform_features","reason":"","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides insights into the behavior and structure of Time Series 1, including local behavior, a potential dominant period (which is not trusted), and global trends. However, it does not explicitly identify the most similar waveform type among the candidates. To achieve the goal of matching Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth), and cross-checking all four candidate types, additional analysis steps are required."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- waveform_features
  inputs: series, optional start/end
  outputs: waveform_hint, jump_ratio, harmonic, template_match
  often_combined_with: fft_period, step_levels, diff_stats
- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
</io_concepts>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "To match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth), we will first utilize the 'waveform_features' tool to extract essential features of the time series. Subsequently, we will apply the 'pairwise_distance' tool to compare the given time series with the reference waveforms based on these extracted features.",
  "workflow": [
    {
      "step": 1,
      "tool": "waveform_features",
      "output_key": "waveform_hint",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "pairwise_distance",
      "output_key": "pairwise_similarity",
      "input_binding": {
        "series_index": "$step1.series"
      }
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m1`

tokens prompt=874 completion=169 latency=6.05s

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
{"workflow":[{"step":1,"tool":"waveform_features","output_key":"waveform_hint","input_binding":{}},{"step":2,"tool":"pairwise_distance","output_key":"pairwise_similarity","input_binding":{"series_index":"$step1.series"}}],"reasoning":"To match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth), we will first utilize the 'waveform_features' tool to extract essential features of the time series. Subsequently, we will apply the 'pairwise_distance' tool to compare the given time series with the reference waveforms based on these extracted features."}
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

- waveform_features: Classify waveform shape (sine/square/triangle/sawtooth/ambiguous) using jump ratio, plateau clustering, harmonic structure, and folded-template match. Do NOT treat FFT period alone as evidence of a sine wave.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=waveform_hint plus jump/plateau/harmonic/template-match diagnostics}
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  args: {method=euclidean|dtw, series_index=reference 1-based (default 1)}
  returns: {distances=per-candidate distances, nearest=winner, method=distance metadata}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}
</assignment>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The objective is to match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth). First, we need to identify the waveform hint of Time Series 1 by invoking the 'waveform_features' tool. Then, we will compute the pairwise similarity between Time Series 1 and each reference waveform using the 'pairwise_distance' tool.",
  "calls": [
    {
      "step": 1,
      "tool": "waveform_features",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "pairwise_distance",
      "args": {
        "series_index": 1,
        "method": "euclidean"
      }
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=7922 completion=293 latency=13.03s

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
{"evidence_plan":{"objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","claims_to_support":[{"claim":"Time Series 1 is accurately matched to one of the candidate waveforms.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["cross-check all four candidate types"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"","supports_evidence":[]},{"tool":"waveform_features","reason":"","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides insights into the behavior and structure of Time Series 1, including local behavior, a potential dominant period (which is not trusted), and global trends. However, it does not explicitly identify the most similar waveform type among the candidates. To achieve the goal of matching Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth), and cross-checking all four candidate types, additional analysis steps are required."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "matching:step1",
    "step": 1,
    "tool_name": "waveform_features",
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
      "dominant_period": 299,
      "period_trusted": true,
      "jump_ratio": 0.0,
      "n_large_jumps": 0,
      "jump_threshold": 20.952000000000197,
      "max_abs_diff": 8.77,
      "max_jump_frac": 0.0837151584574257,
      "jump_regime": {
        "n_large_jumps": 0,
        "alternation_rate": null,
        "spacing_cv": null,
        "jump_to_intra_ratio": null,
        "median_spacing": null
      },
      "amplitude_bimodality": 0.27712854757929883,
      "n_unique_levels": 49,
      "n_plateau_runs": 68,
      "level_tolerance": 1.0475999999999999,
      "folded_mean_abs_slope": 0.279513422818792,
      "rise_fall_asymmetry": 0.922814421225608,
      "harmonic": {
        "fundamental_share": 0.6301202381374233,
        "odd_even_ratio": 3.039542827019815,
        "high_harmonic_share": 0.3698797618625767
      },
      "template_match": {
        "best": "sawtooth",
        "best_corr": 0.9664853744662082,
        "margin": 0.10285347719085891,
        "scores": {
          "sine": 0.8636318972753493,
          "square": 0.8186171971400291,
          "triangle": 0.8420751140010535,
          "sawtooth": 0.9664853744662082
        }
      },
      "waveform_hint": "sawtooth",
      "metric_definition": "waveform_hint from jump regime + plateau/harmonic/template features; periodicity alone does not imply sine",
      "evidence_source_id": "waveform_features:1:None:None",
      "warnings": [
        "periodicity_is_not_waveform_type"
      ]
    },
    "error": null,
    "args_fingerprint": "5b7b04a641500b5559a6fb20edbe60ac39db4655"
  },
  {
    "call_id": "matching:step2",
    "step": 2,
    "tool_name": "pairwise_distance",
    "arguments": {
      "series_index": 1,
      "method": "euclidean"
    },
    "resolved_arguments": {
      "series_index": 1,
      "method": "euclidean"
    },
    "success": false,
    "data": {},
    "error": "Need >=2 series",
    "args_fingerprint": ""
  }
]
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Local behavior has been analyzed using sliding window statistics and counts of local extrema. No anomalies were detected within the specified z-score threshold.","scale":"short","observations":["Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 29, \"mean_of_means\": -18.551806872395673, \"mean_of_stds\": 2.777843427701618, \"max_local_std\": 7.5853416277705055}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 5, \"n_troughs\": 5, \"peak_idx\": [88, 247, 249, 385, 504], \"trough_idx\": [87, 148, 303, 386, 505]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.65397557979793}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Analyze local behavior for pattern recognition and anomaly detection.","claims_to_support":[{"claim":"Local behavior patterns exist and can be identified.","required_evidence":["sliding_window_statistics","local_extrema_counts"]},{"claim":"Anomalies can be detected.","required_evidence":["outlier_spikes_in_windows"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["compare multiple small segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measure local volatility and rolling level variations for pattern recognition.","supports_evidence":["sliding_window_statistics"]},{"tool":"local_extrema","reason":"Count local peaks and troughs to understand local behavior patterns.","supports_evidence":["local_extrema_counts"]},{"tool":"anomaly_detect","reason":"Detect anomalies via z-score threshold in sliding windows.","supports_evidence":["outlier_spikes_in_windows"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility_results","input_binding":{}},{"step":2,"tool":"local_extrema","output_key":"extrema_count","input_binding":{}},{"step":3,"tool":"anomaly_detect","output_key":"anomaly_detection_results","input_binding":{}}],"reasoning":"The objective is to analyze the local behavior for pattern recognition and anomaly detection in the given short-scale context. It requires detecting anomalies and understanding the local behavior patterns using the selected tools."},"structured_observations":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"coverage":{"local_behavior":"tool_supported","anomaly_detection":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":29,"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":5,"n_troughs":5,"peak_idx":[88,247,249,385,504],"trough_idx":[87,148,303,386,505]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step3","step":3,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.65397557979793},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify repeated patterns and periodicity in a univariate time series to support waveform classification. The FFT analysis (fft_period) suggested a dominant period of 599 with a spectral strength of 0.175, which is nearly equal to the length of the series. However, this period is not trusted due to its proximity to the series length. Subsequent seasonal autocorrelation (seas_acf) analysis aimed to validate the existence of a seasonal period, but it failed due to an invalid lag value for the series length.","scale":"medium","observations":["FFT analysis detected a dominant period close to the series length, but it's not trusted.","Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 599.0, \"spectral_strength\": 0.17524073250280806, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 599.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 599, \"seas_acf1\": null, \"strength_hint\": \"unavailable\", \"note\": \"lag 599 invalid for length 599\"}, \"error\": null, \"args_fingerprint\": \"2ccd068769598ae281eace53d0f2d13063c05494\"}"],"evidence_plan":{"objective":"Identify repeated patterns and periodicity to support waveform classification.","claims_to_support":[{"claim":"The series contains repeated patterns.","required_evidence":["seasonal_period"]},{"claim":"A seasonal period exists in the series.","required_evidence":["periodicity_across_various_sections"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["periodicity across various sections"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that might represent the repeated patterns.","supports_evidence":["seasonal_period"]},{"tool":"seas_acf","reason":"To confirm the presence of a seasonal period via seasonal autocorrelation at a specific lag derived from the dominant period.","supports_evidence":["periodicity_across_various_sections"]},{"tool":"waveform_features","reason":"To classify the waveform shape based on additional features like jump ratio, plateau clustering, and harmonic structure.","supports_evidence":["waveform_classification"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to detect the dominant period in the series which might represent the repeated patterns. Then, we employ 'seas_acf' with the detected period as the lag to confirm the presence of a seasonal period via seasonal autocorrelation, thus validating the periodicity across various sections of the series."},"structured_observations":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"coverage":{"repeated_patterns":"qualified","seasonal_period":"unresolved"},"unresolved_claims":["A seasonal period exists in the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":599.0,"spectral_strength":0.17524073250280806,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":599.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":599,"seas_acf1":null,"strength_hint":"unavailable","note":"lag 599 invalid for length 599"},"error":null,"args_fingerprint":"2ccd068769598ae281eace53d0f2d13063c05494"}],"skipped_stages":[]},"long":{"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. The executed tools indicate a clear upward trend with a positive slope and significant long-term dependencies based on the high autocorrelation values.","scale":"long","observations":["There is a global upward trend in the time series with a positive slope of approximately 0.138.","The time series exhibits strong long-term dependencies with a maximum lag of 20."],"evidence_intervals":[],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 0.13752508361204013, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": -16.869799666110183, \"std\": 29.073289239528357, \"start_value\": -21.95, \"end_value\": 60.29}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.9933703558016056, 0.9867055929542156, 0.9800089578860637, 0.9732750465749592, 0.9665066179952697, 0.9597066979705894, 0.9528784351666171, 0.9460161587554587, 0.9391184156821324, 0.9321910802236684, 0.9252397633867561, 0.9182603830706991, 0.9112500345243497, 0.9042072407863354, 0.8971322520954204, 0.8900248365731779, 0.8828861044084975, 0.8757161328270339, 0.8685176486212105, 0.8612920904358338], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure for global trends and dependencies.","claims_to_support":[{"claim":"There exists a global trend in the time series.","required_evidence":["slope","direction"]},{"claim":"There are long-term dependencies in the time series.","required_evidence":["autocorrelation"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["analyze the complete sequence"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To detect the overall trend direction and slope of the time series.","supports_evidence":["slope","direction"]},{"tool":"autocorr","reason":"To measure long-term dependencies through autocorrelation.","supports_evidence":["autocorrelation"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"autocorr","output_key":"autocorr_result","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective at the long scale is to analyze the overall structure for global trends and dependencies. This requires identifying any global trends and long-term dependencies in the time series. We will use segment_trend to detect the overall trend direction and slope of the time series, and then use autocorr to measure long-term dependencies through autocorrelation."},"structured_observations":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}],"coverage":{"global_trends":"tool_supported","long_term_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":0.13752508361204013,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":-16.869799666110183,"std":29.073289239528357,"start_value":-21.95,"end_value":60.29},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.9933703558016056,0.9867055929542156,0.9800089578860637,0.9732750465749592,0.9665066179952697,0.9597066979705894,0.9528784351666171,0.9460161587554587,0.9391184156821324,0.9321910802236684,0.9252397633867561,0.9182603830706991,0.9112500345243497,0.9042072407863354,0.8971322520954204,0.8900248365731779,0.8828861044084975,0.8757161328270339,0.8685176486212105,0.8612920904358338],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria. FFT analysis detected a dominant period close to the series length, but it's not trusted. Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length. There is a global upward trend in the time series with a positive slope of approximately 0.138. The time series exhibits strong long-term dependencies with a maximum lag of 20.","structured_by_scale":{"short":[{"claim":"Local behavior patterns exist and can be identified.","evidence":[{"type":"sliding_window_statistics","value":{"mean_of_means":-18.551806872395673,"mean_of_stds":2.777843427701618,"max_local_std":7.5853416277705055},"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_extrema_counts","value":{"n_peaks":5,"n_troughs":5},"source_tool":"local_extrema","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"local_behavior"},{"claim":"Anomalies can be detected.","evidence":[{"type":"outlier_spikes_in_windows","value":{"z_threshold":3.0,"n_anomalies":0,"max_abs_z":2.65397557979793},"source_tool":"anomaly_detect","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_detection"}],"medium":[{"claim":"The series contains repeated patterns.","evidence":[{"type":"seasonal_period","value":599,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"repeated_patterns"},{"claim":"A seasonal period exists in the series.","evidence":[{"type":"periodicity_across_various_sections","value":"unavailable","source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"unresolved","maps_to_measurement":"seasonal_period"}],"long":[{"claim":"There exists a global trend in the time series.","evidence":[{"type":"slope","value":0.13752508361204013,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"direction","value":"upward","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trends"},{"claim":"There are long-term dependencies in the time series.","evidence":[{"type":"autocorrelation","value":0.9933703558016056,"source_tool":"autocorr","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_term_dependence"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.","required_measurements":["pairwise_similarity","change_location"],"validation_requirements":["cross-check all four candidate types"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Base; local_overall=overall; task_type=['seasonality analysis']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[599]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the waveform features extracted, Time Series 1 shows characteristics closest to the sawtooth waveform, with a similarity score of 0.9664853744662082, significantly higher than the other waveform types.",
  "role": "matching",
  "hypothesis": "Time Series 1 is best matched to the sawtooth waveform.",
  "evidence": ["waveform_features:1:None:None"],
  "candidate_preference": "D",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["matching:step1"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 1 shows characteristics most similar to a sawtooth waveform.",
      "evidence": [
        {
          "type": "similarity_score",
          "value": 0.9664853744662082,
          "provenance": "tool",
          "ref": "waveform_features:1:None:None",
          "call_id": "matching:step1"
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

tokens prompt=1968 completion=231 latency=8.58s

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
Here is a list of values in the Time Series 1. Based on the Time Series 1 data provided, what type of waveform does the Time Series 1 most resemble?
</question>

<candidates>
A) Sine.
B) Square.
C) Triangle.
D) Sawtooth.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Identify which waveform Type (Sine, Square, Triangle, Sawtooth) Time Series 1 most resembles.",
  "question_type": "choice",
  "required_output": "The type of waveform Time Series 1 most resembles.",
  "success_criteria": [
    "Time Series 1 is accurately matched to one of the candidate waveforms.",
    "All possible waveform comparisons are evaluated and validated."
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Analyze local behavior for pattern recognition and anomaly detection.",
      "required_measurements": [
        "local_behavior",
        "anomaly_detection"
      ]
    },
    {
      "agent": "homo:medium",
      "objective": "Identify repeated patterns and periodicity to support waveform classification.",
      "required_measurements": [
        "repeated_patterns",
        "seasonal_period"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Analyze the overall structure for global trends and dependencies.",
      "required_measurements": [
        "global_trends",
        "long_term_dependence"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Match Time Series 1 against reference waveforms (Sine, Square, Triangle, Sawtooth) to determine the most similar pattern.",
      "required_measurements": [
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
          "type": "sliding_window_statistics",
          "value": {
            "mean_of_means": -18.551806872395673,
            "mean_of_stds": 2.777843427701618,
            "max_local_std": 7.5853416277705055
          },
          "trusted": true
        },
        {
          "series_index": null,
          "type": "local_extrema_counts",
          "value": {
            "n_peaks": 5,
            "n_troughs": 5
          },
          "trusted": true
        },
        {
          "series_index": null,
          "type": "outlier_spikes_in_windows",
          "value": {
            "z_threshold": 3.0,
            "n_anomalies": 0,
            "max_abs_z": 2.65397557979793
          },
          "trusted": true
        }
      ],
      "coverage": {
        "local_behavior": "tool_supported",
        "anomaly_detection": "tool_supported"
      },
      "summary": "Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria."
    },
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "seasonal_period",
          "value": 599,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "periodicity_across_various_sections",
          "value": "unavailable",
          "trusted": true
        }
      ],
      "coverage": {
        "repeated_patterns": "qualified",
        "seasonal_period": "unresolved"
      },
      "summary": "FFT analysis detected a dominant period close to the series length, but it's not trusted. | Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "slope",
          "value": 0.13752508361204013,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "direction",
          "value": "upward",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "autocorrelation",
          "value": 0.9933703558016056,
          "trusted": true
        }
      ],
      "coverage": {
        "global_trends": "tool_supported",
        "long_term_dependence": "tool_supported"
      },
      "summary": "There is a global upward trend in the time series with a positive slope of approximately 0.138. | The time series exhibits strong long-term dependencies with a maximum lag of 20."
    }
  },
  "conflicts": [],
  "summary": "Local behavior patterns have been recognized using statistical measures and extremum counts. Anomalies were not detected within the given criteria. FFT analysis detected a dominant period close to the series length, but it's not trusted. Seasonal autocorrelation analysis could not validate the presence of a seasonal period due to an invalid lag value for the series length. There is a global upward trend in the time series with a positive slope of approximately 0.138. The time series exhibits strong long-term dependencies with a maximum lag of 20."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Time Series 1 is best matched to the sawtooth waveform.",
      "reasoning_chain": [
        "Time Series 1 shows characteristics most similar to a sawtooth waveform.",
        "similarity_score=0.9664853744662082"
      ],
      "candidate_preference": "D",
      "confidence": 1.0,
      "grounded": true,
      "grounded_in": [
        "similarity_score"
      ],
      "uncertainty": ""
    }
  ]
}
</heter_reasoning>

<execution_metadata>
{
  "option_mapping": {},
  "verified_preference": "D",
  "verified": true,
  "warnings": [
    "waveform_hint_mapped:sawtooth->D"
  ]
}
</execution_metadata>

<question_rules>
- Waveform shape: periodicity ≠ sine. Prefer homo_perception waveform_hint / jump/plateau evidence over FFT period alone; if uncertain, still pick one letter and record conflicts (do not mechanically default to A).
</question_rules>

Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "Heter reasoning strongly matches Time Series 1 to a sawtooth waveform based on a high similarity score. Execution metadata verifies this preference with a verified waveform hint mapping. Although medium-scale analysis could not resolve a clear seasonal period, short-scale and long-scale analysis did not contradict this match.",
  "answer": "D",
  "explanation": "The similarity score between Time Series 1 and the sawtooth waveform is very high at 0.966, indicating a strong match according to hetero:matching. Additionally, execution metadata supports this choice with a verified preference and a waveform hint mapping that aligns the sawtooth waveform with option D.",
  "confidence": 1.0,
  "conflicts": [],
  "cited_evidence": ["similarity_score", "verified_preference", "waveform_hint_mapped:sawtooth->D"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": null
  }
}
```
