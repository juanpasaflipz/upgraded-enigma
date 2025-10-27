import dynamic from 'next/dynamic'

const PricingTable = dynamic(() => import('@/components/PricingTable'), { ssr: false })

export default function PricingPage() {
  return (
    <main className="min-h-screen">
      <PricingTable />
    </main>
  )
}
