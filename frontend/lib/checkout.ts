export async function checkout(plan: string) {
  const backend = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";
  try {
    const res = await fetch(`${backend}/api/stripe/create-checkout-session?plan=${encodeURIComponent(plan)}`, {
      method: "POST",
    });
    const data = await res.json();
    if (data?.url) {
      window.location.href = data.url;
    } else {
      console.warn("No checkout URL returned", data);
    }
  } catch (e) {
    console.warn("Checkout failed", e);
  }
}
