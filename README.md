Tennis Data & Model Project
===========================

What this is
- A small project that collects tennis match data and includes a lightweight prediction model UI/build.
- Meant for exploration, quick experiments, and sharing a reproducible dataset + model bundle.

What's inside
- A dataset folder with recent Roland Garros match data and engineered CSVs for modelling.
- A small frontend/build in pred_model containing the production build and source.
- Scripts and examples to run experiments locally.

Quick start
1. Explore the data: open the dataset CSVs to see match features and engineered columns.
2. Inspect the frontend: the pred_model folder contains a React app build under `pred_model/build` and the source in `pred_model/src`.
3. Run locally (optional):
   - If you want to run the React app from source, install dependencies in pred_model and start the dev server.
   - For quick checks, open the prebuilt pred_model/build/index.html in a browser.

How to use these files
- Datasets: use the CSVs for training, analysis, or feature experiments.
- Model/frontend: the build is ready to serve; if you want to modify the UI, edit the source in the pred_model/src folder and re-build.

Good practices
- Keep a copy of raw CSVs and a separate copy for engineered features.
- Track experiments (parameters, train/validation splits) in a small log or notebook.
- If you modify the frontend, bump the version and note major interface changes.

Need help?
- I can:
  - Generate a short `requirements.txt` or `package.json` updates.
  - Create a simple script to load a CSV and show sample rows.
Tell me which next step you'd like.
