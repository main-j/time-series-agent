# Agent IO summary: `Align:ts2caption_qa_120:33`

- Architecture pred: `D` (success=True)
- model_calls=16, tool_calls=7, latency=214.8s

## Planner — `planner`

tokens prompt=1132 completion=588 latency=20.84s

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
A) This time series displays multiple distinct plateau levels with abrupt transitions, featuring stable periods at different value ranges and a notable sharp peak around index 550.
B) This time series shows mostly zero values with sparse non-zero spikes occurring irregularly, exhibiting a highly sparse pattern with occasional brief activations concentrated in later indices.
C) This time series exhibits regular oscillatory behavior with consistent amplitude variations, showing cyclical patterns that maintain relatively stable periodicity throughout the entire sequence.
D) This time series demonstrates complex multi-level dynamics with several distinct phases, including high-amplitude oscillations, sustained plateaus, and gradual transitions between different operational states.
</candidates>

<metadata>
local_overall=overall; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the AgentPlan JSON now.

```

### OUTPUT

```
{
  "reasoning": "The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the structural characteristics and identifying patterns such as plateaus, peaks, sparsity, oscillations, and phase dynamics.",
  "task_summary": "Analyze the provided time series data to choose the correct descriptive statement from the candidates.",
  "target_output": "The correct description among the candidates A, B, C, or D that best fits the time series data.",
  "answer_type": "choice",
  "capability": "time series analysis",
  "scope": "overall",
  "univariate": true,
  "homo_assignments": [
    {
      "scale": "short",
      "objective": "Identify local features such as sudden transitions and peaks in the time series.",
      "required_measurements": ["step_level_count", "change_location"],
      "validation_requirements": ["verify consistency with potential abrupt transitions and peaks described in candidates"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "medium",
      "objective": "Detect any recurring patterns or cyclical behaviors present in the data.",
      "required_measurements": ["seasonal_period", "seasonal_strength"],
      "validation_requirements": ["confirm the regularity and stability of identified cycles"],
      "target_series": [1],
      "focus_intervals": []
    },
    {
      "scale": "long",
      "objective": "Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.",
      "required_measurements": ["global_trend", "persistence", "residual_noise_ratio"],
      "validation_requirements": ["evaluate if the observed trends align with the descriptions provided in candidates"],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "hetero_assignments": [
    {
      "role": "reasoning",
      "objective": "Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.",
      "required_measurements": ["step_level_count", "change_location", "seasonal_period", "seasonal_strength", "global_trend", "persistence", "residual_noise_ratio"],
      "validation_requirements": ["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],
      "target_series": [1],
      "focus_intervals": []
    }
  ],
  "success_criteria": ["Each agent produces findings consistent with the other, leading to the selection of one candidate based on the best fit for the overall characteristics of the time series."],
  "notes": "While 'overall' scope is specified, the analysis should cover all scales relevant to identifying features mentioned in the candidates."
}
```

## Homogeneous (short, s1s2) — `homogeneous:short:s1s2:m0`

tokens prompt=4162 completion=272 latency=10.82s

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
{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the structural characteristics and identifying patterns such as plateaus, peaks, sparsity, oscillations, and phase dynamics.","task_summary":"Analyze the provided time series data to choose the correct descriptive statement from the candidates.","target_output":"The correct description among the candidates A, B, C, or D that best fits the time series data.","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","required_measurements":["step_level_count","change_location","seasonal_period","seasonal_strength","global_trend","persistence","residual_noise_ratio"],"validation_requirements":["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each agent produces findings consistent with the other, leading to the selection of one candidate based on the best fit for the overall characteristics of the time series."],"notes":"While 'overall' scope is specified, the analysis should cover all scales relevant to identifying features mentioned in the candidates."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify local features such as sudden transitions and peaks in the time series. This requires detecting step levels and change locations, which can be done using appropriate tools.",
  "evidence_plan": {
    "objective": "Identify local features such as sudden transitions and peaks in the time series.",
    "claims_to_support": [
      {
        "claim": "The time series contains abrupt transitions and peaks.",
        "required_evidence": ["step_level_count", "change_location"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "short"
    },
    "validation_needs": ["verify consistency with potential abrupt transitions and peaks described in candidates"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "step_levels",
        "reason": "Counts discrete step/plateau levels which are relevant for detecting abrupt transitions.",
        "supports_evidence": ["step_level_count"]
      },
      {
        "tool": "change_points",
        "reason": "Localizes potential level/regime transitions which are relevant for detecting abrupt changes.",
        "supports_evidence": ["change_location"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (short, s3) — `homogeneous:short:s3:m0`

tokens prompt=728 completion=145 latency=5.18s

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
{"evidence_plan":{"objective":"Identify local features such as sudden transitions and peaks in the time series.","claims_to_support":[{"claim":"The time series contains abrupt transitions and peaks.","required_evidence":["step_level_count","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify consistency with potential abrupt transitions and peaks described in candidates"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels which are relevant for detecting abrupt transitions.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions which are relevant for detecting abrupt changes.","supports_evidence":["change_location"]}],"no_tool_decision":null},"reasoning":"The objective is to identify local features such as sudden transitions and peaks in the time series. This requires detecting step levels and change locations, which can be done using appropriate tools."}
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
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The objective is to identify local features such as sudden transitions and peaks in the time series. For this, we need to detect step levels and change points in the given time series. First, we use step_levels to count discrete step/plateau levels, then use change_points to localize potential level/regime transitions.",
  "workflow": [
    {
      "step": 1,
      "tool": "step_levels",
      "output_key": "series",
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

## Homogeneous (short, s4) — `homogeneous:short:s4:m0`

tokens prompt=854 completion=142 latency=5.10s

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
{"workflow":[{"step":1,"tool":"step_levels","output_key":"series","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify local features such as sudden transitions and peaks in the time series. For this, we need to detect step levels and change points in the given time series. First, we use step_levels to count discrete step/plateau levels, then use change_points to localize potential level/regime transitions."}
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
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "Identify local features such as sudden transitions and peaks in the time series by detecting step levels and change points. First, step_levels will be used on the series to count discrete step/plateau levels within the entire series. Then, change_points will be applied to identify potential abrupt transitions.",
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

## Homogeneous (short, s5) — `homogeneous:short:s5:m0`

tokens prompt=2239 completion=372 latency=13.70s

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
{"evidence_plan":{"objective":"Identify local features such as sudden transitions and peaks in the time series.","claims_to_support":[{"claim":"The time series contains abrupt transitions and peaks.","required_evidence":["step_level_count","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify consistency with potential abrupt transitions and peaks described in candidates"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels which are relevant for detecting abrupt transitions.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions which are relevant for detecting abrupt changes.","supports_evidence":["change_location"]}],"no_tool_decision":null},"reasoning":"The objective is to identify local features such as sudden transitions and peaks in the time series. This requires detecting step levels and change locations, which can be done using appropriate tools."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "short:step1",
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
      "n_unique_levels": 15,
      "n_plateau_runs": 182,
      "levels": [
        0.0,
        0.07,
        0.09,
        0.060000000000000046,
        0.03,
        0.04,
        0.23,
        0.29,
        0.27,
        0.1,
        0.13,
        0.17,
        0.2,
        0.37,
        0.3
      ],
      "plateau_runs": [
        0.0,
        0.07,
        0.0,
        0.09,
        0.060000000000000046,
        0.0,
        0.03,
        0.04,
        0.0,
        0.03,
        0.23,
        0.0,
        0.29,
        0.0,
        0.03,
        0.0,
        0.07,
        0.0,
        0.03,
        0.0,
        0.07,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.04,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.07,
        0.0,
        0.03,
        0.0,
        0.07,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.07,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.0,
        0.03,
        0.23,
        0.0,
        0.03,
        0.0,
        0.27,
        0.0,
        0.1,
        0.0,
        0.1,
        0.0,
        0.03,
        0.1,
        0.0,
        0.03,
        0.1,
        0.03,
        0.07,
        0.03
      ],
      "plateau_lengths": [
        6,
        1,
        1,
        1,
        66,
        37,
        1,
        1,
        15,
        1,
        1,
        19,
        1,
        62,
        1,
        4,
        1,
        4,
        1,
        7,
        1,
        3,
        1,
        1,
        1,
        1,
        1,
        1,
        1,
        3,
        1,
        5,
        1,
        1,
        1,
        3,
        2,
        20,
        3,
        1,
        1,
        3,
        1,
        1,
        1,
        1,
        6,
        2,
        9,
        1,
        15,
        1,
        5,
        1,
        30,
        1,
        39,
        1,
        6,
        1,
        9,
        1,
        1,
        13,
        3,
        2,
        1,
        25,
        1,
        19,
        1,
        16,
        1,
        1,
        12,
        2,
        1,
        1,
        1,
        1
      ],
      "tolerance": 0.0037
    },
    "error": null,
    "args_fingerprint": "9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"
  },
  {
    "call_id": "short:step2",
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
          "index": 614,
          "score": 0.1102777777777778
        },
        {
          "index": 613,
          "score": 0.10833333333333335
        },
        {
          "index": 615,
          "score": 0.10833333333333335
        },
        {
          "index": 616,
          "score": 0.10833333333333334
        },
        {
          "index": 617,
          "score": 0.10555555555555556
        }
      ]
    },
    "error": null,
    "args_fingerprint": "74c7edab88cb08cce8091a42bd61b720a5b8a3b5"
  }
]
</executed_steps>

<assignment>
{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=short.

```

### OUTPUT

```
{
  "reasoning": "The time series has been analyzed for step levels and change points. Step levels identified 15 unique levels and 182 plateau runs, suggesting several abrupt transitions. Change points have been localized at indices 614, 613, 615, 616, and 617 with scores indicating significant changes.",
  "scale": "short",
  "observations": ["The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs."],
  "evidence_intervals": ["Indices 614, 613, 615, 616, and 617 show significant changes in the time series."],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The time series contains abrupt transitions.",
      "evidence": [
        {
          "type": "change_location",
          "value": [614, 613, 615, 616, 617],
          "source_tool": "change_points",
          "call_id": "short:step2",
          "provenance": "tool"
        },
        {
          "type": "step_level_count",
          "value": 15,
          "source_tool": "step_levels",
          "call_id": "short:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "change_location"
    }
  ],
  "coverage": {"change_location": "tool_supported", "step_level_count": "tool_supported"},
  "unresolved_claims": []
}
```

## Homogeneous (medium, s1s2) — `homogeneous:medium:s1s2:m0`

tokens prompt=4159 completion=305 latency=12.00s

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
{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the structural characteristics and identifying patterns such as plateaus, peaks, sparsity, oscillations, and phase dynamics.","task_summary":"Analyze the provided time series data to choose the correct descriptive statement from the candidates.","target_output":"The correct description among the candidates A, B, C, or D that best fits the time series data.","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","required_measurements":["step_level_count","change_location","seasonal_period","seasonal_strength","global_trend","persistence","residual_noise_ratio"],"validation_requirements":["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each agent produces findings consistent with the other, leading to the selection of one candidate based on the best fit for the overall characteristics of the time series."],"notes":"While 'overall' scope is specified, the analysis should cover all scales relevant to identifying features mentioned in the candidates."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength.",
  "evidence_plan": {
    "objective": "Detect any recurring patterns or cyclical behaviors present in the data",
    "claims_to_support": [
      {
        "claim": "There is a seasonal pattern present in the data",
        "required_evidence": ["seasonal_period"]
      },
      {
        "claim": "The identified seasonal pattern has a certain strength",
        "required_evidence": ["seasonal_strength"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "medium"
    },
    "validation_needs": ["confirm the regularity and stability of identified cycles"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "seas_acf",
        "reason": "To identify the seasonal autocorrelation at a specified lag indicative of a seasonal pattern",
        "supports_evidence": ["seasonal_period"]
      },
      {
        "tool": "stl_strength",
        "reason": "To evaluate the strength of the detected seasonal pattern through seasonal decomposition",
        "supports_evidence": ["seasonal_strength"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (medium, s3) — `homogeneous:medium:s3:m0`

tokens prompt=804 completion=133 latency=4.78s

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
{"evidence_plan":{"objective":"Detect any recurring patterns or cyclical behaviors present in the data","claims_to_support":[{"claim":"There is a seasonal pattern present in the data","required_evidence":["seasonal_period"]},{"claim":"The identified seasonal pattern has a certain strength","required_evidence":["seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["confirm the regularity and stability of identified cycles"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"To identify the seasonal autocorrelation at a specified lag indicative of a seasonal pattern","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To evaluate the strength of the detected seasonal pattern through seasonal decomposition","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"reasoning":"The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- seas_acf
  inputs: series_window, lag
  outputs: seas_acf1, strength_hint
  often_combined_with: autocorr, stl_strength, fft_period
- stl_strength
  inputs: series, period(optional; omit→auto capped FFT)
  outputs: period, seasonal_strength, season_strength_bin, trend_strength
  depends: period often bound from fft_period.dominant_period when trusted
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength.",
  "workflow": [
    {
      "step": 1,
      "tool": "seas_acf",
      "output_key": "seas_acf1",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "stl_strength",
      "output_key": "seasonal_strength",
      "input_binding": {}
    }
  ]
}
```

## Homogeneous (medium, s4) — `homogeneous:medium:s4:m0`

tokens prompt=891 completion=233 latency=8.29s

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
{"workflow":[{"step":1,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{}}],"reasoning":"The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength."}
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
- stl_strength: STL seasonal/trend strength.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, period=optional positive int | omit → auto via fft_period; never null/placeholder strings}
  returns: {series=period, period_trusted, seasonal_strength, season_strength_bin, trend_strength}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "To meet the objective of detecting recurring patterns or cyclical behaviors in the univariate time series data, we need to identify the seasonal period and measure the strength of these seasonal patterns. We will first use the seas_acf tool to analyze the seasonal autocorrelation and get a hint on the seasonal strength. However, the workflow provided starts with stl_strength which requires an explicit period. Since the workflow does not follow the sequence where seas_acf is used to derive the period before feeding it into stl_strength, we adjust to a logical order starting with fft_period for finding the dominant seasonal period. Then, we pass this period into stl_strength to measure the seasonal strength.",
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

tokens prompt=1134 completion=253 latency=9.06s

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
{"evidence_plan":{"objective":"Detect any recurring patterns or cyclical behaviors present in the data","claims_to_support":[{"claim":"There is a seasonal pattern present in the data","required_evidence":["seasonal_period"]},{"claim":"The identified seasonal pattern has a certain strength","required_evidence":["seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["confirm the regularity and stability of identified cycles"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"To identify the seasonal autocorrelation at a specified lag indicative of a seasonal pattern","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To evaluate the strength of the detected seasonal pattern through seasonal decomposition","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"reasoning":"The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength."}
</evidence_capability_plan>

<executed_steps>
[
  {
    "call_id": "medium:step1",
    "step": 1,
    "tool_name": "seas_acf",
    "arguments": {},
    "resolved_arguments": {},
    "success": false,
    "data": {},
    "error": "seas_acf requires lag/m/frequency (e.g. 26 for weekly half-year)",
    "args_fingerprint": ""
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
      "series_index": 1
    },
    "success": true,
    "data": {
      "series_index": 1,
      "start": null,
      "end": null,
      "period": 65,
      "period_trusted": true,
      "period_source": "auto_fft_capped",
      "seasonal_strength": 0.0,
      "season_strength_bin": "none",
      "trend_strength": 0.03813522289604454,
      "metric_definition": "seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong",
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "34827fb2e16888e8e2671517f14e31426613297a"
  }
]
</executed_steps>

<assignment>
{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=medium.

```

### OUTPUT

```
{
  "reasoning": "The objective was to detect any recurring patterns or cyclical behaviors in the data, particularly focusing on the seasonal pattern and its strength. The stl_strength tool was successfully executed, providing information about the seasonal strength of the time series data.",
  "scale": "medium",
  "observations": ["The analysis confirms there is no significant seasonal pattern present in the data.", "The seasonal strength is measured at 0.0, indicating no discernible seasonality."],
  "evidence_intervals": [],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "There is no significant seasonal pattern present in the data",
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

## Homogeneous (long, s1s2) — `homogeneous:long:s1s2:m0`

tokens prompt=4176 completion=429 latency=16.57s

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
{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the structural characteristics and identifying patterns such as plateaus, peaks, sparsity, oscillations, and phase dynamics.","task_summary":"Analyze the provided time series data to choose the correct descriptive statement from the candidates.","target_output":"The correct description among the candidates A, B, C, or D that best fits the time series data.","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","required_measurements":["step_level_count","change_location","seasonal_period","seasonal_strength","global_trend","persistence","residual_noise_ratio"],"validation_requirements":["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each agent produces findings consistent with the other, leading to the selection of one candidate based on the best fit for the overall characteristics of the time series."],"notes":"While 'overall' scope is specified, the analysis should cover all scales relevant to identifying features mentioned in the candidates."}
</plan_context>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the EvidenceCapabilityPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios.",
  "evidence_plan": {
    "objective": "Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.",
    "claims_to_support": [
      {
        "claim": "The series shows a global trend over the long term.",
        "required_evidence": ["global_trend"]
      },
      {
        "claim": "The series demonstrates persistence or lack thereof.",
        "required_evidence": ["persistence"]
      },
      {
        "claim": "The residual noise strength relative to the series variance provides insight into complexity.",
        "required_evidence": ["residual_noise_ratio"]
      }
    ],
    "analysis_scope": {
      "target_series": [1],
      "focus_intervals": [],
      "scale": "long"
    },
    "validation_needs": ["evaluate if the observed trends align with the descriptions provided in candidates"]
  },
  "capability_selection": {
    "selected_tools": [
      {
        "tool": "segment_trend",
        "reason": "To measure the global trend over the long term by estimating the linear slope and direction.",
        "supports_evidence": ["global_trend"]
      },
      {
        "tool": "hurst_exponent",
        "reason": "To gauge the persistence or absence of it by estimating the Hurst exponent, providing insights into the series's self-similar behavior and long-term memory.",
        "supports_evidence": ["persistence"]
      },
      {
        "tool": "noise_decomposition",
        "reason": "To calculate the residual noise ratio, giving a sense of the complexity of the series by comparing the variance of the residual noise to the total variance.",
        "supports_evidence": ["residual_noise_ratio"]
      }
    ],
    "no_tool_decision": null
  }
}
```

## Homogeneous (long, s3) — `homogeneous:long:s3:m0`

tokens prompt=884 completion=182 latency=6.51s

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
{"evidence_plan":{"objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","claims_to_support":[{"claim":"The series shows a global trend over the long term.","required_evidence":["global_trend"]},{"claim":"The series demonstrates persistence or lack thereof.","required_evidence":["persistence"]},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","required_evidence":["residual_noise_ratio"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["evaluate if the observed trends align with the descriptions provided in candidates"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the global trend over the long term by estimating the linear slope and direction.","supports_evidence":["global_trend"]},{"tool":"hurst_exponent","reason":"To gauge the persistence or absence of it by estimating the Hurst exponent, providing insights into the series's self-similar behavior and long-term memory.","supports_evidence":["persistence"]},{"tool":"noise_decomposition","reason":"To calculate the residual noise ratio, giving a sense of the complexity of the series by comparing the variance of the residual noise to the total variance.","supports_evidence":["residual_noise_ratio"]}],"no_tool_decision":null},"reasoning":"The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios."}
</evidence_capability_plan>

<io_concepts>
Tool IO concepts (for workflow planning; not full argument schemas):

- segment_trend
  inputs: series_index, start, end
  outputs: series
- hurst_exponent
  inputs: series
  outputs: hurst, persistence_hint
- noise_decomposition
  inputs: series, period(optional)
  outputs: noise_ratio, noise_level, noise_type_hint
</io_concepts>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ToolWorkflow JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios.",
  "workflow": [
    {
      "step": 1,
      "tool": "segment_trend",
      "output_key": "trend_series",
      "input_binding": {}
    },
    {
      "step": 2,
      "tool": "hurst_exponent",
      "output_key": "persistence_info",
      "input_binding": {"series": "$step1.series"}
    },
    {
      "step": 3,
      "tool": "noise_decomposition",
      "output_key": "noise_info",
      "input_binding": {"series": "$step1.series"}
    }
  ]
}
```

## Homogeneous (long, s4) — `homogeneous:long:s4:m0`

tokens prompt=1038 completion=166 latency=5.99s

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
{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_info","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_info","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios."}
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
- hurst_exponent: Estimate Hurst exponent via hurst.compute_Hc(kind=random_walk), matching MMTS label generation. Returns persistence_hint at 0.45/0.55.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index}
  returns: {series=Hurst via compute_Hc, persistence_hint, estimator metadata}
- noise_decomposition: MMTS-style residual noise strength: Var(residual)/Var(series) after STL (conservative vs high-pass), with bins none/low/medium/high at 0.1/0.33/0.66 and a heuristic noise_type_hint.
  args: {series_index=int|list|'all'|str (1-based; default=all if multi), start=optional inclusive start index, end=optional inclusive end index, period=optional int}
  returns: {series=noise_ratio=Var(resid)/Var(series), noise_level bins none/low/medium/high, type hint}
</tool_invocation_spec>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

<assignment>
{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}
</assignment>

Produce the InvocationPlan JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios.",
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
      "tool": "noise_decomposition",
      "args": {
        "series_index": 1
      }
    }
  ]
}
```

## Homogeneous (long, s5) — `homogeneous:long:s5:m0`

tokens prompt=1891 completion=594 latency=21.50s

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
{"evidence_plan":{"objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","claims_to_support":[{"claim":"The series shows a global trend over the long term.","required_evidence":["global_trend"]},{"claim":"The series demonstrates persistence or lack thereof.","required_evidence":["persistence"]},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","required_evidence":["residual_noise_ratio"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["evaluate if the observed trends align with the descriptions provided in candidates"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the global trend over the long term by estimating the linear slope and direction.","supports_evidence":["global_trend"]},{"tool":"hurst_exponent","reason":"To gauge the persistence or absence of it by estimating the Hurst exponent, providing insights into the series's self-similar behavior and long-term memory.","supports_evidence":["persistence"]},{"tool":"noise_decomposition","reason":"To calculate the residual noise ratio, giving a sense of the complexity of the series by comparing the variance of the residual noise to the total variance.","supports_evidence":["residual_noise_ratio"]}],"no_tool_decision":null},"reasoning":"The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios."}
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
      "slope": 0.0001808066759388039,
      "direction": "upward",
      "direction_class": "vague",
      "trend_method": "endpoint",
      "mean": 0.023152777777777776,
      "std": 0.04964797179538216,
      "start_value": 0.0,
      "end_value": 0.13
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
      "hurst": 0.272970366926496,
      "persistence_hint": "anti_persistent",
      "estimator": "hurst.compute_Hc",
      "metric_definition": "MMTS-compatible R/S Hurst via hurst.compute_Hc",
      "n_effective": 720,
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
    "tool_name": "noise_decomposition",
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
      "period": 65,
      "residual_std": 0.04940306036570875,
      "residual_rmse": 0.0503157258974057,
      "series_std": 0.04964797179538216,
      "residual_var": 0.0024406623734978625,
      "series_var": 0.0024649211033950626,
      "stl_noise_ratio": 0.9901584148661206,
      "highpass_noise_ratio": 0.6007384554970204,
      "noise_ratio": 0.9901584148661206,
      "noise_level": "high",
      "metric_definition": "Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high",
      "estimator": "STL_residual_variance_ratio",
      "seasonal_strength": 0.0,
      "trend_strength": 0.03813522289604454,
      "noise_type_hint": "quantization_like",
      "acf_lag1": 0.44965105792480026,
      "warnings": []
    },
    "error": null,
    "args_fingerprint": "909854aa026a467bebd5ecbc24b3a7475254db9c"
  }
]
</executed_steps>

<assignment>
{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>

Produce the ScaleObservation JSON for scale=long.

```

### OUTPUT

```
{
  "reasoning": "The analysis includes evaluating the global trend, persistence, and residual noise ratio to assess the overall behavior and long-range structure of the series. The segment_trend tool indicates a slight upward trend with a vague classification due to the low slope value. The hurst_exponent analysis reveals anti-persistence, suggesting the series lacks memory. Lastly, the noise_decomposition tool calculates a high residual noise ratio, indicating significant residual noise.",
  "scale": "long",
  "observations": ["The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope.", "The series does not show long-term memory, as indicated by an anti-persistent behavior.", "There is significant residual noise, suggesting a high level of complexity within the series."],
  "evidence_intervals": ["long:step1", "long:step2", "long:step3"],
  "confidence": 0.0,
  "tool_calls": [],
  "structured_observations": [
    {
      "claim": "The series shows a global trend over the long term.",
      "evidence": [
        {
          "type": "global_trend",
          "value": 0.0001808066759388039,
          "source_tool": "segment_trend",
          "call_id": "long:step1",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "global_trend"
    },
    {
      "claim": "The series demonstrates persistence or lack thereof.",
      "evidence": [
        {
          "type": "persistence",
          "value": 0.272970366926496,
          "source_tool": "hurst_exponent",
          "call_id": "long:step2",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "persistence"
    },
    {
      "claim": "The residual noise strength relative to the series variance provides insight into complexity.",
      "evidence": [
        {
          "type": "residual_noise_ratio",
          "value": 0.9901584148661206,
          "source_tool": "noise_decomposition",
          "call_id": "long:step3",
          "provenance": "tool"
        }
      ],
      "confidence": "tool_supported",
      "maps_to_measurement": "residual_noise_ratio"
    }
  ],
  "coverage": {"global_trend": "tool_supported", "persistence": "tool_supported", "residual_noise_ratio": "tool_supported"},
  "unresolved_claims": []
}
```

## Heterogeneous (reasoning, s1s2) — `heterogeneous:reasoning:s1s2:m0`

tokens prompt=11645 completion=593 latency=26.68s

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
{"role":"reasoning","objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","required_measurements":["step_level_count","change_location","seasonal_period","seasonal_strength","global_trend","persistence","residual_noise_ratio"],"validation_requirements":["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],"target_series":[1],"focus_intervals":[]}
</assignment>

<plan_context>
{"reasoning":"The task requires selecting the most accurate description for the given univariate time series data among four candidate statements. It necessitates examining the structural characteristics and identifying patterns such as plateaus, peaks, sparsity, oscillations, and phase dynamics.","task_summary":"Analyze the provided time series data to choose the correct descriptive statement from the candidates.","target_output":"The correct description among the candidates A, B, C, or D that best fits the time series data.","answer_type":"choice","capability":"time series analysis","scope":"overall","univariate":true,"homo_assignments":[{"scale":"short","objective":"Identify local features such as sudden transitions and peaks in the time series.","required_measurements":["step_level_count","change_location"],"validation_requirements":["verify consistency with potential abrupt transitions and peaks described in candidates"],"target_series":[1],"focus_intervals":[]},{"scale":"medium","objective":"Detect any recurring patterns or cyclical behaviors present in the data.","required_measurements":["seasonal_period","seasonal_strength"],"validation_requirements":["confirm the regularity and stability of identified cycles"],"target_series":[1],"focus_intervals":[]},{"scale":"long","objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","required_measurements":["global_trend","persistence","residual_noise_ratio"],"validation_requirements":["evaluate if the observed trends align with the descriptions provided in candidates"],"target_series":[1],"focus_intervals":[]}],"hetero_assignments":[{"role":"reasoning","objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","required_measurements":["step_level_count","change_location","seasonal_period","seasonal_strength","global_trend","persistence","residual_noise_ratio"],"validation_requirements":["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],"target_series":[1],"focus_intervals":[]}],"scales":["short","medium","long"],"heterogeneous_agents":["reasoning"],"success_criteria":["Each agent produces findings consistent with the other, leading to the selection of one candidate based on the best fit for the overall characteristics of the time series."],"notes":"While 'overall' scope is specified, the analysis should cover all scales relevant to identifying features mentioned in the candidates."}
</plan_context>

<task_summary>
Analyze the provided time series data to choose the correct descriptive statement from the candidates.
</task_summary>

<temporal_profile>
{"short":{"reasoning":"The time series has been analyzed for step levels and change points. Step levels identified 15 unique levels and 182 plateau runs, suggesting several abrupt transitions. Change points have been localized at indices 614, 613, 615, 616, and 617 with scores indicating significant changes.","scale":"short","observations":["The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs."],"evidence_intervals":["Indices 614, 613, 615, 616, and 617 show significant changes in the time series."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 15, \"n_plateau_runs\": 182, \"levels\": [0.0, 0.07, 0.09, 0.060000000000000046, 0.03, 0.04, 0.23, 0.29, 0.27, 0.1, 0.13, 0.17, 0.2, 0.37, 0.3], \"plateau_runs\": [0.0, 0.07, 0.0, 0.09, 0.060000000000000046, 0.0, 0.03, 0.04, 0.0, 0.03, 0.23, 0.0, 0.29, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.04, 0.0, 0.03, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.07, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.23, 0.0, 0.03, 0.0, 0.27, 0.0, 0.1, 0.0, 0.1, 0.0, 0.03, 0.1, 0.0, 0.03, 0.1, 0.03, 0.07, 0.03], \"plateau_lengths\": [6, 1, 1, 1, 66, 37, 1, 1, 15, 1, 1, 19, 1, 62, 1, 4, 1, 4, 1, 7, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 5, 1, 1, 1, 3, 2, 20, 3, 1, 1, 3, 1, 1, 1, 1, 6, 2, 9, 1, 15, 1, 5, 1, 30, 1, 39, 1, 6, 1, 9, 1, 1, 13, 3, 2, 1, 25, 1, 19, 1, 16, 1, 1, 12, 2, 1, 1, 1, 1], \"tolerance\": 0.0037}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 614, \"score\": 0.1102777777777778}, {\"index\": 613, \"score\": 0.10833333333333335}, {\"index\": 615, \"score\": 0.10833333333333335}, {\"index\": 616, \"score\": 0.10833333333333334}, {\"index\": 617, \"score\": 0.10555555555555556}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify local features such as sudden transitions and peaks in the time series.","claims_to_support":[{"claim":"The time series contains abrupt transitions and peaks.","required_evidence":["step_level_count","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify consistency with potential abrupt transitions and peaks described in candidates"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels which are relevant for detecting abrupt transitions.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions which are relevant for detecting abrupt changes.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"series","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify local features such as sudden transitions and peaks in the time series. For this, we need to detect step levels and change points in the given time series. First, we use step_levels to count discrete step/plateau levels, then use change_points to localize potential level/regime transitions."},"structured_observations":[{"claim":"The time series contains abrupt transitions.","evidence":[{"type":"change_location","value":[614,613,615,616,617],"source_tool":"change_points","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"step_level_count","value":15,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"}],"coverage":{"change_location":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":15,"n_plateau_runs":182,"levels":[0.0,0.07,0.09,0.060000000000000046,0.03,0.04,0.23,0.29,0.27,0.1,0.13,0.17,0.2,0.37,0.3],"plateau_runs":[0.0,0.07,0.0,0.09,0.060000000000000046,0.0,0.03,0.04,0.0,0.03,0.23,0.0,0.29,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.04,0.0,0.03,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.07,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.23,0.0,0.03,0.0,0.27,0.0,0.1,0.0,0.1,0.0,0.03,0.1,0.0,0.03,0.1,0.03,0.07,0.03],"plateau_lengths":[6,1,1,1,66,37,1,1,15,1,1,19,1,62,1,4,1,4,1,7,1,3,1,1,1,1,1,1,1,3,1,5,1,1,1,3,2,20,3,1,1,3,1,1,1,1,6,2,9,1,15,1,5,1,30,1,39,1,6,1,9,1,1,13,3,2,1,25,1,19,1,16,1,1,12,2,1,1,1,1],"tolerance":0.0037},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"short:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":614,"score":0.1102777777777778},{"index":613,"score":0.10833333333333335},{"index":615,"score":0.10833333333333335},{"index":616,"score":0.10833333333333334},{"index":617,"score":0.10555555555555556}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to detect any recurring patterns or cyclical behaviors in the data, particularly focusing on the seasonal pattern and its strength. The stl_strength tool was successfully executed, providing information about the seasonal strength of the time series data.","scale":"medium","observations":["The analysis confirms there is no significant seasonal pattern present in the data.","The seasonal strength is measured at 0.0, indicating no discernible seasonality."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"seas_acf\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": false, \"data\": {}, \"error\": \"seas_acf requires lag/m/frequency (e.g. 26 for weekly half-year)\", \"args_fingerprint\": \"\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 65, \"period_trusted\": true, \"period_source\": \"auto_fft_capped\", \"seasonal_strength\": 0.0, \"season_strength_bin\": \"none\", \"trend_strength\": 0.03813522289604454, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"34827fb2e16888e8e2671517f14e31426613297a\"}"],"evidence_plan":{"objective":"Detect any recurring patterns or cyclical behaviors present in the data","claims_to_support":[{"claim":"There is a seasonal pattern present in the data","required_evidence":["seasonal_period"]},{"claim":"The identified seasonal pattern has a certain strength","required_evidence":["seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["confirm the regularity and stability of identified cycles"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"To identify the seasonal autocorrelation at a specified lag indicative of a seasonal pattern","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To evaluate the strength of the detected seasonal pattern through seasonal decomposition","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{}}],"reasoning":"The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength."},"structured_observations":[{"claim":"There is no significant seasonal pattern present in the data","evidence":[{"type":"seasonal_strength","value":0.0,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"}],"coverage":{"seasonal_strength":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"seas_acf","arguments":{},"resolved_arguments":{},"success":false,"data":{},"error":"seas_acf requires lag/m/frequency (e.g. 26 for weekly half-year)","args_fingerprint":""},{"call_id":"medium:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":65,"period_trusted":true,"period_source":"auto_fft_capped","seasonal_strength":0.0,"season_strength_bin":"none","trend_strength":0.03813522289604454,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":[]},"error":null,"args_fingerprint":"34827fb2e16888e8e2671517f14e31426613297a"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes evaluating the global trend, persistence, and residual noise ratio to assess the overall behavior and long-range structure of the series. The segment_trend tool indicates a slight upward trend with a vague classification due to the low slope value. The hurst_exponent analysis reveals anti-persistence, suggesting the series lacks memory. Lastly, the noise_decomposition tool calculates a high residual noise ratio, indicating significant residual noise.","scale":"long","observations":["The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope.","The series does not show long-term memory, as indicated by an anti-persistent behavior.","There is significant residual noise, suggesting a high level of complexity within the series."],"evidence_intervals":["long:step1","long:step2","long:step3"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 0.0001808066759388039, \"direction\": \"upward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 0.023152777777777776, \"std\": 0.04964797179538216, \"start_value\": 0.0, \"end_value\": 0.13}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.272970366926496, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 720, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 65, \"residual_std\": 0.04940306036570875, \"residual_rmse\": 0.0503157258974057, \"series_std\": 0.04964797179538216, \"residual_var\": 0.0024406623734978625, \"series_var\": 0.0024649211033950626, \"stl_noise_ratio\": 0.9901584148661206, \"highpass_noise_ratio\": 0.6007384554970204, \"noise_ratio\": 0.9901584148661206, \"noise_level\": \"high\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.0, \"trend_strength\": 0.03813522289604454, \"noise_type_hint\": \"quantization_like\", \"acf_lag1\": 0.44965105792480026, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"909854aa026a467bebd5ecbc24b3a7475254db9c\"}"],"evidence_plan":{"objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","claims_to_support":[{"claim":"The series shows a global trend over the long term.","required_evidence":["global_trend"]},{"claim":"The series demonstrates persistence or lack thereof.","required_evidence":["persistence"]},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","required_evidence":["residual_noise_ratio"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["evaluate if the observed trends align with the descriptions provided in candidates"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the global trend over the long term by estimating the linear slope and direction.","supports_evidence":["global_trend"]},{"tool":"hurst_exponent","reason":"To gauge the persistence or absence of it by estimating the Hurst exponent, providing insights into the series's self-similar behavior and long-term memory.","supports_evidence":["persistence"]},{"tool":"noise_decomposition","reason":"To calculate the residual noise ratio, giving a sense of the complexity of the series by comparing the variance of the residual noise to the total variance.","supports_evidence":["residual_noise_ratio"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_info","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_info","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios."},"structured_observations":[{"claim":"The series shows a global trend over the long term.","evidence":[{"type":"global_trend","value":0.0001808066759388039,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series demonstrates persistence or lack thereof.","evidence":[{"type":"persistence","value":0.272970366926496,"source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","evidence":[{"type":"residual_noise_ratio","value":0.9901584148661206,"source_tool":"noise_decomposition","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"residual_noise_ratio"}],"coverage":{"global_trend":"tool_supported","persistence":"tool_supported","residual_noise_ratio":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":0.0001808066759388039,"direction":"upward","direction_class":"vague","trend_method":"endpoint","mean":0.023152777777777776,"std":0.04964797179538216,"start_value":0.0,"end_value":0.13},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.272970366926496,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":720,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step3","step":3,"tool_name":"noise_decomposition","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":65,"residual_std":0.04940306036570875,"residual_rmse":0.0503157258974057,"series_std":0.04964797179538216,"residual_var":0.0024406623734978625,"series_var":0.0024649211033950626,"stl_noise_ratio":0.9901584148661206,"highpass_noise_ratio":0.6007384554970204,"noise_ratio":0.9901584148661206,"noise_level":"high","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.0,"trend_strength":0.03813522289604454,"noise_type_hint":"quantization_like","acf_lag1":0.44965105792480026,"warnings":[]},"error":null,"args_fingerprint":"909854aa026a467bebd5ecbc24b3a7475254db9c"}],"skipped_stages":[]},"conflicts":[],"summary":"The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs. The analysis confirms there is no significant seasonal pattern present in the data. The seasonal strength is measured at 0.0, indicating no discernible seasonality. The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope. The series does not show long-term memory, as indicated by an anti-persistent behavior. There is significant residual noise, suggesting a high level of complexity within the series.","structured_by_scale":{"short":[{"claim":"The time series contains abrupt transitions.","evidence":[{"type":"change_location","value":[614,613,615,616,617],"source_tool":"change_points","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"step_level_count","value":15,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"}],"medium":[{"claim":"There is no significant seasonal pattern present in the data","evidence":[{"type":"seasonal_strength","value":0.0,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"}],"long":[{"claim":"The series shows a global trend over the long term.","evidence":[{"type":"global_trend","value":0.0001808066759388039,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series demonstrates persistence or lack thereof.","evidence":[{"type":"persistence","value":0.272970366926496,"source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","evidence":[{"type":"residual_noise_ratio","value":0.9901584148661206,"source_tool":"noise_decomposition","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"residual_noise_ratio"}]}}
</temporal_profile>

<prior_task_evidence>
(none)
</prior_task_evidence>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>



Produce the EvidenceCapabilityPlan JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "The current assignment focuses on comparing the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics. The previous temporal profile and evidence plan provide detailed observations regarding step levels, change points, seasonal patterns, global trends, persistence, and residual noise. Given these details, the task is to validate the coherence between detected structural elements and the statements made in the candidate descriptions. Since the necessary evidence (step_level_count, change_location, seasonal_period, seasonal_strength, global_trend, persistence, residual_noise_ratio) has already been gathered through prior steps, the main requirement now is to ensure that the findings align with the provided descriptions.",
  "evidence_plan": {
    "objective": "Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.",
    "claims_to_support": [
      {"claim": "The series contains abrupt transitions and peaks.", "required_evidence": ["step_level_count", "change_location"]},
      {"claim": "There is no significant seasonal pattern present in the data.", "required_evidence": ["seasonal_period", "seasonal_strength"]},
      {"claim": "The series shows a global trend over the long term.", "required_evidence": ["global_trend"]},
      {"claim": "The series demonstrates persistence or lack thereof.", "required_evidence": ["persistence"]},
      {"claim": "The residual noise strength relative to the series variance provides insight into complexity.", "required_evidence": ["residual_noise_ratio"]}
    ],
    "analysis_scope": {"target_series": [1], "role": "reasoning"},
    "validation_needs": ["Ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."]
  },
  "capability_selection": {
    "selected_tools": [],
    "no_tool_decision": {
      "skip_tools": true,
      "reason": "All required measurements have been gathered previously in the short, medium, and long scales, and there are no gaps or additional requirements for tool application.",
      "evidence_sources": [{"type": "upstream_observation", "ref": "temporal_profile", "field": "short.change_location"}, {"type": "upstream_observation", "ref": "temporal_profile", "field": "short.step_level_count"}, {"type": "upstream_observation", "ref": "temporal_profile", "field": "medium.seasonal_strength"}, {"type": "upstream_observation", "ref": "temporal_profile", "field": "long.global_trend"}, {"type": "upstream_observation", "ref": "temporal_profile", "field": "long.persistence"}, {"type": "upstream_observation", "ref": "temporal_profile", "field": "long.residual_noise_ratio"}]
    }
  }
}
```

## Heterogeneous (reasoning, s5) — `heterogeneous:reasoning:s5:m0`

tokens prompt=8412 completion=901 latency=36.95s

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
{"evidence_plan":{"objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","claims_to_support":[{"claim":"The series contains abrupt transitions and peaks.","required_evidence":["step_level_count","change_location"]},{"claim":"There is no significant seasonal pattern present in the data.","required_evidence":["seasonal_period","seasonal_strength"]},{"claim":"The series shows a global trend over the long term.","required_evidence":["global_trend"]},{"claim":"The series demonstrates persistence or lack thereof.","required_evidence":["persistence"]},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","required_evidence":["residual_noise_ratio"]}],"analysis_scope":{"target_series":[1],"role":"reasoning"},"validation_needs":["Ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."]},"capability_selection":{"selected_tools":[],"no_tool_decision":{"skip_tools":true,"reason":"All required measurements have been gathered previously in the short, medium, and long scales, and there are no gaps or additional requirements for tool application.","evidence_sources":[{"type":"upstream_observation","ref":"temporal_profile","field":"short.change_location"},{"type":"upstream_observation","ref":"temporal_profile","field":"short.step_level_count"},{"type":"upstream_observation","ref":"temporal_profile","field":"medium.seasonal_strength"},{"type":"upstream_observation","ref":"temporal_profile","field":"long.global_trend"},{"type":"upstream_observation","ref":"temporal_profile","field":"long.persistence"},{"type":"upstream_observation","ref":"temporal_profile","field":"long.residual_noise_ratio"}]}},"reasoning":"The current assignment focuses on comparing the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics. The previous temporal profile and evidence plan provide detailed observations regarding step levels, change points, seasonal patterns, global trends, persistence, and residual noise. Given these details, the task is to validate the coherence between detected structural elements and the statements made in the candidate descriptions. Since the necessary evidence (step_level_count, change_location, seasonal_period, seasonal_strength, global_trend, persistence, residual_noise_ratio) has already been gathered through prior steps, the main requirement now is to ensure that the findings align with the provided descriptions."}
</evidence_capability_plan>

<executed_steps>
(none)
</executed_steps>

<temporal_profile>
{"short":{"reasoning":"The time series has been analyzed for step levels and change points. Step levels identified 15 unique levels and 182 plateau runs, suggesting several abrupt transitions. Change points have been localized at indices 614, 613, 615, 616, and 617 with scores indicating significant changes.","scale":"short","observations":["The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs."],"evidence_intervals":["Indices 614, 613, 615, 616, and 617 show significant changes in the time series."],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"short:step1\", \"step\": 1, \"tool_name\": \"step_levels\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"n_unique_levels\": 15, \"n_plateau_runs\": 182, \"levels\": [0.0, 0.07, 0.09, 0.060000000000000046, 0.03, 0.04, 0.23, 0.29, 0.27, 0.1, 0.13, 0.17, 0.2, 0.37, 0.3], \"plateau_runs\": [0.0, 0.07, 0.0, 0.09, 0.060000000000000046, 0.0, 0.03, 0.04, 0.0, 0.03, 0.23, 0.0, 0.29, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.04, 0.0, 0.03, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.07, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.07, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.0, 0.03, 0.23, 0.0, 0.03, 0.0, 0.27, 0.0, 0.1, 0.0, 0.1, 0.0, 0.03, 0.1, 0.0, 0.03, 0.1, 0.03, 0.07, 0.03], \"plateau_lengths\": [6, 1, 1, 1, 66, 37, 1, 1, 15, 1, 1, 19, 1, 62, 1, 4, 1, 4, 1, 7, 1, 3, 1, 1, 1, 1, 1, 1, 1, 3, 1, 5, 1, 1, 1, 3, 2, 20, 3, 1, 1, 3, 1, 1, 1, 1, 6, 2, 9, 1, 15, 1, 5, 1, 30, 1, 39, 1, 6, 1, 9, 1, 1, 13, 3, 2, 1, 25, 1, 19, 1, 16, 1, 1, 12, 2, 1, 1, 1, 1], \"tolerance\": 0.0037}, \"error\": null, \"args_fingerprint\": \"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4\"}","{\"call_id\": \"short:step2\", \"step\": 2, \"tool_name\": \"change_points\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"candidates\": [{\"index\": 614, \"score\": 0.1102777777777778}, {\"index\": 613, \"score\": 0.10833333333333335}, {\"index\": 615, \"score\": 0.10833333333333335}, {\"index\": 616, \"score\": 0.10833333333333334}, {\"index\": 617, \"score\": 0.10555555555555556}]}, \"error\": null, \"args_fingerprint\": \"74c7edab88cb08cce8091a42bd61b720a5b8a3b5\"}"],"evidence_plan":{"objective":"Identify local features such as sudden transitions and peaks in the time series.","claims_to_support":[{"claim":"The time series contains abrupt transitions and peaks.","required_evidence":["step_level_count","change_location"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"short"},"validation_needs":["verify consistency with potential abrupt transitions and peaks described in candidates"]},"capability_selection":{"selected_tools":[{"tool":"step_levels","reason":"Counts discrete step/plateau levels which are relevant for detecting abrupt transitions.","supports_evidence":["step_level_count"]},{"tool":"change_points","reason":"Localizes potential level/regime transitions which are relevant for detecting abrupt changes.","supports_evidence":["change_location"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"step_levels","output_key":"series","input_binding":{}},{"step":2,"tool":"change_points","output_key":"series","input_binding":{}}],"reasoning":"The objective is to identify local features such as sudden transitions and peaks in the time series. For this, we need to detect step levels and change points in the given time series. First, we use step_levels to count discrete step/plateau levels, then use change_points to localize potential level/regime transitions."},"structured_observations":[{"claim":"The time series contains abrupt transitions.","evidence":[{"type":"change_location","value":[614,613,615,616,617],"source_tool":"change_points","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"step_level_count","value":15,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"}],"coverage":{"change_location":"tool_supported","step_level_count":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"short:step1","step":1,"tool_name":"step_levels","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"n_unique_levels":15,"n_plateau_runs":182,"levels":[0.0,0.07,0.09,0.060000000000000046,0.03,0.04,0.23,0.29,0.27,0.1,0.13,0.17,0.2,0.37,0.3],"plateau_runs":[0.0,0.07,0.0,0.09,0.060000000000000046,0.0,0.03,0.04,0.0,0.03,0.23,0.0,0.29,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.04,0.0,0.03,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.07,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.07,0.0,0.03,0.0,0.03,0.0,0.03,0.0,0.03,0.23,0.0,0.03,0.0,0.27,0.0,0.1,0.0,0.1,0.0,0.03,0.1,0.0,0.03,0.1,0.03,0.07,0.03],"plateau_lengths":[6,1,1,1,66,37,1,1,15,1,1,19,1,62,1,4,1,4,1,7,1,3,1,1,1,1,1,1,1,3,1,5,1,1,1,3,2,20,3,1,1,3,1,1,1,1,6,2,9,1,15,1,5,1,30,1,39,1,6,1,9,1,1,13,3,2,1,25,1,19,1,16,1,1,12,2,1,1,1,1],"tolerance":0.0037},"error":null,"args_fingerprint":"9085edb4b07f5d90a11fdac4a3741b2e86abb4c4"},{"call_id":"short:step2","step":2,"tool_name":"change_points","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"candidates":[{"index":614,"score":0.1102777777777778},{"index":613,"score":0.10833333333333335},{"index":615,"score":0.10833333333333335},{"index":616,"score":0.10833333333333334},{"index":617,"score":0.10555555555555556}]},"error":null,"args_fingerprint":"74c7edab88cb08cce8091a42bd61b720a5b8a3b5"}],"skipped_stages":[]},"medium":{"reasoning":"The objective was to detect any recurring patterns or cyclical behaviors in the data, particularly focusing on the seasonal pattern and its strength. The stl_strength tool was successfully executed, providing information about the seasonal strength of the time series data.","scale":"medium","observations":["The analysis confirms there is no significant seasonal pattern present in the data.","The seasonal strength is measured at 0.0, indicating no discernible seasonality."],"evidence_intervals":[],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"medium:step1\", \"step\": 1, \"tool_name\": \"seas_acf\", \"arguments\": {}, \"resolved_arguments\": {}, \"success\": false, \"data\": {}, \"error\": \"seas_acf requires lag/m/frequency (e.g. 26 for weekly half-year)\", \"args_fingerprint\": \"\"}","{\"call_id\": \"medium:step2\", \"step\": 2, \"tool_name\": \"stl_strength\", \"arguments\": {\"series_index\": 1, \"period\": \"$step1.dominant_period\"}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 65, \"period_trusted\": true, \"period_source\": \"auto_fft_capped\", \"seasonal_strength\": 0.0, \"season_strength_bin\": \"none\", \"trend_strength\": 0.03813522289604454, \"metric_definition\": \"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong\", \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"34827fb2e16888e8e2671517f14e31426613297a\"}"],"evidence_plan":{"objective":"Detect any recurring patterns or cyclical behaviors present in the data","claims_to_support":[{"claim":"There is a seasonal pattern present in the data","required_evidence":["seasonal_period"]},{"claim":"The identified seasonal pattern has a certain strength","required_evidence":["seasonal_strength"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"medium"},"validation_needs":["confirm the regularity and stability of identified cycles"]},"capability_selection":{"selected_tools":[{"tool":"seas_acf","reason":"To identify the seasonal autocorrelation at a specified lag indicative of a seasonal pattern","supports_evidence":["seasonal_period"]},{"tool":"stl_strength","reason":"To evaluate the strength of the detected seasonal pattern through seasonal decomposition","supports_evidence":["seasonal_strength"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"seas_acf","output_key":"seas_acf1","input_binding":{}},{"step":2,"tool":"stl_strength","output_key":"seasonal_strength","input_binding":{}}],"reasoning":"The objective at the medium scale is to detect any recurring patterns or cyclical behaviors present in the data, specifically focusing on seasonal patterns and their strength. This involves identifying the seasonal period and measuring the seasonal strength."},"structured_observations":[{"claim":"There is no significant seasonal pattern present in the data","evidence":[{"type":"seasonal_strength","value":0.0,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"}],"coverage":{"seasonal_strength":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"medium:step1","step":1,"tool_name":"seas_acf","arguments":{},"resolved_arguments":{},"success":false,"data":{},"error":"seas_acf requires lag/m/frequency (e.g. 26 for weekly half-year)","args_fingerprint":""},{"call_id":"medium:step2","step":2,"tool_name":"stl_strength","arguments":{"series_index":1,"period":"$step1.dominant_period"},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":65,"period_trusted":true,"period_source":"auto_fft_capped","seasonal_strength":0.0,"season_strength_bin":"none","trend_strength":0.03813522289604454,"metric_definition":"seasonal_strength=1-Var(resid)/Var(seasonal+resid) (STL proxy for MMTS 1-Var(n)/Var(s+n)); bins none<0.2, weak<0.5, moderate<=0.8, else strong","warnings":[]},"error":null,"args_fingerprint":"34827fb2e16888e8e2671517f14e31426613297a"}],"skipped_stages":[]},"long":{"reasoning":"The analysis includes evaluating the global trend, persistence, and residual noise ratio to assess the overall behavior and long-range structure of the series. The segment_trend tool indicates a slight upward trend with a vague classification due to the low slope value. The hurst_exponent analysis reveals anti-persistence, suggesting the series lacks memory. Lastly, the noise_decomposition tool calculates a high residual noise ratio, indicating significant residual noise.","scale":"long","observations":["The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope.","The series does not show long-term memory, as indicated by an anti-persistent behavior.","There is significant residual noise, suggesting a high level of complexity within the series."],"evidence_intervals":["long:step1","long:step2","long:step3"],"confidence":0.0,"tool_calls":[],"tool_summaries":["{\"call_id\": \"long:step1\", \"step\": 1, \"tool_name\": \"segment_trend\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"slope\": 0.0001808066759388039, \"direction\": \"upward\", \"direction_class\": \"vague\", \"trend_method\": \"endpoint\", \"mean\": 0.023152777777777776, \"std\": 0.04964797179538216, \"start_value\": 0.0, \"end_value\": 0.13}, \"error\": null, \"args_fingerprint\": \"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c\"}","{\"call_id\": \"long:step2\", \"step\": 2, \"tool_name\": \"hurst_exponent\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"hurst\": 0.272970366926496, \"persistence_hint\": \"anti_persistent\", \"estimator\": \"hurst.compute_Hc\", \"metric_definition\": \"MMTS-compatible R/S Hurst via hurst.compute_Hc\", \"n_effective\": 720, \"kind\": \"random_walk\", \"simplified\": true, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd\"}","{\"call_id\": \"long:step3\", \"step\": 3, \"tool_name\": \"noise_decomposition\", \"arguments\": {\"series_index\": 1}, \"resolved_arguments\": {\"series_index\": 1}, \"success\": true, \"data\": {\"series_index\": 1, \"start\": null, \"end\": null, \"period\": 65, \"residual_std\": 0.04940306036570875, \"residual_rmse\": 0.0503157258974057, \"series_std\": 0.04964797179538216, \"residual_var\": 0.0024406623734978625, \"series_var\": 0.0024649211033950626, \"stl_noise_ratio\": 0.9901584148661206, \"highpass_noise_ratio\": 0.6007384554970204, \"noise_ratio\": 0.9901584148661206, \"noise_level\": \"high\", \"metric_definition\": \"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high\", \"estimator\": \"STL_residual_variance_ratio\", \"seasonal_strength\": 0.0, \"trend_strength\": 0.03813522289604454, \"noise_type_hint\": \"quantization_like\", \"acf_lag1\": 0.44965105792480026, \"warnings\": []}, \"error\": null, \"args_fingerprint\": \"909854aa026a467bebd5ecbc24b3a7475254db9c\"}"],"evidence_plan":{"objective":"Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.","claims_to_support":[{"claim":"The series shows a global trend over the long term.","required_evidence":["global_trend"]},{"claim":"The series demonstrates persistence or lack thereof.","required_evidence":["persistence"]},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","required_evidence":["residual_noise_ratio"]}],"analysis_scope":{"target_series":[1],"focus_intervals":[],"scale":"long"},"validation_needs":["evaluate if the observed trends align with the descriptions provided in candidates"]},"capability_selection":{"selected_tools":[{"tool":"segment_trend","reason":"To measure the global trend over the long term by estimating the linear slope and direction.","supports_evidence":["global_trend"]},{"tool":"hurst_exponent","reason":"To gauge the persistence or absence of it by estimating the Hurst exponent, providing insights into the series's self-similar behavior and long-term memory.","supports_evidence":["persistence"]},{"tool":"noise_decomposition","reason":"To calculate the residual noise ratio, giving a sense of the complexity of the series by comparing the variance of the residual noise to the total variance.","supports_evidence":["residual_noise_ratio"]}],"no_tool_decision":null},"workflow":{"workflow":[{"step":1,"tool":"segment_trend","output_key":"trend_series","input_binding":{}},{"step":2,"tool":"hurst_exponent","output_key":"persistence_info","input_binding":{"series":"$step1.series"}},{"step":3,"tool":"noise_decomposition","output_key":"noise_info","input_binding":{"series":"$step1.series"}}],"reasoning":"The objective for the long-scale analysis is to assess the overall behavior and long-range structure of the series, specifically focusing on stability, growth trends, and complexity. This involves measuring global trends, persistence, and residual noise ratios."},"structured_observations":[{"claim":"The series shows a global trend over the long term.","evidence":[{"type":"global_trend","value":0.0001808066759388039,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series demonstrates persistence or lack thereof.","evidence":[{"type":"persistence","value":0.272970366926496,"source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","evidence":[{"type":"residual_noise_ratio","value":0.9901584148661206,"source_tool":"noise_decomposition","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"residual_noise_ratio"}],"coverage":{"global_trend":"tool_supported","persistence":"tool_supported","residual_noise_ratio":"tool_supported"},"unresolved_claims":[],"executed_steps":[{"call_id":"long:step1","step":1,"tool_name":"segment_trend","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"slope":0.0001808066759388039,"direction":"upward","direction_class":"vague","trend_method":"endpoint","mean":0.023152777777777776,"std":0.04964797179538216,"start_value":0.0,"end_value":0.13},"error":null,"args_fingerprint":"dbb507103e8bfb8f4233a57c0f4bc8ada18d233c"},{"call_id":"long:step2","step":2,"tool_name":"hurst_exponent","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"hurst":0.272970366926496,"persistence_hint":"anti_persistent","estimator":"hurst.compute_Hc","metric_definition":"MMTS-compatible R/S Hurst via hurst.compute_Hc","n_effective":720,"kind":"random_walk","simplified":true,"warnings":[]},"error":null,"args_fingerprint":"5e211acd7a4e5a1f7a809775804d850b4fdbe4bd"},{"call_id":"long:step3","step":3,"tool_name":"noise_decomposition","arguments":{"series_index":1},"resolved_arguments":{"series_index":1},"success":true,"data":{"series_index":1,"start":null,"end":null,"period":65,"residual_std":0.04940306036570875,"residual_rmse":0.0503157258974057,"series_std":0.04964797179538216,"residual_var":0.0024406623734978625,"series_var":0.0024649211033950626,"stl_noise_ratio":0.9901584148661206,"highpass_noise_ratio":0.6007384554970204,"noise_ratio":0.9901584148661206,"noise_level":"high","metric_definition":"Var(residual)/Var(series) (conservative max of STL residual and high-pass); thresholds none<0.1, low<0.33, medium<=0.66, else high","estimator":"STL_residual_variance_ratio","seasonal_strength":0.0,"trend_strength":0.03813522289604454,"noise_type_hint":"quantization_like","acf_lag1":0.44965105792480026,"warnings":[]},"error":null,"args_fingerprint":"909854aa026a467bebd5ecbc24b3a7475254db9c"}],"skipped_stages":[]},"conflicts":[],"summary":"The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs. The analysis confirms there is no significant seasonal pattern present in the data. The seasonal strength is measured at 0.0, indicating no discernible seasonality. The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope. The series does not show long-term memory, as indicated by an anti-persistent behavior. There is significant residual noise, suggesting a high level of complexity within the series.","structured_by_scale":{"short":[{"claim":"The time series contains abrupt transitions.","evidence":[{"type":"change_location","value":[614,613,615,616,617],"source_tool":"change_points","call_id":"short:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null},{"type":"step_level_count","value":15,"source_tool":"step_levels","call_id":"short:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"change_location"}],"medium":[{"claim":"There is no significant seasonal pattern present in the data","evidence":[{"type":"seasonal_strength","value":0.0,"source_tool":"stl_strength","call_id":"medium:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"seasonal_strength"}],"long":[{"claim":"The series shows a global trend over the long term.","evidence":[{"type":"global_trend","value":0.0001808066759388039,"source_tool":"segment_trend","call_id":"long:step1","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"global_trend"},{"claim":"The series demonstrates persistence or lack thereof.","evidence":[{"type":"persistence","value":0.272970366926496,"source_tool":"hurst_exponent","call_id":"long:step2","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"persistence"},{"claim":"The residual noise strength relative to the series variance provides insight into complexity.","evidence":[{"type":"residual_noise_ratio","value":0.9901584148661206,"source_tool":"noise_decomposition","call_id":"long:step3","provenance":"tool","ref":null,"series_index":null,"args_fingerprint":null}],"confidence":"tool_supported","maps_to_measurement":"residual_noise_ratio"}]}}
</temporal_profile>

<assignment>
{"role":"reasoning","objective":"Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.","required_measurements":["step_level_count","change_location","seasonal_period","seasonal_strength","global_trend","persistence","residual_noise_ratio"],"validation_requirements":["ensure coherence between structural elements detected and statements about plateau levels, sparsity, oscillations, etc."],"target_series":[1],"focus_intervals":[]}
</assignment>

<metadata>
subset=Align; local_overall=overall; task_type=caption; domain=alibaba; qa_type=a multiple choice question; question_type=choice; is_univariate=True; n_series=1; series_lengths=[720]; index_base=0; series_truncated=False; focus_intervals=[]; query_series_index=1; candidate_series_indices=[]; align_direction=ts2caption; option_to_series={}
</metadata>



Produce the TaskEvidence JSON for role=reasoning.

```

### OUTPUT

```
{
  "reasoning": "Based on the temporal profile evidence, the series exhibits abrupt transitions and peaks, lacks significant seasonal patterns, shows a minor upward trend over the long term, demonstrates anti-persistent behavior, and has high residual noise.",
  "role": "reasoning",
  "hypothesis": "Candidate B accurately matches the observed characteristics of the series.",
  "evidence": [
    "The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs.",
    "Analysis confirms there is no significant seasonal pattern present in the data with a seasonal strength measured at 0.0, indicating no discernible seasonality.",
    "The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope, and does not show long-term memory, as indicated by an anti-persistent behavior.",
    "There is significant residual noise, suggesting a high level of complexity within the series."
  ],
  "candidate_preference": null,
  "confidence": 0.0,
  "tool_calls": [],
  "cited_tool_call_ids": [
    "short:step1",
    "short:step2",
    "medium:step2",
    "long:step1",
    "long:step2",
    "long:step3"
  ],
  "executed_tools": [],
  "tool_summaries": [],
  "reasoning_claims": [
    {
      "claim": "The series contains abrupt transitions and peaks.",
      "evidence": [
        {
          "type": "change_location",
          "value": [614, 613, 615, 616, 617],
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step2"
        },
        {
          "type": "step_level_count",
          "value": 15,
          "provenance": "tool",
          "ref": null,
          "call_id": "short:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "There is no significant seasonal pattern present in the data.",
      "evidence": [
        {
          "type": "seasonal_strength",
          "value": 0.0,
          "provenance": "tool",
          "ref": null,
          "call_id": "medium:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The series shows a global trend over the long term.",
      "evidence": [
        {
          "type": "global_trend",
          "value": 0.0001808066759388039,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step1"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The series demonstrates persistence or lack thereof.",
      "evidence": [
        {
          "type": "persistence",
          "value": 0.272970366926496,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step2"
        }
      ],
      "confidence": "tool_supported"
    },
    {
      "claim": "The residual noise strength relative to the series variance provides insight into complexity.",
      "evidence": [
        {
          "type": "residual_noise_ratio",
          "value": 0.9901584148661206,
          "provenance": "tool",
          "ref": null,
          "call_id": "long:step3"
        }
      ],
      "confidence": "tool_supported"
    }
  ],
  "coverage": {
    "change_location": "tool_supported",
    "step_level_count": "tool_supported",
    "seasonal_strength": "tool_supported",
    "global_trend": "tool_supported",
    "persistence": "tool_supported",
    "residual_noise_ratio": "tool_supported"
  },
  "unresolved_claims": []
}
```

## Integration — `integration`

tokens prompt=2083 completion=260 latency=9.66s

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
A) This time series displays multiple distinct plateau levels with abrupt transitions, featuring stable periods at different value ranges and a notable sharp peak around index 550.
B) This time series shows mostly zero values with sparse non-zero spikes occurring irregularly, exhibiting a highly sparse pattern with occasional brief activations concentrated in later indices.
C) This time series exhibits regular oscillatory behavior with consistent amplitude variations, showing cyclical patterns that maintain relatively stable periodicity throughout the entire sequence.
D) This time series demonstrates complex multi-level dynamics with several distinct phases, including high-amplitude oscillations, sustained plateaus, and gradual transitions between different operational states.
</candidates>

<question_type>
choice
</question_type>

<planner_intent>
{
  "goal": "Analyze the provided time series data to choose the correct descriptive statement from the candidates.",
  "question_type": "choice",
  "required_output": "The correct description among the candidates A, B, C, or D that best fits the time series data.",
  "success_criteria": [
    "Each agent produces findings consistent with the other, leading to the selection of one candidate based on the best fit for the overall characteristics of the time series."
  ],
  "assignments_brief": [
    {
      "agent": "homo:short",
      "objective": "Identify local features such as sudden transitions and peaks in the time series.",
      "required_measurements": [
        "step_level_count",
        "change_location"
      ]
    },
    {
      "agent": "homo:medium",
      "objective": "Detect any recurring patterns or cyclical behaviors present in the data.",
      "required_measurements": [
        "seasonal_period",
        "seasonal_strength"
      ]
    },
    {
      "agent": "homo:long",
      "objective": "Assess the overall behavior and long-range structure of the series, such as stability, growth trends, or complexity.",
      "required_measurements": [
        "global_trend",
        "persistence",
        "residual_noise_ratio"
      ]
    },
    {
      "agent": "hetero:reasoning",
      "objective": "Compare the gathered measurements against the four candidate descriptions to determine which one accurately matches the observed characteristics.",
      "required_measurements": [
        "step_level_count",
        "change_location",
        "seasonal_period",
        "seasonal_strength",
        "global_trend",
        "persistence",
        "residual_noise_ratio"
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
          "value": [
            614,
            613,
            615,
            616,
            617
          ],
          "trusted": true
        },
        {
          "series_index": null,
          "type": "step_level_count",
          "value": 15,
          "trusted": true
        }
      ],
      "coverage": {
        "change_location": "tool_supported",
        "step_level_count": "tool_supported"
      },
      "summary": "The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs."
    },
    "medium": {
      "states": [
        {
          "series_index": null,
          "type": "seasonal_strength",
          "value": 0.0,
          "trusted": true
        }
      ],
      "coverage": {
        "seasonal_strength": "tool_supported"
      },
      "summary": "The analysis confirms there is no significant seasonal pattern present in the data. | The seasonal strength is measured at 0.0, indicating no discernible seasonality."
    },
    "long": {
      "states": [
        {
          "series_index": null,
          "type": "global_trend",
          "value": 0.0001808066759388039,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "persistence",
          "value": 0.272970366926496,
          "trusted": true
        },
        {
          "series_index": null,
          "type": "residual_noise_ratio",
          "value": 0.9901584148661206,
          "trusted": true
        }
      ],
      "coverage": {
        "global_trend": "tool_supported",
        "persistence": "tool_supported",
        "residual_noise_ratio": "tool_supported"
      },
      "summary": "The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope. | The series does not show long-term memory, as indicated by an anti-persistent behavior. | There is significant residual noise, suggesting a high level of complexity within the series."
    }
  },
  "conflicts": [],
  "summary": "The time series includes multiple distinct step levels and abrupt transitions, evidenced by change point locations and plateau runs. The analysis confirms there is no significant seasonal pattern present in the data. The seasonal strength is measured at 0.0, indicating no discernible seasonality. The series exhibits a minor upward trend over the long term but with vague certainty due to the shallow slope. The series does not show long-term memory, as indicated by an anti-persistent behavior. There is significant residual noise, suggesting a high level of complexity within the series."
}
</homo_perception>

<heter_reasoning>
{
  "roles": [
    {
      "role": "reasoning",
      "hypothesis": "Candidate B accurately matches the observed characteristics of the series.",
      "reasoning_chain": [
        "The series contains abrupt transitions and peaks.",
        "change_location=[614, 613, 615, 616, 617]",
        "step_level_count=15",
        "There is no significant seasonal pattern present in the data.",
        "seasonal_strength=0.0",
        "The series shows a global trend over the long term.",
        "global_trend=0.0001808066759388039",
        "The series demonstrates persistence or lack thereof.",
        "persistence=0.272970366926496",
        "The residual noise strength relative to the series variance provides insight into complexity.",
        "residual_noise_ratio=0.9901584148661206"
      ],
      "candidate_preference": null,
      "confidence": 0.5,
      "grounded": true,
      "grounded_in": [
        "change_location",
        "step_level_count",
        "seasonal_strength",
        "global_trend",
        "persistence",
        "residual_noise_ratio"
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
  "reasoning": "Heter reasoning aligns with multiple distinct step levels and abrupt transitions as detected by homo short scale analysis, absence of seasonal pattern as per medium scale analysis, and indication of complexity through persistence and residual noise ratio from long scale analysis. However, there's a conflict with hypothesized preference for B given that the description should account for multiple phases, plateaus, and transitions as well as potential sparse or regular oscillatory behavior.",
  "answer": "D",
  "explanation": "The description D best fits the observed characteristics, including multiple distinct phases, plateaus, and transitions, and it encompasses the anti-persistence behavior and high residual noise indicative of complexity.",
  "confidence": 0.5,
  "conflicts": ["Heter reasoning misaligned with candidate B which did not reflect the comprehensive dynamic complexity as seen in the series"],
  "cited_evidence": ["change_location", "step_level_count", "seasonal_strength", "global_trend", "persistence", "residual_noise_ratio"],
  "decision_trace": {
    "metric": null,
    "observed_value": null,
    "intervals_from_question": [],
    "matched_label": null,
    "matched_letter": "D"
  }
}
```
