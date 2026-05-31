import pandas as pd
import collections
import collections.abc
# Parche de compatibilidad obligatorio para experta en Python 3.10+
collections.Mapping = collections.abc.Mapping

from experta import *
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datos_clientes import datos_clientes

# --- PIPELINE DE MACHINE LEARNING SUPERVISADO ---
def entrenar_modelo_ml():
    df = pd.DataFrame(datos_clientes)
    
    # Preparación de variables predictoras (X) y objetivo (y)
    X = df[["Ingreso_Mensual", "Buro_Credito_Score", "Factor_Certeza_CF"]]
    y = df["Dictamen_Final"]
    
    # Codificar la variable categórica de salida
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # División de datos: Entrenamiento (80%) y Prueba (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.20, random_state=42)
    
    # Algoritmo de clasificación supervisado
    model = RandomForestClassifier(n_estimators=50, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluación con Validación Cruzada (Cross-Validation con 5 pliegues)
    cv_scores = cross_val_score(model, X, y_encoded, cv=5)
    acc_promedio = cv_scores.mean()
    
    return model, le, acc_promedio

# --- MOTOR DE INFERENCIA CLÁSICO (SISTEMA EXPERTO) ---
class Solicitud(Fact):
    pass

class MotorRiesgo(KnowledgeEngine):
    def __init__(self):  # CORREGIDO
        super().__init__()
        self.diagnostico = []
        self.score_puntos = 0
        self.decision = "PENDIENTE"

    def registrar_hallazgo(self, variable, estatus, puntos, detalle):
        self.diagnostico.append({
            "Variable": variable,
            "Estatus": estatus,
            "Puntos": puntos,
            "Detalle": detalle
        })
        self.score_puntos += puntos

    # CORREGIDO: Uso de MATCH en lugar de L()
    @Rule(Solicitud(dti=MATCH.d & P(lambda d: d > 0.45)))
    def regla_dti_critico(self):
        self.registrar_hallazgo("DTI (Deuda/Ingreso)", "CRÍTICO", -100, "Sobreendeudamiento detectado (>45%)")
        self.decision = "RECHAZADO"

    @Rule(Solicitud(buro=MATCH.b & P(lambda b: b < 550)))
    def regla_buro_insuficiente(self):
        self.registrar_hallazgo("Buró de Crédito", "CRÍTICO", -80, "Historial de riesgo o sin comportamiento reportado")

    @Rule(Solicitud(buro=MATCH.b & P(lambda b: b >= 720)))
    def regla_buro_excelente(self):
        self.registrar_hallazgo("Buró de Crédito", "EXCELENTE", 50, "Excelente comportamiento de pago histórico")

    @Rule(Solicitud(antiguedad=MATCH.a & P(lambda a: a >= 3)))
    def regla_estabilidad(self):
        self.registrar_hallazgo("Antigüedad Laboral", "ESTABLE", 20, "Arraigo laboral óptimo")