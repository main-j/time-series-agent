# Agent IO summary: `Base:synthtic_qa_700:538`

- Architecture pred: `B` (success=True)
- model_calls=12, tool_calls=4, latency=161.6s

## Planner — `planner`

tokens prompt=1035 completion=519 latency=18.40s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 1036 present a global maximum or minimum value or neither? (The index starts from 0)
</question>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

<metadata>
local_overall=local; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "To determine if point 1036 represents a global maximum, minimum, or neither, we need detailed examination of the entire Time Series 1. This involves understanding the behavior of the time series around point 1036 from both a short-term and long-term perspective. We will use the homogeneous agents to gather relevant data points and then utilize a heterogeneous agent for comparison and validation against the candidates.",
  "task_summary": "Identify if the value at point 1036 of Time Series 1 is a global maximum, minimum, or neither.",
  "target_output": "Max|Min|Neither",
  "answer_type": "choice",
  "capability": "choice",
  "scope": "local",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Examine the local behavior around point 1036 for immediate variations.",
      "required_measurements": ["endpoint_slope", "pairwise_similarity"],
      "validation_requirements": ["Measure consistency across nearby points"],
      "target_series": [1],
      "focus_intervals": [[1035, 1037]]
    },
    {
      "scale": "long",
      "objective": "Analyze the overall series to establish a global context.",
      "required_measurements": ["step_level_count", "global_extremum"],
      "validation_requirements": ["Confirm absence of higher/lower points globally"],
      "target_series": [1],
      "focus_intervals": [[0, 1036]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.",
      "required_measurements": ["endpoint_slope", "pairwise_similarity", "step_level_count", "global_extremum"],
      "validation_requirements": ["Ensure the classification is consistent with all gathered evidence"],
      "target_series": [1],
      "focus_intervals": [[0, 1036]]
    }
  ],
  "success_criteria": ["Accurate identification of the extremum status at point 1036 based on gathered evidence"],
  "notes": "The chosen scope is 'local' since we are examining a specific point in the series, even though the long-term analysis spans the whole series."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4117 completion=278 latency=11.08s

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
{"scale":"short","objective":"Examine the local behavior around point 1036 for immediate variations.","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Measure consistency across nearby points"],"target_series":[1],"focus_intervals":[[1035,1037]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 1036 represents a global maximum, minimum, or neither, we need detailed examination of the entire Time Series 1. This involves understanding the behavior of the time series around point 1036 from both a short-term and long-term perspective. We will use the homogeneous agents to gather relevant data points and then utilize a heterogeneous agent for comparison and validation against the candidates.","task_summary":"Identify if the value at point 1036 of Time Series 1 is a global maximum, minimum, or neither.","target_output":"Max|Min|Neither","answer_type":"choice","capability":"choice","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Examine the local behavior around point 1036 for immediate variations.","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Measure consistency across nearby points"],"target_series":[1],"focus_intervals":[[1035,1037]]},{"scale":"long","objective":"Analyze the overall series to establish a global context.","required_measurements":["step_level_count","global_extremum"],"validation_requirements":["Confirm absence of higher/lower points globally"],"target_series":[1],"focus_intervals":[[0,1036]]}],"hetero_assignments":[{"role":"matching","objective":"Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.","required_measurements":["endpoint_slope","pairwise_similarity","step_level_count","global_extremum"],"validation_requirements":["Ensure the classification is consistent with all gathered evidence"],"target_series":[1],"focus_intervals":[[0,1036]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of the extremum status at point 1036 based on gathered evidence"],"notes":"The chosen scope is 'local' since we are examining a specific point in the series, even though the long-term analysis spans the whole series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to examine the local behavior around point 1036 for immediate variations, focusing on endpoint slope and pairwise similarity, with a requirement for measure consistency across nearby points.",
  "evidence_plan": {
    "objective": "Examine the local behavior around point 1036 for immediate variations.",
    "claims_to_support": [
      {"claim": "The endpoint slope around point 1036 indicates the direction of immediate change.", "required_evidence": ["slope"]},
      {"claim": "Pairwise similarity between neighboring points provides local consistency measures.", "required_evidence": ["pairwise_similarity"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[1035,1037]], "scale": "short"},
    "validation_needs": ["Measure consistency across nearby points"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "diff_stats", "reason": "Endpoint slope around point 1036 needs to be examined.", "supports_evidence": ["slope"]},
      {"tool": "interval_compare", "reason": "Local consistency measures between neighboring points are required.", "supports_evidence": ["pairwise_similarity"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=763 completion=210 latency=7.53s

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
{"evidence_plan":{"objective":"Examine the local behavior around point 1036 for immediate variations.","claims_to_support":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","required_evidence":["slope"]},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[1035,1037]],"scale":"short"},"validation_needs":["Measure consistency across nearby points"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Endpoint slope around point 1036 needs to be examined.","supports_evidence":["slope"]},{"tool":"interval_compare","reason":"Local consistency measures between neighboring points are required.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective is to examine the local behavior around point 1036 for immediate variations, focusing on endpoint slope and pairwise similarity, with a requirement for measure consistency across nearby points."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- diff_stats
  inputs: series_index, start, end
  outputs: series
- interval_compare
  inputs: series_index, start, end, left_interval, right_interval, start/mid/end
  outputs: left/right
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'diff_stats' to get the endpoint slope around point 1036, then 'interval_compare' to analyze pairwise similarity between neighboring points for consistency.",
  "workflow": [
    {
      "step": 1,
      "tool": "diff_stats",
      "output_key": "endpoint_slope",
      "input_binding": {"series_index": 1, "start": 1036, "end": 1036}
    },
    {
      "step": 2,
      "tool": "interval_compare",
      "output_key": "pairwise_similarity",
      "input_binding": {"series_index": 1, "start": 1035, "end": 1037, "left_interval": [1035, 1036], "right_interval": [1036, 1037], "start/mid/end": "mid"}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=924 completion=221 latency=7.95s

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
{"workflow":[{"step":1,"tool":"diff_stats","output_key":"endpoint_slope","input_binding":{"series_index":1,"start":1036,"end":1036}},{"step":2,"tool":"interval_compare","output_key":"pairwise_similarity","input_binding":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"}}],"reasoning":"First, we use 'diff_stats' to get the endpoint slope around point 1036, then 'interval_compare' to analyze pairwise similarity between neighboring points for consistency."}
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
- interval_compare: Compare left/right interval statistics on one series (mean/std/max/min/n_peaks/trend per side).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, left_interval=[start,end] inclusive, right_interval=[start,end] inclusive, start/mid/end=alt split mode}
  returns: {left/right=interval statistics, trends, extrema counts, and deltas}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Examine the local behavior around point 1036 for immediate variations.","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Measure consistency across nearby points"],"target_series":[1],"focus_intervals":[[1035,1037]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "First, calculate the endpoint slope around point 1036 using diff_stats. Then, evaluate the pairwise similarity between the intervals [1035,1036] and [1036,1037] using interval_compare.",
  "calls": [
    {
      "step": 1,
      "tool": "diff_stats",
      "args": {
        "series_index": 1,
        "start": 1036,
        "end": 1036
      }
    },
    {
      "step": 2,
      "tool": "interval_compare",
      "args": {
        "series_index": 1,
        "start": 1035,
        "end": 1037,
        "left_interval": [1035, 1036],
        "right_interval": [1036, 1037],
        "start/mid/end": "mid"
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1607 completion=524 latency=18.97s

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
{"evidence_plan":{"objective":"Examine the local behavior around point 1036 for immediate variations.","claims_to_support":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","required_evidence":["slope"]},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[1035,1037]],"scale":"short"},"validation_needs":["Measure consistency across nearby points"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Endpoint slope around point 1036 needs to be examined.","supports_evidence":["slope"]},{"tool":"interval_compare","reason":"Local consistency measures between neighboring points are required.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective is to examine the local behavior around point 1036 for immediate variations, focusing on endpoint slope and pairwise similarity, with a requirement for measure consistency across nearby points."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "diff_stats",
    "arguments": {
      "series_index": 1,
      "start": 1036,
      "end": 1036
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 1036,
      "end": 1036
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 1036,
      "end": 1036,
      "mean_diff": 0.0,
      "std_diff": 0.0,
      "max_abs_diff": 0.0,
      "n_sign_changes": 0
    },
    "error": null,
    "args_fingerprint": "5b5d096dccef950c9712c89d4b1aba6e171ecb10"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "interval_compare",
    "arguments": {
      "series_index": 1,
      "start": 1035,
      "end": 1037,
      "left_interval": [
        1035,
        1036
      ],
      "right_interval": [
        1036,
        1037
      ],
      "start/mid/end": "mid"
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 1035,
      "end": 1037,
      "left_interval": [
        1035,
        1036
      ],
      "right_interval": [
        1036,
        1037
      ],
      "start/mid/end": "mid"
    },
    "success": true,
    "data": {
      "series_index": 1,
      "mode": "pair",
      "left_interval": [
        1035,
        1036
      ],
      "right_interval": [
        1036,
        1036
      ],
      "left_mean": -129.79500000000002,
      "right_mean": -130.3,
      "left_std": 0.5050000000000097,
      "right_std": 0.0,
      "left_max": -129.29,
      "right_max": -130.3,
      "left_min": -130.3,
      "right_min": -130.3,
      "left_max_index": 1035,
      "right_max_index": 1036,
      "left_n_peaks": 0,
      "right_n_peaks": 0,
      "left_n_troughs": 0,
      "right_n_troughs": 0,
      "left_direction": "downward",
      "right_direction": "flat",
      "left_slope": -1.0100000000000193,
      "right_slope": 0.0,
      "mean_delta": -0.5049999999999955,
      "max_delta": -1.0100000000000193,
      "same_trend_direction": false
    },
    "error": null,
    "args_fingerprint": "b965ae5d627fad5674c2ff4fc8b8d81bb9544f29"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Examine the local behavior around point 1036 for immediate variations.","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Measure consistency across nearby points"],"target_series":[1],"focus_intervals":[[1035,1037]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The local behavior around point 1036 was examined using two tools: diff_stats to evaluate the endpoint slope and interval_compare to assess pairwise similarity between neighboring points. The diff_stats tool indicated that there is no difference in values around point 1036, resulting in a mean difference and standard deviation of 0.0, with zero sign changes. The interval_compare tool revealed that the left interval [1035, 1036] has a downward trend, whereas the right interval [1036, 1037] is flat, showing a slope difference and indicating a lack of trend consistency.",
  "scale": "short",
  "observations": [
    "Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values.",
    "Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat."
  ],
  "evidence_intervals": [
    "[1035,1037]"
  ],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The endpoint slope around point 1036 indicates the direction of immediate change.",
      "evidence": [
        {
          "type": "slope",
          "value": 0.0,
          "source_tool": "diff_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "endpoint_slope"
    },
    {
      "claim": "Pairwise similarity between neighboring points provides local consistency measures.",
      "evidence": [
        {
          "type": "pairwise_similarity",
          "value": -0.5049999999999955,
          "source_tool": "interval_compare",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {
    "endpoint_slope": "tool_supported",
    "pairwise_similarity": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4114 completion=333 latency=13.10s

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
{"scale":"long","objective":"Analyze the overall series to establish a global context.","required_measurements":["step_level_count","global_extremum"],"validation_requirements":["Confirm absence of higher/lower points globally"],"target_series":[1],"focus_intervals":[[0,1036]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 1036 represents a global maximum, minimum, or neither, we need detailed examination of the entire Time Series 1. This involves understanding the behavior of the time series around point 1036 from both a short-term and long-term perspective. We will use the homogeneous agents to gather relevant data points and then utilize a heterogeneous agent for comparison and validation against the candidates.","task_summary":"Identify if the value at point 1036 of Time Series 1 is a global maximum, minimum, or neither.","target_output":"Max|Min|Neither","answer_type":"choice","capability":"choice","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Examine the local behavior around point 1036 for immediate variations.","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Measure consistency across nearby points"],"target_series":[1],"focus_intervals":[[1035,1037]]},{"scale":"long","objective":"Analyze the overall series to establish a global context.","required_measurements":["step_level_count","global_extremum"],"validation_requirements":["Confirm absence of higher/lower points globally"],"target_series":[1],"focus_intervals":[[0,1036]]}],"hetero_assignments":[{"role":"matching","objective":"Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.","required_measurements":["endpoint_slope","pairwise_similarity","step_level_count","global_extremum"],"validation_requirements":["Ensure the classification is consistent with all gathered evidence"],"target_series":[1],"focus_intervals":[[0,1036]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of the extremum status at point 1036 based on gathered evidence"],"notes":"The chosen scope is 'local' since we are examining a specific point in the series, even though the long-term analysis spans the whole series."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "To analyze the overall series and establish a global context, we need to confirm the absence of higher or lower points globally relative to the target point 1036. The objective requires measuring step levels and identifying global extrema.",
  "evidence_plan": {
    "objective": "Analyze the overall series to establish a global context.",
    "claims_to_support": [
      {
        "claim": "The step level count of the series helps identify distinct step/plateau levels.",
        "required_evidence": ["step_level_count"]
      },
      {
        "claim": "Global extremum values need to be identified to confirm the absence of higher/lower points globally.",
        "required_evidence": ["global_extremum"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[0, 1036]],
      "scale": "long"
    },
    "validation_needs": [
      "Confirm absence of higher/lower points globally"
    ]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "step_levels",
        "reason": "Counts discrete step/plateau levels, essential for understanding stepwise behavior.",
        "supports_evidence": ["step_level_count"]
      },
      {
        "tool": "global_extrema",
        "reason": "Provides global max/min values and indices necessary for confirming extremum status.",
        "supports_evidence": ["global_extremum"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=781 completion=216 latency=7.67s

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
{"evidence_plan":{"objective":"Analyze the overall series to establish a global context.","claims_to_support":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","required_evidence":["step_level_count"]},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1036]],"scale":"long"},"validation_needs":["Confirm absence of higher/lower points globally"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels, essential for understanding stepwise behavior.","supports_evidence":["step_level_count"]},{"tool":"global_extrema","reason":"Provides global max/min values and indices necessary for confirming extremum status.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"reasoning":"To analyze the overall series and establish a global context, we need to confirm the absence of higher or lower points globally relative to the target point 1036. The objective requires measuring step levels and identifying global extrema."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- global_extrema
  inputs: series_index, start, end, index, index_base
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "To meet the objective of analyzing the overall series and establishing a global context, the steps include identifying step levels and finding global extrema. The first step involves using the 'step_levels' tool to count discrete step/plateau levels, which is essential for understanding stepwise behavior. Following this, the 'global_extrema' tool will be used to provide global max/min values and their indices, needed to confirm the absence of higher or lower points globally.",
  "workflow": [
    {
      "step": 1,
      "tool": "step_levels",
      "output_key": "series",
      "input_binding": {"series_index": 1, "start": 0, "end": 1036}
    },
    {
      "step": 2,
      "tool": "global_extrema",
      "output_key": "series",
      "input_binding": {"series_index": 1, "start": 0, "end": 1036}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=962 completion=187 latency=6.73s

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
{"workflow":[{"step":1,"tool":"step_levels","output_key":"series","input_binding":{"series_index":1,"start":0,"end":1036}},{"step":2,"tool":"global_extrema","output_key":"series","input_binding":{"series_index":1,"start":0,"end":1036}}],"reasoning":"To meet the objective of analyzing the overall series and establishing a global context, the steps include identifying step levels and finding global extrema. The first step involves using the 'step_levels' tool to count discrete step/plateau levels, which is essential for understanding stepwise behavior. Following this, the 'global_extrema' tool will be used to provide global max/min values and their indices, needed to confirm the absence of higher or lower points globally."}
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
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the overall series to establish a global context.","required_measurements":["step_level_count","global_extremum"],"validation_requirements":["Confirm absence of higher/lower points globally"],"target_series":[1],"focus_intervals":[[0,1036]]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the overall series to establish a global context by counting the number of unique step levels and finding the global extremum. The workflow includes using the 'step_levels' tool to identify step levels within the given interval, followed by the 'global_extrema' tool to find the global maximum and minimum values and their indices.",
  "calls": [
    {
      "step": 1,
      "tool": "step_levels",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 1036
      }
    },
    {
      "step": 2,
      "tool": "global_extrema",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 1036
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=3491 completion=536 latency=20.23s

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
{"evidence_plan":{"objective":"Analyze the overall series to establish a global context.","claims_to_support":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","required_evidence":["step_level_count"]},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1036]],"scale":"long"},"validation_needs":["Confirm absence of higher/lower points globally"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels, essential for understanding stepwise behavior.","supports_evidence":["step_level_count"]},{"tool":"global_extrema","reason":"Provides global max/min values and indices necessary for confirming extremum status.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"reasoning":"To analyze the overall series and establish a global context, we need to confirm the absence of higher or lower points globally relative to the target point 1036. The objective requires measuring step levels and identifying global extrema."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
    "step": 1,
    "tool_name": "step_levels",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 1036
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 1036
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 1036,
      "n_unique_levels": 39,
      "n_plateau_runs": 59,
      "levels": [
        135.53178571428572,
        226.8613043478261,
        218.48944444444442,
        210.07718749999995,
        109.4552830188679,
        115.72368421052629,
        236.1438095238095,
        241.8516666666667,
        148.89499999999998,
        157.89468750000003,
        165.77687500000002,
        171.80166666666665,
        277.1919999999999,
        289.97275862068983,
        186.15615384615379,
        177.0770967741936,
        262.8625,
        252.9395918367347,
        130.00727272727275,
        101.23374999999999,
        92.61888888888889,
        83.82791666666668,
        77.30714285714286,
        48.43333333333333,
        40.512727272727275,
        32.351000000000006,
        23.952,
        16.04125,
        8.195555555555554,
        0.20250000000000012,
        -4.41,
        66.35714285714286,
        58.36333333333334,
        -90.36714285714285,
        -97.99666666666667,
        -105.55333333333334,
        -113.80142857142857,
        -122.52000000000001,
        -128.7575
      ],
      "plateau_runs": [
        135.53178571428572,
        226.8613043478261,
        218.48944444444442,
        210.07718749999995,
        109.4552830188679,
        115.72368421052629,
        220.2270833333333,
        228.29818181818183,
        236.1438095238095,
        241.8516666666667,
        148.89499999999998,
        157.89468750000003,
        165.77687500000002,
        171.80166666666665,
        277.1919999999999,
        289.97275862068983,
        186.15615384615379,
        177.0770967741936,
        170.324,
        262.8625,
        252.9395918367347,
        146.71370370370374,
        138.41478260869573,
        130.00727272727275,
        223.78324324324328,
        215.92368421052632,
        208.34,
        101.23374999999999,
        92.61888888888889,
        83.82791666666668,
        77.30714285714286,
        170.67117647058825,
        162.40304347826086,
        154.88312499999998,
        48.43333333333333,
        40.512727272727275,
        32.351000000000006,
        23.952,
        16.04125,
        8.195555555555554,
        0.20250000000000012,
        -4.41,
        90.18125,
        82.32125000000002,
        74.48,
        66.35714285714286,
        58.36333333333334,
        50.96333333333333,
        43.08857142857143,
        35.53285714285714,
        27.845714285714283,
        20.051428571428573,
        14.566666666666665,
        -90.36714285714285,
        -97.99666666666667,
        -105.55333333333334,
        -113.80142857142857,
        -122.52000000000001,
        -128.7575
      ],
      "plateau_lengths": [
        56,
        23,
        18,
        32,
        53,
        19,
        24,
        22,
        21,
        6,
        18,
        32,
        16,
        6,
        15,
        58,
        26,
        31,
        15,
        24,
        49,
        27,
        23,
        22,
        37,
        19,
        17,
        16,
        18,
        24,
        14,
        34,
        23,
        16,
        15,
        11,
        10,
        10,
        8,
        9,
        8,
        1,
        8,
        8,
        7,
        7,
        6,
        6,
        7,
        7,
        7,
        7,
        3,
        7,
        6,
        6,
        7,
        8,
        4
      ],
      "tolerance": 4.2301
    },
    "error": null,
    "args_fingerprint": "2b5a8022f20fa2f6362fd1ed9f6303db57cad136"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "global_extrema",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 1036
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 1036
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 1036,
      "max_index": 398,
      "min_index": 1036,
      "max_value": 292.71,
      "min_value": -130.3,
      "n_peaks": 7,
      "n_troughs": 6,
      "peak_indices": [
        56,
        273,
        398,
        491,
        636,
        781,
        926
      ],
      "trough_indices": [
        142,
        274,
        490,
        635,
        780,
        925
      ]
    },
    "error": null,
    "args_fingerprint": "519f0a90762ead41ba4a77c99ba151f9db6131a9"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the overall series to establish a global context.","required_measurements":["step_level_count","global_extremum"],"validation_requirements":["Confirm absence of higher/lower points globally"],"target_series":[1],"focus_intervals":[[0,1036]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes counting the number of distinct step/plateau levels and identifying the global maximum and minimum values. The step levels tool has determined there are 39 unique levels within the specified interval [0, 1036]. The global extrema tool has provided the maximum value at index 398 as 292.71 and the minimum value at index 1036 as -130.3.",
  "scale": "long",
  "observations": ["The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3.", "No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036."],
  "evidence_intervals": ["[0, 1036]"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The step level count of the series helps identify distinct step/plateau levels.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 39,
          "source_tool": "step_levels",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "step_level_count"
    },
    {
      "claim": "Global extremum values need to be identified to confirm the absence of higher/lower points globally.",
      "evidence": [
        {
          "type": "global_max_value",
          "value": 292.71,
          "source_tool": "global_extrema",
          "call_id": "long:step2",
          "provenance": "tool"
        },
        {
          "type": "global_min_value",
          "value": -130.3,
          "source_tool": "global_extrema",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_extremum"
    }
  ],
  "coverage": {"step_level_count": "tool_supported", "global_extremum": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=10472 completion=438 latency=19.88s

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
{"role":"matching","objective":"Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.","required_measurements":["endpoint_slope","pairwise_similarity","step_level_count","global_extremum"],"validation_requirements":["Ensure the classification is consistent with all gathered evidence"],"target_series":[1],"focus_intervals":[[0,1036]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 1036 represents a global maximum, minimum, or neither, we need detailed examination of the entire Time Series 1. This involves understanding the behavior of the time series around point 1036 from both a short-term and long-term perspective. We will use the homogeneous agents to gather relevant data points and then utilize a heterogeneous agent for comparison and validation against the candidates.","task_summary":"Identify if the value at point 1036 of Time Series 1 is a global maximum, minimum, or neither.","target_output":"Max|Min|Neither","answer_type":"choice","capability":"choice","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Examine the local behavior around point 1036 for immediate variations.","required_measurements":["endpoint_slope","pairwise_similarity"],"validation_requirements":["Measure consistency across nearby points"],"target_series":[1],"focus_intervals":[[1035,1037]]},{"scale":"long","objective":"Analyze the overall series to establish a global context.","required_measurements":["step_level_count","global_extremum"],"validation_requirements":["Confirm absence of higher/lower points globally"],"target_series":[1],"focus_intervals":[[0,1036]]}],"hetero_assignments":[{"role":"matching","objective":"Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.","required_measurements":["endpoint_slope","pairwise_similarity","step_level_count","global_extremum"],"validation_requirements":["Ensure the classification is consistent with all gathered evidence"],"target_series":[1],"focus_intervals":[[0,1036]]}],"scales":["short","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of the extremum status at point 1036 based on gathered evidence"],"notes":"The chosen scope is 'local' since we are examining a specific point in the series, even though the long-term analysis spans the whole series."}
</plan_context>

<task_summary>
Identify if the value at point 1036 of Time Series 1 is a global maximum, minimum, or neither.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The local behavior around point 1036 was examined using two tools: diff_stats to evaluate the endpoint slope and interval_compare to assess pairwise similarity between neighboring points. The diff_stats tool indicated that there is no difference in values around point 1036, resulting in a mean difference and standard deviation of 0.0, with zero sign changes. The interval_compare tool revealed that the left interval [1035, 1036] has a downward trend, whereas the right interval [1036, 1037] is flat, showing a slope difference and indicating a lack of trend consistency.","scale":"short","observations":["Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values.","Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat."],"evidence_intervals":["[1035,1037]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 1036, \"end\": 1036}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 1036, \"end\": 1036}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 1036, \"end\": 1036, \"mean_diff\": 0.0, \"std_diff\": 0.0, \"max_abs_diff\": 0.0, \"n_sign_changes\": 0}, \"error\": null, \"args_fingerprint\": \"5b5d096dccef950c9712c89d4b1aba6e171ecb10\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"interval_compare\", \"arguments\": {\"series_index\": 1, \"start\": 1035, \"end\": 1037, \"left_interval\": [1035, 1036], \"right_interval\": [1036, 1037], \"start/mid/end\": \"mid\"}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 1035, \"end\": 1037, \"left_interval\": [1035, 1036], \"right_interval\": [1036, 1037], \"start/mid/end\": \"mid\"}, \"success\": true, \"data\": {\"series_index\": 1, \"mode\": \"pair\", \"left_interval\": [1035, 1036], \"right_interval\": [1036, 1036], \"left_mean\": -129.79500000000002, \"right_mean\": -130.3, \"left_std\": 0.5050000000000097, \"right_std\": 0.0, \"left_max\": -129.29, \"right_max\": -130.3, \"left_min\": -130.3, \"right_min\": -130.3, \"left_max_index\": 1035, \"right_max_index\": 1036, \"left_n_peaks\": 0, \"right_n_peaks\": 0, \"left_n_troughs\": 0, \"right_n_troughs\": 0, \"left_direction\": \"downward\", \"right_direction\": \"flat\", \"left_slope\": -1.0100000000000193, \"right_slope\": 0.0, \"mean_delta\": -0.5049999999999955, \"max_delta\": -1.0100000000000193, \"same_trend_direction\": false}, \"error\": null, \"args_fingerprint\": \"b965ae5d627fad5674c2ff4fc8b8d81bb9544f29\"}"],"evidence_plan":{"objective":"Examine the local behavior around point 1036 for immediate variations.","claims_to_support":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","required_evidence":["slope"]},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[1035,1037]],"scale":"short"},"validation_needs":["Measure consistency across nearby points"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Endpoint slope around point 1036 needs to be examined.","supports_evidence":["slope"]},{"tool":"interval_compare","reason":"Local consistency measures between neighboring points are required.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"endpoint_slope","input_binding":{"series_index":1,"start":1036,"end":1036}},{"step":2,"tool":"interval_compare","output_key":"pairwise_similarity","input_binding":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"}}],"reasoning":"First, we use 'diff_stats' to get the endpoint slope around point 1036, then 'interval_compare' to analyze pairwise similarity between neighboring points for consistency."},"structured_observations":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","evidence":[{"type":"slope","value":0.0,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","evidence":[{"type":"pairwise_similarity","value":-0.5049999999999955,"source_tool":"interval_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"coverage":{"endpoint_slope":"tool_supported","pairwise_similarity":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":1036,"end":1036},"resolved_arguments":{"series_index":1,"start":1036,"end":1036},"success":true,"data":{"series_index":1,"start":1036,"end":1036,"mean_diff":0.0,"std_diff":0.0,"max_abs_diff":0.0,"n_sign_changes":0},"error":null,"args_fingerprint":"5b5d096dccef950c9712c89d4b1aba6e171ecb10"},{"call_id":"short:step2","step":2,"tool_name":"interval_compare","arguments":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"},"resolved_arguments":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"},"success":true,"data":{"series_index":1,"mode":"pair","left_interval":[1035,1036],"right_interval":[1036,1036],"left_mean":-129.79500000000002,"right_mean":-130.3,"left_std":0.5050000000000097,"right_std":0.0,"left_max":-129.29,"right_max":-130.3,"left_min":-130.3,"right_min":-130.3,"left_max_index":1035,"right_max_index":1036,"left_n_peaks":0,"right_n_peaks":0,"left_n_troughs":0,"right_n_troughs":0,"left_direction":"downward","right_direction":"flat","left_slope":-1.0100000000000193,"right_slope":0.0,"mean_delta":-0.5049999999999955,"max_delta":-1.0100000000000193,"same_trend_direction":false},"error":null,"args_fingerprint":"b965ae5d627fad5674c2ff4fc8b8d81bb9544f29"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The analysis includes counting the number of distinct step/plateau levels and identifying the global maximum and minimum values. The step levels tool has determined there are 39 unique levels within the specified interval [0, 1036]. The global extrema tool has provided the maximum value at index 398 as 292.71 and the minimum value at index 1036 as -130.3.","scale":"long","observations":["The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3.","No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036."],"evidence_intervals":["[0, 1036]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 1036, \"n_unique_levels\": 39, \"n_plateau_runs\": 59, \"levels\": [135.53178571428572, 226.8613043478261, 218.48944444444442, 210.07718749999995, 109.4552830188679, 115.72368421052629, 236.1438095238095, 241.8516666666667, 148.89499999999998, 157.89468750000003, 165.77687500000002, 171.80166666666665, 277.1919999999999, 289.97275862068983, 186.15615384615379, 177.0770967741936, 262.8625, 252.9395918367347, 130.00727272727275, 101.23374999999999, 92.61888888888889, 83.82791666666668, 77.30714285714286, 48.43333333333333, 40.512727272727275, 32.351000000000006, 23.952, 16.04125, 8.195555555555554, 0.20250000000000012, -4.41, 66.35714285714286, 58.36333333333334, -90.36714285714285, -97.99666666666667, -105.55333333333334, -113.80142857142857, -122.52000000000001, -128.7575], \"plateau_runs\": [135.53178571428572, 226.8613043478261, 218.48944444444442, 210.07718749999995, 109.4552830188679, 115.72368421052629, 220.2270833333333, 228.29818181818183, 236.1438095238095, 241.8516666666667, 148.89499999999998, 157.89468750000003, 165.77687500000002, 171.80166666666665, 277.1919999999999, 289.97275862068983, 186.15615384615379, 177.0770967741936, 170.324, 262.8625, 252.9395918367347, 146.71370370370374, 138.41478260869573, 130.00727272727275, 223.78324324324328, 215.92368421052632, 208.34, 101.23374999999999, 92.61888888888889, 83.82791666666668, 77.30714285714286, 170.67117647058825, 162.40304347826086, 154.88312499999998, 48.43333333333333, 40.512727272727275, 32.351000000000006, 23.952, 16.04125, 8.195555555555554, 0.20250000000000012, -4.41, 90.18125, 82.32125000000002, 74.48, 66.35714285714286, 58.36333333333334, 50.96333333333333, 43.08857142857143, 35.53285714285714, 27.845714285714283, 20.051428571428573, 14.566666666666665, -90.36714285714285, -97.99666666666667, -105.55333333333334, -113.80142857142857, -122.52000000000001, -128.7575], \"plateau_lengths\": [56, 23, 18, 32, 53, 19, 24, 22, 21, 6, 18, 32, 16, 6, 15, 58, 26, 31, 15, 24, 49, 27, 23, 22, 37, 19, 17, 16, 18, 24, 14, 34, 23, 16, 15, 11, 10, 10, 8, 9, 8, 1, 8, 8, 7, 7, 6, 6, 7, 7, 7, 7, 3, 7, 6, 6, 7, 8, 4], \"tolerance\": 4.2301}, \"error\": null, \"args_fingerprint\": \"2b5a8022f20fa2f6362fd1ed9f6303db57cad136\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 1036, \"max_index\": 398, \"min_index\": 1036, \"max_value\": 292.71, \"min_value\": -130.3, \"n_peaks\": 7, \"n_troughs\": 6, \"peak_indices\": [56, 273, 398, 491, 636, 781, 926], \"trough_indices\": [142, 274, 490, 635, 780, 925]}, \"error\": null, \"args_fingerprint\": \"519f0a90762ead41ba4a77c99ba151f9db6131a9\"}"],"evidence_plan":{"objective":"Analyze the overall series to establish a global context.","claims_to_support":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","required_evidence":["step_level_count"]},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1036]],"scale":"long"},"validation_needs":["Confirm absence of higher/lower points globally"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels, essential for understanding stepwise behavior.","supports_evidence":["step_level_count"]},{"tool":"global_extrema","reason":"Provides global max/min values and indices necessary for confirming extremum status.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"series","input_binding":{"series_index":1,"start":0,"end":1036}},{"step":2,"tool":"global_extrema","output_key":"series","input_binding":{"series_index":1,"start":0,"end":1036}}],"reasoning":"To meet the objective of analyzing the overall series and establishing a global context, the steps include identifying step levels and finding global extrema. The first step involves using the 'step_levels' tool to count discrete step/plateau levels, which is essential for understanding stepwise behavior. Following this, the 'global_extrema' tool will be used to provide global max/min values and their indices, needed to confirm the absence of higher or lower points globally."},"structured_observations":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","evidence":[{"type":"step_level_count","value":39,"source_tool":"step_levels","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","evidence":[{"type":"global_max_value","value":292.71,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_min_value","value":-130.3,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}],"coverage":{"step_level_count":"tool_supported","global_extremum":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":1036},"resolved_arguments":{"series_index":1,"start":0,"end":1036},"success":true,"data":{"series_index":1,"start":0,"end":1036,"n_unique_levels":39,"n_plateau_runs":59,"levels":[135.53178571428572,226.8613043478261,218.48944444444442,210.07718749999995,109.4552830188679,115.72368421052629,236.1438095238095,241.8516666666667,148.89499999999998,157.89468750000003,165.77687500000002,171.80166666666665,277.1919999999999,289.97275862068983,186.15615384615379,177.0770967741936,262.8625,252.9395918367347,130.00727272727275,101.23374999999999,92.61888888888889,83.82791666666668,77.30714285714286,48.43333333333333,40.512727272727275,32.351000000000006,23.952,16.04125,8.195555555555554,0.20250000000000012,-4.41,66.35714285714286,58.36333333333334,-90.36714285714285,-97.99666666666667,-105.55333333333334,-113.80142857142857,-122.52000000000001,-128.7575],"plateau_runs":[135.53178571428572,226.8613043478261,218.48944444444442,210.07718749999995,109.4552830188679,115.72368421052629,220.2270833333333,228.29818181818183,236.1438095238095,241.8516666666667,148.89499999999998,157.89468750000003,165.77687500000002,171.80166666666665,277.1919999999999,289.97275862068983,186.15615384615379,177.0770967741936,170.324,262.8625,252.9395918367347,146.71370370370374,138.41478260869573,130.00727272727275,223.78324324324328,215.92368421052632,208.34,101.23374999999999,92.61888888888889,83.82791666666668,77.30714285714286,170.67117647058825,162.40304347826086,154.88312499999998,48.43333333333333,40.512727272727275,32.351000000000006,23.952,16.04125,8.195555555555554,0.20250000000000012,-4.41,90.18125,82.32125000000002,74.48,66.35714285714286,58.36333333333334,50.96333333333333,43.08857142857143,35.53285714285714,27.845714285714283,20.051428571428573,14.566666666666665,-90.36714285714285,-97.99666666666667,-105.55333333333334,-113.80142857142857,-122.52000000000001,-128.7575],"plateau_lengths":[56,23,18,32,53,19,24,22,21,6,18,32,16,6,15,58,26,31,15,24,49,27,23,22,37,19,17,16,18,24,14,34,23,16,15,11,10,10,8,9,8,1,8,8,7,7,6,6,7,7,7,7,3,7,6,6,7,8,4],"tolerance":4.2301},"error":null,"args_fingerprint":"2b5a8022f20fa2f6362fd1ed9f6303db57cad136"},{"call_id":"long:step2","step":2,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":1036},"resolved_arguments":{"series_index":1,"start":0,"end":1036},"success":true,"data":{"series_index":1,"start":0,"end":1036,"max_index":398,"min_index":1036,"max_value":292.71,"min_value":-130.3,"n_peaks":7,"n_troughs":6,"peak_indices":[56,273,398,491,636,781,926],"trough_indices":[142,274,490,635,780,925]},"error":null,"args_fingerprint":"519f0a90762ead41ba4a77c99ba151f9db6131a9"}],"skipped_stages":[]},"conflicts":[],"summary":"Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values. Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat. The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3. No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036.","structured_by_scale":{"short":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","evidence":[{"type":"slope","value":0.0,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","evidence":[{"type":"pairwise_similarity","value":-0.5049999999999955,"source_tool":"interval_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","evidence":[{"type":"step_level_count","value":39,"source_tool":"step_levels","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","evidence":[{"type":"global_max_value","value":292.71,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_min_value","value":-130.3,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
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
  "reasoning": "The current evidence provides a clear picture of the behavior around and within the interval containing point 1036. Local behavior around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values, and different trends for the neighboring intervals. The global context confirms that point 1036 holds the minimum value (-130.3), making it necessary to classify it.",
  "evidence_plan": {
    "objective": "Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.",
    "claims_to_support": [
      {
        "claim": "Point 1036 is a global extremum.",
        "required_evidence": ["global_extremum", "endpoint_slope", "pairwise_similarity", "step_level_count"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["Consistency across gathered evidence"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All necessary evidence has been gathered from prior observations, no additional tools are required for classification.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "temporal_profile.short.tool_summaries",
          "field": "endpoint_slope"
        },
        {
          "type": "upstream_observation",
          "ref": "temporal_profile.short.tool_summaries",
          "field": "pairwise_similarity"
        },
        {
          "type": "upstream_observation",
          "ref": "temporal_profile.long.tool_summaries",
          "field": "step_level_count"
        },
        {
          "type": "upstream_observation",
          "ref": "temporal_profile.long.tool_summaries",
          "field": "global_extremum"
        }
      ]
    }
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=9226 completion=479 latency=20.97s

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
{"evidence_plan":{"objective":"Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.","claims_to_support":[{"claim":"Point 1036 is a global extremum.","required_evidence":["global_extremum","endpoint_slope","pairwise_similarity","step_level_count"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["Consistency across gathered evidence"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All necessary evidence has been gathered from prior observations, no additional tools are required for classification.","evidence_sources":[{"type":"upstream_observation","ref":"temporal_profile.short.tool_summaries","field":"endpoint_slope"},{"type":"upstream_observation","ref":"temporal_profile.short.tool_summaries","field":"pairwise_similarity"},{"type":"upstream_observation","ref":"temporal_profile.long.tool_summaries","field":"step_level_count"},{"type":"upstream_observation","ref":"temporal_profile.long.tool_summaries","field":"global_extremum"}]}},"reasoning":"The current evidence provides a clear picture of the behavior around and within the interval containing point 1036. Local behavior around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values, and different trends for the neighboring intervals. The global context confirms that point 1036 holds the minimum value (-130.3), making it necessary to classify it."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The local behavior around point 1036 was examined using two tools: diff_stats to evaluate the endpoint slope and interval_compare to assess pairwise similarity between neighboring points. The diff_stats tool indicated that there is no difference in values around point 1036, resulting in a mean difference and standard deviation of 0.0, with zero sign changes. The interval_compare tool revealed that the left interval [1035, 1036] has a downward trend, whereas the right interval [1036, 1037] is flat, showing a slope difference and indicating a lack of trend consistency.","scale":"short","observations":["Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values.","Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat."],"evidence_intervals":["[1035,1037]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 1036, \"end\": 1036}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 1036, \"end\": 1036}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 1036, \"end\": 1036, \"mean_diff\": 0.0, \"std_diff\": 0.0, \"max_abs_diff\": 0.0, \"n_sign_changes\": 0}, \"error\": null, \"args_fingerprint\": \"5b5d096dccef950c9712c89d4b1aba6e171ecb10\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"interval_compare\", \"arguments\": {\"series_index\": 1, \"start\": 1035, \"end\": 1037, \"left_interval\": [1035, 1036], \"right_interval\": [1036, 1037], \"start/mid/end\": \"mid\"}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 1035, \"end\": 1037, \"left_interval\": [1035, 1036], \"right_interval\": [1036, 1037], \"start/mid/end\": \"mid\"}, \"success\": true, \"data\": {\"series_index\": 1, \"mode\": \"pair\", \"left_interval\": [1035, 1036], \"right_interval\": [1036, 1036], \"left_mean\": -129.79500000000002, \"right_mean\": -130.3, \"left_std\": 0.5050000000000097, \"right_std\": 0.0, \"left_max\": -129.29, \"right_max\": -130.3, \"left_min\": -130.3, \"right_min\": -130.3, \"left_max_index\": 1035, \"right_max_index\": 1036, \"left_n_peaks\": 0, \"right_n_peaks\": 0, \"left_n_troughs\": 0, \"right_n_troughs\": 0, \"left_direction\": \"downward\", \"right_direction\": \"flat\", \"left_slope\": -1.0100000000000193, \"right_slope\": 0.0, \"mean_delta\": -0.5049999999999955, \"max_delta\": -1.0100000000000193, \"same_trend_direction\": false}, \"error\": null, \"args_fingerprint\": \"b965ae5d627fad5674c2ff4fc8b8d81bb9544f29\"}"],"evidence_plan":{"objective":"Examine the local behavior around point 1036 for immediate variations.","claims_to_support":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","required_evidence":["slope"]},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[1035,1037]],"scale":"short"},"validation_needs":["Measure consistency across nearby points"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Endpoint slope around point 1036 needs to be examined.","supports_evidence":["slope"]},{"tool":"interval_compare","reason":"Local consistency measures between neighboring points are required.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"endpoint_slope","input_binding":{"series_index":1,"start":1036,"end":1036}},{"step":2,"tool":"interval_compare","output_key":"pairwise_similarity","input_binding":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"}}],"reasoning":"First, we use 'diff_stats' to get the endpoint slope around point 1036, then 'interval_compare' to analyze pairwise similarity between neighboring points for consistency."},"structured_observations":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","evidence":[{"type":"slope","value":0.0,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","evidence":[{"type":"pairwise_similarity","value":-0.5049999999999955,"source_tool":"interval_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"coverage":{"endpoint_slope":"tool_supported","pairwise_similarity":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":1036,"end":1036},"resolved_arguments":{"series_index":1,"start":1036,"end":1036},"success":true,"data":{"series_index":1,"start":1036,"end":1036,"mean_diff":0.0,"std_diff":0.0,"max_abs_diff":0.0,"n_sign_changes":0},"error":null,"args_fingerprint":"5b5d096dccef950c9712c89d4b1aba6e171ecb10"},{"call_id":"short:step2","step":2,"tool_name":"interval_compare","arguments":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"},"resolved_arguments":{"series_index":1,"start":1035,"end":1037,"left_interval":[1035,1036],"right_interval":[1036,1037],"start/mid/end":"mid"},"success":true,"data":{"series_index":1,"mode":"pair","left_interval":[1035,1036],"right_interval":[1036,1036],"left_mean":-129.79500000000002,"right_mean":-130.3,"left_std":0.5050000000000097,"right_std":0.0,"left_max":-129.29,"right_max":-130.3,"left_min":-130.3,"right_min":-130.3,"left_max_index":1035,"right_max_index":1036,"left_n_peaks":0,"right_n_peaks":0,"left_n_troughs":0,"right_n_troughs":0,"left_direction":"downward","right_direction":"flat","left_slope":-1.0100000000000193,"right_slope":0.0,"mean_delta":-0.5049999999999955,"max_delta":-1.0100000000000193,"same_trend_direction":false},"error":null,"args_fingerprint":"b965ae5d627fad5674c2ff4fc8b8d81bb9544f29"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The analysis includes counting the number of distinct step/plateau levels and identifying the global maximum and minimum values. The step levels tool has determined there are 39 unique levels within the specified interval [0, 1036]. The global extrema tool has provided the maximum value at index 398 as 292.71 and the minimum value at index 1036 as -130.3.","scale":"long","observations":["The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3.","No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036."],"evidence_intervals":["[0, 1036]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 1036, \"n_unique_levels\": 39, \"n_plateau_runs\": 59, \"levels\": [135.53178571428572, 226.8613043478261, 218.48944444444442, 210.07718749999995, 109.4552830188679, 115.72368421052629, 236.1438095238095, 241.8516666666667, 148.89499999999998, 157.89468750000003, 165.77687500000002, 171.80166666666665, 277.1919999999999, 289.97275862068983, 186.15615384615379, 177.0770967741936, 262.8625, 252.9395918367347, 130.00727272727275, 101.23374999999999, 92.61888888888889, 83.82791666666668, 77.30714285714286, 48.43333333333333, 40.512727272727275, 32.351000000000006, 23.952, 16.04125, 8.195555555555554, 0.20250000000000012, -4.41, 66.35714285714286, 58.36333333333334, -90.36714285714285, -97.99666666666667, -105.55333333333334, -113.80142857142857, -122.52000000000001, -128.7575], \"plateau_runs\": [135.53178571428572, 226.8613043478261, 218.48944444444442, 210.07718749999995, 109.4552830188679, 115.72368421052629, 220.2270833333333, 228.29818181818183, 236.1438095238095, 241.8516666666667, 148.89499999999998, 157.89468750000003, 165.77687500000002, 171.80166666666665, 277.1919999999999, 289.97275862068983, 186.15615384615379, 177.0770967741936, 170.324, 262.8625, 252.9395918367347, 146.71370370370374, 138.41478260869573, 130.00727272727275, 223.78324324324328, 215.92368421052632, 208.34, 101.23374999999999, 92.61888888888889, 83.82791666666668, 77.30714285714286, 170.67117647058825, 162.40304347826086, 154.88312499999998, 48.43333333333333, 40.512727272727275, 32.351000000000006, 23.952, 16.04125, 8.195555555555554, 0.20250000000000012, -4.41, 90.18125, 82.32125000000002, 74.48, 66.35714285714286, 58.36333333333334, 50.96333333333333, 43.08857142857143, 35.53285714285714, 27.845714285714283, 20.051428571428573, 14.566666666666665, -90.36714285714285, -97.99666666666667, -105.55333333333334, -113.80142857142857, -122.52000000000001, -128.7575], \"plateau_lengths\": [56, 23, 18, 32, 53, 19, 24, 22, 21, 6, 18, 32, 16, 6, 15, 58, 26, 31, 15, 24, 49, 27, 23, 22, 37, 19, 17, 16, 18, 24, 14, 34, 23, 16, 15, 11, 10, 10, 8, 9, 8, 1, 8, 8, 7, 7, 6, 6, 7, 7, 7, 7, 3, 7, 6, 6, 7, 8, 4], \"tolerance\": 4.2301}, \"error\": null, \"args_fingerprint\": \"2b5a8022f20fa2f6362fd1ed9f6303db57cad136\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1036}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 1036, \"max_index\": 398, \"min_index\": 1036, \"max_value\": 292.71, \"min_value\": -130.3, \"n_peaks\": 7, \"n_troughs\": 6, \"peak_indices\": [56, 273, 398, 491, 636, 781, 926], \"trough_indices\": [142, 274, 490, 635, 780, 925]}, \"error\": null, \"args_fingerprint\": \"519f0a90762ead41ba4a77c99ba151f9db6131a9\"}"],"evidence_plan":{"objective":"Analyze the overall series to establish a global context.","claims_to_support":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","required_evidence":["step_level_count"]},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","required_evidence":["global_extremum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1036]],"scale":"long"},"validation_needs":["Confirm absence of higher/lower points globally"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels, essential for understanding stepwise behavior.","supports_evidence":["step_level_count"]},{"tool":"global_extrema","reason":"Provides global max/min values and indices necessary for confirming extremum status.","supports_evidence":["global_extremum"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"series","input_binding":{"series_index":1,"start":0,"end":1036}},{"step":2,"tool":"global_extrema","output_key":"series","input_binding":{"series_index":1,"start":0,"end":1036}}],"reasoning":"To meet the objective of analyzing the overall series and establishing a global context, the steps include identifying step levels and finding global extrema. The first step involves using the 'step_levels' tool to count discrete step/plateau levels, which is essential for understanding stepwise behavior. Following this, the 'global_extrema' tool will be used to provide global max/min values and their indices, needed to confirm the absence of higher or lower points globally."},"structured_observations":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","evidence":[{"type":"step_level_count","value":39,"source_tool":"step_levels","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","evidence":[{"type":"global_max_value","value":292.71,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_min_value","value":-130.3,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}],"coverage":{"step_level_count":"tool_supported","global_extremum":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":1036},"resolved_arguments":{"series_index":1,"start":0,"end":1036},"success":true,"data":{"series_index":1,"start":0,"end":1036,"n_unique_levels":39,"n_plateau_runs":59,"levels":[135.53178571428572,226.8613043478261,218.48944444444442,210.07718749999995,109.4552830188679,115.72368421052629,236.1438095238095,241.8516666666667,148.89499999999998,157.89468750000003,165.77687500000002,171.80166666666665,277.1919999999999,289.97275862068983,186.15615384615379,177.0770967741936,262.8625,252.9395918367347,130.00727272727275,101.23374999999999,92.61888888888889,83.82791666666668,77.30714285714286,48.43333333333333,40.512727272727275,32.351000000000006,23.952,16.04125,8.195555555555554,0.20250000000000012,-4.41,66.35714285714286,58.36333333333334,-90.36714285714285,-97.99666666666667,-105.55333333333334,-113.80142857142857,-122.52000000000001,-128.7575],"plateau_runs":[135.53178571428572,226.8613043478261,218.48944444444442,210.07718749999995,109.4552830188679,115.72368421052629,220.2270833333333,228.29818181818183,236.1438095238095,241.8516666666667,148.89499999999998,157.89468750000003,165.77687500000002,171.80166666666665,277.1919999999999,289.97275862068983,186.15615384615379,177.0770967741936,170.324,262.8625,252.9395918367347,146.71370370370374,138.41478260869573,130.00727272727275,223.78324324324328,215.92368421052632,208.34,101.23374999999999,92.61888888888889,83.82791666666668,77.30714285714286,170.67117647058825,162.40304347826086,154.88312499999998,48.43333333333333,40.512727272727275,32.351000000000006,23.952,16.04125,8.195555555555554,0.20250000000000012,-4.41,90.18125,82.32125000000002,74.48,66.35714285714286,58.36333333333334,50.96333333333333,43.08857142857143,35.53285714285714,27.845714285714283,20.051428571428573,14.566666666666665,-90.36714285714285,-97.99666666666667,-105.55333333333334,-113.80142857142857,-122.52000000000001,-128.7575],"plateau_lengths":[56,23,18,32,53,19,24,22,21,6,18,32,16,6,15,58,26,31,15,24,49,27,23,22,37,19,17,16,18,24,14,34,23,16,15,11,10,10,8,9,8,1,8,8,7,7,6,6,7,7,7,7,3,7,6,6,7,8,4],"tolerance":4.2301},"error":null,"args_fingerprint":"2b5a8022f20fa2f6362fd1ed9f6303db57cad136"},{"call_id":"long:step2","step":2,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":1036},"resolved_arguments":{"series_index":1,"start":0,"end":1036},"success":true,"data":{"series_index":1,"start":0,"end":1036,"max_index":398,"min_index":1036,"max_value":292.71,"min_value":-130.3,"n_peaks":7,"n_troughs":6,"peak_indices":[56,273,398,491,636,781,926],"trough_indices":[142,274,490,635,780,925]},"error":null,"args_fingerprint":"519f0a90762ead41ba4a77c99ba151f9db6131a9"}],"skipped_stages":[]},"conflicts":[],"summary":"Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values. Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat. The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3. No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036.","structured_by_scale":{"short":[{"claim":"The endpoint slope around point 1036 indicates the direction of immediate change.","evidence":[{"type":"slope","value":0.0,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Pairwise similarity between neighboring points provides local consistency measures.","evidence":[{"type":"pairwise_similarity","value":-0.5049999999999955,"source_tool":"interval_compare","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"The step level count of the series helps identify distinct step/plateau levels.","evidence":[{"type":"step_level_count","value":39,"source_tool":"step_levels","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Global extremum values need to be identified to confirm the absence of higher/lower points globally.","evidence":[{"type":"global_max_value","value":292.71,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_min_value","value":-130.3,"source_tool":"global_extrema","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_extremum"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.","required_measurements":["endpoint_slope","pairwise_similarity","step_level_count","global_extremum"],"validation_requirements":["Ensure the classification is consistent with all gathered evidence"],"target_series":[1],"focus_intervals":[[0,1036]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1037]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
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
  "reasoning": "Based on the gathered evidence, point 1036 does not exhibit any significant local changes and its global value is confirmed as the minimum within the entire series. Therefore, it can be classified as a global extremum.",
  "role": "matching",
  "hypothesis": "Point 1036 is a global extremum.",
  "evidence": [
    "Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values.",
    "The global extrema tool identifies point 1036 as having the minimum value of -130.3."
  ],
  "candidate_preference": "B",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "long:step2"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Point 1036 does not show any significant changes in the local context, as indicated by a mean and standard difference of 0.0.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 0.0,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Point 1036 has been identified as the global minimum value (-130.3) in the series between [0, 1036]",
      "evidence": [
        {
          "type": "global_min_value",
          "value": -130.3,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "endpoint_slope": "tool_supported",
    "global_extremum": "tool_supported",
    "pairwise_similarity": "tool_supported",
    "step_level_count": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1705 completion=246 latency=9.01s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 1036 present a global maximum or minimum value or neither? (The index starts from 0)
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
  "goal": "Identify if the value at point 1036 of Time Series 1 is a global maximum, minimum, or neither.",
  "question_type": "choice",
  "required_output": "Max|Min|Neither",
  "success_criteria": [
    "Accurate identification of the extremum status at point 1036 based on gathered evidence"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Examine the local behavior around point 1036 for immediate variations.",
      "required_measurements": [
        "endpoint_slope",
        "pairwise_similarity"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Analyze the overall series to establish a global context.",
      "required_measurements": [
        "step_level_count",
        "global_extremum"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Compare the identified local and global characteristics to classify the value at point 1036 as a global maximum, minimum, or neither.",
      "required_measurements": [
        "endpoint_slope",
        "pairwise_similarity",
        "step_level_count",
        "global_extremum"
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
          "type": "slope",
          "value": 0.0,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "pairwise_similarity",
          "value": -0.5049999999999955,
          "trusted": true
        }
      ],
      "coverage": {
        "endpoint_slope": "tool_supported",
        "pairwise_similarity": "tool_supported"
      },
      "summary": "Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values. | Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "step_level_count",
          "value": 39,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "global_max_value",
          "value": 292.71,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "global_min_value",
          "value": -130.3,
          "trusted": true
        }
      ],
      "coverage": {
        "step_level_count": "tool_supported",
        "global_extremum": "tool_supported"
      },
      "summary": "The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3. | No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036."
    }
  },
  "conflicts": [],
  "summary": "Endpoint slope analysis around point 1036 shows no significant changes with a mean and standard difference of 0.0, implying stable values. Neighboring intervals [1035,1036] and [1036,1037] exhibit different behaviors, with the first showing a downward trend and the second being flat. The overall series between intervals [0, 1036] contains 39 distinct step/plateau levels. The global extremum values include a maximum of 292.71 and a minimum of -130.3. No points outside these extrema exist within the interval, providing confirmation of the highest and lowest global points relative to the target point 1036."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Point 1036 is a global extremum.",
      "reasoning_chain": [
        "Point 1036 does not show any significant changes in the local context, as indicated by a mean and standard difference of 0.0.",
        "endpoint_slope=0.0",
        "Point 1036 has been identified as the global minimum value (-130.3) in the series between [0, 1036]",
        "global_min_value=-130.3"
      ],
      "candidate_preference": "B",
      "confidence": 1.0,
      "grounded": true,
      "grounded_in": [
        "endpoint_slope",
        "global_min_value"
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
  "reasoning": "Heter reasoning confirms that Point 1036 is identified as the global minimum value (-130.3) in the series between [0, 1036], aligning with the trusted states from Homo perception indicating an endpoint slope of 0.0 and the series having a global minimum of -130.3.",
  "answer": "B",
  "explanation": "Based on the Homo perception, point 1036 shows no significant change in the immediate context with a slope of 0.0 and is confirmed as the global minimum value of -130.3. The Heter reasoning matches this finding, supporting the classification of point 1036 as a global minimum.",
  "confidence": 1.0,
  "conflicts": [],
  "cited_evidence": ["endpoint_slope", "global_min_value"],
  "decision_trace": {
    "metric": "global_min_value",
    "observed_value": -130.3,
    "intervals_from_question": [],
    "matched_label": "global_minimum",
    "matched_letter": "B"
  }
}
```
