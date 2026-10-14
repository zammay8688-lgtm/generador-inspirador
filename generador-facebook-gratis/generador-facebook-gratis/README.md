# Generador diario para Facebook

## 1. Subir a GitHub
1. Crea un repositorio público nuevo.
2. Sube todo el contenido de esta carpeta.
3. En Settings > Pages, selecciona **Deploy from a branch**, rama `main`, carpeta `/public`.

## 2. Configurar secretos
En Settings > Secrets and variables > Actions agrega:
- Secret `FACEBOOK_PAGE_ID`
- Secret `FACEBOOK_PAGE_ACCESS_TOKEN`
- Variable `META_GRAPH_VERSION` con la versión vigente indicada por Meta, por ejemplo `vXX.X`.
- Variable `NOMBRE_PAGINA` con tu firma visible.

No escribas tokens dentro del código.

## 3. Primera prueba
Ve a Actions > Generar y publicar frase diaria > Run workflow.
El horario configurado es 13:00 UTC, equivalente a 07:00 en Ciudad de México.

## 4. Liga pública
Después de activar Pages, GitHub mostrará la dirección pública en Settings > Pages.

## Importante
La automatización está diseñada para una Página de Facebook administrada por ti, no para un perfil personal. Revisa los permisos y la versión vigente de Graph API en Meta for Developers.
