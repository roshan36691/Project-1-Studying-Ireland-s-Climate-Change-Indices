from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
df_ireland = pd.read_csv(app_dir / "temperature.csv")
df_germany = pd.read_csv(app_dir / "GermanAnalysis.csv")
