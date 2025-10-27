import * as React from 'react'

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: 'default' | 'outline'
}

export function Button({ variant = 'default', className = '', ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none h-10 px-4 py-2'
  const styles =
    variant === 'outline'
      ? 'border border-zinc-700 text-zinc-100 bg-transparent hover:bg-zinc-800 focus:ring-zinc-400'
      : 'bg-emerald-500 text-black hover:bg-emerald-400 focus:ring-emerald-300'
  return <button className={`${base} ${styles} ${className}`} {...props} />
}

