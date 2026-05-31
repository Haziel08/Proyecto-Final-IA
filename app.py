import streamlit as st  # importa Streamlit para construir la interfaz web
import pandas as pd  # importa pandas para manipular datos en tablas
import io  # importa io para manejar buffers de memoria como archivos
import datetime  # importa datetime para obtener la fecha y hora actuales

from src.modelo_ml import entrenar_modelo  # importa la función para entrenar el modelo ML
from src.evaluador_hibrido import (
    evaluar_sistema_experto,  # importa la evaluación del sistema experto
    evaluar_modelo_ml,  # importa la evaluación del modelo de ML
    dictamen_final,  # importa la función que combina ambos dictámenes
    generar_explicacion_paso_a_paso  # importa la generación de explicación detallada
)


st.set_page_config(
    page_title="Sistema Experto de Crédito",  # define el título de la página
    layout="wide"  # usa un layout ancho para la aplicación
)


@st.cache_resource  # cachea el recurso del modelo para mejorar el rendimiento
def cargar_modelo():
    return entrenar_modelo()  # retorna el modelo entrenado y sus metadatos


def main():
    modelo, encoder_y, accuracy_cv, columnas = cargar_modelo()  # carga el modelo y parámetros requeridos

    st.sidebar.title("Sistema de Crédito")  # muestra el título del panel lateral
    vista = st.sidebar.radio(
        "Navegación",  # etiqueta del selector de vistas
        ["Solicitud", "Evaluación", "Dataset"]  # opciones disponibles para el usuario
    )

    if "solicitud" not in st.session_state:  # inicializa la solicitud si no existe en la sesión
        st.session_state.solicitud = None  # establece la solicitud como None por defecto

    if vista == "Solicitud":  # muestra el formulario cuando la vista es Solicitud
        st.title("Solicitud de Crédito")  # título principal de la sección

        with st.form("formulario_credito"):  # inicia el formulario de solicitud
            col1, col2 = st.columns(2)  # divide el formulario en dos columnas

            with col1:  # primera columna del formulario
                nombre = st.text_input("Nombre completo")  # campo para el nombre del solicitante
                monto = st.number_input("Monto solicitado", min_value=1000, value=1000)  # campo para el monto solicitado
                ingresos = st.number_input("Ingresos mensuales", min_value=1, value=1)  # campo para los ingresos mensuales
                gastos = st.number_input("Pagos mensuales de deuda", min_value=0, value=0)  # campo para los pagos de deuda

            with col2:  # segunda columna del formulario
                buro = st.slider("Puntaje de buró", 300, 850, 710)  # selector de puntaje de buró
                antiguedad = st.number_input("Años en empleo actual", 0, 40, 4)  # años en el empleo actual
                vivienda = st.selectbox("Tipo de vivienda", ["Propia", "Rentada", "Familiares"])  # tipo de vivienda
                dependientes = st.number_input("Dependientes económicos", 0, 10, 1)  # número de dependientes económicos

            enviar = st.form_submit_button("Enviar solicitud")  # botón para enviar el formulario

            if enviar:  # si el formulario se envía
                if not nombre.strip():  # valida que el nombre no esté vacío
                    st.error("Ingresa el nombre del solicitante.")  # muestra error si falta el nombre
                    return  # detiene la ejecución actual

                if ingresos <= 0:  # valida que los ingresos sean mayores a cero
                    st.error("Los ingresos deben ser mayores a cero.")  # muestra mensaje de error
                    return  # detiene la ejecución actual
                
                dti = gastos / ingresos  # calcula el ratio deuda-ingreso

                st.session_state.solicitud = {  # guarda los datos de la solicitud en el estado de sesión
                    "nombre": nombre,  # nombre del solicitante
                    "monto": monto,  # monto solicitado
                    "ingresos": ingresos,  # ingresos mensuales
                    "gastos": gastos,  # gastos mensuales de deuda
                    "buro": buro,  # puntaje de buró
                    "antiguedad": antiguedad,  # años en empleo actual
                    "vivienda": vivienda,  # tipo de vivienda
                    "dependientes": dependientes,  # número de dependientes
                    "dti": dti  # ratio deuda-ingreso calculado
                }

                st.success("Solicitud registrada correctamente.")

    elif vista == "Evaluación":  # si la vista seleccionada es Evaluación
        st.title("Evaluación paso a paso")  # título de la sección de evaluación

        if st.session_state.solicitud is None:  # si no hay solicitud en el estado de sesión
            st.info("Primero registra una solicitud.")  # indica que se debe registrar una solicitud primero
            return  # detiene la ejecución de la vista

        datos = st.session_state.solicitud  # recupera los datos de la solicitud guardada

        resultado_experto = evaluar_sistema_experto(datos)  # evalúa los datos con el sistema experto
        resultado_ml = evaluar_modelo_ml(modelo, encoder_y, datos)  # evalúa los datos con el modelo ML
        final, explicacion_final = dictamen_final(resultado_experto, resultado_ml)  # obtiene el dictamen combinado

        st.subheader("Datos del solicitante")  # subtítulo para los datos del solicitante
        st.json(datos)  # muestra los datos en formato JSON

        st.subheader("Indicadores calculados")  # subtítulo para los indicadores calculados

        col_a, col_b, col_c = st.columns(3)  # crea tres columnas para las métricas
        col_a.metric("Ingreso mensual", f"${datos['ingresos']:,.2f}")  # muestra el ingreso mensual formateado
        col_b.metric("Pagos de deuda", f"${datos['gastos']:,.2f}")  # muestra los pagos de deuda formateados
        col_c.metric("DTI", f"{datos['dti']:.2%}")  # muestra el DTI como porcentaje

        if datos["dti"] <= 0.30:  # si el DTI es bajo
            st.success("Nivel de endeudamiento bajo.")  # mensaje de nivel bajo
        elif datos["dti"] <= 0.45:  # si el DTI es moderado
            st.warning("Nivel de endeudamiento moderado.")  # mensaje de nivel moderado
        else:  # si el DTI es alto
            st.error("Nivel de endeudamiento crítico.")  # mensaje de nivel crítico

        st.subheader("Resultado del Sistema Experto")  # subtítulo para el resultado experto

        col1, col2 = st.columns(2)  # crea dos columnas para mostrar métricas expertas
        col1.metric("Dictamen experto", resultado_experto["dictamen"])  # muestra el dictamen del sistema experto
        col2.metric("Puntaje por reglas", resultado_experto["score"])  # muestra el puntaje del sistema experto

        st.write("Reglas evaluadas:")  # texto previo a la tabla de reglas
        st.dataframe(
            pd.DataFrame(resultado_experto["diagnostico"]),  # convierte el diagnóstico del experto en DataFrame
            use_container_width=True  # usa todo el ancho disponible
        )

        st.subheader("Resultado del Modelo de Aprendizaje")  # subtítulo para el resultado del modelo ML

        col3, col4 = st.columns(2)  # crea dos columnas para métricas del ML
        col3.metric("Predicción ML", resultado_ml["dictamen"])  # muestra la predicción del modelo ML
        col4.metric("Confianza", f"{resultado_ml['confianza'] * 100:.2f}%")  # muestra la confianza del modelo

        st.caption(f"Exactitud promedio por validación cruzada: {accuracy_cv * 100:.2f}%")  # muestra la precisión promedio del modelo

        st.write("Probabilidad por clase:")  # texto para la tabla de probabilidades
        df_probs = resultado_ml["probabilidades"].copy()  # copia las probabilidades para no modificar el original
        df_probs["Probabilidad"] = df_probs["Probabilidad"] * 100  # convierte el valor a porcentaje
        st.dataframe(df_probs, use_container_width=True)  # muestra la tabla de probabilidades

        st.bar_chart(df_probs.set_index("Dictamen"))  # grafica las probabilidades por clase

        st.subheader("Dictamen Final Híbrido")  # subtítulo para el dictamen final híbrido
        st.metric("Resultado final", final)  # muestra el resultado final combinado
        st.write(explicacion_final)  # muestra la explicación final del dictamen

        st.subheader("Explicación paso a paso")  # subtítulo para la explicación detallada

        pasos = generar_explicacion_paso_a_paso(
            datos,  # datos de entrada utilizados en la explicación
            resultado_experto,  # resultado del sistema experto
            resultado_ml,  # resultado del modelo ML
            final  # dictamen final combinado
        )

        for paso in pasos:  # recorre cada paso de la explicación
            st.write(paso)  # muestra el paso en la interfaz

        st.subheader("Descargar reporte")  # subtítulo para la sección de descarga

        output = io.BytesIO()  # crea un buffer en memoria para el archivo Excel

        df_datos = pd.DataFrame([datos])  # DataFrame con los datos de la solicitud
        df_reglas = pd.DataFrame(resultado_experto["diagnostico"])  # DataFrame del diagnóstico experto
        df_probs = resultado_ml["probabilidades"].copy()  # copia las probabilidades del modelo ML
        df_probs["Probabilidad"] = df_probs["Probabilidad"] * 100  # convierte a porcentaje

        df_resumen = pd.DataFrame([{  # DataFrame con el resumen final
            "Cliente": datos["nombre"],  # nombre del solicitante
            "Monto solicitado": datos["monto"],  # monto solicitado
            "Ingreso mensual": datos["ingresos"],  # ingresos mensuales
            "Pagos de deuda": datos["gastos"],  # gastos mensuales de deuda
            "DTI": datos["dti"],  # ratio deuda-ingreso
            "Dictamen sistema experto": resultado_experto["dictamen"],  # dictamen del sistema experto
            "Puntaje sistema experto": resultado_experto["score"],  # puntaje generado por el experto
            "Dictamen modelo ML": resultado_ml["dictamen"],  # dictamen del modelo ML
            "Confianza ML": resultado_ml["confianza"] * 100,  # confianza del ML en porcentaje
            "Dictamen final": final,  # resultado final híbrido
            "Explicación final": explicacion_final,  # explicación final del dictamen
            "Fecha de evaluación": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # fecha y hora de la evaluación
        }])

        df_pasos = pd.DataFrame({
            "Paso": pasos  # DataFrame con cada paso de la explicación
        })

        with pd.ExcelWriter(output, engine="openpyxl") as writer:  # crea el archivo Excel en el buffer
            df_resumen.to_excel(writer, sheet_name="Resumen", index=False)  # hoja con el resumen general
            df_datos.to_excel(writer, sheet_name="Datos Solicitud", index=False)  # hoja con los datos de la solicitud
            df_reglas.to_excel(writer, sheet_name="Reglas Expertas", index=False)  # hoja con las reglas expertas
            df_probs.to_excel(writer, sheet_name="Probabilidades ML", index=False)  # hoja con las probabilidades del ML
            df_pasos.to_excel(writer, sheet_name="Paso a Paso", index=False)  # hoja con la explicación paso a paso

        st.download_button(
            label="Descargar reporte en Excel",  # botón para descargar el reporte
            data=output.getvalue(),  # obtiene el contenido binario del archivo
            file_name=f"reporte_credito_{datos['nombre'].replace(' ', '_')}.xlsx",  # nombre de archivo generado
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # tipo MIME de Excel
        )

    elif vista == "Dataset":  # si la vista seleccionada es el dataset
        st.title("Dataset de entrenamiento")  # título para la vista de dataset

        try:  # intenta leer el archivo CSV del dataset
            df = pd.read_csv("data/clientes_credito.csv")  # carga el archivo CSV

            st.write("Registros cargados:", len(df))  # muestra la cantidad de registros cargados
            st.dataframe(df, use_container_width=True)  # muestra el dataset en una tabla

            st.subheader("Distribución de dictámenes")  # subtítulo para la distribución de dictámenes
            st.bar_chart(df["Dictamen_Final"].value_counts())  # grafica la distribución de dictámenes

        except FileNotFoundError:  # si el archivo no se encuentra
            st.error("No se encontró el archivo data/clientes_credito.csv")  # muestra mensaje de error

if __name__ == "__main__":  # punto de entrada principal
    main()  # ejecuta la función principal
