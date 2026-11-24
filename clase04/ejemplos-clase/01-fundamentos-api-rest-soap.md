# 1. Fundamentos de API, REST y SOAP

Objetivo: que distingan la puerta de la API, la base y la pantalla antes de abrir Postman.

## La frase de partida

«Una API es un contrato que permite que dos sistemas intercambien información. El cliente pide un recurso. El servidor responde una representación. Nosotros no vamos a escribir SQL.»

## Qué mostrar

Escribe esta URL y márcala:

`https://34.95.210.33.sslip.io/api/v4/productos/1`

- `https`: HTTP cifrado. La contraseña no viaja en claro.
- Host: `34.95.210.33.sslip.io`.
- Path: `/api/v4/productos/1`. El `1` es un path parameter.
- Un endpoint es el método más esa ruta. `GET` de productos y `POST` de login no son el mismo endpoint.

## REST y SOAP, sin mezclarlos

REST organiza recursos y no recuerda la petición anterior. JSON es lo habitual en esta API. REST no exige JSON.

SOAP envía un sobre XML y describe las operaciones en un WSDL. No está obligado a usar HTTP.

GraphQL y gRPC se nombran y no se practican.

## Pregunta

«¿Entrar a PostgreSQL con la contraseña del curso es lo mismo que llamar la API?»

No. La contraseña solo se presenta en el login. Las consultas de ventas las hace la API con otra cuenta, de solo lectura.

## Si no tienen Postman

Escuchan este bloque y dejan el cuaderno en la sección 00, sin ejecutar el login.
