import Link from 'next/link'

async function fetchProject(id: string) {
  const base = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'
  const res = await fetch(`${base}/api/projects/${id}`, { cache: 'no-store' })
  if (!res.ok) throw new Error('Failed to load project')
  return res.json()
}

export default async function ProjectPage({ params }: { params: { id: string } }) {
  const project = await fetchProject(params.id)
  const spec = project.artifacts.find((a: any) => a.type === 'spec')
  const zip = project.artifacts.find((a: any) => a.type === 'prototype_zip')
  const transcript = project.artifacts.find((a: any) => a.type === 'transcript')

  return (
    <main className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Project #{project.id}</h1>
        <Link href="/dashboard" className="text-zinc-400 underline">Back</Link>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="col-span-2 space-y-4">
          <div className="rounded-lg border border-zinc-800 p-4">
            <h2 className="font-semibold mb-2">Status</h2>
            <span className="px-2 py-1 rounded bg-zinc-800 text-zinc-200 text-sm">{project.status}</span>
          </div>
          <div className="rounded-lg border border-zinc-800 p-4">
            <h2 className="font-semibold mb-2">Artifacts</h2>
            <ul className="space-y-2 text-sm">
              {transcript && <li><a className="text-emerald-400 underline" href={transcript.url}>transcript.txt</a></li>}
              {spec && <li><a className="text-emerald-400 underline" href={spec.url}>spec.json</a></li>}
              {zip && <li><a className="text-emerald-400 underline" href={zip.url}>prototype.zip</a></li>}
              {(!transcript && !spec && !zip) && <li className="text-zinc-400">No artifacts yet. Refresh in a moment.</li>}
            </ul>
          </div>
        </div>
        <div className="space-y-4">
          <div className="rounded-lg border border-zinc-800 p-4">
            <h2 className="font-semibold mb-2">Source</h2>
            <a className="text-zinc-300 underline" href={project.youtube_url} target="_blank">{project.youtube_url}</a>
          </div>
        </div>
      </div>
    </main>
  )
}

