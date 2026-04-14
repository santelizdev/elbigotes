"use client";

import { useEffect, useState } from "react";

import styles from "@/components/accounts/registration.module.css";
import { AccountAccessNotice } from "@/components/accounts/account-access-notice";
import { ErrorState } from "@/components/shared/error-state";
import { LoadingPanel } from "@/components/shared/loading-panel";
import { Button } from "@/components/ui/button";
import {
  BusinessWorkspaceResponse,
  clearStoredAccessToken,
  getBusinessWorkspace,
  getStoredAccessToken,
} from "@/lib/services/accounts-service";
import { getApiErrorMessage } from "@/lib/services/api-client";

function formatDateLabel(value?: string | null) {
  if (!value) {
    return null;
  }

  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }

  return new Intl.DateTimeFormat("es-CL", {
    day: "numeric",
    month: "long",
    year: "numeric",
  }).format(parsed);
}

export function BusinessDashboard() {
  const [workspace, setWorkspace] = useState<BusinessWorkspaceResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [missingToken, setMissingToken] = useState(false);

  useEffect(() => {
    async function loadWorkspace() {
      const token = getStoredAccessToken();
      if (!token) {
        setMissingToken(true);
        setLoading(false);
        return;
      }

      try {
        const response = await getBusinessWorkspace(token);
        setWorkspace(response);
      } catch (error) {
        clearStoredAccessToken();
        setError(
          getApiErrorMessage(
            error,
            "No pudimos cargar tu área comercial. Inicia sesión nuevamente.",
          ),
        );
      } finally {
        setLoading(false);
      }
    }

    loadWorkspace();
  }, []);

  if (loading) {
    return <LoadingPanel message="Cargando área comercial..." />;
  }

  if (missingToken) {
    return <AccountAccessNotice />;
  }

  if (error || !workspace) {
    return (
      <div className={styles.page}>
        <ErrorState message={error ?? "No pudimos cargar el panel comercial."} />
      </div>
    );
  }

  const primaryPlace = workspace.places.find((place) => place.is_primary);
  const currentMembership =
    workspace.profile.memberships.find((membership) => membership.status === "active") ??
    workspace.profile.memberships.find((membership) => membership.status === "trial") ??
    workspace.profile.memberships[0];
  const membershipEndsAtLabel = formatDateLabel(currentMembership?.ends_at);
  const membershipRenewsAtLabel = formatDateLabel(currentMembership?.renews_at);
  const membershipHeadline =
    currentMembership?.access_tier === "business_free_lifetime"
      ? "Gratuita permanente"
      : currentMembership?.access_tier === "business_trial"
        ? currentMembership.status === "expired"
          ? "Renovación requerida"
          : "Prueba comercial"
        : currentMembership?.access_tier === "business_paid"
          ? currentMembership.status === "past_due"
            ? "Pago pendiente"
            : "Plan comercial"
          : currentMembership?.plan_name ?? "Sin membresía asignada";
  const membershipCopy = !currentMembership
    ? "Este perfil todavía no tiene una asignación de membresía activa."
    : currentMembership.access_tier === "business_free_lifetime"
      ? "Esta categoría quedó con acceso comercial permanente y no requiere renovación periódica."
      : currentMembership.access_tier === "business_trial"
        ? currentMembership.status === "expired"
          ? "El periodo gratuito ya venció. Esta cuenta necesita renovación para recuperar estado comercial activo."
          : membershipEndsAtLabel
            ? `Tu periodo gratuito vence el ${membershipEndsAtLabel}. Antes de esa fecha debemos definir su renovación.`
            : "Esta cuenta está operando con un periodo gratuito inicial de 30 días."
        : currentMembership.access_tier === "business_paid"
          ? currentMembership.status === "past_due"
            ? "La membresía quedó con cobro pendiente. Conviene regularizarla para mantener el negocio activo."
            : membershipRenewsAtLabel
              ? `Tu siguiente renovación comercial está planificada para el ${membershipRenewsAtLabel}.`
              : "La membresía comercial está activa para esta cuenta."
          : `Estado actual: ${currentMembership.status}.`;

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <p className="eyebrow">Área cliente</p>
        <h1 className="page-title">{workspace.profile.business_name}</h1>
        <p className="page-lead">
          Este panel concentra tu estado comercial, la publicación principal y las sucursales
          asociadas a la cuenta.
        </p>
        <div className={styles.heroActions}>
          <Button href="/mi-negocio/editar" variant="secondary">
            Editar datos
          </Button>
          <Button href="/mi-negocio/sucursales/nueva" variant="primary">
            Añadir sucursal
          </Button>
        </div>
      </section>

      <section className={styles.cards}>
        <article className={styles.card}>
          <p className="eyebrow">Membresía</p>
          <h3>{membershipHeadline}</h3>
          <p>{membershipCopy}</p>
        </article>

        <article className={styles.card}>
          <p className="eyebrow">Ficha principal</p>
          <h3>{primaryPlace?.status === "active" ? "Publicada" : "En revisión"}</h3>
          <p>
            {primaryPlace
              ? `${primaryPlace.formatted_address || `${primaryPlace.commune}, ${primaryPlace.region}`}`
              : "Aún no hay una ficha principal vinculada."}
          </p>
        </article>

        <article className={styles.card}>
          <p className="eyebrow">Sucursales</p>
          <h3>{workspace.places.length}</h3>
          <p>Todas las fichas nuevas quedan en revisión manual antes de mostrarse al público.</p>
        </article>
      </section>

      <section className={styles.formCard}>
        <p className="eyebrow">Tus fichas</p>
        <h2>Publicaciones y sucursales</h2>
        <div className={styles.stackList}>
          {workspace.places.map((place) => (
            <article key={place.slug} className={styles.listCard}>
              <div>
                <strong>{place.name}</strong>
                <p>{place.formatted_address || `${place.commune}, ${place.region}`}</p>
              </div>
              <span className={styles.statusBox}>
                {place.is_primary ? "Principal" : "Sucursal"} ·{" "}
                {place.status === "active" ? "Publicada" : "En revisión"}
              </span>
            </article>
          ))}
        </div>
      </section>
    </div>
  );
}
