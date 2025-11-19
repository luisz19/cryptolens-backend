import joblib
import pandas as pd
from pathlib import Path

# Caminho dos arquivos do modelo
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "improved_random_forest_model.joblib"
FEATURES_PATH = BASE_DIR / "models" / "model_features.joblib"

# Carregar modelo e features
model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)

def recommend_cryptos(risk_profile: str, risk_return_df: pd.DataFrame, predicted_movement_df: pd.DataFrame):
    """
    Gera recomendações de criptomoedas com base no perfil de risco do usuário.
    """

    # Definir critérios de risco — baseados na lógica do notebook
    risk_profiles_refined = {
        "Conservative": {"volatility_condition": "<=", "volatility_threshold": 0.5,
                         "return_condition": "<=", "return_threshold": 0.15},
        "Moderate": {"volatility_condition": "between", "volatility_threshold_low": 0.5,
                     "volatility_threshold_high": 1.0, "return_condition": "between",
                     "return_threshold_low": 0.15, "return_threshold_high": 0.25},
        "Aggressive": {"volatility_condition": ">", "volatility_threshold": 1.0,
                       "return_condition": ">", "return_threshold": 0.25}
    }

    if risk_profile not in risk_profiles_refined:
        raise ValueError("Invalid risk profile. Choose from 'Conservative', 'Moderate', 'Aggressive'.")

    criteria = risk_profiles_refined[risk_profile]

    # Filtragem baseada no perfil de risco
    df = risk_return_df.copy()
    if criteria["volatility_condition"] == "<=":
        df = df[df["annualized_volatility"] <= criteria["volatility_threshold"]]
    elif criteria["volatility_condition"] == ">":
        df = df[df["annualized_volatility"] > criteria["volatility_threshold"]]
    elif criteria["volatility_condition"] == "between":
        df = df[(df["annualized_volatility"] > criteria["volatility_threshold_low"]) &
                (df["annualized_volatility"] <= criteria["volatility_threshold_high"])]

    if criteria["return_condition"] == "<=":
        df = df[df["annualized_return"] <= criteria["return_threshold"]]
    elif criteria["return_condition"] == ">":
        df = df[df["annualized_return"] > criteria["return_threshold"]]
    elif criteria["return_condition"] == "between":
        df = df[(df["annualized_return"] > criteria["return_threshold_low"]) &
                (df["annualized_return"] <= criteria["return_threshold_high"])]

    # Previsões com o modelo
    X = df[model_features]
    predicted_risk = model.predict(X)

    df["predicted_risk_level"] = predicted_risk
    df["user_risk_profile"] = risk_profile

    # Ordenar e retornar top 10
    return df[["network", "annualized_return", "annualized_volatility", "predicted_risk_level"]].head(10).to_dict(orient="records")
