import Link from 'next/link'
import { ViabilityBadge } from './ViabilityBadge'

export default function ProjectCard({ project }: { project: any }){
  return (
    <div className="rounded-lg border border-zinc-800 p-4 flex items-center justify-between">
      <div className="space-y-1">
        <div className="font-medium">Project #{project.id}</div>
        <div className="text-xs text-zinc-400 truncate max-w-[360px]">{project.youtube_url}</div>
        <div className="flex items-center gap-2">
          <span className="text-xs px-2 py-0.5 rounded bg-zinc-800">{project.status}</span>
          <ViabilityBadge label={project.mvp_viability} reason={project.viability_reason} />
          {project.viability_reason && (
            <span
              className="inline-flex items-center justify-center w-4 h-4 rounded-full bg-zinc-800 text-zinc-300 text-[10px] cursor-help"
              title={project.viability_reason}
              aria-label={project.viability_reason}
            >
              i
            </span>
          )}
        </div>
      </div>
      <Link className="text-emerald-400 underline text-sm" href={`/project/${project.id}`}>Open</Link>
    </div>
  )
}
