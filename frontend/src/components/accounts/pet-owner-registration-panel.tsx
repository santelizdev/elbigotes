"use client";

import { ChangeEvent, FormEvent, useMemo, useState } from "react";

import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import { FormCheckbox, FormField, FormGrid, InfoBox } from "@/components/ui/form-primitives";
import { TooltipInfo } from "@/components/ui/tooltip-info";
import {
  CHILE_REGIONS,
  DEFAULT_REGION,
  getCommunesForRegion,
} from "@/lib/constants/chile-locations";
import { PET_BREEDS_BY_TYPE } from "@/lib/constants/pet-breeds";
import { getApiErrorMessage } from "@/lib/services/api-client";
import {
  PetOwnerRegistrationDraft,
  mapPetOwnerRegistrationDraftToPayload,
  registerPetOwnerAccount,
} from "@/lib/services/accounts-service";
import { cn } from "@/lib/utils/cn";

const ALLOWED_EMAIL_DOMAINS = new Set([
  "gmail.com",
  "yahoo.com",
  "outlook.com",
  "hotmail.com",
  "proton.me",
  "protonmail.com",
]);

interface RegistrationFieldErrors {
  full_name?: string;
  email?: string;
  password?: string;
  phone?: string;
  commune?: string;
  pet_name?: string;
  pet_type?: string;
}

interface PetOwnerRegistrationPanelProps {
  submitLabel?: string;
  className?: string;
}

function buildEmailError(email: string) {
  const normalized = email.trim().toLowerCase();

  if (!normalized) {
    return "Ingresa un correo para continuar.";
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalized)) {
    return "Ingresa un correo con formato válido.";
  }

  const domain = normalized.split("@")[1] ?? "";

  if (!ALLOWED_EMAIL_DOMAINS.has(domain)) {
    return "Usa Gmail, Yahoo, Outlook, Hotmail o Proton. Si no tienes uno, puedes continuar con Google o Facebook.";
  }

  return null;
}

function buildRegistrationErrors(draft: PetOwnerRegistrationDraft): RegistrationFieldErrors {
  const errors: RegistrationFieldErrors = {};

  if (!draft.full_name.trim()) {
    errors.full_name = "Ingresa tu nombre completo.";
  }

  const emailError = buildEmailError(draft.email);
  if (emailError) {
    errors.email = emailError;
  }

  if (draft.password.length < 8) {
    errors.password = "La contraseña debe tener al menos 8 caracteres.";
  }

  if (!draft.tutor_profile.phone.trim()) {
    errors.phone = "Ingresa un teléfono de contacto.";
  }

  if (!draft.tutor_profile.commune?.trim()) {
    errors.commune = "Selecciona una comuna.";
  }

  if (!draft.pet_profile.name.trim()) {
    errors.pet_name = "Ingresa el nombre de tu mascota.";
  }

  if (!draft.pet_profile.type.trim()) {
    errors.pet_type = "Selecciona un tipo de mascota.";
  }

  return errors;
}

export function PetOwnerRegistrationPanel({
  submitLabel = "Crear cuenta de tutor",
  className,
}: PetOwnerRegistrationPanelProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<RegistrationFieldErrors>({});
  const [selectedRegion, setSelectedRegion] = useState(DEFAULT_REGION);
  const [petType, setPetType] = useState("dog");
  const [breedQuery, setBreedQuery] = useState("");
  const [hasSpecialCondition, setHasSpecialCondition] = useState(false);
  const [hasSpecialDiet, setHasSpecialDiet] = useState(false);
  const [isEmailVerified] = useState(false);

  const breedOptions = useMemo(() => PET_BREEDS_BY_TYPE[petType] ?? [], [petType]);

  function handlePetTypeChange(event: ChangeEvent<HTMLSelectElement>) {
    setPetType(event.target.value);
    setBreedQuery("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    const formData = new FormData(form);
    const draft: PetOwnerRegistrationDraft = {
      full_name: String(formData.get("full_name") ?? ""),
      email: String(formData.get("email") ?? "").trim().toLowerCase(),
      password: String(formData.get("password") ?? ""),
      tutor_profile: {
        phone: String(formData.get("phone") ?? ""),
        address_line: String(formData.get("address_line") ?? ""),
        commune: String(formData.get("commune") ?? ""),
        region: String(formData.get("region") ?? "") || DEFAULT_REGION,
        marketing_opt_in: formData.get("marketing_opt_in") === "on",
        has_special_condition: formData.get("has_special_condition") === "on",
        special_condition_notes: String(formData.get("special_condition_notes") ?? ""),
        has_special_diet: formData.get("has_special_diet") === "on",
        special_diet_notes: String(formData.get("special_diet_notes") ?? ""),
        isEmailVerified,
      },
      pet_profile: {
        name: String(formData.get("pet_name") ?? ""),
        type: String(formData.get("pet_type") ?? petType),
        breed: String(formData.get("pet_breed") ?? ""),
        sex: String(formData.get("pet_sex") ?? "unknown"),
        birth_date: String(formData.get("pet_birth_date") ?? "") || undefined,
      },
    };

    const validationErrors = buildRegistrationErrors(draft);
    setFieldErrors(validationErrors);

    if (Object.keys(validationErrors).length > 0) {
      setLoading(false);
      return;
    }

    try {
      const response = await registerPetOwnerAccount(mapPetOwnerRegistrationDraftToPayload(draft));
      form.reset();
      setSelectedRegion(DEFAULT_REGION);
      setPetType("dog");
      setBreedQuery("");
      setHasSpecialCondition(false);
      setHasSpecialDiet(false);
      setFieldErrors({});

      const petName =
        response && typeof response === "object" && "initial_pet" in response
          ? response.initial_pet.name
          : "Tu mascota";

      setSuccessMessage(
        `Cuenta creada. Revisa tu correo para confirmar tu cuenta. ${petName} ya quedó asociado a tu perfil.`,
      );
    } catch (submitError) {
      setError(
        getApiErrorMessage(
          submitError,
          "No pudimos crear la cuenta del tutor. Revisa los datos e intenta nuevamente.",
        ),
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className={cn("grid gap-4", className)} onSubmit={handleSubmit}>
      <InfoBox className="rounded-[1.2rem]">
        Registramos la cuenta base del usuario y, por separado, dejamos preparado el perfil del
        tutor y la primera mascota. Eso nos permite crecer después sin mezclar autenticación con
        datos clínicos o de preferencia.
      </InfoBox>

      <FormGrid>
        <FormField label="Nombre completo" htmlFor="full_name" error={fieldErrors.full_name}>
          <input
            id="full_name"
            name="full_name"
            required
            className={cn("form-control", fieldErrors.full_name && "border-red-500")}
          />
        </FormField>

        <FormField
          label={
            <span className="inline-flex items-center gap-2">
              Email
              <TooltipInfo
                label="Información sobre correos permitidos"
                content="Solo se permiten correos de proveedores confiables como: Gmail, Yahoo, Outlook, Proton. Si no tienes uno, puedes registrarte con Google o Facebook."
              />
            </span>
          }
          htmlFor="email"
          error={fieldErrors.email}
        >
          <input
            id="email"
            name="email"
            type="email"
            required
            className={cn("form-control", fieldErrors.email && "border-red-500")}
          />
        </FormField>

        <FormField label="Password" htmlFor="password" error={fieldErrors.password}>
          <input
            id="password"
            name="password"
            type="password"
            minLength={8}
            required
            className={cn("form-control", fieldErrors.password && "border-red-500")}
          />
        </FormField>

        <FormField label="Teléfono" htmlFor="phone" error={fieldErrors.phone}>
          <input
            id="phone"
            name="phone"
            required
            className={cn("form-control", fieldErrors.phone && "border-red-500")}
          />
        </FormField>

        <FormField label="Región" htmlFor="region">
          <select
            id="region"
            name="region"
            value={selectedRegion}
            onChange={(event) => setSelectedRegion(event.target.value)}
            className="form-control"
          >
            {CHILE_REGIONS.map((item) => (
              <option key={item.region} value={item.region}>
                {item.region}
              </option>
            ))}
          </select>
        </FormField>

        <FormField label="Comuna" htmlFor="commune" error={fieldErrors.commune}>
          <select
            id="commune"
            name="commune"
            required
            className={cn("form-control", fieldErrors.commune && "border-red-500")}
          >
            <option value="">Selecciona una comuna</option>
            {getCommunesForRegion(selectedRegion).map((commune) => (
              <option key={commune} value={commune}>
                {commune}
              </option>
            ))}
          </select>
        </FormField>

        <FormField label="Dirección" htmlFor="address_line" fullWidth>
          <input
            id="address_line"
            name="address_line"
            placeholder="Calle, número o referencia útil"
            className="form-control"
          />
        </FormField>
      </FormGrid>

      <InfoBox tone="muted" className="rounded-[1.2rem]">
        La verificación por correo ya queda conectada vía Brevo cuando el servidor tenga
        configurados <code>BREVO_API_KEY</code> y <code>BREVO_SENDER_EMAIL</code>.
      </InfoBox>

      <FormGrid>
        <FormField label="Nombre mascota" htmlFor="pet_name" error={fieldErrors.pet_name}>
          <input
            id="pet_name"
            name="pet_name"
            required
            className={cn("form-control", fieldErrors.pet_name && "border-red-500")}
          />
        </FormField>

        <FormField label="Tipo de mascota" htmlFor="pet_type" error={fieldErrors.pet_type}>
          <select
            id="pet_type"
            name="pet_type"
            value={petType}
            onChange={handlePetTypeChange}
            className={cn("form-control", fieldErrors.pet_type && "border-red-500")}
          >
            <option value="dog">Perro</option>
            <option value="cat">Gato</option>
            <option value="other">Otra</option>
          </select>
        </FormField>

        <FormField
          label="Raza"
          htmlFor="pet_breed"
          helper="Puedes escribir para filtrar opciones según el tipo de mascota."
        >
          <input
            id="pet_breed"
            name="pet_breed"
            list={`pet-breeds-${petType}`}
            value={breedQuery}
            onChange={(event) => setBreedQuery(event.target.value)}
            className="form-control"
            placeholder={petType === "other" ? "Ej. Conejo enano" : "Busca o escribe una raza"}
          />
          <datalist id={`pet-breeds-${petType}`}>
            {breedOptions.map((breed) => (
              <option key={breed} value={breed} />
            ))}
          </datalist>
        </FormField>

        <FormField label="Sexo" htmlFor="pet_sex">
          <select id="pet_sex" name="pet_sex" defaultValue="unknown" className="form-control">
            <option value="unknown">No identificado</option>
            <option value="male">Macho</option>
            <option value="female">Hembra</option>
          </select>
        </FormField>

        <FormField label="Fecha de nacimiento" htmlFor="pet_birth_date">
          <input id="pet_birth_date" name="pet_birth_date" type="date" className="form-control" />
        </FormField>
      </FormGrid>

      <FormGrid>
        <FormField
          label={
            <span className="inline-flex items-center gap-2">
              Condición especial
              <TooltipInfo
                label="Información sobre condición médica"
                content="Indica si tu mascota tiene alguna condición médica diagnosticada. Esto nos permitirá sugerir servicios especializados."
              />
            </span>
          }
          htmlFor="has_special_condition"
          fullWidth
        >
          <div className="grid gap-3">
            <FormCheckbox htmlFor="has_special_condition">
              <input
                id="has_special_condition"
                name="has_special_condition"
                type="checkbox"
                checked={hasSpecialCondition}
                onChange={(event) => setHasSpecialCondition(event.target.checked)}
                className="h-4 w-4 rounded border-app-border-strong accent-[var(--accent-emerald)]"
              />
              <span>Mi mascota tiene una condición médica diagnosticada</span>
            </FormCheckbox>

            {hasSpecialCondition ? (
              <textarea
                id="special_condition_notes"
                name="special_condition_notes"
                className="form-control min-h-24 resize-y"
                placeholder="Cuéntanos lo esencial para mejorar futuras recomendaciones."
              />
            ) : null}
          </div>
        </FormField>

        <FormField
          label={
            <span className="inline-flex items-center gap-2">
              Dieta especial
              <TooltipInfo
                label="Información sobre dieta especial"
                content="Indica si tu mascota sigue una dieta específica para poder recomendarte tiendas o productos adecuados."
              />
            </span>
          }
          htmlFor="has_special_diet"
          fullWidth
        >
          <div className="grid gap-3">
            <FormCheckbox htmlFor="has_special_diet">
              <input
                id="has_special_diet"
                name="has_special_diet"
                type="checkbox"
                checked={hasSpecialDiet}
                onChange={(event) => setHasSpecialDiet(event.target.checked)}
                className="h-4 w-4 rounded border-app-border-strong accent-[var(--accent-emerald)]"
              />
              <span>Mi mascota sigue una dieta específica</span>
            </FormCheckbox>

            {hasSpecialDiet ? (
              <textarea
                id="special_diet_notes"
                name="special_diet_notes"
                className="form-control min-h-24 resize-y"
                placeholder="Ej. alimento hipoalergénico, renal, gastrointestinal o BARF."
              />
            ) : null}
          </div>
        </FormField>
      </FormGrid>

      <FormCheckbox htmlFor="marketing_opt_in">
        <input
          id="marketing_opt_in"
          name="marketing_opt_in"
          type="checkbox"
          defaultChecked
          className="h-4 w-4 rounded border-app-border-strong accent-[var(--accent-emerald)]"
        />
        <span>Acepto recibir comunicaciones útiles y campañas personalizadas</span>
      </FormCheckbox>

      <Button type="submit" disabled={loading}>
        {loading ? "Creando cuenta..." : submitLabel}
      </Button>

      {loading ? <LoadingPanel message="Registrando tutor y mascota..." /> : null}
      {error ? <ErrorState message={error} /> : null}
      {successMessage ? <div className="success-banner">{successMessage}</div> : null}
    </form>
  );
}
