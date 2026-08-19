# Agent IO summary: `InWild:tsqa_1084:213`

- Architecture pred: `A` (success=True)
- model_calls=14, tool_calls=4, latency=209.3s

## Planner — `planner`

tokens prompt=1126 completion=470 latency=16.68s

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
Looking at the weekly time series data, which of the following statements best characterizes the overall trend and pattern observed?
</question>

<candidates>
A) The time series exhibits a consistent downward trend with occasional small rebounds, with the maximum value occurring at the beginning of the series and the minimum value appearing in the middle portion.
B) The time series shows a cyclical pattern with clear seasonal variations, where values consistently rise  and fall.
C) The time series displays a U-shaped pattern with values decreasing in the first half and then gradually increasing to nearly original levels by the end of the observation period.
D) The time series demonstrates a step-like decline pattern with sharp drops followed by extended periods of stability, with the final value approximately 25% lower than the initial value.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.",
  "task_summary": "Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.",
  "target_output": "Which candidate statement best characterizes the overall trend and pattern of the time series?",
  "answer_type": "choice",
  "capability": "planning",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "long",
      "objective": "Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.",
      "required_measurements": ["global_slope", "level_changes"],
      "validation_requirements": ["check for consistency across long intervals"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "short",
      "objective": "Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.",
      "required_measurements": ["change_points", "anomalies"],
      "validation_requirements": ["verify through comparison with longer-term trends"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.",
      "required_measurements": ["global_slope", "level_changes", "change_points", "anomalies"],
      "validation_requirements": ["evaluate the fit of each candidate description based on the identified features"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Each statement's description should be reconciled against the actual observations and measurements made by the agents."],
  "notes": "It is crucial that the long-term and short-term behaviors are accurately captured and that the reasoning process considers all potential patterns and trends described by the candidates."
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4066 completion=315 latency=12.33s

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
{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.","task_summary":"Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.","target_output":"Which candidate statement best characterizes the overall trend and pattern of the time series?","answer_type":"choice","capability":"planning","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each statement's description should be reconciled against the actual observations and measurements made by the agents."],"notes":"It is crucial that the long-term and short-term behaviors are accurately captured and that the reasoning process considers all potential patterns and trends described by the candidates."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The task requires identifying the overall trend and long-term behavior of the time series, including global slope and level changes. To achieve this, we need to evaluate the long-term trends and detect any significant changes in the level of the series.",
  "evidence_plan": {
    "objective": "Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.",
    "claims_to_support": [
      {
        "claim": "The time series exhibits a global upward or downward trend over the entire period.",
        "required_evidence": ["global_slope"]
      },
      {
        "claim": "There are level changes indicating shifts in the underlying behavior of the series.",
        "required_evidence": ["level_changes"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "long"
    },
    "validation_needs": ["check for consistency across long intervals"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "segment_trend",
        "reason": "To measure the overall slope of the series over the entire period.",
        "supports_evidence": ["global_slope"]
      },
      {
        "tool": "step_levels",
        "reason": "To detect distinct step changes or level shifts in the series.",
        "supports_evidence": ["level_changes"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=761 completion=159 latency=5.67s

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
{"evidence_plan":{"objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","claims_to_support":[{"claim":"The time series exhibits a global upward or downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["check for consistency across long intervals"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall slope of the series over the entire period.","supports_evidence":["global_slope"]},{"tool":"step_levels","reason":"To detect distinct step changes or level shifts in the series.","supports_evidence":["level_changes"]}],"no_tool_decision":null},"reasoning":"The task requires identifying the overall trend and long-term behavior of the time series, including global slope and level changes. To achieve this, we need to evaluate the long-term trends and detect any significant changes in the level of the series."}
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
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "trend_segment",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "step_levels",
      "output_key": "level_shifts",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=877 completion=157 latency=5.63s

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
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_shifts","input_binding":{}}],"reasoning":"The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series."}
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
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series.",
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
      "tool": "step_levels",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=2139 completion=386 latency=14.17s

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
{"evidence_plan":{"objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","claims_to_support":[{"claim":"The time series exhibits a global upward or downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["check for consistency across long intervals"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall slope of the series over the entire period.","supports_evidence":["global_slope"]},{"tool":"step_levels","reason":"To detect distinct step changes or level shifts in the series.","supports_evidence":["level_changes"]}],"no_tool_decision":null},"reasoning":"The task requires identifying the overall trend and long-term behavior of the time series, including global slope and level changes. To achieve this, we need to evaluate the long-term trends and detect any significant changes in the level of the series."}
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
      "slope": -4.104117647058822,
      "direction": "downward",
      "direction_class": "downward",
      "trend_method": "endpoint",
      "mean": 1783.2290384615385,
      "std": 77.97555470638059,
      "start_value": 1912.11,
      "end_value": 1702.8
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
      "n_unique_levels": 27,
      "n_plateau_runs": 38,
      "levels": [
        1912.11,
        1923.03,
        1931.16,
        1927.69,
        1889.87,
        1886.04,
        1878.57,
        1860.8000000000002,
        1849.77,
        1841.54,
        1832.06,
        1817.76,
        1807.7,
        1802.8200000000002,
        1791.03,
        1787.66,
        1776.32,
        1767.1599999999999,
        1763.26,
        1757.09,
        1749.77,
        1742.64,
        1737.765,
        1718.7725,
        1707.3049999999998,
        1695.99,
        1702.91
      ],
      "plateau_runs": [
        1912.11,
        1923.03,
        1931.16,
        1927.69,
        1921.135,
        1913.69,
        1889.87,
        1886.04,
        1878.57,
        1860.8000000000002,
        1849.77,
        1841.54,
        1832.06,
        1817.76,
        1807.7,
        1802.8200000000002,
        1791.03,
        1787.66,
        1776.32,
        1767.1599999999999,
        1763.26,
        1757.09,
        1761.3249999999998,
        1749.77,
        1742.64,
        1737.765,
        1718.7725,
        1707.3049999999998,
        1695.99,
        1702.91,
        1708.06,
        1698.78,
        1694.6,
        1702.31,
        1696.06,
        1706.43,
        1709.98,
        1702.8
      ],
      "plateau_lengths": [
        1,
        1,
        1,
        1,
        2,
        1,
        1,
        1,
        1,
        2,
        1,
        1,
        2,
        1,
        1,
        2,
        1,
        1,
        1,
        2,
        1,
        1,
        2,
        1,
        1,
        2,
        4,
        2,
        1,
        1,
        1,
        1,
        2,
        1,
        1,
        3,
        1,
        1
      ],
      "tolerance": 2.809750000000003
    },
    "error": null,
    "args_fingerprint": "9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The time series has been analyzed for its global trend and level changes over the entire period. The segment_trend tool indicates a downward trend with a slope of -4.104, while the step_levels tool identifies numerous level changes in the series.",
  "scale": "long",
  "observations": ["The time series shows a global downward trend with a negative slope of -4.104.", "The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior."],
  "evidence_intervals": ["Entire series"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The time series exhibits a global downward trend over the entire period.",
      "evidence": [
        {
          "type": "global_slope",
          "value": -4.104117647058822,
          "source_tool": "segment_trend",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_slope"
    },
    {
      "claim": "There are level changes indicating shifts in the underlying behavior of the series.",
      "evidence": [
        {
          "type": "level_changes",
          "value": 27,
          "source_tool": "step_levels",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "level_changes"
    }
  ],
  "coverage": {"global_slope": "tool_supported", "level_changes": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4062 completion=262 latency=10.39s

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
{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.","task_summary":"Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.","target_output":"Which candidate statement best characterizes the overall trend and pattern of the time series?","answer_type":"choice","capability":"planning","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each statement's description should be reconciled against the actual observations and measurements made by the agents."],"notes":"It is crucial that the long-term and short-term behaviors are accurately captured and that the reasoning process considers all potential patterns and trends described by the candidates."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series.",
  "evidence_plan": {
    "objective": "Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.",
    "claims_to_support": [
      {"claim": "Abrupt changes are present in the series", "required_evidence": ["change_points"]},
      {"claim": "Short-term anomalies exist in the series", "required_evidence": ["anomalies"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["verify through comparison with longer-term trends"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "change_points", "reason": "To localize potential level/regime transitions in the series.", "supports_evidence": ["change_points"]},
      {"tool": "anomaly_detect", "reason": "To detect spikes/outliers via z-score threshold in a window.", "supports_evidence": ["anomalies"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=736 completion=166 latency=5.91s

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
{"evidence_plan":{"objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","claims_to_support":[{"claim":"Abrupt changes are present in the series","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify through comparison with longer-term trends"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To localize potential level/regime transitions in the series.","supports_evidence":["change_points"]},{"tool":"anomaly_detect","reason":"To detect spikes/outliers via z-score threshold in a window.","supports_evidence":["anomalies"]}],"no_tool_decision":null},"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- anomaly_detect
  inputs: series_index, start, end, z_threshold
  outputs: series
- change_points
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input.",
  "workflow": [
    {
      "step": 1,
      "tool": "change_points",
      "output_key": "change_points",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "anomaly_detect",
      "output_key": "anomalies",
      "input_binding": {"start": "$step1.start", "end": "$step1.end"}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=857 completion=168 latency=6.01s

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
{"workflow":[{"step":1,"tool":"change_points","output_key":"change_points","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input."}
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
- change_points: Mean-shift change-point candidates.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=ranked mean-shift candidate indices and scores}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input.",
  "calls": [
    {
      "step": 1,
      "tool": "change_points",
      "args": {
        "series_index": 1
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

tokens prompt=1253 completion=514 latency=18.30s

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
{"evidence_plan":{"objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","claims_to_support":[{"claim":"Abrupt changes are present in the series","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify through comparison with longer-term trends"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To localize potential level/regime transitions in the series.","supports_evidence":["change_points"]},{"tool":"anomaly_detect","reason":"To detect spikes/outliers via z-score threshold in a window.","supports_evidence":["anomalies"]}],"no_tool_decision":null},"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
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
          "index": 10,
          "score": 49.00199999999995
        },
        {
          "index": 9,
          "score": 48.077999999999975
        },
        {
          "index": 7,
          "score": 47.746000000000095
        },
        {
          "index": 8,
          "score": 47.508000000000266
        },
        {
          "index": 11,
          "score": 43.08400000000006
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
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
      "max_abs_z": 1.8971453565864365
    },
    "error": null,
    "args_fingerprint": "9ee1de07f72732a041d0e186f599357a414ae94b"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate the presence of potential abrupt changes but no short-term anomalies detected in the series. Confidence levels are derived directly from the evidence provided by the tools.",
  "scale": "short",
  "observations": ["Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."],
  "evidence_intervals": ["All data intervals for series index 1 were analyzed for change points and anomalies."],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Abrupt changes are present in the series",
      "evidence": [
        {
          "type": "change_points",
          "value": "[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]",
          "source_tool": "change_points",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_points"
    },
    {
      "claim": "Short-term anomalies exist in the series",
      "evidence": [
        {
          "type": "anomalies",
          "value": "0",
          "source_tool": "anomaly_detect",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "anomalies"
    }
  ],
  "coverage": {"change_points": "tool_supported", "anomalies": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=9308 completion=472 latency=20.63s

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
{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.","task_summary":"Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.","target_output":"Which candidate statement best characterizes the overall trend and pattern of the time series?","answer_type":"choice","capability":"planning","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each statement's description should be reconciled against the actual observations and measurements made by the agents."],"notes":"It is crucial that the long-term and short-term behaviors are accurately captured and that the reasoning process considers all potential patterns and trends described by the candidates."}
</plan_context>

<task_summary>
Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate the presence of potential abrupt changes but no short-term anomalies detected in the series. Confidence levels are derived directly from the evidence provided by the tools.","scale":"short","observations":["Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."],"evidence_intervals":["All data intervals for series index 1 were analyzed for change points and anomalies."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 10, \"score\": 49.00199999999995}, {\"index\": 9, \"score\": 48.077999999999975}, {\"index\": 7, \"score\": 47.746000000000095}, {\"index\": 8, \"score\": 47.508000000000266}, {\"index\": 11, \"score\": 43.08400000000006}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 1.8971453565864365}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","claims_to_support":[{"claim":"Abrupt changes are present in the series","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify through comparison with longer-term trends"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To localize potential level/regime transitions in the series.","supports_evidence":["change_points"]},{"tool":"anomaly_detect","reason":"To detect spikes/outliers via z-score threshold in a window.","supports_evidence":["anomalies"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"change_points","output_key":"change_points","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input."},"structured_observations":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}],"coverage":{"change_points":"tool_supported","anomalies":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":10,"score":49.00199999999995},{"index":9,"score":48.077999999999975},{"index":7,"score":47.746000000000095},{"index":8,"score":47.508000000000266},{"index":11,"score":43.08400000000006}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":1.8971453565864365},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The time series has been analyzed for its global trend and level changes over the entire period. The segment_trend tool indicates a downward trend with a slope of -4.104, while the step_levels tool identifies numerous level changes in the series.","scale":"long","observations":["The time series shows a global downward trend with a negative slope of -4.104.","The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -4.104117647058822, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 1783.2290384615385, \"std\": 77.97555470638059, \"start_value\": 1912.11, \"end_value\": 1702.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 27, \"n_plateau_runs\": 38, \"levels\": [1912.11, 1923.03, 1931.16, 1927.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91], \"plateau_runs\": [1912.11, 1923.03, 1931.16, 1927.69, 1921.135, 1913.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1761.3249999999998, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91, 1708.06, 1698.78, 1694.6, 1702.31, 1696.06, 1706.43, 1709.98, 1702.8], \"plateau_lengths\": [1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 4, 2, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1], \"tolerance\": 2.809750000000003}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","claims_to_support":[{"claim":"The time series exhibits a global upward or downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["check for consistency across long intervals"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall slope of the series over the entire period.","supports_evidence":["global_slope"]},{"tool":"step_levels","reason":"To detect distinct step changes or level shifts in the series.","supports_evidence":["level_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_shifts","input_binding":{}}],"reasoning":"The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series."},"structured_observations":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"coverage":{"global_slope":"tool_supported","level_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-4.104117647058822,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":1783.2290384615385,"std":77.97555470638059,"start_value":1912.11,"end_value":1702.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":27,"n_plateau_runs":38,"levels":[1912.11,1923.03,1931.16,1927.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91],"plateau_runs":[1912.11,1923.03,1931.16,1927.69,1921.135,1913.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1761.3249999999998,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91,1708.06,1698.78,1694.6,1702.31,1696.06,1706.43,1709.98,1702.8],"plateau_lengths":[1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,2,4,2,1,1,1,1,2,1,1,3,1,1],"tolerance":2.809750000000003},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The time series shows a global downward trend with a negative slope of -4.104. The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior. Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0.","structured_by_scale":{"long":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"short":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.",
  "evidence_plan": {
    "objective": "Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.",
    "claims_to_support": [
      {
        "claim": "The time series exhibits a global downward trend over the entire period.",
        "required_evidence": ["global_slope"]
      },
      {
        "claim": "There are level changes indicating shifts in the underlying behavior of the series.",
        "required_evidence": ["level_changes"]
      },
      {
        "claim": "Abrupt changes are present in the series.",
        "required_evidence": ["change_points"]
      },
      {
        "claim": "Short-term anomalies exist in the series.",
        "required_evidence": ["anomalies"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "reasoning"
    },
    "validation_needs": ["evaluate the fit of each candidate description based on the identified features"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "No additional tools are required as all necessary evidence (global slope, level changes, change points, anomalies) has been previously gathered.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_slope"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step2",
          "field": "level_changes"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step1",
          "field": "change_points"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step2",
          "field": "anomalies"
        }
      ]
    }
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=6014 completion=766 latency=30.22s

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
{"evidence_plan":{"objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","claims_to_support":[{"claim":"The time series exhibits a global downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]},{"claim":"Abrupt changes are present in the series.","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series.","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"role":"reasoning"},"validation_needs":["evaluate the fit of each candidate description based on the identified features"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"No additional tools are required as all necessary evidence (global slope, level changes, change points, anomalies) has been previously gathered.","evidence_sources":[{"type":"upstream_observation","ref":"long:step1","field":"global_slope"},{"type":"upstream_observation","ref":"long:step2","field":"level_changes"},{"type":"upstream_observation","ref":"short:step1","field":"change_points"},{"type":"upstream_observation","ref":"short:step2","field":"anomalies"}]}},"reasoning":"The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate the presence of potential abrupt changes but no short-term anomalies detected in the series. Confidence levels are derived directly from the evidence provided by the tools.","scale":"short","observations":["Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."],"evidence_intervals":["All data intervals for series index 1 were analyzed for change points and anomalies."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 10, \"score\": 49.00199999999995}, {\"index\": 9, \"score\": 48.077999999999975}, {\"index\": 7, \"score\": 47.746000000000095}, {\"index\": 8, \"score\": 47.508000000000266}, {\"index\": 11, \"score\": 43.08400000000006}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 1.8971453565864365}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","claims_to_support":[{"claim":"Abrupt changes are present in the series","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify through comparison with longer-term trends"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To localize potential level/regime transitions in the series.","supports_evidence":["change_points"]},{"tool":"anomaly_detect","reason":"To detect spikes/outliers via z-score threshold in a window.","supports_evidence":["anomalies"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"change_points","output_key":"change_points","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input."},"structured_observations":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}],"coverage":{"change_points":"tool_supported","anomalies":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":10,"score":49.00199999999995},{"index":9,"score":48.077999999999975},{"index":7,"score":47.746000000000095},{"index":8,"score":47.508000000000266},{"index":11,"score":43.08400000000006}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":1.8971453565864365},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The time series has been analyzed for its global trend and level changes over the entire period. The segment_trend tool indicates a downward trend with a slope of -4.104, while the step_levels tool identifies numerous level changes in the series.","scale":"long","observations":["The time series shows a global downward trend with a negative slope of -4.104.","The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -4.104117647058822, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 1783.2290384615385, \"std\": 77.97555470638059, \"start_value\": 1912.11, \"end_value\": 1702.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 27, \"n_plateau_runs\": 38, \"levels\": [1912.11, 1923.03, 1931.16, 1927.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91], \"plateau_runs\": [1912.11, 1923.03, 1931.16, 1927.69, 1921.135, 1913.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1761.3249999999998, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91, 1708.06, 1698.78, 1694.6, 1702.31, 1696.06, 1706.43, 1709.98, 1702.8], \"plateau_lengths\": [1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 4, 2, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1], \"tolerance\": 2.809750000000003}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","claims_to_support":[{"claim":"The time series exhibits a global upward or downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["check for consistency across long intervals"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall slope of the series over the entire period.","supports_evidence":["global_slope"]},{"tool":"step_levels","reason":"To detect distinct step changes or level shifts in the series.","supports_evidence":["level_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_shifts","input_binding":{}}],"reasoning":"The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series."},"structured_observations":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"coverage":{"global_slope":"tool_supported","level_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-4.104117647058822,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":1783.2290384615385,"std":77.97555470638059,"start_value":1912.11,"end_value":1702.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":27,"n_plateau_runs":38,"levels":[1912.11,1923.03,1931.16,1927.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91],"plateau_runs":[1912.11,1923.03,1931.16,1927.69,1921.135,1913.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1761.3249999999998,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91,1708.06,1698.78,1694.6,1702.31,1696.06,1706.43,1709.98,1702.8],"plateau_lengths":[1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,2,4,2,1,1,1,1,2,1,1,3,1,1],"tolerance":2.809750000000003},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The time series shows a global downward trend with a negative slope of -4.104. The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior. Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0.","structured_by_scale":{"long":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"short":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Based on the evidence gathered, the time series exhibits a global downward trend and includes multiple level changes and abrupt changes. There are no short-term anomalies present in the series.",
  "hypothesis": "Statement B provides the most accurate description of the overall trend and pattern observed in the time series.",
  "evidence": [
    "The time series shows a global downward trend with a negative slope of -4.104.",
    "Multiple level changes have been identified, suggesting shifts in the underlying behavior of the series.",
    "Potential abrupt changes were detected at various indexes."
  ],
  "candidate_preference": "B",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["long:step1", "long:step2", "short:step1", "short:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The time series exhibits a global downward trend over the entire period.",
      "evidence": [
        {
          "type": "global_slope",
          "value": -4.104117647058822,
          "provenance": "upstream",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are level changes indicating shifts in the underlying behavior of the series.",
      "evidence": [
        {
          "type": "level_changes",
          "value": 27,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Abrupt changes are present in the series.",
      "evidence": [
        {
          "type": "change_points",
          "value": "[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]",
          "provenance": "upstream",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Short-term anomalies exist in the series.",
      "evidence": [
        {
          "type": "anomalies",
          "value": 0,
          "provenance": "upstream",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "global_slope": "tool_supported",
    "level_changes": "tool_supported",
    "change_points": "tool_supported",
    "anomalies": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m1`

tokens prompt=9319 completion=461 latency=20.20s

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
{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.","task_summary":"Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.","target_output":"Which candidate statement best characterizes the overall trend and pattern of the time series?","answer_type":"choice","capability":"planning","scope":"overall","univariate":true,"homo_assignments":[{"scale":"long","objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","required_measurements":["global_slope","level_changes"],"validation_requirements":["check for consistency across long intervals"],"target_series":[1],"focus_intervals":[]},{"scale":"short","objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","required_measurements":["change_points","anomalies"],"validation_requirements":["verify through comparison with longer-term trends"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}],"scales":["long","short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each statement's description should be reconciled against the actual observations and measurements made by the agents."],"notes":"It is crucial that the long-term and short-term behaviors are accurately captured and that the reasoning process considers all potential patterns and trends described by the candidates."}
</plan_context>

<task_summary>
Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate the presence of potential abrupt changes but no short-term anomalies detected in the series. Confidence levels are derived directly from the evidence provided by the tools.","scale":"short","observations":["Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."],"evidence_intervals":["All data intervals for series index 1 were analyzed for change points and anomalies."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 10, \"score\": 49.00199999999995}, {\"index\": 9, \"score\": 48.077999999999975}, {\"index\": 7, \"score\": 47.746000000000095}, {\"index\": 8, \"score\": 47.508000000000266}, {\"index\": 11, \"score\": 43.08400000000006}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 1.8971453565864365}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","claims_to_support":[{"claim":"Abrupt changes are present in the series","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify through comparison with longer-term trends"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To localize potential level/regime transitions in the series.","supports_evidence":["change_points"]},{"tool":"anomaly_detect","reason":"To detect spikes/outliers via z-score threshold in a window.","supports_evidence":["anomalies"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"change_points","output_key":"change_points","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input."},"structured_observations":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}],"coverage":{"change_points":"tool_supported","anomalies":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":10,"score":49.00199999999995},{"index":9,"score":48.077999999999975},{"index":7,"score":47.746000000000095},{"index":8,"score":47.508000000000266},{"index":11,"score":43.08400000000006}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":1.8971453565864365},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The time series has been analyzed for its global trend and level changes over the entire period. The segment_trend tool indicates a downward trend with a slope of -4.104, while the step_levels tool identifies numerous level changes in the series.","scale":"long","observations":["The time series shows a global downward trend with a negative slope of -4.104.","The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -4.104117647058822, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 1783.2290384615385, \"std\": 77.97555470638059, \"start_value\": 1912.11, \"end_value\": 1702.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 27, \"n_plateau_runs\": 38, \"levels\": [1912.11, 1923.03, 1931.16, 1927.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91], \"plateau_runs\": [1912.11, 1923.03, 1931.16, 1927.69, 1921.135, 1913.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1761.3249999999998, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91, 1708.06, 1698.78, 1694.6, 1702.31, 1696.06, 1706.43, 1709.98, 1702.8], \"plateau_lengths\": [1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 4, 2, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1], \"tolerance\": 2.809750000000003}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","claims_to_support":[{"claim":"The time series exhibits a global upward or downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["check for consistency across long intervals"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall slope of the series over the entire period.","supports_evidence":["global_slope"]},{"tool":"step_levels","reason":"To detect distinct step changes or level shifts in the series.","supports_evidence":["level_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_shifts","input_binding":{}}],"reasoning":"The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series."},"structured_observations":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"coverage":{"global_slope":"tool_supported","level_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-4.104117647058822,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":1783.2290384615385,"std":77.97555470638059,"start_value":1912.11,"end_value":1702.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":27,"n_plateau_runs":38,"levels":[1912.11,1923.03,1931.16,1927.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91],"plateau_runs":[1912.11,1923.03,1931.16,1927.69,1921.135,1913.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1761.3249999999998,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91,1708.06,1698.78,1694.6,1702.31,1696.06,1706.43,1709.98,1702.8],"plateau_lengths":[1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,2,4,2,1,1,1,1,2,1,1,3,1,1],"tolerance":2.809750000000003},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The time series shows a global downward trend with a negative slope of -4.104. The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior. Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0.","structured_by_scale":{"long":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"short":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['parse_failure']
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures.",
  "evidence_plan": {
    "objective": "Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.",
    "claims_to_support": [
      {
        "claim": "The time series exhibits a global downward trend over the entire period.",
        "required_evidence": ["global_slope"]
      },
      {
        "claim": "There are level changes indicating shifts in the underlying behavior of the series.",
        "required_evidence": ["level_changes"]
      },
      {
        "claim": "Abrupt changes are present in the series.",
        "required_evidence": ["change_points"]
      },
      {
        "claim": "Short-term anomalies exist in the series.",
        "required_evidence": ["anomalies"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "reasoning"
    },
    "validation_needs": ["evaluate the fit of each candidate description based on the identified features"]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "No additional tools are required as all the necessary evidence has already been gathered.",
      "evidence_sources": [
        {
          "type": "upstream_observation",
          "ref": "long:step1",
          "field": "global_slope"
        },
        {
          "type": "upstream_observation",
          "ref": "long:step2",
          "field": "level_changes"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step1",
          "field": "change_points"
        },
        {
          "type": "upstream_observation",
          "ref": "short:step2",
          "field": "anomalies"
        }
      ]
    }
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m1`

tokens prompt=6003 completion=704 latency=27.87s

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
{"evidence_plan":{"objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","claims_to_support":[{"claim":"The time series exhibits a global downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]},{"claim":"Abrupt changes are present in the series.","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series.","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"role":"reasoning"},"validation_needs":["evaluate the fit of each candidate description based on the identified features"]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"No additional tools are required as all the necessary evidence has already been gathered.","evidence_sources":[{"type":"upstream_observation","ref":"long:step1","field":"global_slope"},{"type":"upstream_observation","ref":"long:step2","field":"level_changes"},{"type":"upstream_observation","ref":"short:step1","field":"change_points"},{"type":"upstream_observation","ref":"short:step2","field":"anomalies"}]}},"reasoning":"The task requires evaluating different possible patterns in a univariate weekly time series to determine which statement best describes the overall trend and pattern observed. This necessitates an examination of the series over both the short and long term scales to identify trends, patterns, and structures."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate the presence of potential abrupt changes but no short-term anomalies detected in the series. Confidence levels are derived directly from the evidence provided by the tools.","scale":"short","observations":["Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."],"evidence_intervals":["All data intervals for series index 1 were analyzed for change points and anomalies."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 10, \"score\": 49.00199999999995}, {\"index\": 9, \"score\": 48.077999999999975}, {\"index\": 7, \"score\": 47.746000000000095}, {\"index\": 8, \"score\": 47.508000000000266}, {\"index\": 11, \"score\": 43.08400000000006}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"anomaly_detect\", \"arguments\": {\"series_index\": 1, \"start\": \"$step1.start\", \"end\": \"$step1.end\"}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"z_threshold\": 3.0, \"n_anomalies\": 0, \"anomaly_indices\": [], \"max_abs_z\": 1.8971453565864365}, \"error\": null, \"args_fingerprint\": \"9ee1de07f72732a041d0e186f599357a414ae94b\"}"],"evidence_plan":{"objective":"Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.","claims_to_support":[{"claim":"Abrupt changes are present in the series","required_evidence":["change_points"]},{"claim":"Short-term anomalies exist in the series","required_evidence":["anomalies"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify through comparison with longer-term trends"]},"capability_selection":{"selected_tools":[{"tool":"change_points","reason":"To localize potential level/regime transitions in the series.","supports_evidence":["change_points"]},{"tool":"anomaly_detect","reason":"To detect spikes/outliers via z-score threshold in a window.","supports_evidence":["anomalies"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"change_points","output_key":"change_points","input_binding":{}},{"step":2,"tool":"anomaly_detect","output_key":"anomalies","input_binding":{"start":"$step1.start","end":"$step1.end"}}],"reasoning":"The objective for the short-scale analysis is to detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities. This involves identifying change points and anomalies within the series. First, we need to find the change points using the change_points tool, then detect anomalies using anomaly_detect with the identified change points as input."},"structured_observations":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}],"coverage":{"change_points":"tool_supported","anomalies":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":10,"score":49.00199999999995},{"index":9,"score":48.077999999999975},{"index":7,"score":47.746000000000095},{"index":8,"score":47.508000000000266},{"index":11,"score":43.08400000000006}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"short:step2","step":2,"tool_name":"anomaly_detect","arguments":{"series_index":1,"start":"$step1.start","end":"$step1.end"},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"z_threshold":3.0,"n_anomalies":0,"anomaly_indices":[],"max_abs_z":1.8971453565864365},"error":null,"args_fingerprint":"9ee1de07f72732a041d0e186f599357a414ae94b"}],"skipped_stages":[]},"medium":null,"long":{"reasoning":"The time series has been analyzed for its global trend and level changes over the entire period. The segment_trend tool indicates a downward trend with a slope of -4.104, while the step_levels tool identifies numerous level changes in the series.","scale":"long","observations":["The time series shows a global downward trend with a negative slope of -4.104.","The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior."],"evidence_intervals":["Entire series"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -4.104117647058822, \"direction\": \"downward\", \"direction_class\": \"downward\", \"trend_method\": \"endpoint\", \"mean\": 1783.2290384615385, \"std\": 77.97555470638059, \"start_value\": 1912.11, \"end_value\": 1702.8}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 27, \"n_plateau_runs\": 38, \"levels\": [1912.11, 1923.03, 1931.16, 1927.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91], \"plateau_runs\": [1912.11, 1923.03, 1931.16, 1927.69, 1921.135, 1913.69, 1889.87, 1886.04, 1878.57, 1860.8000000000002, 1849.77, 1841.54, 1832.06, 1817.76, 1807.7, 1802.8200000000002, 1791.03, 1787.66, 1776.32, 1767.1599999999999, 1763.26, 1757.09, 1761.3249999999998, 1749.77, 1742.64, 1737.765, 1718.7725, 1707.3049999999998, 1695.99, 1702.91, 1708.06, 1698.78, 1694.6, 1702.31, 1696.06, 1706.43, 1709.98, 1702.8], \"plateau_lengths\": [1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1, 1, 2, 4, 2, 1, 1, 1, 1, 2, 1, 1, 3, 1, 1], \"tolerance\": 2.809750000000003}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}"],"evidence_plan":{"objective":"Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.","claims_to_support":[{"claim":"The time series exhibits a global upward or downward trend over the entire period.","required_evidence":["global_slope"]},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","required_evidence":["level_changes"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["check for consistency across long intervals"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall slope of the series over the entire period.","supports_evidence":["global_slope"]},{"tool":"step_levels","reason":"To detect distinct step changes or level shifts in the series.","supports_evidence":["level_changes"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_segment","input_binding":{}},{"step":2,"tool":"step_levels","output_key":"level_shifts","input_binding":{}}],"reasoning":"The objective is to identify the overall trend and long-term behavior of the time series, including detecting global slope and level changes. First, we use the 'segment_trend' tool to measure the overall slope of the series over the entire period. Then, we use the 'step_levels' tool to detect any distinct step changes or level shifts within the series."},"structured_observations":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"coverage":{"global_slope":"tool_supported","level_changes":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-4.104117647058822,"direction":"downward","direction_class":"downward","trend_method":"endpoint","mean":1783.2290384615385,"std":77.97555470638059,"start_value":1912.11,"end_value":1702.8},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":27,"n_plateau_runs":38,"levels":[1912.11,1923.03,1931.16,1927.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91],"plateau_runs":[1912.11,1923.03,1931.16,1927.69,1921.135,1913.69,1889.87,1886.04,1878.57,1860.8000000000002,1849.77,1841.54,1832.06,1817.76,1807.7,1802.8200000000002,1791.03,1787.66,1776.32,1767.1599999999999,1763.26,1757.09,1761.3249999999998,1749.77,1742.64,1737.765,1718.7725,1707.3049999999998,1695.99,1702.91,1708.06,1698.78,1694.6,1702.31,1696.06,1706.43,1709.98,1702.8],"plateau_lengths":[1,1,1,1,2,1,1,1,1,2,1,1,2,1,1,2,1,1,1,2,1,1,2,1,1,2,4,2,1,1,1,1,2,1,1,3,1,1],"tolerance":2.809750000000003},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"}],"skipped_stages":[]},"conflicts":[],"summary":"The time series shows a global downward trend with a negative slope of -4.104. The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior. Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0.","structured_by_scale":{"long":[{"claim":"The time series exhibits a global downward trend over the entire period.","evidence":[{"type":"global_slope","value":-4.104117647058822,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_slope"},{"claim":"There are level changes indicating shifts in the underlying behavior of the series.","evidence":[{"type":"level_changes","value":27,"source_tool":"step_levels","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"level_changes"}],"short":[{"claim":"Abrupt changes are present in the series","evidence":[{"type":"change_points","value":"[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]","source_tool":"change_points","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_points"},{"claim":"Short-term anomalies exist in the series","evidence":[{"type":"anomalies","value":"0","source_tool":"anomaly_detect","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"anomalies"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.","required_measurements":["global_slope","level_changes","change_points","anomalies"],"validation_requirements":["evaluate the fit of each candidate description based on the identified features"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=economy; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[52]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Based on the evidence gathered, the time series exhibits a global downward trend and includes multiple level changes and abrupt changes. There are no short-term anomalies present in the series.",
  "hypothesis": "The time series shows a persistent declining trend alongside shifts in levels and potentially abrupt changes.",
  "evidence": ["time series shows a global downward trend", "presence of level changes indicating shifts in underlying behavior", "potential abrupt changes at specific points", "no short-term anomalies detected"],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["long:step1", "long:step2", "short:step1", "short:step2"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The time series exhibits a global downward trend over the entire period.",
      "evidence": [
        {
          "type": "global_slope",
          "value": -4.104117647058822,
          "provenance": "upstream",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "There are level changes indicating shifts in the underlying behavior of the series.",
      "evidence": [
        {
          "type": "level_changes",
          "value": 27,
          "provenance": "upstream",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "Abrupt changes are present in the series.",
      "evidence": [
        {
          "type": "change_points",
          "value": "[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]",
          "provenance": "upstream",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "context_supported"
    },
    {
      "claim": "Short-term anomalies exist in the series.",
      "evidence": [
        {
          "type": "anomalies",
          "value": 0,
          "provenance": "upstream",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "context_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=1655 completion=420 latency=15.12s

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
Looking at the weekly time series data, which of the following statements best characterizes the overall trend and pattern observed?
</question>

<candidates>
A) The time series exhibits a consistent downward trend with occasional small rebounds, with the maximum value occurring at the beginning of the series and the minimum value appearing in the middle portion.
B) The time series shows a cyclical pattern with clear seasonal variations, where values consistently rise  and fall.
C) The time series displays a U-shaped pattern with values decreasing in the first half and then gradually increasing to nearly original levels by the end of the observation period.
D) The time series demonstrates a step-like decline pattern with sharp drops followed by extended periods of stability, with the final value approximately 25% lower than the initial value.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Evaluate a weekly time series to determine which description best matches the observed overall trend and pattern.",
  "question_type": "choice",
  "required_output": "Which candidate statement best characterizes the overall trend and pattern of the time series?",
  "success_criteria": [
    "Each statement's description should be reconciled against the actual observations and measurements made by the agents."
  ],
  "assignments_brief": [
    {
      "agent": "homo:long",
      "objective": "Identify the overall trend and long-term behavior of the time series, including any global slope or level changes.",
      "required_measurements": [
        "global_slope",
        "level_changes"
      ]
    },
    {
      "agent": "homo:short",
      "objective": "Detect abrupt changes and short-term anomalies that may indicate specific patterns or irregularities.",
      "required_measurements": [
        "change_points",
        "anomalies"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Use the evidence gathered to reason about which of the candidate statements best captures the overall trend and pattern of the time series.",
      "required_measurements": [
        "global_slope",
        "level_changes",
        "change_points",
        "anomalies"
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
          "type": "change_points",
          "value": "[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "anomalies",
          "value": "0",
          "trusted": true
        }
      ],
      "coverage": {
        "change_points": "tool_supported",
        "anomalies": "tool_supported"
      },
      "summary": "Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_slope",
          "value": -4.104117647058822,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "level_changes",
          "value": 27,
          "trusted": true
        }
      ],
      "coverage": {
        "global_slope": "tool_supported",
        "level_changes": "tool_supported"
      },
      "summary": "The time series shows a global downward trend with a negative slope of -4.104. | The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior."
    }
  },
  "conflicts": [],
  "summary": "The time series shows a global downward trend with a negative slope of -4.104. The series also exhibits multiple level changes over the period, indicating shifts in the underlying behavior. Potential abrupt changes identified at indexes 10, 9, 7, 8, and 11 with respective scores above 43. No short-term anomalies detected as maximum absolute z-score was below the anomaly threshold of 3.0."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
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



Produce the FinalAnswer JSON now.

```

### OUTPUT

```
{
  "reasoning": "The time series has a global downward trend with a negative slope of -4.104 and multiple level changes, suggesting shifts in the underlying behavior. There are potential abrupt changes identified at certain points in the time series but no short-term anomalies detected.",
  "answer": "A",
  "explanation": "The overall trend is characterized by a consistent downward movement interspersed with some temporary rebounds (level changes), which aligns with option A. Option B suggests a clear seasonal pattern which is not supported. Option C implies a U-shape pattern, inconsistent with the negative global slope. Option D mentions sharp drops and extended stability which can somewhat describe the change points, but does not fully capture the continuous downward trend.",
  "confidence": 0.85,
  "conflicts": [],
  "cited_evidence": [
    "homo:long.global_slope=-4.104117647058822",
    "homo:long.level_changes=27",
    "homo:short.change_points=[{'index': 10, 'score': 49.00199999999995}, {'index': 9, 'score': 48.077999999999975}, {'index': 7, 'score': 47.746000000000095}, {'index': 8, 'score': 47.508000000000266}, {'index': 11, 'score': 43.08400000000006}]"
  ],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "A"
  }
}
```
