"use client";

import { useEffect, useMemo, useState } from "react";

import styles from "@/components/places/place-loop-actions.module.css";
import { Button } from "@/components/ui/button";
import {
  getSavedPlaceStatus,
  getStoredAccessToken,
  removeSavedPlace,
  savePlace,
} from "@/lib/services/accounts-service";
import { getApiErrorMessage } from "@/lib/services/api-client";
import { siteConfig } from "@/lib/constants/site";
import { Place } from "@/lib/types";

function SaveIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M6.75 3.75h10.5A1.75 1.75 0 0 1 19 5.5v14.44a.31.31 0 0 1-.5.24L12 15.29l-6.5 4.89a.31.31 0 0 1-.5-.24V5.5a1.75 1.75 0 0 1 1.75-1.75Zm0 1.5a.25.25 0 0 0-.25.25v12.94l5.05-3.8a.75.75 0 0 1 .9 0l5.05 3.8V5.5a.25.25 0 0 0-.25-.25Z"
        fill="currentColor"
      />
    </svg>
  );
}

function ShareIcon() {
  return (
    <svg viewBox="0 0 24 24" role="presentation" focusable="false">
      <path
        d="M15.5 5.25a3.25 3.25 0 1 1 1.57 2.78l-7.18 3.59a3.27 3.27 0 0 1 0 .76l7.18 3.59a3.25 3.25 0 1 1-.67 1.34l-7.18-3.6a3.25 3.25 0 1 1 0-3.42l7.18-3.6a3.26 3.26 0 0 1-.22-1.18Zm0 1.5a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5Zm-8 6.75a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5Zm8 7.25a1.75 1.75 0 1 0 0-3.5 1.75 1.75 0 0 0 0 3.5Z"
        fill="currentColor"
      />
    </svg>
  );
}

interface PlaceLoopActionsProps {
  place: Place;
}

export function PlaceLoopActions({ place }: PlaceLoopActionsProps) {
  const [isSaved, setIsSaved] = useState(false);
  const [isCheckingSaved, setIsCheckingSaved] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSharing, setIsSharing] = useState(false);
  const [helperMessage, setHelperMessage] = useState<string | null>(null);
  const [saveUnavailable, setSaveUnavailable] = useState<string | null>(null);

  const token = typeof window === "undefined" ? null : getStoredAccessToken();
  const shareUrl = useMemo(() => {
    if (typeof window !== "undefined") {
      return `${window.location.origin}/lugares/${place.slug}`;
    }
    return `${siteConfig.siteUrl.replace(/\/$/, "")}/lugares/${place.slug}`;
  }, [place.slug]);

  useEffect(() => {
    let isMounted = true;

    async function loadSavedStatus() {
      if (!token) {
        if (isMounted) {
          setIsCheckingSaved(false);
        }
        return;
      }

      try {
        const response = await getSavedPlaceStatus(token, place.slug);
        if (!isMounted) {
          return;
        }
        setIsSaved(response.is_saved);
        setSaveUnavailable(null);
      } catch (error) {
        if (!isMounted) {
          return;
        }
        setSaveUnavailable(
          getApiErrorMessage(
            error,
            "Guardar esta ficha no está disponible para este tipo de cuenta.",
          ),
        );
      } finally {
        if (isMounted) {
          setIsCheckingSaved(false);
        }
      }
    }

    loadSavedStatus();

    return () => {
      isMounted = false;
    };
  }, [place.slug, token]);

  async function handleSaveClick() {
    if (!token) {
      window.location.href = "/ingresar";
      return;
    }

    setIsSaving(true);
    setHelperMessage(null);

    try {
      if (isSaved) {
        await removeSavedPlace(token, place.slug);
        setIsSaved(false);
        setHelperMessage("La ficha se quitó de tu perfil.");
      } else {
        await savePlace(token, place.slug);
        setIsSaved(true);
        setHelperMessage("La ficha quedó guardada en tu perfil.");
      }
    } catch (error) {
      setHelperMessage(
        getApiErrorMessage(
          error,
          "No pudimos actualizar tus guardados. Intenta nuevamente.",
        ),
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleShareClick() {
    setIsSharing(true);
    setHelperMessage(null);

    const sharePayload = {
      title: `${place.name} | Elbigotes`,
      text: `${place.name} en ${place.commune}. Mira esta ficha en Elbigotes.`,
      url: shareUrl,
    };

    try {
      if (typeof navigator !== "undefined" && navigator.share) {
        await navigator.share(sharePayload);
        setHelperMessage("La ficha se compartió correctamente.");
        return;
      }

      if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareUrl);
        setHelperMessage("Copiamos el enlace para compartir la ficha.");
        return;
      }

      setHelperMessage("Copia este enlace para compartir la ficha.");
    } catch (error) {
      const message =
        error instanceof DOMException && error.name === "AbortError"
          ? "Se canceló la acción de compartir."
          : "No pudimos compartir ahora mismo. Intenta nuevamente.";
      setHelperMessage(message);
    } finally {
      setIsSharing(false);
    }
  }

  const saveButtonLabel = !token
    ? "Ingresar para guardar"
    : isSaved
      ? "Guardada en mi perfil"
      : "Guardar en mi perfil";

  const helperText =
    helperMessage ??
    saveUnavailable ??
    (!token
      ? "Inicia sesión como tutor para guardar fichas y revisitarlas después."
      : "Guárdala para volver rápido desde tu cuenta y compártela cuando la necesites.");

  return (
    <section className={styles.panel} aria-label="Acciones de la ficha">
      <div className={styles.header}>
        <h3 className={styles.title}>Guardar y compartir</h3>
        <p className={styles.copy}>
          Si te interesa este negocio, puedes dejarlo guardado en tu perfil o compartirlo por redes
          y mensajería en segundos.
        </p>
      </div>

      <div className={styles.actions}>
        <Button
          type="button"
          variant={isSaved ? "primary" : "secondary"}
          onClick={handleSaveClick}
          disabled={isSaving || isCheckingSaved || Boolean(saveUnavailable)}
        >
          <span className={styles.buttonContent}>
            <span className={styles.icon}>
              <SaveIcon />
            </span>
            <span>{isSaving ? "Actualizando..." : saveButtonLabel}</span>
          </span>
        </Button>

        <Button type="button" variant="ghost" onClick={handleShareClick} disabled={isSharing}>
          <span className={styles.buttonContent}>
            <span className={styles.icon}>
              <ShareIcon />
            </span>
            <span>{isSharing ? "Compartiendo..." : "Compartir ficha"}</span>
          </span>
        </Button>
      </div>

      <p className={`${styles.helper} ${helperMessage ? styles.helperStrong : ""}`}>{helperText}</p>
    </section>
  );
}
