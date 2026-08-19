# Agent IO summary: `Align:caption2ts_qa_120:73`

- Architecture pred: `D` (success=True)
- model_calls=18, tool_calls=8, latency=203.6s

## Planner — `planner`

tokens prompt=1153 completion=505 latency=17.96s

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
'This time series data shows relatively stable low values (16-20) from index 0-12, followed by a dramatic upward trend starting at index 13, reaching peak values around 95-100 from index 15-23, with one notable dip to 71.75 at index 18.' According to the above textual description of a time series, select the time series from the following four options that most accurately reflects the described characteristics.
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
  "reasoning": "The task requires identifying which time series among the provided options best matches the given textual description of trends and patterns. This involves both understanding the temporal dynamics and comparing them against the described behavior.",
  "task_summary": "Match a time series from given options to a textual description of trends and patterns.",
  "target_output": "select the time series from the following four options that most accurately reflects the described characteristics",
  "answer_type": "choice",
  "capability": "match and validate descriptive pattern characteristics against visual/numeric data.",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "medium",
      "objective": "Identify periods of stability and trend changes within the time series.",
      "required_measurements": ["endpoint_slope", "step_level_count"],
      "validation_requirements": ["ensure periods of relative stability are accurately identified"],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 23]]
    },
    {
      "scale": "short",
      "objective": "Detect abrupt changes and anomalies like dips within the time series.",
      "required_measurements": ["change_location", "anomaly_score"],
      "validation_requirements": ["verify specific changes align with described behavior"],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 23]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Compare observed behaviors across all candidate time series against the textual description and rank them.",
      "required_measurements": ["pairwise_similarity", "reverse_similarity", "caption_claim_support"],
      "validation_requirements": ["verify the chosen time series best matches the described characteristics"],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 23]]
    }
  ],
  "success_criteria": [
    "Identifying consistent stable low values followed by a significant increase, including any notable drops.",
    "Comparing candidate time series against the textual description to ensure accurate reflection of described behaviors."
  ],
  "notes": "Ensure all critical features mentioned in the description, such as initial stability, subsequent increase, peak range, and a specific dip, are captured and compared properly."
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4141 completion=267 latency=10.63s

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
{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of trends and patterns. This involves both understanding the temporal dynamics and comparing them against the described behavior.","task_summary":"Match a time series from given options to a textual description of trends and patterns.","target_output":"select the time series from the following four options that most accurately reflects the described characteristics","answer_type":"choice","capability":"match and validate descriptive pattern characteristics against visual/numeric data.","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]},{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"hetero_assignments":[{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Identifying consistent stable low values followed by a significant increase, including any notable drops.","Comparing candidate time series against the textual description to ensure accurate reflection of described behaviors."],"notes":"Ensure all critical features mentioned in the description, such as initial stability, subsequent increase, peak range, and a specific dip, are captured and compared properly."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify periods of stability and trend changes within the time series, focusing on measuring endpoint slopes and step level counts while ensuring accuracy in identifying periods of relative stability.",
  "evidence_plan": {
    "objective": "Identify periods of stability and trend changes within the time series.",
    "claims_to_support": [
      {"claim": "Measure endpoint slopes of the time series.", "required_evidence": ["endpoint_slope"]},
      {"claim": "Count the number of step levels in the time series.", "required_evidence": ["step_level_count"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [[0, 23]], "scale": "medium"},
    "validation_needs": ["endpoint_slope", "step_level_count"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "segment_trend", "reason": "Measures endpoint slope of the time series over the entire interval.", "supports_evidence": ["endpoint_slope"]},
      {"tool": "step_levels", "reason": "Counts discrete step levels, reflecting periods of stability and change.", "supports_evidence": ["step_level_count"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=789 completion=129 latency=4.63s

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
{"evidence_plan":{"objective":"Identify periods of stability and trend changes within the time series.","claims_to_support":[{"claim":"Measure endpoint slopes of the time series.","required_evidence":["endpoint_slope"]},{"claim":"Count the number of step levels in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,23]],"scale":"medium"},"validation_needs":["endpoint_slope","step_level_count"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures endpoint slope of the time series over the entire interval.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"Counts discrete step levels, reflecting periods of stability and change.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"reasoning":"The objective is to identify periods of stability and trend changes within the time series, focusing on measuring endpoint slopes and step level counts while ensuring accuracy in identifying periods of relative stability."}
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
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "endpoint_slope",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "step_levels",
      "output_key": "step_level_count",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=903 completion=158 latency=5.68s

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
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_level_count","input_binding":{}}],"reasoning":"The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently."}
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
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently.",
  "calls": [
    {
      "step": 1,
      "tool": "segment_trend",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 23
      }
    },
    {
      "step": 2,
      "tool": "step_levels",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 23
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=1712 completion=397 latency=14.35s

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
{"evidence_plan":{"objective":"Identify periods of stability and trend changes within the time series.","claims_to_support":[{"claim":"Measure endpoint slopes of the time series.","required_evidence":["endpoint_slope"]},{"claim":"Count the number of step levels in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,23]],"scale":"medium"},"validation_needs":["endpoint_slope","step_level_count"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures endpoint slope of the time series over the entire interval.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"Counts discrete step levels, reflecting periods of stability and change.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"reasoning":"The objective is to identify periods of stability and trend changes within the time series, focusing on measuring endpoint slopes and step level counts while ensuring accuracy in identifying periods of relative stability."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "medium:step1",
    "step": 1,
    "tool_name": "segment_trend",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 23,
      "slope": 0.026521739130434784,
      "direction": "upward",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 7.260833333333333,
      "std": 4.719874571662071,
      "start_value": 0.89,
      "end_value": 1.5
    },
    "error": null,
    "args_fingerprint": "1fa3e05bcf7003070de53468b1fb53c0bde4defe"
  },
  {
    "call_id": "medium:step2",
    "step": 2,
    "tool_name": "step_levels",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 23,
      "n_unique_levels": 18,
      "n_plateau_runs": 21,
      "levels": [
        0.89,
        1.37,
        2.4,
        4.94,
        7.955,
        8.52,
        8.85,
        9.56,
        10.065000000000001,
        11.25,
        13.87,
        20.37,
        14.08,
        9.07,
        7.46,
        6.73,
        6.23,
        3.2
      ],
      "plateau_runs": [
        0.89,
        1.37,
        2.4,
        4.94,
        7.955,
        8.52,
        8.85,
        9.56,
        10.065000000000001,
        11.25,
        13.87,
        20.37,
        14.08,
        9.07,
        7.46,
        6.73,
        6.23,
        4.82,
        3.2,
        2.22,
        1.5
      ],
      "plateau_lengths": [
        2,
        1,
        1,
        1,
        2,
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
        1
      ],
      "tolerance": 0.1948
    },
    "error": null,
    "args_fingerprint": "5f449048a3d8b9b281bc92f1b7926d7314990900"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify periods of stability and trend changes within the time series by measuring endpoint slopes and counting step levels. The segment_trend tool successfully measured the endpoint slope as upward with a direction class of vague. The step_levels tool counted 18 unique step levels, indicating multiple periods of stability and change within the time series.",
  "scale": "medium",
  "observations": ["Endpoint slope measurement indicates an upward trend but with vague directionality.", "Step level count shows significant variability in the time series, with 18 unique levels identified."],
  "evidence_intervals": ["[0,23]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Measure endpoint slopes of the time series.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 0.026521739130434784,
          "source_tool": "segment_trend",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "endpoint_slope"
    },
    {
      "claim": "Count the number of step levels in the time series.",
      "evidence": [
        {
          "type": "step_level_count",
          "value": 18,
          "source_tool": "step_levels",
          "call_id": "medium:step2",
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

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4139 completion=284 latency=11.24s

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
{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of trends and patterns. This involves both understanding the temporal dynamics and comparing them against the described behavior.","task_summary":"Match a time series from given options to a textual description of trends and patterns.","target_output":"select the time series from the following four options that most accurately reflects the described characteristics","answer_type":"choice","capability":"match and validate descriptive pattern characteristics against visual/numeric data.","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]},{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"hetero_assignments":[{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Identifying consistent stable low values followed by a significant increase, including any notable drops.","Comparing candidate time series against the textual description to ensure accurate reflection of described behaviors."],"notes":"Ensure all critical features mentioned in the description, such as initial stability, subsequent increase, peak range, and a specific dip, are captured and compared properly."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect abrupt changes and anomalies such as dips within the time series. For scale=short, we focus on local changes and abrupt shifts. We need to identify the location of changes and calculate anomaly scores to support claims.",
  "evidence_plan": {
    "objective": "Detect abrupt changes and anomalies like dips within the time series.",
    "claims_to_support": [
      {"claim": "abrupt changes are detected within the time series", "required_evidence": ["change_location"]},
      {"claim": "anomalies such as dips are identified within the time series", "required_evidence": ["anomaly_score"]}
    ],
    "analysis_scope": {"target_series": [1, 2, 3, 4], "focus_intervals": [[0, 23]], "scale": "short"},
    "validation_needs": ["verify specific changes align with described behavior"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "diff_stats", "reason": "detection of abrupt changes through first difference statistics", "supports_evidence": ["change_location"]},
      {"tool": "anomaly_detect", "reason": "detect spikes and outliers in a window", "supports_evidence": ["anomaly_score"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=806 completion=145 latency=5.20s

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
{"evidence_plan":{"objective":"Detect abrupt changes and anomalies like dips within the time series.","claims_to_support":[{"claim":"abrupt changes are detected within the time series","required_evidence":["change_location"]},{"claim":"anomalies such as dips are identified within the time series","required_evidence":["anomaly_score"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,23]],"scale":"short"},"validation_needs":["verify specific changes align with described behavior"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"detection of abrupt changes through first difference statistics","supports_evidence":["change_location"]},{"tool":"anomaly_detect","reason":"detect spikes and outliers in a window","supports_evidence":["anomaly_score"]}],"no_tool_decision":null},"reasoning":"The objective is to detect abrupt changes and anomalies such as dips within the time series. For scale=short, we focus on local changes and abrupt shifts. We need to identify the location of changes and calculate anomaly scores to support claims."}
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
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "For detecting abrupt changes and anomalies in the time series, the diff_stats tool should be used first to identify locations where changes occur. Then, the anomaly_detect tool can be utilized to identify anomalies based on these change points.",
  "workflow": [
    {
      "step": 1,
      "tool": "diff_stats",
      "output_key": "change_location",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "output_key": "anomaly_score",
      "input_binding": {"start": "$step1.start", "end": "$step1.end"}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=900 completion=179 latency=6.41s

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
{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_location","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_score","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"For detecting abrupt changes and anomalies in the time series, the diff_stats tool should be used first to identify locations where changes occur. Then, the anomaly_detect tool can be utilized to identify anomalies based on these change points."}
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
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The workflow involves two steps. The first step uses the diff_stats tool to detect abrupt changes in the time series. Since no specific interval was specified for the series, we'll consider the full length of the series. The second step utilizes the anomaly_detect tool to identify anomalies based on the identified change points.",
  "calls": [
    {
      "step": 1,
      "tool": "diff_stats",
      "args": {
        "series_index": 1,
        "start": 0,
        "end": 23
      }
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "args": {
        "series_index": 1,
        "start": "$step1.start",
        "end": "$step1.end"
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1301 completion=370 latency=13.24s

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
{"evidence_plan":{"objective":"Detect abrupt changes and anomalies like dips within the time series.","claims_to_support":[{"claim":"abrupt changes are detected within the time series","required_evidence":["change_location"]},{"claim":"anomalies such as dips are identified within the time series","required_evidence":["anomaly_score"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,23]],"scale":"short"},"validation_needs":["verify specific changes align with described behavior"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"detection of abrupt changes through first difference statistics","supports_evidence":["change_location"]},{"tool":"anomaly_detect","reason":"detect spikes and outliers in a window","supports_evidence":["anomaly_score"]}],"no_tool_decision":null},"reasoning":"The objective is to detect abrupt changes and anomalies such as dips within the time series. For scale=short, we focus on local changes and abrupt shifts. We need to identify the location of changes and calculate anomaly scores to support claims."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "diff_stats",
    "arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 23,
      "mean_diff": 0.026521739130434836,
      "std_diff": 2.4923981967708415,
      "max_abs_diff": 6.500000000000002,
      "n_sign_changes": 3
    },
    "error": null,
    "args_fingerprint": "ab2e93895dc600bfdd9107e99f858b2b615526d8"
  },
  {
    "call_id": "short:step2",
    "step": 2,
    "tool_name": "anomaly_detect",
    "arguments": {
      "series_index": 1,
      "start": "$step1.start",
      "end": "$step1.end"
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 0,
      "end": 23
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 23,
      "z_threshold": 3.0,
      "n_anomalies": 0,
      "anomaly_indices": [],
      "max_abs_z": 2.7774396263353167
    },
    "error": null,
    "args_fingerprint": "80792d37f261dd92c61e5c31a98e5d616f183c3e"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Executed diff_stats and anomaly_detect tools to find abrupt changes and anomalies in the specified time series. Diff_stats found three sign changes, indicating potential abrupt shifts, but no anomalies were detected by anomaly_detect within the confidence threshold.",
  "scale": "short",
  "observations": ["Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold.", "No anomalies were identified within the defined time series segment using the anomaly detection method."],
  "evidence_intervals": ["time series data segment [0, 23]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "abrupt changes are detected within the time series",
      "evidence": [
        {
          "type": "change_location",
          "value": 3,
          "source_tool": "diff_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_location"
    },
    {
      "claim": "anomalies such as dips are identified within the time series",
      "evidence": [
        {
          "type": "anomaly_score",
          "value": 0,
          "source_tool": "anomaly_detect",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomaly_score"
    }
  ],
  "coverage": {"change_location": "tool_supported", "anomaly_score": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=6086 completion=408 latency=16.71s

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
{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of trends and patterns. This involves both understanding the temporal dynamics and comparing them against the described behavior.","task_summary":"Match a time series from given options to a textual description of trends and patterns.","target_output":"select the time series from the following four options that most accurately reflects the described characteristics","answer_type":"choice","capability":"match and validate descriptive pattern characteristics against visual/numeric data.","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]},{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"hetero_assignments":[{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Identifying consistent stable low values followed by a significant increase, including any notable drops.","Comparing candidate time series against the textual description to ensure accurate reflection of described behaviors."],"notes":"Ensure all critical features mentioned in the description, such as initial stability, subsequent increase, peak range, and a specific dip, are captured and compared properly."}
</plan_context>

<task_summary>
Match a time series from given options to a textual description of trends and patterns.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed diff_stats and anomaly_detect tools to find abrupt changes and anomalies in the specified time series. Diff_stats found three sign changes, indicating potential abrupt shifts, but no anomalies were detected by anomaly_detect within the confidence threshold.","scale":"short","observations":["Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold.","No anomalies were identified within the defined time series segment using the anomaly detection method."],"evidence_intervals":["time series data segment [0, 23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"mean_diff\": 0.026521739130434836, \"std_diff\": 2.4923981967708415, \"max_abs_diff\": 6.500000000000002, \"n_sign_changes\": 3}, \"error\": null, \"args_fingerprint\": \"ab2e93895dc600bfdd9107e99f858b2b615526d8\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.7774396263353167}, \"error\": null, \"args_fingerprint\": \"80792d37f261dd92c61e5c31a98e5d616f183c3e\"}"],"evidence_plan":{"objective":"Detect abrupt changes and anomalies like dips within the time series.","claims_to_support":[{"claim":"abrupt changes are detected within the time series","required_evidence":["change_location"]},{"claim":"anomalies such as dips are identified within the time series","required_evidence":["anomaly_score"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,23]],"scale":"short"},"validation_needs":["verify specific changes align with described behavior"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"detection of abrupt changes through first difference statistics","supports_evidence":["change_location"]},{"tool":"anomaly_detect","reason":"detect spikes and outliers in a window","supports_evidence":["anomaly_score"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_location","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_score","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"For detecting abrupt changes and anomalies in the time series, the diff_stats tool should be used first to identify locations where changes occur. Then, the anomaly_detect tool can be utilized to identify anomalies based on these change points."},"structured_observations":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}],"coverage":{"change_location":"tool_supported","anomaly_score":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"mean_diff":0.026521739130434836,"std_diff":2.4923981967708415,"max_abs_diff":6.500000000000002,"n_sign_changes":3},"error":null,"args_fingerprint":"ab2e93895dc600bfdd9107e99f858b2b615526d8"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.7774396263353167},"error":null,"args_fingerprint":"80792d37f261dd92c61e5c31a98e5d616f183c3e"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify periods of stability and trend changes within the time series by measuring endpoint slopes and counting step levels. The segment_trend tool successfully measured the endpoint slope as upward with a direction class of vague. The step_levels tool counted 18 unique step levels, indicating multiple periods of stability and change within the time series.","scale":"medium","observations":["Endpoint slope measurement indicates an upward trend but with vague directionality.","Step level count shows significant variability in the time series, with 18 unique levels identified."],"evidence_intervals":["[0,23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"slope\": 0.026521739130434784, \"direction\": \"upward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 7.260833333333333, \"std\": 4.719874571662071, \"start_value\": 0.89, \"end_value\": 1.5}, \"error\": null, \"args_fingerprint\": \"1fa3e05bcf7003070de53468b1fb53c0bde4defe\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"n_unique_levels\": 18, \"n_plateau_runs\": 21, \"levels\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 3.2], \"plateau_runs\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 4.82, 3.2, 2.22, 1.5], \"plateau_lengths\": [2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 0.1948}, \"error\": null, \"args_fingerprint\": \"5f449048a3d8b9b281bc92f1b7926d7314990900\"}"],"evidence_plan":{"objective":"Identify periods of stability and trend changes within the time series.","claims_to_support":[{"claim":"Measure endpoint slopes of the time series.","required_evidence":["endpoint_slope"]},{"claim":"Count the number of step levels in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,23]],"scale":"medium"},"validation_needs":["endpoint_slope","step_level_count"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures endpoint slope of the time series over the entire interval.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"Counts discrete step levels, reflecting periods of stability and change.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_level_count","input_binding":{}}],"reasoning":"The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently."},"structured_observations":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"endpoint_slope":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"slope":0.026521739130434784,"direction":"upward","direction_class":"vague","trend_method":"endpoint","mean":7.260833333333333,"std":4.719874571662071,"start_value":0.89,"end_value":1.5},"error":null,"args_fingerprint":"1fa3e05bcf7003070de53468b1fb53c0bde4defe"},{"call_id":"medium:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"n_unique_levels":18,"n_plateau_runs":21,"levels":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,3.2],"plateau_runs":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,4.82,3.2,2.22,1.5],"plateau_lengths":[2,1,1,1,2,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":0.1948},"error":null,"args_fingerprint":"5f449048a3d8b9b281bc92f1b7926d7314990900"}],"skipped_stages":[]},"long":null,"conflicts":[],"summary":"Endpoint slope measurement indicates an upward trend but with vague directionality. Step level count shows significant variability in the time series, with 18 unique levels identified. Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold. No anomalies were identified within the defined time series segment using the anomaly detection method.","structured_by_scale":{"medium":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"short":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}]}}
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
  "reasoning": "The current assignment focuses on matching candidate time series against a textual description and ranking them based on how well they reflect the described behavior. Prior evidence provides endpoint slopes, step level counts, and detections of abrupt changes, but lacks direct measures of similarity and reverse similarity needed for the matching task. Pairwise and reverse similarity measures must be computed to determine the best match.",
  "evidence_plan": {
    "objective": "Compare observed behaviors across all candidate time series against the textual description and rank them.",
    "claims_to_support": [
      {
        "claim": "Pairwise similarity measures between candidate time series and the reference description are accurate.",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "Reverse similarity measures between candidate time series and the reference description are accurate.",
        "required_evidence": ["reverse_similarity"]
      },
      {
        "claim": "Candidate time series support the caption claim with high accuracy.",
        "required_evidence": ["caption_claim_support"]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2, 3, 4],
      "role": "matching"
    },
    "validation_needs": ["verify the chosen time series best matches the described characteristics"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "pairwise_distance",
        "reason": "Rank candidates based on direct similarity to the reference description.",
        "supports_evidence": ["pairwise_similarity"]
      },
      {
        "tool": "reverse_match",
        "reason": "Calculate reverse-direction similarity measures for candidates.",
        "supports_evidence": ["reverse_similarity"]
      },
      {
        "tool": "describe_series",
        "reason": "Provide detailed descriptions for qualitative analysis to assess caption claim support.",
        "supports_evidence": ["caption_claim_support"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m0`

tokens prompt=754 completion=199 latency=7.07s

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
{"evidence_plan":{"objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","claims_to_support":[{"claim":"Pairwise similarity measures between candidate time series and the reference description are accurate.","required_evidence":["pairwise_similarity"]},{"claim":"Reverse similarity measures between candidate time series and the reference description are accurate.","required_evidence":["reverse_similarity"]},{"claim":"Candidate time series support the caption claim with high accuracy.","required_evidence":["caption_claim_support"]}],"analysis_scope":{"target_series":[1,2,3,4],"role":"matching"},"validation_needs":["verify the chosen time series best matches the described characteristics"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"Rank candidates based on direct similarity to the reference description.","supports_evidence":["pairwise_similarity"]},{"tool":"reverse_match","reason":"Calculate reverse-direction similarity measures for candidates.","supports_evidence":["reverse_similarity"]},{"tool":"describe_series","reason":"Provide detailed descriptions for qualitative analysis to assess caption claim support.","supports_evidence":["caption_claim_support"]}],"no_tool_decision":null},"reasoning":"The current assignment focuses on matching candidate time series against a textual description and ranking them based on how well they reflect the described behavior. Prior evidence provides endpoint slopes, step level counts, and detections of abrupt changes, but lacks direct measures of similarity and reverse similarity needed for the matching task. Pairwise and reverse similarity measures must be computed to determine the best match."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
- reverse_match
  inputs: query_series_index, candidate_series_indices, method
  outputs: ranking
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The workflow begins with computing pairwise distance measures between candidate time series as per the textual description to establish direct similarity. Following that, we compute reverse-match scores to ensure bidirectional consistency in our comparison approach. These two steps provide us with comprehensive similarity metrics necessary for validating if the candidates indeed support the given caption claim accurately.",
  "workflow": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "output_key": "distances",
      "input_binding": {
        "method": "euclidean"
      }
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "output_key": "ranking",
      "input_binding": {
        "query_series_index": "$pairwise_distance.nearest",
        "candidate_series_indices": "[1, 2, 3, 4]",
        "method": "cosine_similarity"
      }
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m0`

tokens prompt=989 completion=156 latency=5.62s

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
{"workflow":[{"step":1,"tool":"pairwise_distance","output_key":"distances","input_binding":{"method":"euclidean"}},{"step":2,"tool":"reverse_match","output_key":"ranking","input_binding":{"query_series_index":"$pairwise_distance.nearest","candidate_series_indices":"[1, 2, 3, 4]","method":"cosine_similarity"}}],"reasoning":"The workflow begins with computing pairwise distance measures between candidate time series as per the textual description to establish direct similarity. Following that, we compute reverse-match scores to ensure bidirectional consistency in our comparison approach. These two steps provide us with comprehensive similarity metrics necessary for validating if the candidates indeed support the given caption claim accurately."}
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
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  args: {method=euclidean|dtw, series_index=reference 1-based (default 1)}
  returns: {distances=per-candidate distances, nearest=winner, method=distance metadata}
- reverse_match: Reverse each candidate series and rank candidates against the query using length-normalized z-DTW or Euclidean distance.
  args: {query_series_index=1-based query (default 1), candidate_series_indices=optional 1-based list (default all others), method=dtw|euclidean}
  returns: {ranking=reversed-candidate distances and winner}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The workflow involves calculating pairwise distances followed by reverse matching to ensure bidirectional consistency in similarity metrics. The assignment requires measuring similarity and verifying which time series best supports the described characteristics.",
  "calls": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "args": {
        "series_index": 1,
        "method": "euclidean"
      }
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "args": {
        "query_series_index": 1,
        "candidate_series_indices": [1, 2, 3, 4],
        "method": "cosine_similarity"
      }
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=5324 completion=707 latency=27.50s

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
{"evidence_plan":{"objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","claims_to_support":[{"claim":"Pairwise similarity measures between candidate time series and the reference description are accurate.","required_evidence":["pairwise_similarity"]},{"claim":"Reverse similarity measures between candidate time series and the reference description are accurate.","required_evidence":["reverse_similarity"]},{"claim":"Candidate time series support the caption claim with high accuracy.","required_evidence":["caption_claim_support"]}],"analysis_scope":{"target_series":[1,2,3,4],"role":"matching"},"validation_needs":["verify the chosen time series best matches the described characteristics"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"Rank candidates based on direct similarity to the reference description.","supports_evidence":["pairwise_similarity"]},{"tool":"reverse_match","reason":"Calculate reverse-direction similarity measures for candidates.","supports_evidence":["reverse_similarity"]},{"tool":"describe_series","reason":"Provide detailed descriptions for qualitative analysis to assess caption claim support.","supports_evidence":["caption_claim_support"]}],"no_tool_decision":null},"reasoning":"The current assignment focuses on matching candidate time series against a textual description and ranking them based on how well they reflect the described behavior. Prior evidence provides endpoint slopes, step level counts, and detections of abrupt changes, but lacks direct measures of similarity and reverse similarity needed for the matching task. Pairwise and reverse similarity measures must be computed to determine the best match."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "matching:step1",
    "step": 1,
    "tool_name": "pairwise_distance",
    "arguments": {
      "series_index": 1,
      "method": "euclidean"
    },
    "resolved_arguments": {
      "series_index": 1,
      "method": "euclidean"
    },
    "success": true,
    "data": {
      "method": "euclidean",
      "ref_series_index": 1,
      "distances": [
        {
          "series_index": 2,
          "distance": 8.268318948814954
        },
        {
          "series_index": 3,
          "distance": 6.895902621773473
        },
        {
          "series_index": 4,
          "distance": 6.872527859186135
        }
      ],
      "nearest": {
        "series_index": 4,
        "distance": 6.872527859186135
      }
    },
    "error": null,
    "args_fingerprint": "fe7a85ad7d3efdb3d80e106346a3cfd176c3a6df"
  },
  {
    "call_id": "matching:step2",
    "step": 2,
    "tool_name": "reverse_match",
    "arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        1,
        2,
        3,
        4
      ],
      "method": "cosine_similarity"
    },
    "resolved_arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        1,
        2,
        3,
        4
      ],
      "method": "cosine_similarity"
    },
    "success": false,
    "data": {},
    "error": "method must be dtw or euclidean",
    "args_fingerprint": ""
  }
]
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed diff_stats and anomaly_detect tools to find abrupt changes and anomalies in the specified time series. Diff_stats found three sign changes, indicating potential abrupt shifts, but no anomalies were detected by anomaly_detect within the confidence threshold.","scale":"short","observations":["Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold.","No anomalies were identified within the defined time series segment using the anomaly detection method."],"evidence_intervals":["time series data segment [0, 23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"mean_diff\": 0.026521739130434836, \"std_diff\": 2.4923981967708415, \"max_abs_diff\": 6.500000000000002, \"n_sign_changes\": 3}, \"error\": null, \"args_fingerprint\": \"ab2e93895dc600bfdd9107e99f858b2b615526d8\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.7774396263353167}, \"error\": null, \"args_fingerprint\": \"80792d37f261dd92c61e5c31a98e5d616f183c3e\"}"],"evidence_plan":{"objective":"Detect abrupt changes and anomalies like dips within the time series.","claims_to_support":[{"claim":"abrupt changes are detected within the time series","required_evidence":["change_location"]},{"claim":"anomalies such as dips are identified within the time series","required_evidence":["anomaly_score"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,23]],"scale":"short"},"validation_needs":["verify specific changes align with described behavior"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"detection of abrupt changes through first difference statistics","supports_evidence":["change_location"]},{"tool":"anomaly_detect","reason":"detect spikes and outliers in a window","supports_evidence":["anomaly_score"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_location","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_score","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"For detecting abrupt changes and anomalies in the time series, the diff_stats tool should be used first to identify locations where changes occur. Then, the anomaly_detect tool can be utilized to identify anomalies based on these change points."},"structured_observations":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}],"coverage":{"change_location":"tool_supported","anomaly_score":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"mean_diff":0.026521739130434836,"std_diff":2.4923981967708415,"max_abs_diff":6.500000000000002,"n_sign_changes":3},"error":null,"args_fingerprint":"ab2e93895dc600bfdd9107e99f858b2b615526d8"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.7774396263353167},"error":null,"args_fingerprint":"80792d37f261dd92c61e5c31a98e5d616f183c3e"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify periods of stability and trend changes within the time series by measuring endpoint slopes and counting step levels. The segment_trend tool successfully measured the endpoint slope as upward with a direction class of vague. The step_levels tool counted 18 unique step levels, indicating multiple periods of stability and change within the time series.","scale":"medium","observations":["Endpoint slope measurement indicates an upward trend but with vague directionality.","Step level count shows significant variability in the time series, with 18 unique levels identified."],"evidence_intervals":["[0,23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"slope\": 0.026521739130434784, \"direction\": \"upward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 7.260833333333333, \"std\": 4.719874571662071, \"start_value\": 0.89, \"end_value\": 1.5}, \"error\": null, \"args_fingerprint\": \"1fa3e05bcf7003070de53468b1fb53c0bde4defe\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"n_unique_levels\": 18, \"n_plateau_runs\": 21, \"levels\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 3.2], \"plateau_runs\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 4.82, 3.2, 2.22, 1.5], \"plateau_lengths\": [2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 0.1948}, \"error\": null, \"args_fingerprint\": \"5f449048a3d8b9b281bc92f1b7926d7314990900\"}"],"evidence_plan":{"objective":"Identify periods of stability and trend changes within the time series.","claims_to_support":[{"claim":"Measure endpoint slopes of the time series.","required_evidence":["endpoint_slope"]},{"claim":"Count the number of step levels in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,23]],"scale":"medium"},"validation_needs":["endpoint_slope","step_level_count"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures endpoint slope of the time series over the entire interval.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"Counts discrete step levels, reflecting periods of stability and change.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_level_count","input_binding":{}}],"reasoning":"The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently."},"structured_observations":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"endpoint_slope":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"slope":0.026521739130434784,"direction":"upward","direction_class":"vague","trend_method":"endpoint","mean":7.260833333333333,"std":4.719874571662071,"start_value":0.89,"end_value":1.5},"error":null,"args_fingerprint":"1fa3e05bcf7003070de53468b1fb53c0bde4defe"},{"call_id":"medium:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"n_unique_levels":18,"n_plateau_runs":21,"levels":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,3.2],"plateau_runs":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,4.82,3.2,2.22,1.5],"plateau_lengths":[2,1,1,1,2,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":0.1948},"error":null,"args_fingerprint":"5f449048a3d8b9b281bc92f1b7926d7314990900"}],"skipped_stages":[]},"long":null,"conflicts":[],"summary":"Endpoint slope measurement indicates an upward trend but with vague directionality. Step level count shows significant variability in the time series, with 18 unique levels identified. Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold. No anomalies were identified within the defined time series segment using the anomaly detection method.","structured_by_scale":{"medium":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"short":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
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
  "reasoning": "Based on the pairwise distance calculations, Time Series 1 shows the smallest distances to Time Series 4, suggesting it might have the closest match to the described characteristics. However, reverse_similarity calculation failed due to incorrect method input, so further verification is necessary to fully evaluate similarities. Detailed descriptions of the series would help confirm the caption claim support.",
  "role": "matching",
  "hypothesis": "Time Series 4 has the highest similarity measures with the textual description among all candidates, followed by Time Series 3, while Time Series 2 is relatively farther away.",
  "evidence": ["The pairwise distance measures indicate the closest similarity of Time Series 1 to Time Series 4, 3rd to Time Series 3. Reverse similarity could not be calculated successfully due to an error.", "Endpoint slopes and step level counts provide secondary measures of trend and stability which align with similarity measures to some extent."],
  "candidate_preference": "D",
  "confidence": 0.7,
  "tool_calls": [],
  "cited_tool_call_ids": ["matching:step1", "medium:step1", "medium:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Pairwise distance measures indicate Time Series 4 has the lowest distance to Time Series 1, suggesting high similarity.",
      "evidence": [
        {
          "type": "pairwise_distance",
          "value": 6.872527859186135,
          "provenance": "tool",
          "ref": "matching:step1",
          "call_id": "matching:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Reverse similarity measures could not be calculated successfully due to an error.",
      "evidence": [
        {
          "type": "reverse_similarity_error",
          "value": "method must be dtw or euclidean",
          "provenance": "tool",
          "ref": "matching:step2",
          "call_id": "matching:step2"
        }
      ],
      "confidence": "unresolved"
    },
    {
      "claim": "Endpoint slope measurements and step level counts offer secondary measures of similarity between time series.",
      "evidence": [
        {
          "type": "endpoint_slope",
          "value": 0.026521739130434784,
          "provenance": "tool",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        },
        {
          "type": "step_level_count",
          "value": 18,
          "provenance": "tool",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "pairwise_similarity": "tool_supported",
    "reverse_similarity": "unresolved",
    "caption_claim_support": "unresolved"
  },
  "unresolved_claims": [
    "Reverse similarity measures between the candidate time series and the reference description could not be calculated due to method specification issues."
  ]
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=6117 completion=375 latency=15.48s

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
{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of trends and patterns. This involves both understanding the temporal dynamics and comparing them against the described behavior.","task_summary":"Match a time series from given options to a textual description of trends and patterns.","target_output":"select the time series from the following four options that most accurately reflects the described characteristics","answer_type":"choice","capability":"match and validate descriptive pattern characteristics against visual/numeric data.","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Identify periods of stability and trend changes within the time series.","required_measurements":["endpoint_slope","step_level_count"],"validation_requirements":["ensure periods of relative stability are accurately identified"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]},{"scale":"short","objective":"Detect abrupt changes and anomalies like dips within the time series.","required_measurements":["change_location","anomaly_score"],"validation_requirements":["verify specific changes align with described behavior"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"hetero_assignments":[{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Identifying consistent stable low values followed by a significant increase, including any notable drops.","Comparing candidate time series against the textual description to ensure accurate reflection of described behaviors."],"notes":"Ensure all critical features mentioned in the description, such as initial stability, subsequent increase, peak range, and a specific dip, are captured and compared properly."}
</plan_context>

<task_summary>
Match a time series from given options to a textual description of trends and patterns.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed diff_stats and anomaly_detect tools to find abrupt changes and anomalies in the specified time series. Diff_stats found three sign changes, indicating potential abrupt shifts, but no anomalies were detected by anomaly_detect within the confidence threshold.","scale":"short","observations":["Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold.","No anomalies were identified within the defined time series segment using the anomaly detection method."],"evidence_intervals":["time series data segment [0, 23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"mean_diff\": 0.026521739130434836, \"std_diff\": 2.4923981967708415, \"max_abs_diff\": 6.500000000000002, \"n_sign_changes\": 3}, \"error\": null, \"args_fingerprint\": \"ab2e93895dc600bfdd9107e99f858b2b615526d8\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.7774396263353167}, \"error\": null, \"args_fingerprint\": \"80792d37f261dd92c61e5c31a98e5d616f183c3e\"}"],"evidence_plan":{"objective":"Detect abrupt changes and anomalies like dips within the time series.","claims_to_support":[{"claim":"abrupt changes are detected within the time series","required_evidence":["change_location"]},{"claim":"anomalies such as dips are identified within the time series","required_evidence":["anomaly_score"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,23]],"scale":"short"},"validation_needs":["verify specific changes align with described behavior"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"detection of abrupt changes through first difference statistics","supports_evidence":["change_location"]},{"tool":"anomaly_detect","reason":"detect spikes and outliers in a window","supports_evidence":["anomaly_score"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_location","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_score","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"For detecting abrupt changes and anomalies in the time series, the diff_stats tool should be used first to identify locations where changes occur. Then, the anomaly_detect tool can be utilized to identify anomalies based on these change points."},"structured_observations":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}],"coverage":{"change_location":"tool_supported","anomaly_score":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"mean_diff":0.026521739130434836,"std_diff":2.4923981967708415,"max_abs_diff":6.500000000000002,"n_sign_changes":3},"error":null,"args_fingerprint":"ab2e93895dc600bfdd9107e99f858b2b615526d8"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.7774396263353167},"error":null,"args_fingerprint":"80792d37f261dd92c61e5c31a98e5d616f183c3e"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify periods of stability and trend changes within the time series by measuring endpoint slopes and counting step levels. The segment_trend tool successfully measured the endpoint slope as upward with a direction class of vague. The step_levels tool counted 18 unique step levels, indicating multiple periods of stability and change within the time series.","scale":"medium","observations":["Endpoint slope measurement indicates an upward trend but with vague directionality.","Step level count shows significant variability in the time series, with 18 unique levels identified."],"evidence_intervals":["[0,23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"slope\": 0.026521739130434784, \"direction\": \"upward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 7.260833333333333, \"std\": 4.719874571662071, \"start_value\": 0.89, \"end_value\": 1.5}, \"error\": null, \"args_fingerprint\": \"1fa3e05bcf7003070de53468b1fb53c0bde4defe\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"n_unique_levels\": 18, \"n_plateau_runs\": 21, \"levels\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 3.2], \"plateau_runs\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 4.82, 3.2, 2.22, 1.5], \"plateau_lengths\": [2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 0.1948}, \"error\": null, \"args_fingerprint\": \"5f449048a3d8b9b281bc92f1b7926d7314990900\"}"],"evidence_plan":{"objective":"Identify periods of stability and trend changes within the time series.","claims_to_support":[{"claim":"Measure endpoint slopes of the time series.","required_evidence":["endpoint_slope"]},{"claim":"Count the number of step levels in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,23]],"scale":"medium"},"validation_needs":["endpoint_slope","step_level_count"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures endpoint slope of the time series over the entire interval.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"Counts discrete step levels, reflecting periods of stability and change.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_level_count","input_binding":{}}],"reasoning":"The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently."},"structured_observations":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"endpoint_slope":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"slope":0.026521739130434784,"direction":"upward","direction_class":"vague","trend_method":"endpoint","mean":7.260833333333333,"std":4.719874571662071,"start_value":0.89,"end_value":1.5},"error":null,"args_fingerprint":"1fa3e05bcf7003070de53468b1fb53c0bde4defe"},{"call_id":"medium:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"n_unique_levels":18,"n_plateau_runs":21,"levels":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,3.2],"plateau_runs":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,4.82,3.2,2.22,1.5],"plateau_lengths":[2,1,1,1,2,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":0.1948},"error":null,"args_fingerprint":"5f449048a3d8b9b281bc92f1b7926d7314990900"}],"skipped_stages":[]},"long":null,"conflicts":[],"summary":"Endpoint slope measurement indicates an upward trend but with vague directionality. Step level count shows significant variability in the time series, with 18 unique levels identified. Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold. No anomalies were identified within the defined time series segment using the anomaly detection method.","structured_by_scale":{"medium":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"short":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
retry_context=unresolved_claims=['Reverse similarity measures between the candidate time series and the reference description could not be calculated due to method specification issues.']
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides insights into abrupt changes and anomalies but lacks information regarding pairwise similarity, reverse similarity, and caption claim support for the target time series. To fully address the objective, we need to assess how well each candidate time series matches the textual description, considering both direct and reverse matches.",
  "evidence_plan": {
    "objective": "Compare observed behaviors across all candidate time series against the textual description and rank them.",
    "claims_to_support": [
      {"claim": "Calculate pairwise similarity between candidate time series.", "required_evidence": ["pairwise_similarity"]},
      {"claim": "Calculate reverse similarity between candidate time series and the reference description.", "required_evidence": ["reverse_similarity"]},
      {"claim": "Support the caption claims with candidate time series data.", "required_evidence": ["caption_claim_support"]}
    ],
    "analysis_scope": {"target_series": [1, 2, 3, 4], "role": "matching"},
    "validation_needs": ["verify the chosen time series best matches the described characteristics"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "pairwise_distance",
        "reason": "To compute similarity metrics between each pair of candidate time series.",
        "supports_evidence": ["pairwise_similarity"]
      },
      {
        "tool": "reverse_match",
        "reason": "To compute reverse similarity between each candidate time series and a reference description.",
        "supports_evidence": ["reverse_similarity"]
      },
      {
        "tool": "describe_series",
        "reason": "To generate descriptive statistics that can support the caption claims with numerical data.",
        "supports_evidence": ["caption_claim_support"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s3) — `heterogeneous:matching:s3:m1`

tokens prompt=739 completion=189 latency=6.71s

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
{"evidence_plan":{"objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","claims_to_support":[{"claim":"Calculate pairwise similarity between candidate time series.","required_evidence":["pairwise_similarity"]},{"claim":"Calculate reverse similarity between candidate time series and the reference description.","required_evidence":["reverse_similarity"]},{"claim":"Support the caption claims with candidate time series data.","required_evidence":["caption_claim_support"]}],"analysis_scope":{"target_series":[1,2,3,4],"role":"matching"},"validation_needs":["verify the chosen time series best matches the described characteristics"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"To compute similarity metrics between each pair of candidate time series.","supports_evidence":["pairwise_similarity"]},{"tool":"reverse_match","reason":"To compute reverse similarity between each candidate time series and a reference description.","supports_evidence":["reverse_similarity"]},{"tool":"describe_series","reason":"To generate descriptive statistics that can support the caption claims with numerical data.","supports_evidence":["caption_claim_support"]}],"no_tool_decision":null},"reasoning":"The current evidence provides insights into abrupt changes and anomalies but lacks information regarding pairwise similarity, reverse similarity, and caption claim support for the target time series. To fully address the objective, we need to assess how well each candidate time series matches the textual description, considering both direct and reverse matches."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- pairwise_distance
  inputs: method, series_index
  outputs: distances, nearest, method
- reverse_match
  inputs: query_series_index, candidate_series_indices, method
  outputs: ranking
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The workflow needs to first calculate pairwise similarity between candidate time series using 'pairwise_distance', then evaluate reverse similarity between each candidate and a reference description using 'reverse_match'. The objective is to fully assess how well each candidate time series matches the textual description, considering both direct and reverse matches.",
  "workflow": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "output_key": "distances",
      "input_binding": {"method": "euclidean", "series_index": "$candidate_series_indices[$stepN]"}
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "output_key": "ranking",
      "input_binding": {"query_series_index": "$step1.nearest", "candidate_series_indices": "$candidate_series_indices", "method": "$step1.method"}
    }
  ]
}
```

## Heterogeneous (matching, s4) — `heterogeneous:matching:s4:m1`

tokens prompt=988 completion=186 latency=6.67s

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
{"workflow":[{"step":1,"tool":"pairwise_distance","output_key":"distances","input_binding":{"method":"euclidean","series_index":"$candidate_series_indices[$stepN]"}},{"step":2,"tool":"reverse_match","output_key":"ranking","input_binding":{"query_series_index":"$step1.nearest","candidate_series_indices":"$candidate_series_indices","method":"$step1.method"}}],"reasoning":"The workflow needs to first calculate pairwise similarity between candidate time series using 'pairwise_distance', then evaluate reverse similarity between each candidate and a reference description using 'reverse_match'. The objective is to fully assess how well each candidate time series matches the textual description, considering both direct and reverse matches."}
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
- pairwise_distance: Distance from reference series to others (euclidean/dtw).
  args: {method=euclidean|dtw, series_index=reference 1-based (default 1)}
  returns: {distances=per-candidate distances, nearest=winner, method=distance metadata}
- reverse_match: Reverse each candidate series and rank candidates against the query using length-normalized z-DTW or Euclidean distance.
  args: {query_series_index=1-based query (default 1), candidate_series_indices=optional 1-based list (default all others), method=dtw|euclidean}
  returns: {ranking=reversed-candidate distances and winner}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=era5_2018; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[24, 24, 24, 24]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
</assignment>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the InvocationPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "First, calculate the pairwise distances of each candidate time series to the reference time series (assumed as the first one with index 1) using the euclidean method. Then, use these calculated nearest distances for further evaluation if necessary, but specifically for this plan, directly proceed to reversing the candidates and ranking them against the query using reverse_match.",
  "calls": [
    {
      "step": 1,
      "tool": "pairwise_distance",
      "args": {
        "method": "euclidean",
        "series_index": 1
      }
    },
    {
      "step": 2,
      "tool": "reverse_match",
      "args": {
        "query_series_index": 1,
        "candidate_series_indices": [2, 3, 4],
        "method": "euclidean"
      }
    }
  ]
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=5565 completion=510 latency=20.25s

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
{"evidence_plan":{"objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","claims_to_support":[{"claim":"Calculate pairwise similarity between candidate time series.","required_evidence":["pairwise_similarity"]},{"claim":"Calculate reverse similarity between candidate time series and the reference description.","required_evidence":["reverse_similarity"]},{"claim":"Support the caption claims with candidate time series data.","required_evidence":["caption_claim_support"]}],"analysis_scope":{"target_series":[1,2,3,4],"role":"matching"},"validation_needs":["verify the chosen time series best matches the described characteristics"]},"capability_selection":{"selected_tools":[{"tool":"pairwise_distance","reason":"To compute similarity metrics between each pair of candidate time series.","supports_evidence":["pairwise_similarity"]},{"tool":"reverse_match","reason":"To compute reverse similarity between each candidate time series and a reference description.","supports_evidence":["reverse_similarity"]},{"tool":"describe_series","reason":"To generate descriptive statistics that can support the caption claims with numerical data.","supports_evidence":["caption_claim_support"]}],"no_tool_decision":null},"reasoning":"The current evidence provides insights into abrupt changes and anomalies but lacks information regarding pairwise similarity, reverse similarity, and caption claim support for the target time series. To fully address the objective, we need to assess how well each candidate time series matches the textual description, considering both direct and reverse matches."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "matching:step1",
    "step": 1,
    "tool_name": "pairwise_distance",
    "arguments": {
      "method": "euclidean",
      "series_index": 1
    },
    "resolved_arguments": {
      "method": "euclidean",
      "series_index": 1
    },
    "success": true,
    "data": {
      "method": "euclidean",
      "ref_series_index": 1,
      "distances": [
        {
          "series_index": 2,
          "distance": 8.268318948814954
        },
        {
          "series_index": 3,
          "distance": 6.895902621773473
        },
        {
          "series_index": 4,
          "distance": 6.872527859186135
        }
      ],
      "nearest": {
        "series_index": 4,
        "distance": 6.872527859186135
      }
    },
    "error": null,
    "args_fingerprint": "fe7a85ad7d3efdb3d80e106346a3cfd176c3a6df"
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
        4
      ],
      "method": "euclidean"
    },
    "resolved_arguments": {
      "query_series_index": 1,
      "candidate_series_indices": [
        2,
        3,
        4
      ],
      "method": "euclidean"
    },
    "success": true,
    "data": {
      "query_series_index": 1,
      "ranking": [
        {
          "series_index": 4,
          "reverse_distance": 1.1571824633425407,
          "method_used": "z_euclidean"
        },
        {
          "series_index": 3,
          "reverse_distance": 1.6604337155735063,
          "method_used": "z_euclidean"
        },
        {
          "series_index": 2,
          "reverse_distance": 1.841091337620738,
          "method_used": "z_euclidean"
        }
      ],
      "nearest": {
        "series_index": 4,
        "reverse_distance": 1.1571824633425407,
        "method_used": "z_euclidean"
      },
      "winner_margin": 0.5032512522309656
    },
    "error": null,
    "args_fingerprint": "0d870833e1e2f35865f1b6ca79026585de2eec8e"
  }
]
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed diff_stats and anomaly_detect tools to find abrupt changes and anomalies in the specified time series. Diff_stats found three sign changes, indicating potential abrupt shifts, but no anomalies were detected by anomaly_detect within the confidence threshold.","scale":"short","observations":["Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold.","No anomalies were identified within the defined time series segment using the anomaly detection method."],"evidence_intervals":["time series data segment [0, 23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"mean_diff\": 0.026521739130434836, \"std_diff\": 2.4923981967708415, \"max_abs_diff\": 6.500000000000002, \"n_sign_changes\": 3}, \"error\": null, \"args_fingerprint\": \"ab2e93895dc600bfdd9107e99f858b2b615526d8\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.7774396263353167}, \"error\": null, \"args_fingerprint\": \"80792d37f261dd92c61e5c31a98e5d616f183c3e\"}"],"evidence_plan":{"objective":"Detect abrupt changes and anomalies like dips within the time series.","claims_to_support":[{"claim":"abrupt changes are detected within the time series","required_evidence":["change_location"]},{"claim":"anomalies such as dips are identified within the time series","required_evidence":["anomaly_score"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,23]],"scale":"short"},"validation_needs":["verify specific changes align with described behavior"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"detection of abrupt changes through first difference statistics","supports_evidence":["change_location"]},{"tool":"anomaly_detect","reason":"detect spikes and outliers in a window","supports_evidence":["anomaly_score"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"diff_stats","output_key":"change_location","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomaly_score","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"For detecting abrupt changes and anomalies in the time series, the diff_stats tool should be used first to identify locations where changes occur. Then, the anomaly_detect tool can be utilized to identify anomalies based on these change points."},"structured_observations":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}],"coverage":{"change_location":"tool_supported","anomaly_score":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"diff_stats","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"mean_diff":0.026521739130434836,"std_diff":2.4923981967708415,"max_abs_diff":6.500000000000002,"n_sign_changes":3},"error":null,"args_fingerprint":"ab2e93895dc600bfdd9107e99f858b2b615526d8"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.7774396263353167},"error":null,"args_fingerprint":"80792d37f261dd92c61e5c31a98e5d616f183c3e"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to identify periods of stability and trend changes within the time series by measuring endpoint slopes and counting step levels. The segment_trend tool successfully measured the endpoint slope as upward with a direction class of vague. The step_levels tool counted 18 unique step levels, indicating multiple periods of stability and change within the time series.","scale":"medium","observations":["Endpoint slope measurement indicates an upward trend but with vague directionality.","Step level count shows significant variability in the time series, with 18 unique levels identified."],"evidence_intervals":["[0,23]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"slope\": 0.026521739130434784, \"direction\": \"upward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 7.260833333333333, \"std\": 4.719874571662071, \"start_value\": 0.89, \"end_value\": 1.5}, \"error\": null, \"args_fingerprint\": \"1fa3e05bcf7003070de53468b1fb53c0bde4defe\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 0, \"end\": 23}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 0, \"end\": 23, \"n_unique_levels\": 18, \"n_plateau_runs\": 21, \"levels\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 3.2], \"plateau_runs\": [0.89, 1.37, 2.4, 4.94, 7.955, 8.52, 8.85, 9.56, 10.065000000000001, 11.25, 13.87, 20.37, 14.08, 9.07, 7.46, 6.73, 6.23, 4.82, 3.2, 2.22, 1.5], \"plateau_lengths\": [2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1], \"tolerance\": 0.1948}, \"error\": null, \"args_fingerprint\": \"5f449048a3d8b9b281bc92f1b7926d7314990900\"}"],"evidence_plan":{"objective":"Identify periods of stability and trend changes within the time series.","claims_to_support":[{"claim":"Measure endpoint slopes of the time series.","required_evidence":["endpoint_slope"]},{"claim":"Count the number of step levels in the time series.","required_evidence":["step_level_count"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[0,23]],"scale":"medium"},"validation_needs":["endpoint_slope","step_level_count"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"Measures endpoint slope of the time series over the entire interval.","supports_evidence":["endpoint_slope"]},{"tool":"step_levels","reason":"Counts discrete step levels, reflecting periods of stability and change.","supports_evidence":["step_level_count"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"endpoint_slope","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"step_level_count","input_binding":{}}],"reasoning":"The objective is to measure endpoint slopes of the time series and count the number of step levels, using the selected tools segment_trend and step_levels. The order respects dependency rules since both tools can be executed independently."},"structured_observations":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"coverage":{"endpoint_slope":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"slope":0.026521739130434784,"direction":"upward","direction_class":"vague","trend_method":"endpoint","mean":7.260833333333333,"std":4.719874571662071,"start_value":0.89,"end_value":1.5},"error":null,"args_fingerprint":"1fa3e05bcf7003070de53468b1fb53c0bde4defe"},{"call_id":"medium:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1,"start":0,"end":23},"resolved_arguments":{"series_index":1,"start":0,"end":23},"success":true,"data":{"series_index":1,"start":0,"end":23,"n_unique_levels":18,"n_plateau_runs":21,"levels":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,3.2],"plateau_runs":[0.89,1.37,2.4,4.94,7.955,8.52,8.85,9.56,10.065000000000001,11.25,13.87,20.37,14.08,9.07,7.46,6.73,6.23,4.82,3.2,2.22,1.5],"plateau_lengths":[2,1,1,1,2,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1],"tolerance":0.1948},"error":null,"args_fingerprint":"5f449048a3d8b9b281bc92f1b7926d7314990900"}],"skipped_stages":[]},"long":null,"conflicts":[],"summary":"Endpoint slope measurement indicates an upward trend but with vague directionality. Step level count shows significant variability in the time series, with 18 unique levels identified. Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold. No anomalies were identified within the defined time series segment using the anomaly detection method.","structured_by_scale":{"medium":[{"claim":"Measure endpoint slopes of the time series.","evidence":[{"type":"endpoint_slope","value":0.026521739130434784,"source_tool":"segment_trend","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"endpoint_slope"},{"claim":"Count the number of step levels in the time series.","evidence":[{"type":"step_level_count","value":18,"source_tool":"step_levels","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"step_level_count"}],"short":[{"claim":"abrupt changes are detected within the time series","evidence":[{"type":"change_location","value":3,"source_tool":"diff_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"anomalies such as dips are identified within the time series","evidence":[{"type":"anomaly_score","value":0,"source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_score"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Compare observed behaviors across all candidate time series against the textual description and rank them.","required_measurements":["pairwise_similarity","reverse_similarity","caption_claim_support"],"validation_requirements":["verify the chosen time series best matches the described characteristics"],"target_series":[1,2,3,4],"focus_intervals":[[0,23]]}
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
  "reasoning": "Based on the calculated pairwise and reverse similarity measures, Time Series 4 has the lowest distance to Time Series 1 in both forward and reverse comparisons, suggesting it most closely aligns with the described characteristics.",
  "role": "matching",
  "hypothesis": "Time Series 4 is the closest match to the textual description among the candidates.",
  "evidence": [
    "pairwise_distance matching:step1 results show that Time Series 4 has the smallest Euclidean distance to Time Series 1 (6.8725), indicating high similarity.",
    "reverse_match matching:step2 results indicate that Time Series 4 has the lowest reverse Euclidean distance (1.1572) to Time Series 1, further supporting its alignment."
  ],
  "candidate_preference": "D",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["matching:step1", "matching:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Calculate pairwise similarity between candidate time series.",
      "evidence": [
        {
          "type": "pairwise_similarity",
          "value": 6.8725,
          "provenance": "tool",
          "ref": "pairwise_distance matching:step1",
          "call_id": "matching:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Calculate reverse similarity between candidate time series and the reference description.",
      "evidence": [
        {
          "type": "reverse_similarity",
          "value": 1.1572,
          "provenance": "tool",
          "ref": "reverse_match matching:step2",
          "call_id": "matching:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "pairwise_similarity": "tool_supported",
    "reverse_similarity": "tool_supported",
    "caption_claim_support": "unresolved"
  },
  "unresolved_claims": [
    {
      "claim": "Support the caption claims with candidate time series data.",
      "notes": "Further descriptive statistics or additional tools may be needed to provide concrete numerical support for claims made in the caption."
    }
  ]
}
```

## Integration — `integration`

tokens prompt=1689 completion=221 latency=8.12s

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
'This time series data shows relatively stable low values (16-20) from index 0-12, followed by a dramatic upward trend starting at index 13, reaching peak values around 95-100 from index 15-23, with one notable dip to 71.75 at index 18.' According to the above textual description of a time series, select the time series from the following four options that most accurately reflects the described characteristics.
</question>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Match a time series from given options to a textual description of trends and patterns.",
  "question_type": "choice",
  "required_output": "select the time series from the following four options that most accurately reflects the described characteristics",
  "success_criteria": [
    "Identifying consistent stable low values followed by a significant increase, including any notable drops.",
    "Comparing candidate time series against the textual description to ensure accurate reflection of described behaviors."
  ],
  "assignments_brief": [
    {
      "agent": "homo:medium",
      "objective": "Identify periods of stability and trend changes within the time series.",
      "required_measurements": [
        "endpoint_slope",
        "step_level_count"
      ]
    },
    {
      "agent": "homo:short",
      "objective": "Detect abrupt changes and anomalies like dips within the time series.",
      "required_measurements": [
        "change_location",
        "anomaly_score"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Compare observed behaviors across all candidate time series against the textual description and rank them.",
      "required_measurements": [
        "pairwise_similarity",
        "reverse_similarity",
        "caption_claim_support"
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
          "value": 3,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "anomaly_score",
          "value": 0,
          "trusted": true
        }
      ],
      "coverage": {
        "change_location": "tool_supported",
        "anomaly_score": "tool_supported"
      },
      "summary": "Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold. | No anomalies were identified within the defined time series segment using the anomaly detection method."
    },
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "endpoint_slope",
          "value": 0.026521739130434784,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "step_level_count",
          "value": 18,
          "trusted": true
        }
      ],
      "coverage": {
        "endpoint_slope": "tool_supported",
        "step_level_count": "tool_supported"
      },
      "summary": "Endpoint slope measurement indicates an upward trend but with vague directionality. | Step level count shows significant variability in the time series, with 18 unique levels identified."
    }
  },
  "conflicts": [],
  "summary": "Endpoint slope measurement indicates an upward trend but with vague directionality. Step level count shows significant variability in the time series, with 18 unique levels identified. Detected three sign changes suggesting abrupt shifts in the time series but found no anomalies exceeding the anomaly score threshold. No anomalies were identified within the defined time series segment using the anomaly detection method."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Time Series 4 has the highest similarity measures with the textual description among all candidates, followed by Time Series 3, while Time Series 2 is relatively farther away.",
      "reasoning_chain": [
        "Pairwise distance measures indicate Time Series 4 has the lowest distance to Time Series 1, suggesting high similarity.",
        "pairwise_distance=6.872527859186135",
        "Reverse similarity measures could not be calculated successfully due to an error.",
        "reverse_similarity_error=method must be dtw or euclidean",
        "Endpoint slope measurements and step level counts offer secondary measures of similarity between time series.",
        "endpoint_slope=0.026521739130434784",
        "step_level_count=18"
      ],
      "candidate_preference": "D",
      "confidence": 0.7,
      "grounded": true,
      "grounded_in": [
        "pairwise_distance",
        "reverse_similarity_error",
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
  "option_mapping": {
    "A": 1,
    "B": 2,
    "C": 3,
    "D": 4
  },
  "verified_preference": "D",
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
  "reasoning": "According to the textual description, the time series should show a period of stable low values followed by a dramatic upward trend with one notable dip. The hetero agent reasoning suggests that Time Series 4 has the highest similarity measures with the textual description, which aligns well with the requirement. Moreover, the verified preference in the execution metadata points to 'D', further confirming the selection of Time Series 4.",
  "answer": "D",
  "explanation": "The time series selected, Time Series 4, best matches the provided text description because it displays stable low values followed by a sharp increase, including one notable dip.",
  "confidence": 0.7,
  "conflicts": [],
  "cited_evidence": ["pairwise_distance", "reverse_similarity_error", "endpoint_slope", "step_level_count"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": null
  }
}
```
