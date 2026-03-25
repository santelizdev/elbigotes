export function ErrorState({
  title = "No se pudo cargar la información",
  message,
}: {
  title?: string;
  message: string;
}) {
  return (
    <div className="feedback-panel feedback-panel--error">
      <p className="feedback-panel__title">{title}</p>
      <p>{message}</p>
    </div>
  );
}

