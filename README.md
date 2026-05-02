# Métodos Cuantitativos en Finanzas - Proyecto 1

Integrantes del equipo:
- López Fuentes Paula Juliana
- Olavarria Guerra Bruno
- Reyes Díaz Axel Gabriel
- Toledo Camargo Ulises

El presente proyecto tiene como objetivo analizar el riesgo financiero de distintos activos mediante la implementación de medidas cuantitativas ampliamente utilizadas en la gestión de riesgos: el **Value at Risk (VaR)** y el **Expected Shortfall (ES)**.
El análisis no se limita a una única metodología, sino que incorpora diferentes enfoques:

- Métodos históricos
- Métodos paramétricos (Normal y t-Student)
- Simulación Monte Carlo
- Modelos dinámicos con ventanas móviles (rolling windows)
- Backtesting para validación de modelos
Este enfoque permite no solo estimar el riesgo, sino también evaluar la robustez y precisión de los modelos utilizados, lo cual es fundamental en contextos financieros reales.

Los datos fueron obtenidos de **Yahoo Finance** utilizando la librería `yfinance`.

## 1. Activos analizados:
- BIMBOA.MX (Grupo Bimbo)
- AMX (América Móvil)
- GMEXICOB.MX (Grupo México)


Características de los datos que observamos:
- Frecuencia: diaria
- Variable base: precios de cierre
- Transformación: rendimientos diarios

Respecto a la frecuencia diaria podemos verla reflejada en la grafica de manera interactiva, el puntero nos podrá dar la el rendimiento de ese dia y nos podrá dar el fecha en donde nos situémos.

Los rendimientos se calcularon a partir de los precios y se limpiaron eliminando valores faltantes (`NaN`) para asegurar consistencia en los cálculos.

Se calcularon las siguientes métricas estadísticas de cada uno de los activos:

### 2.1. Media
En nuestro caso la media de BIMBO fue de 0.0453%  lo cual es consistente con la teoría financiera, donde los retornos diarios no presentan tendencia significativa en el corto plazo. 

### 2.2. Sesgo 
El sesgo permite identificar asimetrías en la distribución:

- Sesgo negativo → mayor probabilidad de pérdidas extremas
- Sesgo positivo → mayor probabilidad de ganancias extremas

En activos financieros es común observar sesgo negativo, lo que implica mayor exposición a eventos adversos.

En este ejercicio el sesgo fue de 0.4135 lo cual nos permite analizar que vamos a tener mayor probablidad de tener ganancias a lo largo del tiempo y de igual manera la acción ha presentado algunos rendimientos superiores al promedio, aunque no de manera extrema, ya que el sesgo no es muy grande.

### 2.3. Esceso de Curtosis
La curtosis mide el grosor de las colas de la distribución:

- Curtosis > 0 → distribución leptocúrtica (colas pesadas)
- Curtosis ≈ 0 → distribución normal

Nustro cálculo del exceso de curtosis fue de 3.6254, es decir, una curtosis positiva (Exceso de curtosis - 3 = 0.6254) por lo que podemos decir que el modelo tiene colas pesadas y la acción puede presentar algunos rendimientos extremos, tanto positivos como negativos, con una frecuencia ligeramente mayor a la esperada bajo normalidad. Esto nos lleva a penaser que los rendimientos no siguen una distribución normal, como ya hemos visto en clase, lo cual impacta directamente la estimación del riesgo.

## 3. Estimación de Value at Risk (VaR) y Expected Shortfall (ES)
Se calcularon las medidas de riesgo para niveles de confianza:
- 95%
- 97.5%
- 99%

### 3.1 Métodos utilizados

#### 🔹 Método histórico
- Basado en cuantiles empíricos
- No asume distribución
- Captura directamente el comportamiento observado

#### 🔹 Método paramétrico (Normal)
- Supone que los rendimientos siguen una distribución normal
- Puede subestimar el riesgo en presencia de colas pesadas

#### 🔹 Método paramétrico (t-Student)
- Considera colas más pesadas
- Se utilizó la función `t.fit` de la librería `spicy.stats` para ajustar los grados de libertad según los rendimientos observados.
- Más adecuado para datos financieros

#### 🔹 Simulación Monte Carlo
- Genera escenarios simulados
- Basado en supuestos de media y volatilidad
- Permite aproximar distribuciones complejas


### Resultados para la acción BIMBOA.MX con nivel de confianza 97.5%
Con el método Histórico el resultado del VaR fue de -3.45%.
Con el método Normal el resultado del VaR fue de -3.55%.
Con el método de t-Student el resultado del VaR fue de -3.69%.
Con el método de Monte Carlo el resultado del VaR fue de -3.58%.

El VaR cercano a -3.5% indica que, bajo el nivel de confianza analizado, la pérdida diaria no debería exceder aproximadamente ese umbral en condiciones normales de mercado.

El resultado del método Historico del ES fue de -4.50% . 
El resultado del método Normal del ES fue de -4.59% 
El resultado del método t-student del ES fue de -4.76% 
El resultado del método Monte Carlo del ES fue de -4.63% 

Por otro lado, el ES cercano a -4.5% muestra que, cuando el rendimiento cae más allá del VaR, la pérdida promedio esperada es considerablemente mayor. Esto evidencia que el VaR solo señala un punto de corte, mientras que el ES captura la severidad de la cola izquierda.

### 3.2 Interpretación de resultados
- El VaR indica la pérdida máxima esperada con cierto nivel de confianza.
- El ES (CVaR) mide la pérdida promedio en escenarios extremos.

### Hallazgos importantes:
- El modelo normal y el histórico tienden a subestimar el riesgo en casos que caen en las colas de la distribución.
- El modelo t-Student es más conservador.
- El CVaR siempre es más severo que el VaR, ya que considera la cola completa
Esto confirma que los mercados presentan colas pesadas y ciertos riesgos más extremos no despreciables y que la diferencia entre métodos y la elección del modelo impacta directamente la medición del riesgo.

## 4. Análisis visual de la distribución
Se construyeron histogramas con:
- Distribución de rendimientos
- Líneas de VaR y CVaR para distintos métodos
- Zona de pérdidas destacada

En la gráfica de distribución se observa que el VaR funciona como un umbral de pérdida, mientras que el ES se ubica más hacia la cola izquierda. Esto es relevante porque el ES no solo identifica cuándo se rebasa un umbral, sino que mide la pérdida promedio en los peores escenarios.

Por esta razón, el Expected Shortfall ofrece una lectura más completa del riesgo extremo.

#### Interpretación:
- Se observa claramente que la cola izquierda (pérdidas) es relevante.
- Las diferencias entre métodos reflejan distintos niveles de conservadurismo.
- El VaR histórico se ajusta mejor a la distribución empírica.

## 5. Análisis dinámico: Rolling Windows
Se implementó un modelo de riesgo dinámico usando ventanas móviles de:
- 252 días (aprox. 1 año bursátil)

Este enfoque permite que las medidas de riesgo se actualicen conforme cambia la información disponible. En lugar de calcular un VaR y ES estáticos para toda la muestra, se estima el riesgo usando una ventana móvil de los rendimientos.

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

## 6. Backtesting (Validación de modelos)
Se evaluó la calidad de las estimaciones mediante el conteo de violaciones. Una violación ocurre cuando el rendimiento observado es menor que el VaR o ES estimado.
El objetivo del backtesting es verificar si el modelo subestima o sobreestima el riesgo.

En nuestro caso se estimo para el 95% y 99% para los metodos Normal e Historico con una ventana de tiempo de 252 días. 

En nuetro caso las filas 1 y tres sobrepasan el valor de 2.5% (definido por el profesor como "Una buena estimación genera un porcentaje de violaciones menores al 2.5%") por lo que son modelos que convendria se revisaran pues sus estimaciones de VaR tanto parametrico como historico estan fuera del rango considerado aceptable en un modelo. 

### Metodología:
- Se utilizan ventanas móviles.
- Se compara la estimación con el rendimiento siguiente (consideramos 252 rendimientos para estimar el VaR asociado al rendimiento número 253).
- Se evalúan dos métodos:
  - Paramétrico con una distribución Normal.
  - Histórico.
- Se cuentan el número total de violaciones.
- Se suma el número total de evaluaciones para ver que porcentaje cumplio la condición de violación que definimos anteriormente.

### 6.1 Criterio de evaluación
Un modelo es adecuado si el porcentaje de violaciones es bajo, en nuestro caso, lo será si el porcentaje de violaciones es menor a 2.5%.

### 6.2 Interpretación
- En el caso de muchas violaciones, implica que el modelo subestima el riesgo.
- En el caso de muy pocas violaciones, implica que el modelo es conservador.
- En el caso de un buen balance, el modelo lo consideraremos confiable.
- El modelo histórico suele comportarse mejor en contraste a que el modelo normal puede fallar en eventos extremos.

## 7. VaR con volatilidad móvil
Se implementó un modelo adicional donde el VaR depende de una volatilidad estimada dinámicamente mediante una ventana de 252 días con niveles de confianza del 95% y 99%.

Este enfoque utiliza cuantiles de la distribución normal y una desviación estándar móvil. La ventaja principal es que el modelo reacciona a cambios recientes en el mercado.

### Hallazgos principales
- Responde mejor a cambios recientes de volatilidad.
- Captura de forma más adecuada periodos de alta incertidumbre.
- Es más realista que un VaR estático.
- El VaR depende de una volatilidad estimada dinámicamente.
- Mejora la capacidad de capturar cambios en el riesgo.

La gráfica muestra que, cuando los rendimientos presentan mayor dispersión, el VaR con volatilidad móvil se ajusta y se vuelve más conservador.

## 8. Violaciones del modelo con volatilidad móvil
Se evaluó el desempeño del modelo mediante:
- Número de violaciones
- Porcentaje de violaciones

### Resultados esperados:
- Con α = 95% esperariamos aproximadamente un 5% de violaciones.
- Con α = 99% esperariamos aproximadamente un 1% de violaciones.

### Conclusión:
- Si los resultados se acercan a estos valores, entonces el modelo está bien calibrado.
- Si no, es necesario un ajuste.

## 9. Conclusiones generales
Los resultados muestran que los rendimientos financieros presentan desviaciones importantes respecto a la normalidad, particularmente por la presencia de colas pesadas y asimetría negativa.
Esto implica que modelos simplificados, como el VaR paramétrico de una distribución normal, pueden no ser suficientes para capturar el riesgo real, especialmente en escenarios extremos.
El Expected Shortfall resulta una medida más robusta que el VaR, ya que considera la magnitud promedio de las pérdidas más severas, a cambio de ser más conservador. Además, el análisis de las Rolling Windows demuestra que el riesgo financiero es dinámico y cambia a lo largo del tiempo.
En conjunto, el proyecto demuestra que una adecuada medición del riesgo requiere combinar diferentes metodologías, analizar visualmente los resultados y validar los modelos mediante backtesting.

## 10. Tecnologías utilizadas
- Python
- Streamlit
- Pandas
- NumPy
- Matplotlib
- SciPy
- Yahoo Finance
