import ProjectCard from './ProjectCard'

export default function ProjectList({ projects }: { projects: any[] }){
  if (!projects?.length) {
    return <p className="text-sm text-zinc-400">No projects yet. Create one from the home page.</p>
  }
  return (
    <div className="space-y-3">
      {projects.map((p) => <ProjectCard key={p.id} project={p} />)}
    </div>
  )
}

