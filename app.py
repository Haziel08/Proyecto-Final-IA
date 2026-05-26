import streamlit as st
import pandas as pd
import io
import datetime
from motor_riesgo import MotorRiesgo, Solicitud, calcular_certeza

def main():
    st.set_page_config(page_title="CreditExpert AI", layout="wide")
    
    # Persistencia de datos
    if 'solicitud_enviada' not in st.session_state: st.session_state.solicitud_enviada = False
    if 'datos' not in st.session_state: st.session_state.datos = {}

    st.sidebar.title("💳 Sistema de Crédito")
    vista = st.sidebar.radio("Seleccionar Interfaz:", ["👤 Solicitante (Usuario)", "🔍 Analista de Riesgo (Experto)"])

    # --- VISTA USUARIO ---
    if vista == "👤 Solicitante (Usuario)":
        st.header("Formulario de Solicitud de Crédito")
        with st.form("user_form"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre Completo")
                monto = st.number_input("Monto solicitado ($)", min_value=1000)
                ingresos = st.number_input("Ingresos Netos Mensuales ($)", min_value=1)
                gastos = st.number_input("Pagos de Deudas Actuales ($)", min_value=0)
            with col2:
                buro = st.slider("Puntaje de Buró (Estimado)", 300, 850, 650)
                antiguedad = st.number_input("Años en empleo actual", 0, 40, 2)
                vivienda = st.selectbox("Situación de Vivienda", ["Propia", "Rentada", "Familiares"])
                dependientes = st.number_input("Número de Dependientes", 0, 10, 0)
            
            if st.form_submit_button("Enviar Solicitud"):
                st.session_state.datos = {
                    "nombre": nombre, "monto": monto, "ingresos": ingresos, "gastos": gastos,
                    "buro": buro, "antiguedad": antiguedad, "vivienda": vivienda,
                    "dependientes": dependientes, "dti": gastos / ingresos
                }
                st.session_state.solicitud_enviada = True
                st.success("¡Solicitud enviada con éxito! El analista revisará su caso.")

    # --- VISTA ANALISTA ---
    elif vista == "🔍 Analista de Riesgo (Experto)":
        st.header("Panel de Control de Decisiones Crediticias")
        
        if not st.session_state.solicitud_enviada:
            st.info("No hay solicitudes pendientes de análisis.")
        else:
            d = st.session_state.datos
            engine = MotorRiesgo()
            engine.reset()
            engine.declare(Solicitud(**d))
            engine.run()

            # Lógica de decisión final por score
            if engine.decision != "RECHAZADO":
                if engine.score_puntos >= 40: engine.decision = "APROBADO"
                elif engine.score_puntos >= 0: engine.decision = "SUJETO A CONDICIONES"
                else: engine.decision = "RECHAZADO"

            certeza = calcular_certeza(d)

            # --- PRESENTACIÓN DE RESULTADOS ---
            color = "green" if engine.decision == "APROBADO" else "red"
            st.markdown(f"<h1 style='text-align: center; color: {color};'>{engine.decision}</h1>", unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            c1.metric("Score Final", f"{engine.score_puntos} pts")
            c2.metric("Factor de Certeza", f"{certeza*100}%")
            c3.metric("Relación Deuda/Ingreso", f"{d['dti']:.1%}")

            st.subheader("📋 Justificación Técnica del Motor Experto")
            df_diag = pd.DataFrame(engine.diagnostico)
            st.table(df_diag)

            # --- GENERACIÓN DE EXCEL ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame([d]).to_excel(writer, sheet_name="Datos_Entrada", index=False)
                df_diag.to_excel(writer, sheet_name="Justificacion_Reglas", index=False)
                # Resumen ejecutivo
                resumen = {
                    "Nombre": d['nombre'], "Resultado": engine.decision, 
                    "Score": engine.score_puntos, "Certeza": certeza,
                    "Fecha": datetime.datetime.now()
                }
                pd.DataFrame([resumen]).to_excel(writer, sheet_name="Conclusion_Final", index=False)
            
            st.download_button(
                label="📥 Descargar Reporte de Auditoría (Excel)",
                data=output.getvalue(),
                file_name=f"Auditoria_Credito_{d['nombre']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__": # CORREGIDO: doble guion bajo
    main()