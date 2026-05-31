import pandas as pd
from src.motor_experto import MotorExpertoCredito, Solicitud


def evaluar_sistema_experto(datos):
    motor = MotorExpertoCredito()
    motor.reset()

    motor.declare(Solicitud(
        ingresos=datos["ingresos"],
        monto=datos["monto"],
        gastos=datos["gastos"],
        buro=datos["buro"],
        antiguedad=datos["antiguedad"],
        vivienda=datos["vivienda"],
        dependientes=datos["dependientes"],
        dti=datos["dti"]
    ))

    motor.run()

    return {
        "dictamen": motor.obtener_dictamen(),
        "score": motor.score,
        "diagnostico": motor.diagnostico
    }


def evaluar_modelo_ml(modelo, encoder_y, datos):
    entrada = pd.DataFrame([{
        "Ingreso_Mensual": datos["ingresos"],
        "Monto_Solicitado": datos["monto"],
        "Gastos_Deuda": datos["gastos"],
        "Buro_Credito_Score": datos["buro"],
        "Antiguedad_Laboral": datos["antiguedad"],
        "Vivienda": datos["vivienda"],
        "Dependientes": datos["dependientes"],
        "DTI": datos["dti"]
    }])

    prediccion = modelo.predict(entrada)[0]
    dictamen = encoder_y.inverse_transform([prediccion])[0]

    probabilidades = modelo.predict_proba(entrada)[0]
    confianza = max(probabilidades)

    clases = encoder_y.inverse_transform(modelo.classes_)

    detalle_probabilidades = pd.DataFrame({
        "Dictamen": clases,
        "Probabilidad": probabilidades
    })

    return {
        "dictamen": dictamen,
        "confianza": confianza,
        "probabilidades": detalle_probabilidades
    }


def dictamen_final(resultado_experto, resultado_ml):
    experto = resultado_experto["dictamen"]
    ml = resultado_ml["dictamen"]

    if experto == "Rechazado":
        return (
            "Rechazado",
            "El sistema experto detectó una condición crítica o un puntaje insuficiente. Por política de riesgo, el rechazo prevalece sobre el modelo de aprendizaje."
        )

    if experto == "Aprobado" and ml == "Aprobado":
        return (
            "Aprobado",
            "El sistema experto y el modelo de aprendizaje coinciden en aprobar la solicitud."
        )

    if experto == "Sujeto a Aval" and ml == "Aprobado":
        return (
            "Sujeto a Aval",
            "El modelo de aprendizaje predice aprobación, pero el sistema experto detecta riesgo moderado. Se recomienda solicitar aval."
        )

    if experto == "Aprobado" and ml == "Sujeto a Aval":
        return (
            "Sujeto a Aval",
            "El sistema experto aprueba, pero el modelo histórico detecta casos similares con riesgo moderado."
        )

    if experto != ml:
        return (
            "Revisión Manual",
            "Existe discrepancia entre el sistema experto y el modelo de aprendizaje. Se recomienda revisión por analista."
        )

    return experto, "Ambos módulos llegaron a una conclusión compatible."


def generar_explicacion_paso_a_paso(datos, resultado_experto, resultado_ml, final):
    pasos = []

    pasos.append(f"1. Se registró una solicitud de crédito por ${datos['monto']:,.2f}.")
    pasos.append(f"2. El solicitante reportó ingresos mensuales de ${datos['ingresos']:,.2f} y pagos de deuda por ${datos['gastos']:,.2f}.")
    pasos.append(f"3. Se calculó el DTI: {datos['gastos']:,.2f} / {datos['ingresos']:,.2f} = {datos['dti']:.2%}.")
    pasos.append(f"4. El sistema experto evaluó reglas de buró, DTI, antigüedad laboral, vivienda y dependientes.")
    pasos.append(f"5. El puntaje total del sistema experto fue de {resultado_experto['score']} puntos.")
    pasos.append(f"6. El dictamen del sistema experto fue: {resultado_experto['dictamen']}.")
    pasos.append(f"7. El modelo de aprendizaje predijo: {resultado_ml['dictamen']} con {resultado_ml['confianza'] * 100:.2f}% de confianza.")
    pasos.append(f"8. El dictamen final híbrido fue: {final}.")

    return pasos