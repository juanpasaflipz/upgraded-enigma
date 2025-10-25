import { PlayCircle, FileText, Boxes } from 'lucide-react'

const steps = [
  { icon: PlayCircle, title: 'Paste URL', desc: 'Share the YouTube link to analyze' },
  { icon: FileText, title: 'Analyze', desc: 'We draft a structured product spec' },
  { icon: Boxes, title: 'Generate', desc: 'Download a Next.js + Tailwind prototype' },
]

export default function HowItWorks(){
  return (
    <section className="py-6">
      <h2 className="text-2xl font-bold mb-4">How it works</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {steps.map((s) => (
          <div key={s.title} className="rounded-lg border border-zinc-800 p-4">
            <s.icon className="mb-2 text-emerald-400" />
            <h3 className="font-semibold">{s.title}</h3>
            <p className="text-sm text-zinc-300">{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

