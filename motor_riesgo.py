import collections
import collections.abc
# Parche de compatibilidad para experta en Python 3.10+
collections.Mapping = collections.abc.Mapping

from experta import *

class Solicitud(Fact):
    """Variables financieras reales de riesgo"""
    pass

class MotorRiesgo(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.diagnostico = []
        self.score_puntos = 0
        self.decision = "PENDIENTE"
        self.certeza = 0.0

    def registrar_hallazgo(self, variable, estatus, impacto, puntos, detalle):
        self.diagnostico.append({
            "Variable": variable,
            "Estatus": estatus,
            "Impacto": impacto,
            "Puntos": puntos,
            "Detalle": detalle
        })
        self.score_puntos += puntos

    # --- REGLAS DE BLOQUEO (Hard Rules) ---
    # CORREGIDO: Se usa MATCH.d en lugar de L(d)
    @Rule(Solicitud(dti=MATCH.d & P(lambda d: d > 0.45)))
    def regla_dti_critico(self):
        self.registrar_hallazgo("DTI (Deuda/Ingreso)", "CRÍTICO", "NEGATIVO", -100, "Sobreendeudamiento detectado (>45%)")
        self.decision = "RECHAZADO"

    # CORREGIDO: Se usa MATCH.b en lugar de L(b)
    @Rule(Solicitud(buro=MATCH.b & P(lambda b: b < 550)))
    def regla_buro_insuficiente(self):
        self.registrar_hallazgo("Buró de Crédito", "CRÍTICO", "NEGATIVO", -80, "Historial crediticio de muy alto riesgo")

    # --- REGLAS DE SCORING (Soft Rules) ---
    # CORREGIDO: Se usa MATCH.b en lugar de L(b)
    @Rule(Solicitud(buro=MATCH.b & P(lambda b: b >= 750)))
    def regla_buro_excelente(self):
        self.registrar_hallazgo("Buró de Crédito", "EXCELENTE", "POSITIVO", 50, "Cliente con alta solvencia moral")

    # CORREGIDO: Se usa MATCH.a en lugar de L(a)
    @Rule(Solicitud(antiguedad=MATCH.a & P(lambda a: a >= 3)))
    def regla_estabilidad(self):
        self.registrar_hallazgo("Antigüedad Laboral", "ESTABLE", "POSITIVO", 20, "Baja probabilidad de desempleo inmediato")

    @Rule(Solicitud(vivienda='Propia'))
    def regla_patrimonio(self):
        self.registrar_hallazgo("Vivienda", "PROPIA", "POSITIVO", 15, "Respaldo patrimonial sólido")

    # CORREGIDO: Se usa MATCH.dep en lugar de L(dep)
    @Rule(Solicitud(dependientes=MATCH.dep & P(lambda dep: dep >= 3)))
    def regla_carga_familiar(self):
        self.registrar_hallazgo("Carga Familiar", "ALTA", "NEGATIVO", -15, "Menor capacidad de ahorro residual")

def calcular_certeza(datos):
    """Calcula qué tan confiable es la decisión basándose en la calidad del dato"""
    puntos_confianza = 0
    if datos['antiguedad'] > 0: puntos_confianza += 40
    if datos['buro'] > 300: puntos_confianza += 30
    if datos['ingresos'] > datos['gastos']: puntos_confianza += 30
    return puntos_confianza / 100