import { FeedbackPanel } from "@/components/ui/feedback-panel";

export function EmptyState({
  title,
  message,
}: {
  title: string;
  message: string;
}) {
  return <FeedbackPanel title={title} message={<p className="m-0">{message}</p>} />;
}
