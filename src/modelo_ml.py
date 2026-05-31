import pandas as pd  # importa pandas para la manipulación de datos en tablas
from sklearn.compose import ColumnTransformer  # importa ColumnTransformer para preprocesamiento de columnas
from sklearn.ensemble import RandomForestClassifier  # importa el clasificador Random Forest
from sklearn.model_selection import cross_val_score  # importa validación cruzada para evaluar el modelo
from sklearn.pipeline import Pipeline  # importa Pipeline para encadenar transformaciones y estimador
from sklearn.preprocessing import OneHotEncoder, LabelEncoder  # importa codificadores para variables categóricas y etiquetas


def cargar_dataset(ruta_csv="data/clientes_credito.csv"):
    return pd.read_csv(ruta_csv)  # carga el dataset desde un archivo CSV y retorna un DataFrame


def entrenar_modelo(ruta_csv="data/clientes_credito.csv"):
    df = cargar_dataset(ruta_csv)  # carga el dataset utilizando la función anterior

    columnas_x = [  # define las columnas de entrada que se usarán para el entrenamiento
        "Ingreso_Mensual",
        "Monto_Solicitado",
        "Gastos_Deuda",
        "Buro_Credito_Score",
        "Antiguedad_Laboral",
        "Vivienda",
        "Dependientes",
        "DTI"
    ]

    X = df[columnas_x]  # selecciona las características del dataset
    y = df["Dictamen_Final"]  # selecciona la columna objetivo del dataset

    encoder_y = LabelEncoder()  # crea un codificador para convertir etiquetas de texto en números
    y_codificado = encoder_y.fit_transform(y)  # ajusta y transforma la columna objetivo

    columnas_categoricas = ["Vivienda"]  # lista de columnas categóricas para transformar
    columnas_numericas = [  # lista de columnas numéricas que se mantienen sin cambios
        "Ingreso_Mensual",
        "Monto_Solicitado",
        "Gastos_Deuda",
        "Buro_Credito_Score",
        "Antiguedad_Laboral",
        "Dependientes",
        "DTI"
    ]

    preprocesador = ColumnTransformer(  # define el preprocesador de columnas
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), columnas_categoricas),  # codifica las columnas categóricas
            ("num", "passthrough", columnas_numericas)  # pasa las columnas numéricas sin cambios
        ]
    )

    modelo = Pipeline(steps=[  # crea un pipeline que aplica preprocesamiento y luego clasifica
        ("preprocesador", preprocesador),  # primer paso: transforma características
        ("clasificador", RandomForestClassifier(  # segundo paso: clasifica con Random Forest
            n_estimators=100,  # número de árboles en el bosque aleatorio
            random_state=42,  # semilla para reproducibilidad
            class_weight="balanced"  # ajusta pesos de clases automáticamente
        ))
    ])

    modelo.fit(X, y_codificado)  # entrena el pipeline con las características y las etiquetas codificadas

    scores = cross_val_score(modelo, X, y_codificado, cv=5)  # evalúa el modelo con validación cruzada de 5 pliegues

    return modelo, encoder_y, scores.mean(), columnas_x  # retorna el modelo entrenado, el codificador, la precisión promedio y las columnas usadas