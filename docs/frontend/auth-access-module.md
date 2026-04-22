# Access & Registration Module

## Scope

Este ajuste mantiene el login actual y agrega un registro visible de tutores de mascotas dentro de
`/ingresar`, sin romper el backend actual ni las rutas existentes.

## Implemented

- Login existente con email/password.
- Botón `Continuar con Google` con handler real preparado.
- Botón `Continuar con Facebook` en reemplazo de Outlook.
- Registro de tutores visible en la misma pantalla de acceso.
- Tooltips accesibles para:
  - email
  - condición especial
  - dieta especial
- Validación frontend de email:
  - formato válido
  - dominio permitido
- Estructura frontend preparada para:
  - `User`
  - `TutorProfile`
  - `PetProfile`
- Select buscable de raza dependiente del tipo de mascota.
- Mensaje post-registro orientado a futura verificación por correo.

## Active Integrations

### Google OAuth

- Endpoint activo: `/api/v1/accounts/oauth/google/start/`
- Callback activo: `/api/v1/accounts/oauth/google/callback/`
- Variables backend requeridas:
  - `GOOGLE_CLIENT_ID`
  - `GOOGLE_CLIENT_SECRET`
- Comportamiento actual:
  - si el email ya existe, entra con su cuenta
  - si no existe, se crea una cuenta base `pet_owner` con correo verificado por Google

### Facebook OAuth

- Variable esperada: `NEXT_PUBLIC_FACEBOOK_AUTH_URL`
- Handler listo: `handleFacebookLogin()`
- Falta backend:
  - endpoint OAuth de inicio
  - callback
  - intercambio de sesión/token

### Brevo Email Verification

- Variables futuras:
  - `BREVO_API_KEY`
  - `BREVO_SENDER_EMAIL`
- Variables opcionales:
  - `BREVO_SENDER_NAME`
  - `BREVO_REPLY_TO`
- Estado activo:
  - el registro dispara correo de verificación si Brevo está configurado
  - endpoint activo: `/api/v1/accounts/verify-email/`
  - `isEmailVerified = false` se mantiene como base frontend hasta que el usuario confirme

## Data Structure

El formulario ya trabaja con un draft frontend escalable:

```ts
{
  full_name,
  email,
  password,
  tutor_profile: {
    phone,
    address_line,
    commune,
    region,
    marketing_opt_in,
    has_special_condition,
    special_condition_notes,
    has_special_diet,
    special_diet_notes,
    isEmailVerified
  },
  pet_profile: {
    name,
    type,
    breed,
    sex,
    birth_date
  }
}
```

Por compatibilidad, ese draft se mapea al payload actual del backend antes del submit.

## Safe Extension Rules

- Mantener `User` solo para autenticación base.
- No mover condiciones o dieta de mascota al modelo `User`.
- Seguir usando el mapper desde draft frontend al contrato backend mientras el backend no cambie.
- Si se agrega OAuth real, reutilizar los handlers ya creados y no mezclar lógica visual con callbacks.
