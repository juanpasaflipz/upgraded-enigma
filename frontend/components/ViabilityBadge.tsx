export function ViabilityBadge({ label, reason }: { label?: string; reason?: string }) {
  const style = label === "mvp-ready" ? "bg-green-100 text-green-800"
    : label === "idea-only" ? "bg-amber-100 text-amber-800"
    : label === "not-a-project" ? "bg-red-100 text-red-800"
    : "bg-gray-100 text-gray-800"
  const text = label ?? "unknown"
  return (
    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${style}`} title={reason || ""}>
      {text}
    </span>
  )
}

