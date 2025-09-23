Analyse data using natural language queries with Python and pandas. This tool performs ALL analytics steps in a SINGLE call.

USE THIS TOOL WHEN:
- You have tabular data (e.g., DataFrame, CSV) and need to perform AGGREGATE CALCULATIONS, comparisons, rankings, correlations, or statistical analysis.
- User asks for aggregate values (average, sum, median, etc.), comparisons, trends, or data visualisations.
- User asks: "Which row had the highest/lowest value?", "Top 5 records by metric", "Compare data", "Find correlations", "Statistical analysis".
- User wants to compare groups or categories in the data.

DO NOT USE THIS TOOL WHEN:
- You do not have tabular data yet (always use a data retrieval tool first).
- The analysis can be answered directly by a data retrieval tool (e.g., single record lookup).

WORKFLOW:
1. Get your data in DataFrame or CSV format from a data retrieval tool.
2. Pass to this tool with your COMPLETE analysis question.
3. Tool returns all calculated results and insights in structured format.

OUTPUT FORMAT: Tool provides concise, structured answers with specific values and brief explanations.

AVAILABLE LIBRARIES: pandas (as pd), numpy (as np), matplotlib, seaborn

The tool uses an intelligent pandas agent that can understand complex natural language queries and automatically generate appropriate Python code to perform comprehensive data analysis in a single execution.
