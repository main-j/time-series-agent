# Agent IO summary: `Base:synthtic_qa_700:546`

- Architecture pred: `C` (success=True)
- model_calls=12, tool_calls=3, latency=151.5s

## Planner — `planner`

tokens prompt=1034 completion=510 latency=18.08s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 646 present a global maximum or minimum value or neither? (The index starts from 0)
</question>

<candidates>
A) Max
B) Min
C) Neither
</candidates>

<metadata>
local_overall=local; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "To determine if point 646 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity of point 646 and the overall range of the entire time series.",
  "task_summary": "Determine whether the value at point 646 of a given time series is a global maximum, minimum, or neither.",
  "target_output": "choice",
  "answer_type": "choice",
  "capability": "time-series analysis",
  "scope": "local",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.",
      "required_measurements": ["endpoint_slope", "step_level_count"],
      "validation_requirements": ["Check consistency with neighboring points to ensure accurate identification of local extrema."],
      "target_series": [1],
      "focus_intervals": [[645, 647]]
    },
    {
      "scale": "long",
      "objective": "Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.",
      "required_measurements": ["global_maximum", "global_minimum"],
      "validation_requirements": ["Verify the identified global extrema against the whole series for robustness."],
      "target_series": [1],
      "focus_intervals": [[0, 1037]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.",
      "required_measurements": ["global_maximum", "global_minimum", "endpoint_slope", "step_level_count"],
      "validation_requirements": ["Confirm the logical consistency between local and global scale analyses."],
      "target_series": [1],
      "focus_intervals": [[0, 1037]]
    }
  ],
  "success_criteria": ["Correctly identify if point 646 is a global maximum, minimum, or neither based on gathered data."],
  "notes": "Ensure that all necessary checks are performed to validate findings across different scales."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4123 completion=359 latency=14.00s

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
{"scale":"short","objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["Check consistency with neighboring points to ensure accurate identification of local extrema."],"target_series":[1],"focus_intervals":[[645,647]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 646 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity of point 646 and the overall range of the entire time series.","task_summary":"Determine whether the value at point 646 of a given time series is a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["Check consistency with neighboring points to ensure accurate identification of local extrema."],"target_series":[1],"focus_intervals":[[645,647]]},{"scale":"long","objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","required_measurements":["global_maximum","global_minimum"],"validation_requirements":["Verify the identified global extrema against the whole series for robustness."],"target_series":[1],"focus_intervals":[[0,1037]]}],"hetero_assignments":[{"role":"reasoning","objective":"Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.","required_measurements":["global_maximum","global_minimum","endpoint_slope","step_level_count"],"validation_requirements":["Confirm the logical consistency between local and global scale analyses."],"target_series":[1],"focus_intervals":[[0,1037]]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correctly identify if point 646 is a global maximum, minimum, or neither based on gathered data."],"notes":"Ensure that all necessary checks are performed to validate findings across different scales."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. We need to measure endpoint slopes and count step levels within the specified focus intervals.",
  "evidence_plan": {
    "objective": "Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.",
    "claims_to_support": [
      {
        "claim": "Point 646 has an abrupt change in its local behavior.",
        "required_evidence": ["endpoint_slope"]
      },
      {
        "claim": "There are distinct step levels around point 646.",
        "required_evidence": ["step_level_count"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[645,647]],
      "scale": "short"
    },
    "validation_needs": ["Check consistency with neighboring points to ensure accurate identification of local extrema."]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "diff_stats",
        "reason": "To identify abrupt changes or discontinuities around point 646, we need first-difference statistics, such as endpoint slopes, to understand the rate of change.",
        "supports_evidence": ["endpoint_slope"]
      },
      {
        "tool": "step_levels",
        "reason": "To identify the presence of distinct step levels around point 646, we need to count the discrete steps in the local region.",
        "supports_evidence": ["step_level_count"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=807 completion=194 latency=6.91s

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
{"evidence_plan":{"objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","claims_to_support":[{"claim":"Point 646 has an abrupt change in its local behavior.","required_evidence":["endpoint_slope"]},{"claim":"There are distinct step levels around point 646.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[645,647]],"scale":"short"},"validation_needs":["Check consistency with neighboring points to ensure accurate identification of local extrema."]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To identify abrupt changes or discontinuities around point 646, we need first-difference statistics, such as endpoint slopes, to understand the rate of change.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"To identify the presence of distinct step levels around point 646, we need to count the discrete steps in the local region.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"reasoning":"The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. We need to measure endpoint slopes and count step levels within the specified focus intervals."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- diff_stats
  inputs: series_index, start, end
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. First, we use diff_stats to measure endpoint slopes, then we use step_levels to count the discrete steps in the local region.",
  "workflow": [
    {
      "step": 1,
      "tool": "diff_stats",
      "output_key": "abrupt_change_stats",
      "input_binding": {
        "series_index": 1,
        "start": 645,
        "end": 647
      }
    },
    {
      "step": 2,
      "tool": "step_levels",
      "output_key": "step_level_counts",
      "input_binding": {
        "series_index": 1,
        "start": 645,
        "end": 647
      }
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=901 completion=158 latency=5.68s

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
{"workflow":[{"step":1,"tool":"diff_stats","output_key":"abrupt_change_stats","input_binding":{"series_index":1,"start":645,"end":647}},{"step":2,"tool":"step_levels","output_key":"step_level_counts","input_binding":{"series_index":1,"start":645,"end":647}}],"reasoning":"The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. First, we use diff_stats to measure endpoint slopes, then we use step_levels to count the discrete steps in the local region."}
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
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
</tool_invocation_spec>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["Check consistency with neighboring points to ensure accurate identification of local extrema."],"target_series":[1],"focus_intervals":[[645,647]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima. This involves measuring endpoint slopes and counting discrete step levels within the specified interval.",
  "calls": [
    {
      "step": 1,
      "tool": "diff_stats",
      "args": {
        "series_index": 1,
        "start": 645,
        "end": 647
      }
    },
    {
      "step": 2,
      "tool": "step_levels",
      "args": {
        "series_index": 1,
        "start": 645,
        "end": 647
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1412 completion=447 latency=16.01s

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
{"evidence_plan":{"objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","claims_to_support":[{"claim":"Point 646 has an abrupt change in its local behavior.","required_evidence":["endpoint_slope"]},{"claim":"There are distinct step levels around point 646.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[645,647]],"scale":"short"},"validation_needs":["Check consistency with neighboring points to ensure accurate identification of local extrema."]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To identify abrupt changes or discontinuities around point 646, we need first-difference statistics, such as endpoint slopes, to understand the rate of change.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"To identify the presence of distinct step levels around point 646, we need to count the discrete steps in the local region.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"reasoning":"The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. We need to measure endpoint slopes and count step levels within the specified focus intervals."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "diff_stats",
    "arguments": {
      "series_index": 1,
      "start": 645,
      "end": 647
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 645,
      "end": 647
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 645,
      "end": 647,
      "mean_diff": 16.839999999999975,
      "std_diff": 18.03000000000003,
      "max_abs_diff": 34.870000000000005,
      "n_sign_changes": 1
    },
    "error": null,
    "args_fingerprint": "f2f091658a883754e5797293853b32f5ce02addc"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "step_levels",
    "arguments": {
      "series_index": 1,
      "start": 645,
      "end": 647
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 645,
      "end": 647
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 645,
      "end": 647,
      "n_unique_levels": 3,
      "n_plateau_runs": 3,
      "levels": [
        -609.8,
        -574.93,
        -576.12
      ],
      "plateau_runs": [
        -609.8,
        -574.93,
        -576.12
      ],
      "plateau_lengths": [
        1,
        1,
        1
      ],
      "tolerance": 0.34870000000000007
    },
    "error": null,
    "args_fingerprint": "edccb7d904065f7b1a1612a265c67ed46b98101b"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["Check consistency with neighboring points to ensure accurate identification of local extrema."],"target_series":[1],"focus_intervals":[[645,647]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Based on the executed_steps, there is an analysis of the local behavior around point 646, with a focus on detecting abrupt changes and counting distinct step levels. The diff_stats tool provides first-difference statistics which indicate a mean difference of approximately 16.84 and a maximum absolute difference of approximately 34.87 within the interval [645, 647]. The step_levels tool counts three unique step levels within the same interval, suggesting the presence of distinct step behavior around point 646.",
  "scale": "short",
  "observations": ["The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes.", "Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646."],
  "evidence_intervals": ["[645, 647]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Point 646 has an abrupt change in its local behavior.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 16.84,
          "source_tool": "diff_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "endpoint_slope"
    },
    {
      "claim": "There are distinct step levels around point 646.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 3,
          "source_tool": "step_levels",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "step_level_count"
    }
  ],
  "coverage": {"endpoint_slope": "tool_supported", "step_level_count": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4124 completion=290 latency=11.46s

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
{"scale":"long","objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","required_measurements":["global_maximum","global_minimum"],"validation_requirements":["Verify the identified global extrema against the whole series for robustness."],"target_series":[1],"focus_intervals":[[0,1037]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 646 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity of point 646 and the overall range of the entire time series.","task_summary":"Determine whether the value at point 646 of a given time series is a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["Check consistency with neighboring points to ensure accurate identification of local extrema."],"target_series":[1],"focus_intervals":[[645,647]]},{"scale":"long","objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","required_measurements":["global_maximum","global_minimum"],"validation_requirements":["Verify the identified global extrema against the whole series for robustness."],"target_series":[1],"focus_intervals":[[0,1037]]}],"hetero_assignments":[{"role":"reasoning","objective":"Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.","required_measurements":["global_maximum","global_minimum","endpoint_slope","step_level_count"],"validation_requirements":["Confirm the logical consistency between local and global scale analyses."],"target_series":[1],"focus_intervals":[[0,1037]]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correctly identify if point 646 is a global maximum, minimum, or neither based on gathered data."],"notes":"Ensure that all necessary checks are performed to validate findings across different scales."}
</plan_context>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to determine if the value at point 646 in the time series represents a global extreme. To achieve this, we need to identify the global maximum and minimum values across the entire series.",
  "evidence_plan": {
    "objective": "Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.",
    "claims_to_support": [
      {
        "claim": "Point 646 represents a global maximum.",
        "required_evidence": ["global_maximum"]
      },
      {
        "claim": "Point 646 represents a global minimum.",
        "required_evidence": ["global_minimum"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[0,1037]],
      "scale": "long"
    },
    "validation_needs": ["Verify the identified global extrema against the whole series for robustness."]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "global_extrema",
        "reason": "Identifying the global maximum and minimum requires detecting the highest and lowest values in the entire series.",
        "supports_evidence": ["global_maximum", "global_minimum"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=736 completion=131 latency=4.70s

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
{"evidence_plan":{"objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","claims_to_support":[{"claim":"Point 646 represents a global maximum.","required_evidence":["global_maximum"]},{"claim":"Point 646 represents a global minimum.","required_evidence":["global_minimum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1037]],"scale":"long"},"validation_needs":["Verify the identified global extrema against the whole series for robustness."]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"Identifying the global maximum and minimum requires detecting the highest and lowest values in the entire series.","supports_evidence":["global_maximum","global_minimum"]}],"no_tool_decision":null},"reasoning":"The objective is to determine if the value at point 646 in the time series represents a global extreme. To achieve this, we need to identify the global maximum and minimum values across the entire series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- global_extrema
  inputs: series_index, start, end, index, index_base
  outputs: series
</io_concepts>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "To determine if point 646 represents a global extreme, we must first identify the global maximum and minimum values across the entire series using the global_extrema tool.",
  "workflow": [
    {
      "step": 1,
      "tool": "global_extrema",
      "output_key": "global_extrema_result",
      "input_binding": {
        "series_index": 0,
        "start": 0,
        "end": 1037,
        "index": 646,
        "index_base": 0
      }
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=814 completion=140 latency=5.03s

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
{"workflow":[{"step":1,"tool":"global_extrema","output_key":"global_extrema_result","input_binding":{"series_index":0,"start":0,"end":1037,"index":646,"index_base":0}}],"reasoning":"To determine if point 646 represents a global extreme, we must first identify the global maximum and minimum values across the entire series using the global_extrema tool."}
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
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","required_measurements":["global_maximum","global_minimum"],"validation_requirements":["Verify the identified global extrema against the whole series for robustness."],"target_series":[1],"focus_intervals":[[0,1037]]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme. The required measurements include the global maximum and minimum values. The workflow involves using the global_extrema tool to identify these extremes.",
  "calls": [
    {
      "step": 1,
      "tool": "global_extrema",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 1037,
        "index": 646,
        "index_base": 0
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1211 completion=413 latency=14.72s

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
{"evidence_plan":{"objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","claims_to_support":[{"claim":"Point 646 represents a global maximum.","required_evidence":["global_maximum"]},{"claim":"Point 646 represents a global minimum.","required_evidence":["global_minimum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1037]],"scale":"long"},"validation_needs":["Verify the identified global extrema against the whole series for robustness."]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"Identifying the global maximum and minimum requires detecting the highest and lowest values in the entire series.","supports_evidence":["global_maximum","global_minimum"]}],"no_tool_decision":null},"reasoning":"The objective is to determine if the value at point 646 in the time series represents a global extreme. To achieve this, we need to identify the global maximum and minimum values across the entire series."}
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
      "end": 1037,
      "index": 646,
      "index_base": 0
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 1037,
      "index": 646,
      "index_base": 0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 1037,
      "max_index": 43,
      "min_index": 1037,
      "max_value": -38.29,
      "min_value": -1304.36,
      "n_peaks": 7,
      "n_troughs": 7,
      "peak_indices": [
        114,
        247,
        380,
        513,
        646,
        779,
        912
      ],
      "trough_indices": [
        113,
        246,
        379,
        512,
        645,
        778,
        911
      ],
      "query_index": 646,
      "query_position": 646,
      "query_value": -574.93,
      "is_global_max": false,
      "is_global_min": false,
      "is_local_peak": true,
      "is_local_trough": false
    },
    "error": null,
    "args_fingerprint": "693d63d500eea32eedb8479115c19f3ac3e36925"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","required_measurements":["global_maximum","global_minimum"],"validation_requirements":["Verify the identified global extrema against the whole series for robustness."],"target_series":[1],"focus_intervals":[[0,1037]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective was to compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme. The global extrema analysis was successfully performed on the time series covering the interval [0,1037]. The point at index 646 does not represent either a global maximum or a global minimum.",
  "scale": "long",
  "observations": ["Point 646 is a local peak but not a global maximum or minimum.", "The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36."],
  "evidence_intervals": ["[0,1037]"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Point 646 represents a global maximum.",
      "evidence": [
        {
          "type": "global_extrema",
          "value": false,
          "source_tool": "global_extrema",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_maximum"
    },
    {
      "claim": "Point 646 represents a global minimum.",
      "evidence": [
        {
          "type": "global_extrema",
          "value": false,
          "source_tool": "global_extrema",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_minimum"
    }
  ],
  "coverage": {"global_maximum": "tool_supported", "global_minimum": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=7758 completion=440 latency=18.66s

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
{"role":"reasoning","objective":"Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.","required_measurements":["global_maximum","global_minimum","endpoint_slope","step_level_count"],"validation_requirements":["Confirm the logical consistency between local and global scale analyses."],"target_series":[1],"focus_intervals":[[0,1037]]}
</assignment>

<plan_context>
{"reasoning":"To determine if point 646 in the given univariate time series is a global maximum, minimum, or neither, we need to analyze the behavior around that point. This involves examining both the immediate vicinity of point 646 and the overall range of the entire time series.","task_summary":"Determine whether the value at point 646 of a given time series is a global maximum, minimum, or neither.","target_output":"choice","answer_type":"choice","capability":"time-series analysis","scope":"local","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["Check consistency with neighboring points to ensure accurate identification of local extrema."],"target_series":[1],"focus_intervals":[[645,647]]},{"scale":"long","objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","required_measurements":["global_maximum","global_minimum"],"validation_requirements":["Verify the identified global extrema against the whole series for robustness."],"target_series":[1],"focus_intervals":[[0,1037]]}],"hetero_assignments":[{"role":"reasoning","objective":"Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.","required_measurements":["global_maximum","global_minimum","endpoint_slope","step_level_count"],"validation_requirements":["Confirm the logical consistency between local and global scale analyses."],"target_series":[1],"focus_intervals":[[0,1037]]}],"scales":["short","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Correctly identify if point 646 is a global maximum, minimum, or neither based on gathered data."],"notes":"Ensure that all necessary checks are performed to validate findings across different scales."}
</plan_context>

<task_summary>
Determine whether the value at point 646 of a given time series is a global maximum, minimum, or neither.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Based on the executed_steps, there is an analysis of the local behavior around point 646, with a focus on detecting abrupt changes and counting distinct step levels. The diff_stats tool provides first-difference statistics which indicate a mean difference of approximately 16.84 and a maximum absolute difference of approximately 34.87 within the interval [645, 647]. The step_levels tool counts three unique step levels within the same interval, suggesting the presence of distinct step behavior around point 646.","scale":"short","observations":["The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes.","Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646."],"evidence_intervals":["[645, 647]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 645, \"end\": 647, \"mean_diff\": 16.839999999999975, \"std_diff\": 18.03000000000003, \"max_abs_diff\": 34.870000000000005, \"n_sign_changes\": 1}, \"error\": null, \"args_fingerprint\": \"f2f091658a883754e5797293853b32f5ce02addc\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 645, \"end\": 647, \"n_unique_levels\": 3, \"n_plateau_runs\": 3, \"levels\": [-609.8, -574.93, -576.12], \"plateau_runs\": [-609.8, -574.93, -576.12], \"plateau_lengths\": [1, 1, 1], \"tolerance\": 0.34870000000000007}, \"error\": null, \"args_fingerprint\": \"edccb7d904065f7b1a1612a265c67ed46b98101b\"}"],"evidence_plan":{"objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","claims_to_support":[{"claim":"Point 646 has an abrupt change in its local behavior.","required_evidence":["endpoint_slope"]},{"claim":"There are distinct step levels around point 646.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[645,647]],"scale":"short"},"validation_needs":["Check consistency with neighboring points to ensure accurate identification of local extrema."]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To identify abrupt changes or discontinuities around point 646, we need first-difference statistics, such as endpoint slopes, to understand the rate of change.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"To identify the presence of distinct step levels around point 646, we need to count the discrete steps in the local region.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"abrupt_change_stats","input_binding":{"series_index":1,"start":645,"end":647}},{"step":2,"tool":"step_levels","output_key":"step_level_counts","input_binding":{"series_index":1,"start":645,"end":647}}],"reasoning":"The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. First, we use diff_stats to measure endpoint slopes, then we use step_levels to count the discrete steps in the local region."},"structured_observations":[{"claim":"Point 646 has an abrupt change in its local behavior.","evidence":[{"type":"endpoint_slope","value":16.84,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"There are distinct step levels around point 646.","evidence":[{"type":"step_level_count","value":3,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"endpoint_slope":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":645,"end":647},"resolved_arguments":{"series_index":1,"start":645,"end":647},"success":true,"data":{"series_index":1,"start":645,"end":647,"mean_diff":16.839999999999975,"std_diff":18.03000000000003,"max_abs_diff":34.870000000000005,"n_sign_changes":1},"error":null,"args_fingerprint":"f2f091658a883754e5797293853b32f5ce02addc"},{"call_id":"short:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1,"start":645,"end":647},"resolved_arguments":{"series_index":1,"start":645,"end":647},"success":true,"data":{"series_index":1,"start":645,"end":647,"n_unique_levels":3,"n_plateau_runs":3,"levels":[-609.8,-574.93,-576.12],"plateau_runs":[-609.8,-574.93,-576.12],"plateau_lengths":[1,1,1],"tolerance":0.34870000000000007},"error":null,"args_fingerprint":"edccb7d904065f7b1a1612a265c67ed46b98101b"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The objective was to compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme. The global extrema analysis was successfully performed on the time series covering the interval [0,1037]. The point at index 646 does not represent either a global maximum or a global minimum.","scale":"long","observations":["Point 646 is a local peak but not a global maximum or minimum.","The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36."],"evidence_intervals":["[0,1037]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1037, \"index\": 646, \"index_base\": 0}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1037, \"index\": 646, \"index_base\": 0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 1037, \"max_index\": 43, \"min_index\": 1037, \"max_value\": -38.29, \"min_value\": -1304.36, \"n_peaks\": 7, \"n_troughs\": 7, \"peak_indices\": [114, 247, 380, 513, 646, 779, 912], \"trough_indices\": [113, 246, 379, 512, 645, 778, 911], \"query_index\": 646, \"query_position\": 646, \"query_value\": -574.93, \"is_global_max\": false, \"is_global_min\": false, \"is_local_peak\": true, \"is_local_trough\": false}, \"error\": null, \"args_fingerprint\": \"693d63d500eea32eedb8479115c19f3ac3e36925\"}"],"evidence_plan":{"objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","claims_to_support":[{"claim":"Point 646 represents a global maximum.","required_evidence":["global_maximum"]},{"claim":"Point 646 represents a global minimum.","required_evidence":["global_minimum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1037]],"scale":"long"},"validation_needs":["Verify the identified global extrema against the whole series for robustness."]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"Identifying the global maximum and minimum requires detecting the highest and lowest values in the entire series.","supports_evidence":["global_maximum","global_minimum"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"global_extrema","output_key":"global_extrema_result","input_binding":{"series_index":0,"start":0,"end":1037,"index":646,"index_base":0}}],"reasoning":"To determine if point 646 represents a global extreme, we must first identify the global maximum and minimum values across the entire series using the global_extrema tool."},"structured_observations":[{"claim":"Point 646 represents a global maximum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum"},{"claim":"Point 646 represents a global minimum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum"}],"coverage":{"global_maximum":"tool_supported","global_minimum":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":1037,"index":646,"index_base":0},"resolved_arguments":{"series_index":1,"start":0,"end":1037,"index":646,"index_base":0},"success":true,"data":{"series_index":1,"start":0,"end":1037,"max_index":43,"min_index":1037,"max_value":-38.29,"min_value":-1304.36,"n_peaks":7,"n_troughs":7,"peak_indices":[114,247,380,513,646,779,912],"trough_indices":[113,246,379,512,645,778,911],"query_index":646,"query_position":646,"query_value":-574.93,"is_global_max":false,"is_global_min":false,"is_local_peak":true,"is_local_trough":false},"error":null,"args_fingerprint":"693d63d500eea32eedb8479115c19f3ac3e36925"}],"skipped_stages":[]},"conflicts":[],"summary":"The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes. Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646. Point 646 is a local peak but not a global maximum or minimum. The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36.","structured_by_scale":{"short":[{"claim":"Point 646 has an abrupt change in its local behavior.","evidence":[{"type":"endpoint_slope","value":16.84,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"There are distinct step levels around point 646.","evidence":[{"type":"step_level_count","value":3,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"long":[{"claim":"Point 646 represents a global maximum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum"},{"claim":"Point 646 represents a global minimum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current evidence from the short and long scale analyses shows that point 646 has local abrupt changes and distinct step levels but does not represent a global maximum or minimum. To confirm the logical consistency between local and global scale analyses, no further tools are needed since the evidence already indicates the required facts.",
  "evidence_plan": {
    "objective": "Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.",
    "claims_to_support": [
      {
        "claim": "Point 646 represents a global maximum.",
        "required_evidence": ["global_maximum"]
      },
      {
        "claim": "Point 646 represents a global minimum.",
        "required_evidence": ["global_minimum"]
      },
      {
        "claim": "Point 646 has abrupt changes in its local behavior.",
        "required_evidence": ["endpoint_slope"]
      },
      {
        "claim": "There are distinct step levels around point 646.",
        "required_evidence": ["step_level_count"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "reasoning"
    },
    "validation_needs": ["logical_consistency_between_scales"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All required evidence is already available from previous tasks, and the logical consistency is directly supported by existing findings.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_extrema"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step1",
          "field": "diff_stats"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step2",
          "field": "step_levels"
        }
      ]
    }
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=4399 completion=724 latency=27.60s

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
{"evidence_plan":{"objective":"Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.","claims_to_support":[{"claim":"Point 646 represents a global maximum.","required_evidence":["global_maximum"]},{"claim":"Point 646 represents a global minimum.","required_evidence":["global_minimum"]},{"claim":"Point 646 has abrupt changes in its local behavior.","required_evidence":["endpoint_slope"]},{"claim":"There are distinct step levels around point 646.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"role":"reasoning"},"validation_needs":["logical_consistency_between_scales"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All required evidence is already available from previous tasks, and the logical consistency is directly supported by existing findings.","evidence_sources":[{"type":"upstream_observation","ref":"long:step1","field":"global_extrema"},{"type":"upstream_observation","ref":"short:step1","field":"diff_stats"},{"type":"upstream_observation","ref":"short:step2","field":"step_levels"}]}},"reasoning":"The current evidence from the short and long scale analyses shows that point 646 has local abrupt changes and distinct step levels but does not represent a global maximum or minimum. To confirm the logical consistency between local and global scale analyses, no further tools are needed since the evidence already indicates the required facts."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Based on the executed_steps, there is an analysis of the local behavior around point 646, with a focus on detecting abrupt changes and counting distinct step levels. The diff_stats tool provides first-difference statistics which indicate a mean difference of approximately 16.84 and a maximum absolute difference of approximately 34.87 within the interval [645, 647]. The step_levels tool counts three unique step levels within the same interval, suggesting the presence of distinct step behavior around point 646.","scale":"short","observations":["The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes.","Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646."],"evidence_intervals":["[645, 647]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 645, \"end\": 647, \"mean_diff\": 16.839999999999975, \"std_diff\": 18.03000000000003, \"max_abs_diff\": 34.870000000000005, \"n_sign_changes\": 1}, \"error\": null, \"args_fingerprint\": \"f2f091658a883754e5797293853b32f5ce02addc\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 645, \"end\": 647}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 645, \"end\": 647, \"n_unique_levels\": 3, \"n_plateau_runs\": 3, \"levels\": [-609.8, -574.93, -576.12], \"plateau_runs\": [-609.8, -574.93, -576.12], \"plateau_lengths\": [1, 1, 1], \"tolerance\": 0.34870000000000007}, \"error\": null, \"args_fingerprint\": \"edccb7d904065f7b1a1612a265c67ed46b98101b\"}"],"evidence_plan":{"objective":"Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.","claims_to_support":[{"claim":"Point 646 has an abrupt change in its local behavior.","required_evidence":["endpoint_slope"]},{"claim":"There are distinct step levels around point 646.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[645,647]],"scale":"short"},"validation_needs":["Check consistency with neighboring points to ensure accurate identification of local extrema."]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"To identify abrupt changes or discontinuities around point 646, we need first-difference statistics, such as endpoint slopes, to understand the rate of change.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"To identify the presence of distinct step levels around point 646, we need to count the discrete steps in the local region.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"abrupt_change_stats","input_binding":{"series_index":1,"start":645,"end":647}},{"step":2,"tool":"step_levels","output_key":"step_level_counts","input_binding":{"series_index":1,"start":645,"end":647}}],"reasoning":"The objective requires identifying the local behavior around point 646 to detect any abrupt changes or local maxima/minima. First, we use diff_stats to measure endpoint slopes, then we use step_levels to count the discrete steps in the local region."},"structured_observations":[{"claim":"Point 646 has an abrupt change in its local behavior.","evidence":[{"type":"endpoint_slope","value":16.84,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"There are distinct step levels around point 646.","evidence":[{"type":"step_level_count","value":3,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"endpoint_slope":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":645,"end":647},"resolved_arguments":{"series_index":1,"start":645,"end":647},"success":true,"data":{"series_index":1,"start":645,"end":647,"mean_diff":16.839999999999975,"std_diff":18.03000000000003,"max_abs_diff":34.870000000000005,"n_sign_changes":1},"error":null,"args_fingerprint":"f2f091658a883754e5797293853b32f5ce02addc"},{"call_id":"short:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1,"start":645,"end":647},"resolved_arguments":{"series_index":1,"start":645,"end":647},"success":true,"data":{"series_index":1,"start":645,"end":647,"n_unique_levels":3,"n_plateau_runs":3,"levels":[-609.8,-574.93,-576.12],"plateau_runs":[-609.8,-574.93,-576.12],"plateau_lengths":[1,1,1],"tolerance":0.34870000000000007},"error":null,"args_fingerprint":"edccb7d904065f7b1a1612a265c67ed46b98101b"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The objective was to compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme. The global extrema analysis was successfully performed on the time series covering the interval [0,1037]. The point at index 646 does not represent either a global maximum or a global minimum.","scale":"long","observations":["Point 646 is a local peak but not a global maximum or minimum.","The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36."],"evidence_intervals":["[0,1037]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"global_extrema\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1037, \"index\": 646, \"index_base\": 0}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 1037, \"index\": 646, \"index_base\": 0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 1037, \"max_index\": 43, \"min_index\": 1037, \"max_value\": -38.29, \"min_value\": -1304.36, \"n_peaks\": 7, \"n_troughs\": 7, \"peak_indices\": [114, 247, 380, 513, 646, 779, 912], \"trough_indices\": [113, 246, 379, 512, 645, 778, 911], \"query_index\": 646, \"query_position\": 646, \"query_value\": -574.93, \"is_global_max\": false, \"is_global_min\": false, \"is_local_peak\": true, \"is_local_trough\": false}, \"error\": null, \"args_fingerprint\": \"693d63d500eea32eedb8479115c19f3ac3e36925\"}"],"evidence_plan":{"objective":"Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.","claims_to_support":[{"claim":"Point 646 represents a global maximum.","required_evidence":["global_maximum"]},{"claim":"Point 646 represents a global minimum.","required_evidence":["global_minimum"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,1037]],"scale":"long"},"validation_needs":["Verify the identified global extrema against the whole series for robustness."]},"capability_selection":{"selected_tools":[{"tool":"global_extrema","reason":"Identifying the global maximum and minimum requires detecting the highest and lowest values in the entire series.","supports_evidence":["global_maximum","global_minimum"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"global_extrema","output_key":"global_extrema_result","input_binding":{"series_index":0,"start":0,"end":1037,"index":646,"index_base":0}}],"reasoning":"To determine if point 646 represents a global extreme, we must first identify the global maximum and minimum values across the entire series using the global_extrema tool."},"structured_observations":[{"claim":"Point 646 represents a global maximum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum"},{"claim":"Point 646 represents a global minimum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum"}],"coverage":{"global_maximum":"tool_supported","global_minimum":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"global_extrema","arguments":{"series_index":1,"start":0,"end":1037,"index":646,"index_base":0},"resolved_arguments":{"series_index":1,"start":0,"end":1037,"index":646,"index_base":0},"success":true,"data":{"series_index":1,"start":0,"end":1037,"max_index":43,"min_index":1037,"max_value":-38.29,"min_value":-1304.36,"n_peaks":7,"n_troughs":7,"peak_indices":[114,247,380,513,646,779,912],"trough_indices":[113,246,379,512,645,778,911],"query_index":646,"query_position":646,"query_value":-574.93,"is_global_max":false,"is_global_min":false,"is_local_peak":true,"is_local_trough":false},"error":null,"args_fingerprint":"693d63d500eea32eedb8479115c19f3ac3e36925"}],"skipped_stages":[]},"conflicts":[],"summary":"The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes. Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646. Point 646 is a local peak but not a global maximum or minimum. The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36.","structured_by_scale":{"short":[{"claim":"Point 646 has an abrupt change in its local behavior.","evidence":[{"type":"endpoint_slope","value":16.84,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"There are distinct step levels around point 646.","evidence":[{"type":"step_level_count","value":3,"source_tool":"step_levels","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"long":[{"claim":"Point 646 represents a global maximum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_maximum"},{"claim":"Point 646 represents a global minimum.","evidence":[{"type":"global_extrema","value":false,"source_tool":"global_extrema","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_minimum"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.","required_measurements":["global_maximum","global_minimum","endpoint_slope","step_level_count"],"validation_requirements":["Confirm the logical consistency between local and global scale analyses."],"target_series":[1],"focus_intervals":[[0,1037]]}
</assignment>

<metadata>
subset=Base; local_overall=local; task_type=['index']; domain=synthetic; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[1038]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Based on the gathered evidence, point 646 does not represent a global maximum or minimum but exhibits local behavior characterized by abrupt changes and distinct step levels.",
  "role": "reasoning",
  "hypothesis": "Point 646 has local characteristics such as abrupt changes and distinct step levels, but it does not represent a global maximum or minimum.",
  "evidence": [
    "The global_extrema tool confirms that point 646 does not represent a global maximum or minimum. The maximum value is found at index 43 with a value of -38.29, and the minimum value is at index 1037 with a value of -1304.36.",
    "First-difference statistics indicate a mean difference of approximately 16.84 and a maximum absolute difference of approximately 34.87 within the interval [645, 647], suggesting an abrupt change in local behavior around point 646.",
    "Three unique step levels were identified within the interval [645, 647], confirming the presence of distinct step levels around point 646."
  ],
  "candidate_preference": null,
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["long:step1", "short:step1", "short:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Point 646 represents a global maximum.",
      "evidence": [
        {
          "type": "global_extrema",
          "value": false,
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Point 646 represents a global minimum.",
      "evidence": [
        {
          "type": "global_extrema",
          "value": false,
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Point 646 has abrupt changes in its local behavior.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 16.84,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are distinct step levels around point 646.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 3,
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "global_maximum": "tool_supported",
    "global_minimum": "tool_supported",
    "endpoint_slope": "tool_supported",
    "step_level_count": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1571 completion=234 latency=8.57s

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
Here is a list of values in a Time Series 1. Based on provided Time Series 1, does point 646 present a global maximum or minimum value or neither? (The index starts from 0)
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
  "goal": "Determine whether the value at point 646 of a given time series is a global maximum, minimum, or neither.",
  "question_type": "choice",
  "required_output": "choice",
  "success_criteria": [
    "Correctly identify if point 646 is a global maximum, minimum, or neither based on gathered data."
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Identify the local behavior around point 646 to detect any abrupt changes or local maxima/minima.",
      "required_measurements": [
        "endpoint_slope",
        "step_level_count"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Compare the value at point 646 to the entire span of the time series to determine if it represents a global extreme.",
      "required_measurements": [
        "global_maximum",
        "global_minimum"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Reason about whether the value at point 646 is a global maximum, minimum, or neither based on gathered evidence.",
      "required_measurements": [
        "global_maximum",
        "global_minimum",
        "endpoint_slope",
        "step_level_count"
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
          "value": 16.84,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "step_level_count",
          "value": 3,
          "trusted": true
        }
      ],
      "coverage": {
        "endpoint_slope": "tool_supported",
        "step_level_count": "tool_supported"
      },
      "summary": "The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes. | Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_extrema",
          "value": false,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "global_extrema",
          "value": false,
          "trusted": true
        }
      ],
      "coverage": {
        "global_maximum": "tool_supported",
        "global_minimum": "tool_supported"
      },
      "summary": "Point 646 is a local peak but not a global maximum or minimum. | The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36."
    }
  },
  "conflicts": [],
  "summary": "The analysis around point 646 shows significant differences between neighboring points, indicating potential abrupt changes. Distinct step levels have been identified within the focus interval, supporting claims of changes in local behavior around point 646. Point 646 is a local peak but not a global maximum or minimum. The global maximum occurs at index 43 with a value of -38.29 and the global minimum occurs at index 1037 with a value of -1304.36."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
      "hypothesis": "Point 646 has local characteristics such as abrupt changes and distinct step levels, but it does not represent a global maximum or minimum.",
      "reasoning_chain": [
        "Point 646 represents a global maximum.",
        "global_extrema=False",
        "Point 646 represents a global minimum.",
        "global_extrema=False",
        "Point 646 has abrupt changes in its local behavior.",
        "endpoint_slope=16.84",
        "There are distinct step levels around point 646.",
        "step_level_count=3"
      ],
      "candidate_preference": null,
      "confidence": 1.0,
      "grounded": true,
      "grounded_in": [
        "global_extrema",
        "endpoint_slope",
        "step_level_count"
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
  "reasoning": "Heter reasoning concludes that point 646 is a local peak but not a global maximum or minimum. This is supported by the Homo perception which identifies significant differences between neighboring points and distinct step levels around point 646, but also explicitly states that point 646 is not a global maximum or minimum. Homo perception provides specific details about global extrema occurring at different indices, further reinforcing this conclusion.",
  "answer": "C",
  "explanation": "The value at point 646 is neither a global maximum nor a global minimum according to the analysis provided. Although point 646 represents a local peak, it does not meet the criteria for being a global extreme value.",
  "confidence": 1.0,
  "conflicts": [],
  "cited_evidence": ["global_extrema", "endpoint_slope", "step_level_count"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "C"
  }
}
```
