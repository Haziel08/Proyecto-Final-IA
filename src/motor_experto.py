import collections  # importa la librería collections para compatibilidad con versiones de Python
import collections.abc  # importa abstract base classes de collections

collections.Mapping = collections.abc.Mapping  # reestablece Mapping para compatibilidad con experta

from experta import KnowledgeEngine, Fact, Rule, MATCH, P  # importa componentes centrales del motor experto


class Solicitud(Fact):  # define un hecho de tipo Solicitud para el motor experto
    pass  # no se añaden campos adicionales, solo se utiliza como etiqueta de hecho


class MotorExpertoCredito(KnowledgeEngine):  # define el motor experto para crédito
    def __init__(self):  # constructor del motor experto
        super().__init__()  # inicializa el motor experto base
        self.diagnostico = []  # almacena las reglas evaluadas y sus resultados
        self.score = 0  # puntuación acumulada de la evaluación
        self.bloqueo = False  # indica si la solicitud tiene un bloqueo crítico

    def registrar(self, regla, variable, resultado, impacto, puntos, explicacion, cumple=True):  # agrega una evaluación al diagnóstico
        self.diagnostico.append({  # añade un diccionario con los detalles de la regla evaluada
            "Regla evaluada": regla,  # nombre o descripción de la regla
            "Variable": variable,  # variable analizada por la regla
            "Resultado": resultado,  # valor observado de la variable
            "Cumple": "Sí" if cumple else "No",  # indica si la condición se cumple
            "Impacto": impacto,  # impacto de la regla en el dictamen
            "Puntos": puntos,  # puntos asignados por la regla
            "Explicación": explicacion  # texto explicativo del resultado
        })

        if cumple:  # si la regla se cumple
            self.score += puntos  # sumar los puntos al score total

        if impacto == "CRÍTICO" and cumple:  # si el impacto es crítico y se cumple la regla
            self.bloqueo = True  # marca el bloqueo para rechazo automático

    @Rule(Solicitud(dti=MATCH.dti))  # regla que se activa cuando la solicitud contiene un campo dti
    def evaluar_dti(self, dti):  # método para evaluar la relación deuda-ingreso
        if dti > 0.45:  # si el DTI es mayor al 45%
            self.registrar(
                "DTI > 45%",  # descripción de la regla
                "DTI",  # variable evaluada
                f"{dti:.2%}",  # resultado formateado como porcentaje
                "CRÍTICO",  # impacto crítico
                -100,  # puntos negativos por riesgo alto
                "La deuda mensual supera el 45% del ingreso. Riesgo alto de sobreendeudamiento."  # explicación de riesgo
            )
        elif dti <= 0.30:  # si el DTI es bajo o igual al 30%
            self.registrar(
                "DTI <= 30%",
                "DTI",
                f"{dti:.2%}",
                "POSITIVO",
                30,
                "La relación deuda/ingreso es saludable."  # explicación positiva
            )
        else:  # si el DTI está entre 30% y 45%
            self.registrar(
                "30% < DTI <= 45%",
                "DTI",
                f"{dti:.2%}",
                "MODERADO",
                0,
                "La relación deuda/ingreso es aceptable, pero requiere vigilancia."  # explica que hay que vigilar el riesgo
            )

    @Rule(Solicitud(buro=MATCH.buro))  # regla que se activa cuando la solicitud contiene puntaje de buró
    def evaluar_buro(self, buro):  # método para evaluar el puntaje de crédito
        if buro < 550:  # puntaje muy bajo
            self.registrar(
                "Buró < 550",
                "Buró de crédito",
                buro,
                "CRÍTICO",
                -80,
                "El puntaje de buró indica alto riesgo crediticio."  # explicación de riesgo grave
            )
        elif buro >= 750:  # puntaje excelente
            self.registrar(
                "Buró >= 750",
                "Buró de crédito",
                buro,
                "POSITIVO",
                50,
                "El solicitante tiene excelente historial crediticio."  # explicación positiva
            )
        elif buro >= 700:  # puntaje bueno
            self.registrar(
                "700 <= Buró < 750",
                "Buró de crédito",
                buro,
                "POSITIVO",
                30,
                "El solicitante tiene buen historial crediticio."  # explicación favorable
            )
        elif buro >= 600:  # puntaje aceptable
            self.registrar(
                "600 <= Buró < 700",
                "Buró de crédito",
                buro,
                "MODERADO",
                10,
                "El historial crediticio es aceptable, pero no sobresaliente."  # explicación moderada
            )
        else:  # puntaje entre 550 y 599
            self.registrar(
                "550 <= Buró < 600",
                "Buró de crédito",
                buro,
                "NEGATIVO",
                -20,
                "El historial crediticio es bajo y representa riesgo."  # explicación de riesgo
            )

    @Rule(Solicitud(antiguedad=MATCH.a))  # regla que se activa cuando la solicitud contiene antigüedad laboral
    def evaluar_antiguedad(self, a):  # evalúa la antigüedad en el empleo actual
        if a >= 3:  # si tiene 3 años o más en el empleo
            self.registrar(
                "Antigüedad >= 3 años",
                "Antigüedad laboral",
                f"{a} años",
                "POSITIVO",
                20,
                "Tiene estabilidad laboral suficiente."  # explicación positiva por estabilidad
            )
        else:  # si tiene menos de 3 años en el empleo
            self.registrar(
                "Antigüedad < 3 años",
                "Antigüedad laboral",
                f"{a} años",
                "NEGATIVO",
                -10,
                "La antigüedad laboral es baja."  # explicación negativa por menor estabilidad
            )

    @Rule(Solicitud(vivienda=MATCH.vivienda))  # regla que se activa cuando la solicitud contiene tipo de vivienda
    def evaluar_vivienda(self, vivienda):  # evalúa el tipo de vivienda del solicitante
        if vivienda == "Propia":  # si la vivienda es propia
            self.registrar(
                "Vivienda propia",
                "Vivienda",
                vivienda,
                "POSITIVO",
                15,
                "Contar con vivienda propia reduce el riesgo financiero."  # explicación de menor riesgo
            )
        elif vivienda == "Familiares":  # si vive con familiares
            self.registrar(
                "Vivienda con familiares",
                "Vivienda",
                vivienda,
                "MODERADO",
                5,
                "Vivir con familiares puede reducir algunos gastos fijos."  # explicación de impacto moderado
            )
        else:  # caso de vivienda rentada
            self.registrar(
                "Vivienda rentada",
                "Vivienda",
                vivienda,
                "NEUTRO",
                0,
                "La renta representa un gasto mensual adicional."  # explicación neutra/negativa por renta
            )

    @Rule(Solicitud(dependientes=MATCH.dep))  # regla que se activa cuando la solicitud contiene dependientes
    def evaluar_dependientes(self, dep):  # evalúa la cantidad de dependientes económicos
        if dep >= 3:  # si tiene tres o más dependientes
            self.registrar(
                "Dependientes >= 3",
                "Dependientes",
                dep,
                "NEGATIVO",
                -15,
                "Una carga familiar alta reduce la capacidad de pago."  # explicación de riesgo por carga alta
            )
        elif dep == 0:  # si no tiene dependientes
            self.registrar(
                "Sin dependientes",
                "Dependientes",
                dep,
                "POSITIVO",
                10,
                "No tener dependientes mejora la capacidad de pago."  # explicación positiva
            )
        else:  # si tiene uno o dos dependientes
            self.registrar(
                "1 o 2 dependientes",
                "Dependientes",
                dep,
                "NEUTRO",
                0,
                "La carga familiar es manejable."  # explicación neutral
            )

    def obtener_dictamen(self):  # determina el dictamen final según score y bloqueo
        if self.bloqueo:  # si hay bloqueo crítico activado
            return "Rechazado"  # rechaza inmediatamente
        if self.score >= 60:  # si la puntuación es 60 o más
            return "Aprobado"  # solicita aprobación
        if self.score >= 25:  # si la puntuación está entre 25 y 59
            return "Sujeto a Aval"  # sujeta a aval
        return "Rechazado"  # rechazo por puntuación insuficiente