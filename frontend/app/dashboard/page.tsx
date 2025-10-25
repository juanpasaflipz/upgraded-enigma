import ProjectList from '@/components/ProjectList'

async function fetchProjects() {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  const res = await fetch(`${base}/api/projects`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Failed to load projects')
  return res.json()
}

export default async function DashboardPage() {
  const projects = await fetchProjects()
  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>
      <ProjectList projects={projects} />
    </main>
  )
}

