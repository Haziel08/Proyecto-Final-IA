import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, LabelEncoder


def cargar_dataset(ruta_csv="data/clientes_credito.csv"):
    return pd.read_csv(ruta_csv)


def entrenar_modelo(ruta_csv="data/clientes_credito.csv"):
    df = cargar_dataset(ruta_csv)

    columnas_x = [
        "Ingreso_Mensual",
        "Monto_Solicitado",
        "Gastos_Deuda",
        "Buro_Credito_Score",
        "Antiguedad_Laboral",
        "Vivienda",
        "Dependientes",
        "DTI"
    ]

    X = df[columnas_x]
    y = df["Dictamen_Final"]

    encoder_y = LabelEncoder()
    y_codificado = encoder_y.fit_transform(y)

    columnas_categoricas = ["Vivienda"]
    columnas_numericas = [
        "Ingreso_Mensual",
        "Monto_Solicitado",
        "Gastos_Deuda",
        "Buro_Credito_Score",
        "Antiguedad_Laboral",
        "Dependientes",
        "DTI"
    ]

    preprocesador = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), columnas_categoricas),
            ("num", "passthrough", columnas_numericas)
        ]
    )

    modelo = Pipeline(steps=[
        ("preprocesador", preprocesador),
        ("clasificador", RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced"
        ))
    ])

    modelo.fit(X, y_codificado)

    scores = cross_val_score(modelo, X, y_codificado, cv=5)

    return modelo, encoder_y, scores.mean(), columnas_x