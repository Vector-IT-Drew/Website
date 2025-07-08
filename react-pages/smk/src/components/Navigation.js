import { useState, useEffect } from 'react';

export const Navigation = ({ heroComplete = true }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [showNav, setShowNav] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 100);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    if (heroComplete) {
      // Add a small delay after hero completes, then fade in the nav
      const timer = setTimeout(() => {
        setShowNav(true);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [heroComplete]);

  if (!heroComplete) return null;

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
      isScrolled 
        ? 'bg-background/95 backdrop-blur-sm border-b border-border' 
        : 'bg-transparent'
    } ${
      showNav 
        ? 'opacity-100 translate-y-0' 
        : 'opacity-0 -translate-y-4'
    }`}>
      <div className="container mx-auto py-0 px-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <img 
              src="/lovable-uploads/f935332a-65f6-45da-9303-f7fcc78afbce.png" 
              alt="SMK Greenpoint" 
              className="h-6 w-auto md:h-7 lg:h-8" 
            />
          </div>
          <div className="hidden md:flex items-center space-x-8">
            <a 
              href="/" 
              className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
            >
              HOME
            </a>
            <a 
              href="/listings?portfolio=smk" 
              className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
            >
              BROWSE AVAILABILITY
            </a>
            <a 
              href="/#contact" 
              className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
            >
              CONTACT LEASING
            </a>
          </div>
        </div>
      </div>
    </nav>
  );
}; 