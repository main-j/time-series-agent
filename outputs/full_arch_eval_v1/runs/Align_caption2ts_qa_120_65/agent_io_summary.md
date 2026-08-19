# Agent IO summary: `Align:caption2ts_qa_120:65`

- Architecture pred: `A` (success=True)
- model_calls=12, tool_calls=3, latency=128.7s

## Planner — `planner`

tokens prompt=1152 completion=517 latency=18.36s

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
'This time series data exhibits relatively stable values around 4.3-5.5 for most observations, with two prominent anomalous spikes: one reaching 7.73 at index 107 and an extreme outlier of 26.45 at index 142, followed by a gradual decline back to baseline levels.' According to the above textual description of a time series, select the time series from the following four options that most accurately reflects the described characteristics.
</question>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires identifying which time series among the provided options best matches the given textual description of having stable baseline values within a specific range, with notable anomalies at specified indices.",
  "task_summary": "Select the time series that best matches a textual description involving stable values, spikes, and an extreme outlier.",
  "target_output": "Identify the time series that best fits the described characteristics from the options provided.",
  "answer_type": "choice",
  "capability": "choice",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "medium",
      "objective": "Detect stable periods and anomalies in the time series.",
      "required_measurements": ["baseline_value_range", "anomaly_location", "anomaly_magnitude"],
      "validation_requirements": ["Check if stable ranges and anomaly details are consistent with text description."],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 287]]
    },
    {
      "scale": "short",
      "objective": "Locate the anomalous spikes and confirm their magnitudes.",
      "required_measurements": ["anomaly_magnitude", "change_location"],
      "validation_requirements": ["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[107, 142]]
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.",
      "required_measurements": ["baseline_value_range", "anomaly_location", "anomaly_magnitude", "pairwise_similarity"],
      "validation_requirements": ["Cross-validate against the textual description and ensure consistency with chosen time series characteristics."],
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 287]]
    }
  ],
  "success_criteria": ["Time series selected must exhibit features identical to those described in the textual summary."],
  "notes": "Ensure all selected measurements align with the textual description, especially focusing on baseline stability and anomaly specifics."
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4164 completion=347 latency=13.57s

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
{"scale":"medium","objective":"Detect stable periods and anomalies in the time series.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude"],"validation_requirements":["Check if stable ranges and anomaly details are consistent with text description."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of having stable baseline values within a specific range, with notable anomalies at specified indices.","task_summary":"Select the time series that best matches a textual description involving stable values, spikes, and an extreme outlier.","target_output":"Identify the time series that best fits the described characteristics from the options provided.","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Detect stable periods and anomalies in the time series.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude"],"validation_requirements":["Check if stable ranges and anomaly details are consistent with text description."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]},{"scale":"short","objective":"Locate the anomalous spikes and confirm their magnitudes.","required_measurements":["anomaly_magnitude","change_location"],"validation_requirements":["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],"target_series":[1,2,3,4],"focus_intervals":[[107,142]]}],"hetero_assignments":[{"role":"matching","objective":"Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude","pairwise_similarity"],"validation_requirements":["Cross-validate against the textual description and ensure consistency with chosen time series characteristics."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Time series selected must exhibit features identical to those described in the textual summary."],"notes":"Ensure all selected measurements align with the textual description, especially focusing on baseline stability and anomaly specifics."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective is to detect stable periods and anomalies in the time series and to ensure that the baseline value range and anomaly details are consistent with the text description. This involves analyzing the entire time series to identify stable periods and anomalies, as well as verifying the magnitude and location of specific anomalies.",
  "evidence_plan": {
    "objective": "Detect stable periods and anomalies in the time series.",
    "claims_to_support": [
      {
        "claim": "The time series has stable baseline values within a specific range.",
        "required_evidence": ["value_range"]
      },
      {
        "claim": "There are anomalies located at specific indices.",
        "required_evidence": ["anomaly_location", "anomaly_magnitude"]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2, 3, 4],
      "focus_intervals": [[0, 287]],
      "scale": "medium"
    },
    "validation_needs": ["baseline_value_range", "anomaly_location", "anomaly_magnitude"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "describe_series",
        "reason": "To get an overview of the entire series, including value range and other basic statistics.",
        "supports_evidence": ["value_range"]
      },
      {
        "tool": "anomaly_detect",
        "reason": "To detect anomalies based on z-score thresholds within the specified window.",
        "supports_evidence": ["anomaly_location", "anomaly_magnitude"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=833 completion=153 latency=5.48s

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
{"evidence_plan":{"objective":"Detect stable periods and anomalies in the time series.","claims_to_support":[{"claim":"The time series has stable baseline values within a specific range.","required_evidence":["value_range"]},{"claim":"There are anomalies located at specific indices.","required_evidence":["anomaly_location","anomaly_magnitude"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,287]],"scale":"medium"},"validation_needs":["baseline_value_range","anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"To get an overview of the entire series, including value range and other basic statistics.","supports_evidence":["value_range"]},{"tool":"anomaly_detect","reason":"To detect anomalies based on z-score thresholds within the specified window.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"reasoning":"The objective is to detect stable periods and anomalies in the time series and to ensure that the baseline value range and anomaly details are consistent with the text description. This involves analyzing the entire time series to identify stable periods and anomalies, as well as verifying the magnitude and location of specific anomalies."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- describe_series
  inputs: note
  outputs: series
- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'describe_series' to get an overview of the entire series including the value range, which helps us understand the baseline values within the series. Then, we use 'anomaly_detect' to find anomalies based on z-score thresholds within the specified window, which will provide the location and magnitude of anomalies.",
  "workflow": [
    {
      "step": 1,
      "tool": "describe_series",
      "output_key": "series_overview",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "output_key": "detected_anomalies",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=917 completion=139 latency=5.01s

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
{"workflow":[{"step":1,"tool":"describe_series","output_key":"series_overview","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"detected_anomalies","input_binding":{}}],"reasoning":"First, we use 'describe_series' to get an overview of the entire series including the value range, which helps us understand the baseline values within the series. Then, we use 'anomaly_detect' to find anomalies based on z-score thresholds within the specified window, which will provide the location and magnitude of anomalies."}
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
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"scale":"medium","objective":"Detect stable periods and anomalies in the time series.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude"],"validation_requirements":["Check if stable ranges and anomaly details are consistent with text description."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'describe_series' to get an overview of the entire series including the value range, which helps us understand the baseline values within the series. Then, we use 'anomaly_detect' to find anomalies based on z-score thresholds within the specified window, which will provide the location and magnitude of anomalies.",
  "calls": [
    {
      "step": 1,
      "tool": "describe_series",
      "args": {}
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

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=2041 completion=458 latency=16.74s

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
{"evidence_plan":{"objective":"Detect stable periods and anomalies in the time series.","claims_to_support":[{"claim":"The time series has stable baseline values within a specific range.","required_evidence":["value_range"]},{"claim":"There are anomalies located at specific indices.","required_evidence":["anomaly_location","anomaly_magnitude"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,287]],"scale":"medium"},"validation_needs":["baseline_value_range","anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"To get an overview of the entire series, including value range and other basic statistics.","supports_evidence":["value_range"]},{"tool":"anomaly_detect","reason":"To detect anomalies based on z-score thresholds within the specified window.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"reasoning":"The objective is to detect stable periods and anomalies in the time series and to ensure that the baseline value range and anomaly details are consistent with the text description. This involves analyzing the entire time series to identify stable periods and anomalies, as well as verifying the magnitude and location of specific anomalies."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "medium:step1",
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
          "mean": 4.952430555555555,
          "std": 1.9078562891836137,
          "min": 3.97,
          "max": 26.45,
          "median": 4.63,
          "range": 22.48,
          "p50": 4.63,
          "p90": 5.479,
          "p99": 8.619199999999969,
          "start": 5.3,
          "end": 4.47,
          "slope": -0.0028919860627177702
        },
        {
          "series_index": 2,
          "index": 2,
          "length": 288,
          "mean": 84.02100694444444,
          "std": 20.42108720919401,
          "min": 47.35,
          "max": 100.0,
          "median": 97.48,
          "range": 52.65,
          "p50": 97.48,
          "p90": 99.721,
          "p99": 100.0,
          "start": 99.53,
          "end": 100.0,
          "slope": 0.001637630662020902
        },
        {
          "series_index": 3,
          "index": 3,
          "length": 288,
          "mean": 5.220104166666667,
          "std": 2.627362625171734,
          "min": 0.63,
          "max": 15.92,
          "median": 6.015,
          "range": 15.29,
          "p50": 6.015,
          "p90": 7.87,
          "p99": 10.594699999999994,
          "start": 2.42,
          "end": 3.06,
          "slope": 0.0022299651567944255
        },
        {
          "series_index": 4,
          "index": 4,
          "length": 288,
          "mean": 48.13027777777778,
          "std": 31.14168003399152,
          "min": 2.71,
          "max": 100.76,
          "median": 39.99,
          "range": 98.05000000000001,
          "p50": 39.99,
          "p90": 96.95700000000001,
          "p99": 100.4826,
          "start": 49.39,
          "end": 13.29,
          "slope": -0.12578397212543554
        }
      ]
    },
    "error": null,
    "args_fingerprint": "90b10717d4a3e6c0750bb980207b8d86753ac968"
  },
  {
    "call_id": "medium:step2",
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
      "n_anomalies": 3,
      "anomaly_indices": [
        143,
        144,
        145
      ],
      "max_abs_z": 11.267918640582419
    },
    "error": null,
    "args_fingerprint": "9ee1de07f72732a041d0e186f599357a414ae94b"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Detect stable periods and anomalies in the time series.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude"],"validation_requirements":["Check if stable ranges and anomaly details are consistent with text description."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The time series has been analyzed for stable periods and anomalies using two tools: 'describe_series' and 'anomaly_detect'. The 'describe_series' tool provided an overview of the time series including value ranges, while the 'anomaly_detect' tool detected anomalies based on z-score thresholds. The series with index 1 shows stable baseline values within a specific range and anomalies located at specific indices, which matches the claims to support.",
  "scale": "medium",
  "observations": ["Time series has stable baseline values within a range and contains anomalies.", "Stable baseline values were found between minimum and maximum values reported.", "Anomalies detected at specific indices using z-score thresholds."],
  "evidence_intervals": ["Value range from 3.97 to 26.45", "Anomalies located at indices [143, 144, 145]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The time series has stable baseline values within a specific range.",
      "evidence": [
        {
          "type": "value_range",
          "value": [3.97, 26.45],
          "source_tool": "describe_series",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "value_range"
    },
    {
      "claim": "There are anomalies located at specific indices.",
      "evidence": [
        {
          "type": "anomaly_location",
          "value": [143, 144, 145],
          "source_tool": "anomaly_detect",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomaly_location"
    }
  ],
  "coverage": {"value_range": "tool_supported", "anomaly_location": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4184 completion=304 latency=11.99s

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
{"scale":"short","objective":"Locate the anomalous spikes and confirm their magnitudes.","required_measurements":["anomaly_magnitude","change_location"],"validation_requirements":["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],"target_series":[1,2,3,4],"focus_intervals":[[107,142]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of having stable baseline values within a specific range, with notable anomalies at specified indices.","task_summary":"Select the time series that best matches a textual description involving stable values, spikes, and an extreme outlier.","target_output":"Identify the time series that best fits the described characteristics from the options provided.","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Detect stable periods and anomalies in the time series.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude"],"validation_requirements":["Check if stable ranges and anomaly details are consistent with text description."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]},{"scale":"short","objective":"Locate the anomalous spikes and confirm their magnitudes.","required_measurements":["anomaly_magnitude","change_location"],"validation_requirements":["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],"target_series":[1,2,3,4],"focus_intervals":[[107,142]]}],"hetero_assignments":[{"role":"matching","objective":"Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude","pairwise_similarity"],"validation_requirements":["Cross-validate against the textual description and ensure consistency with chosen time series characteristics."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Time series selected must exhibit features identical to those described in the textual summary."],"notes":"Ensure all selected measurements align with the textual description, especially focusing on baseline stability and anomaly specifics."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria.",
  "evidence_plan": {
    "objective": "Locate the anomalous spikes and confirm their magnitudes.",
    "claims_to_support": [
      {
        "claim": "There are anomalous spikes at text indices 107 and 142.",
        "required_evidence": ["anomaly_location"]
      },
      {
        "claim": "The magnitudes of these anomalous spikes match 7.73 and 26.45.",
        "required_evidence": ["anomaly_magnitude"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [[107, 142]],
      "scale": "short"
    },
    "validation_needs": ["anomaly_location", "anomaly_magnitude"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "anomaly_detect",
        "reason": "Anomalous spikes need to be located and their magnitudes confirmed, which aligns with the anomaly_detect tool's capability to detect and measure spikes.",
        "supports_evidence": ["anomaly_location", "anomaly_magnitude"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=793 completion=139 latency=4.98s

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
{"evidence_plan":{"objective":"Locate the anomalous spikes and confirm their magnitudes.","claims_to_support":[{"claim":"There are anomalous spikes at text indices 107 and 142.","required_evidence":["anomaly_location"]},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","required_evidence":["anomaly_magnitude"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[107,142]],"scale":"short"},"validation_needs":["anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"anomaly_detect","reason":"Anomalous spikes need to be located and their magnitudes confirmed, which aligns with the anomaly_detect tool's capability to detect and measure spikes.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"reasoning":"The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria. Given the provided tools and scope, only the anomaly_detect tool can achieve this.",
  "workflow": [
    {
      "step": 1,
      "tool": "anomaly_detect",
      "output_key": "anomalies",
      "input_binding": {
        "series_index": 1,
        "start": 107,
        "end": 142,
        "z_threshold": 3
      }
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=857 completion=128 latency=4.62s

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
{"workflow":[{"step":1,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"series_index":1,"start":107,"end":142,"z_threshold":3}}],"reasoning":"The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria. Given the provided tools and scope, only the anomaly_detect tool can achieve this."}
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

- anomaly_detect: Detect spikes/outliers via z-score threshold in a window.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, z_threshold=float (default 3.0)}
  returns: {series=anomaly count/indices and max absolute z-score}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<assignment>
{"scale":"short","objective":"Locate the anomalous spikes and confirm their magnitudes.","required_measurements":["anomaly_magnitude","change_location"],"validation_requirements":["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],"target_series":[1,2,3,4],"focus_intervals":[[107,142]]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria. Given the provided tools and scope, only the anomaly_detect tool can achieve this.",
  "calls": [
    {
      "step": 1,
      "tool": "anomaly_detect",
      "args": {
        "series_index": 1,
        "start": 107,
        "end": 142,
        "z_threshold": 3
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1094 completion=352 latency=12.54s

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
{"evidence_plan":{"objective":"Locate the anomalous spikes and confirm their magnitudes.","claims_to_support":[{"claim":"There are anomalous spikes at text indices 107 and 142.","required_evidence":["anomaly_location"]},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","required_evidence":["anomaly_magnitude"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[107,142]],"scale":"short"},"validation_needs":["anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"anomaly_detect","reason":"Anomalous spikes need to be located and their magnitudes confirmed, which aligns with the anomaly_detect tool's capability to detect and measure spikes.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"reasoning":"The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
    "tool_name": "anomaly_detect",
    "arguments": {
      "series_index": 1,
      "start": 107,
      "end": 142,
      "z_threshold": 3
    },
    "resolved_arguments": {
      "series_index": 1,
      "start": 107,
      "end": 142,
      "z_threshold": 3
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": 107,
      "end": 142,
      "z_threshold": 3.0,
      "n_anomalies": 0,
      "anomaly_indices": [],
      "max_abs_z": 2.937606194893875
    },
    "error": null,
    "args_fingerprint": "3a5e6618356a43125415150ae758d6bc8572b262"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Locate the anomalous spikes and confirm their magnitudes.","required_measurements":["anomaly_magnitude","change_location"],"validation_requirements":["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],"target_series":[1,2,3,4],"focus_intervals":[[107,142]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "An attempt was made to find anomalies in the specified text intervals using the anomaly detection tool, but no anomalies were found within the z-score threshold.",
  "scale": "short",
  "observations": ["No anomalous spikes were detected in the specified text intervals."],
  "evidence_intervals": ["[107, 142]"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There are anomalous spikes at text indices 107 and 142.",
      "evidence": [
        {
          "type": "anomaly_location",
          "value": "none",
          "source_tool": "anomaly_detect",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomaly_location"
    },
    {
      "claim": "The magnitudes of these anomalous spikes match 7.73 and 26.45.",
      "evidence": [
        {
          "type": "anomaly_magnitude",
          "value": "not_applicable",
          "source_tool": "anomaly_detect",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomaly_magnitude"
    }
  ],
  "coverage": {"anomaly_location": "tool_supported", "anomaly_magnitude": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=6391 completion=269 latency=11.58s

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
{"role":"matching","objective":"Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude","pairwise_similarity"],"validation_requirements":["Cross-validate against the textual description and ensure consistency with chosen time series characteristics."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}
</assignment>

<plan_context>
{"reasoning":"The task requires identifying which time series among the provided options best matches the given textual description of having stable baseline values within a specific range, with notable anomalies at specified indices.","task_summary":"Select the time series that best matches a textual description involving stable values, spikes, and an extreme outlier.","target_output":"Identify the time series that best fits the described characteristics from the options provided.","answer_type":"choice","capability":"choice","scope":"overall","univariate":true,"homo_assignments":[{"scale":"medium","objective":"Detect stable periods and anomalies in the time series.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude"],"validation_requirements":["Check if stable ranges and anomaly details are consistent with text description."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]},{"scale":"short","objective":"Locate the anomalous spikes and confirm their magnitudes.","required_measurements":["anomaly_magnitude","change_location"],"validation_requirements":["Verify spike locations match text indices 107 and 142, and spike magnitudes match 7.73 and 26.45."],"target_series":[1,2,3,4],"focus_intervals":[[107,142]]}],"hetero_assignments":[{"role":"matching","objective":"Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude","pairwise_similarity"],"validation_requirements":["Cross-validate against the textual description and ensure consistency with chosen time series characteristics."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}],"scales":["medium","short"],"heterogeneous_agents":["matching"],"success_criteria":["Time series selected must exhibit features identical to those described in the textual summary."],"notes":"Ensure all selected measurements align with the textual description, especially focusing on baseline stability and anomaly specifics."}
</plan_context>

<task_summary>
Select the time series that best matches a textual description involving stable values, spikes, and an extreme outlier.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"An attempt was made to find anomalies in the specified text intervals using the anomaly detection tool, but no anomalies were found within the z-score threshold.","scale":"short","observations":["No anomalous spikes were detected in the specified text intervals."],"evidence_intervals":["[107, 142]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": 107, \"end\": 142, \"z_threshold\": 3}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 107, \"end\": 142, \"z_threshold\": 3}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 107, \"end\": 142, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.937606194893875}, \"error\": null, \"args_fingerprint\": \"3a5e6618356a43125415150ae758d6bc8572b262\"}"],"evidence_plan":{"objective":"Locate the anomalous spikes and confirm their magnitudes.","claims_to_support":[{"claim":"There are anomalous spikes at text indices 107 and 142.","required_evidence":["anomaly_location"]},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","required_evidence":["anomaly_magnitude"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[107,142]],"scale":"short"},"validation_needs":["anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"anomaly_detect","reason":"Anomalous spikes need to be located and their magnitudes confirmed, which aligns with the anomaly_detect tool's capability to detect and measure spikes.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"series_index":1,"start":107,"end":142,"z_threshold":3}}],"reasoning":"The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria. Given the provided tools and scope, only the anomaly_detect tool can achieve this."},"structured_observations":[{"claim":"There are anomalous spikes at text indices 107 and 142.","evidence":[{"type":"anomaly_location","value":"none","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","evidence":[{"type":"anomaly_magnitude","value":"not_applicable","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_magnitude"}],"coverage":{"anomaly_location":"tool_supported","anomaly_magnitude":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":107,"end":142,"z_threshold":3},"resolved_arguments":{"series_index":1,"start":107,"end":142,"z_threshold":3},"success":true,"data":{"series_index":1,"start":107,"end":142,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.937606194893875},"error":null,"args_fingerprint":"3a5e6618356a43125415150ae758d6bc8572b262"}],"skipped_stages":[]},"medium":{"reasoning":"The time series has been analyzed for stable periods and anomalies using two tools: 'describe_series' and 'anomaly_detect'. The 'describe_series' tool provided an overview of the time series including value ranges, while the 'anomaly_detect' tool detected anomalies based on z-score thresholds. The series with index 1 shows stable baseline values within a specific range and anomalies located at specific indices, which matches the claims to support.","scale":"medium","observations":["Time series has stable baseline values within a range and contains anomalies.","Stable baseline values were found between minimum and maximum values reported.","Anomalies detected at specific indices using z-score thresholds."],"evidence_intervals":["Value range from 3.97 to 26.45","Anomalies located at indices [143, 144, 145]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 4.952430555555555, \"std\": 1.9078562891836137, \"min\": 3.97, \"max\": 26.45, \"median\": 4.63, \"range\": 22.48, \"p50\": 4.63, \"p90\": 5.479, \"p99\": 8.619199999999969, \"start\": 5.3, \"end\": 4.47, \"slope\": -0.0028919860627177702}, {\"series_index\": 2, \"index\": 2, \"length\": 288, \"mean\": 84.02100694444444, \"std\": 20.42108720919401, \"min\": 47.35, \"max\": 100.0, \"median\": 97.48, \"range\": 52.65, \"p50\": 97.48, \"p90\": 99.721, \"p99\": 100.0, \"start\": 99.53, \"end\": 100.0, \"slope\": 0.001637630662020902}, {\"series_index\": 3, \"index\": 3, \"length\": 288, \"mean\": 5.220104166666667, \"std\": 2.627362625171734, \"min\": 0.63, \"max\": 15.92, \"median\": 6.015, \"range\": 15.29, \"p50\": 6.015, \"p90\": 7.87, \"p99\": 10.594699999999994, \"start\": 2.42, \"end\": 3.06, \"slope\": 0.0022299651567944255}, {\"series_index\": 4, \"index\": 4, \"length\": 288, \"mean\": 48.13027777777778, \"std\": 31.14168003399152, \"min\": 2.71, \"max\": 100.76, \"median\": 39.99, \"range\": 98.05000000000001, \"p50\": 39.99, \"p90\": 96.95700000000001, \"p99\": 100.4826, \"start\": 49.39, \"end\": 13.29, \"slope\": -0.12578397212543554}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 3, \"anomaly_indices\": [143, 144, 145], \"max_abs_z\": 11.267918640582419}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Detect stable periods and anomalies in the time series.","claims_to_support":[{"claim":"The time series has stable baseline values within a specific range.","required_evidence":["value_range"]},{"claim":"There are anomalies located at specific indices.","required_evidence":["anomaly_location","anomaly_magnitude"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,287]],"scale":"medium"},"validation_needs":["baseline_value_range","anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"To get an overview of the entire series, including value range and other basic statistics.","supports_evidence":["value_range"]},{"tool":"anomaly_detect","reason":"To detect anomalies based on z-score thresholds within the specified window.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"series_overview","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"detected_anomalies","input_binding":{}}],"reasoning":"First, we use 'describe_series' to get an overview of the entire series including the value range, which helps us understand the baseline values within the series. Then, we use 'anomaly_detect' to find anomalies based on z-score thresholds within the specified window, which will provide the location and magnitude of anomalies."},"structured_observations":[{"claim":"The time series has stable baseline values within a specific range.","evidence":[{"type":"value_range","value":[3.97,26.45],"source_tool":"describe_series","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"value_range"},{"claim":"There are anomalies located at specific indices.","evidence":[{"type":"anomaly_location","value":[143,144,145],"source_tool":"anomaly_detect","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"}],"coverage":{"value_range":"tool_supported","anomaly_location":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":4.952430555555555,"std":1.9078562891836137,"min":3.97,"max":26.45,"median":4.63,"range":22.48,"p50":4.63,"p90":5.479,"p99":8.619199999999969,"start":5.3,"end":4.47,"slope":-0.0028919860627177702},{"series_index":2,"index":2,"length":288,"mean":84.02100694444444,"std":20.42108720919401,"min":47.35,"max":100.0,"median":97.48,"range":52.65,"p50":97.48,"p90":99.721,"p99":100.0,"start":99.53,"end":100.0,"slope":0.001637630662020902},{"series_index":3,"index":3,"length":288,"mean":5.220104166666667,"std":2.627362625171734,"min":0.63,"max":15.92,"median":6.015,"range":15.29,"p50":6.015,"p90":7.87,"p99":10.594699999999994,"start":2.42,"end":3.06,"slope":0.0022299651567944255},{"series_index":4,"index":4,"length":288,"mean":48.13027777777778,"std":31.14168003399152,"min":2.71,"max":100.76,"median":39.99,"range":98.05000000000001,"p50":39.99,"p90":96.95700000000001,"p99":100.4826,"start":49.39,"end":13.29,"slope":-0.12578397212543554}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"medium:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":3,"anomaly_indices":[143,144,145],"max_abs_z":11.267918640582419},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"long":null,"conflicts":[],"summary":"Time series has stable baseline values within a range and contains anomalies. Stable baseline values were found between minimum and maximum values reported. Anomalies detected at specific indices using z-score thresholds. No anomalous spikes were detected in the specified text intervals.","structured_by_scale":{"medium":[{"claim":"The time series has stable baseline values within a specific range.","evidence":[{"type":"value_range","value":[3.97,26.45],"source_tool":"describe_series","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"value_range"},{"claim":"There are anomalies located at specific indices.","evidence":[{"type":"anomaly_location","value":[143,144,145],"source_tool":"anomaly_detect","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"}],"short":[{"claim":"There are anomalous spikes at text indices 107 and 142.","evidence":[{"type":"anomaly_location","value":"none","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","evidence":[{"type":"anomaly_magnitude","value":"not_applicable","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_magnitude"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides an overview of stable baseline values and anomalies detected through 'describe_series' and 'anomaly_detect', but lacks direct evidence related to the pairwise similarity requirement. Additionally, the textual description indicates expected stable baseline values, anomaly magnitudes, and specific anomaly locations which have not been fully validated.",
  "evidence_plan": {
    "objective": "Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.",
    "claims_to_support": [
      {
        "claim": "Each time series matches the described characteristics, including stable baseline values, presence of anomalies, and anomaly magnitude.",
        "required_evidence": ["baseline_value_range", "anomaly_location", "anomaly_magnitude", "pairwise_similarity"]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2, 3, 4],
      "role": "matching"
    },
    "validation_needs": ["baseline_value_range", "anomaly_location", "anomaly_magnitude", "pairwise_similarity"]
  },
  "capability_selection": {
    "selected_tools": [
      "describe_series",
      "anomaly_detect",
      "pairwise_distance"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=4928 completion=424 latency=16.73s

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
{"evidence_plan":{"objective":"Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"An attempt was made to find anomalies in the specified text intervals using the anomaly detection tool, but no anomalies were found within the z-score threshold.","scale":"short","observations":["No anomalous spikes were detected in the specified text intervals."],"evidence_intervals":["[107, 142]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": 107, \"end\": 142, \"z_threshold\": 3}, \"resolved_arguments\": {\"series_index\": 1, \"start\": 107, \"end\": 142, \"z_threshold\": 3}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": 107, \"end\": 142, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 2.937606194893875}, \"error\": null, \"args_fingerprint\": \"3a5e6618356a43125415150ae758d6bc8572b262\"}"],"evidence_plan":{"objective":"Locate the anomalous spikes and confirm their magnitudes.","claims_to_support":[{"claim":"There are anomalous spikes at text indices 107 and 142.","required_evidence":["anomaly_location"]},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","required_evidence":["anomaly_magnitude"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[[107,142]],"scale":"short"},"validation_needs":["anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"anomaly_detect","reason":"Anomalous spikes need to be located and their magnitudes confirmed, which aligns with the anomaly_detect tool's capability to detect and measure spikes.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"series_index":1,"start":107,"end":142,"z_threshold":3}}],"reasoning":"The objective is to locate anomalous spikes and confirm their magnitudes in the given time series. The required measurements are anomaly magnitudes and change locations, with specific verification criteria. Given the provided tools and scope, only the anomaly_detect tool can achieve this."},"structured_observations":[{"claim":"There are anomalous spikes at text indices 107 and 142.","evidence":[{"type":"anomaly_location","value":"none","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","evidence":[{"type":"anomaly_magnitude","value":"not_applicable","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_magnitude"}],"coverage":{"anomaly_location":"tool_supported","anomaly_magnitude":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":107,"end":142,"z_threshold":3},"resolved_arguments":{"series_index":1,"start":107,"end":142,"z_threshold":3},"success":true,"data":{"series_index":1,"start":107,"end":142,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":2.937606194893875},"error":null,"args_fingerprint":"3a5e6618356a43125415150ae758d6bc8572b262"}],"skipped_stages":[]},"medium":{"reasoning":"The time series has been analyzed for stable periods and anomalies using two tools: 'describe_series' and 'anomaly_detect'. The 'describe_series' tool provided an overview of the time series including value ranges, while the 'anomaly_detect' tool detected anomalies based on z-score thresholds. The series with index 1 shows stable baseline values within a specific range and anomalies located at specific indices, which matches the claims to support.","scale":"medium","observations":["Time series has stable baseline values within a range and contains anomalies.","Stable baseline values were found between minimum and maximum values reported.","Anomalies detected at specific indices using z-score thresholds."],"evidence_intervals":["Value range from 3.97 to 26.45","Anomalies located at indices [143, 144, 145]"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"describe_series\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": true, \"data\": {\"series\": [{\"series_index\": 1, \"index\": 1, \"length\": 288, \"mean\": 4.952430555555555, \"std\": 1.9078562891836137, \"min\": 3.97, \"max\": 26.45, \"median\": 4.63, \"range\": 22.48, \"p50\": 4.63, \"p90\": 5.479, \"p99\": 8.619199999999969, \"start\": 5.3, \"end\": 4.47, \"slope\": -0.0028919860627177702}, {\"series_index\": 2, \"index\": 2, \"length\": 288, \"mean\": 84.02100694444444, \"std\": 20.42108720919401, \"min\": 47.35, \"max\": 100.0, \"median\": 97.48, \"range\": 52.65, \"p50\": 97.48, \"p90\": 99.721, \"p99\": 100.0, \"start\": 99.53, \"end\": 100.0, \"slope\": 0.001637630662020902}, {\"series_index\": 3, \"index\": 3, \"length\": 288, \"mean\": 5.220104166666667, \"std\": 2.627362625171734, \"min\": 0.63, \"max\": 15.92, \"median\": 6.015, \"range\": 15.29, \"p50\": 6.015, \"p90\": 7.87, \"p99\": 10.594699999999994, \"start\": 2.42, \"end\": 3.06, \"slope\": 0.0022299651567944255}, {\"series_index\": 4, \"index\": 4, \"length\": 288, \"mean\": 48.13027777777778, \"std\": 31.14168003399152, \"min\": 2.71, \"max\": 100.76, \"median\": 39.99, \"range\": 98.05000000000001, \"p50\": 39.99, \"p90\": 96.95700000000001, \"p99\": 100.4826, \"start\": 49.39, \"end\": 13.29, \"slope\": -0.12578397212543554}]}, \"error\": null, \"args_fingerprint\": \"90b10717d4a3e6c0750bb980207b8d86753ac968\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 3, \"anomaly_indices\": [143, 144, 145], \"max_abs_z\": 11.267918640582419}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Detect stable periods and anomalies in the time series.","claims_to_support":[{"claim":"The time series has stable baseline values within a specific range.","required_evidence":["value_range"]},{"claim":"There are anomalies located at specific indices.","required_evidence":["anomaly_location","anomaly_magnitude"]}],"analysis_scope":{"target_series":[1,2,3,4],"focus_intervals":[[0,287]],"scale":"medium"},"validation_needs":["baseline_value_range","anomaly_location","anomaly_magnitude"]},"capability_selection":{"selected_tools":[{"tool":"describe_series","reason":"To get an overview of the entire series, including value range and other basic statistics.","supports_evidence":["value_range"]},{"tool":"anomaly_detect","reason":"To detect anomalies based on z-score thresholds within the specified window.","supports_evidence":["anomaly_location","anomaly_magnitude"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"describe_series","output_key":"series_overview","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"detected_anomalies","input_binding":{}}],"reasoning":"First, we use 'describe_series' to get an overview of the entire series including the value range, which helps us understand the baseline values within the series. Then, we use 'anomaly_detect' to find anomalies based on z-score thresholds within the specified window, which will provide the location and magnitude of anomalies."},"structured_observations":[{"claim":"The time series has stable baseline values within a specific range.","evidence":[{"type":"value_range","value":[3.97,26.45],"source_tool":"describe_series","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"value_range"},{"claim":"There are anomalies located at specific indices.","evidence":[{"type":"anomaly_location","value":[143,144,145],"source_tool":"anomaly_detect","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"}],"coverage":{"value_range":"tool_supported","anomaly_location":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"describe_series","arguments":{},"resolved_arguments":{},"success":true,"data":{"series":[{"series_index":1,"index":1,"length":288,"mean":4.952430555555555,"std":1.9078562891836137,"min":3.97,"max":26.45,"median":4.63,"range":22.48,"p50":4.63,"p90":5.479,"p99":8.619199999999969,"start":5.3,"end":4.47,"slope":-0.0028919860627177702},{"series_index":2,"index":2,"length":288,"mean":84.02100694444444,"std":20.42108720919401,"min":47.35,"max":100.0,"median":97.48,"range":52.65,"p50":97.48,"p90":99.721,"p99":100.0,"start":99.53,"end":100.0,"slope":0.001637630662020902},{"series_index":3,"index":3,"length":288,"mean":5.220104166666667,"std":2.627362625171734,"min":0.63,"max":15.92,"median":6.015,"range":15.29,"p50":6.015,"p90":7.87,"p99":10.594699999999994,"start":2.42,"end":3.06,"slope":0.0022299651567944255},{"series_index":4,"index":4,"length":288,"mean":48.13027777777778,"std":31.14168003399152,"min":2.71,"max":100.76,"median":39.99,"range":98.05000000000001,"p50":39.99,"p90":96.95700000000001,"p99":100.4826,"start":49.39,"end":13.29,"slope":-0.12578397212543554}]},"error":null,"args_fingerprint":"90b10717d4a3e6c0750bb980207b8d86753ac968"},{"call_id":"medium:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":3,"anomaly_indices":[143,144,145],"max_abs_z":11.267918640582419},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"long":null,"conflicts":[],"summary":"Time series has stable baseline values within a range and contains anomalies. Stable baseline values were found between minimum and maximum values reported. Anomalies detected at specific indices using z-score thresholds. No anomalous spikes were detected in the specified text intervals.","structured_by_scale":{"medium":[{"claim":"The time series has stable baseline values within a specific range.","evidence":[{"type":"value_range","value":[3.97,26.45],"source_tool":"describe_series","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"value_range"},{"claim":"There are anomalies located at specific indices.","evidence":[{"type":"anomaly_location","value":[143,144,145],"source_tool":"anomaly_detect","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"}],"short":[{"claim":"There are anomalous spikes at text indices 107 and 142.","evidence":[{"type":"anomaly_location","value":"none","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_location"},{"claim":"The magnitudes of these anomalous spikes match 7.73 and 26.45.","evidence":[{"type":"anomaly_magnitude","value":"not_applicable","source_tool":"anomaly_detect","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomaly_magnitude"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.","required_measurements":["baseline_value_range","anomaly_location","anomaly_magnitude","pairwise_similarity"],"validation_requirements":["Cross-validate against the textual description and ensure consistency with chosen time series characteristics."],"target_series":[1,2,3,4],"focus_intervals":[[0,287]]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=['caption']; domain=cloudops; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=4; series_lengths=[288, 288, 288, 288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=None; candidate_series_indices=[1, 2, 3, 4]; align_direction=caption2ts; option_to_series={'A': 1, 'B': 2, 'C': 3, 'D': 4}
</metadata>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, Time Series 1 shows stable baseline values within a range from 3.97 to 26.45 and contains anomalies located at specific indices as detected by the 'anomaly_detect' tool. This matches the characteristics outlined in the assignment.",
  "role": "matching",
  "hypothesis": "Time Series 1 best fits the described characteristics of stable baseline values and anomalies.",
  "evidence": ["The time series has stable baseline values within a specific range.", "Anomalies detected at specific indices using z-score thresholds."],
  "candidate_preference": "A",
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["medium:step1", "medium:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The time series has stable baseline values within a specific range.",
      "evidence": [
        {
          "type": "value_range",
          "value": [3.97, 26.45],
          "provenance": "upstream",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "There are anomalies located at specific indices.",
      "evidence": [
        {
          "type": "anomaly_location",
          "value": [143, 144, 145],
          "provenance": "upstream",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {
    "anomaly_location": "context_supported",
    "baseline_value_range": "context_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1561 completion=190 latency=6.98s

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
'This time series data exhibits relatively stable values around 4.3-5.5 for most observations, with two prominent anomalous spikes: one reaching 7.73 at index 107 and an extreme outlier of 26.45 at index 142, followed by a gradual decline back to baseline levels.' According to the above textual description of a time series, select the time series from the following four options that most accurately reflects the described characteristics.
</question>

<candidates>
A) Time Series 1. B) Time Series 2. C) Time Series 3. D) Time Series 4
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Select the time series that best matches a textual description involving stable values, spikes, and an extreme outlier.",
  "question_type": "choice",
  "required_output": "Identify the time series that best fits the described characteristics from the options provided.",
  "success_criteria": [
    "Time series selected must exhibit features identical to those described in the textual summary."
  ],
  "assignments_brief": [
    {
      "agent": "homo:medium",
      "objective": "Detect stable periods and anomalies in the time series.",
      "required_measurements": [
        "baseline_value_range",
        "anomaly_location",
        "anomaly_magnitude"
      ]
    },
    {
      "agent": "homo:short",
      "objective": "Locate the anomalous spikes and confirm their magnitudes.",
      "required_measurements": [
        "anomaly_magnitude",
        "change_location"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Match each time series against the described characteristics, including baseline stability, presence and magnitude of anomalies.",
      "required_measurements": [
        "baseline_value_range",
        "anomaly_location",
        "anomaly_magnitude",
        "pairwise_similarity"
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
          "type": "anomaly_location",
          "value": "none",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "anomaly_magnitude",
          "value": "not_applicable",
          "trusted": true
        }
      ],
      "coverage": {
        "anomaly_location": "tool_supported",
        "anomaly_magnitude": "tool_supported"
      },
      "summary": "No anomalous spikes were detected in the specified text intervals."
    },
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "value_range",
          "value": [
            3.97,
            26.45
          ],
          "trusted": true
        },
        {
          "series_index": null,
          "type": "anomaly_location",
          "value": [
            143,
            144,
            145
          ],
          "trusted": true
        }
      ],
      "coverage": {
        "value_range": "tool_supported",
        "anomaly_location": "tool_supported"
      },
      "summary": "Time series has stable baseline values within a range and contains anomalies. | Stable baseline values were found between minimum and maximum values reported. | Anomalies detected at specific indices using z-score thresholds."
    }
  },
  "conflicts": [],
  "summary": "Time series has stable baseline values within a range and contains anomalies. Stable baseline values were found between minimum and maximum values reported. Anomalies detected at specific indices using z-score thresholds. No anomalous spikes were detected in the specified text intervals."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
      "hypothesis": "Time Series 1 best fits the described characteristics of stable baseline values and anomalies.",
      "reasoning_chain": [
        "The time series has stable baseline values within a specific range.",
        "value_range=[3.97, 26.45]",
        "There are anomalies located at specific indices.",
        "anomaly_location=[143, 144, 145]"
      ],
      "candidate_preference": "A",
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "value_range",
        "anomaly_location"
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
  "verified_preference": "A",
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
  "reasoning": "Heter reasoning aligns with Homo perception's detection of a stable baseline and anomalies. Homo's medium-scale analysis identified stable values between 3.97 and 26.45, including anomalies at index 143, 144, and 145. Execution metadata confirms preference for 'A'.",
  "answer": "A",
  "explanation": "The perceived stable baseline values and anomaly locations align with the textual description, particularly confirming the extreme outlier at the specified index.",
  "confidence": 0.95,
  "conflicts": [],
  "cited_evidence": ["value_range", "anomaly_location"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": null
  }
}
```
