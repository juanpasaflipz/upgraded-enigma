const BASE = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function createProject(body: { youtube_url: string; title?: string }){
  const res = await fetch(`${BASE}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if(!res.ok) throw new Error('Failed to create project')
  return res.json()
}

