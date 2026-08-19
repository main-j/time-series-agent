# Agent IO summary: `Align:ts2caption_qa_120:15`

- Architecture pred: `C` (success=True)
- model_calls=22, tool_calls=12, latency=297.6s

## Planner — `planner`

tokens prompt=1150 completion=577 latency=20.48s

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
A) This series demonstrates a complex multi-phase behavior: initial growth to around 35, followed by decline and stabilization near 15, then dramatic rise to peak values around 50.
B) The data shows consistent cyclical patterns with values fluctuating between 1-10, punctuated by dramatic spikes exceeding 20, suggesting a recurring seasonal or operational pattern.
C) This time series exhibits regular periodic oscillations with occasional sharp spikes, maintaining relatively low baseline values around 2-3 with periodic peaks reaching up to 21.
D) The time series displays high variability with frequent fluctuations between 5-18, including periods of constant values and irregular spikes, suggesting unstable or noisy underlying processes.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.",
  "task_summary": "Select the best description for the provided univariate time series data among four given options.",
  "target_output": "Choose the best description from the candidates.",
  "answer_type": "choice",
  "capability": "hierarchical time-series analysis",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Identify any localized events, abrupt changes, and short-term variations in the series.",
      "required_measurements": ["change_location", "abrupt_changes", "short_term_variations"],
      "validation_requirements": ["Compare findings across different segments of the series to ensure consistency"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "medium",
      "objective": "Detect patterns such as cycles, steps, and repeated regimes within the series.",
      "required_measurements": ["seasonal_period", "regime_changes", "pairwise_similarity"],
      "validation_requirements": ["Cross-validate findings with neighboring segments to ensure robustness"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "long",
      "objective": "Analyze the overall structure, trends, and long-term dependencies of the series.",
      "required_measurements": ["global_trend", "persistence", "long_range_dependence"],
      "validation_requirements": ["Reconcile with observations from medium and short scales for a comprehensive view"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "matching",
      "objective": "Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.",
      "required_measurements": ["change_location", "abrupt_changes", "short_term_variations", "seasonal_period", "regime_changes", "pairwise_similarity", "global_trend", "persistence", "long_range_dependence"],
      "validation_requirements": ["Cross-check with alternative descriptions to confirm the match"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Accurate identification of key features", "Robust alignment with a single descriptive statement", "Consistent validation across scales"],
  "notes": "Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4152 completion=323 latency=12.68s

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
{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.","task_summary":"Select the best description for the provided univariate time series data among four given options.","target_output":"Choose the best description from the candidates.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of key features","Robust alignment with a single descriptive statement","Consistent validation across scales"],"notes":"Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations.",
  "evidence_plan": {
    "objective": "Identify any localized events, abrupt changes, and short-term variations in the series.",
    "claims_to_support": [
      {"claim": "Localized events exist in the series.", "required_evidence": ["change_location"]},
      {"claim": "There are abrupt changes in the series.", "required_evidence": ["abrupt_changes"]},
      {"claim": "Short-term variations are present in the series.", "required_evidence": ["short_term_variations"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "short"},
    "validation_needs": ["Compare findings across different segments of the series to ensure consistency"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "diff_stats", "reason": "Measures first-difference statistics to detect abrupt changes.", "supports_evidence": ["abrupt_changes"]},
      {"tool": "sliding_stats", "reason": "Provides local volatility measurements to understand short-term variations.", "supports_evidence": ["short_term_variations"]},
      {"tool": "local_extrema", "reason": "Counts local peaks and troughs to identify localized events.", "supports_evidence": ["change_location"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=808 completion=212 latency=7.54s

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
{"evidence_plan":{"objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","claims_to_support":[{"claim":"Localized events exist in the series.","required_evidence":["change_location"]},{"claim":"There are abrupt changes in the series.","required_evidence":["abrupt_changes"]},{"claim":"Short-term variations are present in the series.","required_evidence":["short_term_variations"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["Compare findings across different segments of the series to ensure consistency"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Measures first-difference statistics to detect abrupt changes.","supports_evidence":["abrupt_changes"]},{"tool":"sliding_stats","reason":"Provides local volatility measurements to understand short-term variations.","supports_evidence":["short_term_variations"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs to identify localized events.","supports_evidence":["change_location"]}],"no_tool_decision":null},"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations."}
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
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations.",
  "workflow": [
    {
      "step": 1,
      "tool": "local_extrema",
      "output_key": "localized_events",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "diff_stats",
      "output_key": "abrupt_changes",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "sliding_stats",
      "output_key": "short_term_variations",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=990 completion=209 latency=7.47s

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
{"workflow":[{"step":1,"tool":"local_extrema","output_key":"localized_events","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"abrupt_changes","input_binding":{}},{"step":3,"tool":"sliding_stats","output_key":"short_term_variations","input_binding":{}}],"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations."}
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
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations.",
  "calls": [
    {
      "step": 1,
      "tool": "local_extrema",
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
      "tool": "sliding_stats",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=1635 completion=475 latency=17.09s

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
{"evidence_plan":{"objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","claims_to_support":[{"claim":"Localized events exist in the series.","required_evidence":["change_location"]},{"claim":"There are abrupt changes in the series.","required_evidence":["abrupt_changes"]},{"claim":"Short-term variations are present in the series.","required_evidence":["short_term_variations"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["Compare findings across different segments of the series to ensure consistency"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Measures first-difference statistics to detect abrupt changes.","supports_evidence":["abrupt_changes"]},{"tool":"sliding_stats","reason":"Provides local volatility measurements to understand short-term variations.","supports_evidence":["short_term_variations"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs to identify localized events.","supports_evidence":["change_location"]}],"no_tool_decision":null},"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
    "step": 1,
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
      "n_peaks": 20,
      "n_troughs": 20,
      "peak_idx": [
        14,
        24,
        38,
        47,
        52,
        71,
        96,
        111,
        121,
        135,
        144,
        158,
        168,
        183,
        192,
        207,
        216,
        239,
        264,
        286
      ],
      "trough_idx": [
        10,
        17,
        34,
        40,
        51,
        59,
        83,
        106,
        113,
        130,
        137,
        154,
        161,
        178,
        184,
        202,
        208,
        227,
        251,
        274
      ]
    },
    "error": null,
    "args_fingerprint": "31139f7e956301f570b30f3a308473f914523713"
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
      "mean_diff": -0.05623693379790942,
      "std_diff": 2.1971065355442745,
      "max_abs_diff": 15.55,
      "n_sign_changes": 48
    },
    "error": null,
    "args_fingerprint": "4a37b60672ab33aaec2956de8706ddd2e6292caf"
  },
  {
    "call_id": "short:step3",
    "step": 3,
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
      "window": 14,
      "mean_of_means": 2.693153246753247,
      "mean_of_stds": 1.9296070077763567,
      "max_local_std": 6.194638440471185
    },
    "error": null,
    "args_fingerprint": "5d90c6e3697596cfb881b17b747f76e320a9ebe9"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate that localized events, abrupt changes, and short-term variations have been identified through the use of local_extrema, diff_stats, and sliding_stats respectively. The objective of identifying localized events, abrupt changes, and short-term variations is met.",
  "scale": "short",
  "observations": ["20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations."],
  "evidence_intervals": ["full series"],
  "confidence": 1.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Localized events exist in the series.",
      "evidence": [
        {
          "type": "change_location",
          "value": 40,
          "source_tool": "local_extrema",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_location"
    },
    {
      "claim": "There are abrupt changes in the series.",
      "evidence": [
        {
          "type": "abrupt_changes",
          "value": 48,
          "source_tool": "diff_stats",
          "call_id": "short:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "abrupt_changes"
    },
    {
      "claim": "Short-term variations are present in the series.",
      "evidence": [
        {
          "type": "short_term_variations",
          "value": 6.19,
          "source_tool": "sliding_stats",
          "call_id": "short:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "short_term_variations"
    }
  ],
  "coverage": {"change_location": "tool_supported", "abrupt_changes": "tool_supported", "short_term_variations": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4149 completion=329 latency=12.89s

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
{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.","task_summary":"Select the best description for the provided univariate time series data among four given options.","target_output":"Choose the best description from the candidates.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of key features","Robust alignment with a single descriptive statement","Consistent validation across scales"],"notes":"Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective at the medium scale is to detect patterns such as cycles, steps, and repeated regimes within the series. This requires measuring seasonal periods, identifying regime changes, and assessing pairwise similarities between different segments of the series.",
  "evidence_plan": {
    "objective": "Detect patterns such as cycles, steps, and repeated regimes within the series.",
    "claims_to_support": [
      {"claim": "A seasonal period exists in the series.", "required_evidence": ["seasonal_period"]},
      {"claim": "There are regime changes in the series.", "required_evidence": ["regime_changes"]},
      {"claim": "Similarities exist between different segments of the series.", "required_evidence": ["pairwise_similarity"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["Cross-validate findings with neighboring segments to ensure robustness"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "To determine the dominant period indicative of a seasonal cycle.", "supports_evidence": ["seasonal_period"]},
      {"tool": "change_points", "reason": "To identify potential regime shifts in the series.", "supports_evidence": ["regime_changes"]},
      {"tool": "cross_series_compare", "reason": "To compare different segments of the series for pairwise similarity.", "supports_evidence": ["pairwise_similarity"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=850 completion=189 latency=6.75s

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
{"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"A seasonal period exists in the series.","required_evidence":["seasonal_period"]},{"claim":"There are regime changes in the series.","required_evidence":["regime_changes"]},{"claim":"Similarities exist between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To determine the dominant period indicative of a seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"To identify potential regime shifts in the series.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"To compare different segments of the series for pairwise similarity.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective at the medium scale is to detect patterns such as cycles, steps, and repeated regimes within the series. This requires measuring seasonal periods, identifying regime changes, and assessing pairwise similarities between different segments of the series."}
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
- cross_series_compare
  inputs: series_index_1, series_index_2, optional start/end
  outputs: comparison stats, correlation, distance
  often_combined_with: lag_corr, pairwise_distance
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to find the dominant period in the series which can be indicative of a seasonal cycle. Then, we apply 'change_points' to identify regime shifts within the same series. Finally, we perform a pairwise comparison using 'cross_series_compare' to assess the similarities between different segments of the series.",
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
      "output_key": "regime_change_results",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "cross_series_compare",
      "output_key": "similarity_results",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=991 completion=197 latency=7.06s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"regime_change_results","input_binding":{}},{"step":3,"tool":"cross_series_compare","output_key":"similarity_results","input_binding":{}}],"reasoning":"First, we use 'fft_period' to find the dominant period in the series which can be indicative of a seasonal cycle. Then, we apply 'change_points' to identify regime shifts within the same series. Finally, we perform a pairwise comparison using 'cross_series_compare' to assess the similarities between different segments of the series."}
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
- cross_series_compare: Compare windows across TWO series (analogical / multi-series segment tasks). Returns per-series segment stats, trend match, distance, correlation.
  args: {series_index_1=1-based int (default 1), series_index_2=1-based int (default 2), start=optional shared window start, end=optional shared window end, left_interval=optional [start,end] for series 1, right_interval=optional [start,end] for series 2}
  returns: {series_1/series_2=segment stats, comparison=trend agreement, distance, correlation}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to find the dominant period in the series which can be indicative of a seasonal cycle. Then, we apply 'change_points' to identify regime shifts within the same series. Finally, we perform a pairwise comparison using 'cross_series_compare' to assess the similarities between different segments of the series.",
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
    },
    {
      "step": 3,
      "tool": "cross_series_compare",
      "args": {
        "series_index_1": 1,
        "series_index_2": 1
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m0`

tokens prompt=1392 completion=456 latency=16.31s

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
{"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"A seasonal period exists in the series.","required_evidence":["seasonal_period"]},{"claim":"There are regime changes in the series.","required_evidence":["regime_changes"]},{"claim":"Similarities exist between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"To determine the dominant period indicative of a seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"To identify potential regime shifts in the series.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"To compare different segments of the series for pairwise similarity.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective at the medium scale is to detect patterns such as cycles, steps, and repeated regimes within the series. This requires measuring seasonal periods, identifying regime changes, and assessing pairwise similarities between different segments of the series."}
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
      "spectral_strength": 0.0867384112592565,
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
          "index": 172,
          "score": 4.17
        },
        {
          "index": 173,
          "score": 4.167857142857143
        },
        {
          "index": 174,
          "score": 4.055714285714285
        },
        {
          "index": 171,
          "score": 4.007857142857144
        },
        {
          "index": 161,
          "score": 3.875714285714284
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  },
  {
    "call_id": "medium:step3",
    "step": 3,
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

<assignment>
{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate that a seasonal period has been identified with a dominant period of 24 hours, and there are multiple change points identified in the data series. Pairwise similarity analysis could not be performed due to the lack of a second series. The analysis has successfully addressed the presence of seasonal patterns and regime changes, but lacks cross-validation with neighboring segments.",
  "scale": "medium",
  "observations": ["Seasonal period exists with a dominant period of 24 hours.", "Multiple potential regime changes have been identified in the series.", "Unable to perform pairwise similarity analysis due to insufficient data."],
  "evidence_intervals": ["[0, 288)"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "A seasonal period exists in the series.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "seasonal_period"
    },
    {
      "claim": "There are regime changes in the series.",
      "evidence": [
        {
          "type": "regime_changes",
          "value": "Multiple candidates found",
          "source_tool": "change_points",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "regime_changes"
    },
    {
      "claim": "Similarities exist between different segments of the series.",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {"seasonal_period": "tool_supported", "regime_changes": "tool_supported", "pairwise_similarity": "unresolved"},
  "unresolved_claims": ["Similarities exist between different segments of the series."]
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m1`

tokens prompt=4172 completion=338 latency=13.23s

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
{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.","task_summary":"Select the best description for the provided univariate time series data among four given options.","target_output":"Choose the best description from the candidates.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of key features","Robust alignment with a single descriptive statement","Consistent validation across scales"],"notes":"Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
retry_context=unresolved_claims=['Similarities exist between different segments of the series.']; retry capability planning
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective at the medium scale is to detect patterns such as cycles, steps, and repeated regimes within the series. This requires measuring seasonal periods, regime changes, and pairwise similarities. Validation is needed by cross-validating findings with neighboring segments.",
  "evidence_plan": {
    "objective": "Detect patterns such as cycles, steps, and repeated regimes within the series.",
    "claims_to_support": [
      {"claim": "Seasonal patterns exist within the series.", "required_evidence": ["seasonal_period"]},
      {"claim": "Regime changes occur within the series.", "required_evidence": ["regime_changes"]},
      {"claim": "Pairwise similarity exists between different segments of the series.", "required_evidence": ["pairwise_similarity"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "medium"},
    "validation_needs": ["Cross-validate findings with neighboring segments to ensure robustness"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "fft_period", "reason": "Detect dominant spectral period as an indication of potential seasonal cycle.", "supports_evidence": ["seasonal_period"]},
      {"tool": "change_points", "reason": "Locate potential regime changes in the series to analyze level shifts.", "supports_evidence": ["regime_changes"]},
      {"tool": "cross_series_compare", "reason": "Measure similarity between paired segments to identify repeated regimes.", "supports_evidence": ["pairwise_similarity"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m1`

tokens prompt=859 completion=209 latency=7.45s

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
{"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"Seasonal patterns exist within the series.","required_evidence":["seasonal_period"]},{"claim":"Regime changes occur within the series.","required_evidence":["regime_changes"]},{"claim":"Pairwise similarity exists between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"Detect dominant spectral period as an indication of potential seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"Locate potential regime changes in the series to analyze level shifts.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"Measure similarity between paired segments to identify repeated regimes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective at the medium scale is to detect patterns such as cycles, steps, and repeated regimes within the series. This requires measuring seasonal periods, regime changes, and pairwise similarities. Validation is needed by cross-validating findings with neighboring segments."}
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
- cross_series_compare
  inputs: series_index_1, series_index_2, optional start/end
  outputs: comparison stats, correlation, distance
  often_combined_with: lag_corr, pairwise_distance
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes.",
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
      "output_key": "regime_change_indices",
      "input_binding": {}
    },
    {
      "step": 3,
      "tool": "cross_series_compare",
      "output_key": "similarity_stats",
      "input_binding": {"series_index_1": "$step1.series", "series_index_2": "$step2.series"}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m1`

tokens prompt=1008 completion=224 latency=8.00s

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
{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"regime_change_indices","input_binding":{}},{"step":3,"tool":"cross_series_compare","output_key":"similarity_stats","input_binding":{"series_index_1":"$step1.series","series_index_2":"$step2.series"}}],"reasoning":"First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes."}
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
- cross_series_compare: Compare windows across TWO series (analogical / multi-series segment tasks). Returns per-series segment stats, trend match, distance, correlation.
  args: {series_index_1=1-based int (default 1), series_index_2=1-based int (default 2), start=optional shared window start, end=optional shared window end, left_interval=optional [start,end] for series 1, right_interval=optional [start,end] for series 2}
  returns: {series_1/series_2=segment stats, comparison=trend agreement, distance, correlation}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes.",
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
    },
    {
      "step": 3,
      "tool": "cross_series_compare",
      "args": {
        "series_index_1": 1,
        "series_index_2": 1,
        "start": "$step2.regime_change_indices[0]",
        "end": "$step2.regime_change_indices[1]"
      }
    }
  ]
}
```

## Homogeneous (medium, s5) — `homogeneous:medium:s5:m1`

tokens prompt=1429 completion=480 latency=17.16s

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
{"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"Seasonal patterns exist within the series.","required_evidence":["seasonal_period"]},{"claim":"Regime changes occur within the series.","required_evidence":["regime_changes"]},{"claim":"Pairwise similarity exists between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"Detect dominant spectral period as an indication of potential seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"Locate potential regime changes in the series to analyze level shifts.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"Measure similarity between paired segments to identify repeated regimes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"reasoning":"The objective at the medium scale is to detect patterns such as cycles, steps, and repeated regimes within the series. This requires measuring seasonal periods, regime changes, and pairwise similarities. Validation is needed by cross-validating findings with neighboring segments."}
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
      "spectral_strength": 0.0867384112592565,
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
          "index": 172,
          "score": 4.17
        },
        {
          "index": 173,
          "score": 4.167857142857143
        },
        {
          "index": 174,
          "score": 4.055714285714285
        },
        {
          "index": 171,
          "score": 4.007857142857144
        },
        {
          "index": 161,
          "score": 3.875714285714284
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  },
  {
    "call_id": "medium:step3",
    "step": 3,
    "tool_name": "cross_series_compare",
    "arguments": {
      "series_index_1": 1,
      "series_index_2": 1,
      "start": "$step2.regime_change_indices[0]",
      "end": "$step2.regime_change_indices[1]"
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

<assignment>
{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "Executed steps indicate that seasonal patterns have been detected with a dominant period of 24 hours and regime changes identified at specific indices. Pairwise similarity comparison could not be conducted due to the requirement of at least two distinct series.",
  "scale": "medium",
  "observations": ["Dominant period of 24 hours indicates daily cycles within the series.", "Potential regime changes identified at various points in the data."],
  "evidence_intervals": ["Step1 identifies a dominant period of 24 hours", "Step2 locates regime change candidates at indices 161, 171, 172, 173, and 174"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "Seasonal patterns exist within the series.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24.0,
          "source_tool": "fft_period",
          "call_id": "medium:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "seasonal_period"
    },
    {
      "claim": "Regime changes occur within the series.",
      "evidence": [
        {
          "type": "regime_changes",
          "value": [161, 171, 172, 173, 174],
          "source_tool": "change_points",
          "call_id": "medium:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "regime_changes"
    },
    {
      "claim": "Pairwise similarity exists between different segments of the series.",
      "evidence": [],
      "confidence": "unresolved",
      "maps_to_measurement": "pairwise_similarity"
    }
  ],
  "coverage": {"seasonal_period": "tool_supported", "regime_changes": "tool_supported", "pairwise_similarity": "unresolved"},
  "unresolved_claims": ["Pairwise similarity exists between different segments of the series."]
}
```

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4154 completion=369 latency=14.36s

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
{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.","task_summary":"Select the best description for the provided univariate time series data among four given options.","target_output":"Choose the best description from the candidates.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of key features","Robust alignment with a single descriptive statement","Consistent validation across scales"],"notes":"Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend, persistence, and long-range dependence. The validation requirement mandates reconciling these findings with observations from medium and short scales for a comprehensive view.",
  "evidence_plan": {
    "objective": "Analyze the overall structure, trends, and long-term dependencies of the series.",
    "claims_to_support": [
      {"claim": "There is a discernible global trend in the series.", "required_evidence": ["global trend"]},
      {"claim": "The series exhibits persistence over time.", "required_evidence": ["persistence"]},
      {"claim": "There are long-range dependencies in the series.", "required_evidence": ["long-range dependence"]}
    ],
    "analysis_scope": {"target_series": [1], "focus_intervals": [], "scale": "long"},
    "validation_needs": ["Reconcile with observations from medium and short scales for a comprehensive view"]
  },
  "capability_selection": {
    "selected_tools": [
      {"tool": "segment_trend", "reason": "To measure the overall direction and slope of the series, which indicates a global trend.", "supports_evidence": ["global trend"]},
      {"tool": "hurst_exponent", "reason": "To estimate persistence in the series over long periods, capturing whether past values influence future ones.", "supports_evidence": ["persistence"]},
      {"tool": "autocorr", "reason": "To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.", "supports_evidence": ["long-range dependence"]}
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=881 completion=215 latency=7.66s

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
{"evidence_plan":{"objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","claims_to_support":[{"claim":"There is a discernible global trend in the series.","required_evidence":["global trend"]},{"claim":"The series exhibits persistence over time.","required_evidence":["persistence"]},{"claim":"There are long-range dependencies in the series.","required_evidence":["long-range dependence"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Reconcile with observations from medium and short scales for a comprehensive view"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall direction and slope of the series, which indicates a global trend.","supports_evidence":["global trend"]},{"tool":"hurst_exponent","reason":"To estimate persistence in the series over long periods, capturing whether past values influence future ones.","supports_evidence":["persistence"]},{"tool":"autocorr","reason":"To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.","supports_evidence":["long-range dependence"]}],"no_tool_decision":null},"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend, persistence, and long-range dependence. The validation requirement mandates reconciling these findings with observations from medium and short scales for a comprehensive view."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- autocorr
  inputs: series, max_lag or lags[]
  outputs: best_lag, acf, acf_at_lags
  depends: max_lag should cover candidate period when validating fft_period
- hurst_exponent
  inputs: series
  outputs: hurst, persistence_hint
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend using segment_trend, estimating persistence in the series using hurst_exponent, and investigating long-range dependencies with autocorr. These steps will provide evidence for the discernible global trend, persistence, and long-range dependence claims.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "trend_measurement",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "hurst_exponent",
      "output_key": "persistence_measurement",
      "input_binding": {"series": "$step1.series"}
    },
    {
      "step": 3,
      "tool": "autocorr",
      "output_key": "lagged_correlation",
      "input_binding": {"series": "$step1.series"}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=1051 completion=200 latency=7.18s

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
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_measurement","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"autocorr","output_key":"lagged_correlation","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend using segment_trend, estimating persistence in the series using hurst_exponent, and investigating long-range dependencies with autocorr. These steps will provide evidence for the discernible global trend, persistence, and long-range dependence claims."}
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
- autocorr: Autocorrelation up to max_lag (full ACF list). Optional lags=[...] returns acf_at_lags for specific lags.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, max_lag=int, lags=optional list of specific lags}
  returns: {series=best_lag and full autocorrelation values through max_lag; optional acf_at_lags}
- hurst_exponent: Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), matching MMTS label generation. Returns persistence_hint at 0.45/0.55.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=Hurst via compute_Hc, persistence_hint, estimator metadata}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "Analyze the overall structure, trends, and long-term dependencies of the time series using segment_trend, hurst_exponent, and autocorr tools. Segment_trend measures the global trend, hurst_exponent estimates the persistence, and autocorr investigates long-range dependencies. All tools will operate on the entire series without specifying start/end indices.",
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
      "tool": "hurst_exponent",
      "args": {
        "series_index": 1
      }
    },
    {
      "step": 3,
      "tool": "autocorr",
      "args": {
        "series_index": 1,
        "max_lag": 20
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1976 completion=541 latency=19.68s

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
{"evidence_plan":{"objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","claims_to_support":[{"claim":"There is a discernible global trend in the series.","required_evidence":["global trend"]},{"claim":"The series exhibits persistence over time.","required_evidence":["persistence"]},{"claim":"There are long-range dependencies in the series.","required_evidence":["long-range dependence"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Reconcile with observations from medium and short scales for a comprehensive view"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall direction and slope of the series, which indicates a global trend.","supports_evidence":["global trend"]},{"tool":"hurst_exponent","reason":"To estimate persistence in the series over long periods, capturing whether past values influence future ones.","supports_evidence":["persistence"]},{"tool":"autocorr","reason":"To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.","supports_evidence":["long-range dependence"]}],"no_tool_decision":null},"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend, persistence, and long-range dependence. The validation requirement mandates reconciling these findings with observations from medium and short scales for a comprehensive view."}
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
      "slope": -0.05623693379790941,
      "direction": "downward",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 2.7979861111111113,
      "std": 2.9204491140208004,
      "start_value": 20.82,
      "end_value": 4.68
    },
    "error": null,
    "args_fingerprint": "dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"
  },
  {
    "call_id": "long:step2",
    "step": 2,
    "tool_name": "hurst_exponent",
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
      "hurst": 0.07099234166287388,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 288,
      "kind": "random_walk",
      "simplified": true,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"
  },
  {
    "call_id": "long:step3",
    "step": 3,
    "tool_name": "autocorr",
    "arguments": {
      "series_index": 1,
      "max_lag": 20
    },
    "resolved_arguments": {
      "series_index": 1,
      "max_lag": 20
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "max_lag": 20,
      "best_lag": 1,
      "acf": [
        0.6509729608310599,
        0.39330435304481126,
        0.2770177892525852,
        0.16060205192533394,
        0.05270878274349066,
        -0.04715485654720299,
        -0.13044791233107672,
        -0.1967197110143704,
        -0.2397437058113089,
        -0.2793934356481875,
        -0.32341088664915374,
        -0.33999193360055413,
        -0.3052687703505414,
        -0.2531820727996157,
        -0.22232160753042138,
        -0.18857009087507176,
        -0.1260879650393981,
        -0.04492781059304181,
        0.05241074283919136,
        0.1570942937331285
      ],
      "acf_at_lags": {}
    },
    "error": null,
    "args_fingerprint": "4c5402c38b7224460d6af99a8080d7d8833ea0c9"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes measurements of the global trend, persistence, and long-range dependence as required. The global trend shows a vague downward direction with a negative slope (-0.0562). The Hurst exponent indicates anti-persistent behavior (0.071), suggesting past values may inversely influence future ones. Autocorrelation analysis reveals lagged correlations extending beyond immediate neighbors, indicative of long-range dependencies.",
  "scale": "long",
  "observations": ["The series exhibits a vague downward global trend with a negative slope.", "Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies.", "Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."],
  "evidence_intervals": ["none specified"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There is a discernible global trend in the series.",
      "evidence": [
        {
          "type": "global_trend",
          "value": "-0.0562",
          "source_tool": "segment_trend",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "The series exhibits persistence over time.",
      "evidence": [
        {
          "type": "persistence",
          "value": "anti_persistent",
          "source_tool": "hurst_exponent",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "There are long-range dependencies in the series.",
      "evidence": [
        {
          "type": "long_range_dependence",
          "value": "-0.2793934356481875",
          "source_tool": "autocorr",
          "call_id": "long:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "long_range_dependence"
    }
  ],
  "coverage": {"global_trend": "tool_supported", "persistence": "tool_supported", "long_range_dependence": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m0`

tokens prompt=9851 completion=490 latency=21.60s

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
{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.","task_summary":"Select the best description for the provided univariate time series data among four given options.","target_output":"Choose the best description from the candidates.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of key features","Robust alignment with a single descriptive statement","Consistent validation across scales"],"notes":"Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."}
</plan_context>

<task_summary>
Select the best description for the provided univariate time series data among four given options.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that localized events, abrupt changes, and short-term variations have been identified through the use of local_extrema, diff_stats, and sliding_stats respectively. The objective of identifying localized events, abrupt changes, and short-term variations is met.","scale":"short","observations":["20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations."],"evidence_intervals":["full series"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 20, \"n_troughs\": 20, \"peak_idx\": [14, 24, 38, 47, 52, 71, 96, 111, 121, 135, 144, 158, 168, 183, 192, 207, 216, 239, 264, 286], \"trough_idx\": [10, 17, 34, 40, 51, 59, 83, 106, 113, 130, 137, 154, 161, 178, 184, 202, 208, 227, 251, 274]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.05623693379790942, \"std_diff\": 2.1971065355442745, \"max_abs_diff\": 15.55, \"n_sign_changes\": 48}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 14, \"mean_of_means\": 2.693153246753247, \"mean_of_stds\": 1.9296070077763567, \"max_local_std\": 6.194638440471185}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}"],"evidence_plan":{"objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","claims_to_support":[{"claim":"Localized events exist in the series.","required_evidence":["change_location"]},{"claim":"There are abrupt changes in the series.","required_evidence":["abrupt_changes"]},{"claim":"Short-term variations are present in the series.","required_evidence":["short_term_variations"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["Compare findings across different segments of the series to ensure consistency"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Measures first-difference statistics to detect abrupt changes.","supports_evidence":["abrupt_changes"]},{"tool":"sliding_stats","reason":"Provides local volatility measurements to understand short-term variations.","supports_evidence":["short_term_variations"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs to identify localized events.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"local_extrema","output_key":"localized_events","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"abrupt_changes","input_binding":{}},{"step":3,"tool":"sliding_stats","output_key":"short_term_variations","input_binding":{}}],"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations."},"structured_observations":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"coverage":{"change_location":"tool_supported","abrupt_changes":"tool_supported","short_term_variations":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":20,"n_troughs":20,"peak_idx":[14,24,38,47,52,71,96,111,121,135,144,158,168,183,192,207,216,239,264,286],"trough_idx":[10,17,34,40,51,59,83,106,113,130,137,154,161,178,184,202,208,227,251,274]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.05623693379790942,"std_diff":2.1971065355442745,"max_abs_diff":15.55,"n_sign_changes":48},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":14,"mean_of_means":2.693153246753247,"mean_of_stds":1.9296070077763567,"max_local_std":6.194638440471185},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate that seasonal patterns have been detected with a dominant period of 24 hours and regime changes identified at specific indices. Pairwise similarity comparison could not be conducted due to the requirement of at least two distinct series.","scale":"medium","observations":["Dominant period of 24 hours indicates daily cycles within the series.","Potential regime changes identified at various points in the data."],"evidence_intervals":["Step1 identifies a dominant period of 24 hours","Step2 locates regime change candidates at indices 161, 171, 172, 173, and 174"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.0867384112592565, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 172, \"score\": 4.17}, {\"index\": 173, \"score\": 4.167857142857143}, {\"index\": 174, \"score\": 4.055714285714285}, {\"index\": 171, \"score\": 4.007857142857144}, {\"index\": 161, \"score\": 3.875714285714284}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": \"$step2.regime_change_indices[0]\", \"end\": \"$step2.regime_change_indices[1]\"}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"Seasonal patterns exist within the series.","required_evidence":["seasonal_period"]},{"claim":"Regime changes occur within the series.","required_evidence":["regime_changes"]},{"claim":"Pairwise similarity exists between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"Detect dominant spectral period as an indication of potential seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"Locate potential regime changes in the series to analyze level shifts.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"Measure similarity between paired segments to identify repeated regimes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"regime_change_indices","input_binding":{}},{"step":3,"tool":"cross_series_compare","output_key":"similarity_stats","input_binding":{"series_index_1":"$step1.series","series_index_2":"$step2.series"}}],"reasoning":"First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes."},"structured_observations":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"seasonal_period":"tool_supported","regime_changes":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity exists between different segments of the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.0867384112592565,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":172,"score":4.17},{"index":173,"score":4.167857142857143},{"index":174,"score":4.055714285714285},{"index":171,"score":4.007857142857144},{"index":161,"score":3.875714285714284}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"medium:step3","step":3,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":"$step2.regime_change_indices[0]","end":"$step2.regime_change_indices[1]"},"resolved_arguments":{"series_index_1":1,"series_index_2":1},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes measurements of the global trend, persistence, and long-range dependence as required. The global trend shows a vague downward direction with a negative slope (-0.0562). The Hurst exponent indicates anti-persistent behavior (0.071), suggesting past values may inversely influence future ones. Autocorrelation analysis reveals lagged correlations extending beyond immediate neighbors, indicative of long-range dependencies.","scale":"long","observations":["The series exhibits a vague downward global trend with a negative slope.","Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies.","Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."],"evidence_intervals":["none specified"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.05623693379790941, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 2.7979861111111113, \"std\": 2.9204491140208004, \"start_value\": 20.82, \"end_value\": 4.68}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.07099234166287388, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 288, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.6509729608310599, 0.39330435304481126, 0.2770177892525852, 0.16060205192533394, 0.05270878274349066, -0.04715485654720299, -0.13044791233107672, -0.1967197110143704, -0.2397437058113089, -0.2793934356481875, -0.32341088664915374, -0.33999193360055413, -0.3052687703505414, -0.2531820727996157, -0.22232160753042138, -0.18857009087507176, -0.1260879650393981, -0.04492781059304181, 0.05241074283919136, 0.1570942937331285], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","claims_to_support":[{"claim":"There is a discernible global trend in the series.","required_evidence":["global trend"]},{"claim":"The series exhibits persistence over time.","required_evidence":["persistence"]},{"claim":"There are long-range dependencies in the series.","required_evidence":["long-range dependence"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Reconcile with observations from medium and short scales for a comprehensive view"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall direction and slope of the series, which indicates a global trend.","supports_evidence":["global trend"]},{"tool":"hurst_exponent","reason":"To estimate persistence in the series over long periods, capturing whether past values influence future ones.","supports_evidence":["persistence"]},{"tool":"autocorr","reason":"To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.","supports_evidence":["long-range dependence"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_measurement","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"autocorr","output_key":"lagged_correlation","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend using segment_trend, estimating persistence in the series using hurst_exponent, and investigating long-range dependencies with autocorr. These steps will provide evidence for the discernible global trend, persistence, and long-range dependence claims."},"structured_observations":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}],"coverage":{"global_trend":"tool_supported","persistence":"tool_supported","long_range_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.05623693379790941,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":2.7979861111111113,"std":2.9204491140208004,"start_value":20.82,"end_value":4.68},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.07099234166287388,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":288,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step3","step":3,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.6509729608310599,0.39330435304481126,0.2770177892525852,0.16060205192533394,0.05270878274349066,-0.04715485654720299,-0.13044791233107672,-0.1967197110143704,-0.2397437058113089,-0.2793934356481875,-0.32341088664915374,-0.33999193360055413,-0.3052687703505414,-0.2531820727996157,-0.22232160753042138,-0.18857009087507176,-0.1260879650393981,-0.04492781059304181,0.05241074283919136,0.1570942937331285],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations. Dominant period of 24 hours indicates daily cycles within the series. Potential regime changes identified at various points in the data. The series exhibits a vague downward global trend with a negative slope. Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies. Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation.","structured_by_scale":{"short":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"medium":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) This series demonstrates a complex multi-phase behavior: initial growth to around 35, followed by decline and stabilization near 15, then dramatic rise to peak values around 50.
B) The data shows consistent cyclical patterns with values fluctuating between 1-10, punctuated by dramatic spikes exceeding 20, suggesting a recurring seasonal or operational pattern.
C) This time series exhibits regular periodic oscillations with occasional sharp spikes, maintaining relatively low baseline values around 2-3 with periodic peaks reaching up to 21.
D) The time series displays high variability with frequent fluctuations between 5-18, including periods of constant values and irregular spikes, suggesting unstable or noisy underlying processes.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence covers short-term characteristics, seasonal patterns, and long-range dependencies. However, pairwise similarity, which is essential for matching, was not evaluated because there were no other candidate series provided. The objective is to match the observed time series to the most accurate description among the given candidates.",
  "evidence_plan": {
    "objective": "Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.",
    "claims_to_support": [
      {
        "claim": "Localized events exist in the series.",
        "required_evidence": ["change_location"]
      },
      {
        "claim": "There are abrupt changes in the series.",
        "required_evidence": ["abrupt_changes"]
      },
      {
        "claim": "Short-term variations are present in the series.",
        "required_evidence": ["short_term_variations"]
      },
      {
        "claim": "Seasonal patterns exist within the series.",
        "required_evidence": ["seasonal_period"]
      },
      {
        "claim": "Regime changes occur within the series.",
        "required_evidence": ["regime_changes"]
      },
      {
        "claim": "Pairwise similarity exists between different segments of the series.",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "There is a discernible global trend in the series.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "The series exhibits persistence over time.",
        "required_evidence": ["persistence"]
      },
      {
        "claim": "There are long-range dependencies in the series.",
        "required_evidence": ["long_range_dependence"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": [
      "Cross-check with alternative descriptions to confirm the match"
    ]
  },
  "capability_selection": {
    "selected_tools": [
      "describe_series",
      "fft_period",
      "global_extrema",
      "local_extrema",
      "pairwise_distance",
      "segment_trend",
      "smooth_shape_match",
      "subsequence_rank",
      "waveform_features"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m0`

tokens prompt=8353 completion=1024 latency=41.69s

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
{"evidence_plan":{"objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that localized events, abrupt changes, and short-term variations have been identified through the use of local_extrema, diff_stats, and sliding_stats respectively. The objective of identifying localized events, abrupt changes, and short-term variations is met.","scale":"short","observations":["20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations."],"evidence_intervals":["full series"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 20, \"n_troughs\": 20, \"peak_idx\": [14, 24, 38, 47, 52, 71, 96, 111, 121, 135, 144, 158, 168, 183, 192, 207, 216, 239, 264, 286], \"trough_idx\": [10, 17, 34, 40, 51, 59, 83, 106, 113, 130, 137, 154, 161, 178, 184, 202, 208, 227, 251, 274]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.05623693379790942, \"std_diff\": 2.1971065355442745, \"max_abs_diff\": 15.55, \"n_sign_changes\": 48}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 14, \"mean_of_means\": 2.693153246753247, \"mean_of_stds\": 1.9296070077763567, \"max_local_std\": 6.194638440471185}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}"],"evidence_plan":{"objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","claims_to_support":[{"claim":"Localized events exist in the series.","required_evidence":["change_location"]},{"claim":"There are abrupt changes in the series.","required_evidence":["abrupt_changes"]},{"claim":"Short-term variations are present in the series.","required_evidence":["short_term_variations"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["Compare findings across different segments of the series to ensure consistency"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Measures first-difference statistics to detect abrupt changes.","supports_evidence":["abrupt_changes"]},{"tool":"sliding_stats","reason":"Provides local volatility measurements to understand short-term variations.","supports_evidence":["short_term_variations"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs to identify localized events.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"local_extrema","output_key":"localized_events","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"abrupt_changes","input_binding":{}},{"step":3,"tool":"sliding_stats","output_key":"short_term_variations","input_binding":{}}],"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations."},"structured_observations":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"coverage":{"change_location":"tool_supported","abrupt_changes":"tool_supported","short_term_variations":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":20,"n_troughs":20,"peak_idx":[14,24,38,47,52,71,96,111,121,135,144,158,168,183,192,207,216,239,264,286],"trough_idx":[10,17,34,40,51,59,83,106,113,130,137,154,161,178,184,202,208,227,251,274]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.05623693379790942,"std_diff":2.1971065355442745,"max_abs_diff":15.55,"n_sign_changes":48},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":14,"mean_of_means":2.693153246753247,"mean_of_stds":1.9296070077763567,"max_local_std":6.194638440471185},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate that seasonal patterns have been detected with a dominant period of 24 hours and regime changes identified at specific indices. Pairwise similarity comparison could not be conducted due to the requirement of at least two distinct series.","scale":"medium","observations":["Dominant period of 24 hours indicates daily cycles within the series.","Potential regime changes identified at various points in the data."],"evidence_intervals":["Step1 identifies a dominant period of 24 hours","Step2 locates regime change candidates at indices 161, 171, 172, 173, and 174"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.0867384112592565, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 172, \"score\": 4.17}, {\"index\": 173, \"score\": 4.167857142857143}, {\"index\": 174, \"score\": 4.055714285714285}, {\"index\": 171, \"score\": 4.007857142857144}, {\"index\": 161, \"score\": 3.875714285714284}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": \"$step2.regime_change_indices[0]\", \"end\": \"$step2.regime_change_indices[1]\"}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"Seasonal patterns exist within the series.","required_evidence":["seasonal_period"]},{"claim":"Regime changes occur within the series.","required_evidence":["regime_changes"]},{"claim":"Pairwise similarity exists between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"Detect dominant spectral period as an indication of potential seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"Locate potential regime changes in the series to analyze level shifts.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"Measure similarity between paired segments to identify repeated regimes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"regime_change_indices","input_binding":{}},{"step":3,"tool":"cross_series_compare","output_key":"similarity_stats","input_binding":{"series_index_1":"$step1.series","series_index_2":"$step2.series"}}],"reasoning":"First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes."},"structured_observations":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"seasonal_period":"tool_supported","regime_changes":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity exists between different segments of the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.0867384112592565,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":172,"score":4.17},{"index":173,"score":4.167857142857143},{"index":174,"score":4.055714285714285},{"index":171,"score":4.007857142857144},{"index":161,"score":3.875714285714284}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"medium:step3","step":3,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":"$step2.regime_change_indices[0]","end":"$step2.regime_change_indices[1]"},"resolved_arguments":{"series_index_1":1,"series_index_2":1},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes measurements of the global trend, persistence, and long-range dependence as required. The global trend shows a vague downward direction with a negative slope (-0.0562). The Hurst exponent indicates anti-persistent behavior (0.071), suggesting past values may inversely influence future ones. Autocorrelation analysis reveals lagged correlations extending beyond immediate neighbors, indicative of long-range dependencies.","scale":"long","observations":["The series exhibits a vague downward global trend with a negative slope.","Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies.","Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."],"evidence_intervals":["none specified"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.05623693379790941, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 2.7979861111111113, \"std\": 2.9204491140208004, \"start_value\": 20.82, \"end_value\": 4.68}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.07099234166287388, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 288, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.6509729608310599, 0.39330435304481126, 0.2770177892525852, 0.16060205192533394, 0.05270878274349066, -0.04715485654720299, -0.13044791233107672, -0.1967197110143704, -0.2397437058113089, -0.2793934356481875, -0.32341088664915374, -0.33999193360055413, -0.3052687703505414, -0.2531820727996157, -0.22232160753042138, -0.18857009087507176, -0.1260879650393981, -0.04492781059304181, 0.05241074283919136, 0.1570942937331285], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","claims_to_support":[{"claim":"There is a discernible global trend in the series.","required_evidence":["global trend"]},{"claim":"The series exhibits persistence over time.","required_evidence":["persistence"]},{"claim":"There are long-range dependencies in the series.","required_evidence":["long-range dependence"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Reconcile with observations from medium and short scales for a comprehensive view"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall direction and slope of the series, which indicates a global trend.","supports_evidence":["global trend"]},{"tool":"hurst_exponent","reason":"To estimate persistence in the series over long periods, capturing whether past values influence future ones.","supports_evidence":["persistence"]},{"tool":"autocorr","reason":"To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.","supports_evidence":["long-range dependence"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_measurement","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"autocorr","output_key":"lagged_correlation","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend using segment_trend, estimating persistence in the series using hurst_exponent, and investigating long-range dependencies with autocorr. These steps will provide evidence for the discernible global trend, persistence, and long-range dependence claims."},"structured_observations":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}],"coverage":{"global_trend":"tool_supported","persistence":"tool_supported","long_range_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.05623693379790941,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":2.7979861111111113,"std":2.9204491140208004,"start_value":20.82,"end_value":4.68},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.07099234166287388,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":288,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step3","step":3,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.6509729608310599,0.39330435304481126,0.2770177892525852,0.16060205192533394,0.05270878274349066,-0.04715485654720299,-0.13044791233107672,-0.1967197110143704,-0.2397437058113089,-0.2793934356481875,-0.32341088664915374,-0.33999193360055413,-0.3052687703505414,-0.2531820727996157,-0.22232160753042138,-0.18857009087507176,-0.1260879650393981,-0.04492781059304181,0.05241074283919136,0.1570942937331285],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations. Dominant period of 24 hours indicates daily cycles within the series. Potential regime changes identified at various points in the data. The series exhibits a vague downward global trend with a negative slope. Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies. Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation.","structured_by_scale":{"short":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"medium":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) This series demonstrates a complex multi-phase behavior: initial growth to around 35, followed by decline and stabilization near 15, then dramatic rise to peak values around 50.
B) The data shows consistent cyclical patterns with values fluctuating between 1-10, punctuated by dramatic spikes exceeding 20, suggesting a recurring seasonal or operational pattern.
C) This time series exhibits regular periodic oscillations with occasional sharp spikes, maintaining relatively low baseline values around 2-3 with periodic peaks reaching up to 21.
D) The time series displays high variability with frequent fluctuations between 5-18, including periods of constant values and irregular spikes, suggesting unstable or noisy underlying processes.
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the series exhibits significant localized events, abrupt changes, short-term variations, a daily cycle (seasonality), and some form of anti-persistent behavior with long-range dependencies. The observed characteristics suggest frequent fluctuations but also a regular seasonal pattern with occasional sharp increases.",
  "role": "matching",
  "hypothesis": "The series fits best with an option that captures its key behaviors: periodic fluctuations, seasonality, and sharp spikes.",
  "evidence": ["The series shows 20 peaks and troughs as localized events.", "There are 48 sign changes indicating abrupt changes.", "Maximum local standard deviation of 6.19 indicates significant short-term variations.", "A dominant period of 24 hours suggests daily seasonality.", "Regime changes are identified at various points.", "The Hurst exponent analysis suggests anti-persistent behavior.", "Autocorrelation analysis identifies lagged correlations extending over multiple lags, indicative of long-range dependencies."],
  "candidate_preference": "C",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "short:step3", "medium:step1", "medium:step2", "long:step1", "long:step2", "long:step3"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Localized events exist in the series.",
      "evidence": [
        {
          "type": "change_location",
          "value": 20,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are abrupt changes in the series.",
      "evidence": [
        {
          "type": "abrupt_changes",
          "value": 48,
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Short-term variations are present in the series.",
      "evidence": [
        {
          "type": "short_term_variations",
          "value": 6.19,
          "provenance": "tool",
          "ref": "short:step3",
          "call_id": "short:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Seasonal patterns exist within the series.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24.0,
          "provenance": "tool",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Regime changes occur within the series.",
      "evidence": [
        {
          "type": "regime_changes",
          "value": [161, 171, 172, 173, 174],
          "provenance": "tool",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There is a discernible global trend in the series.",
      "evidence": [
        {
          "type": "global_trend",
          "value": "-0.0562",
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The series exhibits anti-persistent behavior over time.",
      "evidence": [
        {
          "type": "persistence",
          "value": "anti_persistent",
          "provenance": "tool",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are long-range dependencies in the series.",
      "evidence": [
        {
          "type": "long_range_dependence",
          "value": "-0.2793934356481875",
          "provenance": "tool",
          "ref": "long:step3",
          "call_id": "long:step3"
        }
     
```

## Heterogeneous (matching, s1s2) — `heterogeneous:matching:s1s2:m1`

tokens prompt=9862 completion=449 latency=19.99s

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
{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the overall structure and identifying patterns, cyclicality, variability, and extreme events within the time series.","task_summary":"Select the best description for the provided univariate time series data among four given options.","target_output":"Choose the best description from the candidates.","answer_type":"choice","capability":"hierarchical time-series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","required_measurements":["change_location","abrupt_changes","short_term_variations"],"validation_requirements":["Compare findings across different segments of the series to ensure consistency"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","required_measurements":["seasonal_period","regime_changes","pairwise_similarity"],"validation_requirements":["Cross-validate findings with neighboring segments to ensure robustness"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","required_measurements":["global_trend","persistence","long_range_dependence"],"validation_requirements":["Reconcile with observations from medium and short scales for a comprehensive view"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["matching"],"success_criteria":["Accurate identification of key features","Robust alignment with a single descriptive statement","Consistent validation across scales"],"notes":"Ensure the analysis captures both fine-grained and overarching trends to accurately reflect the nature of the time series."}
</plan_context>

<task_summary>
Select the best description for the provided univariate time series data among four given options.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that localized events, abrupt changes, and short-term variations have been identified through the use of local_extrema, diff_stats, and sliding_stats respectively. The objective of identifying localized events, abrupt changes, and short-term variations is met.","scale":"short","observations":["20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations."],"evidence_intervals":["full series"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 20, \"n_troughs\": 20, \"peak_idx\": [14, 24, 38, 47, 52, 71, 96, 111, 121, 135, 144, 158, 168, 183, 192, 207, 216, 239, 264, 286], \"trough_idx\": [10, 17, 34, 40, 51, 59, 83, 106, 113, 130, 137, 154, 161, 178, 184, 202, 208, 227, 251, 274]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.05623693379790942, \"std_diff\": 2.1971065355442745, \"max_abs_diff\": 15.55, \"n_sign_changes\": 48}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 14, \"mean_of_means\": 2.693153246753247, \"mean_of_stds\": 1.9296070077763567, \"max_local_std\": 6.194638440471185}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}"],"evidence_plan":{"objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","claims_to_support":[{"claim":"Localized events exist in the series.","required_evidence":["change_location"]},{"claim":"There are abrupt changes in the series.","required_evidence":["abrupt_changes"]},{"claim":"Short-term variations are present in the series.","required_evidence":["short_term_variations"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["Compare findings across different segments of the series to ensure consistency"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Measures first-difference statistics to detect abrupt changes.","supports_evidence":["abrupt_changes"]},{"tool":"sliding_stats","reason":"Provides local volatility measurements to understand short-term variations.","supports_evidence":["short_term_variations"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs to identify localized events.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"local_extrema","output_key":"localized_events","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"abrupt_changes","input_binding":{}},{"step":3,"tool":"sliding_stats","output_key":"short_term_variations","input_binding":{}}],"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations."},"structured_observations":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"coverage":{"change_location":"tool_supported","abrupt_changes":"tool_supported","short_term_variations":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":20,"n_troughs":20,"peak_idx":[14,24,38,47,52,71,96,111,121,135,144,158,168,183,192,207,216,239,264,286],"trough_idx":[10,17,34,40,51,59,83,106,113,130,137,154,161,178,184,202,208,227,251,274]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.05623693379790942,"std_diff":2.1971065355442745,"max_abs_diff":15.55,"n_sign_changes":48},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":14,"mean_of_means":2.693153246753247,"mean_of_stds":1.9296070077763567,"max_local_std":6.194638440471185},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate that seasonal patterns have been detected with a dominant period of 24 hours and regime changes identified at specific indices. Pairwise similarity comparison could not be conducted due to the requirement of at least two distinct series.","scale":"medium","observations":["Dominant period of 24 hours indicates daily cycles within the series.","Potential regime changes identified at various points in the data."],"evidence_intervals":["Step1 identifies a dominant period of 24 hours","Step2 locates regime change candidates at indices 161, 171, 172, 173, and 174"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.0867384112592565, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 172, \"score\": 4.17}, {\"index\": 173, \"score\": 4.167857142857143}, {\"index\": 174, \"score\": 4.055714285714285}, {\"index\": 171, \"score\": 4.007857142857144}, {\"index\": 161, \"score\": 3.875714285714284}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": \"$step2.regime_change_indices[0]\", \"end\": \"$step2.regime_change_indices[1]\"}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"Seasonal patterns exist within the series.","required_evidence":["seasonal_period"]},{"claim":"Regime changes occur within the series.","required_evidence":["regime_changes"]},{"claim":"Pairwise similarity exists between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"Detect dominant spectral period as an indication of potential seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"Locate potential regime changes in the series to analyze level shifts.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"Measure similarity between paired segments to identify repeated regimes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"regime_change_indices","input_binding":{}},{"step":3,"tool":"cross_series_compare","output_key":"similarity_stats","input_binding":{"series_index_1":"$step1.series","series_index_2":"$step2.series"}}],"reasoning":"First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes."},"structured_observations":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"seasonal_period":"tool_supported","regime_changes":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity exists between different segments of the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.0867384112592565,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":172,"score":4.17},{"index":173,"score":4.167857142857143},{"index":174,"score":4.055714285714285},{"index":171,"score":4.007857142857144},{"index":161,"score":3.875714285714284}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"medium:step3","step":3,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":"$step2.regime_change_indices[0]","end":"$step2.regime_change_indices[1]"},"resolved_arguments":{"series_index_1":1,"series_index_2":1},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes measurements of the global trend, persistence, and long-range dependence as required. The global trend shows a vague downward direction with a negative slope (-0.0562). The Hurst exponent indicates anti-persistent behavior (0.071), suggesting past values may inversely influence future ones. Autocorrelation analysis reveals lagged correlations extending beyond immediate neighbors, indicative of long-range dependencies.","scale":"long","observations":["The series exhibits a vague downward global trend with a negative slope.","Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies.","Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."],"evidence_intervals":["none specified"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.05623693379790941, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 2.7979861111111113, \"std\": 2.9204491140208004, \"start_value\": 20.82, \"end_value\": 4.68}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.07099234166287388, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 288, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.6509729608310599, 0.39330435304481126, 0.2770177892525852, 0.16060205192533394, 0.05270878274349066, -0.04715485654720299, -0.13044791233107672, -0.1967197110143704, -0.2397437058113089, -0.2793934356481875, -0.32341088664915374, -0.33999193360055413, -0.3052687703505414, -0.2531820727996157, -0.22232160753042138, -0.18857009087507176, -0.1260879650393981, -0.04492781059304181, 0.05241074283919136, 0.1570942937331285], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","claims_to_support":[{"claim":"There is a discernible global trend in the series.","required_evidence":["global trend"]},{"claim":"The series exhibits persistence over time.","required_evidence":["persistence"]},{"claim":"There are long-range dependencies in the series.","required_evidence":["long-range dependence"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Reconcile with observations from medium and short scales for a comprehensive view"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall direction and slope of the series, which indicates a global trend.","supports_evidence":["global trend"]},{"tool":"hurst_exponent","reason":"To estimate persistence in the series over long periods, capturing whether past values influence future ones.","supports_evidence":["persistence"]},{"tool":"autocorr","reason":"To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.","supports_evidence":["long-range dependence"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_measurement","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"autocorr","output_key":"lagged_correlation","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend using segment_trend, estimating persistence in the series using hurst_exponent, and investigating long-range dependencies with autocorr. These steps will provide evidence for the discernible global trend, persistence, and long-range dependence claims."},"structured_observations":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}],"coverage":{"global_trend":"tool_supported","persistence":"tool_supported","long_range_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.05623693379790941,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":2.7979861111111113,"std":2.9204491140208004,"start_value":20.82,"end_value":4.68},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.07099234166287388,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":288,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step3","step":3,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.6509729608310599,0.39330435304481126,0.2770177892525852,0.16060205192533394,0.05270878274349066,-0.04715485654720299,-0.13044791233107672,-0.1967197110143704,-0.2397437058113089,-0.2793934356481875,-0.32341088664915374,-0.33999193360055413,-0.3052687703505414,-0.2531820727996157,-0.22232160753042138,-0.18857009087507176,-0.1260879650393981,-0.04492781059304181,0.05241074283919136,0.1570942937331285],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations. Dominant period of 24 hours indicates daily cycles within the series. Potential regime changes identified at various points in the data. The series exhibits a vague downward global trend with a negative slope. Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies. Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation.","structured_by_scale":{"short":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"medium":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
retry_context=unresolved_claims=['parse_failure']
</metadata>

<candidates>
A) This series demonstrates a complex multi-phase behavior: initial growth to around 35, followed by decline and stabilization near 15, then dramatic rise to peak values around 50.
B) The data shows consistent cyclical patterns with values fluctuating between 1-10, punctuated by dramatic spikes exceeding 20, suggesting a recurring seasonal or operational pattern.
C) This time series exhibits regular periodic oscillations with occasional sharp spikes, maintaining relatively low baseline values around 2-3 with periodic peaks reaching up to 21.
D) The time series displays high variability with frequent fluctuations between 5-18, including periods of constant values and irregular spikes, suggesting unstable or noisy underlying processes.
</candidates>

Produce the EvidenceCapabilityPlan JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "The current evidence covers short-term characteristics, seasonal patterns, and long-range dependencies. However, pairwise similarity, which is essential for matching, was not evaluated because there were insufficient distinct series for comparison. The objective is to match the observed time series to the most accurate description among the given candidates.",
  "evidence_plan": {
    "objective": "Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.",
    "claims_to_support": [
      {
        "claim": "Localized events exist in the series.",
        "required_evidence": ["change_location"]
      },
      {
        "claim": "There are abrupt changes in the series.",
        "required_evidence": ["abrupt_changes"]
      },
      {
        "claim": "Short-term variations are present in the series.",
        "required_evidence": ["short_term_variations"]
      },
      {
        "claim": "Seasonal patterns exist within the series.",
        "required_evidence": ["seasonal_period"]
      },
      {
        "claim": "Regime changes occur within the series.",
        "required_evidence": ["regime_changes"]
      },
      {
        "claim": "Pairwise similarity exists between different segments of the series.",
        "required_evidence": ["pairwise_similarity"]
      },
      {
        "claim": "There is a discernible global trend in the series.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "The series exhibits persistence over time.",
        "required_evidence": ["persistence"]
      },
      {
        "claim": "There are long-range dependencies in the series.",
        "required_evidence": ["long_range_dependence"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "role": "matching"
    },
    "validation_needs": [
      "Cross-check with alternative descriptions to confirm the match."
    ]
  },
  "capability_selection": {
    "selected_tools": [
      "describe_series",
      "pairwise_distance"
    ],
    "no_tool_decision": null
  }
}
```

## Heterogeneous (matching, s5) — `heterogeneous:matching:s5:m1`

tokens prompt=8353 completion=1024 latency=41.69s

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
{"evidence_plan":{"objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","claims_to_support":[],"analysis_scope":{},"validation_needs":[]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"Parse failure fallback; use temporal profile context","evidence_sources":[]}},"reasoning":"Parse failure; skip tools and use temporal profile."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"Executed steps indicate that localized events, abrupt changes, and short-term variations have been identified through the use of local_extrema, diff_stats, and sliding_stats respectively. The objective of identifying localized events, abrupt changes, and short-term variations is met.","scale":"short","observations":["20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations."],"evidence_intervals":["full series"],"confidence":1.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"local_extrema\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_peaks\": 20, \"n_troughs\": 20, \"peak_idx\": [14, 24, 38, 47, 52, 71, 96, 111, 121, 135, 144, 158, 168, 183, 192, 207, 216, 239, 264, 286], \"trough_idx\": [10, 17, 34, 40, 51, 59, 83, 106, 113, 130, 137, 154, 161, 178, 184, 202, 208, 227, 251, 274]}, \"error\": null, \"args_fingerprint\": \"31139f7e956301f570b30f3a308473f914523713\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"diff_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"mean_diff\": -0.05623693379790942, \"std_diff\": 2.1971065355442745, \"max_abs_diff\": 15.55, \"n_sign_changes\": 48}, \"error\": null, \"args_fingerprint\": \"4a37b60672ab33aaec2956de8706ddd2e6292caf\"}","{\"call_id\": \"short:step3\", \"step\": 3, \"tool_name\": \"sliding_stats\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"window\": 14, \"mean_of_means\": 2.693153246753247, \"mean_of_stds\": 1.9296070077763567, \"max_local_std\": 6.194638440471185}, \"error\": null, \"args_fingerprint\": \"5d90c6e3697596cfb881b17b747f76e320a9ebe9\"}"],"evidence_plan":{"objective":"Identify any localized events, abrupt changes, and short-term variations in the series.","claims_to_support":[{"claim":"Localized events exist in the series.","required_evidence":["change_location"]},{"claim":"There are abrupt changes in the series.","required_evidence":["abrupt_changes"]},{"claim":"Short-term variations are present in the series.","required_evidence":["short_term_variations"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["Compare findings across different segments of the series to ensure consistency"]},"capability_selection":{"selected_tools":[{"tool":"diff_stats","reason":"Measures first-difference statistics to detect abrupt changes.","supports_evidence":["abrupt_changes"]},{"tool":"sliding_stats","reason":"Provides local volatility measurements to understand short-term variations.","supports_evidence":["short_term_variations"]},{"tool":"local_extrema","reason":"Counts local peaks and troughs to identify localized events.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"local_extrema","output_key":"localized_events","input_binding":{}},{"step":2,"tool":"diff_stats","output_key":"abrupt_changes","input_binding":{}},{"step":3,"tool":"sliding_stats","output_key":"short_term_variations","input_binding":{}}],"reasoning":"The objective is to identify localized events, abrupt changes, and short-term variations in the series. This involves detecting localized changes, counting abrupt changes, and measuring short-term variations. To achieve this, we first apply local_extrema to count local peaks and troughs which indicate localized events. Next, we use diff_stats to detect abrupt changes by analyzing the differences between consecutive values. Finally, sliding_stats provides local volatility measurements to understand short-term variations."},"structured_observations":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"coverage":{"change_location":"tool_supported","abrupt_changes":"tool_supported","short_term_variations":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"local_extrema","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_peaks":20,"n_troughs":20,"peak_idx":[14,24,38,47,52,71,96,111,121,135,144,158,168,183,192,207,216,239,264,286],"trough_idx":[10,17,34,40,51,59,83,106,113,130,137,154,161,178,184,202,208,227,251,274]},"error":null,"args_fingerprint":"31139f7e956301f570b30f3a308473f914523713"},{"call_id":"short:step2","step":2,"tool_name":"diff_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"mean_diff":-0.05623693379790942,"std_diff":2.1971065355442745,"max_abs_diff":15.55,"n_sign_changes":48},"error":null,"args_fingerprint":"4a37b60672ab33aaec2956de8706ddd2e6292caf"},{"call_id":"short:step3","step":3,"tool_name":"sliding_stats","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"window":14,"mean_of_means":2.693153246753247,"mean_of_stds":1.9296070077763567,"max_local_std":6.194638440471185},"error":null,"args_fingerprint":"5d90c6e3697596cfb881b17b747f76e320a9ebe9"}],"skipped_stages":[]},"medium":{"reasoning":"Executed steps indicate that seasonal patterns have been detected with a dominant period of 24 hours and regime changes identified at specific indices. Pairwise similarity comparison could not be conducted due to the requirement of at least two distinct series.","scale":"medium","observations":["Dominant period of 24 hours indicates daily cycles within the series.","Potential regime changes identified at various points in the data."],"evidence_intervals":["Step1 identifies a dominant period of 24 hours","Step2 locates regime change candidates at indices 161, 171, 172, 173, and 174"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"fft_period\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"dominant_period\": 24.0, \"spectral_strength\": 0.0867384112592565, \"period_trusted\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"726ee7605c7aac2e5823de42d4c34d3c89859438\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 172, \"score\": 4.17}, {\"index\": 173, \"score\": 4.167857142857143}, {\"index\": 174, \"score\": 4.055714285714285}, {\"index\": 171, \"score\": 4.007857142857144}, {\"index\": 161, \"score\": 3.875714285714284}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}","{\"call_id\": \"medium:step3\", \"step\": 3, \"tool_name\": \"cross_series_compare\", \"arguments\": {\"series_index_1\": 1, \"series_index_2\": 1, \"start\": \"$step2.regime_change_indices[0]\", \"end\": \"$step2.regime_change_indices[1]\"}, \"resolved_arguments\": {\"series_index_1\": 1, \"series_index_2\": 1}, \"success\": false, \"data\": {}, \"error\": \"Need >=2 series\", \"args_fingerprint\": \"\"}"],"evidence_plan":{"objective":"Detect patterns such as cycles, steps, and repeated regimes within the series.","claims_to_support":[{"claim":"Seasonal patterns exist within the series.","required_evidence":["seasonal_period"]},{"claim":"Regime changes occur within the series.","required_evidence":["regime_changes"]},{"claim":"Pairwise similarity exists between different segments of the series.","required_evidence":["pairwise_similarity"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["Cross-validate findings with neighboring segments to ensure robustness"]},"capability_selection":{"selected_tools":[{"tool":"fft_period","reason":"Detect dominant spectral period as an indication of potential seasonal cycle.","supports_evidence":["seasonal_period"]},{"tool":"change_points","reason":"Locate potential regime changes in the series to analyze level shifts.","supports_evidence":["regime_changes"]},{"tool":"cross_series_compare","reason":"Measure similarity between paired segments to identify repeated regimes.","supports_evidence":["pairwise_similarity"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"fft_period","output_key":"dominant_period","input_binding":{}},{"step":2,"tool":"change_points","output_key":"regime_change_indices","input_binding":{}},{"step":3,"tool":"cross_series_compare","output_key":"similarity_stats","input_binding":{"series_index_1":"$step1.series","series_index_2":"$step2.series"}}],"reasoning":"First, we use 'fft_period' to detect the dominant spectral period to indicate potential seasonal cycles. Next, we utilize 'change_points' to locate possible regime changes within the series for analyzing level shifts. Lastly, we apply 'cross_series_compare' to measure the similarity between different segments of the series to identify repeated regimes."},"structured_observations":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"coverage":{"seasonal_period":"tool_supported","regime_changes":"tool_supported","pairwise_similarity":"unresolved"},"unresolved_claims":["Pairwise similarity exists between different segments of the series."],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"fft_period","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"dominant_period":24.0,"spectral_strength":0.0867384112592565,"period_trusted":true,"warnings":[]},"error":null,"args_fingerprint":"726ee7605c7aac2e5823de42d4c34d3c89859438"},{"call_id":"medium:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":172,"score":4.17},{"index":173,"score":4.167857142857143},{"index":174,"score":4.055714285714285},{"index":171,"score":4.007857142857144},{"index":161,"score":3.875714285714284}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"},{"call_id":"medium:step3","step":3,"tool_name":"cross_series_compare","arguments":{"series_index_1":1,"series_index_2":1,"start":"$step2.regime_change_indices[0]","end":"$step2.regime_change_indices[1]"},"resolved_arguments":{"series_index_1":1,"series_index_2":1},"success":false,"data":{},"error":"Need >=2 series","args_fingerprint":""}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes measurements of the global trend, persistence, and long-range dependence as required. The global trend shows a vague downward direction with a negative slope (-0.0562). The Hurst exponent indicates anti-persistent behavior (0.071), suggesting past values may inversely influence future ones. Autocorrelation analysis reveals lagged correlations extending beyond immediate neighbors, indicative of long-range dependencies.","scale":"long","observations":["The series exhibits a vague downward global trend with a negative slope.","Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies.","Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."],"evidence_intervals":["none specified"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": -0.05623693379790941, \"direction\": \"downward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 2.7979861111111113, \"std\": 2.9204491140208004, \"start_value\": 20.82, \"end_value\": 4.68}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.07099234166287388, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 288, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"autocorr\", \"arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"resolved_arguments\": {\"series_index\": 1, \"max_lag\": 20}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"max_lag\": 20, \"best_lag\": 1, \"acf\": [0.6509729608310599, 0.39330435304481126, 0.2770177892525852, 0.16060205192533394, 0.05270878274349066, -0.04715485654720299, -0.13044791233107672, -0.1967197110143704, -0.2397437058113089, -0.2793934356481875, -0.32341088664915374, -0.33999193360055413, -0.3052687703505414, -0.2531820727996157, -0.22232160753042138, -0.18857009087507176, -0.1260879650393981, -0.04492781059304181, 0.05241074283919136, 0.1570942937331285], \"acf_at_lags\": {}}, \"error\": null, \"args_fingerprint\": \"4c5402c38b7224460d6af99a8080d7d8833ea0c9\"}"],"evidence_plan":{"objective":"Analyze the overall structure, trends, and long-term dependencies of the series.","claims_to_support":[{"claim":"There is a discernible global trend in the series.","required_evidence":["global trend"]},{"claim":"The series exhibits persistence over time.","required_evidence":["persistence"]},{"claim":"There are long-range dependencies in the series.","required_evidence":["long-range dependence"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["Reconcile with observations from medium and short scales for a comprehensive view"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the overall direction and slope of the series, which indicates a global trend.","supports_evidence":["global trend"]},{"tool":"hurst_exponent","reason":"To estimate persistence in the series over long periods, capturing whether past values influence future ones.","supports_evidence":["persistence"]},{"tool":"autocorr","reason":"To investigate long-range dependencies by assessing lagged correlations that extend over many time steps.","supports_evidence":["long-range dependence"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_measurement","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_measurement","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"autocorr","output_key":"lagged_correlation","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to examine the overall structure, trends, and long-term dependencies in the time series. This involves measuring the global trend using segment_trend, estimating persistence in the series using hurst_exponent, and investigating long-range dependencies with autocorr. These steps will provide evidence for the discernible global trend, persistence, and long-range dependence claims."},"structured_observations":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}],"coverage":{"global_trend":"tool_supported","persistence":"tool_supported","long_range_dependence":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":-0.05623693379790941,"direction":"downward","direction_class":"vague","trend_method":"endpoint","mean":2.7979861111111113,"std":2.9204491140208004,"start_value":20.82,"end_value":4.68},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.07099234166287388,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":288,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step3","step":3,"tool_name":"autocorr","arguments":{"series_index":1,"max_lag":20},"resolved_arguments":{"series_index":1,"max_lag":20},"success":true,"data":{"series_index":1,"start":null,"end":null,"max_lag":20,"best_lag":1,"acf":[0.6509729608310599,0.39330435304481126,0.2770177892525852,0.16060205192533394,0.05270878274349066,-0.04715485654720299,-0.13044791233107672,-0.1967197110143704,-0.2397437058113089,-0.2793934356481875,-0.32341088664915374,-0.33999193360055413,-0.3052687703505414,-0.2531820727996157,-0.22232160753042138,-0.18857009087507176,-0.1260879650393981,-0.04492781059304181,0.05241074283919136,0.1570942937331285],"acf_at_lags":{}},"error":null,"args_fingerprint":"4c5402c38b7224460d6af99a8080d7d8833ea0c9"}],"skipped_stages":[]},"conflicts":[],"summary":"20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations. Dominant period of 24 hours indicates daily cycles within the series. Potential regime changes identified at various points in the data. The series exhibits a vague downward global trend with a negative slope. Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies. Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation.","structured_by_scale":{"short":[{"claim":"Localized events exist in the series.","evidence":[{"type":"change_location","value":40,"source_tool":"local_extrema","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"},{"claim":"There are abrupt changes in the series.","evidence":[{"type":"abrupt_changes","value":48,"source_tool":"diff_stats","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"abrupt_changes"},{"claim":"Short-term variations are present in the series.","evidence":[{"type":"short_term_variations","value":6.19,"source_tool":"sliding_stats","call_id":"short:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"short_term_variations"}],"medium":[{"claim":"Seasonal patterns exist within the series.","evidence":[{"type":"seasonal_period","value":24.0,"source_tool":"fft_period","call_id":"medium:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_period"},{"claim":"Regime changes occur within the series.","evidence":[{"type":"regime_changes","value":[161,171,172,173,174],"source_tool":"change_points","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"regime_changes"},{"claim":"Pairwise similarity exists between different segments of the series.","evidence":[],"confidence":"unresolved","maps_to_measurement":"pairwise_similarity"}],"long":[{"claim":"There is a discernible global trend in the series.","evidence":[{"type":"global_trend","value":"-0.0562","source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series exhibits persistence over time.","evidence":[{"type":"persistence","value":"anti_persistent","source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"There are long-range dependencies in the series.","evidence":[{"type":"long_range_dependence","value":"-0.2793934356481875","source_tool":"autocorr","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"long_range_dependence"}]}}
</temporal_profile>

<assignment>
{"role":"matching","objective":"Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.","required_measurements":["change_location","abrupt_changes","short_term_variations","seasonal_period","regime_changes","pairwise_similarity","global_trend","persistence","long_range_dependence"],"validation_requirements":["Cross-check with alternative descriptions to confirm the match"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=traffic_hourly; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[288]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<candidates>
A) This series demonstrates a complex multi-phase behavior: initial growth to around 35, followed by decline and stabilization near 15, then dramatic rise to peak values around 50.
B) The data shows consistent cyclical patterns with values fluctuating between 1-10, punctuated by dramatic spikes exceeding 20, suggesting a recurring seasonal or operational pattern.
C) This time series exhibits regular periodic oscillations with occasional sharp spikes, maintaining relatively low baseline values around 2-3 with periodic peaks reaching up to 21.
D) The time series displays high variability with frequent fluctuations between 5-18, including periods of constant values and irregular spikes, suggesting unstable or noisy underlying processes.
</candidates>

Produce the TaskEvidence JSON for role=matching.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the series exhibits significant localized events, abrupt changes, short-term variations, a daily cycle (seasonality), and some form of anti-persistent behavior with long-range dependencies. The observed characteristics suggest frequent fluctuations but also a regular seasonal pattern with occasional sharp increases.",
  "role": "matching",
  "hypothesis": "The series fits best with an option that captures its key behaviors: periodic fluctuations, seasonality, and sharp spikes.",
  "evidence": ["The series shows 20 peaks and troughs as localized events.", "There are 48 sign changes indicating abrupt changes.", "Maximum local standard deviation of 6.19 indicates significant short-term variations.", "A dominant period of 24 hours suggests daily seasonality.", "Regime changes are identified at various points.", "The Hurst exponent analysis suggests anti-persistent behavior.", "Autocorrelation analysis identifies lagged correlations extending over multiple lags, indicative of long-range dependencies."],
  "candidate_preference": "C",
  "confidence": 1.0,
  "tool_calls": [],
  "cited_tool_call_ids": ["short:step1", "short:step2", "short:step3", "medium:step1", "medium:step2", "long:step1", "long:step2", "long:step3"],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "Localized events exist in the series.",
      "evidence": [
        {
          "type": "change_location",
          "value": 20,
          "provenance": "tool",
          "ref": "short:step1",
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are abrupt changes in the series.",
      "evidence": [
        {
          "type": "abrupt_changes",
          "value": 48,
          "provenance": "tool",
          "ref": "short:step2",
          "call_id": "short:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Short-term variations are present in the series.",
      "evidence": [
        {
          "type": "short_term_variations",
          "value": 6.19,
          "provenance": "tool",
          "ref": "short:step3",
          "call_id": "short:step3"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Seasonal patterns exist within the series.",
      "evidence": [
        {
          "type": "seasonal_period",
          "value": 24.0,
          "provenance": "tool",
          "ref": "medium:step1",
          "call_id": "medium:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "Regime changes occur within the series.",
      "evidence": [
        {
          "type": "regime_changes",
          "value": [161, 171, 172, 173, 174],
          "provenance": "tool",
          "ref": "medium:step2",
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There is a discernible global trend in the series.",
      "evidence": [
        {
          "type": "global_trend",
          "value": "-0.0562",
          "provenance": "tool",
          "ref": "long:step1",
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The series exhibits anti-persistent behavior over time.",
      "evidence": [
        {
          "type": "persistence",
          "value": "anti_persistent",
          "provenance": "tool",
          "ref": "long:step2",
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There are long-range dependencies in the series.",
      "evidence": [
        {
          "type": "long_range_dependence",
          "value": "-0.2793934356481875",
          "provenance": "tool",
          "ref": "long:step3",
          "call_id": "long:step3"
        }
     
```

## Integration — `integration`

tokens prompt=2016 completion=303 latency=11.15s

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
A) This series demonstrates a complex multi-phase behavior: initial growth to around 35, followed by decline and stabilization near 15, then dramatic rise to peak values around 50.
B) The data shows consistent cyclical patterns with values fluctuating between 1-10, punctuated by dramatic spikes exceeding 20, suggesting a recurring seasonal or operational pattern.
C) This time series exhibits regular periodic oscillations with occasional sharp spikes, maintaining relatively low baseline values around 2-3 with periodic peaks reaching up to 21.
D) The time series displays high variability with frequent fluctuations between 5-18, including periods of constant values and irregular spikes, suggesting unstable or noisy underlying processes.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Select the best description for the provided univariate time series data among four given options.",
  "question_type": "choice",
  "required_output": "Choose the best description from the candidates.",
  "success_criteria": [
    "Accurate identification of key features",
    "Robust alignment with a single descriptive statement",
    "Consistent validation across scales"
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Identify any localized events, abrupt changes, and short-term variations in the series.",
      "required_measurements": [
        "change_location",
        "abrupt_changes",
        "short_term_variations"
      ]
    },
    {
      "agent": "homo:medium",
      "objective": "Detect patterns such as cycles, steps, and repeated regimes within the series.",
      "required_measurements": [
        "seasonal_period",
        "regime_changes",
        "pairwise_similarity"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Analyze the overall structure, trends, and long-term dependencies of the series.",
      "required_measurements": [
        "global_trend",
        "persistence",
        "long_range_dependence"
      ]
    },
    {
      "agent": "hetero:matching",
      "objective": "Match the observed characteristics of the time series to the most accurate description among the given candidates based on identified features.",
      "required_measurements": [
        "change_location",
        "abrupt_changes",
        "short_term_variations",
        "seasonal_period",
        "regime_changes",
        "pairwise_similarity",
        "global_trend",
        "persistence"
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
          "value": 40,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "abrupt_changes",
          "value": 48,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "short_term_variations",
          "value": 6.19,
          "trusted": true
        }
      ],
      "coverage": {
        "change_location": "tool_supported",
        "abrupt_changes": "tool_supported",
        "short_term_variations": "tool_supported"
      },
      "summary": "20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations."
    },
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "seasonal_period",
          "value": 24.0,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "regime_changes",
          "value": [
            161,
            171,
            172,
            173,
            174
          ],
          "trusted": true
        },
        {
          "series_index": null,
          "type": "pairwise_similarity",
          "value": "Pairwise similarity exists between different segments of the series.",
          "trusted": false
        }
      ],
      "coverage": {
        "seasonal_period": "tool_supported",
        "regime_changes": "tool_supported",
        "pairwise_similarity": "unresolved"
      },
      "summary": "Dominant period of 24 hours indicates daily cycles within the series. | Potential regime changes identified at various points in the data."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_trend",
          "value": "-0.0562",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "persistence",
          "value": "anti_persistent",
          "trusted": true
        },
        {
          "series_index": null,
          "type": "long_range_dependence",
          "value": "-0.2793934356481875",
          "trusted": true
        }
      ],
      "coverage": {
        "global_trend": "tool_supported",
        "persistence": "tool_supported",
        "long_range_dependence": "tool_supported"
      },
      "summary": "The series exhibits a vague downward global trend with a negative slope. | Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies. | Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."
    }
  },
  "conflicts": [],
  "summary": "20 peaks and troughs have been identified as localized events. There are 48 sign changes indicating potential abrupt changes. Maximum local standard deviation of 6.19 highlights the presence of short-term variations. Dominant period of 24 hours indicates daily cycles within the series. Potential regime changes identified at various points in the data. The series exhibits a vague downward global trend with a negative slope. Hurst exponent analysis suggests anti-persistent behavior with an indication of long-range dependencies. Autocorrelation analysis identifies lagged correlations extending over multiple lags, supporting long-range dependency observation."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "matching",
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
  "reasoning": "Based on the detailed analysis, the time series exhibits significant short-term variations and abrupt changes, consistent with a highly dynamic nature. It has a clear cyclical component with a seasonal period of 24 hours, indicating daily cycles. There are also notable shifts or regime changes. While the global trend is slightly negative, the anti-persistent behavior and long-range dependence suggest high variability rather than steady or predictable changes. Among the given options, C best matches this profile, capturing the essence of regular oscillations, baseline stability around low values, and occasional sharp spikes.",
  "answer": "C",
  "explanation": "Option C aligns well with the observed features of the time series, including regular periodic oscillations, occasional sharp spikes, and baseline values within a narrow range.",
  "confidence": 0.8,
  "conflicts": [],
  "cited_evidence": ["20 peaks and troughs have been identified as localized events.", "There are 48 sign changes indicating potential abrupt changes.", "Dominant period of 24 hours indicates daily cycles within the series.", "Potential regime changes identified at various points in the data.", "The series exhibits a vague downward global trend with a negative slope."],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "C"
  }
}
```
