### Template Structure

All 17 templates are stored in `template.json` as a list of JSON objects, with following fields:

- `category`: one of `trend`, `seasonality`, `noise`, or `basic`, indicating the aspect of the time series that the question targets.
- `question`: the full English question, which is instantiated with a concrete time series.
- `options` (optional): multiple-choice options when the question is formulated as a classification or categorical judgment task.
- `answer`: a placeholder to be filled with the ground-truth value or label computed from the time series (e.g., `{hurst:.2f}`, `{mean:.2f}`, `{PCT90:.2f}`).

Concretely, the templates are organized as:
- **3 trend templates**: questions about overall trend direction, persistence (via the Hurst exponent), and the sign/magnitude of the regression slope.
- **3 seasonality templates**: questions about the existence and length of periodic patterns, as well as the strength of seasonality.
- **2 noise templates**: questions about the noise level and related properties of the residual component.
- **9 basic templates**: questions about basic descriptive statistics of the time series, such as max/min, mean, range, median, standard deviation, and specific quantiles (e.g., 50th, 90th, and 99th percentiles).

Together with the generation script `../generate_question.py`, these templates define the exact procedure we use to construct synthetic TSQA instances for the MMTS-Base.