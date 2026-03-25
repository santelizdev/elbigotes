export function LoadingPanel({ message = "Cargando información..." }: { message?: string }) {
  return (
    <div className="feedback-panel">
      <div className="feedback-panel__spinner" />
      <p>{message}</p>
    </div>
  );
}

