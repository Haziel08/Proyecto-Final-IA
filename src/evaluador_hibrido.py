import pandas as pd  # importa pandas para trabajar con DataFrames
from src.motor_experto import MotorExpertoCredito, Solicitud  # importa el motor experto y la clase de hecho Solicitud


def evaluar_sistema_experto(datos):  # función que evalúa una solicitud usando el motor experto
    motor = MotorExpertoCredito()  # crea una instancia del motor experto
    motor.reset()  # reinicia el motor antes de declarar nuevos hechos

    motor.declare(Solicitud(  # declara un hecho Solicitud con los datos ingresados
        ingresos=datos["ingresos"],  # ingresos mensuales del solicitante
        monto=datos["monto"],  # monto de crédito solicitado
        gastos=datos["gastos"],  # pagos de deuda mensuales
        buro=datos["buro"],  # puntaje de buró
        antiguedad=datos["antiguedad"],  # años en empleo actual
        vivienda=datos["vivienda"],  # tipo de vivienda
        dependientes=datos["dependientes"],  # dependientes económicos
        dti=datos["dti"]  # ratio deuda-ingreso calculado
    ))

    motor.run()  # ejecuta el motor experto para evaluar las reglas declaradas

    return {  # retorna un diccionario con el dictamen y el diagnóstico
        "dictamen": motor.obtener_dictamen(),  # resultado final del motor experto
        "score": motor.score,  # puntuación acumulada por las reglas
        "diagnostico": motor.diagnostico  # detalles de las reglas evaluadas
    }


def evaluar_modelo_ml(modelo, encoder_y, datos):  # función que evalúa una solicitud con el modelo ML
    entrada = pd.DataFrame([{  # construye un DataFrame con los datos de entrada para el modelo
        "Ingreso_Mensual": datos["ingresos"],  # campo para el ingreso mensual
        "Monto_Solicitado": datos["monto"],  # campo para el monto solicitado
        "Gastos_Deuda": datos["gastos"],  # campo para los pagos de deuda
        "Buro_Credito_Score": datos["buro"],  # campo para el puntaje de buró
        "Antiguedad_Laboral": datos["antiguedad"],  # campo para la antigüedad laboral
        "Vivienda": datos["vivienda"],  # campo para el tipo de vivienda
        "Dependientes": datos["dependientes"],  # campo para los dependientes
        "DTI": datos["dti"]  # campo para el DTI
    }])

    prediccion = modelo.predict(entrada)[0]  # obtiene la predicción codificada del modelo
    dictamen = encoder_y.inverse_transform([prediccion])[0]  # decodifica la predicción a texto

    probabilidades = modelo.predict_proba(entrada)[0]  # obtiene las probabilidades de cada clase
    confianza = max(probabilidades)  # calcula la confianza como la probabilidad máxima

    clases = encoder_y.inverse_transform(modelo.classes_)  # decodifica las clases del modelo

    detalle_probabilidades = pd.DataFrame({  # construye un DataFrame con las probabilidades por clase
        "Dictamen": clases,  # nombres de las clases predichas
        "Probabilidad": probabilidades  # valores de probabilidad correspondientes
    })

    return {  # retorna los resultados de la evaluación ML
        "dictamen": dictamen,  # dictamen predicho por el modelo de ML
        "confianza": confianza,  # nivel de confianza de la predicción
        "probabilidades": detalle_probabilidades  # detalle de probabilidades por clase
    }


def dictamen_final(resultado_experto, resultado_ml):  # función que combina ambos dictámenes
    experto = resultado_experto["dictamen"]  # dictamen del sistema experto
    ml = resultado_ml["dictamen"]  # dictamen del modelo de ML

    if experto == "Rechazado":  # si el motor experto rechaza
        return (
            "Rechazado",
            "El sistema experto detectó una condición crítica o un puntaje insuficiente. Por política de riesgo, el rechazo prevalece sobre el modelo de aprendizaje."
        )

    if experto == "Aprobado" and ml == "Aprobado":  # ambos coinciden en aprobar
        return (
            "Aprobado",
            "El sistema experto y el modelo de aprendizaje coinciden en aprobar la solicitud."
        )

    if experto == "Sujeto a Aval" and ml == "Aprobado":  # experto sugiere aval pero ML aprueba
        return (
            "Sujeto a Aval",
            "El modelo de aprendizaje predice aprobación, pero el sistema experto detecta riesgo moderado. Se recomienda solicitar aval."
        )

    if experto == "Aprobado" and ml == "Sujeto a Aval":  # experto aprueba, ML sugiere aval
        return (
            "Sujeto a Aval",
            "El sistema experto aprueba, pero el modelo histórico detecta casos similares con riesgo moderado."
        )

    if experto != ml:  # si hay discrepancia entre los dos sistemas
        return (
            "Revisión Manual",
            "Existe discrepancia entre el sistema experto y el modelo de aprendizaje. Se recomienda revisión por analista."
        )

    return experto, "Ambos módulos llegaron a una conclusión compatible."  # si coinciden en cualquier otro caso


def generar_explicacion_paso_a_paso(datos, resultado_experto, resultado_ml, final):  # genera explicaciones textuales paso a paso
    pasos = []  # lista para acumular cada paso explicativo

    pasos.append(f"1. Se registró una solicitud de crédito por ${datos['monto']:,.2f}.")  # paso 1: monto solicitado
    pasos.append(f"2. El solicitante reportó ingresos mensuales de ${datos['ingresos']:,.2f} y pagos de deuda por ${datos['gastos']:,.2f}.")  # paso 2: ingresos y deuda
    pasos.append(f"3. Se calculó el DTI: {datos['gastos']:,.2f} / {datos['ingresos']:,.2f} = {datos['dti']:.2%}.")  # paso 3: cálculo del DTI
    pasos.append(f"4. El sistema experto evaluó reglas de buró, DTI, antigüedad laboral, vivienda y dependientes.")  # paso 4: evaluación experta
    pasos.append(f"5. El puntaje total del sistema experto fue de {resultado_experto['score']} puntos.")  # paso 5: puntaje experto
    pasos.append(f"6. El dictamen del sistema experto fue: {resultado_experto['dictamen']}.")  # paso 6: dictamen experto
    pasos.append(f"7. El modelo de aprendizaje predijo: {resultado_ml['dictamen']} con {resultado_ml['confianza'] * 100:.2f}% de confianza.")  # paso 7: dictamen ML y confianza
    pasos.append(f"8. El dictamen final híbrido fue: {final}.")  # paso 8: dictamen final combinado

    return pasos  # retorna la lista de pasos explicativos