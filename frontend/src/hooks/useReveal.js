import { useEffect } from 'react'

export default function useReveal(threshold = 0.1) {
  useEffect(() => {
    const els = document.querySelectorAll('.reveal')
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) e.target.classList.add('on') }),
      { threshold }
    )
    els.forEach((el) => io.observe(el))
    return () => io.disconnect()
  }, [threshold])
}
