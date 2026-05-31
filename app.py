import streamlit as st
import pandas as pd
import io
import datetime

from src.modelo_ml import entrenar_modelo
from src.evaluador_hibrido import (
    evaluar_sistema_experto,
    evaluar_modelo_ml,
    dictamen_final,
    generar_explicacion_paso_a_paso
)


st.set_page_config(
    page_title="Sistema Experto de Crédito",
    layout="wide"
)


@st.cache_resource
def cargar_modelo():
    return entrenar_modelo()


def main():
    modelo, encoder_y, accuracy_cv, columnas = cargar_modelo()

    st.sidebar.title("Sistema de Crédito")
    vista = st.sidebar.radio(
        "Navegación",
        ["Solicitud", "Evaluación", "Dataset"]
    )

    if "solicitud" not in st.session_state:
        st.session_state.solicitud = None

    if vista == "Solicitud":
        st.title("Solicitud de Crédito")

        with st.form("formulario_credito"):
            col1, col2 = st.columns(2)

            with col1:
                nombre = st.text_input("Nombre completo")
                monto = st.number_input("Monto solicitado", min_value=1000, value=1000)
                ingresos = st.number_input("Ingresos mensuales", min_value=1, value=1)
                gastos = st.number_input("Pagos mensuales de deuda", min_value=0, value=0)

            with col2:
                buro = st.slider("Puntaje de buró", 300, 850, 710)
                antiguedad = st.number_input("Años en empleo actual", 0, 40, 4)
                vivienda = st.selectbox("Tipo de vivienda", ["Propia", "Rentada", "Familiares"])
                dependientes = st.number_input("Dependientes económicos", 0, 10, 1)

            enviar = st.form_submit_button("Enviar solicitud")

            if enviar:
                if not nombre.strip():
                    st.error("Ingresa el nombre del solicitante.")
                    return

                if ingresos <= 0:
                    st.error("Los ingresos deben ser mayores a cero.")
                    return
                
                dti = gastos / ingresos

                st.session_state.solicitud = {
                    "nombre": nombre,
                    "monto": monto,
                    "ingresos": ingresos,
                    "gastos": gastos,
                    "buro": buro,
                    "antiguedad": antiguedad,
                    "vivienda": vivienda,
                    "dependientes": dependientes,
                    "dti": dti
                }

                st.success("Solicitud registrada correctamente.")

    elif vista == "Evaluación":
        st.title("Evaluación paso a paso")

        if st.session_state.solicitud is None:
            st.info("Primero registra una solicitud.")
            return

        datos = st.session_state.solicitud

        resultado_experto = evaluar_sistema_experto(datos)
        resultado_ml = evaluar_modelo_ml(modelo, encoder_y, datos)
        final, explicacion_final = dictamen_final(resultado_experto, resultado_ml)

        st.subheader("Datos del solicitante")
        st.json(datos)

        st.subheader("Indicadores calculados")

        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Ingreso mensual", f"${datos['ingresos']:,.2f}")
        col_b.metric("Pagos de deuda", f"${datos['gastos']:,.2f}")
        col_c.metric("DTI", f"{datos['dti']:.2%}")

        if datos["dti"] <= 0.30:
            st.success("Nivel de endeudamiento bajo.")
        elif datos["dti"] <= 0.45:
            st.warning("Nivel de endeudamiento moderado.")
        else:
            st.error("Nivel de endeudamiento crítico.")

        st.subheader("Resultado del Sistema Experto")

        col1, col2 = st.columns(2)
        col1.metric("Dictamen experto", resultado_experto["dictamen"])
        col2.metric("Puntaje por reglas", resultado_experto["score"])

        st.write("Reglas evaluadas:")
        st.dataframe(
            pd.DataFrame(resultado_experto["diagnostico"]),
            use_container_width=True
        )

        st.subheader("Resultado del Modelo de Aprendizaje")

        col3, col4 = st.columns(2)
        col3.metric("Predicción ML", resultado_ml["dictamen"])
        col4.metric("Confianza", f"{resultado_ml['confianza'] * 100:.2f}%")

        st.caption(f"Exactitud promedio por validación cruzada: {accuracy_cv * 100:.2f}%")

        st.write("Probabilidad por clase:")
        df_probs = resultado_ml["probabilidades"].copy()
        df_probs["Probabilidad"] = df_probs["Probabilidad"] * 100
        st.dataframe(df_probs, use_container_width=True)

        st.bar_chart(df_probs.set_index("Dictamen"))

        st.subheader("Dictamen Final Híbrido")
        st.metric("Resultado final", final)
        st.write(explicacion_final)

        st.subheader("Explicación paso a paso")

        pasos = generar_explicacion_paso_a_paso(
            datos,
            resultado_experto,
            resultado_ml,
            final
        )

        for paso in pasos:
            st.write(paso)

        st.subheader("Descargar reporte")

        output = io.BytesIO()

        df_datos = pd.DataFrame([datos])
        df_reglas = pd.DataFrame(resultado_experto["diagnostico"])
        df_probs = resultado_ml["probabilidades"].copy()
        df_probs["Probabilidad"] = df_probs["Probabilidad"] * 100

        df_resumen = pd.DataFrame([{
            "Cliente": datos["nombre"],
            "Monto solicitado": datos["monto"],
            "Ingreso mensual": datos["ingresos"],
            "Pagos de deuda": datos["gastos"],
            "DTI": datos["dti"],
            "Dictamen sistema experto": resultado_experto["dictamen"],
            "Puntaje sistema experto": resultado_experto["score"],
            "Dictamen modelo ML": resultado_ml["dictamen"],
            "Confianza ML": resultado_ml["confianza"] * 100,
            "Dictamen final": final,
            "Explicación final": explicacion_final,
            "Fecha de evaluación": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])

        df_pasos = pd.DataFrame({
            "Paso": pasos
        })

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_resumen.to_excel(writer, sheet_name="Resumen", index=False)
            df_datos.to_excel(writer, sheet_name="Datos Solicitud", index=False)
            df_reglas.to_excel(writer, sheet_name="Reglas Expertas", index=False)
            df_probs.to_excel(writer, sheet_name="Probabilidades ML", index=False)
            df_pasos.to_excel(writer, sheet_name="Paso a Paso", index=False)

        st.download_button(
            label="Descargar reporte en Excel",
            data=output.getvalue(),
            file_name=f"reporte_credito_{datos['nombre'].replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()