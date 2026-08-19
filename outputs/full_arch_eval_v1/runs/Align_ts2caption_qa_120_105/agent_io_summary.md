# Agent IO summary: `Align:ts2caption_qa_120:105`

- Architecture pred: `D` (success=True)
- model_calls=22, tool_calls=10, latency=341.7s

## Planner — `planner`

tokens prompt=1150 completion=510 latency=18.11s

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
A) This series remains essentially flat at zero throughout most of its duration, with only one minor spike occurring around index 64, representing an almost entirely inactive signal.
B) This series displays irregular oscillations with multiple peaks of different heights, ranging from near-zero to approximately 19, with sporadic spikes and extended periods of low values.
C) This time series shows high variability with values fluctuating between approximately 7 and 100, featuring several dramatic drops and recoveries, creating a volatile pattern with significant amplitude changes.
D) This time series exhibits periodic patterns with sharp peaks reaching around 20-26 and valleys dropping near zero, showing cyclical behavior with varying amplitudes throughout the sequence.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.",
  "task_summary": "Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.",
  "target_output": "description",
  "answer_type": "choice",
  "capability": "alignment",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "long",
      "objective": "Assess global trends and major structural shifts across the entire series.",
      "required_measurements": ["global_trend", "level_shift_count"],
      "validation_requirements": ["verify consistency across multiple sections of the series"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "short",
      "objective": "Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.",
      "required_measurements": ["change_locations", "spike_heights", "anomaly_counts"],
      "validation_requirements": ["cross-validate against medium-scale analysis for robustness"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "medium",
      "objective": "Detect recurring patterns, cycles, and intermediate structures.",
      "required_measurements": ["seasonal_pattern", "cycle_length", "amplitude_variability"],
      "validation_requirements": ["ensure cyclic patterns are consistent over time"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "alignment",
      "objective": "Match identified time series characteristics with the most fitting description among the candidates.",
      "required_measurements": ["global_trend", "level_shift_count", "change_locations", "spike_heights", "anomaly_counts", "seasonal_pattern", "cycle_length", "amplitude_variability"],
      "validation_requirements": ["cross-reference findings with multiple scales to ensure coherent interpretation"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["correctly identifies key characteristics of the series"],
  "notes": "Ensure all characteristics are reconciled before making a final selection."
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4078 completion=304 latency=11.94s

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
{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.","task_summary":"Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.","target_output":"description","answer_type":"choice","capability":"alignment","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short","medium"],"heterogeneous_agents":["alignment"],"success_criteria":["correctly identifies key characteristics of the series"],"notes":"Ensure all characteristics are reconciled before making a final selection."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires assessing global trends and major structural shifts across the entire series. This involves identifying overall direction, level shifts, and verifying these characteristics consistently across different segments of the series.",
  "evidence_plan": {
    "objective": "Assess global trends and major structural shifts across the entire series.",
    "claims_to_support": [
      {"claim": "There exists a global trend in the series.", "required_evidence": ["global_trend"]},
      {"claim": "There are significant level shifts in the series.", "required_evidence": ["level_shift_count"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["verify consistency across multiple sections of the series"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "describe_series", "reason": "Provides an initial global statistical overview including slope, which indicates the overall trend.", "supports_evidence": ["global_trend"]},
      {"tool": "segment_trend", "reason": "Analyzes directional trend over specified segments to confirm consistency across the series.", "supports_evidence": ["global_trend"]},
      {"tool": "step_levels", "reason": "Counts discrete step or plateau levels which can indicate significant level shifts.", "supports_evidence": ["level_shift_count"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=787 completion=172 latency=6.14s

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
{"evidence_plan":{"objective":"Assess global trends and major structural shifts across the entire series.","claims_to_support":[{"claim":"There exists a global trend in the series.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview including slope, which indicates the overall trend.","supports_evidence":["global_trend"]},{"tool":"segment_trend","reason":"Analyzes directional trend over specified segments to confirm consistency across the series.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts discrete step or plateau levels which can indicate significant level shifts.","supports_evidence":["level_shift_count"]}],"no_tool_decision":null},"reasoning":"The task requires assessing global trends and major structural shifts across the entire series. This involves identifying overall direction, level shifts, and verifying these characteristics consistently across different segments of the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- segment_trend
  inputs: series_index, start, end
  outputs: series
- step_levels
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required.",
  "workflow": [
    {
      "step": 1,
      "tool": "describe_series",
      "output_key": "initial_statistical_summary",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "segment_trend",
      "output_key": "trend_consistency_across_segments",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "step_levels",
      "output_key": "count_of_significant_level_shifts",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=939 completion=150 latency=5.40s

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
{"workflow":[{"step":1,"tool":"describe_series","output_key":"initial_statistical_summary","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_consistency_across_segments","input_binding":{}},{"step":3,"tool":"step_levels","output_key":"count_of_significant_level_shifts","input_binding":{}}],"reasoning":"The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required."}
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
- segment_trend: Linear slope and direction (upward/downward/flat) for a segment.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series slope/direction for a segment}
- step_levels: Count discrete step/plateau levels (unique values and plateau runs) in a window. Use for stepwise/staircase/plateau questions.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=unique level count, plateau runs, lengths, and tolerance}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required.",
  "calls": [
    {
      "step": 1,
      "tool": "describe_series",
      "args": {}
    },
    {
      "step": 2,
      "tool": "segment_trend",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 3,
      "tool": "step_levels",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=2825 completion=426 latency=15.88s

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
{"evidence_plan":{"objective":"Assess global trends and major structural shifts across the entire series.","claims_to_support":[{"claim":"There exists a global trend in the series.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview including slope, which indicates the overall trend.","supports_evidence":["global_trend"]},{"tool":"segment_trend","reason":"Analyzes directional trend over specified segments to confirm consistency across the series.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts discrete step or plateau levels which can indicate significant level shifts.","supports_evidence":["level_shift_count"]}],"no_tool_decision":null},"reasoning":"The task requires assessing global trends and major structural shifts across the entire series. This involves identifying overall direction, level shifts, and verifying these characteristics consistently across different segments of the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "long:step1",
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
          "length": 288,
          "mean": 4.801909722222223,
          "std": 4.6428487609279205,
          "min": 0.0,
          "max": 26.36,
          "median": 4.725,
          "range": 26.36,
          "p50": 4.725,
          "p90": 7.593000000000003,
          "p99": 22.423199999999998,
          "start": 22.34,
          "end": 1.13,
          "slope": -0.07390243902439024
        }
      ]
    },
    "error": null,
    "args_fingerprint": "90b10717d4a3e6c0750bb980207b8d86753ac968"
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
      "slope": -0.07390243902439024,
      "direction": "downward",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 4.801909722222223,
      "std": 4.6428487609279205,
      "start_value": 22.34,
      "end_value": 1.13
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  },
  {
    "call_id": "long:step3",
    "step": 3,
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
      "n_unique_levels": 40,
      "n_plateau_runs": 199,
      "levels": [
        22.34,
        20.4,
        8.27,
        6.76,
        6.49,
        5.953333333333333,
        7.1,
        5.34,
        3.8,
        3.145,
        1.99,
        0.33,
        0.01,
        2.36,
        10.24,
        22.98,
        8.97,
        4.12,
        1.05,
        3.51,
        0.69,
        7.96,
        9.56,
        1.64,
        2.88,
        4.98,
        5.64,
        4.39,
        17.56,
        19.54,
        11.72,
        20.76,
        21.11,
        12.0,
        26.244999999999997,
        16.62,
        7.53,
        13.09,
        13.43,
        18.67
      ],
      "plateau_runs": [
        22.34,
        20.4,
        8.27,
        6.76,
        6.49,
        5.953333333333333,
        6.5,
        7.1,
        5.34,
        3.8,
        3.145,
        1.99,
        0.33,
        0.01,
        2.36,
        6.08,
        10.24,
        22.98,
        20.32,
        8.97,
        6.75,
        7.22,
        6.35,
        5.952500000000001,
        6.65,
        5.29,
        4.12,
        3.16,
        2.19,
        0.52,
        0.0025,
        1.05,
        6.26,
        5.984999999999999,
        6.8,
        5.14,
        3.91,
        3.51,
        3.21,
        2.16,
        0.69,
        0.025,
        2.24,
        5.77,
        7.96,
        9.56,
        8.27,
        7.27,
        6.6,
        6.96,
        6.064,
        5.11,
        4.19,
        3.415,
        2.53,
        1.64,
        0.076,
        1.87,
        2.88,
        3.8,
        4.98,
        5.64,
        6.1,
        6.91,
        6.39,
        6.993333333333333,
        6.38,
        5.45,
        4.12,
        4.39,
        4.01,
        3.09,
        1.98,
        0.73,
        0.0275,
        1.2,
        1.74,
        2.3,
        3.13,
        4.9
      ],
      "plateau_lengths": [
        1,
        1,
        1,
        1,
        1,
        3,
        2,
        1,
        1,
        1,
        2,
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
        4,
        1,
        1,
        1,
        2,
        1,
        1,
        12,
        1,
        2,
        2,
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
        2,
        1,
        5,
        1,
        1,
        2,
        1,
        1,
        5,
        1,
        1,
        1,
        1,
        1,
        1,
        2,
        1,
        3,
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
        1
      ],
      "tolerance": 0.2636
    },
    "error": null,
    "args_fingerprint": "9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes a global trend assessment and identification of significant level shifts in the series. Tools were used to provide an initial overview of the series and further detail on its trend and level shifts.",
  "scale": "long",
  "observations": ["The series exhibits a downward trend with a negative slope.", "Multiple discrete step or plateau levels suggest numerous level shifts within the series."],
  "evidence_intervals": ["Entire series"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There exists a global trend in the series.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.07390243902439024,
          "source_tool": "describe_series",
          "call_id": "long:step1",
          "provenance": "tool"
        },
        {
          "type": "global_trend",
          "value": -0.07390243902439024,
          "source_tool": "segment_trend",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "There are significant level shifts in the series.",
      "evidence": [
        {
          "type": "level_shift_count",
          "value": 40,
          "source_tool": "step_levels",
          "call_id": "long:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "level_shift_count"
    }
  ],
  "coverage": {"global_trend": "tool_supported", "level_shift_count": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4085 completion=301 latency=11.83s

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
{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.","task_summary":"Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.","target_output":"description","answer_type":"choice","capability":"alignment","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short","medium"],"heterogeneous_agents":["alignment"],"success_criteria":["correctly identifies key characteristics of the series"],"notes":"Ensure all characteristics are reconciled before making a final selection."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations, spike heights, and anomaly counts.",
  "evidence_plan": {
    "objective": "Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.",
    "claims_to_support": [
      {"claim": "Change locations are accurately identified.", "required_evidence": ["change_locations"]},
      {"claim": "Spike heights are correctly measured.", "required_evidence": ["spike_heights"]},
      {"claim": "Anomaly counts are precisely determined.", "required_evidence": ["anomaly_counts"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["cross-validate against medium-scale analysis for robustness"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "diff_stats", "reason": "Detects changes and roughness in the series, useful for identifying abrupt changes.", "supports_evidence": ["change_locations"]},
      {"tool": "anomaly_detect", "reason": "Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.", "supports_evidence": ["spike_heights", "anomaly_counts"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=773 completion=128 latency=4.60s

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
{"evidence_plan":{"objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","claims_to_support":[{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["cross-validate against medium-scale analysis for robustness"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Detects changes and roughness in the series, useful for identifying abrupt changes.","supports_evidence":["change_locations"]},{"tool":"anomaly_detect","reason":"Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.","supports_evidence":["spike_heights","anomaly_counts"]}],"no_tool_decision":null},"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations, spike heights, and anomaly counts."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- diff_stats
  inputs: series_index, start, end
  outputs: series
- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations and anomaly counts using the diff_stats and anomaly_detect tools.",
  "workflow": [
    {
      "step": 1,
      "tool": "diff_stats",
      "output_key": "change_locations",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "output_key": "anomaly_counts",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=838 completion=135 latency=4.86s

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
{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_locations","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_counts","input_binding":{}}],"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations and anomaly counts using the diff_stats and anomaly_detect tools."}
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
- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, z_threshold=float (default 3.0)}
  returns: {series=anomaly count/indices and max absolute z-score}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations using the diff_stats tool and then detecting anomalies in the same time series using the anomaly_detect tool.",
  "calls": [
    {
      "step": 1,
      "tool": "diff_stats",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1235 completion=485 latency=17.26s

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
{"evidence_plan":{"objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","claims_to_support":[{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["cross-validate against medium-scale analysis for robustness"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Detects changes and roughness in the series, useful for identifying abrupt changes.","supports_evidence":["change_locations"]},{"tool":"anomaly_detect","reason":"Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.","supports_evidence":["spike_heights","anomaly_counts"]}],"no_tool_decision":null},"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations, spike heights, and anomaly counts."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "diff_stats",
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
      "mean_diff": -0.07390243902439027,
      "std_diff": 2.602568303513662,
      "max_abs_diff": 14.36,
      "n_sign_changes": 56
    },
    "error": null,
    "args_fingerprint": "4a37b60672ab33aaec2956de8706ddd2e6292caf"
  },
  {
    "call_id": "short:step2",
    "step": 2,
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
      "n_anomalies": 10,
      "anomaly_indices": [
        0,
        1,
        24,
        25,
        145,
        168,
        169,
        192,
        193,
        240
      ],
      "max_abs_z": 4.643289365615513
    },
    "error": null,
    "args_fingerprint": "9ee1de07f72732a041d0e186f599357a414ae94b"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Executed steps include 'diff_stats' for detecting changes and roughness in the series, which helps in identifying abrupt changes, and 'anomaly_detect' for detecting spikes/outliers, necessary for measuring spike heights and anomaly counts.",
  "scale": "short",
  "observations": ["Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series."],
  "evidence_intervals": ["[start of series, end of series]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Change locations are accurately identified.",
      "evidence": [
        {
          "type": "change_locations",
          "value": 56,
          "source_tool": "diff_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_locations"
    },
    {
      "claim": "Spike heights are correctly measured.",
      "evidence": [
        {
          "type": "spike_heights",
          "value": 4.643289365615513,
          "source_tool": "anomaly_detect",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "spike_heights"
    },
    {
      "claim": "Anomaly counts are precisely determined.",
      "evidence": [
        {
          "type": "anomaly_counts",
          "value": 10,
          "source_tool": "anomaly_detect",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomaly_counts"
    }
  ],
  "coverage": {"change_locations": "tool_supported", "spike_heights": "tool_supported", "anomaly_counts": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4078 completion=357 latency=13.86s

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
{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.","task_summary":"Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.","target_output":"description","answer_type":"choice","capability":"alignment","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short","medium"],"heterogeneous_agents":["alignment"],"success_criteria":["correctly identifies key characteristics of the series"],"notes":"Ensure all characteristics are reconciled before making a final selection."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect recurring patterns, cycles, and intermediate structures in the medium-scale context. Required measurements include seasonal patterns, cycle lengths, and amplitude variabilities. Validation ensures these cyclic patterns are consistent over time.",
  "evidence_plan": {
    "objective": "Detect recurring patterns, cycles, and intermediate structures.",
    "claims_to_support": [
      {"claim": "The time series exhibits a clear seasonal pattern.", "required_evidence": ["seasonal autocorrelation at known lags"]},
      {"claim": "There are identifiable cycle lengths present.", "required_evidence": ["dominant period from FFT"]},
      {"claim": "Amplitude variability is evident over different cycles.", "required_evidence": ["variations in amplitude over cycle lengths"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["verify cyclic patterns are consistent over time"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "seas_acf", "reason": "Measures seasonal autocorrelation at known lags to support the detection of seasonal patterns.", "supports_evidence": ["seasonal autocorrelation at known lags"]},
      {"tool": "fft_period", "reason": "Finds dominant period via FFT to identify cycle lengths.", "supports_evidence": ["dominant period from FFT"]},
      {"tool": "value_at_index", "reason": "Retrieves specific amplitude values at various points to evaluate amplitude variability.", "supports_evidence": ["variations in amplitude over cycle lengths"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=880 completion=154 latency=5.52s

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
{"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"The time series exhibits a clear seasonal pattern.","required_evidence":["seasonal autocorrelation at known lags"]},{"claim":"There are identifiable cycle lengths present.","required_evidence":["dominant period from FFT"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["variations in amplitude over cycle lengths"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verify cyclic patterns are consistent over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at known lags to support the detection of seasonal patterns.","supports_evidence":["seasonal autocorrelation at known lags"]},{"tool":"fft_period","reason":"Finds dominant period via FFT to identify cycle lengths.","supports_evidence":["dominant period from FFT"]},{"tool":"value_at_index","reason":"Retrieves specific amplitude values at various points to evaluate amplitude variability.","supports_evidence":["variations in amplitude over cycle lengths"]}],"no_tool_decision":null},"reasoning":"The objective is to detect recurring patterns, cycles, and intermediate structures in the medium-scale context. Required measurements include seasonal patterns, cycle lengths, and amplitude variabilities. Validation ensures these cyclic patterns are consistent over time."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- value_at_index
  inputs: series_index, start, end, index, index_base
  outputs: series
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
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to find the dominant period in the time series to identify potential cycle lengths. Then, we employ 'seas_acf' with the determined period as the lag to assess seasonal autocorrelation, supporting the claim about seasonal patterns.",
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
      "output_key": "seas_acf1",
      "input_binding": {"lag": "$step1.dominant_period"}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=983 completion=152 latency=5.48s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{"lag":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to find the dominant period in the time series to identify potential cycle lengths. Then, we employ 'seas_acf' with the determined period as the lag to assess seasonal autocorrelation, supporting the claim about seasonal patterns."}
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
- seas_acf: MMTS seas_acf1: seasonal autocorrelation ρ_m=γ_m/γ_0 at lag m (e.g. lag=26 for weekly half-year frequency).
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, lag=required seasonal lag m (aliases: m, frequency, period)}
  returns: {series=seas_acf1 at lag m with strength_hint}
- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to find the dominant period in the time series to identify potential cycle lengths. Then, we employ 'seas_acf' with the determined period as the lag to assess seasonal autocorrelation, supporting the claim about seasonal patterns.",
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

tokens prompt=1232 completion=482 latency=17.16s

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
{"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"The time series exhibits a clear seasonal pattern.","required_evidence":["seasonal autocorrelation at known lags"]},{"claim":"There are identifiable cycle lengths present.","required_evidence":["dominant period from FFT"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["variations in amplitude over cycle lengths"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verify cyclic patterns are consistent over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at known lags to support the detection of seasonal patterns.","supports_evidence":["seasonal autocorrelation at known lags"]},{"tool":"fft_period","reason":"Finds dominant period via FFT to identify cycle lengths.","supports_evidence":["dominant period from FFT"]},{"tool":"value_at_index","reason":"Retrieves specific amplitude values at various points to evaluate amplitude variability.","supports_evidence":["variations in amplitude over cycle lengths"]}],"no_tool_decision":null},"reasoning":"The objective is to detect recurring patterns, cycles, and intermediate structures in the medium-scale context. Required measurements include seasonal patterns, cycle lengths, and amplitude variabilities. Validation ensures these cyclic patterns are consistent over time."}
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
      "dominant_period": 24.0,
      "spectral_strength": 0.07828587508312988,
      "period_trusted": true,
      "warnings": []
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
      "lag": 24.0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "lag": 24,
      "seas_acf1": 0.6221341620165426,
      "strength_hint": "strong",
      "metric_definition": "ρ_m=γ_m/γ_0 (MMTS seas_acf1)"
    },
    "error": null,
    "args_fingerprint": "719c9194ac84c70646b652980711833b9d1b2003"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective was to detect recurring patterns, cycles, and intermediate structures in the given time series. Tools were successfully used to measure the seasonal autocorrelation and dominant period. The seasonal autocorrelation shows a strong seasonality, indicating a clear seasonal pattern, while the dominant period identified is 24, suggesting daily cycles. However, evidence for amplitude variability over different cycles is still unresolved.",
  "scale": "medium",
  "observations": ["The time series exhibits a clear seasonal pattern as indicated by the strong seasonal autocorrelation.", "A dominant cycle length of 24 hours is identified, suggesting daily cycles.", "Further investigation is needed to confirm amplitude variability over different cycles."],
  "evidence_intervals": ["N/A"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The time series exhibits a clear seasonal pattern.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.6221341620165426,
          "source_tool": "seas_acf",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "seasonal_pattern"
    },
    {
      "claim": "There are identifiable cycle lengths present.",
      "evidence": [
        {
          "type": "dominant_cycle_length",
          "value": 24.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "cycle_length"
    },
    {
      "claim": "Amplitude variability is evident over different cycles.",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "amplitude_variability"
    }
  ],
  "coverage": {"seasonal_pattern": "tool_supported", "cycle_length": "tool_supported", "amplitude_variability": "unresolved"},
  "unresolved_claims": ["Amplitude variability is evident over different cycles."]
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m1`

tokens prompt=4100 completion=331 latency=12.95s

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
{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.","task_summary":"Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.","target_output":"description","answer_type":"choice","capability":"alignment","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short","medium"],"heterogeneous_agents":["alignment"],"success_criteria":["correctly identifies key characteristics of the series"],"notes":"Ensure all characteristics are reconciled before making a final selection."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
retry_context=unresolved_claims=['Amplitude variability is evident over different cycles.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect recurring patterns, cycles, and intermediate structures in the medium-scale context. Required measurements include seasonal patterns, cycle length, and amplitude variability, with validation focusing on ensuring these cyclic patterns are consistent over time.",
  "evidence_plan": {
    "objective": "Detect recurring patterns, cycles, and intermediate structures.",
    "claims_to_support": [
      {"claim": "Seasonal pattern exists.", "required_evidence": ["seasonal_pattern"]},
      {"claim": "Cycle length can be determined.", "required_evidence": ["cycle_length"]},
      {"claim": "Amplitude variability is evident over different cycles.", "required_evidence": ["amplitude_variability"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["seasonal_pattern consistency over time"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "seas_acf", "reason": "Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.", "supports_evidence": ["seasonal_pattern"]},
      {"tool": "fft_period", "reason": "Determines dominant period to support evidence for cycle length.", "supports_evidence": ["cycle_length"]},
      {"tool": "noise_decomposition", "reason": "Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.", "supports_evidence": ["amplitude_variability"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m1`

tokens prompt=855 completion=210 latency=7.48s

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
{"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["seasonal_pattern consistency over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.","supports_evidence":["seasonal_pattern"]},{"tool":"fft_period","reason":"Determines dominant period to support evidence for cycle length.","supports_evidence":["cycle_length"]},{"tool":"noise_decomposition","reason":"Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.","supports_evidence":["amplitude_variability"]}],"no_tool_decision":null},"reasoning":"The objective is to detect recurring patterns, cycles, and intermediate structures in the medium-scale context. Required measurements include seasonal patterns, cycle length, and amplitude variability, with validation focusing on ensuring these cyclic patterns are consistent over time."}
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
- noise_decomposition
  inputs: series, period(optional)
  outputs: noise_ratio, noise_level, noise_type_hint
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations.",
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
    },
    {
      "step": 3,
      "tool": "noise_decomposition",
      "output_key": "noise_level",
      "input_binding": {"period": "$step1.dominant_period"}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m1`

tokens prompt=1056 completion=213 latency=7.64s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_level","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations."}
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
- noise_decomposition: MMTS-style residual noise strength: Var(residual)/Var(series) after STL (conservative vs high-pass), with bins none/low/medium/high at 0.1/0.33/0.66 and a heuristic noise_type_hint.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, period=optional int}
  returns: {series=noise_ratio=Var(resid)/Var(series), noise_level bins none/low/medium/high, type hint}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations.",
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
    },
    {
      "step": 3,
      "tool": "noise_decomposition",
      "args": {
        "series_index": 1,
        "period": "$step1.dominant_period"
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m1`

tokens prompt=1753 completion=552 latency=19.95s

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
{"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["seasonal_pattern consistency over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.","supports_evidence":["seasonal_pattern"]},{"tool":"fft_period","reason":"Determines dominant period to support evidence for cycle length.","supports_evidence":["cycle_length"]},{"tool":"noise_decomposition","reason":"Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.","supports_evidence":["amplitude_variability"]}],"no_tool_decision":null},"reasoning":"The objective is to detect recurring patterns, cycles, and intermediate structures in the medium-scale context. Required measurements include seasonal patterns, cycle length, and amplitude variability, with validation focusing on ensuring these cyclic patterns are consistent over time."}
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
      "dominant_period": 24.0,
      "spectral_strength": 0.07828587508312988,
      "period_trusted": true,
      "warnings": []
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
      "lag": 24.0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "lag": 24,
      "seas_acf1": 0.6221341620165426,
      "strength_hint": "strong",
      "metric_definition": "ρ_m=γ_m/γ_0 (MMTS seas_acf1)"
    },
    "error": null,
    "args_fingerprint": "719c9194ac84c70646b652980711833b9d1b2003"
  },
  {
    "call_id": "medium:step3",
    "step": 3,
    "tool_name": "noise_decomposition",
    "arguments": {
      "series_index": 1,
      "period": "$step1.dominant_period"
    },
    "resolved_arguments": {
      "series_index": 1,
      "period": 24.0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "period": 24,
      "residual_std": 2.4391051338422796,
      "residual_rmse": 2.4500078262611216,
      "series_std": 4.6428487609279205,
      "residual_var": 5.949233853935763,
      "series_var": 21.556044616849924,
      "stl_noise_ratio": 0.2759891232218499,
      "highpass_noise_ratio": 0.7462237732864964,
      "noise_ratio": 0.7462237732864964,
      "noise_level": "high",
      "metric_definition": "Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high",
      "estimator": "STL_residual_variance_ratio",
      "seasonal_strength": 0.7138646424006991,
      "trend_strength": 0.07908771069719633,
      "noise_type_hint": "uniform_like",
      "acf_lag1": 0.8395141359811984,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "47a883230742f4cbb4f0165dcae85330e8c37e27"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate strong seasonal patterns with a dominant period of 24, consistent spectral strength, and moderate-to-strong seasonal and trend components, implying recurring patterns and cycles. Residual variability suggests amplitude changes across cycles.",
  "scale": "medium",
  "observations": ["Strong seasonal pattern identified.", "Dominant cycle length detected as 24 units.", "Residual variance indicates amplitude variability over cycles."],
  "evidence_intervals": ["[null, null]"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Seasonal pattern exists.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.7138646424006991,
          "source_tool": "noise_decomposition",
          "call_id": "medium:step3",
          "provenance": "tool"
        },
        {
          "type": "seas_acf_strength",
          "value": 0.6221341620165426,
          "source_tool": "seas_acf",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "seasonal_pattern"
    },
    {
      "claim": "Cycle length can be determined.",
      "evidence": [
        {
          "type": "dominant_period",
          "value": 24.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "cycle_length"
    },
    {
      "claim": "Amplitude variability is evident over different cycles.",
      "evidence": [
        {
          "type": "noise_ratio",
          "value": 0.7462237732864964,
          "source_tool": "noise_decomposition",
          "call_id": "medium:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "amplitude_variability"
    }
  ],
  "coverage": {"seasonal_pattern": "tool_supported", "cycle_length": "tool_supported", "amplitude_variability": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (alignment, s1s2) — `heterogeneous:alignment:s1s2:m0`

tokens prompt=12452 completion=703 latency=31.84s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=alignment.
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
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  produces: distances, nearest, method
  use_when: One query series must be ranked against multiple candidate series.
  avoid_when: Reverse, subsequence, or robust-outlier matching semantics are required.
  limitations: Distance meaning depends on normalization/method; unequal lengths may be truncated.
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
- caption_verify: Verify structured caption claims against one or more candidate series and rank candidates by passed claims. Supports trend, period, levels/runs, extrema, volatility, anomaly, stationarity, value_band, spike, zero_gap, peak_at, drop_magnitude, high_freq, reaching_up_to, and basic stats.
  produces: candidates, best_match
  use_when: Explicit numeric/structural claims from a caption must be checked against candidates.
  avoid_when: The caption requires open-ended semantics not representable as supported claim types.
  limitations: Structured claim checker, not free-form language understanding.; Supports trend/period/levels/extrema/volatility/anomaly/stationarity/value_band/spike/zero_gap/peak_at/drop_magnitude/high_freq/reaching_up_to.

Output ONLY JSON (EvidenceCapabilityPlan):
{
  "reasoning": "string",
  "evidence_plan": {
    "objective": "string",
    "claims_to_support": [
      {"claim": "string", "required_evidence": ["string"]}
    ],
    "analysis_scope": {"target_series": [1], "role": "alignment"},
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
{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.","task_summary":"Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.","target_output":"description","answer_type":"choice","capability":"alignment","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short","medium"],"heterogeneous_agents":["alignment"],"success_criteria":["correctly identifies key characteristics of the series"],"notes":"Ensure all characteristics are reconciled before making a final selection."}
</plan_context>

<task_summary>
Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps include 'diff_stats' for detecting changes and roughness in the series, which helps in identifying abrupt changes, and 'anomaly_detect' for detecting spikes/outliers, necessary for measuring spike heights and anomaly counts.","scale":"short","observations":["Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series."],"evidence_intervals":["[start of series, end of series]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.07390243902439027, \"std_diff\": 2.602568303513662, \"max_abs_diff\": 14.36, \"n_sign_changes\": 56}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 10, \"anomaly_indices\": [0, 1, 24, 25, 145, 168, 169, 192, 193, 240], \"max_abs_z\": 4.643289365615513}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","claims_to_support":[{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["cross-validate against medium-scale analysis for robustness"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Detects changes and roughness in the series, useful for identifying abrupt changes.","supports_evidence":["change_locations"]},{"tool":"anomaly_detect","reason":"Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.","supports_evidence":["spike_heights","anomaly_counts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_locations","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_counts","input_binding":{}}],"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations and anomaly counts using the diff_stats and anomaly_detect tools."},"structured_observations":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"coverage":{"change_locations":"tool_supported","spike_heights":"tool_supported","anomaly_counts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.07390243902439027,"std_diff":2.602568303513662,"max_abs_diff":14.36,"n_sign_changes":56},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":10,"anomaly_indices":[0,1,24,25,145,168,169,192,193,240],"max_abs_z":4.643289365615513},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate strong seasonal patterns with a dominant period of 24, consistent spectral strength, and moderate-to-strong seasonal and trend components, implying recurring patterns and cycles. Residual variability suggests amplitude changes across cycles.","scale":"medium","observations":["Strong seasonal pattern identified.","Dominant cycle length detected as 24 units.","Residual variance indicates amplitude variability over cycles."],"evidence_intervals":["[null, null]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.07828587508312988, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 24, \"seas_acf1\": 0.6221341620165426, \"strength_hint\": \"strong\", \"metric_definition\": \"ρ_m=γ_m/γ_0 (MMTS seas_acf1)\"}, \"error\": null, \"args_fingerprint\": \"719c9194ac84c70646b652980711833b9d1b2003\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 24, \"residual_std\": 2.4391051338422796, \"residual_rmse\": 2.4500078262611216, \"series_std\": 4.6428487609279205, \"residual_var\": 5.949233853935763, \"series_var\": 21.556044616849924, \"stl_noise_ratio\": 0.2759891232218499, \"highpass_noise_ratio\": 0.7462237732864964, \"noise_ratio\": 0.7462237732864964, \"noise_level\": \"high\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.7138646424006991, \"trend_strength\": 0.07908771069719633, \"noise_type_hint\": \"uniform_like\", \"acf_lag1\": 0.8395141359811984, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"47a883230742f4cbb4f0165dcae85330e8c37e27\"}"],"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["seasonal_pattern consistency over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.","supports_evidence":["seasonal_pattern"]},{"tool":"fft_period","reason":"Determines dominant period to support evidence for cycle length.","supports_evidence":["cycle_length"]},{"tool":"noise_decomposition","reason":"Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.","supports_evidence":["amplitude_variability"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_level","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations."},"structured_observations":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}],"coverage":{"seasonal_pattern":"tool_supported","cycle_length":"tool_supported","amplitude_variability":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.07828587508312988,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":24,"seas_acf1":0.6221341620165426,"strength_hint":"strong","metric_definition":"ρ_m=γ_m/γ_0 (MMTS seas_acf1)"},"error":null,"args_fingerprint":"719c9194ac84c70646b652980711833b9d1b2003"},{"call_id":"medium:step3","step":3,"tool_name":"noise_decomposition","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":24,"residual_std":2.4391051338422796,"residual_rmse":2.4500078262611216,"series_std":4.6428487609279205,"residual_var":5.949233853935763,"series_var":21.556044616849924,"stl_noise_ratio":0.2759891232218499,"highpass_noise_ratio":0.7462237732864964,"noise_ratio":0.7462237732864964,"noise_level":"high","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.7138646424006991,"trend_strength":0.07908771069719633,"noise_type_hint":"uniform_like","acf_lag1":0.8395141359811984,"warnings":[]},"error":null,"args_fingerprint":"47a883230742f4cbb4f0165dcae85330e8c37e27"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend assessment and identification of significant level shifts in the series. Tools were used to provide an initial overview of the series and further detail on its trend and level shifts.","scale":"long","observations":["The series exhibits a downward trend with a negative slope.","Multiple discrete step or plateau levels suggest numerous level shifts within the series."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"min\": 0.0, \"max\": 26.36, \"median\": 4.725, \"range\": 26.36, \"p50\": 4.725, \"p90\": 7.593000000000003, \"p99\": 22.423199999999998, \"start\": 22.34, \"end\": 1.13, \"slope\": -0.07390243902439024}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.07390243902439024, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"start_value\": 22.34, \"end_value\": 1.13}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 40, \"n_plateau_runs\": 199, \"levels\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 10.24, 22.98, 8.97, 4.12, 1.05, 3.51, 0.69, 7.96, 9.56, 1.64, 2.88, 4.98, 5.64, 4.39, 17.56, 19.54, 11.72, 20.76, 21.11, 12.0, 26.244999999999997, 16.62, 7.53, 13.09, 13.43, 18.67], \"plateau_runs\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 6.5, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 6.08, 10.24, 22.98, 20.32, 8.97, 6.75, 7.22, 6.35, 5.952500000000001, 6.65, 5.29, 4.12, 3.16, 2.19, 0.52, 0.0025, 1.05, 6.26, 5.984999999999999, 6.8, 5.14, 3.91, 3.51, 3.21, 2.16, 0.69, 0.025, 2.24, 5.77, 7.96, 9.56, 8.27, 7.27, 6.6, 6.96, 6.064, 5.11, 4.19, 3.415, 2.53, 1.64, 0.076, 1.87, 2.88, 3.8, 4.98, 5.64, 6.1, 6.91, 6.39, 6.993333333333333, 6.38, 5.45, 4.12, 4.39, 4.01, 3.09, 1.98, 0.73, 0.0275, 1.2, 1.74, 2.3, 3.13, 4.9], \"plateau_lengths\": [1, 1, 1, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 2, 1, 1, 12, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 2, 1, 5, 1, 1, 2, 1, 1, 5, 1, 1, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1], \"tolerance\": 0.2636}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Assess global trends and major structural shifts across the entire series.","claims_to_support":[{"claim":"There exists a global trend in the series.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview including slope, which indicates the overall trend.","supports_evidence":["global_trend"]},{"tool":"segment_trend","reason":"Analyzes directional trend over specified segments to confirm consistency across the series.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts discrete step or plateau levels which can indicate significant level shifts.","supports_evidence":["level_shift_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"initial_statistical_summary","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_consistency_across_segments","input_binding":{}},{"step":3,"tool":"step_levels","output_key":"count_of_significant_level_shifts","input_binding":{}}],"reasoning":"The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required."},"structured_observations":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"coverage":{"global_trend":"tool_supported","level_shift_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":4.801909722222223,"std":4.6428487609279205,"min":0.0,"max":26.36,"median":4.725,"range":26.36,"p50":4.725,"p90":7.593000000000003,"p99":22.423199999999998,"start":22.34,"end":1.13,"slope":-0.07390243902439024}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.07390243902439024,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.801909722222223,"std":4.6428487609279205,"start_value":22.34,"end_value":1.13},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step3","step":3,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":40,"n_plateau_runs":199,"levels":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,10.24,22.98,8.97,4.12,1.05,3.51,0.69,7.96,9.56,1.64,2.88,4.98,5.64,4.39,17.56,19.54,11.72,20.76,21.11,12.0,26.244999999999997,16.62,7.53,13.09,13.43,18.67],"plateau_runs":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,6.5,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,6.08,10.24,22.98,20.32,8.97,6.75,7.22,6.35,5.952500000000001,6.65,5.29,4.12,3.16,2.19,0.52,0.0025,1.05,6.26,5.984999999999999,6.8,5.14,3.91,3.51,3.21,2.16,0.69,0.025,2.24,5.77,7.96,9.56,8.27,7.27,6.6,6.96,6.064,5.11,4.19,3.415,2.53,1.64,0.076,1.87,2.88,3.8,4.98,5.64,6.1,6.91,6.39,6.993333333333333,6.38,5.45,4.12,4.39,4.01,3.09,1.98,0.73,0.0275,1.2,1.74,2.3,3.13,4.9],"plateau_lengths":[1,1,1,1,1,3,2,1,1,1,2,1,1,4,1,1,1,1,1,1,1,1,1,4,1,1,1,2,1,1,12,1,2,2,1,1,1,1,1,1,1,4,1,1,1,1,1,1,2,1,5,1,1,2,1,1,5,1,1,1,1,1,1,2,1,3,1,1,1,1,1,1,1,1,4,1,1,1,1,1],"tolerance":0.2636},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The series exhibits a downward trend with a negative slope. Multiple discrete step or plateau levels suggest numerous level shifts within the series. Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series. Strong seasonal pattern identified. Dominant cycle length detected as 24 units. Residual variance indicates amplitude variability over cycles.","structured_by_scale":{"long":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"short":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"medium":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) This series remains essentially flat at zero throughout most of its duration, with only one minor spike occurring around index 64, representing an almost entirely inactive signal.
B) This series displays irregular oscillations with multiple peaks of different heights, ranging from near-zero to approximately 19, with sporadic spikes and extended periods of low values.
C) This time series shows high variability with values fluctuating between approximately 7 and 100, featuring several dramatic drops and recoveries, creating a volatile pattern with significant amplitude changes.
D) This time series exhibits periodic patterns with sharp peaks reaching around 20-26 and valleys dropping near zero, showing cyclical behavior with varying amplitudes throughout the sequence.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=alignment.

```

### OUTPUT

```
{
  "reasoning": "The task requires matching the time series characteristics described in the temporal profile and metadata against the given candidate descriptions. Based on the evidence already provided, we can identify the relevant features such as global trend, level shift count, change locations, spike heights, anomaly counts, seasonal pattern, cycle length, and amplitude variability.",
  "evidence_plan": {
    "objective": "Match identified time series characteristics with the most fitting description among the candidates.",
    "claims_to_support": [
      {
        "claim": "The series has a negative global trend.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "There are significant level shifts in the series.",
        "required_evidence": ["level_shift_count"]
      },
      {
        "claim": "Specific instances of abrupt changes are accurately identified.",
        "required_evidence": ["change_locations"]
      },
      {
        "claim": "Spike heights are correctly measured.",
        "required_evidence": ["spike_heights"]
      },
      {
        "claim": "Anomaly counts are precisely determined.",
        "required_evidence": ["anomaly_counts"]
      },
      {
        "claim": "A strong seasonal pattern exists.",
        "required_evidence": ["seasonal_pattern"]
      },
      {
        "claim": "The cycle length can be determined.",
        "required_evidence": ["cycle_length"]
      },
      {
        "claim": "Amplitude variability is evident over different cycles.",
        "required_evidence": ["amplitude_variability"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "alignment"
    },
    "validation_needs": [
      "cross-reference findings with multiple scales to ensure coherent interpretation",
      "verify consistency across multiple sections of the series"
    ]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All required evidence is provided by upstream observations.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_trend"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step3",
          "field": "level_shift_count"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step1",
          "field": "change_locations"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step2",
          "field": "spike_heights"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step2",
          "field": "anomaly_counts"
        },
        {
          "type": "upstream_observation",
          "ref": "medium:step2",
          "field": "seasonal_pattern"
        },
        {
          "type": "upstream_observation",
          "ref": "medium:step1",
          "field": "cycle_length"
        },
        {
          "type": "upstream_observation",
          "ref": "medium:step3",
          "field": "amplitude_variability"
        }
      ]
    }
  }
}
```

## Heterogeneous (alignment, s5) — `heterogeneous:alignment:s5:m0`

tokens prompt=9958 completion=1024 latency=42.88s

### INPUT (system)

```
You are a Heterogeneous Agent (role=alignment) at Stage 5: Evidence Integration.
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
  "role": "alignment",
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
{"evidence_plan":{"objective":"Match identified time series characteristics with the most fitting description among the candidates.","claims_to_support":[{"claim":"The series has a negative global trend.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]},{"claim":"Specific instances of abrupt changes are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]},{"claim":"A strong seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"The cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"role":"alignment"},"validation_needs":["cross-reference findings with multiple scales to ensure coherent interpretation","verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All required evidence is provided by upstream observations.","evidence_sources":[{"type":"upstream_observation","ref":"long:step1","field":"global_trend"},{"type":"upstream_observation","ref":"long:step3","field":"level_shift_count"},{"type":"upstream_observation","ref":"short:step1","field":"change_locations"},{"type":"upstream_observation","ref":"short:step2","field":"spike_heights"},{"type":"upstream_observation","ref":"short:step2","field":"anomaly_counts"},{"type":"upstream_observation","ref":"medium:step2","field":"seasonal_pattern"},{"type":"upstream_observation","ref":"medium:step1","field":"cycle_length"},{"type":"upstream_observation","ref":"medium:step3","field":"amplitude_variability"}]}},"reasoning":"The task requires matching the time series characteristics described in the temporal profile and metadata against the given candidate descriptions. Based on the evidence already provided, we can identify the relevant features such as global trend, level shift count, change locations, spike heights, anomaly counts, seasonal pattern, cycle length, and amplitude variability."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps include 'diff_stats' for detecting changes and roughness in the series, which helps in identifying abrupt changes, and 'anomaly_detect' for detecting spikes/outliers, necessary for measuring spike heights and anomaly counts.","scale":"short","observations":["Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series."],"evidence_intervals":["[start of series, end of series]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.07390243902439027, \"std_diff\": 2.602568303513662, \"max_abs_diff\": 14.36, \"n_sign_changes\": 56}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 10, \"anomaly_indices\": [0, 1, 24, 25, 145, 168, 169, 192, 193, 240], \"max_abs_z\": 4.643289365615513}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","claims_to_support":[{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["cross-validate against medium-scale analysis for robustness"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Detects changes and roughness in the series, useful for identifying abrupt changes.","supports_evidence":["change_locations"]},{"tool":"anomaly_detect","reason":"Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.","supports_evidence":["spike_heights","anomaly_counts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_locations","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_counts","input_binding":{}}],"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations and anomaly counts using the diff_stats and anomaly_detect tools."},"structured_observations":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"coverage":{"change_locations":"tool_supported","spike_heights":"tool_supported","anomaly_counts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.07390243902439027,"std_diff":2.602568303513662,"max_abs_diff":14.36,"n_sign_changes":56},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":10,"anomaly_indices":[0,1,24,25,145,168,169,192,193,240],"max_abs_z":4.643289365615513},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate strong seasonal patterns with a dominant period of 24, consistent spectral strength, and moderate-to-strong seasonal and trend components, implying recurring patterns and cycles. Residual variability suggests amplitude changes across cycles.","scale":"medium","observations":["Strong seasonal pattern identified.","Dominant cycle length detected as 24 units.","Residual variance indicates amplitude variability over cycles."],"evidence_intervals":["[null, null]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.07828587508312988, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 24, \"seas_acf1\": 0.6221341620165426, \"strength_hint\": \"strong\", \"metric_definition\": \"ρ_m=γ_m/γ_0 (MMTS seas_acf1)\"}, \"error\": null, \"args_fingerprint\": \"719c9194ac84c70646b652980711833b9d1b2003\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 24, \"residual_std\": 2.4391051338422796, \"residual_rmse\": 2.4500078262611216, \"series_std\": 4.6428487609279205, \"residual_var\": 5.949233853935763, \"series_var\": 21.556044616849924, \"stl_noise_ratio\": 0.2759891232218499, \"highpass_noise_ratio\": 0.7462237732864964, \"noise_ratio\": 0.7462237732864964, \"noise_level\": \"high\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.7138646424006991, \"trend_strength\": 0.07908771069719633, \"noise_type_hint\": \"uniform_like\", \"acf_lag1\": 0.8395141359811984, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"47a883230742f4cbb4f0165dcae85330e8c37e27\"}"],"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["seasonal_pattern consistency over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.","supports_evidence":["seasonal_pattern"]},{"tool":"fft_period","reason":"Determines dominant period to support evidence for cycle length.","supports_evidence":["cycle_length"]},{"tool":"noise_decomposition","reason":"Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.","supports_evidence":["amplitude_variability"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_level","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations."},"structured_observations":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}],"coverage":{"seasonal_pattern":"tool_supported","cycle_length":"tool_supported","amplitude_variability":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.07828587508312988,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":24,"seas_acf1":0.6221341620165426,"strength_hint":"strong","metric_definition":"ρ_m=γ_m/γ_0 (MMTS seas_acf1)"},"error":null,"args_fingerprint":"719c9194ac84c70646b652980711833b9d1b2003"},{"call_id":"medium:step3","step":3,"tool_name":"noise_decomposition","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":24,"residual_std":2.4391051338422796,"residual_rmse":2.4500078262611216,"series_std":4.6428487609279205,"residual_var":5.949233853935763,"series_var":21.556044616849924,"stl_noise_ratio":0.2759891232218499,"highpass_noise_ratio":0.7462237732864964,"noise_ratio":0.7462237732864964,"noise_level":"high","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.7138646424006991,"trend_strength":0.07908771069719633,"noise_type_hint":"uniform_like","acf_lag1":0.8395141359811984,"warnings":[]},"error":null,"args_fingerprint":"47a883230742f4cbb4f0165dcae85330e8c37e27"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend assessment and identification of significant level shifts in the series. Tools were used to provide an initial overview of the series and further detail on its trend and level shifts.","scale":"long","observations":["The series exhibits a downward trend with a negative slope.","Multiple discrete step or plateau levels suggest numerous level shifts within the series."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"min\": 0.0, \"max\": 26.36, \"median\": 4.725, \"range\": 26.36, \"p50\": 4.725, \"p90\": 7.593000000000003, \"p99\": 22.423199999999998, \"start\": 22.34, \"end\": 1.13, \"slope\": -0.07390243902439024}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.07390243902439024, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"start_value\": 22.34, \"end_value\": 1.13}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 40, \"n_plateau_runs\": 199, \"levels\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 10.24, 22.98, 8.97, 4.12, 1.05, 3.51, 0.69, 7.96, 9.56, 1.64, 2.88, 4.98, 5.64, 4.39, 17.56, 19.54, 11.72, 20.76, 21.11, 12.0, 26.244999999999997, 16.62, 7.53, 13.09, 13.43, 18.67], \"plateau_runs\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 6.5, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 6.08, 10.24, 22.98, 20.32, 8.97, 6.75, 7.22, 6.35, 5.952500000000001, 6.65, 5.29, 4.12, 3.16, 2.19, 0.52, 0.0025, 1.05, 6.26, 5.984999999999999, 6.8, 5.14, 3.91, 3.51, 3.21, 2.16, 0.69, 0.025, 2.24, 5.77, 7.96, 9.56, 8.27, 7.27, 6.6, 6.96, 6.064, 5.11, 4.19, 3.415, 2.53, 1.64, 0.076, 1.87, 2.88, 3.8, 4.98, 5.64, 6.1, 6.91, 6.39, 6.993333333333333, 6.38, 5.45, 4.12, 4.39, 4.01, 3.09, 1.98, 0.73, 0.0275, 1.2, 1.74, 2.3, 3.13, 4.9], \"plateau_lengths\": [1, 1, 1, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 2, 1, 1, 12, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 2, 1, 5, 1, 1, 2, 1, 1, 5, 1, 1, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1], \"tolerance\": 0.2636}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Assess global trends and major structural shifts across the entire series.","claims_to_support":[{"claim":"There exists a global trend in the series.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview including slope, which indicates the overall trend.","supports_evidence":["global_trend"]},{"tool":"segment_trend","reason":"Analyzes directional trend over specified segments to confirm consistency across the series.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts discrete step or plateau levels which can indicate significant level shifts.","supports_evidence":["level_shift_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"initial_statistical_summary","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_consistency_across_segments","input_binding":{}},{"step":3,"tool":"step_levels","output_key":"count_of_significant_level_shifts","input_binding":{}}],"reasoning":"The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required."},"structured_observations":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"coverage":{"global_trend":"tool_supported","level_shift_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":4.801909722222223,"std":4.6428487609279205,"min":0.0,"max":26.36,"median":4.725,"range":26.36,"p50":4.725,"p90":7.593000000000003,"p99":22.423199999999998,"start":22.34,"end":1.13,"slope":-0.07390243902439024}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.07390243902439024,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.801909722222223,"std":4.6428487609279205,"start_value":22.34,"end_value":1.13},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step3","step":3,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":40,"n_plateau_runs":199,"levels":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,10.24,22.98,8.97,4.12,1.05,3.51,0.69,7.96,9.56,1.64,2.88,4.98,5.64,4.39,17.56,19.54,11.72,20.76,21.11,12.0,26.244999999999997,16.62,7.53,13.09,13.43,18.67],"plateau_runs":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,6.5,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,6.08,10.24,22.98,20.32,8.97,6.75,7.22,6.35,5.952500000000001,6.65,5.29,4.12,3.16,2.19,0.52,0.0025,1.05,6.26,5.984999999999999,6.8,5.14,3.91,3.51,3.21,2.16,0.69,0.025,2.24,5.77,7.96,9.56,8.27,7.27,6.6,6.96,6.064,5.11,4.19,3.415,2.53,1.64,0.076,1.87,2.88,3.8,4.98,5.64,6.1,6.91,6.39,6.993333333333333,6.38,5.45,4.12,4.39,4.01,3.09,1.98,0.73,0.0275,1.2,1.74,2.3,3.13,4.9],"plateau_lengths":[1,1,1,1,1,3,2,1,1,1,2,1,1,4,1,1,1,1,1,1,1,1,1,4,1,1,1,2,1,1,12,1,2,2,1,1,1,1,1,1,1,4,1,1,1,1,1,1,2,1,5,1,1,2,1,1,5,1,1,1,1,1,1,2,1,3,1,1,1,1,1,1,1,1,4,1,1,1,1,1],"tolerance":0.2636},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The series exhibits a downward trend with a negative slope. Multiple discrete step or plateau levels suggest numerous level shifts within the series. Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series. Strong seasonal pattern identified. Dominant cycle length detected as 24 units. Residual variance indicates amplitude variability over cycles.","structured_by_scale":{"long":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"short":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"medium":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}]}}
</temporal_profile>

<assignment>
{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) This series remains essentially flat at zero throughout most of its duration, with only one minor spike occurring around index 64, representing an almost entirely inactive signal.
B) This series displays irregular oscillations with multiple peaks of different heights, ranging from near-zero to approximately 19, with sporadic spikes and extended periods of low values.
C) This time series shows high variability with values fluctuating between approximately 7 and 100, featuring several dramatic drops and recoveries, creating a volatile pattern with significant amplitude changes.
D) This time series exhibits periodic patterns with sharp peaks reaching around 20-26 and valleys dropping near zero, showing cyclical behavior with varying amplitudes throughout the sequence.
</candidates>

Produce the TaskEvidence JSON for role=alignment.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the series exhibits a downward trend, significant level shifts, multiple abrupt changes, anomalies, strong seasonal patterns with a dominant cycle length of 24 units, and amplitude variability.",
  "role": "alignment",
  "hypothesis": "Option D best matches the identified time series characteristics due to the presence of periodic patterns with sharp peaks and valleys indicating varying amplitudes over cycles.",
  "evidence": [
    "A strong downward global trend is present, with a negative slope (-0.0739).",
    "There are 40 distinct levels suggesting significant level shifts.",
    "56 sign changes identified, indicating multiple abrupt changes.",
    "10 anomalies have been detected within the series.",
    "Strong seasonal pattern exists, with a dominant cycle length of 24 units.",
    "High amplitude variability across different cycles."
  ],
  "candidate_preference": "D",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "long:step1",
    "long:step2",
    "long:step3",
    "short:step1",
    "short:step2",
    "medium:step1",
    "medium:step2",
    "medium:step3"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The series has a negative global trend.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.07390243902439024,
          "provenance": "upstream",
          "ref": "long:step1",
          "call_id": "long:step1"
        },
        {
          "type": "global_trend",
          "value": -0.07390243902439024,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are significant level shifts in the series.",
      "evidence": [
        {
          "type": "level_shift_count",
          "value": 40,
          "provenance": "upstream",
          "ref": "long:step3",
          "call_id": "long:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Specific instances of abrupt changes are accurately identified.",
      "evidence": [
        {
          "type": "change_locations",
          "value": 56,
          "provenance": "upstream",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Spike heights are correctly measured.",
      "evidence": [
        {
          "type": "spike_heights",
          "value": 4.643289365615513,
          "provenance": "upstream",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Anomaly counts are precisely determined.",
      "evidence": [
        {
          "type": "anomaly_counts",
          "value": 10,
          "provenance": "upstream",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "A strong seasonal pattern exists.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.7138646424006991,
          "provenance": "upstream",
          "ref": "medium:step3",
          "call_id": "medium:step3"
        },
        {
          "type": "seas_acf_strength",
          "value": 0.6221341620165426,
          "provenance": "upstream",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The cycle length can be determined.",
      "evidence": [
        {
          "type": "dom
```

## Heterogeneous (alignment, s1s2) — `heterogeneous:alignment:s1s2:m1`

tokens prompt=12463 completion=603 latency=27.73s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=alignment.
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
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  produces: distances, nearest, method
  use_when: One query series must be ranked against multiple candidate series.
  avoid_when: Reverse, subsequence, or robust-outlier matching semantics are required.
  limitations: Distance meaning depends on normalization/method; unequal lengths may be truncated.
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
- caption_verify: Verify structured caption claims against one or more candidate series and rank candidates by passed claims. Supports trend, period, levels/runs, extrema, volatility, anomaly, stationarity, value_band, spike, zero_gap, peak_at, drop_magnitude, high_freq, reaching_up_to, and basic stats.
  produces: candidates, best_match
  use_when: Explicit numeric/structural claims from a caption must be checked against candidates.
  avoid_when: The caption requires open-ended semantics not representable as supported claim types.
  limitations: Structured claim checker, not free-form language understanding.; Supports trend/period/levels/extrema/volatility/anomaly/stationarity/value_band/spike/zero_gap/peak_at/drop_magnitude/high_freq/reaching_up_to.

Output ONLY JSON (EvidenceCapabilityPlan):
{
  "reasoning": "string",
  "evidence_plan": {
    "objective": "string",
    "claims_to_support": [
      {"claim": "string", "required_evidence": ["string"]}
    ],
    "analysis_scope": {"target_series": [1], "role": "alignment"},
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
{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the correct description of the time series based on its visual or numerical characteristics. The descriptions vary widely, suggesting we need to identify key features such as flatness, irregularity, volatility, and periodicity.","task_summary":"Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.","target_output":"description","answer_type":"choice","capability":"alignment","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Assess global trends and major structural shifts across the entire series.","required_measurements":["global_trend","level_shift_count"],"validation_requirements":["verify consistency across multiple sections of the series"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","required_measurements":["change_locations","spike_heights","anomaly_counts"],"validation_requirements":["cross-validate against medium-scale analysis for robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect recurring patterns, cycles, and intermediate structures.","required_measurements":["seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["ensure cyclic patterns are consistent over time"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short","medium"],"heterogeneous_agents":["alignment"],"success_criteria":["correctly identifies key characteristics of the series"],"notes":"Ensure all characteristics are reconciled before making a final selection."}
</plan_context>

<task_summary>
Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps include 'diff_stats' for detecting changes and roughness in the series, which helps in identifying abrupt changes, and 'anomaly_detect' for detecting spikes/outliers, necessary for measuring spike heights and anomaly counts.","scale":"short","observations":["Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series."],"evidence_intervals":["[start of series, end of series]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.07390243902439027, \"std_diff\": 2.602568303513662, \"max_abs_diff\": 14.36, \"n_sign_changes\": 56}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 10, \"anomaly_indices\": [0, 1, 24, 25, 145, 168, 169, 192, 193, 240], \"max_abs_z\": 4.643289365615513}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","claims_to_support":[{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["cross-validate against medium-scale analysis for robustness"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Detects changes and roughness in the series, useful for identifying abrupt changes.","supports_evidence":["change_locations"]},{"tool":"anomaly_detect","reason":"Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.","supports_evidence":["spike_heights","anomaly_counts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_locations","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_counts","input_binding":{}}],"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations and anomaly counts using the diff_stats and anomaly_detect tools."},"structured_observations":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"coverage":{"change_locations":"tool_supported","spike_heights":"tool_supported","anomaly_counts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.07390243902439027,"std_diff":2.602568303513662,"max_abs_diff":14.36,"n_sign_changes":56},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":10,"anomaly_indices":[0,1,24,25,145,168,169,192,193,240],"max_abs_z":4.643289365615513},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate strong seasonal patterns with a dominant period of 24, consistent spectral strength, and moderate-to-strong seasonal and trend components, implying recurring patterns and cycles. Residual variability suggests amplitude changes across cycles.","scale":"medium","observations":["Strong seasonal pattern identified.","Dominant cycle length detected as 24 units.","Residual variance indicates amplitude variability over cycles."],"evidence_intervals":["[null, null]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.07828587508312988, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 24, \"seas_acf1\": 0.6221341620165426, \"strength_hint\": \"strong\", \"metric_definition\": \"ρ_m=γ_m/γ_0 (MMTS seas_acf1)\"}, \"error\": null, \"args_fingerprint\": \"719c9194ac84c70646b652980711833b9d1b2003\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 24, \"residual_std\": 2.4391051338422796, \"residual_rmse\": 2.4500078262611216, \"series_std\": 4.6428487609279205, \"residual_var\": 5.949233853935763, \"series_var\": 21.556044616849924, \"stl_noise_ratio\": 0.2759891232218499, \"highpass_noise_ratio\": 0.7462237732864964, \"noise_ratio\": 0.7462237732864964, \"noise_level\": \"high\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.7138646424006991, \"trend_strength\": 0.07908771069719633, \"noise_type_hint\": \"uniform_like\", \"acf_lag1\": 0.8395141359811984, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"47a883230742f4cbb4f0165dcae85330e8c37e27\"}"],"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["seasonal_pattern consistency over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.","supports_evidence":["seasonal_pattern"]},{"tool":"fft_period","reason":"Determines dominant period to support evidence for cycle length.","supports_evidence":["cycle_length"]},{"tool":"noise_decomposition","reason":"Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.","supports_evidence":["amplitude_variability"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_level","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations."},"structured_observations":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}],"coverage":{"seasonal_pattern":"tool_supported","cycle_length":"tool_supported","amplitude_variability":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.07828587508312988,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":24,"seas_acf1":0.6221341620165426,"strength_hint":"strong","metric_definition":"ρ_m=γ_m/γ_0 (MMTS seas_acf1)"},"error":null,"args_fingerprint":"719c9194ac84c70646b652980711833b9d1b2003"},{"call_id":"medium:step3","step":3,"tool_name":"noise_decomposition","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":24,"residual_std":2.4391051338422796,"residual_rmse":2.4500078262611216,"series_std":4.6428487609279205,"residual_var":5.949233853935763,"series_var":21.556044616849924,"stl_noise_ratio":0.2759891232218499,"highpass_noise_ratio":0.7462237732864964,"noise_ratio":0.7462237732864964,"noise_level":"high","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.7138646424006991,"trend_strength":0.07908771069719633,"noise_type_hint":"uniform_like","acf_lag1":0.8395141359811984,"warnings":[]},"error":null,"args_fingerprint":"47a883230742f4cbb4f0165dcae85330e8c37e27"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend assessment and identification of significant level shifts in the series. Tools were used to provide an initial overview of the series and further detail on its trend and level shifts.","scale":"long","observations":["The series exhibits a downward trend with a negative slope.","Multiple discrete step or plateau levels suggest numerous level shifts within the series."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"min\": 0.0, \"max\": 26.36, \"median\": 4.725, \"range\": 26.36, \"p50\": 4.725, \"p90\": 7.593000000000003, \"p99\": 22.423199999999998, \"start\": 22.34, \"end\": 1.13, \"slope\": -0.07390243902439024}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.07390243902439024, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"start_value\": 22.34, \"end_value\": 1.13}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 40, \"n_plateau_runs\": 199, \"levels\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 10.24, 22.98, 8.97, 4.12, 1.05, 3.51, 0.69, 7.96, 9.56, 1.64, 2.88, 4.98, 5.64, 4.39, 17.56, 19.54, 11.72, 20.76, 21.11, 12.0, 26.244999999999997, 16.62, 7.53, 13.09, 13.43, 18.67], \"plateau_runs\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 6.5, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 6.08, 10.24, 22.98, 20.32, 8.97, 6.75, 7.22, 6.35, 5.952500000000001, 6.65, 5.29, 4.12, 3.16, 2.19, 0.52, 0.0025, 1.05, 6.26, 5.984999999999999, 6.8, 5.14, 3.91, 3.51, 3.21, 2.16, 0.69, 0.025, 2.24, 5.77, 7.96, 9.56, 8.27, 7.27, 6.6, 6.96, 6.064, 5.11, 4.19, 3.415, 2.53, 1.64, 0.076, 1.87, 2.88, 3.8, 4.98, 5.64, 6.1, 6.91, 6.39, 6.993333333333333, 6.38, 5.45, 4.12, 4.39, 4.01, 3.09, 1.98, 0.73, 0.0275, 1.2, 1.74, 2.3, 3.13, 4.9], \"plateau_lengths\": [1, 1, 1, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 2, 1, 1, 12, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 2, 1, 5, 1, 1, 2, 1, 1, 5, 1, 1, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1], \"tolerance\": 0.2636}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Assess global trends and major structural shifts across the entire series.","claims_to_support":[{"claim":"There exists a global trend in the series.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview including slope, which indicates the overall trend.","supports_evidence":["global_trend"]},{"tool":"segment_trend","reason":"Analyzes directional trend over specified segments to confirm consistency across the series.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts discrete step or plateau levels which can indicate significant level shifts.","supports_evidence":["level_shift_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"initial_statistical_summary","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_consistency_across_segments","input_binding":{}},{"step":3,"tool":"step_levels","output_key":"count_of_significant_level_shifts","input_binding":{}}],"reasoning":"The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required."},"structured_observations":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"coverage":{"global_trend":"tool_supported","level_shift_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":4.801909722222223,"std":4.6428487609279205,"min":0.0,"max":26.36,"median":4.725,"range":26.36,"p50":4.725,"p90":7.593000000000003,"p99":22.423199999999998,"start":22.34,"end":1.13,"slope":-0.07390243902439024}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.07390243902439024,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.801909722222223,"std":4.6428487609279205,"start_value":22.34,"end_value":1.13},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step3","step":3,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":40,"n_plateau_runs":199,"levels":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,10.24,22.98,8.97,4.12,1.05,3.51,0.69,7.96,9.56,1.64,2.88,4.98,5.64,4.39,17.56,19.54,11.72,20.76,21.11,12.0,26.244999999999997,16.62,7.53,13.09,13.43,18.67],"plateau_runs":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,6.5,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,6.08,10.24,22.98,20.32,8.97,6.75,7.22,6.35,5.952500000000001,6.65,5.29,4.12,3.16,2.19,0.52,0.0025,1.05,6.26,5.984999999999999,6.8,5.14,3.91,3.51,3.21,2.16,0.69,0.025,2.24,5.77,7.96,9.56,8.27,7.27,6.6,6.96,6.064,5.11,4.19,3.415,2.53,1.64,0.076,1.87,2.88,3.8,4.98,5.64,6.1,6.91,6.39,6.993333333333333,6.38,5.45,4.12,4.39,4.01,3.09,1.98,0.73,0.0275,1.2,1.74,2.3,3.13,4.9],"plateau_lengths":[1,1,1,1,1,3,2,1,1,1,2,1,1,4,1,1,1,1,1,1,1,1,1,4,1,1,1,2,1,1,12,1,2,2,1,1,1,1,1,1,1,4,1,1,1,1,1,1,2,1,5,1,1,2,1,1,5,1,1,1,1,1,1,2,1,3,1,1,1,1,1,1,1,1,4,1,1,1,1,1],"tolerance":0.2636},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The series exhibits a downward trend with a negative slope. Multiple discrete step or plateau levels suggest numerous level shifts within the series. Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series. Strong seasonal pattern identified. Dominant cycle length detected as 24 units. Residual variance indicates amplitude variability over cycles.","structured_by_scale":{"long":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"short":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"medium":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
retry_context=unresolved_claims=['parse_failure']
</metadata>

<candidates>
A) This series remains essentially flat at zero throughout most of its duration, with only one minor spike occurring around index 64, representing an almost entirely inactive signal.
B) This series displays irregular oscillations with multiple peaks of different heights, ranging from near-zero to approximately 19, with sporadic spikes and extended periods of low values.
C) This time series shows high variability with values fluctuating between approximately 7 and 100, featuring several dramatic drops and recoveries, creating a volatile pattern with significant amplitude changes.
D) This time series exhibits periodic patterns with sharp peaks reaching around 20-26 and valleys dropping near zero, showing cyclical behavior with varying amplitudes throughout the sequence.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=alignment.

```

### OUTPUT

```
{
  "reasoning": "The task requires matching the time series characteristics described in the temporal profile and metadata against the given candidate descriptions. Based on the evidence collected, we have data on global trends, level shifts, abrupt changes, anomalies, seasonal patterns, cycle lengths, and amplitude variabilities. The candidates will be evaluated based on these features.",
  "evidence_plan": {
    "objective": "Match identified time series characteristics with the most fitting description among the candidates.",
    "claims_to_support": [
      {"claim": "The series exhibits a negative global trend.", "required_evidence": ["global_trend"]},
      {"claim": "There are significant level shifts in the series.", "required_evidence": ["level_shift_count"]},
      {"claim": "Change locations are accurately identified.", "required_evidence": ["change_locations"]},
      {"claim": "Spike heights are correctly measured.", "required_evidence": ["spike_heights"]},
      {"claim": "Anomaly counts are precisely determined.", "required_evidence": ["anomaly_counts"]},
      {"claim": "Seasonal pattern exists.", "required_evidence": ["seasonal_pattern"]},
      {"claim": "Cycle length can be determined.", "required_evidence": ["cycle_length"]},
      {"claim": "Amplitude variability is evident over different cycles.", "required_evidence": ["amplitude_variability"]}
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "alignment"
    },
    "validation_needs": ["cross-reference findings with multiple scales to ensure coherent interpretation"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All required evidence is already available from prior tool calls.",
      "evidence_sources": [
        {"type": "upstream_observation", "ref": "long:step1", "field": "slope"},
        {"type": "upstream_observation", "ref": "long:step3", "field": "n_unique_levels"},
        {"type": "upstream_observation", "ref": "short:step1", "field": "n_sign_changes"},
        {"type": "upstream_observation", "ref": "short:step2", "field": "max_abs_z"},
        {"type": "upstream_observation", "ref": "short:step2", "field": "n_anomalies"},
        {"type": "upstream_observation", "ref": "medium:step3", "field": "seasonal_strength"},
        {"type": "upstream_observation", "ref": "medium:step1", "field": "dominant_period"},
        {"type": "upstream_observation", "ref": "medium:step3", "field": "noise_ratio"}
      ]
    }
  }
}
```

## Heterogeneous (alignment, s5) — `heterogeneous:alignment:s5:m1`

tokens prompt=9945 completion=1024 latency=42.92s

### INPUT (system)

```
You are a Heterogeneous Agent (role=alignment) at Stage 5: Evidence Integration.
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
  "role": "alignment",
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
{"evidence_plan":{"objective":"Match identified time series characteristics with the most fitting description among the candidates.","claims_to_support":[{"claim":"The series exhibits a negative global trend.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]},{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]},{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"role":"alignment"},"validation_needs":["cross-reference findings with multiple scales to ensure coherent interpretation"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All required evidence is already available from prior tool calls.","evidence_sources":[{"type":"upstream_observation","ref":"long:step1","field":"slope"},{"type":"upstream_observation","ref":"long:step3","field":"n_unique_levels"},{"type":"upstream_observation","ref":"short:step1","field":"n_sign_changes"},{"type":"upstream_observation","ref":"short:step2","field":"max_abs_z"},{"type":"upstream_observation","ref":"short:step2","field":"n_anomalies"},{"type":"upstream_observation","ref":"medium:step3","field":"seasonal_strength"},{"type":"upstream_observation","ref":"medium:step1","field":"dominant_period"},{"type":"upstream_observation","ref":"medium:step3","field":"noise_ratio"}]}},"reasoning":"The task requires matching the time series characteristics described in the temporal profile and metadata against the given candidate descriptions. Based on the evidence collected, we have data on global trends, level shifts, abrupt changes, anomalies, seasonal patterns, cycle lengths, and amplitude variabilities. The candidates will be evaluated based on these features."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps include 'diff_stats' for detecting changes and roughness in the series, which helps in identifying abrupt changes, and 'anomaly_detect' for detecting spikes/outliers, necessary for measuring spike heights and anomaly counts.","scale":"short","observations":["Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series."],"evidence_intervals":["[start of series, end of series]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.07390243902439027, \"std_diff\": 2.602568303513662, \"max_abs_diff\": 14.36, \"n_sign_changes\": 56}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 10, \"anomaly_indices\": [0, 1, 24, 25, 145, 168, 169, 192, 193, 240], \"max_abs_z\": 4.643289365615513}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.","claims_to_support":[{"claim":"Change locations are accurately identified.","required_evidence":["change_locations"]},{"claim":"Spike heights are correctly measured.","required_evidence":["spike_heights"]},{"claim":"Anomaly counts are precisely determined.","required_evidence":["anomaly_counts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["cross-validate against medium-scale analysis for robustness"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Detects changes and roughness in the series, useful for identifying abrupt changes.","supports_evidence":["change_locations"]},{"tool":"anomaly_detect","reason":"Detects spikes/outliers in the series, necessary for measuring spike heights and anomaly counts.","supports_evidence":["spike_heights","anomaly_counts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_locations","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_counts","input_binding":{}}],"reasoning":"The objective for the short-scale analysis is to identify specific instances of abrupt changes, anomalies, and minor local fluctuations. This requires pinpointing exact change locations and anomaly counts using the diff_stats and anomaly_detect tools."},"structured_observations":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"coverage":{"change_locations":"tool_supported","spike_heights":"tool_supported","anomaly_counts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.07390243902439027,"std_diff":2.602568303513662,"max_abs_diff":14.36,"n_sign_changes":56},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":10,"anomaly_indices":[0,1,24,25,145,168,169,192,193,240],"max_abs_z":4.643289365615513},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate strong seasonal patterns with a dominant period of 24, consistent spectral strength, and moderate-to-strong seasonal and trend components, implying recurring patterns and cycles. Residual variability suggests amplitude changes across cycles.","scale":"medium","observations":["Strong seasonal pattern identified.","Dominant cycle length detected as 24 units.","Residual variance indicates amplitude variability over cycles."],"evidence_intervals":["[null, null]"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.07828587508312988, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"seas_acf\", \"arguments\": {\"series_index\": 1, \"lag\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"lag\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"lag\": 24, \"seas_acf1\": 0.6221341620165426, \"strength_hint\": \"strong\", \"metric_definition\": \"ρ_m=γ_m/γ_0 (MMTS seas_acf1)\"}, \"error\": null, \"args_fingerprint\": \"719c9194ac84c70646b652980711833b9d1b2003\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1, \"period\": 24.0}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 24, \"residual_std\": 2.4391051338422796, \"residual_rmse\": 2.4500078262611216, \"series_std\": 4.6428487609279205, \"residual_var\": 5.949233853935763, \"series_var\": 21.556044616849924, \"stl_noise_ratio\": 0.2759891232218499, \"highpass_noise_ratio\": 0.7462237732864964, \"noise_ratio\": 0.7462237732864964, \"noise_level\": \"high\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.7138646424006991, \"trend_strength\": 0.07908771069719633, \"noise_type_hint\": \"uniform_like\", \"acf_lag1\": 0.8395141359811984, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"47a883230742f4cbb4f0165dcae85330e8c37e27\"}"],"evidence_plan":{"objective":"Detect recurring patterns, cycles, and intermediate structures.","claims_to_support":[{"claim":"Seasonal pattern exists.","required_evidence":["seasonal_pattern"]},{"claim":"Cycle length can be determined.","required_evidence":["cycle_length"]},{"claim":"Amplitude variability is evident over different cycles.","required_evidence":["amplitude_variability"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["seasonal_pattern consistency over time"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"Measures seasonal autocorrelation at specific lags to support evidence for seasonal patterns.","supports_evidence":["seasonal_pattern"]},{"tool":"fft_period","reason":"Determines dominant period to support evidence for cycle length.","supports_evidence":["cycle_length"]},{"tool":"noise_decomposition","reason":"Measures noise strength after STL decomposition, indirectly supporting evidence for amplitude variability through residuals.","supports_evidence":["amplitude_variability"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"seas_acf","output_key":"strength_hint","input_binding":{"lag":"$step1.dominant_period"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_level","input_binding":{"period":"$step1.dominant_period"}}],"reasoning":"First, we use 'fft_period' to determine the dominant period and related spectral strengths to identify potential cycles. Then, 'seas_acf' measures seasonal autocorrelation based on the identified dominant period for confirming seasonal patterns. Lastly, 'noise_decomposition' is applied to decompose the series into noise components to detect amplitude variations."},"structured_observations":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}],"coverage":{"seasonal_pattern":"tool_supported","cycle_length":"tool_supported","amplitude_variability":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.07828587508312988,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"seas_acf","arguments":{"series_index":1,"lag":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"lag":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"lag":24,"seas_acf1":0.6221341620165426,"strength_hint":"strong","metric_definition":"ρ_m=γ_m/γ_0 (MMTS seas_acf1)"},"error":null,"args_fingerprint":"719c9194ac84c70646b652980711833b9d1b2003"},{"call_id":"medium:step3","step":3,"tool_name":"noise_decomposition","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1,"period":24.0},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":24,"residual_std":2.4391051338422796,"residual_rmse":2.4500078262611216,"series_std":4.6428487609279205,"residual_var":5.949233853935763,"series_var":21.556044616849924,"stl_noise_ratio":0.2759891232218499,"highpass_noise_ratio":0.7462237732864964,"noise_ratio":0.7462237732864964,"noise_level":"high","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.7138646424006991,"trend_strength":0.07908771069719633,"noise_type_hint":"uniform_like","acf_lag1":0.8395141359811984,"warnings":[]},"error":null,"args_fingerprint":"47a883230742f4cbb4f0165dcae85330e8c37e27"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend assessment and identification of significant level shifts in the series. Tools were used to provide an initial overview of the series and further detail on its trend and level shifts.","scale":"long","observations":["The series exhibits a downward trend with a negative slope.","Multiple discrete step or plateau levels suggest numerous level shifts within the series."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"min\": 0.0, \"max\": 26.36, \"median\": 4.725, \"range\": 26.36, \"p50\": 4.725, \"p90\": 7.593000000000003, \"p99\": 22.423199999999998, \"start\": 22.34, \"end\": 1.13, \"slope\": -0.07390243902439024}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.07390243902439024, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 4.801909722222223, \"std\": 4.6428487609279205, \"start_value\": 22.34, \"end_value\": 1.13}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 40, \"n_plateau_runs\": 199, \"levels\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 10.24, 22.98, 8.97, 4.12, 1.05, 3.51, 0.69, 7.96, 9.56, 1.64, 2.88, 4.98, 5.64, 4.39, 17.56, 19.54, 11.72, 20.76, 21.11, 12.0, 26.244999999999997, 16.62, 7.53, 13.09, 13.43, 18.67], \"plateau_runs\": [22.34, 20.4, 8.27, 6.76, 6.49, 5.953333333333333, 6.5, 7.1, 5.34, 3.8, 3.145, 1.99, 0.33, 0.01, 2.36, 6.08, 10.24, 22.98, 20.32, 8.97, 6.75, 7.22, 6.35, 5.952500000000001, 6.65, 5.29, 4.12, 3.16, 2.19, 0.52, 0.0025, 1.05, 6.26, 5.984999999999999, 6.8, 5.14, 3.91, 3.51, 3.21, 2.16, 0.69, 0.025, 2.24, 5.77, 7.96, 9.56, 8.27, 7.27, 6.6, 6.96, 6.064, 5.11, 4.19, 3.415, 2.53, 1.64, 0.076, 1.87, 2.88, 3.8, 4.98, 5.64, 6.1, 6.91, 6.39, 6.993333333333333, 6.38, 5.45, 4.12, 4.39, 4.01, 3.09, 1.98, 0.73, 0.0275, 1.2, 1.74, 2.3, 3.13, 4.9], \"plateau_lengths\": [1, 1, 1, 1, 1, 3, 2, 1, 1, 1, 2, 1, 1, 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 2, 1, 1, 12, 1, 2, 2, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1, 1, 2, 1, 5, 1, 1, 2, 1, 1, 5, 1, 1, 1, 1, 1, 1, 2, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1, 1, 1, 1, 1], \"tolerance\": 0.2636}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Assess global trends and major structural shifts across the entire series.","claims_to_support":[{"claim":"There exists a global trend in the series.","required_evidence":["global_trend"]},{"claim":"There are significant level shifts in the series.","required_evidence":["level_shift_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["verify consistency across multiple sections of the series"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview including slope, which indicates the overall trend.","supports_evidence":["global_trend"]},{"tool":"segment_trend","reason":"Analyzes directional trend over specified segments to confirm consistency across the series.","supports_evidence":["global_trend"]},{"tool":"step_levels","reason":"Counts discrete step or plateau levels which can indicate significant level shifts.","supports_evidence":["level_shift_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"initial_statistical_summary","input_binding":{}},{"step":2,"tool":"segment_trend","output_key":"trend_consistency_across_segments","input_binding":{}},{"step":3,"tool":"step_levels","output_key":"count_of_significant_level_shifts","input_binding":{}}],"reasoning":"The objective is to assess global trends and major structural shifts across the entire series. The selected tools provide a statistical overview, directional trend analysis, and counting of step levels which together can support the evidence required."},"structured_observations":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"coverage":{"global_trend":"tool_supported","level_shift_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":4.801909722222223,"std":4.6428487609279205,"min":0.0,"max":26.36,"median":4.725,"range":26.36,"p50":4.725,"p90":7.593000000000003,"p99":22.423199999999998,"start":22.34,"end":1.13,"slope":-0.07390243902439024}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.07390243902439024,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":4.801909722222223,"std":4.6428487609279205,"start_value":22.34,"end_value":1.13},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step3","step":3,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":40,"n_plateau_runs":199,"levels":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,10.24,22.98,8.97,4.12,1.05,3.51,0.69,7.96,9.56,1.64,2.88,4.98,5.64,4.39,17.56,19.54,11.72,20.76,21.11,12.0,26.244999999999997,16.62,7.53,13.09,13.43,18.67],"plateau_runs":[22.34,20.4,8.27,6.76,6.49,5.953333333333333,6.5,7.1,5.34,3.8,3.145,1.99,0.33,0.01,2.36,6.08,10.24,22.98,20.32,8.97,6.75,7.22,6.35,5.952500000000001,6.65,5.29,4.12,3.16,2.19,0.52,0.0025,1.05,6.26,5.984999999999999,6.8,5.14,3.91,3.51,3.21,2.16,0.69,0.025,2.24,5.77,7.96,9.56,8.27,7.27,6.6,6.96,6.064,5.11,4.19,3.415,2.53,1.64,0.076,1.87,2.88,3.8,4.98,5.64,6.1,6.91,6.39,6.993333333333333,6.38,5.45,4.12,4.39,4.01,3.09,1.98,0.73,0.0275,1.2,1.74,2.3,3.13,4.9],"plateau_lengths":[1,1,1,1,1,3,2,1,1,1,2,1,1,4,1,1,1,1,1,1,1,1,1,4,1,1,1,2,1,1,12,1,2,2,1,1,1,1,1,1,1,4,1,1,1,1,1,1,2,1,5,1,1,2,1,1,5,1,1,1,1,1,1,2,1,3,1,1,1,1,1,1,1,1,4,1,1,1,1,1],"tolerance":0.2636},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The series exhibits a downward trend with a negative slope. Multiple discrete step or plateau levels suggest numerous level shifts within the series. Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series. Strong seasonal pattern identified. Dominant cycle length detected as 24 units. Residual variance indicates amplitude variability over cycles.","structured_by_scale":{"long":[{"claim":"There exists a global trend in the series.","evidence":[{"type":"global_trend","value":-0.07390243902439024,"source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"global_trend","value":-0.07390243902439024,"source_tool":"segment_trend","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"There are significant level shifts in the series.","evidence":[{"type":"level_shift_count","value":40,"source_tool":"step_levels","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_shift_count"}],"short":[{"claim":"Change locations are accurately identified.","evidence":[{"type":"change_locations","value":56,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_locations"},{"claim":"Spike heights are correctly measured.","evidence":[{"type":"spike_heights","value":4.643289365615513,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"spike_heights"},{"claim":"Anomaly counts are precisely determined.","evidence":[{"type":"anomaly_counts","value":10,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_counts"}],"medium":[{"claim":"Seasonal pattern exists.","evidence":[{"type":"seasonal_strength","value":0.7138646424006991,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"seas_acf_strength","value":0.6221341620165426,"source_tool":"seas_acf","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_pattern"},{"claim":"Cycle length can be determined.","evidence":[{"type":"dominant_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"cycle_length"},{"claim":"Amplitude variability is evident over different cycles.","evidence":[{"type":"noise_ratio","value":0.7462237732864964,"source_tool":"noise_decomposition","call_id":"medium:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"amplitude_variability"}]}}
</temporal_profile>

<assignment>
{"role":"alignment","objective":"Match identified time series characteristics with the most fitting description among the candidates.","required_measurements":["global_trend","level_shift_count","change_locations","spike_heights","anomaly_counts","seasonal_pattern","cycle_length","amplitude_variability"],"validation_requirements":["cross-reference findings with multiple scales to ensure coherent interpretation"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) This series remains essentially flat at zero throughout most of its duration, with only one minor spike occurring around index 64, representing an almost entirely inactive signal.
B) This series displays irregular oscillations with multiple peaks of different heights, ranging from near-zero to approximately 19, with sporadic spikes and extended periods of low values.
C) This time series shows high variability with values fluctuating between approximately 7 and 100, featuring several dramatic drops and recoveries, creating a volatile pattern with significant amplitude changes.
D) This time series exhibits periodic patterns with sharp peaks reaching around 20-26 and valleys dropping near zero, showing cyclical behavior with varying amplitudes throughout the sequence.
</candidates>

Produce the TaskEvidence JSON for role=alignment.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the series exhibits a downward trend, has significant level shifts, detects many abrupt changes, identifies anomalies, and reveals strong seasonal patterns with consistent cycles and amplitude variability. Among the provided options, D best matches this pattern.",
  "hypothesis": "Candidate D accurately describes the time series as having periodic patterns with sharp peaks and valleys, consistent with the strong seasonal component and amplitude changes observed.",
  "evidence": ["series has a negative global trend", "multiple significant level shifts occur", "abrupt changes are detected", "anomalies are found", "strong seasonal patterns exist", "consistent cycle length of 24 units", "amplitude variability over cycles is noted"],
  "candidate_preference": "D",
  "confidence": 0.9,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "long:step1", "long:step2", "long:step3", "medium:step1", "medium:step2", "medium:step3"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The series exhibits a negative global trend.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.07390243902439024,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step2"
        },
        {
          "type": "global_trend",
          "value": -0.07390243902439024,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are significant level shifts in the series.",
      "evidence": [
        {
          "type": "level_shift_count",
          "value": 40,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Change locations are accurately identified.",
      "evidence": [
        {
          "type": "change_locations",
          "value": 56,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Spike heights are correctly measured.",
      "evidence": [
        {
          "type": "spike_heights",
          "value": 4.643289365615513,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Anomaly counts are precisely determined.",
      "evidence": [
        {
          "type": "anomaly_counts",
          "value": 10,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Seasonal pattern exists.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.7138646424006991,
          "provenance": "tool",
          "ref": null,
          "call_id": "medium:step3"
        },
        {
          "type": "seas_acf_strength",
          "value": 0.6221341620165426,
          "provenance": "tool",
          "ref": null,
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Cycle length can be determined.",
      "evidence": [
        {
          "type": "dominant_period",
          "value": 24.0,
          "provenance": "tool",
          "ref": null,
          "call_id": "medium:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Amplitude variability is evident over different cycles.",
      "evidence": [
        {
          "type": "noise_ratio",
          "value": 0.74
```

## Integration — `integration`

tokens prompt=1981 completion=271 latency=10.02s

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
A) This series remains essentially flat at zero throughout most of its duration, with only one minor spike occurring around index 64, representing an almost entirely inactive signal.
B) This series displays irregular oscillations with multiple peaks of different heights, ranging from near-zero to approximately 19, with sporadic spikes and extended periods of low values.
C) This time series shows high variability with values fluctuating between approximately 7 and 100, featuring several dramatic drops and recoveries, creating a volatile pattern with significant amplitude changes.
D) This time series exhibits periodic patterns with sharp peaks reaching around 20-26 and valleys dropping near zero, showing cyclical behavior with varying amplitudes throughout the sequence.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Identify the correct description from the given options for the provided time series based on its visual or numerical characteristics.",
  "question_type": "choice",
  "required_output": "description",
  "success_criteria": [
    "correctly identifies key characteristics of the series"
  ],
  "assignments_brief": [
    {
      "agent": "homo:long",
      "objective": "Assess global trends and major structural shifts across the entire series.",
      "required_measurements": [
        "global_trend",
        "level_shift_count"
      ]
    },
    {
      "agent": "homo:short",
      "objective": "Identify specific instances of abrupt changes, anomalies, and minor local fluctuations.",
      "required_measurements": [
        "change_locations",
        "spike_heights",
        "anomaly_counts"
      ]
    },
    {
      "agent": "homo:medium",
      "objective": "Detect recurring patterns, cycles, and intermediate structures.",
      "required_measurements": [
        "seasonal_pattern",
        "cycle_length",
        "amplitude_variability"
      ]
    },
    {
      "agent": "hetero:alignment",
      "objective": "Match identified time series characteristics with the most fitting description among the candidates.",
      "required_measurements": [
        "global_trend",
        "level_shift_count",
        "change_locations",
        "spike_heights",
        "anomaly_counts",
        "seasonal_pattern",
        "cycle_length",
        "amplitude_variability"
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
          "type": "change_locations",
          "value": 56,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "spike_heights",
          "value": 4.643289365615513,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "anomaly_counts",
          "value": 10,
          "trusted": true
        }
      ],
      "coverage": {
        "change_locations": "tool_supported",
        "spike_heights": "tool_supported",
        "anomaly_counts": "tool_supported"
      },
      "summary": "Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series."
    },
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "seasonal_strength",
          "value": 0.7138646424006991,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "seas_acf_strength",
          "value": 0.6221341620165426,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "dominant_period",
          "value": 24.0,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "noise_ratio",
          "value": 0.7462237732864964,
          "trusted": true
        }
      ],
      "coverage": {
        "seasonal_pattern": "tool_supported",
        "cycle_length": "tool_supported",
        "amplitude_variability": "tool_supported"
      },
      "summary": "Strong seasonal pattern identified. | Dominant cycle length detected as 24 units. | Residual variance indicates amplitude variability over cycles."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_trend",
          "value": -0.07390243902439024,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "global_trend",
          "value": -0.07390243902439024,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "level_shift_count",
          "value": 40,
          "trusted": true
        }
      ],
      "coverage": {
        "global_trend": "tool_supported",
        "level_shift_count": "tool_supported"
      },
      "summary": "The series exhibits a downward trend with a negative slope. | Multiple discrete step or plateau levels suggest numerous level shifts within the series."
    }
  },
  "conflicts": [],
  "summary": "The series exhibits a downward trend with a negative slope. Multiple discrete step or plateau levels suggest numerous level shifts within the series. Abrupt changes were detected through 'diff_stats', with 56 sign changes recorded. Anomalies were identified using 'anomaly_detect', with 10 anomalies found at specific indices within the series. Strong seasonal pattern identified. Dominant cycle length detected as 24 units. Residual variance indicates amplitude variability over cycles."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "alignment",
      "hypothesis": "Parse failure in S5",
      "reasoning_chain": [
        "parse failure"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": false,
      "grounded_in": [],
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

<question_rules>
- Match/Align: answer must be one candidate letter. Trust execution_metadata.option_mapping and verified_preference when present.
</question_rules>

Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "The time series has a strong seasonal component with a dominant cycle length of 24 units, indicating a repetitive behavior with periodic peaks and troughs. The series also shows numerous anomalies and level shifts, along with a slight negative trend, but the presence of a consistent seasonal pattern and the absence of a predominantly flat trend or extreme volatility points towards a cyclic structure.",
  "answer": "D",
  "explanation": "Based on the strong seasonality with a clear dominant period and the description of sharp peaks and valleys, the closest match is option D which describes a time series with periodic patterns having peaks around 20-26 and valleys near zero.",
  "confidence": 0.9,
  "conflicts": [],
  "cited_evidence": ["seasonal_strength", "dominant_period", "noise_ratio", "global_trend", "level_shift_count", "change_locations", "spike_heights", "anomaly_counts"],
  "decision_trace": {
    "metric": "seasonal_pattern",
    "observed_value": 0.7138646424006991,
    "intervals_from_question": [],
    "matched_label": "cyclic",
    "matched_letter": "D"
  }
}
```
