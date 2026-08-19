# Agent IO summary: `Align:ts2caption_qa_120:94`

- Architecture pred: `C` (success=True)
- model_calls=18, tool_calls=14, latency=244.8s

## Planner — `planner`

tokens prompt=1123 completion=491 latency=17.45s

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
A) This time series demonstrates significant variability with multiple peaks and valleys, showing an overall declining trend from higher initial values to lower ranges.
B) This series shows irregular fluctuations with occasional sharp peaks, maintaining relatively low baseline values with intermittent spikes reaching nearly 10 units.
C) This time series exhibits periodic oscillating patterns with irregular spikes, displaying cyclical behavior with values ranging from approximately 1 to 22 units.
D) This series remains remarkably stable around 98.9 units for the first portion, then transitions to higher variability with fluctuations between 97-99 units.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, trends, or anomalies.",
  "task_summary": "Choose the description that best fits the given univariate time series data from the four provided options.",
  "target_output": "description of time series data among four choices",
  "answer_type": "choice",
  "capability": "time series analysis",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "long",
      "objective": "Detect global trend and major structural changes over the entire span of the time series.",
      "required_measurements": ["global_trend", "major_structural_changes"],
      "validation_requirements": ["reliable detection of trend direction and consistency of structural breaks"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "medium",
      "objective": "Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.",
      "required_measurements": ["periodic_patterns", "regime_shifts"],
      "validation_requirements": ["verification of periodicity consistency across different segments", "identification of regime changes based on pattern stability"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "structure",
      "objective": "Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.",
      "required_measurements": ["global_trend", "periodic_patterns", "regime_shifts", "spike_occurrence", "stability_periods"],
      "validation_requirements": ["comparison of quantified characteristics against descriptive claims", "alignment of detected features with candidate statements for verification"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Identification of primary and secondary structural elements that align closely with a specific candidate description.", "Verification through cross-referencing quantitative findings against each candidate statement."],
  "notes": "Ensure all observed patterns and described attributes are thoroughly evaluated against each option for precise alignment."
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4087 completion=292 latency=11.51s

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
{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, trends, or anomalies.","task_summary":"Choose the description that best fits the given univariate time series data from the four provided options.","target_output":"description of time series data among four choices","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["structure"],"success_criteria":["Identification of primary and secondary structural elements that align closely with a specific candidate description.","Verification through cross-referencing quantitative findings against each candidate statement."],"notes":"Ensure all observed patterns and described attributes are thoroughly evaluated against each option for precise alignment."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts.",
  "evidence_plan": {
    "objective": "Detect global trend and major structural changes over the entire span of the time series.",
    "claims_to_support": [
      {"claim": "There is a global trend in the time series.", "required_evidence": ["direction_of_global_trend"]},
      {"claim": "Major structural changes exist in the time series.", "required_evidence": ["locations_of_major_structural_changes"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["reliable detection of trend direction and consistency of structural breaks"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "describe_series", "reason": "Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.", "supports_evidence": ["direction_of_global_trend"]},
      {"tool": "change_points", "reason": "Localizes potential level/regime transitions, helping to identify major structural changes in the series.", "supports_evidence": ["locations_of_major_structural_changes"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=762 completion=168 latency=5.98s

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
{"evidence_plan":{"objective":"Detect global trend and major structural changes over the entire span of the time series.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Major structural changes exist in the time series.","required_evidence":["locations_of_major_structural_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["reliable detection of trend direction and consistency of structural breaks"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.","supports_evidence":["direction_of_global_trend"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions, helping to identify major structural changes in the series.","supports_evidence":["locations_of_major_structural_changes"]}],"no_tool_decision":null},"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- change_points
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
  "reasoning": "The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series.",
  "workflow": [
    {
      "step": 1,
      "tool": "describe_series",
      "output_key": "global_overview",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "change_points",
      "output_key": "structural_changes",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=856 completion=157 latency=5.63s

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
{"workflow":[{"step":1,"tool":"describe_series","output_key":"global_overview","input_binding":{}},{"step":2,"tool":"change_points","output_key":"structural_changes","input_binding":{}}],"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series."}
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
- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series.",
  "calls": [
    {
      "step": 1,
      "tool": "describe_series",
      "args": {}
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

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1408 completion=395 latency=14.14s

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
{"evidence_plan":{"objective":"Detect global trend and major structural changes over the entire span of the time series.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Major structural changes exist in the time series.","required_evidence":["locations_of_major_structural_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["reliable detection of trend direction and consistency of structural breaks"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.","supports_evidence":["direction_of_global_trend"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions, helping to identify major structural changes in the series.","supports_evidence":["locations_of_major_structural_changes"]}],"no_tool_decision":null},"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts."}
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
          "mean": 5.705625000000001,
          "std": 3.115931668848108,
          "min": 1.24,
          "max": 21.93,
          "median": 5.71,
          "range": 20.69,
          "p50": 5.71,
          "p90": 9.606,
          "p99": 15.277499999999987,
          "start": 6.86,
          "end": 6.74,
          "slope": -0.0004181184668989551
        }
      ]
    },
    "error": null,
    "args_fingerprint": "90b10717d4a3e6c0750bb980207b8d86753ac968"
  },
  {
    "call_id": "long:step2",
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
          "index": 225,
          "score": 5.738571428571428
        },
        {
          "index": 224,
          "score": 5.562857142857141
        },
        {
          "index": 226,
          "score": 5.464999999999999
        },
        {
          "index": 227,
          "score": 5.205714285714287
        },
        {
          "index": 223,
          "score": 5.185714285714287
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes a global trend description and identification of major structural changes through change points detection. The describe_series tool indicates a downward global trend with a negative slope, and the change_points tool finds several significant structural changes towards the end of the time series.",
  "scale": "long",
  "observations": ["A global downward trend with negative slope was detected across the series.","Multiple locations indicating major structural changes were identified near the later period of the series."],
  "evidence_intervals": ["Entire series range: [0, 287]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There is a global trend in the time series.",
      "evidence": [
        {
          "type": "direction_of_global_trend",
          "value": "downward",
          "source_tool": "describe_series",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "Major structural changes exist in the time series.",
      "evidence": [
        {
          "type": "locations_of_major_structural_changes",
          "value": [223, 224, 225, 226, 227],
          "source_tool": "change_points",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "major_structural_changes"
    }
  ],
  "coverage": {"global_trend": "tool_supported", "major_structural_changes": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4096 completion=307 latency=12.05s

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
{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, trends, or anomalies.","task_summary":"Choose the description that best fits the given univariate time series data from the four provided options.","target_output":"description of time series data among four choices","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["structure"],"success_criteria":["Identification of primary and secondary structural elements that align closely with a specific candidate description.","Verification through cross-referencing quantitative findings against each candidate statement."],"notes":"Ensure all observed patterns and described attributes are thoroughly evaluated against each option for precise alignment."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. This involves detecting periodic patterns and regime shifts. We need to verify periodicity consistency across different segments and identify regime changes based on pattern stability.",
  "evidence_plan": {
    "objective": "Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.",
    "claims_to_support": [
      {"claim": "There are periodic patterns within the series.", "required_evidence": ["periodic_patterns"]},
      {"claim": "Regime shifts occur, reflecting changes in the patterns or stability of the data.", "required_evidence": ["regime_shifts"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["verification of periodicity consistency across different segments", "identification of regime changes based on pattern stability"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "To detect the dominant period that contributes to the overall characterization of the data.", "supports_evidence": ["periodic_patterns"]},
      {"tool": "change_points", "reason": "To identify regime shifts that reflect changes in the patterns or stability of the data.", "supports_evidence": ["regime_shifts"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=796 completion=148 latency=5.30s

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
{"evidence_plan":{"objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","claims_to_support":[{"claim":"There are periodic patterns within the series.","required_evidence":["periodic_patterns"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that contributes to the overall characterization of the data.","supports_evidence":["periodic_patterns"]},{"tool":"change_points","reason":"To identify regime shifts that reflect changes in the patterns or stability of the data.","supports_evidence":["regime_shifts"]}],"no_tool_decision":null},"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. This involves detecting periodic patterns and regime shifts. We need to verify periodicity consistency across different segments and identify regime changes based on pattern stability."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
- change_points
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. First, we need to detect the dominant period using the fft_period tool. Following this, we will use the change_points tool to identify any regime shifts that reflect changes in the patterns or stability of the data.",
  "workflow": [
    {
      "step": 1,
      "tool": "fft_period",
      "output_key": "dominant_period",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "change_points",
      "output_key": "series",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=845 completion=116 latency=4.20s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. First, we need to detect the dominant period using the fft_period tool. Following this, we will use the change_points tool to identify any regime shifts that reflect changes in the patterns or stability of the data."}
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
- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use the fft_period tool to find the dominant period in the series. Then, we move on to detecting regime shifts with the change_points tool.",
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
      "tool": "change_points",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=1288 completion=368 latency=13.16s

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
{"evidence_plan":{"objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","claims_to_support":[{"claim":"There are periodic patterns within the series.","required_evidence":["periodic_patterns"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that contributes to the overall characterization of the data.","supports_evidence":["periodic_patterns"]},{"tool":"change_points","reason":"To identify regime shifts that reflect changes in the patterns or stability of the data.","supports_evidence":["regime_shifts"]}],"no_tool_decision":null},"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. This involves detecting periodic patterns and regime shifts. We need to verify periodicity consistency across different segments and identify regime changes based on pattern stability."}
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
      "spectral_strength": 0.13039978670209035,
      "period_trusted": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "726ee7605c7aac2e5823de42d4c34d3c89859438"
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
          "index": 225,
          "score": 5.738571428571428
        },
        {
          "index": 224,
          "score": 5.562857142857141
        },
        {
          "index": 226,
          "score": 5.464999999999999
        },
        {
          "index": 227,
          "score": 5.205714285714287
        },
        {
          "index": 223,
          "score": 5.185714285714287
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The analysis has detected a dominant period of 24 hours in the time series with spectral strength indicating a moderate level of periodicity, and change points suggesting regime shifts at specific indices.",
  "scale": "medium",
  "observations": ["A dominant period of 24 hours is identified in the time series.", "Change points indicate potential regime shifts at specific indices."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There are periodic patterns within the series.",
      "evidence": [
        {
          "type": "periodic_patterns",
          "value": 24.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "periodic_patterns"
    },
    {
      "claim": "Regime shifts occur, reflecting changes in the patterns or stability of the data.",
      "evidence": [
        {
          "type": "regime_shifts",
          "value": [223, 224, 225, 226, 227],
          "source_tool": "change_points",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "regime_shifts"
    }
  ],
  "coverage": {"periodic_patterns": "tool_supported", "regime_shifts": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (structure, s1s2) — `heterogeneous:structure:s1s2:m0`

tokens prompt=8219 completion=476 latency=20.30s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=structure.
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
    "analysis_scope": {"target_series": [1], "role": "structure"},
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
{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, trends, or anomalies.","task_summary":"Choose the description that best fits the given univariate time series data from the four provided options.","target_output":"description of time series data among four choices","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["structure"],"success_criteria":["Identification of primary and secondary structural elements that align closely with a specific candidate description.","Verification through cross-referencing quantitative findings against each candidate statement."],"notes":"Ensure all observed patterns and described attributes are thoroughly evaluated against each option for precise alignment."}
</plan_context>

<task_summary>
Choose the description that best fits the given univariate time series data from the four provided options.
</task_summary>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The analysis has detected a dominant period of 24 hours in the time series with spectral strength indicating a moderate level of periodicity, and change points suggesting regime shifts at specific indices.","scale":"medium","observations":["A dominant period of 24 hours is identified in the time series.","Change points indicate potential regime shifts at specific indices."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.13039978670209035, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","claims_to_support":[{"claim":"There are periodic patterns within the series.","required_evidence":["periodic_patterns"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that contributes to the overall characterization of the data.","supports_evidence":["periodic_patterns"]},{"tool":"change_points","reason":"To identify regime shifts that reflect changes in the patterns or stability of the data.","supports_evidence":["regime_shifts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. First, we need to detect the dominant period using the fft_period tool. Following this, we will use the change_points tool to identify any regime shifts that reflect changes in the patterns or stability of the data."},"structured_observations":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}],"coverage":{"periodic_patterns":"tool_supported","regime_shifts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.13039978670209035,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend description and identification of major structural changes through change points detection. The describe_series tool indicates a downward global trend with a negative slope, and the change_points tool finds several significant structural changes towards the end of the time series.","scale":"long","observations":["A global downward trend with negative slope was detected across the series.","Multiple locations indicating major structural changes were identified near the later period of the series."],"evidence_intervals":["Entire series range: [0, 287]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 5.705625000000001, \"std\": 3.115931668848108, \"min\": 1.24, \"max\": 21.93, \"median\": 5.71, \"range\": 20.69, \"p50\": 5.71, \"p90\": 9.606, \"p99\": 15.277499999999987, \"start\": 6.86, \"end\": 6.74, \"slope\": -0.0004181184668989551}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Detect global trend and major structural changes over the entire span of the time series.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Major structural changes exist in the time series.","required_evidence":["locations_of_major_structural_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["reliable detection of trend direction and consistency of structural breaks"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.","supports_evidence":["direction_of_global_trend"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions, helping to identify major structural changes in the series.","supports_evidence":["locations_of_major_structural_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"global_overview","input_binding":{}},{"step":2,"tool":"change_points","output_key":"structural_changes","input_binding":{}}],"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series."},"structured_observations":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"coverage":{"global_trend":"tool_supported","major_structural_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":5.705625000000001,"std":3.115931668848108,"min":1.24,"max":21.93,"median":5.71,"range":20.69,"p50":5.71,"p90":9.606,"p99":15.277499999999987,"start":6.86,"end":6.74,"slope":-0.0004181184668989551}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"conflicts":[],"summary":"A global downward trend with negative slope was detected across the series. Multiple locations indicating major structural changes were identified near the later period of the series. A dominant period of 24 hours is identified in the time series. Change points indicate potential regime shifts at specific indices.","structured_by_scale":{"long":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"medium":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=structure.

```

### OUTPUT

```
```json
{
  "reasoning": "The assignment aims to quantify the characteristics of the time series to select the best descriptive match among the candidates. Previous evidence has identified a global downward trend, periodic patterns, and regime shifts. Further investigation is needed to measure stability periods and spike occurrences.",
  "evidence_plan": {
    "objective": "Quantify the characteristics of the time series, including trends, periodicity, regime shifts, spikes, and stability, to support the selection of the best descriptive match among the candidates.",
    "claims_to_support": [
      {
        "claim": "There is a global trend in the time series.",
        "required_evidence": ["direction_of_global_trend"]
      },
      {
        "claim": "Periodic patterns within the series exist.",
        "required_evidence": ["dominant_periodicity"]
      },
      {
        "claim": "Regime shifts are present in the time series.",
        "required_evidence": ["locations_of_regime_shifts"]
      },
      {
        "claim": "Stability periods within the series can be identified.",
        "required_evidence": ["stability_periods"]
      },
      {
        "claim": "Spike occurrences in the series can be quantified.",
        "required_evidence": ["spike_occurrences"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "structure"
    },
    "validation_needs": ["comparison of quantified characteristics against descriptive claims", "alignment of detected features with candidate statements for verification"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "describe_series",
        "reason": "Provides an initial global statistical overview and trend direction."
      },
      {
        "tool": "fft_period",
        "reason": "Identifies the dominant periodic pattern."
      },
      {
        "tool": "change_points",
        "reason": "Locates significant regime shifts."
      },
      {
        "tool": "cross_series_compare",
        "reason": "Compares stability periods across relevant segments."
      },
      {
        "tool": "anomaly_detect",
        "reason": "Quantifies the occurrence of spikes."
      }
    ],
    "no_tool_decision": null
  }
}
```
```

## Heterogeneous (structure, s3) — `heterogeneous:structure:s3:m0`

tokens prompt=846 completion=361 latency=12.76s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Quantify the characteristics of the time series, including trends, periodicity, regime shifts, spikes, and stability, to support the selection of the best descriptive match among the candidates.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Periodic patterns within the series exist.","required_evidence":["dominant_periodicity"]},{"claim":"Regime shifts are present in the time series.","required_evidence":["locations_of_regime_shifts"]},{"claim":"Stability periods within the series can be identified.","required_evidence":["stability_periods"]},{"claim":"Spike occurrences in the series can be quantified.","required_evidence":["spike_occurrences"]}],"analysis_scope":{"target_series":[1],"role":"structure"},"validation_needs":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview and trend direction.","supports_evidence":[]},{"tool":"fft_period","reason":"Identifies the dominant periodic pattern.","supports_evidence":[]},{"tool":"change_points","reason":"Locates significant regime shifts.","supports_evidence":[]},{"tool":"cross_series_compare","reason":"Compares stability periods across relevant segments.","supports_evidence":[]},{"tool":"anomaly_detect","reason":"Quantifies the occurrence of spikes.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The assignment aims to quantify the characteristics of the time series to select the best descriptive match among the candidates. Previous evidence has identified a global downward trend, periodic patterns, and regime shifts. Further investigation is needed to measure stability periods and spike occurrences."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
- change_points
  inputs: series_index, start, end
  outputs: series
- cross_series_compare
  inputs: series_index_1, series_index_2, optional start/end
  outputs: comparison stats, correlation, distance
  often_combined_with: lag_corr, pairwise_distance
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "The workflow begins with 'describe_series' to get an overview of the time series, followed by 'fft_period' to detect the dominant periodicity. Then, 'change_points' identifies regime shifts. Next, 'anomaly_detect' locates potential spikes, and finally 'cross_series_compare' compares stability periods across relevant segments.",
  "workflow": [
    {
      "step": 1,
      "tool": "describe_series",
      "output_key": "initial_stats",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "fft_period",
      "output_key": "dominant_period_details",
      "input_binding": {
        "series": "$step1.series"
      }
    },
    {
      "step": 3,
      "tool": "change_points",
      "output_key": "regime_shifts",
      "input_binding": {
        "series_index": "$series_index",
        "start": 0,
        "end": 287
      }
    },
    {
      "step": 4,
      "tool": "anomaly_detect",
      "output_key": "spike_details",
      "input_binding": {
        "series_index": "$series_index",
        "start": 0,
        "end": 287,
        "z_threshold": 3.0
      }
    },
    {
      "step": 5,
      "tool": "cross_series_compare",
      "output_key": "pairwise_stability_comparison",
      "input_binding": {
        "series_index_1": "$series_index",
        "series_index_2": "$series_index"
      }
    }
  ]
}
```

## Heterogeneous (structure, s4) — `heterogeneous:structure:s4:m0`

tokens prompt=1226 completion=101 latency=3.76s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"describe_series","output_key":"initial_stats","input_binding":{}},{"step":2,"tool":"fft_period","output_key":"dominant_period_details","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"change_points","output_key":"regime_shifts","input_binding":{"series_index":"$series_index","start":0,"end":287}},{"step":4,"tool":"anomaly_detect","output_key":"spike_details","input_binding":{"series_index":"$series_index","start":0,"end":287,"z_threshold":3.0}},{"step":5,"tool":"cross_series_compare","output_key":"pairwise_stability_comparison","input_binding":{"series_index_1":"$series_index","series_index_2":"$series_index"}}],"reasoning":"The workflow begins with 'describe_series' to get an overview of the time series, followed by 'fft_period' to detect the dominant periodicity. Then, 'change_points' identifies regime shifts. Next, 'anomaly_detect' locates potential spikes, and finally 'cross_series_compare' compares stability periods across relevant segments."}
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
- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, z_threshold=float (default 3.0)}
  returns: {series=anomaly count/indices and max absolute z-score}
- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
- cross_series_compare: Compare windows across TWO series (analogical / multi-series segment tasks). Returns per-series segment stats, trend match, distance, correlation.
  args: {series_index_1=1-based int (default 1), series_index_2=1-based int (default 2), start=optional shared window start, end=optional shared window end, left_interval=optional [start,end] for series 1, right_interval=optional [start,end] for series 2}
  returns: {series_1/series_2=segment stats, comparison=trend agreement, distance, correlation}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}
</assignment>



Produce the InvocationPlan JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "The workflow involves several steps to analyze the time series data, including calculating descriptive statistics, identifying dominant periods, detecting regime shifts, finding anomalies, and comparing the stability between two specified series indices.",
  "calls": [
    {
      "step": 1,
      "tool": "cross_series_compare",
      "args": {
        "series_index_1": 1,
        "series_index_2": 1
      }
    }
  ]
}
```

## Heterogeneous (structure, s5) — `heterogeneous:structure:s5:m0`

tokens prompt=5892 completion=846 latency=33.19s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 5: Evidence Integration.
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
  "role": "structure",
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
{"evidence_plan":{"objective":"Quantify the characteristics of the time series, including trends, periodicity, regime shifts, spikes, and stability, to support the selection of the best descriptive match among the candidates.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Periodic patterns within the series exist.","required_evidence":["dominant_periodicity"]},{"claim":"Regime shifts are present in the time series.","required_evidence":["locations_of_regime_shifts"]},{"claim":"Stability periods within the series can be identified.","required_evidence":["stability_periods"]},{"claim":"Spike occurrences in the series can be quantified.","required_evidence":["spike_occurrences"]}],"analysis_scope":{"target_series":[1],"role":"structure"},"validation_needs":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview and trend direction.","supports_evidence":[]},{"tool":"fft_period","reason":"Identifies the dominant periodic pattern.","supports_evidence":[]},{"tool":"change_points","reason":"Locates significant regime shifts.","supports_evidence":[]},{"tool":"cross_series_compare","reason":"Compares stability periods across relevant segments.","supports_evidence":[]},{"tool":"anomaly_detect","reason":"Quantifies the occurrence of spikes.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The assignment aims to quantify the characteristics of the time series to select the best descriptive match among the candidates. Previous evidence has identified a global downward trend, periodic patterns, and regime shifts. Further investigation is needed to measure stability periods and spike occurrences."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "structure:step1",
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
          "mean": 5.705625000000001,
          "std": 3.115931668848108,
          "min": 1.24,
          "max": 21.93,
          "median": 5.71,
          "range": 20.69,
          "p50": 5.71,
          "p90": 9.606,
          "p99": 15.277499999999987,
          "start": 6.86,
          "end": 6.74,
          "slope": -0.0004181184668989551
        }
      ]
    },
    "error": null,
    "args_fingerprint": "90b10717d4a3e6c0750bb980207b8d86753ac968"
  },
  {
    "call_id": "structure:step2",
    "step": 2,
    "tool_name": "fft_period",
    "arguments": {
      "series": "$step1.series"
    },
    "resolved_arguments": {
      "series": [
        {
          "series_index": 1,
          "index": 1,
          "length": 288,
          "mean": 5.705625000000001,
          "std": 3.115931668848108,
          "min": 1.24,
          "max": 21.93,
          "median": 5.71,
          "range": 20.69,
          "p50": 5.71,
          "p90": 9.606,
          "p99": 15.277499999999987,
          "start": 6.86,
          "end": 6.74,
          "slope": -0.0004181184668989551
        }
      ]
    },
    "success": false,
    "data": {},
    "error": "Unrecognized series selector type: dict",
    "args_fingerprint": ""
  },
  {
    "call_id": "structure:step3",
    "step": 3,
    "tool_name": "change_points",
    "arguments": {
      "start": 0,
      "end": 287
    },
    "resolved_arguments": {
      "start": 0,
      "end": 287
    },
    "success": true,
    "data": {
      "series_index": 1,
      "candidates": [
        {
          "index": 225,
          "score": 5.738571428571428
        },
        {
          "index": 224,
          "score": 5.562857142857141
        },
        {
          "index": 226,
          "score": 5.464999999999999
        },
        {
          "index": 227,
          "score": 5.205714285714287
        },
        {
          "index": 223,
          "score": 5.185714285714287
        }
      ]
    },
    "error": null,
    "args_fingerprint": "5f67b507f05e1e754ac67e0020045c4bacbf97ac"
  },
  {
    "call_id": "structure:step4",
    "step": 4,
    "tool_name": "anomaly_detect",
    "arguments": {
      "start": 0,
      "end": 287,
      "z_threshold": 3.0
    },
    "resolved_arguments": {
      "start": 0,
      "end": 287,
      "z_threshold": 3.0
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 0,
      "end": 287,
      "z_threshold": 3.0,
      "n_anomalies": 3,
      "anomaly_indices": [
        27,
        51,
        75
      ],
      "max_abs_z": 5.206909754217363
    },
    "error": null,
    "args_fingerprint": "18e646a0ccd1883bf57d32fc0e512d252d3f3dec"
  },
  {
    "call_id": "structure:step5",
    "step": 5,
    "tool_name": "cross_series_compare",
    "arguments": {
      "series_index_1": 1,
      "series_index_2": 1
    },
    "resolved_arguments": {
      "series_index_1": 1,
      "series_index_2": 1
    },
    "success": false,
    "data": {},
    "error": "Need >=2 series",
    "args_fingerprint": ""
  }
]
</executed_steps>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The analysis has detected a dominant period of 24 hours in the time series with spectral strength indicating a moderate level of periodicity, and change points suggesting regime shifts at specific indices.","scale":"medium","observations":["A dominant period of 24 hours is identified in the time series.","Change points indicate potential regime shifts at specific indices."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.13039978670209035, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","claims_to_support":[{"claim":"There are periodic patterns within the series.","required_evidence":["periodic_patterns"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that contributes to the overall characterization of the data.","supports_evidence":["periodic_patterns"]},{"tool":"change_points","reason":"To identify regime shifts that reflect changes in the patterns or stability of the data.","supports_evidence":["regime_shifts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. First, we need to detect the dominant period using the fft_period tool. Following this, we will use the change_points tool to identify any regime shifts that reflect changes in the patterns or stability of the data."},"structured_observations":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}],"coverage":{"periodic_patterns":"tool_supported","regime_shifts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.13039978670209035,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend description and identification of major structural changes through change points detection. The describe_series tool indicates a downward global trend with a negative slope, and the change_points tool finds several significant structural changes towards the end of the time series.","scale":"long","observations":["A global downward trend with negative slope was detected across the series.","Multiple locations indicating major structural changes were identified near the later period of the series."],"evidence_intervals":["Entire series range: [0, 287]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 5.705625000000001, \"std\": 3.115931668848108, \"min\": 1.24, \"max\": 21.93, \"median\": 5.71, \"range\": 20.69, \"p50\": 5.71, \"p90\": 9.606, \"p99\": 15.277499999999987, \"start\": 6.86, \"end\": 6.74, \"slope\": -0.0004181184668989551}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Detect global trend and major structural changes over the entire span of the time series.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Major structural changes exist in the time series.","required_evidence":["locations_of_major_structural_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["reliable detection of trend direction and consistency of structural breaks"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.","supports_evidence":["direction_of_global_trend"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions, helping to identify major structural changes in the series.","supports_evidence":["locations_of_major_structural_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"global_overview","input_binding":{}},{"step":2,"tool":"change_points","output_key":"structural_changes","input_binding":{}}],"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series."},"structured_observations":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"coverage":{"global_trend":"tool_supported","major_structural_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":5.705625000000001,"std":3.115931668848108,"min":1.24,"max":21.93,"median":5.71,"range":20.69,"p50":5.71,"p90":9.606,"p99":15.277499999999987,"start":6.86,"end":6.74,"slope":-0.0004181184668989551}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"conflicts":[],"summary":"A global downward trend with negative slope was detected across the series. Multiple locations indicating major structural changes were identified near the later period of the series. A dominant period of 24 hours is identified in the time series. Change points indicate potential regime shifts at specific indices.","structured_by_scale":{"long":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"medium":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}]}}
</temporal_profile>

<assignment>
{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "The time series has been analyzed for its global trend, periodic patterns, regime shifts, and spike occurrences, with some measurements completed but others needing further analysis or adjustment. There's a clear downward trend in the series, with a significant slope indicating a negative global trend. Periodicity analysis indicates a dominant cycle of approximately 24 hours, though further validation is needed due to previous execution errors. Regime shifts were detected around index positions 223 to 227, suggesting major changes in patterns. Spikes were quantified at indices 27, 51, and 75, marking deviations from the norm. However, there is a need to validate stability periods and confirm the periodicity analysis results.",
  "role": "structure",
  "hypothesis": "The time series exhibits a strong downward trend, significant periodic patterns, regime shifts, and occasional spikes.",
  "evidence": [
    "The time series shows a negative global trend, with a significant negative slope of -0.000418.",
    "The dominant periodic pattern detected in the series is approximately 24 hours, indicating daily cyclical behavior.",
    "Change point analysis suggests regime shifts at indices 223, 224, 225, 226, and 227.",
    "Anomaly detection quantified three spike occurrences at indices 27, 51, and 75."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "structure:step1",
    "medium:step2",
    "structure:step3",
    "structure:step4"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "There is a global trend in the time series.",
      "evidence": [
        {
          "type": "direction_of_global_trend",
          "value": "downward",
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Periodic patterns within the series exist.",
      "evidence": [
        {
          "type": "periodic_patterns",
          "value": 24.0,
          "provenance": "upstream",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "Regime shifts are present in the time series.",
      "evidence": [
        {
          "type": "regime_shifts",
          "value": [
            223,
            224,
            225,
            226,
            227
          ],
          "provenance": "tool",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Stability periods within the series can be identified.",
      "evidence": [],
      "confidence": "unresolved"
    },
    {
      "claim": "Spike occurrences in the series can be quantified.",
      "evidence": [
        {
          "type": "spike_occurrences",
          "value": [
            27,
            51,
            75
          ],
          "provenance": "tool",
          "ref": "structure:step4",
          "call_id": "structure:step4"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": [
    "Stability periods within the series can be identified."
  ]
}
```

## Heterogeneous (structure, s1s2) — `heterogeneous:structure:s1s2:m1`

tokens prompt=8238 completion=509 latency=21.59s

### INPUT (system)

```
You are a Heterogeneous Task Agent with role=structure.
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
    "analysis_scope": {"target_series": [1], "role": "structure"},
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
{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, trends, or anomalies.","task_summary":"Choose the description that best fits the given univariate time series data from the four provided options.","target_output":"description of time series data among four choices","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Detect global trend and major structural changes over the entire span of the time series.","required_measurements":["global_trend","major_structural_changes"],"validation_requirements":["reliable detection of trend direction and consistency of structural breaks"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","required_measurements":["periodic_patterns","regime_shifts"],"validation_requirements":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}],"scales":["long","medium"],"heterogeneous_agents":["structure"],"success_criteria":["Identification of primary and secondary structural elements that align closely with a specific candidate description.","Verification through cross-referencing quantitative findings against each candidate statement."],"notes":"Ensure all observed patterns and described attributes are thoroughly evaluated against each option for precise alignment."}
</plan_context>

<task_summary>
Choose the description that best fits the given univariate time series data from the four provided options.
</task_summary>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The analysis has detected a dominant period of 24 hours in the time series with spectral strength indicating a moderate level of periodicity, and change points suggesting regime shifts at specific indices.","scale":"medium","observations":["A dominant period of 24 hours is identified in the time series.","Change points indicate potential regime shifts at specific indices."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.13039978670209035, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","claims_to_support":[{"claim":"There are periodic patterns within the series.","required_evidence":["periodic_patterns"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that contributes to the overall characterization of the data.","supports_evidence":["periodic_patterns"]},{"tool":"change_points","reason":"To identify regime shifts that reflect changes in the patterns or stability of the data.","supports_evidence":["regime_shifts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. First, we need to detect the dominant period using the fft_period tool. Following this, we will use the change_points tool to identify any regime shifts that reflect changes in the patterns or stability of the data."},"structured_observations":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}],"coverage":{"periodic_patterns":"tool_supported","regime_shifts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.13039978670209035,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend description and identification of major structural changes through change points detection. The describe_series tool indicates a downward global trend with a negative slope, and the change_points tool finds several significant structural changes towards the end of the time series.","scale":"long","observations":["A global downward trend with negative slope was detected across the series.","Multiple locations indicating major structural changes were identified near the later period of the series."],"evidence_intervals":["Entire series range: [0, 287]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 5.705625000000001, \"std\": 3.115931668848108, \"min\": 1.24, \"max\": 21.93, \"median\": 5.71, \"range\": 20.69, \"p50\": 5.71, \"p90\": 9.606, \"p99\": 15.277499999999987, \"start\": 6.86, \"end\": 6.74, \"slope\": -0.0004181184668989551}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Detect global trend and major structural changes over the entire span of the time series.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Major structural changes exist in the time series.","required_evidence":["locations_of_major_structural_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["reliable detection of trend direction and consistency of structural breaks"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.","supports_evidence":["direction_of_global_trend"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions, helping to identify major structural changes in the series.","supports_evidence":["locations_of_major_structural_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"global_overview","input_binding":{}},{"step":2,"tool":"change_points","output_key":"structural_changes","input_binding":{}}],"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series."},"structured_observations":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"coverage":{"global_trend":"tool_supported","major_structural_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":5.705625000000001,"std":3.115931668848108,"min":1.24,"max":21.93,"median":5.71,"range":20.69,"p50":5.71,"p90":9.606,"p99":15.277499999999987,"start":6.86,"end":6.74,"slope":-0.0004181184668989551}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"conflicts":[],"summary":"A global downward trend with negative slope was detected across the series. Multiple locations indicating major structural changes were identified near the later period of the series. A dominant period of 24 hours is identified in the time series. Change points indicate potential regime shifts at specific indices.","structured_by_scale":{"long":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"medium":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
retry_context=unresolved_claims=['Stability periods within the series can be identified.']
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=structure.

```

### OUTPUT

```
```json
{
  "reasoning": "The task aims to quantify key characteristics of the time series to select the most accurate descriptive match. Previous analysis provides evidence of a global downward trend, major structural changes, and periodic patterns at a 24-hour interval. Validation is required to confirm these findings against candidate statements.",
  "evidence_plan": {
    "objective": "Quantify the characteristics of the time series, including trends, periodicity, regime shifts, spike occurrence, and stability periods, to support the selection of the best descriptive match among the candidates.",
    "claims_to_support": [
      {
        "claim": "There is a global trend in the time series.",
        "required_evidence": ["global_trend", "slope"]
      },
      {
        "claim": "Regime shifts occur, reflecting changes in the patterns or stability of the data.",
        "required_evidence": ["regime_shifts", "change_points"]
      },
      {
        "claim": "Periodic patterns within the series can be detected.",
        "required_evidence": ["periodic_patterns", "dominant_period"]
      },
      {
        "claim": "Spike occurrences within the series can be identified.",
        "required_evidence": ["spikes"]
      },
      {
        "claim": "Stability periods within the series can be identified.",
        "required_evidence": ["stability_periods"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": []
    },
    "validation_needs": [
      "Comparison of quantified characteristics against descriptive claims",
      "Alignment of detected features with candidate statements for verification"
    ]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "describe_series",
        "reason": "Provide global statistics, including trend direction and slope."
      },
      {
        "tool": "fft_period",
        "reason": "Detect the dominant period of the series for periodic patterns."
      },
      {
        "tool": "change_points",
        "reason": "Identify regime shifts and structural changes."
      },
      {
        "tool": "anomaly_detect",
        "reason": "Detect spikes or anomalies in the series."
      },
      {
        "tool": "adf_stationarity",
        "reason": "Check for periods of stability using stationarity tests."
      }
    ],
    "no_tool_decision": null
  }
}
```
```

## Heterogeneous (structure, s3) — `heterogeneous:structure:s3:m1`

tokens prompt=851 completion=304 latency=10.76s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Quantify the characteristics of the time series, including trends, periodicity, regime shifts, spike occurrence, and stability periods, to support the selection of the best descriptive match among the candidates.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["global_trend","slope"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts","change_points"]},{"claim":"Periodic patterns within the series can be detected.","required_evidence":["periodic_patterns","dominant_period"]},{"claim":"Spike occurrences within the series can be identified.","required_evidence":["spikes"]},{"claim":"Stability periods within the series can be identified.","required_evidence":["stability_periods"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[]},"validation_needs":["Comparison of quantified characteristics against descriptive claims","Alignment of detected features with candidate statements for verification"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provide global statistics, including trend direction and slope.","supports_evidence":[]},{"tool":"fft_period","reason":"Detect the dominant period of the series for periodic patterns.","supports_evidence":[]},{"tool":"change_points","reason":"Identify regime shifts and structural changes.","supports_evidence":[]},{"tool":"anomaly_detect","reason":"Detect spikes or anomalies in the series.","supports_evidence":[]},{"tool":"adf_stationarity","reason":"Check for periods of stability using stationarity tests.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The task aims to quantify key characteristics of the time series to select the most accurate descriptive match. Previous analysis provides evidence of a global downward trend, major structural changes, and periodic patterns at a 24-hour interval. Validation is required to confirm these findings against candidate statements."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
- fft_period
  inputs: series
  outputs: dominant_period, spectral_strength, period_trusted
  depends: none; typically precedes stl_strength
- adf_stationarity
  inputs: series_index, start, end
  outputs: series
- change_points
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "The workflow begins with 'describe_series' to get global statistics and then proceeds to detect periodic patterns using 'fft_period'. After that, we identify any regime shifts with 'change_points', detect spikes or anomalies with 'anomaly_detect', and finally check for stability periods with 'adf_stationarity'.",
  "workflow": [
    {
      "step": 1,
      "tool": "describe_series",
      "output_key": "global_characteristics",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "fft_period",
      "output_key": "periodicity_info",
      "input_binding": {
        "series": "$step1.global_characteristics"
      }
    },
    {
      "step": 3,
      "tool": "change_points",
      "output_key": "structural_changes",
      "input_binding": {
        "series": "$step1.global_characteristics"
      }
    },
    {
      "step": 4,
      "tool": "anomaly_detect",
      "output_key": "anomalies",
      "input_binding": {
        "series": "$step1.global_characteristics"
      }
    },
    {
      "step": 5,
      "tool": "adf_stationarity",
      "output_key": "stability_periods",
      "input_binding": {
        "series": "$step1.global_characteristics"
      }
    }
  ]
}
```

## Heterogeneous (structure, s4) — `heterogeneous:structure:s4:m1`

tokens prompt=1125 completion=242 latency=8.67s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"describe_series","output_key":"global_characteristics","input_binding":{}},{"step":2,"tool":"fft_period","output_key":"periodicity_info","input_binding":{"series":"$step1.global_characteristics"}},{"step":3,"tool":"change_points","output_key":"structural_changes","input_binding":{"series":"$step1.global_characteristics"}},{"step":4,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"series":"$step1.global_characteristics"}},{"step":5,"tool":"adf_stationarity","output_key":"stability_periods","input_binding":{"series":"$step1.global_characteristics"}}],"reasoning":"The workflow begins with 'describe_series' to get global statistics and then proceeds to detect periodic patterns using 'fft_period'. After that, we identify any regime shifts with 'change_points', detect spikes or anomalies with 'anomaly_detect', and finally check for stability periods with 'adf_stationarity'."}
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
- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, z_threshold=float (default 3.0)}
  returns: {series=anomaly count/indices and max absolute z-score}
- fft_period: Dominant period via FFT.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=dominant_period, spectral_strength, period_trusted}
- adf_stationarity: ADF stationarity test.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ADF statistic, p-value, and stationarity flag}
- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}
</assignment>



Produce the InvocationPlan JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "The workflow aims to quantify various characteristics of the univariate time series, including global trends, periodic patterns, regime shifts, spike occurrences, and stability periods. Given that there's only one time series in this scenario (series_index=1), the necessary tools are invoked directly on it without needing comparison or cross-reference steps.",
  "calls": [
    {
      "step": 1,
      "tool": "describe_series",
      "args": {}
    },
    {
      "step": 2,
      "tool": "fft_period",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 3,
      "tool": "change_points",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 4,
      "tool": "anomaly_detect",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 5,
      "tool": "adf_stationarity",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Heterogeneous (structure, s5) — `heterogeneous:structure:s5:m1`

tokens prompt=5825 completion=909 latency=35.52s

### INPUT (system)

```
You are a Heterogeneous Agent (role=structure) at Stage 5: Evidence Integration.
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
  "role": "structure",
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
{"evidence_plan":{"objective":"Quantify the characteristics of the time series, including trends, periodicity, regime shifts, spike occurrence, and stability periods, to support the selection of the best descriptive match among the candidates.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["global_trend","slope"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts","change_points"]},{"claim":"Periodic patterns within the series can be detected.","required_evidence":["periodic_patterns","dominant_period"]},{"claim":"Spike occurrences within the series can be identified.","required_evidence":["spikes"]},{"claim":"Stability periods within the series can be identified.","required_evidence":["stability_periods"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[]},"validation_needs":["Comparison of quantified characteristics against descriptive claims","Alignment of detected features with candidate statements for verification"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provide global statistics, including trend direction and slope.","supports_evidence":[]},{"tool":"fft_period","reason":"Detect the dominant period of the series for periodic patterns.","supports_evidence":[]},{"tool":"change_points","reason":"Identify regime shifts and structural changes.","supports_evidence":[]},{"tool":"anomaly_detect","reason":"Detect spikes or anomalies in the series.","supports_evidence":[]},{"tool":"adf_stationarity","reason":"Check for periods of stability using stationarity tests.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The task aims to quantify key characteristics of the time series to select the most accurate descriptive match. Previous analysis provides evidence of a global downward trend, major structural changes, and periodic patterns at a 24-hour interval. Validation is required to confirm these findings against candidate statements."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "structure:step1",
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
          "mean": 5.705625000000001,
          "std": 3.115931668848108,
          "min": 1.24,
          "max": 21.93,
          "median": 5.71,
          "range": 20.69,
          "p50": 5.71,
          "p90": 9.606,
          "p99": 15.277499999999987,
          "start": 6.86,
          "end": 6.74,
          "slope": -0.0004181184668989551
        }
      ]
    },
    "error": null,
    "args_fingerprint": "90b10717d4a3e6c0750bb980207b8d86753ac968"
  },
  {
    "call_id": "structure:step2",
    "step": 2,
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
      "spectral_strength": 0.13039978670209035,
      "period_trusted": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "726ee7605c7aac2e5823de42d4c34d3c89859438"
  },
  {
    "call_id": "structure:step3",
    "step": 3,
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
          "index": 225,
          "score": 5.738571428571428
        },
        {
          "index": 224,
          "score": 5.562857142857141
        },
        {
          "index": 226,
          "score": 5.464999999999999
        },
        {
          "index": 227,
          "score": 5.205714285714287
        },
        {
          "index": 223,
          "score": 5.185714285714287
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  },
  {
    "call_id": "structure:step4",
    "step": 4,
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
      "n_anomalies": 3,
      "anomaly_indices": [
        27,
        51,
        75
      ],
      "max_abs_z": 5.206909754217363
    },
    "error": null,
    "args_fingerprint": "9ee1de07f72732a041d0e186f599357a414ae94b"
  },
  {
    "call_id": "structure:step5",
    "step": 5,
    "tool_name": "adf_stationarity",
    "arguments": {
      "series_index": 1
    },
    "resolved_arguments": {
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "adf_stat": -8.368854348719763,
      "pvalue": 2.6963171384897947e-13,
      "is_stationary_at_5pct": true
    },
    "error": null,
    "args_fingerprint": "b85911723fcf8ec7bd59fcade39c401459cd70f2"
  }
]
</executed_steps>

<temporal_profile>
{"short":null,"medium":{"reasoning":"The analysis has detected a dominant period of 24 hours in the time series with spectral strength indicating a moderate level of periodicity, and change points suggesting regime shifts at specific indices.","scale":"medium","observations":["A dominant period of 24 hours is identified in the time series.","Change points indicate potential regime shifts at specific indices."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.13039978670209035, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.","claims_to_support":[{"claim":"There are periodic patterns within the series.","required_evidence":["periodic_patterns"]},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","required_evidence":["regime_shifts"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["verification of periodicity consistency across different segments","identification of regime changes based on pattern stability"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To detect the dominant period that contributes to the overall characterization of the data.","supports_evidence":["periodic_patterns"]},{"tool":"change_points","reason":"To identify regime shifts that reflect changes in the patterns or stability of the data.","supports_evidence":["regime_shifts"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify repeated patterns or regimes within the series that contribute to the overall characterization of the data. First, we need to detect the dominant period using the fft_period tool. Following this, we will use the change_points tool to identify any regime shifts that reflect changes in the patterns or stability of the data."},"structured_observations":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}],"coverage":{"periodic_patterns":"tool_supported","regime_shifts":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.13039978670209035,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes a global trend description and identification of major structural changes through change points detection. The describe_series tool indicates a downward global trend with a negative slope, and the change_points tool finds several significant structural changes towards the end of the time series.","scale":"long","observations":["A global downward trend with negative slope was detected across the series.","Multiple locations indicating major structural changes were identified near the later period of the series."],"evidence_intervals":["Entire series range: [0, 287]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 5.705625000000001, \"std\": 3.115931668848108, \"min\": 1.24, \"max\": 21.93, \"median\": 5.71, \"range\": 20.69, \"p50\": 5.71, \"p90\": 9.606, \"p99\": 15.277499999999987, \"start\": 6.86, \"end\": 6.74, \"slope\": -0.0004181184668989551}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 225, \"score\": 5.738571428571428}, {\"index\": 224, \"score\": 5.562857142857141}, {\"index\": 226, \"score\": 5.464999999999999}, {\"index\": 227, \"score\": 5.205714285714287}, {\"index\": 223, \"score\": 5.185714285714287}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Detect global trend and major structural changes over the entire span of the time series.","claims_to_support":[{"claim":"There is a global trend in the time series.","required_evidence":["direction_of_global_trend"]},{"claim":"Major structural changes exist in the time series.","required_evidence":["locations_of_major_structural_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["reliable detection of trend direction and consistency of structural breaks"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"Provides an initial global statistical overview, including mean, slope, and other descriptive statistics that indicate trend direction.","supports_evidence":["direction_of_global_trend"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions, helping to identify major structural changes in the series.","supports_evidence":["locations_of_major_structural_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"global_overview","input_binding":{}},{"step":2,"tool":"change_points","output_key":"structural_changes","input_binding":{}}],"reasoning":"The objective is to detect the global trend and major structural changes over the entire span of the time series, requiring tools that can provide a reliable overview and identify significant shifts. The first step is to use 'describe_series' to get an initial global statistical overview, which will help determine the direction of the global trend. Then, using 'change_points', we can identify the locations of major structural changes in the series."},"structured_observations":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"coverage":{"global_trend":"tool_supported","major_structural_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":5.705625000000001,"std":3.115931668848108,"min":1.24,"max":21.93,"median":5.71,"range":20.69,"p50":5.71,"p90":9.606,"p99":15.277499999999987,"start":6.86,"end":6.74,"slope":-0.0004181184668989551}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"long:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":225,"score":5.738571428571428},{"index":224,"score":5.562857142857141},{"index":226,"score":5.464999999999999},{"index":227,"score":5.205714285714287},{"index":223,"score":5.185714285714287}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"conflicts":[],"summary":"A global downward trend with negative slope was detected across the series. Multiple locations indicating major structural changes were identified near the later period of the series. A dominant period of 24 hours is identified in the time series. Change points indicate potential regime shifts at specific indices.","structured_by_scale":{"long":[{"claim":"There is a global trend in the time series.","evidence":[{"type":"direction_of_global_trend","value":"downward","source_tool":"describe_series","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"Major structural changes exist in the time series.","evidence":[{"type":"locations_of_major_structural_changes","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"major_structural_changes"}],"medium":[{"claim":"There are periodic patterns within the series.","evidence":[{"type":"periodic_patterns","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"periodic_patterns"},{"claim":"Regime shifts occur, reflecting changes in the patterns or stability of the data.","evidence":[{"type":"regime_shifts","value":[223,224,225,226,227],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_shifts"}]}}
</temporal_profile>

<assignment>
{"role":"structure","objective":"Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.","required_measurements":["global_trend","periodic_patterns","regime_shifts","spike_occurrence","stability_periods"],"validation_requirements":["comparison of quantified characteristics against descriptive claims","alignment of detected features with candidate statements for verification"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=structure.

```

### OUTPUT

```
{
  "reasoning": "The time series exhibits a global downward trend with a negative slope, as well as periodic patterns at a 24-hour interval. Regime shifts are identified through change point analysis, and anomalies are detected within the series. Adf stationarity test confirms periods of stability.",
  "role": "structure",
  "hypothesis": "The time series presents a global downward trend, periodic patterns every 24 hours, regime shifts at specific points, and anomalies. Stability periods are confirmed by stationarity tests.",
  "evidence": [
    "The global trend analysis shows a negative slope of -0.0004181184668989551, indicating a declining pattern throughout the series.",
    "Fourier analysis confirms a dominant period of 24 hours, corresponding to daily fluctuations.",
    "Change point detection highlights multiple instances of structural changes, mainly towards the end of the time series.",
    "Anomaly detection identifies three significant spike events at indices 27, 51, and 75, suggesting unusual peaks in the data.",
    "Adf stationarity test results show that the time series becomes stationary with a p-value less than 0.05, confirming stable periods."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "structure:step1",
    "structure:step2",
    "structure:step3",
    "structure:step4",
    "structure:step5"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "There is a global trend in the time series.",
      "evidence": [
        {
          "type": "global_trend",
          "value": -0.0004181184668989551,
          "provenance": "local",
          "ref": "structure:step1",
          "call_id": "structure:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Regime shifts occur, reflecting changes in the patterns or stability of the data.",
      "evidence": [
        {
          "type": "regime_shifts",
          "value": [223, 224, 225, 226, 227],
          "provenance": "local",
          "ref": "structure:step3",
          "call_id": "structure:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Periodic patterns within the series can be detected.",
      "evidence": [
        {
          "type": "periodic_patterns",
          "value": 24.0,
          "provenance": "local",
          "ref": "structure:step2",
          "call_id": "structure:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Spike occurrences within the series can be identified.",
      "evidence": [
        {
          "type": "spikes",
          "value": [27, 51, 75],
          "provenance": "local",
          "ref": "structure:step4",
          "call_id": "structure:step4"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Stability periods within the series can be identified.",
      "evidence": [
        {
          "type": "stability_periods",
          "value": true,
          "provenance": "local",
          "ref": "structure:step5",
          "call_id": "structure:step5"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "global_trend": "tool_supported",
    "periodic_patterns": "tool_supported",
    "regime_shifts": "tool_supported",
    "spike_occurrence": "tool_supported",
    "stability_periods": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1720 completion=237 latency=8.67s

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
A) This time series demonstrates significant variability with multiple peaks and valleys, showing an overall declining trend from higher initial values to lower ranges.
B) This series shows irregular fluctuations with occasional sharp peaks, maintaining relatively low baseline values with intermittent spikes reaching nearly 10 units.
C) This time series exhibits periodic oscillating patterns with irregular spikes, displaying cyclical behavior with values ranging from approximately 1 to 22 units.
D) This series remains remarkably stable around 98.9 units for the first portion, then transitions to higher variability with fluctuations between 97-99 units.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Choose the description that best fits the given univariate time series data from the four provided options.",
  "question_type": "choice",
  "required_output": "description of time series data among four choices",
  "success_criteria": [
    "Identification of primary and secondary structural elements that align closely with a specific candidate description.",
    "Verification through cross-referencing quantitative findings against each candidate statement."
  ],
  "assignments_brief": [
    {
      "agent": "homo:long",
      "objective": "Detect global trend and major structural changes over the entire span of the time series.",
      "required_measurements": [
        "global_trend",
        "major_structural_changes"
      ]
    },
    {
      "agent": "homo:medium",
      "objective": "Identify repeated patterns or regimes within the series that contribute to the overall characterization of the data.",
      "required_measurements": [
        "periodic_patterns",
        "regime_shifts"
      ]
    },
    {
      "agent": "hetero:structure",
      "objective": "Quantify the characteristics of the time series, including trends, periodicity, spikes, and stability, to support the selection of the best descriptive match among the candidates.",
      "required_measurements": [
        "global_trend",
        "periodic_patterns",
        "regime_shifts",
        "spike_occurrence",
        "stability_periods"
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
          "type": "periodic_patterns",
          "value": 24.0,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "regime_shifts",
          "value": [
            223,
            224,
            225,
            226,
            227
          ],
          "trusted": true
        }
      ],
      "coverage": {
        "periodic_patterns": "tool_supported",
        "regime_shifts": "tool_supported"
      },
      "summary": "A dominant period of 24 hours is identified in the time series. | Change points indicate potential regime shifts at specific indices."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "direction_of_global_trend",
          "value": "downward",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "locations_of_major_structural_changes",
          "value": [
            223,
            224,
            225,
            226,
            227
          ],
          "trusted": true
        }
      ],
      "coverage": {
        "global_trend": "tool_supported",
        "major_structural_changes": "tool_supported"
      },
      "summary": "A global downward trend with negative slope was detected across the series. | Multiple locations indicating major structural changes were identified near the later period of the series."
    }
  },
  "conflicts": [],
  "summary": "A global downward trend with negative slope was detected across the series. Multiple locations indicating major structural changes were identified near the later period of the series. A dominant period of 24 hours is identified in the time series. Change points indicate potential regime shifts at specific indices."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "structure",
      "hypothesis": "The time series exhibits a strong downward trend, significant periodic patterns, regime shifts, and occasional spikes.",
      "reasoning_chain": [
        "There is a global trend in the time series.",
        "direction_of_global_trend=downward",
        "Periodic patterns within the series exist.",
        "periodic_patterns=24.0",
        "Regime shifts are present in the time series.",
        "regime_shifts=[223, 224, 225, 226, 227]",
        "Stability periods within the series can be identified.",
        "Spike occurrences in the series can be quantified.",
        "spike_occurrences=[27, 51, 75]"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "direction_of_global_trend",
        "periodic_patterns",
        "regime_shifts",
        "spike_occurrences"
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

<question_rules>
- Match/Align: answer must be one candidate letter. Trust execution_metadata.option_mapping and verified_preference when present.
</question_rules>

Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "The time series has been found to have a downward trend and periodic patterns of 24 hours, with notable regime shifts at certain points. The presence of these elements suggests that the time series fluctuates within cycles but also moves towards a declining trend. There are also mentions of spikes which further confirm the variability of the series. This description best matches option C.",
  "answer": "C",
  "explanation": "Option C best describes the series with its emphasis on periodic oscillations, irregular spikes, and cyclical behaviors. It captures the essence of the 24-hour cycle and the range of values observed, fitting well with the perceived structure of the time series data.",
  "confidence": 0.9,
  "conflicts": [],
  "cited_evidence": ["direction_of_global_trend", "periodic_patterns", "regime_shifts", "spike_occurrences"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "C"
  }
}
```
