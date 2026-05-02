'''
Este es un Scrit generado para almacenar todas las funciones que
utilizaremos en la entrega del 1er proyecto de MCF :D

Autores:
- López Fuentes Paula Juliana
- Olavarria Guerra Bruno
- Reyes Díaz Axel Gabriel
- Toledo Camargo Ulises

'''
# ---------------------------- #
#    PAQUETERÍAS NECESARIAS    #  
# ---------------------------- #

# Manejo de datos
import pandas as pd
import numpy as np

# Cache
import streamlit as st
 
# Visualizacion de datos
import matplotlib.pyplot as plt

# Api de Yahoo Finanzas
import yfinance as yf

# Distribuciones
from scipy.stats import kurtosis, skew, norm, t

@st.cache_data
def obtener_datos(ticker):
    '''
    Descargamos el precio de cierre de uno o
    varios activos desde el 2010

    Input = Ticker del activo en string (Lista o elemento único)
    Output = DataFrame del precio del o de los activos

    '''
    df = yf.download(ticker, start="2010-01-01")['Close']
    return df

@st.cache_data
def calcular_rendimientos(df):
    '''
    Calculamos los rendimientos de un activo

    Input = Data Frame de precios por activo
    Output = Data Frame de rendimientos

    '''
    return df.pct_change().dropna()

def rolling_cvar(x, alpha):
    var = np.quantile(x, 1 - alpha)
    return x[x <= var].mean()

def calcular_var_historico(rendimientos, alpha=0.95):
    return rendimientos.quantile(1 - alpha)

def calcular_es_historico(rendimientos, var):
    return rendimientos[rendimientos <= var].mean()

def verificar_violaciones(rendimientos, var, es):
    violacion_var = rendimientos < var
    violacion_es = rendimientos < es

    tabla = pd.DataFrame({
        "Rendimiento": rendimientos,
        "VaR": var,
        "ES": es,
        "Violacion VaR": violacion_var,
        "Violacion ES": violacion_es
    })
    return tabla
    
def calcular_violaciones(serie, ventana, alpha):

    rolling_mean = serie.rolling(window=ventana).mean()
    rolling_std = serie.rolling(window=ventana).std()

    df_bt = pd.DataFrame({"Rendimiento": serie})

    df_bt["VaR Param"] = norm.ppf(1 - alpha, rolling_mean, rolling_std)

    z = norm.ppf(1 - alpha)

    df_bt["CVaR Param"] = rolling_mean - (
        rolling_std * norm.pdf(z) / (1 - alpha)
    )

    df_bt["VaR Hist"] = serie.rolling(window=ventana).quantile(1 - alpha)

    df_bt["CVaR Hist"] = serie.rolling(window=ventana).apply(
        lambda x: x[x <= np.quantile(x, 1 - alpha)].mean(),
        raw=False
    )

    cols = ["VaR Param", "CVaR Param", "VaR Hist", "CVaR Hist"]

    df_bt[cols] = df_bt[cols].shift(1)

    df_bt = df_bt.dropna()

    return df_bt

def color_filas(row):
    if row["Porcentaje"] > 2.5:
        return ["background-color: #f4a261"] * len(row)  # naranja suave
    return [""] * len(row)