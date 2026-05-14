# Respuestas Control 1

**Integrante:** Igor Assis, Nelson Alejandro Navarro Barria

---

## Pregunta 1: ¿Cómo implementarías el envío de la imagen para los sitios bloqueados?

Básicamente cambiaría la respuesta HTML que está ahora (líneas 108-115) por una imagen. Tendría que leer el archivo de imagen en modo binario, cambiar el header Content-Type a "image/jpeg" o "image/png" según corresponda, y mandar los bytes de la imagen directo en el body de la respuesta HTTP 403. También podría dejarlo como HTML pero metiendo la imagen en base64 con un tag img.

---

## Pregunta 2: En las líneas 105 y 106 buscan en additional_ips si está el nombre actual, ¿por qué hicieron eso?, ¿qué es lo que evita?, ¿cómo sería el flujo del resolver sin esas 2 líneas?

Eso lo hicimos porque cuando un servidor DNS te responde con registros NS (servidores autoritativos), muchas veces también te manda los registros A de esos mismos NS en la sección additional. Entonces primero revisamos si ya tenemos la IP ahí antes de hacer otra consulta.

Sin esas líneas, el resolver siempre tendría que hacer una consulta recursiva extra para resolver la IP del servidor NS, incluso cuando ya venía en la respuesta original. Sería más lento y gastaría más recursos haciendo consultas que no son necesarias.
