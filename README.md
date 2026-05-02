# MCF-PRUEBA-APP
El presente proyecto tiene como objetivo analizar el riesgo financiero de distintos activos mediante la implementación de medidas cuantitativas ampliamente utilizadas en la gestión de riesgos: el **Value at Risk (VaR)** y el **Expected Shortfall (ES)**.
El análisis no se limita a una única metodología, sino que incorpora diferentes enfoques:

- Métodos históricos
- Métodos paramétricos (Normal y t-Student)
- Simulación Monte Carlo
- Modelos dinámicos con ventanas móviles (rolling window)
- Backtesting para validación de modelos
Este enfoque permite no solo estimar el riesgo, sino también evaluar la robustez y precisión de los modelos utilizados, lo cual es fundamental en contextos financieros reales.

Los datos fueron obtenidos de **Yahoo Finance** utilizando la librería `yfinance`.


### Activos analizados:
- BIMBOA.MX (Grupo Bimbo)
- AMX (América Móvil)
- GMEXICOB.MX (Grupo México)


Características de los datos que observamos:
- Frecuencia: diaria
- Variable base: precios de cierre
- Transformación: rendimientos diarios

Respecto a la frecuencia diaria podemos verla reflejada en la gr

Los rendimientos se calcularon a partir de los precios y se limpiaron eliminando valores faltantes (`NaN`) para asegurar consistencia en los cálculos.


Se calcularon las siguientes métricas estadísticas de cada uno de los activos:

### 3.1 Media
En nuestro caso la media de BIMBO fue de 0.0453%  lo cual es consistente con la teoría financiera, donde los retornos diarios no presentan tendencia significativa en el corto plazo. 


### 3.2 Sesgo 
El sesgo permite identificar asimetrías en la distribución:

- Sesgo negativo → mayor probabilidad de pérdidas extremas
- Sesgo positivo → mayor probabilidad de ganancias extremas

En activos financieros es común observar sesgo negativo, lo que implica mayor exposición a eventos adversos.

En este ejercicio el sesgo fue de 0.4135 lo cual nos permite analizar que vamos a tener mayor probablidad de tener ganancias a lo largo del tiempo y de igual manera la acción ha presentado algunos rendimientos superiores al promedio, aunque no de manera extrema, ya que el sesgo no es muy grande.

### 3.3 Curtosis (Exceso de curtosis)

La curtosis mide el grosor de las colas de la distribución:

- Curtosis > 0 → distribución leptocúrtica (colas pesadas)
- Curtosis ≈ 0 → distribución normal

Los resultados muestran curtosis positiva, lo que indica que los eventos extremos (crisis, caídas fuertes) son más frecuentes de lo que predice una distribución normal.
Los rendimientos no siguen una distribución normal estricta, lo cual impacta directamente la estimación del riesgo.

Nustra curtosis fue de 3.6254 el modelo tiene colas pesados la acción puede presentar algunos rendimientos extremos, tanto positivos como negativos, con una frecuencia ligeramente mayor a la esperada bajo normalidad.

## 4. Estimación de VaR y Expected Shortfall

Se calcularon las medidas de riesgo para niveles de confianza:

- 95%
- 97.5%
- 99%

### 4.1 Métodos utilizados

#### 🔹 Método histórico
- Basado en cuantiles empíricos
- No asume distribución
- Captura directamente el comportamiento observado

#### 🔹 Método paramétrico (Normal)
- Supone que los rendimientos siguen una distribución normal
- Puede subestimar el riesgo en presencia de colas pesadas

#### 🔹 Método paramétrico (t-Student)
- Considera colas más pesadas
- Se utilizó con 5 grados de libertad
- Más adecuado para datos financieros

#### 🔹 Simulación Monte Carlo
- Genera escenarios simulados
- Basado en supuestos de media y volatilidad
- Permite aproximar distribuciones complejas


### Resultados clave: BIMBOA.MX con nivel de confianza 97.5%

Pra el metodo Histórico  nos dio el resultado de VaR -3.45%.
Para el metodo Normal el resultado del VaR fue de  -3.55%.
Para el método de t-Student el resultado del VaR fue de -3.69%.
Para el resultado de  Monte Carlo el VaR fue de  -3.58%.

El VaR cercano a -3.5% indica que, bajo el nivel de confianza analizado, la pérdida diaria no debería exceder aproximadamente ese umbral en condiciones normales de mercado.

El resultado del metodo Historico del ES fue de -4.50% . 
El resultado del metodo Normal del ES fue de -4.59% 
El resultado del metodo T-Student del ES fue de-4.76% 
El resultado del metodo Monte Carlo del ES fue de-4.64% 

Por otro lado, el ES cercano a -4.5% muestra que, cuando el rendimiento cae más allá del VaR, la pérdida promedio esperada es considerablemente mayor. Esto evidencia que el VaR solo señala un punto de corte, mientras que el ES captura la severidad de la cola izquierda.

### 4.2 Interpretación de resultados

- El VaR indica la pérdida máxima esperada con cierto nivel de confianza
- El ES (CVaR) mide la pérdida promedio en escenarios extremos

### Hallazgos importantes:

- El modelo normal tiende a subestimar el riesgo
- El modelo t-Student y el histórico son más conservadores
- El CVaR siempre es más severo que el VaR, ya que considera la cola completa
Esto confirma que los mercados presentan colas pesadas y riesgo extremo no despreciable y que la diferencia entre métodos y la elección del modelo impacta directamente la medición del riesgo, especialmente en escenarios extremos.

## 5. Análisis visual de la distribución

Se construyeron histogramas con:

- Distribución de rendimientos
- Líneas de VaR y CVaR para distintos métodos
- Zona de pérdidas destacada


El análisis gráfico de los rendimientos muestra la presencia de asimetría negativa y colas pesadas.

En la gráfica de distribución se observa que el VaR funciona como un umbral de pérdida, mientras que el ES se ubica más hacia la cola izquierda. Esto es relevante porque el ES no solo identifica cuándo se rebasa un umbral, sino que mide la pérdida promedio en los peores escenarios.

Por esta razón, el Expected Shortfall ofrece una lectura más completa del riesgo extremo.

##Interpretación:

- Se observa claramente que la cola izquierda (pérdidas) es relevante
- Las diferencias entre métodos reflejan distintos niveles de conservadurismo
- El VaR histórico se ajusta mejor a la distribución empírica


## 6. Análisis dinámico: Rolling Window

Se implementó un modelo de riesgo dinámico usando ventanas móviles de:

- 252 días (aprox. 1 año bursátil)
- 253 y 254 días (comparación)

Este enfoque permite que las medidas de riesgo se actualicen conforme cambia la información disponible. En lugar de calcular un VaR y ES estáticos para toda la muestra, se estima el riesgo usando únicamente una ventana reciente de rendimientos.

### Variables calculadas:

- Media móvil
- Volatilidad móvil
- VaR paramétrico
- CVaR paramétrico
- VaR histórico
- CVaR histórico

Podemos notar que 
- El riesgo no es constante en el tiempo.
- Se identifican periodos de alta volatilidad.
- El VaR y el ES aumentan en momentos de estrés financiero.
- Se observa clustering de volatilidad, típico en series financieras.

Cuando la volatilidad aumenta, el VaR se vuelve más negativo y el ES aumenta de forma más agresiva. Esto confirma que el riesgo depende del estado del mercado.


## 7. Backtesting (Validación de modelos)

Se evaluó la calidad de las estimaciones mediante el conteo de violaciones.

Una violación ocurre cuando:

Rendimiento observado < VaR o ES estimado

El objetivo del backtesting es verificar si el modelo subestima o sobreestima el riesgo.

En nuestro caso se estimo para el 95% y 99% para los metodos Normal e Historico con una ventana de tiempo de 252 días. 

En nuetro caso las filas 1 y tres sobrepasan el valor de 2.5% por lo que son modelos que convendria se revisaran pues sus estimaciones de VaR tanto parametrico como historico estan fuera del rango considerado aceptable en un modelo. 



### Metodología:

- Se utilizan ventanas rolling
- Se compara la estimación con el rendimiento siguiente
- Se evalúan dos métodos:
  - Paramétrico normal
  - Histórico
- Se cuentan el numero total de violaciones 
- Se una el numero total de evaluaciones para ver que porcentaje cumpio la condicion de violacion


### 7.1 Criterio de evaluación

- Un modelo es adecuado si el porcentaje de violaciones es bajo
- En el proyecto se utiliza el criterio:
  
> ✔ Buen modelo si violaciones < 2.5%


### 7.2 Interpretación

- Muchas violaciones → el modelo subestima el riesgo
- Pocas violaciones → modelo conservador
- Buen balance → modelo confiable
- El modelo histórico suele comportarse mejor
- El modelo normal puede fallar en eventos extremos


## 8. VaR con volatilidad móvil

Se implementó un modelo adicional donde el VaR depende de una volatilidad estimada dinámicamente mediante una ventana de 252 días.

Este enfoque utiliza cuantiles de la distribución normal estándar y una desviación estándar móvil. La ventaja principal es que el modelo reacciona a cambios recientes en el mercado.

### Hallazgos principales

- Responde mejor a cambios recientes de volatilidad.
- Captura de forma más adecuada periodos de alta incertidumbre.
- Es más realista que un VaR estático.
- El VaR depende de una volatilidad estimada dinámicamente
- Se usa una ventana de 252 días
- Se aplican niveles de significancia:
  - α = 0.05
  - α = 0.01

### Interpretación:

- El VaR se ajusta a cambios recientes en la volatilidad
- Es más reactivo que el VaR estático
- Mejora la capacidad de capturar cambios en el riesgo

La gráfica muestra que, cuando los rendimientos presentan mayor dispersión, el VaR con volatilidad móvil se ajusta y se vuelve más conservador.


## 9. Violaciones del modelo con volatilidad móvil

Se evaluó el desempeño del modelo mediante:

- Número de violaciones
- Porcentaje de violaciones

### Resultados esperados:

- α = 0.05 → ~5% violaciones
- α = 0.01 → ~1% violaciones

### Conclusión:

- Si los resultados se acercan a estos valores → modelo bien calibrado
- Si no → ajuste necesario


## 10. Conclusiones generales

Los resultados muestran que los rendimientos financieros presentan desviaciones importantes respecto a la normalidad, particularmente por la presencia de colas pesadas y asimetría negativa.
Esto implica que modelos simplificados, como el VaR normal, pueden no ser suficientes para capturar el riesgo real, especialmente en escenarios extremos.
El Expected Shortfall resulta una medida más robusta que el VaR, ya que considera la magnitud promedio de las pérdidas más severas. Además, el análisis rolling demuestra que el riesgo financiero es dinámico y cambia a lo largo del tiempo.
En conjunto, el proyecto demuestra que una adecuada medición del riesgo requiere combinar diferentes metodologías, analizar visualmente los resultados y validar los modelos mediante backtesting.

## 11. Tecnologías utilizadas

- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- SciPy
- yFinance
-Capi Maximiliano.  
