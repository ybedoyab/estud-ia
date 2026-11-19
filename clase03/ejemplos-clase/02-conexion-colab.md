# 2. Conexión desde Colab

Objetivo: que cada estudiante entre con su cuenta y vea un DataFrame.

Concepto: Colab está fuera de la VM. La conexión va cifrada al puerto 6432 y el certificado se valida.

Qué decir: «la contraseña se pide ocultándola. No la peguen en el cuaderno ni en el chat».

Demostración: celdas de credenciales y de `SELECT 1`.

Resultado esperado: una fila `conexion_ok` con el valor 1.

Pregunta: ¿por qué el usuario `estudiante`, sin número, no sirve para el pipeline?

Error frecuente: `sslmode` sin el certificado, o usar el host equivocado.

Corrección: no cambien `DB_HOST`, `DB_PORT` ni `DB_NAME`. Si la contraseña falló, ejecuten otra vez solo esa celda.

Transición: «ya tenemos filas. Pandas las resume sin volver a escribir SQL».
