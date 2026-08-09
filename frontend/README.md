# frontend/ (placeholder)

Esta carpeta es un placeholder. El frontend real de Ruta Agustina es un
proyecto aparte en React, desplegado en Vercel. Este `Dockerfile` mínimo
solo existe para que `docker compose up`, desde la raíz del monorepo, pueda
levantar backend + frontend juntos en desarrollo local sin fallar, incluso
antes de que el código real del frontend viva en esta carpeta.

Cuando el frontend real se incorpore aquí (o como submódulo/otro
repositorio enlazado), reemplaza este `Dockerfile` por el suyo.
