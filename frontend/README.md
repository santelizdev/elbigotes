# Elbigotes Frontend

Cliente público en Next.js para explorar el ecosistema pet sobre mapa, con prioridad en velocidad de lectura, búsqueda geolocalizada y publicación de mascotas perdidas.

## Variables de entorno

Usa `frontend/.env.example` como base.

- `NEXT_PUBLIC_SITE_URL`
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_DEFAULT_LAT`
- `NEXT_PUBLIC_DEFAULT_LNG`
- `NEXT_PUBLIC_DEFAULT_ZOOM`
- `NEXT_PUBLIC_USE_MOCKS`

## Desarrollo local

```bash
cd frontend
npm install
npm run dev
```

## Notas de arquitectura

- `src/app`: rutas públicas con App Router.
- `src/components`: piezas de UI y composición de experiencias.
- `src/lib/services`: cliente HTTP y adaptadores del backend Django.
- `src/lib/mocks`: fallback ordenado mientras el backend no esté disponible.
- `src/hooks`: estado de exploración del mapa sin introducir librerías de estado global demasiado pronto.

