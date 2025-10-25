"use client"
import { useState } from 'react'
import { ArrowRight } from 'lucide-react'
import Hero from '@/components/Hero'
import HowItWorks from '@/components/HowItWorks'
import CTA from '@/components/CTA'
import { createProject } from '@/lib/api'

export default function Home() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const res = await createProject({ youtube_url: url })
      window.location.href = `/project/${res.id}`
    } catch (err: any) {
      setError(err?.message || 'Failed to create project')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="max-w-5xl mx-auto p-6 space-y-10">
      <Hero />
      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          aria-label="YouTube URL"
          type="url"
          placeholder="Paste a YouTube URL…"
          value={url}
          onChange={(e)=>setUrl(e.target.value)}
          className="flex-1 rounded-md bg-zinc-900 border border-zinc-800 px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-md bg-emerald-500 text-black font-medium px-4 py-3 hover:opacity-90 disabled:opacity-60"
        >
          {loading ? 'Queuing…' : 'Generate'} <ArrowRight size={18} />
        </button>
      </form>
      {error && <p className="text-red-400 text-sm">{error}</p>}
      <HowItWorks />
      <CTA />
    </main>
  )
}

