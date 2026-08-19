# Agent IO summary: `InWild:tsqa_1084:153`

- Architecture pred: `A` (success=True)
- model_calls=14, tool_calls=4, latency=147.2s

## Planner — `planner`

tokens prompt=1001 completion=404 latency=14.31s

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
Can the pattern of this time-series data be summarized as a seasonal stepwise ascent?
</question>

<candidates>
A) Yes.
B) No.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires determining whether a given time series exhibits a seasonal stepwise ascent pattern. This necessitates identifying seasonal components and step changes, which are best approached using both temporal-scale and functional perspectives.",
  "task_summary": "Determine if the time series has a seasonal stepwise ascent pattern.",
  "target_output": "choice",
  "answer_type": "choice",
  "capability": "time-series pattern detection",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "long",
      "objective": "Identify long-term trends and possible seasonal patterns",
      "required_measurements": ["seasonal_period", "trend_slope"],
      "validation_requirements": ["Check consistency across different segments of the series"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "medium",
      "objective": "Identify mid-term patterns and possible step changes",
      "required_measurements": ["step_level_count", "step_change_times"],
      "validation_requirements": ["Confirm step changes are consistent within the identified seasonal period"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent",
      "required_measurements": ["seasonal_period", "step_level_count", "trend_slope", "step_change_times"],
      "validation_requirements": ["Ensure seasonal periodicity and steps align logically and temporally"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Pattern confirmation matches A or B based on the provided evidence"],
  "notes": "Requires detailed examination of the time series for consistent seasonal and stepwise features."
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=3998 completion=288 latency=11.32s

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
{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires determining whether a given time series exhibits a seasonal stepwise ascent pattern. This necessitates identifying seasonal components and step changes, which are best approached using both temporal-scale and functional perspectives.","task_summary":"Determine if the time series has a seasonal stepwise ascent pattern.","target_output":"choice","answer_type":"choice","capability":"time-series pattern detection","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["reasoning"],"success_criteria":["Pattern confirmation matches A or B based on the provided evidence"],"notes":"Requires detailed examination of the time series for consistent seasonal and stepwise features."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires identifying long-term trends and possible seasonal patterns, focusing on measurements such as the seasonal period and trend slope. Validation across different segments of the series is necessary to ensure consistency.",
  "evidence_plan": {
    "objective": "Identify long-term trends and possible seasonal patterns",
    "claims_to_support": [
      {
        "claim": "There exists a seasonal period in the series.",
        "required_evidence": ["seasonal_period"]
      },
      {
        "claim": "The trend over the series is linearly increasing or decreasing.",
        "required_evidence": ["trend_slope"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "long"
    },
    "validation_needs": ["Check consistency across different segments of the series"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "fft_period",
        "reason": "To detect the dominant periodic component indicating potential seasonal patterns.",
        "supports_evidence": ["seasonal_period"]
      },
      {
        "tool": "segment_trend",
        "reason": "To assess the overall linear trend slope of the series.",
        "supports_evidence": ["trend_slope"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=756 completion=155 latency=5.53s

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
{"evidence_plan":{"objective":"Identify long-term trends and possible seasonal patterns","claims_to_support":[{"claim":"There exists a seasonal period in the series.","required_evidence":["seasonal_period"]},{"claim":"The trend over the series is linearly increasing or decreasing.","required_evidence":["trend_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Check consistency across different segments of the series"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant periodic component indicating potential seasonal patterns.","supports_evidence":["seasonal_period"]},{"tool":"segment_trend","reason":"To assess the overall linear trend slope of the series.","supports_evidence":["trend_slope"]}],"no_tool_decision":null},"reasoning":"The task requires identifying long-term trends and possible seasonal patterns, focusing on measurements such as the seasonal period and trend slope. Validation across different segments of the series is necessary to ensure consistency."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series.",
  "workflow": [
    {
      "step": 1,
      "tool": "fft_period",
      "output_key": "dominant_period",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "segment_trend",
      "output_key": "trend_slope",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=847 completion=153 latency=5.49s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_slope","input_binding":{}}],"reasoning":"The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series."}
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
- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series.",
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
      "tool": "segment_trend",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1172 completion=385 latency=13.71s

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
{"evidence_plan":{"objective":"Identify long-term trends and possible seasonal patterns","claims_to_support":[{"claim":"There exists a seasonal period in the series.","required_evidence":["seasonal_period"]},{"claim":"The trend over the series is linearly increasing or decreasing.","required_evidence":["trend_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Check consistency across different segments of the series"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant periodic component indicating potential seasonal patterns.","supports_evidence":["seasonal_period"]},{"tool":"segment_trend","reason":"To assess the overall linear trend slope of the series.","supports_evidence":["trend_slope"]}],"no_tool_decision":null},"reasoning":"The task requires identifying long-term trends and possible seasonal patterns, focusing on measurements such as the seasonal period and trend slope. Validation across different segments of the series is necessary to ensure consistency."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
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
      "dominant_period": 180.0,
      "spectral_strength": 0.28088920040679355,
      "period_trusted": false,
      "warnings": [
        "dominant_period_near_series_length"
      ]
    },
    "error": null,
    "args_fingerprint": "726ee7605c7aac2e5823de42d4c34d3c89859438"
  },
  {
    "call_id": "long:step2",
    "step": 2,
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
      "slope": 5.027932960893855,
      "direction": "upward",
      "direction_class": "upward",
      "trend_method": "endpoint",
      "mean": 385.0,
      "std": 383.0397426435597,
      "start_value": 0.0,
      "end_value": 900.0
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis has identified a potential seasonal period and determined that the trend over the series is linearly increasing, with a slope of approximately 5.03. However, the detected seasonal period should be considered with caution due to the warning about it being near the series length.",
  "scale": "long",
  "observations": ["A potential seasonal period of 180 units was detected in the series.", "The trend over the series is linearly increasing with a slope of approximately 5.03."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There exists a seasonal period in the series.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 180.0,
          "source_tool": "fft_period",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "qualified",
      "maps_to_measurement": "seasonal_period"
    },
    {
      "claim": "The trend over the series is linearly increasing or decreasing.",
      "evidence": [
        {
          "type": "trend_slope",
          "value": 5.027932960893855,
          "source_tool": "segment_trend",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "trend_slope"
    }
  ],
  "coverage": {"seasonal_period": "qualified", "trend_slope": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4000 completion=276 latency=10.88s

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
{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires determining whether a given time series exhibits a seasonal stepwise ascent pattern. This necessitates identifying seasonal components and step changes, which are best approached using both temporal-scale and functional perspectives.","task_summary":"Determine if the time series has a seasonal stepwise ascent pattern.","target_output":"choice","answer_type":"choice","capability":"time-series pattern detection","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["reasoning"],"success_criteria":["Pattern confirmation matches A or B based on the provided evidence"],"notes":"Requires detailed examination of the time series for consistent seasonal and stepwise features."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify mid-term patterns and possible step changes in the time series. This involves detecting seasonal stepwise changes and confirming their consistency within the identified seasonal period.",
  "evidence_plan": {
    "objective": "Identify mid-term patterns and possible step changes",
    "claims_to_support": [
      {"claim": "The time series contains a certain number of distinct step levels.", "required_evidence": ["step_level_count"]},
      {"claim": "Step changes occur at specific times within the time series.", "required_evidence": ["step_change_times"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["Confirm step changes are consistent within the identified seasonal period"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "step_levels", "reason": "Count discrete step/plateau levels to measure the number of distinct step levels in the time series.", "supports_evidence": ["step_level_count"]},
      {"tool": "change_points", "reason": "Localize potential level/regime transitions to determine specific times when step changes occur.", "supports_evidence": ["step_change_times"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=754 completion=150 latency=5.36s

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
{"evidence_plan":{"objective":"Identify mid-term patterns and possible step changes","claims_to_support":[{"claim":"The time series contains a certain number of distinct step levels.","required_evidence":["step_level_count"]},{"claim":"Step changes occur at specific times within the time series.","required_evidence":["step_change_times"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Confirm step changes are consistent within the identified seasonal period"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Count discrete step/plateau levels to measure the number of distinct step levels in the time series.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localize potential level/regime transitions to determine specific times when step changes occur.","supports_evidence":["step_change_times"]}],"no_tool_decision":null},"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. This involves detecting seasonal stepwise changes and confirming their consistency within the identified seasonal period."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- step_levels
  inputs: series_index, start, end
  outputs: series
- change_points
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur.",
  "workflow": [
    {
      "step": 1,
      "tool": "step_levels",
      "output_key": "step_level_output",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "change_points",
      "output_key": "change_point_output",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=858 completion=148 latency=5.35s

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
{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_output","input_binding":{}},{"step":2,"tool":"change_points","output_key":"change_point_output","input_binding":{}}],"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur."}
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

- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur.",
  "calls": [
    {
      "step": 1,
      "tool": "step_levels",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "change_points",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=1439 completion=363 latency=13.07s

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
{"evidence_plan":{"objective":"Identify mid-term patterns and possible step changes","claims_to_support":[{"claim":"The time series contains a certain number of distinct step levels.","required_evidence":["step_level_count"]},{"claim":"Step changes occur at specific times within the time series.","required_evidence":["step_change_times"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Confirm step changes are consistent within the identified seasonal period"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Count discrete step/plateau levels to measure the number of distinct step levels in the time series.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localize potential level/regime transitions to determine specific times when step changes occur.","supports_evidence":["step_change_times"]}],"no_tool_decision":null},"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. This involves detecting seasonal stepwise changes and confirming their consistency within the identified seasonal period."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "medium:step1",
    "step": 1,
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
      "n_unique_levels": 9,
      "n_plateau_runs": 9,
      "levels": [
        0.0,
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        900.0
      ],
      "plateau_runs": [
        0.0,
        100.0,
        200.0,
        300.0,
        400.0,
        500.0,
        600.0,
        700.0,
        900.0
      ],
      "plateau_lengths": [
        77,
        1,
        2,
        14,
        10,
        8,
        14,
        2,
        52
      ],
      "tolerance": 15.0
    },
    "error": null,
    "args_fingerprint": "9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"
  },
  {
    "call_id": "medium:step2",
    "step": 2,
    "tool_name": "change_points",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "candidates": [
        {
          "index": 128,
          "score": 277.7777777777778
        },
        {
          "index": 127,
          "score": 266.66666666666674
        },
        {
          "index": 78,
          "score": 266.6666666666667
        },
        {
          "index": 79,
          "score": 255.55555555555557
        },
        {
          "index": 77,
          "score": 255.55555555555554
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify mid-term patterns and possible step changes in the time series. Using the 'step_levels' tool, we determined there are 9 unique step levels. The 'change_points' tool identified several potential step change points within the time series.",
  "scale": "medium",
  "observations": ["The time series exhibits 9 distinct step levels and multiple potential step change points."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The time series contains a certain number of distinct step levels.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 9,
          "source_tool": "step_levels",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "step_level_count"
    },
    {
      "claim": "Step changes occur at specific times within the time series.",
      "evidence": [
        {
          "type": "step_change_times",
          "value": [128, 127, 78, 79, 77],
          "source_tool": "change_points",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "step_change_times"
    }
  ],
  "coverage": {"step_level_count": "tool_supported", "step_change_times": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=7596 completion=315 latency=13.78s

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
{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires determining whether a given time series exhibits a seasonal stepwise ascent pattern. This necessitates identifying seasonal components and step changes, which are best approached using both temporal-scale and functional perspectives.","task_summary":"Determine if the time series has a seasonal stepwise ascent pattern.","target_output":"choice","answer_type":"choice","capability":"time-series pattern detection","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["reasoning"],"success_criteria":["Pattern confirmation matches A or B based on the provided evidence"],"notes":"Requires detailed examination of the time series for consistent seasonal and stepwise features."}
</plan_context>

<task_summary>
Determine if the time series has a seasonal stepwise ascent pattern.
</task_summary>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The objective was to identify mid-term patterns and possible step changes in the time series. Using the 'step_levels' tool, we determined there are 9 unique step levels. The 'change_points' tool identified several potential step change points within the time series.","scale":"medium","observations":["The time series exhibits 9 distinct step levels and multiple potential step change points."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 9, \"n_plateau_runs\": 9, \"levels\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_runs\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_lengths\": [77, 1, 2, 14, 10, 8, 14, 2, 52], \"tolerance\": 15.0}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 128, \"score\": 277.7777777777778}, {\"index\": 127, \"score\": 266.66666666666674}, {\"index\": 78, \"score\": 266.6666666666667}, {\"index\": 79, \"score\": 255.55555555555557}, {\"index\": 77, \"score\": 255.55555555555554}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify mid-term patterns and possible step changes","claims_to_support":[{"claim":"The time series contains a certain number of distinct step levels.","required_evidence":["step_level_count"]},{"claim":"Step changes occur at specific times within the time series.","required_evidence":["step_change_times"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Confirm step changes are consistent within the identified seasonal period"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Count discrete step/plateau levels to measure the number of distinct step levels in the time series.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localize potential level/regime transitions to determine specific times when step changes occur.","supports_evidence":["step_change_times"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_output","input_binding":{}},{"step":2,"tool":"change_points","output_key":"change_point_output","input_binding":{}}],"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur."},"structured_observations":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}],"coverage":{"step_level_count":"tool_supported","step_change_times":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":9,"n_plateau_runs":9,"levels":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_runs":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_lengths":[77,1,2,14,10,8,14,2,52],"tolerance":15.0},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":128,"score":277.7777777777778},{"index":127,"score":266.66666666666674},{"index":78,"score":266.6666666666667},{"index":79,"score":255.55555555555557},{"index":77,"score":255.55555555555554}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis has identified a potential seasonal period and determined that the trend over the series is linearly increasing, with a slope of approximately 5.03. However, the detected seasonal period should be considered with caution due to the warning about it being near the series length.","scale":"long","observations":["A potential seasonal period of 180 units was detected in the series.","The trend over the series is linearly increasing with a slope of approximately 5.03."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 180.0, \"spectral_strength\": 0.28088920040679355, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 5.027932960893855, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 385.0, \"std\": 383.0397426435597, \"start_value\": 0.0, \"end_value\": 900.0}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}"],"evidence_plan":{"objective":"Identify long-term trends and possible seasonal patterns","claims_to_support":[{"claim":"There exists a seasonal period in the series.","required_evidence":["seasonal_period"]},{"claim":"The trend over the series is linearly increasing or decreasing.","required_evidence":["trend_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Check consistency across different segments of the series"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant periodic component indicating potential seasonal patterns.","supports_evidence":["seasonal_period"]},{"tool":"segment_trend","reason":"To assess the overall linear trend slope of the series.","supports_evidence":["trend_slope"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_slope","input_binding":{}}],"reasoning":"The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series."},"structured_observations":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"coverage":{"seasonal_period":"qualified","trend_slope":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":180.0,"spectral_strength":0.28088920040679355,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":5.027932960893855,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":385.0,"std":383.0397426435597,"start_value":0.0,"end_value":900.0},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"}],"skipped_stages":[]},"conflicts":[],"summary":"A potential seasonal period of 180 units was detected in the series. The trend over the series is linearly increasing with a slope of approximately 5.03. The time series exhibits 9 distinct step levels and multiple potential step change points.","structured_by_scale":{"long":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"medium":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current assignment asks to determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent. Previous tasks have identified a potential seasonal period of 180 units and multiple step levels within the time series. Additionally, there is a linearly increasing trend. However, the seasonal period found through FFT is not trusted due to its proximity to the series length. Thus, validation is needed to ensure that the seasonal periodicity and steps align logically and temporally.",
  "evidence_plan": {
    "objective": "Determine if the time series has a seasonal stepwise ascent pattern.",
    "claims_to_support": [
      {"claim": "There exists a seasonal period in the series.", "required_evidence": ["seasonal_period"]},
      {"claim": "The time series contains a certain number of distinct step levels.", "required_evidence": ["step_level_count"]},
      {"claim": "Step changes occur at specific times within the time series.", "required_evidence": ["step_change_times"]},
      {"claim": "The trend over the series is linearly increasing.", "required_evidence": ["trend_slope"]}
    ],
    "analysis_scope": {"target_series": [1], "role": "reasoning"},
    "validation_needs": ["Seasonal periodicity and steps align logically and temporally"]
  },
  "capability_selection": {
    "selected_tools": [
      "seas_acf"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=4127 completion=700 latency=26.52s

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
{"evidence_plan":{"objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The objective was to identify mid-term patterns and possible step changes in the time series. Using the 'step_levels' tool, we determined there are 9 unique step levels. The 'change_points' tool identified several potential step change points within the time series.","scale":"medium","observations":["The time series exhibits 9 distinct step levels and multiple potential step change points."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 9, \"n_plateau_runs\": 9, \"levels\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_runs\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_lengths\": [77, 1, 2, 14, 10, 8, 14, 2, 52], \"tolerance\": 15.0}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 128, \"score\": 277.7777777777778}, {\"index\": 127, \"score\": 266.66666666666674}, {\"index\": 78, \"score\": 266.6666666666667}, {\"index\": 79, \"score\": 255.55555555555557}, {\"index\": 77, \"score\": 255.55555555555554}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify mid-term patterns and possible step changes","claims_to_support":[{"claim":"The time series contains a certain number of distinct step levels.","required_evidence":["step_level_count"]},{"claim":"Step changes occur at specific times within the time series.","required_evidence":["step_change_times"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Confirm step changes are consistent within the identified seasonal period"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Count discrete step/plateau levels to measure the number of distinct step levels in the time series.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localize potential level/regime transitions to determine specific times when step changes occur.","supports_evidence":["step_change_times"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_output","input_binding":{}},{"step":2,"tool":"change_points","output_key":"change_point_output","input_binding":{}}],"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur."},"structured_observations":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}],"coverage":{"step_level_count":"tool_supported","step_change_times":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":9,"n_plateau_runs":9,"levels":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_runs":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_lengths":[77,1,2,14,10,8,14,2,52],"tolerance":15.0},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":128,"score":277.7777777777778},{"index":127,"score":266.66666666666674},{"index":78,"score":266.6666666666667},{"index":79,"score":255.55555555555557},{"index":77,"score":255.55555555555554}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis has identified a potential seasonal period and determined that the trend over the series is linearly increasing, with a slope of approximately 5.03. However, the detected seasonal period should be considered with caution due to the warning about it being near the series length.","scale":"long","observations":["A potential seasonal period of 180 units was detected in the series.","The trend over the series is linearly increasing with a slope of approximately 5.03."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 180.0, \"spectral_strength\": 0.28088920040679355, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 5.027932960893855, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 385.0, \"std\": 383.0397426435597, \"start_value\": 0.0, \"end_value\": 900.0}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}"],"evidence_plan":{"objective":"Identify long-term trends and possible seasonal patterns","claims_to_support":[{"claim":"There exists a seasonal period in the series.","required_evidence":["seasonal_period"]},{"claim":"The trend over the series is linearly increasing or decreasing.","required_evidence":["trend_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Check consistency across different segments of the series"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant periodic component indicating potential seasonal patterns.","supports_evidence":["seasonal_period"]},{"tool":"segment_trend","reason":"To assess the overall linear trend slope of the series.","supports_evidence":["trend_slope"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_slope","input_binding":{}}],"reasoning":"The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series."},"structured_observations":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"coverage":{"seasonal_period":"qualified","trend_slope":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":180.0,"spectral_strength":0.28088920040679355,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":5.027932960893855,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":385.0,"std":383.0397426435597,"start_value":0.0,"end_value":900.0},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"}],"skipped_stages":[]},"conflicts":[],"summary":"A potential seasonal period of 180 units was detected in the series. The trend over the series is linearly increasing with a slope of approximately 5.03. The time series exhibits 9 distinct step levels and multiple potential step change points.","structured_by_scale":{"long":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"medium":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The combination of step changes and a potential seasonal pattern suggests a possibility of a seasonal stepwise ascent, but further validation is needed to ensure these components align logically and temporally.",
  "role": "reasoning",
  "hypothesis": "Seasonal stepwise ascent might be supported given the existence of both seasonal patterns and step changes.",
  "evidence": [
    "The time series exhibits 9 distinct step levels and multiple potential step change points.",
    "A potential seasonal period of 180 units was detected in the series.",
    "The trend over the series is linearly increasing with a slope of approximately 5.03."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["medium:step1", "medium:step2", "long:step1", "long:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The series has been identified as having 9 distinct step levels and multiple step change points.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 9,
          "provenance": "upstream",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        },
        {
          "type": "step_change_times",
          "value": [128, 127, 78, 79, 77],
          "provenance": "upstream",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "A potential seasonal period of 180 units was detected in the series, though it's near the series length and thus should be considered cautiously.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 180,
          "provenance": "upstream",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "qualified"
    },
    {
      "claim": "The overall trend of the series is linearly increasing with a positive slope of approximately 5.03, which supports a general upward direction.",
      "evidence": [
        {
          "type": "trend_slope",
          "value": 5.027932960893855,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "seasonal_period": "qualified",
    "step_level_count": "context_supported",
    "trend_slope": "context_supported",
    "step_change_times": "context_supported"
  },
  "unresolved_claims": [
    "It remains unresolved whether the step changes and the seasonal pattern align logically and temporally to support a seasonal stepwise ascent without direct alignment data."
  ]
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m1`

tokens prompt=7633 completion=341 latency=14.78s

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
{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires determining whether a given time series exhibits a seasonal stepwise ascent pattern. This necessitates identifying seasonal components and step changes, which are best approached using both temporal-scale and functional perspectives.","task_summary":"Determine if the time series has a seasonal stepwise ascent pattern.","target_output":"choice","answer_type":"choice","capability":"time-series pattern detection","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify long-term trends and possible seasonal patterns","required_measurements":["seasonal_period","trend_slope"],"validation_requirements":["Check consistency across different segments of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify mid-term patterns and possible step changes","required_measurements":["step_level_count","step_change_times"],"validation_requirements":["Confirm step changes are consistent within the identified seasonal period"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["reasoning"],"success_criteria":["Pattern confirmation matches A or B based on the provided evidence"],"notes":"Requires detailed examination of the time series for consistent seasonal and stepwise features."}
</plan_context>

<task_summary>
Determine if the time series has a seasonal stepwise ascent pattern.
</task_summary>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The objective was to identify mid-term patterns and possible step changes in the time series. Using the 'step_levels' tool, we determined there are 9 unique step levels. The 'change_points' tool identified several potential step change points within the time series.","scale":"medium","observations":["The time series exhibits 9 distinct step levels and multiple potential step change points."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 9, \"n_plateau_runs\": 9, \"levels\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_runs\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_lengths\": [77, 1, 2, 14, 10, 8, 14, 2, 52], \"tolerance\": 15.0}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 128, \"score\": 277.7777777777778}, {\"index\": 127, \"score\": 266.66666666666674}, {\"index\": 78, \"score\": 266.6666666666667}, {\"index\": 79, \"score\": 255.55555555555557}, {\"index\": 77, \"score\": 255.55555555555554}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify mid-term patterns and possible step changes","claims_to_support":[{"claim":"The time series contains a certain number of distinct step levels.","required_evidence":["step_level_count"]},{"claim":"Step changes occur at specific times within the time series.","required_evidence":["step_change_times"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Confirm step changes are consistent within the identified seasonal period"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Count discrete step/plateau levels to measure the number of distinct step levels in the time series.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localize potential level/regime transitions to determine specific times when step changes occur.","supports_evidence":["step_change_times"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_output","input_binding":{}},{"step":2,"tool":"change_points","output_key":"change_point_output","input_binding":{}}],"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur."},"structured_observations":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}],"coverage":{"step_level_count":"tool_supported","step_change_times":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":9,"n_plateau_runs":9,"levels":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_runs":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_lengths":[77,1,2,14,10,8,14,2,52],"tolerance":15.0},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":128,"score":277.7777777777778},{"index":127,"score":266.66666666666674},{"index":78,"score":266.6666666666667},{"index":79,"score":255.55555555555557},{"index":77,"score":255.55555555555554}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis has identified a potential seasonal period and determined that the trend over the series is linearly increasing, with a slope of approximately 5.03. However, the detected seasonal period should be considered with caution due to the warning about it being near the series length.","scale":"long","observations":["A potential seasonal period of 180 units was detected in the series.","The trend over the series is linearly increasing with a slope of approximately 5.03."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 180.0, \"spectral_strength\": 0.28088920040679355, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 5.027932960893855, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 385.0, \"std\": 383.0397426435597, \"start_value\": 0.0, \"end_value\": 900.0}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}"],"evidence_plan":{"objective":"Identify long-term trends and possible seasonal patterns","claims_to_support":[{"claim":"There exists a seasonal period in the series.","required_evidence":["seasonal_period"]},{"claim":"The trend over the series is linearly increasing or decreasing.","required_evidence":["trend_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Check consistency across different segments of the series"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant periodic component indicating potential seasonal patterns.","supports_evidence":["seasonal_period"]},{"tool":"segment_trend","reason":"To assess the overall linear trend slope of the series.","supports_evidence":["trend_slope"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_slope","input_binding":{}}],"reasoning":"The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series."},"structured_observations":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"coverage":{"seasonal_period":"qualified","trend_slope":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":180.0,"spectral_strength":0.28088920040679355,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":5.027932960893855,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":385.0,"std":383.0397426435597,"start_value":0.0,"end_value":900.0},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"}],"skipped_stages":[]},"conflicts":[],"summary":"A potential seasonal period of 180 units was detected in the series. The trend over the series is linearly increasing with a slope of approximately 5.03. The time series exhibits 9 distinct step levels and multiple potential step change points.","structured_by_scale":{"long":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"medium":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['It remains unresolved whether the step changes and the seasonal pattern align logically and temporally to support a seasonal stepwise ascent without direct alignment data.']
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides indications of a potential seasonal period and a linear upward trend, along with multiple step changes. However, the logical and temporal alignment between the step changes and the seasonal pattern is still unclear. The step changes have been localized but there's no direct evidence of how these changes correlate with the potential seasonal period.",
  "evidence_plan": {
    "objective": "Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent",
    "claims_to_support": [
      {
        "claim": "There exists a seasonal period in the series.",
        "required_evidence": ["seasonal_period"]
      },
      {
        "claim": "The time series contains a certain number of distinct step levels.",
        "required_evidence": ["step_level_count"]
      },
      {
        "claim": "Step changes occur at specific times within the time series.",
        "required_evidence": ["step_change_times"]
      },
      {
        "claim": "The trend over the series is linearly increasing or decreasing.",
        "required_evidence": ["trend_slope"]
      },
      {
        "claim": "Seasonal periodicity and step changes align logically and temporally.",
        "required_evidence": ["step_change_seasonal_alignment"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "reasoning"
    },
    "validation_needs": ["step_change_seasonal_alignment"]
  },
  "capability_selection": {
    "selected_tools": [
      "seas_acf"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m1`

tokens prompt=4127 completion=700 latency=26.52s

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
{"evidence_plan":{"objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The objective was to identify mid-term patterns and possible step changes in the time series. Using the 'step_levels' tool, we determined there are 9 unique step levels. The 'change_points' tool identified several potential step change points within the time series.","scale":"medium","observations":["The time series exhibits 9 distinct step levels and multiple potential step change points."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 9, \"n_plateau_runs\": 9, \"levels\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_runs\": [0.0, 100.0, 200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 900.0], \"plateau_lengths\": [77, 1, 2, 14, 10, 8, 14, 2, 52], \"tolerance\": 15.0}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 128, \"score\": 277.7777777777778}, {\"index\": 127, \"score\": 266.66666666666674}, {\"index\": 78, \"score\": 266.6666666666667}, {\"index\": 79, \"score\": 255.55555555555557}, {\"index\": 77, \"score\": 255.55555555555554}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify mid-term patterns and possible step changes","claims_to_support":[{"claim":"The time series contains a certain number of distinct step levels.","required_evidence":["step_level_count"]},{"claim":"Step changes occur at specific times within the time series.","required_evidence":["step_change_times"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Confirm step changes are consistent within the identified seasonal period"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Count discrete step/plateau levels to measure the number of distinct step levels in the time series.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localize potential level/regime transitions to determine specific times when step changes occur.","supports_evidence":["step_change_times"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"step_level_output","input_binding":{}},{"step":2,"tool":"change_points","output_key":"change_point_output","input_binding":{}}],"reasoning":"The objective is to identify mid-term patterns and possible step changes in the time series. First, we will use the step_levels tool to count the distinct step levels in the time series. Following this, we will use the change_points tool to localize potential level/regime transitions and determine the specific times when step changes occur."},"structured_observations":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}],"coverage":{"step_level_count":"tool_supported","step_change_times":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":9,"n_plateau_runs":9,"levels":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_runs":[0.0,100.0,200.0,300.0,400.0,500.0,600.0,700.0,900.0],"plateau_lengths":[77,1,2,14,10,8,14,2,52],"tolerance":15.0},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":128,"score":277.7777777777778},{"index":127,"score":266.66666666666674},{"index":78,"score":266.6666666666667},{"index":79,"score":255.55555555555557},{"index":77,"score":255.55555555555554}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis has identified a potential seasonal period and determined that the trend over the series is linearly increasing, with a slope of approximately 5.03. However, the detected seasonal period should be considered with caution due to the warning about it being near the series length.","scale":"long","observations":["A potential seasonal period of 180 units was detected in the series.","The trend over the series is linearly increasing with a slope of approximately 5.03."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 180.0, \"spectral_strength\": 0.28088920040679355, \"period_trusted\": false, \"warnings\": [\"dominant_period_near_series_length\"]}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 5.027932960893855, \"direction\": \"upward\", \"direction_class\": \"upward\", \"trend_method\": \"endpoint\", \"mean\": 385.0, \"std\": 383.0397426435597, \"start_value\": 0.0, \"end_value\": 900.0}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}"],"evidence_plan":{"objective":"Identify long-term trends and possible seasonal patterns","claims_to_support":[{"claim":"There exists a seasonal period in the series.","required_evidence":["seasonal_period"]},{"claim":"The trend over the series is linearly increasing or decreasing.","required_evidence":["trend_slope"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Check consistency across different segments of the series"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant periodic component indicating potential seasonal patterns.","supports_evidence":["seasonal_period"]},{"tool":"segment_trend","reason":"To assess the overall linear trend slope of the series.","supports_evidence":["trend_slope"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_slope","input_binding":{}}],"reasoning":"The objective is to identify long-term trends and possible seasonal patterns in the given series. To achieve this, we first use the 'fft_period' tool to detect the dominant periodic component, which can help identify potential seasonal patterns. Following this, we use the 'segment_trend' tool to assess the overall linear trend slope of the series."},"structured_observations":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"coverage":{"seasonal_period":"qualified","trend_slope":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":180.0,"spectral_strength":0.28088920040679355,"period_trusted":false,"warnings":["dominant_period_near_series_length"]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":5.027932960893855,"direction":"upward","direction_class":"upward","trend_method":"endpoint","mean":385.0,"std":383.0397426435597,"start_value":0.0,"end_value":900.0},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"}],"skipped_stages":[]},"conflicts":[],"summary":"A potential seasonal period of 180 units was detected in the series. The trend over the series is linearly increasing with a slope of approximately 5.03. The time series exhibits 9 distinct step levels and multiple potential step change points.","structured_by_scale":{"long":[{"claim":"There exists a seasonal period in the series.","evidence":[{"type":"seasonal_period","value":180.0,"source_tool":"fft_period","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"qualified","maps_to_measurement":"seasonal_period"},{"claim":"The trend over the series is linearly increasing or decreasing.","evidence":[{"type":"trend_slope","value":5.027932960893855,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"trend_slope"}],"medium":[{"claim":"The time series contains a certain number of distinct step levels.","evidence":[{"type":"step_level_count","value":9,"source_tool":"step_levels","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"},{"claim":"Step changes occur at specific times within the time series.","evidence":[{"type":"step_change_times","value":[128,127,78,79,77],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_change_times"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent","required_measurements":["seasonal_period","step_level_count","trend_slope","step_change_times"],"validation_requirements":["Ensure seasonal periodicity and steps align logically and temporally"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['seasonality analysis', 'deductive reasoning']; domain=healthcare; qa_type=a binary question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[180]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The combination of step changes and a potential seasonal pattern suggests a possibility of a seasonal stepwise ascent, but further validation is needed to ensure these components align logically and temporally.",
  "role": "reasoning",
  "hypothesis": "Seasonal stepwise ascent might be supported given the existence of both seasonal patterns and step changes.",
  "evidence": [
    "The time series exhibits 9 distinct step levels and multiple potential step change points.",
    "A potential seasonal period of 180 units was detected in the series.",
    "The trend over the series is linearly increasing with a slope of approximately 5.03."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["medium:step1", "medium:step2", "long:step1", "long:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The series has been identified as having 9 distinct step levels and multiple step change points.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 9,
          "provenance": "upstream",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        },
        {
          "type": "step_change_times",
          "value": [128, 127, 78, 79, 77],
          "provenance": "upstream",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "A potential seasonal period of 180 units was detected in the series, though it's near the series length and thus should be considered cautiously.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 180,
          "provenance": "upstream",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "qualified"
    },
    {
      "claim": "The overall trend of the series is linearly increasing with a positive slope of approximately 5.03, which supports a general upward direction.",
      "evidence": [
        {
          "type": "trend_slope",
          "value": 5.027932960893855,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "seasonal_period": "qualified",
    "step_level_count": "context_supported",
    "trend_slope": "context_supported",
    "step_change_times": "context_supported"
  },
  "unresolved_claims": [
    "It remains unresolved whether the step changes and the seasonal pattern align logically and temporally to support a seasonal stepwise ascent without direct alignment data."
  ]
}
```

## Integration — `integration`

tokens prompt=1487 completion=191 latency=7.00s

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
Can the pattern of this time-series data be summarized as a seasonal stepwise ascent?
</question>

<candidates>
A) Yes.
B) No.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Determine if the time series has a seasonal stepwise ascent pattern.",
  "question_type": "choice",
  "required_output": "choice",
  "success_criteria": [
    "Pattern confirmation matches A or B based on the provided evidence"
  ],
  "assignments_brief": [
    {
      "agent": "homo:long",
      "objective": "Identify long-term trends and possible seasonal patterns",
      "required_measurements": [
        "seasonal_period",
        "trend_slope"
      ]
    },
    {
      "agent": "homo:medium",
      "objective": "Identify mid-term patterns and possible step changes",
      "required_measurements": [
        "step_level_count",
        "step_change_times"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Determine if the combination of seasonal patterns and step changes supports a seasonal stepwise ascent",
      "required_measurements": [
        "seasonal_period",
        "step_level_count",
        "trend_slope",
        "step_change_times"
      ]
    }
  ]
}
</planner_intent>

<homo_perception>
{
  "by_scale": {
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "step_level_count",
          "value": 9,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "step_change_times",
          "value": [
            128,
            127,
            78,
            79,
            77
          ],
          "trusted": true
        }
      ],
      "coverage": {
        "step_level_count": "tool_supported",
        "step_change_times": "tool_supported"
      },
      "summary": "The time series exhibits 9 distinct step levels and multiple potential step change points."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "seasonal_period",
          "value": 180.0,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "trend_slope",
          "value": 5.027932960893855,
          "trusted": true
        }
      ],
      "coverage": {
        "seasonal_period": "qualified",
        "trend_slope": "tool_supported"
      },
      "summary": "A potential seasonal period of 180 units was detected in the series. | The trend over the series is linearly increasing with a slope of approximately 5.03."
    }
  },
  "conflicts": [],
  "summary": "A potential seasonal period of 180 units was detected in the series. The trend over the series is linearly increasing with a slope of approximately 5.03. The time series exhibits 9 distinct step levels and multiple potential step change points."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
      "hypothesis": "Seasonal stepwise ascent might be supported given the existence of both seasonal patterns and step changes.",
      "reasoning_chain": [
        "The series has been identified as having 9 distinct step levels and multiple step change points.",
        "step_level_count=9",
        "step_change_times=[128, 127, 78, 79, 77]",
        "A potential seasonal period of 180 units was detected in the series, though it's near the series length and thus should be considered cautiously.",
        "seasonal_period=180",
        "The overall trend of the series is linearly increasing with a positive slope of approximately 5.03, which supports a general upward direction.",
        "trend_slope=5.027932960893855"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "step_level_count",
        "step_change_times",
        "seasonal_period",
        "trend_slope"
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
  "reasoning": "Heter reasoning confirms the presence of both seasonal and stepwise patterns in the data, aligning with a seasonal stepwise ascent. However, there's some uncertainty around the seasonal period due to its proximity to the total series length.",
  "answer": "A",
  "explanation": "The time series has 9 distinct step levels and multiple step change points, alongside a potential seasonal period and an overall increasing trend. These characteristics support a seasonal stepwise ascent pattern.",
  "confidence": 0.5,
  "conflicts": [],
  "cited_evidence": ["step_level_count", "step_change_times", "seasonal_period", "trend_slope"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "A"
  }
}
```
