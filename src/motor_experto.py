import collections
import collections.abc

collections.Mapping = collections.abc.Mapping

from experta import KnowledgeEngine, Fact, Rule, MATCH, P


class Solicitud(Fact):
    pass


class MotorExpertoCredito(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.diagnostico = []
        self.score = 0
        self.bloqueo = False

    def registrar(self, regla, variable, resultado, impacto, puntos, explicacion, cumple=True):
        self.diagnostico.append({
            "Regla evaluada": regla,
            "Variable": variable,
            "Resultado": resultado,
            "Cumple": "Sí" if cumple else "No",
            "Impacto": impacto,
            "Puntos": puntos,
            "Explicación": explicacion
        })

        if cumple:
            self.score += puntos

        if impacto == "CRÍTICO" and cumple:
            self.bloqueo = True

    @Rule(Solicitud(dti=MATCH.dti))
    def evaluar_dti(self, dti):
        if dti > 0.45:
            self.registrar(
                "DTI > 45%",
                "DTI",
                f"{dti:.2%}",
                "CRÍTICO",
                -100,
                "La deuda mensual supera el 45% del ingreso. Riesgo alto de sobreendeudamiento."
            )
        elif dti <= 0.30:
            self.registrar(
                "DTI <= 30%",
                "DTI",
                f"{dti:.2%}",
                "POSITIVO",
                30,
                "La relación deuda/ingreso es saludable."
            )
        else:
            self.registrar(
                "30% < DTI <= 45%",
                "DTI",
                f"{dti:.2%}",
                "MODERADO",
                0,
                "La relación deuda/ingreso es aceptable, pero requiere vigilancia."
            )

    @Rule(Solicitud(buro=MATCH.buro))
    def evaluar_buro(self, buro):
        if buro < 550:
            self.registrar(
                "Buró < 550",
                "Buró de crédito",
                buro,
                "CRÍTICO",
                -80,
                "El puntaje de buró indica alto riesgo crediticio."
            )
        elif buro >= 750:
            self.registrar(
                "Buró >= 750",
                "Buró de crédito",
                buro,
                "POSITIVO",
                50,
                "El solicitante tiene excelente historial crediticio."
            )
        elif buro >= 700:
            self.registrar(
                "700 <= Buró < 750",
                "Buró de crédito",
                buro,
                "POSITIVO",
                30,
                "El solicitante tiene buen historial crediticio."
            )
        elif buro >= 600:
            self.registrar(
                "600 <= Buró < 700",
                "Buró de crédito",
                buro,
                "MODERADO",
                10,
                "El historial crediticio es aceptable, pero no sobresaliente."
            )
        else:
            self.registrar(
                "550 <= Buró < 600",
                "Buró de crédito",
                buro,
                "NEGATIVO",
                -20,
                "El historial crediticio es bajo y representa riesgo."
            )

    @Rule(Solicitud(antiguedad=MATCH.a))
    def evaluar_antiguedad(self, a):
        if a >= 3:
            self.registrar(
                "Antigüedad >= 3 años",
                "Antigüedad laboral",
                f"{a} años",
                "POSITIVO",
                20,
                "Tiene estabilidad laboral suficiente."
            )
        else:
            self.registrar(
                "Antigüedad < 3 años",
                "Antigüedad laboral",
                f"{a} años",
                "NEGATIVO",
                -10,
                "La antigüedad laboral es baja."
            )

    @Rule(Solicitud(vivienda=MATCH.vivienda))
    def evaluar_vivienda(self, vivienda):
        if vivienda == "Propia":
            self.registrar(
                "Vivienda propia",
                "Vivienda",
                vivienda,
                "POSITIVO",
                15,
                "Contar con vivienda propia reduce el riesgo financiero."
            )
        elif vivienda == "Familiares":
            self.registrar(
                "Vivienda con familiares",
                "Vivienda",
                vivienda,
                "MODERADO",
                5,
                "Vivir con familiares puede reducir algunos gastos fijos."
            )
        else:
            self.registrar(
                "Vivienda rentada",
                "Vivienda",
                vivienda,
                "NEUTRO",
                0,
                "La renta representa un gasto mensual adicional."
            )

    @Rule(Solicitud(dependientes=MATCH.dep))
    def evaluar_dependientes(self, dep):
        if dep >= 3:
            self.registrar(
                "Dependientes >= 3",
                "Dependientes",
                dep,
                "NEGATIVO",
                -15,
                "Una carga familiar alta reduce la capacidad de pago."
            )
        elif dep == 0:
            self.registrar(
                "Sin dependientes",
                "Dependientes",
                dep,
                "POSITIVO",
                10,
                "No tener dependientes mejora la capacidad de pago."
            )
        else:
            self.registrar(
                "1 o 2 dependientes",
                "Dependientes",
                dep,
                "NEUTRO",
                0,
                "La carga familiar es manejable."
            )

    def obtener_dictamen(self):
        if self.bloqueo:
            return "Rechazado"
        if self.score >= 60:
            return "Aprobado"
        if self.score >= 25:
            return "Sujeto a Aval"
        return "Rechazado"