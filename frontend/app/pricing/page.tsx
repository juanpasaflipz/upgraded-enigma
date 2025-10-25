export default function PricingPage() {
  const tiers = [
    { name: 'Free', price: '$0', features: ['1 project/day', 'Basic analysis', 'Email support'] },
    { name: 'Pro', price: '$19', features: ['Unlimited projects', 'Detailed specs', 'Priority support'] },
    { name: 'Team', price: '$49', features: ['Team dashboard', 'Export templates', 'SLA support'] },
  ]
  return (
    <main className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Pricing</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tiers.map((t) => (
          <div key={t.name} className="rounded-lg border border-zinc-800 p-6">
            <h2 className="text-xl font-semibold">{t.name}</h2>
            <p className="text-3xl font-bold my-2">{t.price}</p>
            <ul className="text-sm text-zinc-300 space-y-1">
              {t.features.map((f) => (<li key={f}>• {f}</li>))}
            </ul>
            <button className="mt-4 w-full rounded-md bg-emerald-500 text-black py-2">Choose</button>
          </div>
        ))}
      </div>
    </main>
  )
}

