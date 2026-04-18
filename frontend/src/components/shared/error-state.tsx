"use client";

import { useEffect } from "react";

import { FeedbackPanel } from "@/components/ui/feedback-panel";

export function ErrorState({
  title = "No se pudo cargar la información",
  message,
}: {
  title?: string;
  message: string;
}) {
  useEffect(() => {
    console.error("[ErrorState]", { title, message });
  }, [title, message]);

  return <FeedbackPanel title={title} message={<p className="m-0">{message}</p>} tone="error" />;
}
