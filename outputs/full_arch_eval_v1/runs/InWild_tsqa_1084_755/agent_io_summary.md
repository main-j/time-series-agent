# Agent IO summary: `InWild:tsqa_1084:755`

- Architecture pred: `B` (success=True)
- model_calls=12, tool_calls=10, latency=159.9s

## Planner — `planner`

tokens prompt=1025 completion=404 latency=14.33s

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
According to time series data analysis, which one has a higher fluctuation frequency, Time Series 1 or Time Series 2?
</question>

<candidates>
A) Time Series 2
B) Time Series 1
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires comparing the fluctuation frequency between two time series. This involves analyzing the short-term variability within each time series.",
  "task_summary": "Determine which time series exhibits higher fluctuation frequency.",
  "target_output": "A) Time Series 2 | B) Time Series 1",
  "answer_type": "choice",
  "capability": "time_series_analysis",
  "scope": "overall",
  "univariate": false,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Identify and quantify short-term variations for Time Series 1.",
      "required_measurements": ["variability", "fluctuation_frequency"],
      "validation_requirements": ["reliability of measurements over different segments"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "short",
      "objective": "Identify and quantify short-term variations for Time Series 2.",
      "required_measurements": ["variability", "fluctuation_frequency"],
      "validation_requirements": ["reliability of measurements over different segments"],
      "target_series": [2],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.",
      "required_measurements": ["variability", "fluctuation_frequency"],
      "validation_requirements": ["cross-validation of findings by multiple short-term analysis"],
      "target_series": [1, 2],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Identification of higher fluctuation frequency time series", "Validation through multiple analysis segments"],
  "notes": "Both series must be analyzed for their short-term fluctuations independently before comparison."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=3948 completion=305 latency=11.94s

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
{"scale":"short","objective":"Identify and quantify short-term variations for Time Series 1.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["reliability of measurements over different segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires comparing the fluctuation frequency between two time series. This involves analyzing the short-term variability within each time series.","task_summary":"Determine which time series exhibits higher fluctuation frequency.","target_output":"A) Time Series 2 | B) Time Series 1","answer_type":"choice","capability":"time_series_analysis","scope":"overall","univariate":false,"homo_assignments":[{"scale":"short","objective":"Identify and quantify short-term variations for Time Series 1.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["reliability of measurements over different segments"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}],"scales":["short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Identification of higher fluctuation frequency time series","Validation through multiple analysis segments"],"notes":"Both series must be analyzed for their short-term fluctuations independently before comparison."}
</plan_context>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify and quantify short-term variations for Time Series 1, focusing on measuring variability and fluctuation frequency. Validation will ensure reliability over different segments.",
  "evidence_plan": {
    "objective": "Identify and quantify short-term variations for Time Series 1.",
    "claims_to_support": [
      {"claim": "Time Series 1 exhibits short-term variability.", "required_evidence": ["rolling level variation"]},
      {"claim": "Fluctuation frequency in Time Series 1 is quantified.", "required_evidence": ["sign changes", "local peaks/troughs"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["reliability of measurements over different segments"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "sliding_stats", "reason": "Measures local volatility which indicates short-term variability.", "supports_evidence": ["rolling level variation"]},
      {"tool": "diff_stats", "reason": "Counts direction switches, reflecting fluctuation frequency.", "supports_evidence": ["sign changes"]},
      {"tool": "local_extrema", "reason": "Counts local peaks and troughs, useful for quantifying fluctuation frequency.", "supports_evidence": ["local peaks/troughs"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=799 completion=200 latency=7.12s

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
{"evidence_plan":{"objective":"Identify and quantify short-term variations for Time Series 1.","claims_to_support":[{"claim":"Time Series 1 exhibits short-term variability.","required_evidence":["rolling level variation"]},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","required_evidence":["sign changes","local peaks/troughs"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["reliability of measurements over different segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability.","supports_evidence":["rolling level variation"]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency.","supports_evidence":["sign changes"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency.","supports_evidence":["local peaks/troughs"]}],"no_tool_decision":null},"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1, focusing on measuring variability and fluctuation frequency. Validation will ensure reliability over different segments."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- sliding_stats
  inputs: series_index, start, end, window
  outputs: series
- diff_stats
  inputs: series_index, start, end
  outputs: series
- local_extrema
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency.",
  "workflow": [
    {
      "step": 1,
      "tool": "sliding_stats",
      "output_key": "local_volatility",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "diff_stats",
      "output_key": "direction_switches",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "local_extrema",
      "output_key": "peaks_troughs",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=972 completion=195 latency=6.98s

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
{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"direction_switches","input_binding":{}},{"step":3,"tool":"local_extrema","output_key":"peaks_troughs","input_binding":{}}],"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency."}
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
- diff_stats: First-difference stats and sign changes.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series first-difference mean/std/range and sign changes}
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify and quantify short-term variations for Time Series 1.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["reliability of measurements over different segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency.",
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
      "tool": "diff_stats",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 3,
      "tool": "local_extrema",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1594 completion=484 latency=17.38s

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
{"evidence_plan":{"objective":"Identify and quantify short-term variations for Time Series 1.","claims_to_support":[{"claim":"Time Series 1 exhibits short-term variability.","required_evidence":["rolling level variation"]},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","required_evidence":["sign changes","local peaks/troughs"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["reliability of measurements over different segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability.","supports_evidence":["rolling level variation"]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency.","supports_evidence":["sign changes"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency.","supports_evidence":["local peaks/troughs"]}],"no_tool_decision":null},"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1, focusing on measuring variability and fluctuation frequency. Validation will ensure reliability over different segments."}
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
      "window": 33,
      "mean_of_means": 57.96657859848485,
      "mean_of_stds": 24.739130624946558,
      "max_local_std": 39.896333489373646
    },
    "error": null,
    "args_fingerprint": "5d90c6e3697596cfb881b17b747f76e320a9ebe9"
  },
  {
    "call_id": "short:step2",
    "step": 2,
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
      "mean_diff": -0.09272727272727278,
      "std_diff": 12.608633105003435,
      "max_abs_diff": 65.99,
      "n_sign_changes": 198
    },
    "error": null,
    "args_fingerprint": "4a37b60672ab33aaec2956de8706ddd2e6292caf"
  },
  {
    "call_id": "short:step3",
    "step": 3,
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
      "n_peaks": 84,
      "n_troughs": 83,
      "peak_idx": [
        3,
        6,
        8,
        14,
        20,
        23,
        26,
        29,
        32,
        36,
        48,
        59,
        67,
        70,
        77,
        86,
        106,
        121,
        126,
        133
      ],
      "trough_idx": [
        5,
        7,
        12,
        16,
        21,
        25,
        28,
        31,
        34,
        41,
        57,
        62,
        69,
        74,
        81,
        90,
        115,
        124,
        130,
        140
      ]
    },
    "error": null,
    "args_fingerprint": "31139f7e956301f570b30f3a308473f914523713"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify and quantify short-term variations for Time Series 1.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["reliability of measurements over different segments"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective was to identify and quantify short-term variations for Time Series 1. Sliding window statistics reveal local volatility, indicating short-term variability through the maximum standard deviation. The number of sign changes and local extrema provide measures of fluctuation frequency.",
  "scale": "short",
  "observations": [
    "Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89.",
    "The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."
  ],
  "evidence_intervals": [
    "The entire series was analyzed without specific focus intervals."
  ],
  "confidence": 0.95,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Time Series 1 exhibits short-term variability.",
      "evidence": [
        {
          "type": "rolling_level_variation",
          "value": 39.896333489373646,
          "source_tool": "sliding_stats",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "rolling_level_variation"
    },
    {
      "claim": "Fluctuation frequency in Time Series 1 is quantified.",
      "evidence": [
        {
          "type": "sign_changes",
          "value": 198,
          "source_tool": "diff_stats",
          "call_id": "short:step2",
          "provenance": "tool"
        },
        {
          "type": "local_peaks_troughs",
          "value": 167,
          "source_tool": "local_extrema",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "fluctuation_frequency"
    }
  ],
  "coverage": {
    "rolling_level_variation": "tool_supported",
    "sign_changes": "tool_supported",
    "local_peaks_troughs": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=6483 completion=397 latency=16.49s

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
{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires comparing the fluctuation frequency between two time series. This involves analyzing the short-term variability within each time series.","task_summary":"Determine which time series exhibits higher fluctuation frequency.","target_output":"A) Time Series 2 | B) Time Series 1","answer_type":"choice","capability":"time_series_analysis","scope":"overall","univariate":false,"homo_assignments":[{"scale":"short","objective":"Identify and quantify short-term variations for Time Series 1.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["reliability of measurements over different segments"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}],"scales":["short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Identification of higher fluctuation frequency time series","Validation through multiple analysis segments"],"notes":"Both series must be analyzed for their short-term fluctuations independently before comparison."}
</plan_context>

<task_summary>
Determine which time series exhibits higher fluctuation frequency.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The objective was to identify and quantify short-term variations for Time Series 1. Sliding window statistics reveal local volatility, indicating short-term variability through the maximum standard deviation. The number of sign changes and local extrema provide measures of fluctuation frequency.","scale":"short","observations":["Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89.","The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."],"evidence_intervals":["The entire series was analyzed without specific focus intervals."],"confidence":0.95,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 33, \"mean_of_means\": 57.96657859848485, \"mean_of_stds\": 24.739130624946558, \"max_local_std\": 39.896333489373646}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.09272727272727278, \"std_diff\": 12.608633105003435, \"max_abs_diff\": 65.99, \"n_sign_changes\": 198}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 84, \"n_troughs\": 83, \"peak_idx\": [3, 6, 8, 14, 20, 23, 26, 29, 32, 36, 48, 59, 67, 70, 77, 86, 106, 121, 126, 133], \"trough_idx\": [5, 7, 12, 16, 21, 25, 28, 31, 34, 41, 57, 62, 69, 74, 81, 90, 115, 124, 130, 140]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}"],"evidence_plan":{"objective":"Identify and quantify short-term variations for Time Series 1.","claims_to_support":[{"claim":"Time Series 1 exhibits short-term variability.","required_evidence":["rolling level variation"]},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","required_evidence":["sign changes","local peaks/troughs"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["reliability of measurements over different segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability.","supports_evidence":["rolling level variation"]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency.","supports_evidence":["sign changes"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency.","supports_evidence":["local peaks/troughs"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"direction_switches","input_binding":{}},{"step":3,"tool":"local_extrema","output_key":"peaks_troughs","input_binding":{}}],"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency."},"structured_observations":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}],"coverage":{"rolling_level_variation":"tool_supported","sign_changes":"tool_supported","local_peaks_troughs":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":33,"mean_of_means":57.96657859848485,"mean_of_stds":24.739130624946558,"max_local_std":39.896333489373646},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.09272727272727278,"std_diff":12.608633105003435,"max_abs_diff":65.99,"n_sign_changes":198},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":84,"n_troughs":83,"peak_idx":[3,6,8,14,20,23,26,29,32,36,48,59,67,70,77,86,106,121,126,133],"trough_idx":[5,7,12,16,21,25,28,31,34,41,57,62,69,74,81,90,115,124,130,140]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89. The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected.","structured_by_scale":{"short":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides short-term fluctuation frequency and variability analysis for Time Series 1. To compare with Time Series 2 and ensure reliable cross-validation, similar analyses should be conducted for Time Series 2.",
  "evidence_plan": {
    "objective": "Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.",
    "claims_to_support": [
      {
        "claim": "Time Series 1 exhibits higher fluctuation frequency compared to Time Series 2",
        "required_evidence": ["variability", "fluctuation_frequency"]
      },
      {
        "claim": "Time Series 2 exhibits higher fluctuation frequency compared to Time Series 1",
        "required_evidence": ["variability", "fluctuation_frequency"]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2],
      "role": "reasoning"
    },
    "validation_needs": ["cross-validation of findings by multiple short-term analysis"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "sliding_stats",
        "arguments": {
          "series_index": 2
        },
        "reason": "Measures local volatility which indicates short-term variability for Time Series 2."
      },
      {
        "tool": "diff_stats",
        "arguments": {
          "series_index": 2
        },
        "reason": "Counts direction switches, reflecting fluctuation frequency for Time Series 2."
      },
      {
        "tool": "local_extrema",
        "arguments": {
          "series_index": 2
        },
        "reason": "Counts local peaks and troughs, useful for quantifying fluctuation frequency for Time Series 2."
      }
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s3) — `heterogeneous:reasoning:s3:m0`

tokens prompt=694 completion=464 latency=16.32s

### INPUT (system)

```
You are a Heterogeneous Agent (role=reasoning) at Stage 3: Tool Workflow Planning.
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
{"evidence_plan":{"objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","claims_to_support":[{"claim":"Time Series 1 exhibits higher fluctuation frequency compared to Time Series 2","required_evidence":["variability","fluctuation_frequency"]},{"claim":"Time Series 2 exhibits higher fluctuation frequency compared to Time Series 1","required_evidence":["variability","fluctuation_frequency"]}],"analysis_scope":{"target_series":[1,2],"role":"reasoning"},"validation_needs":["cross-validation of findings by multiple short-term analysis"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability for Time Series 2.","supports_evidence":[]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency for Time Series 2.","supports_evidence":[]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency for Time Series 2.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides short-term fluctuation frequency and variability analysis for Time Series 1. To compare with Time Series 2 and ensure reliable cross-validation, similar analyses should be conducted for Time Series 2."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- sliding_stats
  inputs: series_index, start, end, window
  outputs: series
- diff_stats
  inputs: series_index, start, end
  outputs: series
- local_extrema
  inputs: series_index, start, end
  outputs: series
</io_concepts>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "To meet the objective of comparing the short-term fluctuation frequency between Time Series 1 and Time Series 2, we need to analyze both series for their variability and fluctuation frequency. This involves executing tools like 'sliding_stats', 'diff_stats', and 'local_extrema' on both series, followed by a comparison step that evaluates the results to determine which series exhibits higher fluctuation frequency.",
  "workflow": [
    {
      "step": 1,
      "tool": "sliding_stats",
      "output_key": "ts1_volatility",
      "input_binding": {"series_index": 1}
    },
    {
      "step": 2,
      "tool": "sliding_stats",
      "output_key": "ts2_volatility",
      "input_binding": {"series_index": 2}
    },
    {
      "step": 3,
      "tool": "diff_stats",
      "output_key": "ts1_fluctuations",
      "input_binding": {"series_index": 1}
    },
    {
      "step": 4,
      "tool": "diff_stats",
      "output_key": "ts2_fluctuations",
      "input_binding": {"series_index": 2}
    },
    {
      "step": 5,
      "tool": "local_extrema",
      "output_key": "ts1_extremes",
      "input_binding": {"series_index": 1}
    },
    {
      "step": 6,
      "tool": "local_extrema",
      "output_key": "ts2_extremes",
      "input_binding": {"series_index": 2}
    },
    {
      "step": 7,
      "tool": "cross_series_compare",
      "output_key": "pair_compare",
      "input_binding": {
        "series_index_1": "$step5.series_index",
        "series_index_2": "$step6.series_index",
        "comparison_stat": ["ts1_volatility", "ts2_volatility", "ts1_fluctuations", "ts2_fluctuations", "ts1_extremes", "ts2_extremes"]
      }
    }
  ]
}
```

## Heterogeneous (reasoning, s4) — `heterogeneous:reasoning:s4:m0`

tokens prompt=1121 completion=190 latency=6.85s

### INPUT (system)

```
You are a Heterogeneous Agent (role=reasoning) at Stage 4: Tool Invocation.
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
{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"ts1_volatility","input_binding":{"series_index":1}},{"step":2,"tool":"sliding_stats","output_key":"ts2_volatility","input_binding":{"series_index":2}},{"step":3,"tool":"diff_stats","output_key":"ts1_fluctuations","input_binding":{"series_index":1}},{"step":4,"tool":"diff_stats","output_key":"ts2_fluctuations","input_binding":{"series_index":2}},{"step":5,"tool":"local_extrema","output_key":"ts1_extremes","input_binding":{"series_index":1}},{"step":6,"tool":"local_extrema","output_key":"ts2_extremes","input_binding":{"series_index":2}},{"step":7,"tool":"cross_series_compare","output_key":"pair_compare","input_binding":{"series_index_1":"$step5.series_index","series_index_2":"$step6.series_index","comparison_stat":["ts1_volatility","ts2_volatility","ts1_fluctuations","ts2_fluctuations","ts1_extremes","ts2_extremes"]}}],"reasoning":"To meet the objective of comparing the short-term fluctuation frequency between Time Series 1 and Time Series 2, we need to analyze both series for their variability and fluctuation frequency. This involves executing tools like 'sliding_stats', 'diff_stats', and 'local_extrema' on both series, followed by a comparison step that evaluates the results to determine which series exhibits higher fluctuation frequency."}
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
- diff_stats: First-difference stats and sign changes.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series first-difference mean/std/range and sign changes}
- local_extrema: Count local peaks and troughs (global indices). Do NOT use for step/plateau level counting—use step_levels instead.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=per-series peak/trough counts and indices}
</tool_invocation_spec>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>

<assignment>
{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}
</assignment>



Produce the InvocationPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The objective requires a comparative analysis of short-term fluctuation frequency between Time Series 1 and Time Series 2. To achieve this, we first calculate the variability and fluctuations of each time series through sliding window statistics and difference statistics. Subsequently, we identify local extrema points to represent potential extreme fluctuations. Finally, these measures are compared between the two time series to assess which has a higher fluctuation frequency.",
  "calls": [
    {
      "step": 1,
      "tool": "cross_series_compare",
      "args": {
        "series_index_1": 1,
        "series_index_2": 2,
        "comparison_stat": ["ts1_volatility", "ts2_volatility", "ts1_fluctuations", "ts2_fluctuations", "ts1_extremes", "ts2_extremes"]
      }
    }
  ]
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=6143 completion=573 latency=22.99s

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
{"evidence_plan":{"objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","claims_to_support":[{"claim":"Time Series 1 exhibits higher fluctuation frequency compared to Time Series 2","required_evidence":["variability","fluctuation_frequency"]},{"claim":"Time Series 2 exhibits higher fluctuation frequency compared to Time Series 1","required_evidence":["variability","fluctuation_frequency"]}],"analysis_scope":{"target_series":[1,2],"role":"reasoning"},"validation_needs":["cross-validation of findings by multiple short-term analysis"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability for Time Series 2.","supports_evidence":[]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency for Time Series 2.","supports_evidence":[]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency for Time Series 2.","supports_evidence":[]}],"no_tool_decision":null},"reasoning":"The current evidence provides short-term fluctuation frequency and variability analysis for Time Series 1. To compare with Time Series 2 and ensure reliable cross-validation, similar analyses should be conducted for Time Series 2."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "reasoning:step1",
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
      "window": 33,
      "mean_of_means": 57.96657859848485,
      "mean_of_stds": 24.739130624946558,
      "max_local_std": 39.896333489373646
    },
    "error": null,
    "args_fingerprint": "5d90c6e3697596cfb881b17b747f76e320a9ebe9"
  },
  {
    "call_id": "reasoning:step2",
    "step": 2,
    "tool_name": "sliding_stats",
    "arguments": {
      "series_index": 2
    },
    "resolved_arguments": {
      "series_index": 2
    },
    "success": true,
    "data": {
      "series_index": 2,
      "window": 33,
      "mean_of_means": 262.38597253787873,
      "mean_of_stds": 2.125438171552925,
      "max_local_std": 5.134493643685143
    },
    "error": null,
    "args_fingerprint": "31c9d715cc0c5b26bd4ec2f09687ec21663b9162"
  },
  {
    "call_id": "reasoning:step3",
    "step": 3,
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
      "mean_diff": -0.09272727272727278,
      "std_diff": 12.608633105003435,
      "max_abs_diff": 65.99,
      "n_sign_changes": 198
    },
    "error": null,
    "args_fingerprint": "4a37b60672ab33aaec2956de8706ddd2e6292caf"
  },
  {
    "call_id": "reasoning:step4",
    "step": 4,
    "tool_name": "diff_stats",
    "arguments": {
      "series_index": 2
    },
    "resolved_arguments": {
      "series_index": 2
    },
    "success": true,
    "data": {
      "series_index": 2,
      "start": null,
      "end": null,
      "mean_diff": -0.006572280178837593,
      "std_diff": 0.5408624732492695,
      "max_abs_diff": 2.3000000000000114,
      "n_sign_changes": 163
    },
    "error": null,
    "args_fingerprint": "92eda19bb497ae63ef3fc658bee02a63371cf7b9"
  },
  {
    "call_id": "reasoning:step5",
    "step": 5,
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
      "n_peaks": 84,
      "n_troughs": 83,
      "peak_idx": [
        3,
        6,
        8,
        14,
        20,
        23,
        26,
        29,
        32,
        36,
        48,
        59,
        67,
        70,
        77,
        86,
        106,
        121,
        126,
        133
      ],
      "trough_idx": [
        5,
        7,
        12,
        16,
        21,
        25,
        28,
        31,
        34,
        41,
        57,
        62,
        69,
        74,
        81,
        90,
        115,
        124,
        130,
        140
      ]
    },
    "error": null,
    "args_fingerprint": "31139f7e956301f570b30f3a308473f914523713"
  },
  {
    "call_id": "reasoning:step6",
    "step": 6,
    "tool_name": "local_extrema",
    "arguments": {
      "series_index": 2
    },
    "resolved_arguments": {
      "series_index": 2
    },
    "success": true,
    "data": {
      "series_index": 2,
      "start": null,
      "end": null,
      "n_peaks": 51,
      "n_troughs": 51,
      "peak_idx": [
        4,
        34,
        51,
        63,
        78,
        91,
        117,
        139,
        153,
        162,
        186,
        215,
        225,
        236,
        259,
        271,
        285,
        295,
        304,
        310
      ],
      "trough_idx": [
        33,
        36,
        59,
        65,
        87,
        110,
        126,
        146,
        154,
        183,
        201,
        224,
        234,
        241,
        268,
        274,
        288,
        297,
        308,
        312
      ]
    },
    "error": null,
    "args_fingerprint": "c0e51af4253c9f0b6a3000ba600a19894ceb74e8"
  },
  {
    "call_id": "reasoning:step7",
    "step": 7,
    "tool_name": "cross_series_compare",
    "arguments": {
      "series_index_1": 1,
      "series_index_2": 2,
      "comparison_stat": [
        "ts1_volatility",
        "ts2_volatility",
        "ts1_fluctuations",
        "ts2_fluctuations",
        "ts1_extremes",
        "ts2_extremes"
      ]
    },
    "resolved_arguments": {
      "series_index_1": 1,
      "series_index_2": 2,
      "comparison_stat": [
        "ts1_volatility",
        "ts2_volatility",
        "ts1_fluctuations",
        "ts2_fluctuations",
        "ts1_extremes",
        "ts2_extremes"
      ]
    },
    "success": true,
    "data": {
      "series_index_1": 1,
      "series_index_2": 2,
      "interval_1": [
        0,
        671
      ],
      "interval_2": [
        0,
        671
      ],
      "series_1": {
        "mean": 58.505758928571424,
        "std": 29.202875806612067,
        "min": 0.63,
        "max": 103.42,
        "min_index": 299,
        "max_index": 575,
        "n_peaks": 84,
        "n_troughs": 83,
        "peak_indices": [
          3,
          6,
          8,
          14,
          20,
          23,
          26,
          29,
          32,
          36,
          48,
          59,
          67,
          70,
          77,
          86,
          106,
          121,
          126,
          133
        ],
        "trough_indices": [
          5,
          7,
          12,
          16,
          21,
          25,
          28,
          31,
          34,
          41,
          57,
          62,
          69,
          74,
          81,
          90,
          115,
          124,
          130,
          140
        ],
        "slope": -0.09272727272727273,
        "direction": "downward"
      },
      "series_2": {
        "mean": 262.4005357142857,
        "std": 4.122507365052847,
        "min": 252.15,
        "max": 271.3,
        "min_index": 635,
        "max_index": 433,
        "n_peaks": 51,
        "n_troughs": 51,
        "peak_indices": [
          4,
          34,
          51,
          63,
          78,
          91,
          117,
          139,
          153,
          162,
          186,
          215,
          225,
          236,
          259,
          271,
          285,
          295,
          304,
          310
        ],
        "trough_indices": [
          33,
          36,
          59,
          65,
          87,
          110,
          126,
          146,
          154,
          183,
          201,
          224,
          234,
          241,
          268,
          274,
          288,
          297,
          308,
          312
        ],
        "slope": -0.006572280178837593,
        "direction": "downward"
      },
      "same_trend_direction": true,
      "mean_delta": 203.89477678571427,
      "max_delta": 167.88,
      "euclidean_distance": 35.96180955767206,
      "corr": 0.0377591170667606,
      "corr_error": null
    },
    "error": null,
    "args_fingerprint": "68911cf068aca275d5261226611e5df21a8bab98"
  }
]
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The objective was to identify and quantify short-term variations for Time Series 1. Sliding window statistics reveal local volatility, indicating short-term variability through the maximum standard deviation. The number of sign changes and local extrema provide measures of fluctuation frequency.","scale":"short","observations":["Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89.","The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."],"evidence_intervals":["The entire series was analyzed without specific focus intervals."],"confidence":0.95,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 33, \"mean_of_means\": 57.96657859848485, \"mean_of_stds\": 24.739130624946558, \"max_local_std\": 39.896333489373646}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.09272727272727278, \"std_diff\": 12.608633105003435, \"max_abs_diff\": 65.99, \"n_sign_changes\": 198}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 84, \"n_troughs\": 83, \"peak_idx\": [3, 6, 8, 14, 20, 23, 26, 29, 32, 36, 48, 59, 67, 70, 77, 86, 106, 121, 126, 133], \"trough_idx\": [5, 7, 12, 16, 21, 25, 28, 31, 34, 41, 57, 62, 69, 74, 81, 90, 115, 124, 130, 140]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}"],"evidence_plan":{"objective":"Identify and quantify short-term variations for Time Series 1.","claims_to_support":[{"claim":"Time Series 1 exhibits short-term variability.","required_evidence":["rolling level variation"]},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","required_evidence":["sign changes","local peaks/troughs"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["reliability of measurements over different segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability.","supports_evidence":["rolling level variation"]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency.","supports_evidence":["sign changes"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency.","supports_evidence":["local peaks/troughs"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"direction_switches","input_binding":{}},{"step":3,"tool":"local_extrema","output_key":"peaks_troughs","input_binding":{}}],"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency."},"structured_observations":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}],"coverage":{"rolling_level_variation":"tool_supported","sign_changes":"tool_supported","local_peaks_troughs":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":33,"mean_of_means":57.96657859848485,"mean_of_stds":24.739130624946558,"max_local_std":39.896333489373646},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.09272727272727278,"std_diff":12.608633105003435,"max_abs_diff":65.99,"n_sign_changes":198},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":84,"n_troughs":83,"peak_idx":[3,6,8,14,20,23,26,29,32,36,48,59,67,70,77,86,106,121,126,133],"trough_idx":[5,7,12,16,21,25,28,31,34,41,57,62,69,74,81,90,115,124,130,140]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89. The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected.","structured_by_scale":{"short":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Both time series were evaluated using multiple measures of short-term variability and fluctuation frequency. Time Series 1 displays higher local volatility and more frequent directional changes compared to Time Series 2.",
  "hypothesis": "Time Series 1 has a higher fluctuation frequency than Time Series 2.",
  "evidence": [
    "Time Series 1's local volatility, as measured by its highest standard deviation within any window, is much larger (39.896) than that of Time Series 2 (5.134), indicating greater short-term variability.",
    "Time Series 1 experiences significantly more sign changes (198) relative to Time Series 2 (163), pointing towards a higher fluctuation frequency."
  ],
  "candidate_preference": "A",
  "confidence": 0.95,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "reasoning:step1",
    "reasoning:step2",
    "reasoning:step3",
    "reasoning:step4"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 1 has higher local volatility compared to Time Series 2.",
      "evidence": [
        {
          "type": "rolling_level_variation",
          "value": 39.896333489373646,
          "provenance": "tool",
          "ref": null,
          "call_id": "reasoning:step1"
        },
        {
          "type": "rolling_level_variation",
          "value": 5.134493643685143,
          "provenance": "tool",
          "ref": null,
          "call_id": "reasoning:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Time Series 1 has a higher fluctuation frequency compared to Time Series 2.",
      "evidence": [
        {
          "type": "sign_changes",
          "value": 198,
          "provenance": "tool",
          "ref": null,
          "call_id": "reasoning:step3"
        },
        {
          "type": "sign_changes",
          "value": 163,
          "provenance": "tool",
          "ref": null,
          "call_id": "reasoning:step4"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {},
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m1`

tokens prompt=6494 completion=300 latency=12.81s

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
{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires comparing the fluctuation frequency between two time series. This involves analyzing the short-term variability within each time series.","task_summary":"Determine which time series exhibits higher fluctuation frequency.","target_output":"A) Time Series 2 | B) Time Series 1","answer_type":"choice","capability":"time_series_analysis","scope":"overall","univariate":false,"homo_assignments":[{"scale":"short","objective":"Identify and quantify short-term variations for Time Series 1.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["reliability of measurements over different segments"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}],"scales":["short"],"heterogeneous_agents":["reasoning"],"success_criteria":["Identification of higher fluctuation frequency time series","Validation through multiple analysis segments"],"notes":"Both series must be analyzed for their short-term fluctuations independently before comparison."}
</plan_context>

<task_summary>
Determine which time series exhibits higher fluctuation frequency.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The objective was to identify and quantify short-term variations for Time Series 1. Sliding window statistics reveal local volatility, indicating short-term variability through the maximum standard deviation. The number of sign changes and local extrema provide measures of fluctuation frequency.","scale":"short","observations":["Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89.","The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."],"evidence_intervals":["The entire series was analyzed without specific focus intervals."],"confidence":0.95,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 33, \"mean_of_means\": 57.96657859848485, \"mean_of_stds\": 24.739130624946558, \"max_local_std\": 39.896333489373646}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.09272727272727278, \"std_diff\": 12.608633105003435, \"max_abs_diff\": 65.99, \"n_sign_changes\": 198}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 84, \"n_troughs\": 83, \"peak_idx\": [3, 6, 8, 14, 20, 23, 26, 29, 32, 36, 48, 59, 67, 70, 77, 86, 106, 121, 126, 133], \"trough_idx\": [5, 7, 12, 16, 21, 25, 28, 31, 34, 41, 57, 62, 69, 74, 81, 90, 115, 124, 130, 140]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}"],"evidence_plan":{"objective":"Identify and quantify short-term variations for Time Series 1.","claims_to_support":[{"claim":"Time Series 1 exhibits short-term variability.","required_evidence":["rolling level variation"]},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","required_evidence":["sign changes","local peaks/troughs"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["reliability of measurements over different segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability.","supports_evidence":["rolling level variation"]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency.","supports_evidence":["sign changes"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency.","supports_evidence":["local peaks/troughs"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"direction_switches","input_binding":{}},{"step":3,"tool":"local_extrema","output_key":"peaks_troughs","input_binding":{}}],"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency."},"structured_observations":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}],"coverage":{"rolling_level_variation":"tool_supported","sign_changes":"tool_supported","local_peaks_troughs":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":33,"mean_of_means":57.96657859848485,"mean_of_stds":24.739130624946558,"max_local_std":39.896333489373646},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.09272727272727278,"std_diff":12.608633105003435,"max_abs_diff":65.99,"n_sign_changes":198},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":84,"n_troughs":83,"peak_idx":[3,6,8,14,20,23,26,29,32,36,48,59,67,70,77,86,106,121,126,133],"trough_idx":[5,7,12,16,21,25,28,31,34,41,57,62,69,74,81,90,115,124,130,140]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89. The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected.","structured_by_scale":{"short":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
retry_context=unresolved_claims=['parse_failure']
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current evidence provides short-term fluctuation frequency and variability analysis for Time Series 1. To compare with Time Series 2 and ensure reliable cross-validation, similar analyses should be conducted for Time Series 2.",
  "evidence_plan": {
    "objective": "Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.",
    "claims_to_support": [
      {
        "claim": "Time Series 1 exhibits higher fluctuation frequency compared to Time Series 2",
        "required_evidence": [
          "sign_changes",
          "local_extrema",
          "max_local_std"
        ]
      },
      {
        "claim": "Time Series 2 exhibits higher fluctuation frequency compared to Time Series 1",
        "required_evidence": [
          "sign_changes",
          "local_extrema",
          "max_local_std"
        ]
      }
    ],
    "analysis_scope": {
      "target_series": [1, 2],
      "focus_intervals": []
    },
    "validation_needs": [
      "Cross-validation of findings by multiple short-term analysis",
      "Ensuring consistency across different segments for reliability"
    ]
  },
  "capability_selection": {
    "selected_tools": [
      "sliding_stats",
      "diff_stats",
      "local_extrema"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m1`

tokens prompt=3080 completion=424 latency=16.01s

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
{"evidence_plan":{"objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The objective was to identify and quantify short-term variations for Time Series 1. Sliding window statistics reveal local volatility, indicating short-term variability through the maximum standard deviation. The number of sign changes and local extrema provide measures of fluctuation frequency.","scale":"short","observations":["Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89.","The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."],"evidence_intervals":["The entire series was analyzed without specific focus intervals."],"confidence":0.95,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 33, \"mean_of_means\": 57.96657859848485, \"mean_of_stds\": 24.739130624946558, \"max_local_std\": 39.896333489373646}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.09272727272727278, \"std_diff\": 12.608633105003435, \"max_abs_diff\": 65.99, \"n_sign_changes\": 198}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 84, \"n_troughs\": 83, \"peak_idx\": [3, 6, 8, 14, 20, 23, 26, 29, 32, 36, 48, 59, 67, 70, 77, 86, 106, 121, 126, 133], \"trough_idx\": [5, 7, 12, 16, 21, 25, 28, 31, 34, 41, 57, 62, 69, 74, 81, 90, 115, 124, 130, 140]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}"],"evidence_plan":{"objective":"Identify and quantify short-term variations for Time Series 1.","claims_to_support":[{"claim":"Time Series 1 exhibits short-term variability.","required_evidence":["rolling level variation"]},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","required_evidence":["sign changes","local peaks/troughs"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["reliability of measurements over different segments"]},"capability_selection":{"selected_tools":[{"tool":"sliding_stats","reason":"Measures local volatility which indicates short-term variability.","supports_evidence":["rolling level variation"]},{"tool":"diff_stats","reason":"Counts direction switches, reflecting fluctuation frequency.","supports_evidence":["sign changes"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs, useful for quantifying fluctuation frequency.","supports_evidence":["local peaks/troughs"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"sliding_stats","output_key":"local_volatility","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"direction_switches","input_binding":{}},{"step":3,"tool":"local_extrema","output_key":"peaks_troughs","input_binding":{}}],"reasoning":"The objective is to identify and quantify short-term variations for Time Series 1 by measuring local volatility and counting sign changes and local peaks/troughs. The sliding_stats tool measures local volatility which indicates short-term variability. The diff_stats tool counts direction switches, reflecting fluctuation frequency. The local_extrema tool counts local peaks and troughs, further quantifying fluctuation frequency."},"structured_observations":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}],"coverage":{"rolling_level_variation":"tool_supported","sign_changes":"tool_supported","local_peaks_troughs":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":33,"mean_of_means":57.96657859848485,"mean_of_stds":24.739130624946558,"max_local_std":39.896333489373646},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.09272727272727278,"std_diff":12.608633105003435,"max_abs_diff":65.99,"n_sign_changes":198},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":84,"n_troughs":83,"peak_idx":[3,6,8,14,20,23,26,29,32,36,48,59,67,70,77,86,106,121,126,133],"trough_idx":[5,7,12,16,21,25,28,31,34,41,57,62,69,74,81,90,115,124,130,140]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"}],"skipped_stages":[]},"medium":null,"long":null,"conflicts":[],"summary":"Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89. The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected.","structured_by_scale":{"short":[{"claim":"Time Series 1 exhibits short-term variability.","evidence":[{"type":"rolling_level_variation","value":39.896333489373646,"source_tool":"sliding_stats","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"rolling_level_variation"},{"claim":"Fluctuation frequency in Time Series 1 is quantified.","evidence":[{"type":"sign_changes","value":198,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"local_peaks_troughs","value":167,"source_tool":"local_extrema","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"fluctuation_frequency"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.","required_measurements":["variability","fluctuation_frequency"],"validation_requirements":["cross-validation of findings by multiple short-term analysis"],"target_series":[1,2],"focus_intervals":[]}
</assignment>

<metadata>
subset=InWild; local_overall=overall; task_type=['basic analysis']; domain=climate; qa_type=a binary question; question_type=choice; is_univariate=False; n_series=2; series_lengths=[672, 672]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[1, 2]; align_direction=None; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "While the detailed metrics for Time Series 1 are available, there is no corresponding data provided for Time Series 2. Therefore, it's not possible to directly compare the fluctuation frequencies between the two time series.",
  "role": "reasoning",
  "hypothesis": "It is impossible to definitively determine which time series shows higher fluctuation without the necessary data for Time Series 2.",
  "evidence": [
    "Time Series 1 shows a significant amount of short-term fluctuation as evidenced by a high max_local_std value and a substantial number of sign changes."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "short:step3"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Time Series 1 exhibits significant short-term fluctuation.",
      "evidence": [
        {
          "type": "rolling_level_variation",
          "value": 39.896333489373646,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        },
        {
          "type": "sign_changes",
          "value": 198,
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "rolling_level_variation": "tool_supported",
    "sign_changes": "tool_supported",
    "local_peaks_troughs": "tool_supported"
  },
  "unresolved_claims": [
    "There is no evidence provided for Time Series 2 to make a valid comparison."
  ]
}
```

## Integration — `integration`

tokens prompt=1252 completion=294 latency=10.54s

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
According to time series data analysis, which one has a higher fluctuation frequency, Time Series 1 or Time Series 2?
</question>

<candidates>
A) Time Series 2
B) Time Series 1
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Determine which time series exhibits higher fluctuation frequency.",
  "question_type": "choice",
  "required_output": "A) Time Series 2 | B) Time Series 1",
  "success_criteria": [
    "Identification of higher fluctuation frequency time series",
    "Validation through multiple analysis segments"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Identify and quantify short-term variations for Time Series 1.",
      "required_measurements": [
        "variability",
        "fluctuation_frequency"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Compare the short-term fluctuation frequency of Time Series 1 and Time Series 2, determine which series shows higher fluctuation.",
      "required_measurements": [
        "variability",
        "fluctuation_frequency"
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
          "type": "rolling_level_variation",
          "value": 39.896333489373646,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "sign_changes",
          "value": 198,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "local_peaks_troughs",
          "value": 167,
          "trusted": true
        }
      ],
      "coverage": {
        "rolling_level_variation": "tool_supported",
        "sign_changes": "tool_supported",
        "local_peaks_troughs": "tool_supported"
      },
      "summary": "Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89. | The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."
    }
  },
  "conflicts": [],
  "summary": "Time Series 1 exhibits short-term variability as indicated by a high max_local_std value of 39.89. The fluctuation frequency in Time Series 1 has been quantified with 198 sign changes detected."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
      "hypothesis": "It is impossible to definitively determine which time series shows higher fluctuation without the necessary data for Time Series 2.",
      "reasoning_chain": [
        "Time Series 1 exhibits significant short-term fluctuation.",
        "rolling_level_variation=39.896333489373646",
        "sign_changes=198"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "rolling_level_variation",
        "sign_changes"
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
  "reasoning": "Heter reasoning indicates that it's impossible to determine which time series has a higher fluctuation frequency without the necessary data for Time Series 2. However, based on the provided data for Time Series 1 alone, it shows significant short-term fluctuation with a rolling_level_variation of 39.896333489373646 and 198 sign changes detected.",
  "answer": "B",
  "explanation": "The perception of Time Series 1 reveals a high level of short-term fluctuation frequency compared to any data provided for Time Series 2, but without direct comparable data for Time Series 2, the reasoning cannot confirm the higher fluctuation frequency conclusively. Therefore, we infer from the available data that Time Series 1 may have a higher fluctuation frequency.",
  "confidence": 0.5,
  "conflicts": ["Lack of Time Series 2 data prevents definitive comparison.", "The hypothesis relies solely on Time Series 1's data which may not fully represent the scenario."],
  "cited_evidence": ["rolling_level_variation", "sign_changes"],
  "decision_trace": {
    "metric": "fluctuation_frequency",
    "observed_value": 198,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "B"
  }
}
```
