import { render, screen } from '@testing-library/react'
import Hero from '@/components/Hero'

describe('Hero', () => {
  it('renders headline', () => {
    render(<Hero />)
    expect(screen.getByText(/Turn YouTube videos into MVPs/i)).toBeInTheDocument()
  })
})

