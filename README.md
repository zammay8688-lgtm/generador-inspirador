# Reflexiones Facebook 2000

Genera 2,000 publicaciones visuales únicas sin guardar 2,000 PNG pesados. Combina 2,000 frases exclusivas con 10 paletas, adornos variables, 8 temas y la fecha actual.

## Frecuencia incluida
Publica cuatro veces al día, aproximadamente a las 08:00, 12:00, 16:00 y 20:00 de Ciudad de México. GitHub cron funciona en UTC y puede tener retrasos.

## Instalación
1. Sube todo a un repositorio privado de GitHub.
2. En Settings > Secrets and variables > Actions crea `FB_PAGE_ID` y `FB_PAGE_TOKEN`.
3. En Actions ejecuta manualmente `Reflexiones Facebook 2000` para probar.
4. Revisa la Página antes de dejar activados los cuatro horarios.

## No repetición
El índice depende de la fecha y de la franja horaria. Hay 2,000 combinaciones exactas; a cuatro publicaciones por día el ciclo cubre 500 días antes de volver al inicio.

## Cambiar frecuencia
Edita `.github/workflows/publicar.yml`. Para reducir a dos publicaciones, conserva únicamente `0 14 * * *` y `0 22 * * *`.

## Seguridad
Nunca escribas el token en los archivos. Guárdalo únicamente como GitHub Secret. Si Meta devuelve un error de límite o autorización, pausa el workflow y revisa el token y los permisos.
