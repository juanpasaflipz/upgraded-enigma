import Link from 'next/link'

export default function CTA(){
  return (
    <section className="rounded-lg border border-zinc-800 p-6 flex items-center justify-between">
      <div>
        <h3 className="text-xl font-semibold">Ready to go further?</h3>
        <p className="text-zinc-300">Upgrade for unlimited projects and premium templates.</p>
      </div>
      <Link href="/pricing" className="px-4 py-2 rounded-md bg-emerald-500 text-black font-medium">See Pricing</Link>
    </section>
  )
}

