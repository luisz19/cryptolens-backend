import joblib
import pandas as pd
import numpy as np

# Caminho relativo aos arquivos salvos
MODEL_PATH = "app/ml/model.joblib"
FEATURES_PATH = "app/ml/model_features.joblib"

# Carregar o modelo e as features
model = joblib.load(MODEL_PATH)
model_features = joblib.load(FEATURES_PATH)

def predict_crypto_movement(input_data: pd.DataFrame):
    """
    Recebe dados de criptomoedas e retorna a previsão de movimento.
    input_data: DataFrame com as mesmas features usadas no treino.
    """
    # Garantir que as colunas estão na ordem certa
    input_data = input_data[model_features]

    # Fazer previsões (1 = alta, 0 = queda)
    preds = model.predict(input_data)

    return preds


def predict_proba_up(input_data: pd.DataFrame):
    """
    Retorna a probabilidade prevista de alta (classe 1) para cada linha.
    Se o modelo não suportar predict_proba, retorna NaN.
    """
    X = input_data[model_features]
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)
        classes = getattr(model, "classes_", None)
        if classes is not None and 1 in list(classes):
            idx = list(classes).index(1)
        else:
            # Fallback: utiliza a última coluna como "classe positiva"
            idx = probs.shape[1] - 1
        return probs[:, idx]
    # Sem suporte a predict_proba
    return np.full(len(X), np.nan)


def recommend_cryptos(user_risk: str, crypto_data: pd.DataFrame, allowed_symbols: set[str] | None = None):
    """
    Gera recomendações com base no perfil de risco do usuário e previsões do modelo.
    """

    # Trabalhar em uma cópia e consolidar em 1 linha por símbolo (última data)
    df = crypto_data.copy()
    # Normaliza símbolo base (ex.: BTCUSDT -> BTC) para cruzar com base cadastrada
    if "symbol" in df.columns:
        df["symbol_base"] = df["symbol"].astype(str).str.replace(r"USDT$", "", regex=True)
    else:
        df["symbol_base"] = None

    # Filtra para somente as moedas cadastradas, se informado
    if allowed_symbols:
        df = df[df["symbol_base"].isin(allowed_symbols)]

    # Se não houver dados suficientes após o filtro, retorna vazio
    if df.empty:
        return []
    # Prepara datas para cálculos por janela
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    else:
        df["date"] = pd.NaT

    # Consolidar uma linha por símbolo para passagem no modelo (último registro)
    df_last = df.sort_values(["symbol_base", "date"]).groupby("symbol_base", as_index=False).tail(1)

    # Métrica de risco baseada em 7 dias: usar volatility_7 normalizada por preço (close)
    # Isso alinha a janela de risco à das predições.
    if "volatility_7" in df_last.columns:
        if "close" in df_last.columns:
            risk_metric = df_last["volatility_7"].astype(float) / (df_last["close"].abs().astype(float) + 1e-9)
        else:
            # Sem close, usa a própria volatility_7 e normaliza por min-max no conjunto atual
            v = df_last["volatility_7"].astype(float)
            rng = float((v.max() - v.min()) or 1.0)
            risk_metric = (v - v.min()) / (rng + 1e-12)
    else:
        # Fallback para zero se coluna estiver ausente
        risk_metric = pd.Series([0.0] * len(df_last), index=df_last.index)

    # Quantis entre as moedas cadastradas
    q1 = risk_metric.quantile(0.33)
    q2 = risk_metric.quantile(0.66)

    def classify_from_value(val: float) -> str:
        if val <= q1:
            return "baixo"
        if val <= q2:
            return "moderado"
        return "alto"

    predictions = predict_crypto_movement(df_last)
    df_last["predicted_movement"] = predictions
    # Probabilidade de alta (classe 1), quando disponível
    try:
        proba_up = predict_proba_up(df_last)
        df_last["predicted_proba_up"] = proba_up
    except Exception:
        df_last["predicted_proba_up"] = np.nan

    # Classificar o risco da moeda baseado em volatilidade
    # Classificar risco usando volatilidade relativa (normalizada) para evitar tudo "alto"
    # Preferimos usar close como base; se não houver, caímos para min-max de volatility_7
    # Aplica classificação baseada na métrica de 7 dias
    df_last["_risk_metric_7d"] = risk_metric
    df_last["Risk_Level"] = df_last["_risk_metric_7d"].apply(classify_from_value)

    # Em vez de filtrar e limitar top 10, retornamos TODAS as moedas
    # e indicamos se elas são elegíveis para o perfil do usuário.
    if user_risk == "baixo":
        eligible_mask = df_last["Risk_Level"] == "baixo"
    elif user_risk == "moderado":
        eligible_mask = df_last["Risk_Level"].isin(["baixo", "moderado"])
    else:  # alto
        eligible_mask = pd.Series([True] * len(df_last), index=df_last.index)

    df_last["eligible_for_profile"] = eligible_mask

    # Selecionar colunas de saída com tolerância a ausência de algumas colunas
    out_cols = []
    # Preferimos expor 'symbol' como base cadastrado (ex.: BTC)
    if "symbol_base" in df_last.columns:
        df_last["symbol"] = df_last["symbol_base"]

    for c in ["symbol", "network", "Risk_Level", "predicted_movement", "predicted_proba_up", "eligible_for_profile"]:
        if c in df_last.columns:
            out_cols.append(c)

    result_df = df_last[out_cols]
    return result_df.to_dict(orient="records")
