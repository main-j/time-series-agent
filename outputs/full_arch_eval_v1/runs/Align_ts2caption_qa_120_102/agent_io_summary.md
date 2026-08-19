# Agent IO summary: `Align:ts2caption_qa_120:102`

- Architecture pred: `B` (success=True)
- model_calls=14, tool_calls=4, latency=190.4s

## Planner — `planner`

tokens prompt=1140 completion=476 latency=16.92s

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
Given the provided time series numerical or graphical data, select the description from the four options that best corresponds to the data.
</question>

<candidates>
A) The data shows regular oscillatory behavior with consistent amplitude variations, featuring recurring peaks around 20-30 and baseline values near 1-2 throughout the sequence.
B) This time series exhibits cyclical patterns with periodic spikes reaching peaks around 15-20, followed by gradual declines to near-zero values before repeating the cycle.
C) This series demonstrates relatively stable fluctuations around 2-3 with occasional upward excursions, showing gradual trending behavior and moderate variability across the observation period.
D) The data maintains high baseline values around 87-94 with occasional step-like transitions and brief periods of lower values, exhibiting overall stability with discrete level changes.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires selecting the most accurate description for the given univariate time series data among four candidate statements, each capturing different features such as oscillatory behavior, cyclical patterns, steady-state levels with step changes, and stable fluctuations.",
  "task_summary": "Choose the correct descriptive statement for the provided time series data among multiple options.",
  "target_output": "The description that best fits the provided time series data.",
  "answer_type": "choice",
  "capability": "Hierarchical time-series analysis",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "medium",
      "objective": "Identify any cyclic or oscillatory trends within the data over intermediate intervals.",
      "required_measurements": ["seasonal_period", "seasonal_strength"],
      "validation_requirements": ["Reconcile findings with overall structural consistency"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "long",
      "objective": "Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.",
      "required_measurements": ["global_trend", "step_level_count"],
      "validation_requirements": ["Confirm trends and step changes are consistent across the entire time span"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.",
      "required_measurements": ["seasonal_period", "seasonal_strength", "global_trend", "step_level_count"],
      "validation_requirements": ["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": [
    "The selected description accurately reflects the observed features of the time series.",
    "The chosen description does not contradict the evidence gathered about the time series structure."
  ],
  "notes": "Ensure all observations are integrated to make a well-informed decision on the description that matches the time series."
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4066 completion=250 latency=9.99s

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
{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements, each capturing different features such as oscillatory behavior, cyclical patterns, steady-state levels with step changes, and stable fluctuations.","task_summary":"Choose the correct descriptive statement for the provided time series data among multiple options.","target_output":"The description that best fits the provided time series data.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}],"scales":["medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["The selected description accurately reflects the observed features of the time series.","The chosen description does not contradict the evidence gathered about the time series structure."],"notes":"Ensure all observations are integrated to make a well-informed decision on the description that matches the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify cyclic or oscillatory trends within the data over intermediate intervals and measure seasonal period and strength. Validation requires reconciliation with overall structural consistency.",
  "evidence_plan": {
    "objective": "Identify any cyclic or oscillatory trends within the data over intermediate intervals.",
    "claims_to_support": [
      {"claim": "There exists a cyclic or oscillatory trend.", "required_evidence": ["seasonal_period", "seasonal_strength"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["Reconcile findings with overall structural consistency"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.", "supports_evidence": ["seasonal_period"]},
      {"tool": "stl_strength", "reason": "To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.", "supports_evidence": ["seasonal_strength"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=775 completion=146 latency=5.27s

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
{"evidence_plan":{"objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend.","required_evidence":["seasonal_period","seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Reconcile findings with overall structural consistency"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"reasoning":"The objective is to identify cyclic or oscillatory trends within the data over intermediate intervals and measure seasonal period and strength. Validation requires reconciliation with overall structural consistency."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
- stl_strength
  inputs: series, period(optional; omit→auto capped FFT)
  outputs: period, seasonal_strength, season_strength_bin, trend_strength
  depends: period often bound from fft_period.dominant_period when trusted
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool.",
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
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=854 completion=146 latency=5.28s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool."}
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

- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
- stl_strength: STL seasonal/trend strength.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, period=optional positive int | omit → auto via fft_period; never null/placeholder strings}
  returns: {series=period, period_trusted, seasonal_strength, season_strength_bin, trend_strength}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool.",
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
      "tool": "stl_strength",
      "args": {
        "series_index": 1,
        "period": "$step1.dominant_period"
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=1253 completion=328 latency=11.77s

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
{"evidence_plan":{"objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend.","required_evidence":["seasonal_period","seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Reconcile findings with overall structural consistency"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"reasoning":"The objective is to identify cyclic or oscillatory trends within the data over intermediate intervals and measure seasonal period and strength. Validation requires reconciliation with overall structural consistency."}
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
      "dominant_period": 23.999999999999996,
      "spectral_strength": 0.08983827881012546,
      "period_trusted": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "726ee7605c7aac2e5823de42d4c34d3c89859438"
  },
  {
    "call_id": "medium:step2",
    "step": 2,
    "tool_name": "stl_strength",
    "arguments": {
      "series_index": 1,
      "period": "$step1.dominant_period"
    },
    "resolved_arguments": {
      "series_index": 1,
      "period": 23.999999999999996
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "period": 23,
      "period_trusted": true,
      "period_source": "requested",
      "seasonal_strength": 0.6584640634890109,
      "season_strength_bin": "moderate",
      "trend_strength": 0.0982930973618047,
      "metric_definition": "seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong",
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "704c027e38d41e8feed4ffdce85920a6e5173d89"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate that a dominant period was detected using FFT (Fast Fourier Transform) with a period length of approximately 24, and this period was confirmed as significant using STL decomposition with a seasonal strength of 0.658, which falls into the 'moderate' category.",
  "scale": "medium",
  "observations": [
    "There exists a cyclic or oscillatory trend within the data."
  ],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There exists a cyclic or oscillatory trend within the data.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        },
        {
          "type": "seasonal_strength",
          "value": 0.6584640634890109,
          "source_tool": "stl_strength",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "cyclic_or_oscillatory_trend"
    }
  ],
  "coverage": {"seasonal_strength": "tool_supported", "seasonal_period": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4075 completion=330 latency=12.89s

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
{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements, each capturing different features such as oscillatory behavior, cyclical patterns, steady-state levels with step changes, and stable fluctuations.","task_summary":"Choose the correct descriptive statement for the provided time series data among multiple options.","target_output":"The description that best fits the provided time series data.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}],"scales":["medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["The selected description accurately reflects the observed features of the time series.","The chosen description does not contradict the evidence gathered about the time series structure."],"notes":"Ensure all observations are integrated to make a well-informed decision on the description that matches the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. Required measurements include the global trend and the count of step-level changes.",
  "evidence_plan": {
    "objective": "Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.",
    "claims_to_support": [
      {
        "claim": "The time series exhibits a global trend.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "There are identifiable step-level changes in the time series.",
        "required_evidence": ["step_level_count"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "long"
    },
    "validation_needs": ["Confirm trends and step changes are consistent across the entire time span"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "segment_trend",
        "reason": "Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.",
        "supports_evidence": ["global_trend"]
      },
      {
        "tool": "step_levels",
        "reason": "Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.",
        "supports_evidence": ["step_level_count"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=780 completion=131 latency=4.70s

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
{"evidence_plan":{"objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","claims_to_support":[{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Confirm trends and step changes are consistent across the entire time span"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. Required measurements include the global trend and the count of step-level changes."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. The required measurements include the global trend and the count of step-level changes.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "trend_series",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "step_levels",
      "output_key": "step_changes",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=859 completion=141 latency=5.07s

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
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_changes","input_binding":{}}],"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. The required measurements include the global trend and the count of step-level changes."}
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
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to analyze the long-term pattern of the single time series provided, focusing on identifying the global trend and counting step-level changes throughout the entire time span. We'll use `segment_trend` to determine the global trend of the series and `step_levels` to quantify the number of distinct step-level changes.",
  "calls": [
    {
      "step": 1,
      "tool": "segment_trend",
      "args": {"series_index": 1}
    },
    {
      "step": 2,
      "tool": "step_levels",
      "args": {"series_index": 1}
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=2488 completion=405 latency=14.99s

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
{"evidence_plan":{"objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","claims_to_support":[{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Confirm trends and step changes are consistent across the entire time span"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. Required measurements include the global trend and the count of step-level changes."}
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
      "slope": -0.006467315716272599,
      "direction": "downward",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 4.751652777777777,
      "std": 3.9109011346481624,
      "start_value": 14.2,
      "end_value": 9.55
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  },
  {
    "call_id": "long:step2",
    "step": 2,
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
      "n_unique_levels": 51,
      "n_plateau_runs": 573,
      "levels": [
        14.2,
        5.4,
        5.83,
        7.53,
        9.26,
        6.41,
        4.45,
        3.29,
        2.5,
        1.78,
        1.05,
        0.67,
        0.3566666666666667,
        4.04,
        8.32,
        10.23,
        6.14,
        6.68,
        10.98,
        11.31,
        9.74,
        4.9,
        2.95,
        1.41,
        13.17,
        7.19,
        15.34,
        11.63,
        3.72,
        5.13,
        8.63,
        9.99,
        8.89,
        10.59,
        11.96,
        8.01,
        13.8,
        15.81,
        12.89,
        2.21
      ],
      "plateau_runs": [
        14.2,
        5.4,
        5.83,
        5.38,
        5.83,
        7.53,
        9.26,
        7.69,
        6.41,
        4.45,
        3.29,
        2.5,
        1.78,
        1.05,
        0.67,
        0.3566666666666667,
        0.85,
        1.74,
        4.04,
        8.32,
        10.23,
        6.62,
        5.525,
        6.14,
        6.68,
        8.23,
        10.98,
        11.31,
        14.12,
        9.74,
        4.9,
        4.07,
        2.95,
        2.0,
        1.41,
        0.53,
        0.82,
        1.81,
        3.88,
        8.38,
        13.17,
        7.19,
        5.77,
        6.24,
        6.72,
        7.6,
        9.2,
        12.97,
        14.05,
        15.34,
        11.63,
        4.95,
        4.23,
        3.49,
        2.58,
        1.64,
        0.97,
        0.72,
        0.4633333333333334,
        0.96,
        1.82,
        2.44,
        3.72,
        4.68,
        5.37,
        6.140000000000001,
        6.6175,
        6.09,
        5.13,
        4.05,
        3.03,
        1.88,
        1.04,
        0.7,
        0.3233333333333333,
        0.61,
        1.06,
        1.4,
        2.29,
        3.36
      ],
      "plateau_lengths": [
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        3,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        4,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        3,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        4,
        1,
        1,
        1,
        3,
        1,
        1,
        1,
        3,
        1,
        1,
        1,
        1,
        1
      ],
      "tolerance": 0.2293
    },
    "error": null,
    "args_fingerprint": "9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The time series has been analyzed for global trends and step-level changes using two tools: 'segment_trend' and 'step_levels'. The 'segment_trend' tool indicates a vague downward trend with a negative slope, confirming the existence of a global trend. The 'step_levels' tool identified a significant number of unique step/plateau levels within the series, indicating frequent step-level changes throughout the time span.",
  "scale": "long",
  "observations": ["The time series exhibits a vague downward trend.", "Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The time series exhibits a global trend.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.006467315716272599,
          "source_tool": "segment_trend",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "There are identifiable step-level changes in the time series.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 51,
          "source_tool": "step_levels",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "step_level_count"
    }
  ],
  "coverage": {"global_trend": "tool_supported", "step_level_count": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=7379 completion=482 latency=20.10s

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
{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements, each capturing different features such as oscillatory behavior, cyclical patterns, steady-state levels with step changes, and stable fluctuations.","task_summary":"Choose the correct descriptive statement for the provided time series data among multiple options.","target_output":"The description that best fits the provided time series data.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}],"scales":["medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["The selected description accurately reflects the observed features of the time series.","The chosen description does not contradict the evidence gathered about the time series structure."],"notes":"Ensure all observations are integrated to make a well-informed decision on the description that matches the time series."}
</plan_context>

<task_summary>
Choose the correct descriptive statement for the provided time series data among multiple options.
</task_summary>

<temporal_profile>
{"short":null,"medium":{"reasoning":"Executed steps indicate that a dominant period was detected using FFT (Fast Fourier Transform) with a period length of approximately 24, and this period was confirmed as significant using STL decomposition with a seasonal strength of 0.658, which falls into the 'moderate' category.","scale":"medium","observations":["There exists a cyclic or oscillatory trend within the data."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 23.999999999999996, \"spectral_strength\": 0.08983827881012546, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 23.999999999999996}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 23, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.6584640634890109, \"season_strength_bin\": \"moderate\", \"trend_strength\": 0.0982930973618047, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"704c027e38d41e8feed4ffdce85920a6e5173d89\"}"],"evidence_plan":{"objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend.","required_evidence":["seasonal_period","seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Reconcile findings with overall structural consistency"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool."},"structured_observations":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"coverage":{"seasonal_strength":"tool_supported","seasonal_period":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":23.999999999999996,"spectral_strength":0.08983827881012546,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":23.999999999999996},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":23,"period_trusted":true,"period_source":"requested","seasonal_strength":0.6584640634890109,"season_strength_bin":"moderate","trend_strength":0.0982930973618047,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":[]},"error":null,"args_fingerprint":"704c027e38d41e8feed4ffdce85920a6e5173d89"}],"skipped_stages":[]},"long":{"reasoning":"The time series has been analyzed for global trends and step-level changes using two tools: 'segment_trend' and 'step_levels'. The 'segment_trend' tool indicates a vague downward trend with a negative slope, confirming the existence of a global trend. The 'step_levels' tool identified a significant number of unique step/plateau levels within the series, indicating frequent step-level changes throughout the time span.","scale":"long","observations":["The time series exhibits a vague downward trend.","Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.006467315716272599, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.751652777777777, \"std\": 3.9109011346481624, \"start_value\": 14.2, \"end_value\": 9.55}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 51, \"n_plateau_runs\": 573, \"levels\": [14.2, 5.4, 5.83, 7.53, 9.26, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 4.04, 8.32, 10.23, 6.14, 6.68, 10.98, 11.31, 9.74, 4.9, 2.95, 1.41, 13.17, 7.19, 15.34, 11.63, 3.72, 5.13, 8.63, 9.99, 8.89, 10.59, 11.96, 8.01, 13.8, 15.81, 12.89, 2.21], \"plateau_runs\": [14.2, 5.4, 5.83, 5.38, 5.83, 7.53, 9.26, 7.69, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 0.85, 1.74, 4.04, 8.32, 10.23, 6.62, 5.525, 6.14, 6.68, 8.23, 10.98, 11.31, 14.12, 9.74, 4.9, 4.07, 2.95, 2.0, 1.41, 0.53, 0.82, 1.81, 3.88, 8.38, 13.17, 7.19, 5.77, 6.24, 6.72, 7.6, 9.2, 12.97, 14.05, 15.34, 11.63, 4.95, 4.23, 3.49, 2.58, 1.64, 0.97, 0.72, 0.4633333333333334, 0.96, 1.82, 2.44, 3.72, 4.68, 5.37, 6.140000000000001, 6.6175, 6.09, 5.13, 4.05, 3.03, 1.88, 1.04, 0.7, 0.3233333333333333, 0.61, 1.06, 1.4, 2.29, 3.36], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 4, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1], \"tolerance\": 0.2293}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","claims_to_support":[{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Confirm trends and step changes are consistent across the entire time span"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_changes","input_binding":{}}],"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. The required measurements include the global trend and the count of step-level changes."},"structured_observations":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"global_trend":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.006467315716272599,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.751652777777777,"std":3.9109011346481624,"start_value":14.2,"end_value":9.55},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":51,"n_plateau_runs":573,"levels":[14.2,5.4,5.83,7.53,9.26,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,4.04,8.32,10.23,6.14,6.68,10.98,11.31,9.74,4.9,2.95,1.41,13.17,7.19,15.34,11.63,3.72,5.13,8.63,9.99,8.89,10.59,11.96,8.01,13.8,15.81,12.89,2.21],"plateau_runs":[14.2,5.4,5.83,5.38,5.83,7.53,9.26,7.69,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,0.85,1.74,4.04,8.32,10.23,6.62,5.525,6.14,6.68,8.23,10.98,11.31,14.12,9.74,4.9,4.07,2.95,2.0,1.41,0.53,0.82,1.81,3.88,8.38,13.17,7.19,5.77,6.24,6.72,7.6,9.2,12.97,14.05,15.34,11.63,4.95,4.23,3.49,2.58,1.64,0.97,0.72,0.4633333333333334,0.96,1.82,2.44,3.72,4.68,5.37,6.140000000000001,6.6175,6.09,5.13,4.05,3.03,1.88,1.04,0.7,0.3233333333333333,0.61,1.06,1.4,2.29,3.36],"plateau_lengths":[1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,4,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,4,1,1,1,3,1,1,1,3,1,1,1,1,1],"tolerance":0.2293},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"There exists a cyclic or oscillatory trend within the data. The time series exhibits a vague downward trend. Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes.","structured_by_scale":{"medium":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"long":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) The data shows regular oscillatory behavior with consistent amplitude variations, featuring recurring peaks around 20-30 and baseline values near 1-2 throughout the sequence.
B) This time series exhibits cyclical patterns with periodic spikes reaching peaks around 15-20, followed by gradual declines to near-zero values before repeating the cycle.
C) This series demonstrates relatively stable fluctuations around 2-3 with occasional upward excursions, showing gradual trending behavior and moderate variability across the observation period.
D) The data maintains high baseline values around 87-94 with occasional step-like transitions and brief periods of lower values, exhibiting overall stability with discrete level changes.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides a cyclic or oscillatory trend with a dominant period of approximately 24 hours, moderate seasonal strength (0.658), a vague downward global trend with a slight negative slope (-0.0065), and fifty-one unique step levels. Given these characteristics, the task requires selecting the most accurate description for the provided time series among four candidate statements.",
  "evidence_plan": {
    "objective": "Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.",
    "claims_to_support": [
      {
        "claim": "There exists a cyclic or oscillatory trend within the data.",
        "required_evidence": ["seasonal_period", "seasonal_strength"]
      },
      {
        "claim": "The time series exhibits a global trend.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "There are identifiable step-level changes in the time series.",
        "required_evidence": ["step_level_count"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["Ensure that chosen description aligns with identified periodicity, level changes, and trends"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All required evidence (seasonal_period, seasonal_strength, global_trend, step_level_count) has been provided by previous analyses and does not require additional tools.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "medium:step1",
          "field": "dominant_period"
        },
        {
          "type": "upstream_observation",
          "ref": "medium:step2",
          "field": "seasonal_strength"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "slope"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step2",
          "field": "n_unique_levels"
        }
      ]
    }
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=6220 completion=669 latency=26.70s

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
{"evidence_plan":{"objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend within the data.","required_evidence":["seasonal_period","seasonal_strength"]},{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All required evidence (seasonal_period, seasonal_strength, global_trend, step_level_count) has been provided by previous analyses and does not require additional tools.","evidence_sources":[{"type":"upstream_observation","ref":"medium:step1","field":"dominant_period"},{"type":"upstream_observation","ref":"medium:step2","field":"seasonal_strength"},{"type":"upstream_observation","ref":"long:step1","field":"slope"},{"type":"upstream_observation","ref":"long:step2","field":"n_unique_levels"}]}},"reasoning":"The current evidence provides a cyclic or oscillatory trend with a dominant period of approximately 24 hours, moderate seasonal strength (0.658), a vague downward global trend with a slight negative slope (-0.0065), and fifty-one unique step levels. Given these characteristics, the task requires selecting the most accurate description for the provided time series among four candidate statements."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":null,"medium":{"reasoning":"Executed steps indicate that a dominant period was detected using FFT (Fast Fourier Transform) with a period length of approximately 24, and this period was confirmed as significant using STL decomposition with a seasonal strength of 0.658, which falls into the 'moderate' category.","scale":"medium","observations":["There exists a cyclic or oscillatory trend within the data."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 23.999999999999996, \"spectral_strength\": 0.08983827881012546, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 23.999999999999996}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 23, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.6584640634890109, \"season_strength_bin\": \"moderate\", \"trend_strength\": 0.0982930973618047, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"704c027e38d41e8feed4ffdce85920a6e5173d89\"}"],"evidence_plan":{"objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend.","required_evidence":["seasonal_period","seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Reconcile findings with overall structural consistency"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool."},"structured_observations":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"coverage":{"seasonal_strength":"tool_supported","seasonal_period":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":23.999999999999996,"spectral_strength":0.08983827881012546,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":23.999999999999996},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":23,"period_trusted":true,"period_source":"requested","seasonal_strength":0.6584640634890109,"season_strength_bin":"moderate","trend_strength":0.0982930973618047,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":[]},"error":null,"args_fingerprint":"704c027e38d41e8feed4ffdce85920a6e5173d89"}],"skipped_stages":[]},"long":{"reasoning":"The time series has been analyzed for global trends and step-level changes using two tools: 'segment_trend' and 'step_levels'. The 'segment_trend' tool indicates a vague downward trend with a negative slope, confirming the existence of a global trend. The 'step_levels' tool identified a significant number of unique step/plateau levels within the series, indicating frequent step-level changes throughout the time span.","scale":"long","observations":["The time series exhibits a vague downward trend.","Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.006467315716272599, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.751652777777777, \"std\": 3.9109011346481624, \"start_value\": 14.2, \"end_value\": 9.55}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 51, \"n_plateau_runs\": 573, \"levels\": [14.2, 5.4, 5.83, 7.53, 9.26, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 4.04, 8.32, 10.23, 6.14, 6.68, 10.98, 11.31, 9.74, 4.9, 2.95, 1.41, 13.17, 7.19, 15.34, 11.63, 3.72, 5.13, 8.63, 9.99, 8.89, 10.59, 11.96, 8.01, 13.8, 15.81, 12.89, 2.21], \"plateau_runs\": [14.2, 5.4, 5.83, 5.38, 5.83, 7.53, 9.26, 7.69, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 0.85, 1.74, 4.04, 8.32, 10.23, 6.62, 5.525, 6.14, 6.68, 8.23, 10.98, 11.31, 14.12, 9.74, 4.9, 4.07, 2.95, 2.0, 1.41, 0.53, 0.82, 1.81, 3.88, 8.38, 13.17, 7.19, 5.77, 6.24, 6.72, 7.6, 9.2, 12.97, 14.05, 15.34, 11.63, 4.95, 4.23, 3.49, 2.58, 1.64, 0.97, 0.72, 0.4633333333333334, 0.96, 1.82, 2.44, 3.72, 4.68, 5.37, 6.140000000000001, 6.6175, 6.09, 5.13, 4.05, 3.03, 1.88, 1.04, 0.7, 0.3233333333333333, 0.61, 1.06, 1.4, 2.29, 3.36], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 4, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1], \"tolerance\": 0.2293}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","claims_to_support":[{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Confirm trends and step changes are consistent across the entire time span"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_changes","input_binding":{}}],"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. The required measurements include the global trend and the count of step-level changes."},"structured_observations":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"global_trend":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.006467315716272599,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.751652777777777,"std":3.9109011346481624,"start_value":14.2,"end_value":9.55},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":51,"n_plateau_runs":573,"levels":[14.2,5.4,5.83,7.53,9.26,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,4.04,8.32,10.23,6.14,6.68,10.98,11.31,9.74,4.9,2.95,1.41,13.17,7.19,15.34,11.63,3.72,5.13,8.63,9.99,8.89,10.59,11.96,8.01,13.8,15.81,12.89,2.21],"plateau_runs":[14.2,5.4,5.83,5.38,5.83,7.53,9.26,7.69,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,0.85,1.74,4.04,8.32,10.23,6.62,5.525,6.14,6.68,8.23,10.98,11.31,14.12,9.74,4.9,4.07,2.95,2.0,1.41,0.53,0.82,1.81,3.88,8.38,13.17,7.19,5.77,6.24,6.72,7.6,9.2,12.97,14.05,15.34,11.63,4.95,4.23,3.49,2.58,1.64,0.97,0.72,0.4633333333333334,0.96,1.82,2.44,3.72,4.68,5.37,6.140000000000001,6.6175,6.09,5.13,4.05,3.03,1.88,1.04,0.7,0.3233333333333333,0.61,1.06,1.4,2.29,3.36],"plateau_lengths":[1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,4,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,4,1,1,1,3,1,1,1,3,1,1,1,1,1],"tolerance":0.2293},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"There exists a cyclic or oscillatory trend within the data. The time series exhibits a vague downward trend. Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes.","structured_by_scale":{"medium":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"long":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) The data shows regular oscillatory behavior with consistent amplitude variations, featuring recurring peaks around 20-30 and baseline values near 1-2 throughout the sequence.
B) This time series exhibits cyclical patterns with periodic spikes reaching peaks around 15-20, followed by gradual declines to near-zero values before repeating the cycle.
C) This series demonstrates relatively stable fluctuations around 2-3 with occasional upward excursions, showing gradual trending behavior and moderate variability across the observation period.
D) The data maintains high baseline values around 87-94 with occasional step-like transitions and brief periods of lower values, exhibiting overall stability with discrete level changes.
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the time series shows a dominant period of approximately 24 hours, moderate seasonal strength (0.658), a vague downward global trend with a slight negative slope (-0.0065), and fifty-one unique step levels. These characteristics align best with candidate D, as it describes overall stability with discrete level changes and baseline values around 87-94.",
  "hypothesis": "The time series characteristics match most closely with candidate D, due to the presence of step-like transitions and high baseline values.",
  "evidence": ["There is a dominant period of approximately 24 hours.", "The seasonal strength is moderate with a value of 0.658", "There is a vague downward global trend with a slope of -0.0065", "There are fifty-one unique step levels within the series"],
  "candidate_preference": "D",
  "confidence": 0.9,
  "tool_calls": [],
  "cited_tool_call_ids": ["medium:step1", "medium:step2", "long:step1", "long:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "There exists a cyclic or oscillatory trend within the data.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24,
          "provenance": "tool",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        },
        {
          "type": "seasonal_strength",
          "value": 0.6584640634890109,
          "provenance": "tool",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The time series exhibits a global trend.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.006467315716272599,
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are identifiable step-level changes in the time series.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 51,
          "provenance": "tool",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "seasonal_period": "tool_supported",
    "seasonal_strength": "tool_supported",
    "global_trend": "tool_supported",
    "step_level_count": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=7390 completion=488 latency=20.34s

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
{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements, each capturing different features such as oscillatory behavior, cyclical patterns, steady-state levels with step changes, and stable fluctuations.","task_summary":"Choose the correct descriptive statement for the provided time series data among multiple options.","target_output":"The description that best fits the provided time series data.","answer_type":"choice","capability":"Hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["Reconcile findings with overall structural consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","required_measurements":["global_trend","step_level_count"],"validation_requirements":["Confirm trends and step changes are consistent across the entire time span"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}],"scales":["medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["The selected description accurately reflects the observed features of the time series.","The chosen description does not contradict the evidence gathered about the time series structure."],"notes":"Ensure all observations are integrated to make a well-informed decision on the description that matches the time series."}
</plan_context>

<task_summary>
Choose the correct descriptive statement for the provided time series data among multiple options.
</task_summary>

<temporal_profile>
{"short":null,"medium":{"reasoning":"Executed steps indicate that a dominant period was detected using FFT (Fast Fourier Transform) with a period length of approximately 24, and this period was confirmed as significant using STL decomposition with a seasonal strength of 0.658, which falls into the 'moderate' category.","scale":"medium","observations":["There exists a cyclic or oscillatory trend within the data."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 23.999999999999996, \"spectral_strength\": 0.08983827881012546, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 23.999999999999996}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 23, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.6584640634890109, \"season_strength_bin\": \"moderate\", \"trend_strength\": 0.0982930973618047, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"704c027e38d41e8feed4ffdce85920a6e5173d89\"}"],"evidence_plan":{"objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend.","required_evidence":["seasonal_period","seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Reconcile findings with overall structural consistency"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool."},"structured_observations":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"coverage":{"seasonal_strength":"tool_supported","seasonal_period":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":23.999999999999996,"spectral_strength":0.08983827881012546,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":23.999999999999996},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":23,"period_trusted":true,"period_source":"requested","seasonal_strength":0.6584640634890109,"season_strength_bin":"moderate","trend_strength":0.0982930973618047,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":[]},"error":null,"args_fingerprint":"704c027e38d41e8feed4ffdce85920a6e5173d89"}],"skipped_stages":[]},"long":{"reasoning":"The time series has been analyzed for global trends and step-level changes using two tools: 'segment_trend' and 'step_levels'. The 'segment_trend' tool indicates a vague downward trend with a negative slope, confirming the existence of a global trend. The 'step_levels' tool identified a significant number of unique step/plateau levels within the series, indicating frequent step-level changes throughout the time span.","scale":"long","observations":["The time series exhibits a vague downward trend.","Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.006467315716272599, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.751652777777777, \"std\": 3.9109011346481624, \"start_value\": 14.2, \"end_value\": 9.55}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 51, \"n_plateau_runs\": 573, \"levels\": [14.2, 5.4, 5.83, 7.53, 9.26, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 4.04, 8.32, 10.23, 6.14, 6.68, 10.98, 11.31, 9.74, 4.9, 2.95, 1.41, 13.17, 7.19, 15.34, 11.63, 3.72, 5.13, 8.63, 9.99, 8.89, 10.59, 11.96, 8.01, 13.8, 15.81, 12.89, 2.21], \"plateau_runs\": [14.2, 5.4, 5.83, 5.38, 5.83, 7.53, 9.26, 7.69, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 0.85, 1.74, 4.04, 8.32, 10.23, 6.62, 5.525, 6.14, 6.68, 8.23, 10.98, 11.31, 14.12, 9.74, 4.9, 4.07, 2.95, 2.0, 1.41, 0.53, 0.82, 1.81, 3.88, 8.38, 13.17, 7.19, 5.77, 6.24, 6.72, 7.6, 9.2, 12.97, 14.05, 15.34, 11.63, 4.95, 4.23, 3.49, 2.58, 1.64, 0.97, 0.72, 0.4633333333333334, 0.96, 1.82, 2.44, 3.72, 4.68, 5.37, 6.140000000000001, 6.6175, 6.09, 5.13, 4.05, 3.03, 1.88, 1.04, 0.7, 0.3233333333333333, 0.61, 1.06, 1.4, 2.29, 3.36], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 4, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1], \"tolerance\": 0.2293}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","claims_to_support":[{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Confirm trends and step changes are consistent across the entire time span"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_changes","input_binding":{}}],"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. The required measurements include the global trend and the count of step-level changes."},"structured_observations":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"global_trend":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.006467315716272599,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.751652777777777,"std":3.9109011346481624,"start_value":14.2,"end_value":9.55},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":51,"n_plateau_runs":573,"levels":[14.2,5.4,5.83,7.53,9.26,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,4.04,8.32,10.23,6.14,6.68,10.98,11.31,9.74,4.9,2.95,1.41,13.17,7.19,15.34,11.63,3.72,5.13,8.63,9.99,8.89,10.59,11.96,8.01,13.8,15.81,12.89,2.21],"plateau_runs":[14.2,5.4,5.83,5.38,5.83,7.53,9.26,7.69,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,0.85,1.74,4.04,8.32,10.23,6.62,5.525,6.14,6.68,8.23,10.98,11.31,14.12,9.74,4.9,4.07,2.95,2.0,1.41,0.53,0.82,1.81,3.88,8.38,13.17,7.19,5.77,6.24,6.72,7.6,9.2,12.97,14.05,15.34,11.63,4.95,4.23,3.49,2.58,1.64,0.97,0.72,0.4633333333333334,0.96,1.82,2.44,3.72,4.68,5.37,6.140000000000001,6.6175,6.09,5.13,4.05,3.03,1.88,1.04,0.7,0.3233333333333333,0.61,1.06,1.4,2.29,3.36],"plateau_lengths":[1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,4,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,4,1,1,1,3,1,1,1,3,1,1,1,1,1],"tolerance":0.2293},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"There exists a cyclic or oscillatory trend within the data. The time series exhibits a vague downward trend. Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes.","structured_by_scale":{"medium":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"long":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
retry_context=unresolved_claims=['parse_failure']
</metadata>

<candidates>
A) The data shows regular oscillatory behavior with consistent amplitude variations, featuring recurring peaks around 20-30 and baseline values near 1-2 throughout the sequence.
B) This time series exhibits cyclical patterns with periodic spikes reaching peaks around 15-20, followed by gradual declines to near-zero values before repeating the cycle.
C) This series demonstrates relatively stable fluctuations around 2-3 with occasional upward excursions, showing gradual trending behavior and moderate variability across the observation period.
D) The data maintains high baseline values around 87-94 with occasional step-like transitions and brief periods of lower values, exhibiting overall stability with discrete level changes.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The task requires matching the structural and temporal characteristics of the provided time series to the best fitting candidate description. Based on previous evidence, there is a cyclical trend with a seasonal period of approximately 24 hours and a seasonal strength of moderate (0.658), along with a vague downward trend and fifty-one step-level changes.",
  "evidence_plan": {
    "objective": "Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.",
    "claims_to_support": [
      {
        "claim": "The time series exhibits cyclical patterns with a seasonal period of approximately 24 hours.",
        "required_evidence": ["seasonal_period"]
      },
      {
        "claim": "The cyclical patterns have a seasonal strength classified as moderate.",
        "required_evidence": ["seasonal_strength"]
      },
      {
        "claim": "There is a vague downward global trend.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "The series has fifty-one step-level changes.",
        "required_evidence": ["step_level_count"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": ["Ensure that chosen description aligns with identified periodicity, level changes, and trends"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All necessary evidence has been collected from previous tasks; no additional tool calls are needed.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "medium:step1",
          "field": "dominant_period"
        },
        {
          "type": "upstream_observation",
          "ref": "medium:step2",
          "field": "seasonal_strength"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "slope"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step2",
          "field": "n_unique_levels"
        }
      ]
    }
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=6218 completion=689 latency=27.48s

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
{"evidence_plan":{"objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","claims_to_support":[{"claim":"The time series exhibits cyclical patterns with a seasonal period of approximately 24 hours.","required_evidence":["seasonal_period"]},{"claim":"The cyclical patterns have a seasonal strength classified as moderate.","required_evidence":["seasonal_strength"]},{"claim":"There is a vague downward global trend.","required_evidence":["global_trend"]},{"claim":"The series has fifty-one step-level changes.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"role":"matching"},"validation_needs":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All necessary evidence has been collected from previous tasks; no additional tool calls are needed.","evidence_sources":[{"type":"upstream_observation","ref":"medium:step1","field":"dominant_period"},{"type":"upstream_observation","ref":"medium:step2","field":"seasonal_strength"},{"type":"upstream_observation","ref":"long:step1","field":"slope"},{"type":"upstream_observation","ref":"long:step2","field":"n_unique_levels"}]}},"reasoning":"The task requires matching the structural and temporal characteristics of the provided time series to the best fitting candidate description. Based on previous evidence, there is a cyclical trend with a seasonal period of approximately 24 hours and a seasonal strength of moderate (0.658), along with a vague downward trend and fifty-one step-level changes."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":null,"medium":{"reasoning":"Executed steps indicate that a dominant period was detected using FFT (Fast Fourier Transform) with a period length of approximately 24, and this period was confirmed as significant using STL decomposition with a seasonal strength of 0.658, which falls into the 'moderate' category.","scale":"medium","observations":["There exists a cyclic or oscillatory trend within the data."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 23.999999999999996, \"spectral_strength\": 0.08983827881012546, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 23.999999999999996}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 23, \"period_trusted\": true, \"period_source\": \"requested\", \"seasonal_strength\": 0.6584640634890109, \"season_strength_bin\": \"moderate\", \"trend_strength\": 0.0982930973618047, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"704c027e38d41e8feed4ffdce85920a6e5173d89\"}"],"evidence_plan":{"objective":"Identify any cyclic or oscillatory trends within the data over intermediate intervals.","claims_to_support":[{"claim":"There exists a cyclic or oscillatory trend.","required_evidence":["seasonal_period","seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Reconcile findings with overall structural consistency"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect dominant period and assess if it corresponds to an oscillatory/cyclic trend.","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To verify the strength and confirm if the identified period corresponds to a significant seasonal trend.","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"The objective is to identify cyclic or oscillatory trends within the traffic hourly data by measuring the seasonal period and strength. This involves using the fft_period tool to detect the dominant period and then verifying this period's significance through the stl_strength tool."},"structured_observations":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"coverage":{"seasonal_strength":"tool_supported","seasonal_period":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":23.999999999999996,"spectral_strength":0.08983827881012546,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":23.999999999999996},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":23,"period_trusted":true,"period_source":"requested","seasonal_strength":0.6584640634890109,"season_strength_bin":"moderate","trend_strength":0.0982930973618047,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":[]},"error":null,"args_fingerprint":"704c027e38d41e8feed4ffdce85920a6e5173d89"}],"skipped_stages":[]},"long":{"reasoning":"The time series has been analyzed for global trends and step-level changes using two tools: 'segment_trend' and 'step_levels'. The 'segment_trend' tool indicates a vague downward trend with a negative slope, confirming the existence of a global trend. The 'step_levels' tool identified a significant number of unique step/plateau levels within the series, indicating frequent step-level changes throughout the time span.","scale":"long","observations":["The time series exhibits a vague downward trend.","Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.006467315716272599, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.751652777777777, \"std\": 3.9109011346481624, \"start_value\": 14.2, \"end_value\": 9.55}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 51, \"n_plateau_runs\": 573, \"levels\": [14.2, 5.4, 5.83, 7.53, 9.26, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 4.04, 8.32, 10.23, 6.14, 6.68, 10.98, 11.31, 9.74, 4.9, 2.95, 1.41, 13.17, 7.19, 15.34, 11.63, 3.72, 5.13, 8.63, 9.99, 8.89, 10.59, 11.96, 8.01, 13.8, 15.81, 12.89, 2.21], \"plateau_runs\": [14.2, 5.4, 5.83, 5.38, 5.83, 7.53, 9.26, 7.69, 6.41, 4.45, 3.29, 2.5, 1.78, 1.05, 0.67, 0.3566666666666667, 0.85, 1.74, 4.04, 8.32, 10.23, 6.62, 5.525, 6.14, 6.68, 8.23, 10.98, 11.31, 14.12, 9.74, 4.9, 4.07, 2.95, 2.0, 1.41, 0.53, 0.82, 1.81, 3.88, 8.38, 13.17, 7.19, 5.77, 6.24, 6.72, 7.6, 9.2, 12.97, 14.05, 15.34, 11.63, 4.95, 4.23, 3.49, 2.58, 1.64, 0.97, 0.72, 0.4633333333333334, 0.96, 1.82, 2.44, 3.72, 4.68, 5.37, 6.140000000000001, 6.6175, 6.09, 5.13, 4.05, 3.03, 1.88, 1.04, 0.7, 0.3233333333333333, 0.61, 1.06, 1.4, 2.29, 3.36], \"plateau_lengths\": [1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 2, 4, 1, 1, 1, 3, 1, 1, 1, 3, 1, 1, 1, 1, 1], \"tolerance\": 0.2293}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.","claims_to_support":[{"claim":"The time series exhibits a global trend.","required_evidence":["global_trend"]},{"claim":"There are identifiable step-level changes in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Confirm trends and step changes are consistent across the entire time span"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures the direction and slope of the trend over the entire time series, providing an estimate of the global trend.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts the number of discrete step/plateau levels, providing an estimate of the number of step-level changes.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_changes","input_binding":{}}],"reasoning":"The objective is to analyze the long-term pattern of the time series, focusing on identifying global trends and step-level changes consistently across the entire time span. The required measurements include the global trend and the count of step-level changes."},"structured_observations":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"global_trend":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.006467315716272599,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.751652777777777,"std":3.9109011346481624,"start_value":14.2,"end_value":9.55},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":51,"n_plateau_runs":573,"levels":[14.2,5.4,5.83,7.53,9.26,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,4.04,8.32,10.23,6.14,6.68,10.98,11.31,9.74,4.9,2.95,1.41,13.17,7.19,15.34,11.63,3.72,5.13,8.63,9.99,8.89,10.59,11.96,8.01,13.8,15.81,12.89,2.21],"plateau_runs":[14.2,5.4,5.83,5.38,5.83,7.53,9.26,7.69,6.41,4.45,3.29,2.5,1.78,1.05,0.67,0.3566666666666667,0.85,1.74,4.04,8.32,10.23,6.62,5.525,6.14,6.68,8.23,10.98,11.31,14.12,9.74,4.9,4.07,2.95,2.0,1.41,0.53,0.82,1.81,3.88,8.38,13.17,7.19,5.77,6.24,6.72,7.6,9.2,12.97,14.05,15.34,11.63,4.95,4.23,3.49,2.58,1.64,0.97,0.72,0.4633333333333334,0.96,1.82,2.44,3.72,4.68,5.37,6.140000000000001,6.6175,6.09,5.13,4.05,3.03,1.88,1.04,0.7,0.3233333333333333,0.61,1.06,1.4,2.29,3.36],"plateau_lengths":[1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,4,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,3,1,1,1,1,1,1,2,4,1,1,1,3,1,1,1,3,1,1,1,1,1],"tolerance":0.2293},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"There exists a cyclic or oscillatory trend within the data. The time series exhibits a vague downward trend. Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes.","structured_by_scale":{"medium":[{"claim":"There exists a cyclic or oscillatory trend within the data.","evidence":[{"type":"seasonal_period","value":24,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seasonal_strength","value":0.6584640634890109,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cyclic_or_oscillatory_trend"}],"long":[{"claim":"The time series exhibits a global trend.","evidence":[{"type":"global_trend","value":-0.006467315716272599,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are identifiable step-level changes in the time series.","evidence":[{"type":"step_level_count","value":51,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.","required_measurements":["seasonal_period","seasonal_strength","global_trend","step_level_count"],"validation_requirements":["Ensure that chosen description aligns with identified periodicity, level changes, and trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) The data shows regular oscillatory behavior with consistent amplitude variations, featuring recurring peaks around 20-30 and baseline values near 1-2 throughout the sequence.
B) This time series exhibits cyclical patterns with periodic spikes reaching peaks around 15-20, followed by gradual declines to near-zero values before repeating the cycle.
C) This series demonstrates relatively stable fluctuations around 2-3 with occasional upward excursions, showing gradual trending behavior and moderate variability across the observation period.
D) The data maintains high baseline values around 87-94 with occasional step-like transitions and brief periods of lower values, exhibiting overall stability with discrete level changes.
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the target time series displays cyclical patterns with a seasonal period of approximately 24 hours and a moderate seasonal strength of 0.658. Additionally, it features a vague downward global trend and fifty-one step-level changes.",
  "role": "matching",
  "hypothesis": "The time series characteristics match best with a description that accounts for cyclical patterns with a periodicity of about 24 hours, moderate strength, vague downward trend, and numerous step-level changes.",
  "evidence": [
    "The time series exhibits cyclical patterns with a seasonal period of approximately 24 hours.",
    "The cyclical patterns have a seasonal strength classified as moderate.",
    "There is a vague downward global trend.",
    "The series has fifty-one step-level changes."
  ],
  "candidate_preference": "B",
  "confidence": 0.9,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "medium:step1",
    "medium:step2",
    "long:step1",
    "long:step2"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The time series exhibits cyclical patterns with a seasonal period of approximately 24 hours.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24,
          "provenance": "tool",
          "ref": null,
          "call_id": "medium:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The cyclical patterns have a seasonal strength classified as moderate.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.6584640634890109,
          "provenance": "tool",
          "ref": null,
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There is a vague downward global trend.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.006467315716272599,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The series has fifty-one step-level changes.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 51,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "seasonal_period": "tool_supported",
    "seasonal_strength": "tool_supported",
    "global_trend": "tool_supported",
    "step_level_count": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1661 completion=237 latency=8.66s

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
Given the provided time series numerical or graphical data, select the description from the four options that best corresponds to the data.
</question>

<candidates>
A) The data shows regular oscillatory behavior with consistent amplitude variations, featuring recurring peaks around 20-30 and baseline values near 1-2 throughout the sequence.
B) This time series exhibits cyclical patterns with periodic spikes reaching peaks around 15-20, followed by gradual declines to near-zero values before repeating the cycle.
C) This series demonstrates relatively stable fluctuations around 2-3 with occasional upward excursions, showing gradual trending behavior and moderate variability across the observation period.
D) The data maintains high baseline values around 87-94 with occasional step-like transitions and brief periods of lower values, exhibiting overall stability with discrete level changes.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Choose the correct descriptive statement for the provided time series data among multiple options.",
  "question_type": "choice",
  "required_output": "The description that best fits the provided time series data.",
  "success_criteria": [
    "The selected description accurately reflects the observed features of the time series.",
    "The chosen description does not contradict the evidence gathered about the time series structure."
  ],
  "assignments_brief": [
    {
      "agent": "homo:medium",
      "objective": "Identify any cyclic or oscillatory trends within the data over intermediate intervals.",
      "required_measurements": [
        "seasonal_period",
        "seasonal_strength"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Analyze the global pattern of the time series, looking for any underlying trends or step-level changes.",
      "required_measurements": [
        "global_trend",
        "step_level_count"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Match the extracted structural and temporal characteristics of the time series to one of the candidate descriptions based on similarity and correspondence.",
      "required_measurements": [
        "seasonal_period",
        "seasonal_strength",
        "global_trend",
        "step_level_count"
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
          "type": "seasonal_period",
          "value": 24,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "seasonal_strength",
          "value": 0.6584640634890109,
          "trusted": true
        }
      ],
      "coverage": {
        "seasonal_strength": "tool_supported",
        "seasonal_period": "tool_supported"
      },
      "summary": "There exists a cyclic or oscillatory trend within the data."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_trend",
          "value": -0.006467315716272599,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "step_level_count",
          "value": 51,
          "trusted": true
        }
      ],
      "coverage": {
        "global_trend": "tool_supported",
        "step_level_count": "tool_supported"
      },
      "summary": "The time series exhibits a vague downward trend. | Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."
    }
  },
  "conflicts": [],
  "summary": "There exists a cyclic or oscillatory trend within the data. The time series exhibits a vague downward trend. Fifty-one unique step-levels were detected within the series, indicating numerous step-level changes."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "The time series characteristics match best with a description that accounts for cyclical patterns with a periodicity of about 24 hours, moderate strength, vague downward trend, and numerous step-level changes.",
      "reasoning_chain": [
        "The time series exhibits cyclical patterns with a seasonal period of approximately 24 hours.",
        "seasonal_period=24",
        "The cyclical patterns have a seasonal strength classified as moderate.",
        "seasonal_strength=0.6584640634890109",
        "There is a vague downward global trend.",
        "global_trend=-0.006467315716272599",
        "The series has fifty-one step-level changes.",
        "step_level_count=51"
      ],
      "candidate_preference": "B",
      "confidence": 0.9,
      "grounded": true,
      "grounded_in": [
        "seasonal_period",
        "seasonal_strength",
        "global_trend",
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
  "reasoning": "The time series data matches best with option B due to its cyclical patterns with periodicity around 24 hours, moderate strength, a vague downward trend, and numerous step-level changes as indicated by the perception and reasoning layers.",
  "answer": "B",
  "explanation": "Option B accurately reflects the observed cyclical patterns with periodic peaks around 15-20, subsequent declines towards zero, and numerous step-level changes, along with a vague downward trend. The perception and reasoning layers confirm these features align closely with the described behavior in option B.",
  "confidence": 0.9,
  "conflicts": [],
  "cited_evidence": ["seasonal_period", "seasonal_strength", "global_trend", "step_level_count"],
  "decision_trace": {
    "metric": "seasonal_strength",
    "observed_value": 0.6584640634890109,
    "intervals_from_question": ["moderate"],
    "matched_label": "moderate",
    "matched_letter": "B"
  }
}
```
