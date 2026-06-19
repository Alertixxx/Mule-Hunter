### Visualization Input Contract

Endpoint / File:

- nodes_viz.json
- fraud_explanations.json

Node fields:

- id: number
- color: "red" | "green"
- size: number
- height: number
- is_anomalous: 0 | 1

Behavior:

- Red nodes = anomalous (EIF)
- Edge highlight on node click
- Tooltip shows SHAP reasons

Output:

- WebGL rendered 3D graph
