import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
from motor_ia import entrenar_modelo_ml, MotorRiesgo, Solicitud

# Ejecución inicial del entrenamiento (se guarda en caché por Streamlit)
@st.cache_resource
def cargar_modelo():
    return entrenar_modelo_ml()

modelo_ml, encoder_clases, accuracy_cv = cargar_modelo()

def main():
    st.set_page_config(page_title="CreditExpert Híbrido AI", layout="wide")
    
    if 'solicitud_enviada' not in st.session_state: st.session_state.solicitud_enviada = False
    if 'datos' not in st.session_state: st.session_state.datos = {}

    st.sidebar.title("💳 Sistema de Crédito Híbrido")
    vista = st.sidebar.radio("Navegación:", ["👤 Solicitante (Usuario)", "🔍 Analista de Riesgo (Experto)"])

    # --- PANTALLA DEL CLIENTE ---
    if vista == "👤 Solicitante (Usuario)":
        st.header("Formulario de Solicitud de Crédito")
        with st.form("user_form"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre Completo", "María Teresa Castillo")
                monto = st.number_input("Monto solicitado ($)", min_value=1000, value=15000)
                ingresos = st.number_input("Ingresos Netos Mensuales ($)", min_value=1, value=45000)
                gastos = st.number_input("Pagos de Deudas Actuales ($)", min_value=0, value=8000)
            with col2:
                buro = st.slider("Puntaje de Buró de Crédito", 300, 850, 710)
                antiguedad = st.number_input("Años en empleo actual", 0, 40, 4)
                vivienda = st.selectbox("Situación de Vivienda", ["Propia", "Rentada", "Familiares"])
                dependientes = st.number_input("Número de Dependientes", 0, 10, 1)
            
            if st.form_submit_button("Enviar Solicitud"):
                st.session_state.datos = {
                    "nombre": nombre, "monto": monto, "ingresos": ingresos, "gastos": gastos,
                    "buro": buro, "antiguedad": antiguedad, "vivienda": vivienda,
                    "dependientes": dependientes, "dti": gastos / ingresos
                }
                st.session_state.solicitud_enviada = True
                st.success("¡Datos enviados con éxito! Pase a la vista de Analista de Riesgo.")

    # --- PANTALLA DEL EXPERTO / ANALISTA ---
    elif vista == "🔍 Analista de Riesgo (Experto)":
        st.header("Panel de Decisiones Híbrido (Sistemas Expertos + ML)")
        
        if not st.session_state.solicitud_enviada:
            st.info("No hay solicitudes entrantes para analizar.")
        else:
            d = st.session_state.datos
            
            # --- COMPONENTE 1: EJECUCIÓN DEL SISTEMA EXPERTO ---
            engine = MotorRiesgo()
            engine.reset()
            engine.declare(Solicitud(**d))
            engine.run()

            if engine.decision != "RECHAZADO":
                if engine.score_puntos >= 40: engine.decision = "Aprobado"
                elif engine.score_puntos >= 0: engine.decision = "Sujeto a Aval"
                else: engine.decision = "Rechazado"

            # --- COMPONENTE 2: PREDICCIÓN DEL MODELO DE MACHINE LEARNING ---
            certeza_calculada = (0.4 if d['antiguedad'] >= 3 else 0.1) + (0.3 if d['buro'] >= 600 else 0.1) + 0.3
            
            input_features = pd.DataFrame([{
                "Ingreso_Mensual": d['ingresos'],
                "Buro_Credito_Score": d['buro'],
                "Factor_Certeza_CF": certeza_calculada * 100
            }])
            
            # Predicción estadística probabilística
            pred_encoded = modelo_ml.predict(input_features)[0]
            dictamen_ml = encoder_clases.inverse_transform([pred_encoded])[0]
            probabilidades = modelo_ml.predict_proba(input_features)[0]
            confianza_prediccion = np.max(probabilidades)

            # --- INTERFAZ GRÁFICA COMPARATIVA ---
            st.subheader("💡 Contraste de Criterios Automáticos")
            c1, c2 = st.columns(2)
            
            with c1:
                st.metric("Dictamen del Sistema Experto (Políticas)", engine.decision)
                st.caption(f"Puntuación acumulada por reglas de negocio: {engine.score_puntos} pts")
            with c2:
                st.metric("Predicción Machine Learning (Histórico)", dictamen_ml)
                st.caption(f"Probabilidad estadística del modelo entrenado: {confianza_prediccion*100:.1f}%")

            st.markdown("---")
            st.subheader("📊 Métricas del Módulo Estadístico Supervisado")
            col_m1, col_m2 = st.columns(2)
            col_m1.metric("Dataset de Entrenamiento Base", "100 Clientes Registrados")
            col_m2.metric("Exactitud Promedio (5-Fold Cross Validation)", f"{accuracy_cv*100:.2f}%")

            # Mostrar logs lógicos
            st.subheader("📋 Justificación de Reglas del Sistema Experto")
            df_diag = pd.DataFrame(engine.diagnostico)
            st.table(df_diag)

            # --- EXPORTACIÓN DE AMBOS CRITERIOS A EXCEL ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                pd.DataFrame([d]).to_excel(writer, sheet_name="Datos_Solicitud", index=False)
                df_diag.to_excel(writer, sheet_name="Auditoria_Reglas_SE", index=False)
                
                resumen_hibrido = {
                    "Cliente": d['nombre'],
                    "Dictamen_Sistema_Experto": engine.decision,
                    "Prediccion_Machine_Learning": dictamen_ml,
                    "Confianza_Estadistica": f"{confianza_prediccion*100:.2f}%",
                    "Validacion_Cruzada_Dataset": f"{accuracy_cv*100:.2f}%",
                    "Fecha_Evaluacion": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                pd.DataFrame([resumen_hibrido]).to_excel(writer, sheet_name="Dictamen_Hibrido", index=False)
            
            st.download_button(
                label="📥 Descargar Reporte de Auditoría Híbrido (Excel)",
                data=output.getvalue(),
                file_name=f"Auditoria_Hibrida_{d['nombre']}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

if __name__ == "__main__": # CORREGIDO
    main()