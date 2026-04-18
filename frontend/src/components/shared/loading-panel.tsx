import { FeedbackPanel } from "@/components/ui/feedback-panel";

export function LoadingPanel({ message = "Cargando información..." }: { message?: string }) {
  return <FeedbackPanel message={<p className="m-0">{message}</p>} loading />;
}
