"use client";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";
import { checkout } from "@/lib/checkout";

const plans = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    description: "Try the AI MVP builder with limited features.",
    features: [
      "3 free projects/month",
      "AI viability scoring",
      "Basic prototype ZIP",
    ],
    cta: "Get Started",
    highlighted: false,
  },
  {
    name: "Pro",
    price: "$19",
    period: "per month",
    description: "For creators & indie hackers who want faster builds.",
    features: [
      "Unlimited projects",
      "Priority queueing",
      "Brand color customization",
      "Full-featured MVP ZIPs",
    ],
    cta: "Upgrade to Pro",
    highlighted: true,
  },
  {
    name: "Studio",
    price: "$79",
    period: "per month",
    description: "For teams & incubators with heavy usage.",
    features: [
      "Team workspace",
      "Make.com automation",
      "Webhook & API access",
      "Custom hosting integrations",
    ],
    cta: "Join Studio",
    highlighted: false,
  },
];

export default function PricingTable() {
  return (
    <div className="bg-white py-16 sm:py-24 text-gray-900">
      <div className="mx-auto max-w-6xl px-6 lg:px-8 text-center">
        <h2 className="text-base font-semibold text-indigo-600">
          Simple, predictable pricing
        </h2>
        <p className="mt-2 text-4xl font-bold tracking-tight text-gray-900">
          Turn ideas into MVPs in minutes
        </p>
        <p className="mt-4 text-lg text-gray-500">
          Choose a plan that fits your creator journey.
        </p>

        <div className="mt-12 grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-8 shadow-lg border ${
                plan.highlighted ? "border-indigo-500" : "border-gray-200"
              }`}
            >
              <h3 className="text-xl font-semibold text-gray-900">
                {plan.name}
              </h3>
              <p className="mt-2 text-gray-500">{plan.description}</p>
              <p className="mt-6">
                <span className="text-4xl font-bold text-gray-900">
                  {plan.price}
                </span>{" "}
                <span className="text-sm text-gray-500">/{plan.period}</span>
              </p>
              <ul className="mt-6 space-y-2 text-left">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center">
                    <Check className="h-4 w-4 text-indigo-600 mr-2" /> {f}
                  </li>
                ))}
              </ul>
              <Button
                onClick={() => checkout(plan.name.toLowerCase())}
                variant={plan.highlighted ? "default" : "outline"}
                className="mt-8 w-full"
              >
                {plan.cta}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

