import Link from 'next/link'

export default function ProjectCard({ project }: { project: any }){
  return (
    <div className="rounded-lg border border-zinc-800 p-4 flex items-center justify-between">
      <div className="space-y-1">
        <div className="font-medium">Project #{project.id}</div>
        <div className="text-xs text-zinc-400 truncate max-w-[360px]">{project.youtube_url}</div>
        <span className="text-xs px-2 py-0.5 rounded bg-zinc-800">{project.status}</span>
      </div>
      <Link className="text-emerald-400 underline text-sm" href={`/project/${project.id}`}>Open</Link>
    </div>
  )
}

