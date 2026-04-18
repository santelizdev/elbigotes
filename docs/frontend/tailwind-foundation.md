# Tailwind Foundation & Frontend Governance

## Objetivo

Estandarizar el frontend para que el equipo pueda iterar sin depender de estilos dispersos,
clases globales improvisadas o CSS modules en cada pantalla.

Esta base introduce Tailwind como infraestructura visual y de layout, pero sin una migración
masiva de una sola vez.

## Qué se implementó

### 1. Base Tailwind

- Se agregó Tailwind al frontend como capa base.
- `frontend/src/app/globals.css` ahora importa Tailwind y expone tokens del sistema visual actual.
- Los tokens visuales existentes siguen viviendo en CSS variables para soportar tema claro/oscuro.
- Tailwind se usa como base de:
  - layout
  - spacing
  - tipografía utilitaria
  - estados comunes

### 2. Componentes núcleo iniciales

Se dejaron listas estas piezas como base del sistema:

1. `Button`
2. `Tag`
3. `StatusPill`
4. `FeedbackPanel`
5. `PageShell`
6. `PageHero`
7. `SectionHeader`
8. `SurfaceCard`
9. `DashboardGrid`
10. `FormGrid`
11. `FormField`
12. `InfoBox`
13. `TextButton`
14. `SkeletonCard`
15. `MapLoadingShell`
16. `MapLegend`

También se conectaron componentes compartidos a esta capa:

- `ErrorState`
- `EmptyState`
- `LoadingPanel`

### 3. Primeras adopciones

Sin entrar en una migración big bang, se aplicó el nuevo estándar en piezas estratégicas:

- `RegistrationHub`
- `AccountAccessNotice`
- componentes compartidos de feedback
- `SiteHeader`
- `ExplorerToolbar`
- `CategoryFilterBar`
- `MapExplorerPage`
- `PlaceCard`
- `PlaceGoogleRating`
- `PlaceLoopActions`
- `PlaceList`
- `PlaceDetailSheet`
- `PlaceProfile`
- `LostPetsExplorer`
- `LostPetReportCard`
- `LostPetReportForm`
- `TextButton`
- `SkeletonCard`
- `MapLoadingShell`
- `MapLegend`
- `AccountLoginForm`
- `BusinessRegistrationForm`
- `PetOwnerRegistrationForm`
- `ClaimRequestForm`
- `BusinessDashboard`
- `PetOwnerDashboard`
- `BusinessProfileEditForm`
- `BusinessBranchCreateForm`
- `ReviewsPage`

Esto deja un patrón real de referencia para migraciones futuras.

## Reglas obligatorias

Estas reglas se deben respetar en cualquier cambio futuro:

1. Tailwind como base de layout y spacing.
2. Componentes propios del proyecto encima de Tailwind.
3. CSS modules solo donde haya casos muy específicos.
4. Nada de migración masiva “big bang”.
5. Documentar 8 a 12 componentes núcleo y 3 a 4 layouts patrón.

## Qué significa cada regla

### Tailwind como base de layout y spacing

Todo lo estructural debe resolverse primero con Tailwind:

- grids
- stacks
- gaps
- paddings
- margins
- containers
- alineación
- estados visuales simples

No crear CSS nuevo para resolver cosas que Tailwind cubre claramente.

### Componentes propios del proyecto encima

No queremos una app escrita con clases utilitarias repetidas en cada página.

La regla es:

- Tailwind resuelve la infraestructura
- los componentes del proyecto encapsulan decisiones repetidas

Ejemplos:

- `Button`
- `TextButton`
- `SurfaceCard`
- `SectionHeader`
- `FeedbackPanel`

Si una combinación de clases aparece más de dos o tres veces, se debe extraer a componente.

### CSS modules solo donde haya casos muy específicos

Los CSS modules siguen permitidos, pero solo para:

- microinteracciones complejas
- composición visual muy particular
- integraciones de mapa
- animaciones o detalles difíciles de expresar con utilidades

No usar CSS modules para:

- paddings
- grids
- botones base
- cards base
- títulos o espaciado repetido

### Nada de migración masiva “big bang”

No se debe intentar reescribir todo el frontend en un solo sprint.

La estrategia correcta es:

1. crear base compartida
2. migrar primitivas
3. migrar pantallas de alto impacto
4. limpiar legacy por bloques cerrados

Esto evita regresiones y reduce costo de mantenimiento.

## Componentes núcleo que se deben proteger

El sistema debe crecer alrededor de estas piezas:

1. `Button`
2. `Tag`
3. `StatusPill`
4. `FeedbackPanel`
5. `PageShell`
6. `PageHero`
7. `SectionHeader`
8. `SurfaceCard`
9. `DashboardGrid`
10. `FormGrid`
11. `FormField`
12. `InfoBox`
13. `TextButton`
14. `SkeletonCard`
15. `MapLoadingShell`
16. `MapLegend`

## Decisiones De Utilidades Globales

Se cerró esta decisión para evitar que el sistema vuelva a dispersarse:

- `text-button` ya no debe existir como clase global. Se reemplaza por `TextButton`.
- `skeleton-card` y sus líneas ya no deben existir como patrón de uso manual. Se reemplazan por `SkeletonCard` y `SkeletonLine`.
- `map-loading-shell` ya no debe existir como patrón global. Se reemplaza por `MapLoadingShell`.
- `map-legend` ya no debe existir como patrón global. Se reemplaza por `MapLegend`.
- `inline-tags` se mantiene por ahora como utilidad controlada porque es solo layout base y no una pieza semántica independiente.
- `stack-md` y `stack-lg` se mantienen por ahora como utilidades controladas de spacing, mientras sigan siendo simples y previsibles.

## Inventario Final De Utilidades Globales Permitidas

Después de esta pasada, las utilidades globales que seguimos permitiendo intencionalmente son:

- `page-shell`
- `page-title`
- `page-lead`
- `eyebrow`
- `stack-md`
- `stack-lg`
- `inline-tags`
- `form-control`
- `feedback-panel`
- `feedback-panel--error`
- `feedback-panel__title`
- `feedback-panel__spinner`
- `success-banner`
- `leaflet-shell`
- `custom-map-marker`
- `custom-map-marker__wrapper`
- `custom-map-marker--active`
- `theme-toggle`
- `theme-toggle__icon`
- `theme-toggle--compact`
- `sr-only`
- `site-footer`

Todo lo demás debería resolverse con componentes UI o clases locales en JSX.

## Layouts patrón a respetar

Estas son las 4 familias de layout que se deben consolidar:

### 1. Hero + Content

Uso:

- home
- páginas de categoría
- páginas de onboarding

Piezas base:

- `PageShell`
- `PageHero`
- `SurfaceCard`

### 2. Dashboard con main + aside

Uso:

- área cliente
- panel de tutor
- panel de negocio

Piezas base:

- `DashboardGrid`
- `SectionHeader`
- `SurfaceCard`

### 3. Explorer con filtros + resultados + mapa

Uso:

- categorías geolocalizadas
- búsquedas por ubicación

Base recomendada:

- toolbar con Tailwind
- panel de resultados
- panel de mapa
- leyenda o contexto lateral

### 4. Form Flow

Uso:

- registro
- reclamos
- publicación de mascota perdida
- edición de perfil

Base recomendada:

- hero corto
- card principal de formulario
- aside contextual opcional

## Cómo decidir si algo va en Tailwind o en CSS module

Usa Tailwind si:

- es layout
- es spacing
- es variante visual simple
- es una card, badge, botón o contenedor repetible

Usa CSS module si:

- hay composición visual única
- la lógica visual depende de estados complejos
- hay una pieza artesanal que no debe contaminar la capa global

## Qué no se debe hacer

- No meter colores hardcodeados nuevos en componentes.
- No agregar clases utilitarias gigantes en cada pantalla sin extraer componente.
- No crear otro set paralelo de botones o cards.
- No mezclar Bootstrap mental model con Tailwind utility sprawl.
- No mover una pantalla a Tailwind si sus primitivas base aún no existen.

## Runners De Verificación

Cada cambio que toque layout, cards, formularios, explorer, header o componentes UI compartidos
debe dejar evidencia ejecutando estos runners dentro de `frontend/`.

### Runner obligatorio 1

- `npm run test:ui-foundation`

Qué valida:

- que no reaparezcan imports de `.module.css` en `frontend/src`
- que las pantallas migradas sigan acopladas a primitivas compartidas
- que la documentación de adopciones siga sincronizada

### Runner obligatorio 2

- `npm run build`

Qué valida:

- compilación productiva completa
- tipado de TypeScript dentro del flujo de build
- generación correcta de rutas estáticas y dinámicas

### Runner futuro visual

- `npm run test:visual:future`

Qué hace hoy:

- deja scaffold listo para Playwright sin forzar la dependencia todavía
- detecta si `@playwright/test` ya fue instalado
- cuando esté disponible, podrá ejecutar `playwright test`

Cuándo conviene habilitarlo:

- antes de tocar header, explorer, mapa, cards críticas o tema claro/oscuro
- cuando queramos evidencia visual adicional además de estructura y build

### Orden recomendado

1. `npm run test:ui-foundation`
2. `npm run build`

### Evidencia mínima esperada en cada entrega

- indicar en la minuta o comentario de cierre que ambos runners pasaron
- si uno no corre, explicar por qué y dejar el bloqueo explícito

## Siguiente fase recomendada

1. Migrar `SiteHeader` de forma controlada usando Tailwind para layout base y mantener CSS module
   solo en detalles finos.
2. Migrar toolbar y filtros del explorer.
3. Migrar cards de resultados y ficha.
4. Migrar formularios de registro y reclamo con componentes de campo estandarizados.

## Nota de gobierno del sprint

La ampliación masiva de datos de lugares, incluyendo la meta de 20.000 registros nuevos, queda
como último ítem de la minuta. Primero consolidamos frontend, gobierno visual y experiencia
operativa; después escalamos volumen.
