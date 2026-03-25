export function EmptyState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return (
    <div className="feedback-panel">
      <p className="feedback-panel__title">{title}</p>
      <p>{message}</p>
    </div>
  );
}

