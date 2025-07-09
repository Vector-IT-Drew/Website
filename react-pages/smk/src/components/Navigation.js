import { useState, useEffect } from 'react';

export const Navigation = ({ heroComplete = true, currentPage = 'home' }) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [showNav, setShowNav] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
        ? 'bg-black/95 backdrop-blur-sm border-b border-white/10' 
        : 'bg-transparent'
    } ${
      showNav 
        ? 'opacity-100 translate-y-0' 
        : 'opacity-0 -translate-y-4'
    }`}>
      <div className="container mx-auto py-0 px-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <a href="/" className="block">
              <img 
                src="/lovable-uploads/f935332a-65f6-45da-9303-f7fcc78afbce.png" 
                alt="SMK Greenpoint" 
                className="h-6 w-auto md:h-7 lg:h-8 cursor-pointer hover:opacity-80 transition-opacity" 
              />
            </a>
          </div>
          
          {/* Mobile menu button */}
          <button
            className="md:hidden p-2 text-white hover:text-zinc-300 transition-colors"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              {isMobileMenuOpen ? (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              ) : (
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              )}
            </svg>
          </button>
          
          {/* Desktop navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {currentPage === 'home' ? (
              <>
                <a 
                  href="#browse-availability" 
                  className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
                  onClick={(e) => {
                    e.preventDefault();
                    window.location.href = '/listings?portfolio=smk';
                  }}
                >
                  BROWSE AVAILABILITY
                </a>
                <a 
                  href="#smk-ownership" 
                  className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
                >
                  SMK OWNERSHIP AND INTENTIONS
                </a>
                <a 
                  href="#living-in-greenpoint" 
                  className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
                >
                  LIVING IN GREENPOINT
                </a>
                <a 
                  href="/listings?portfolio=smk" 
                  className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
                >
                  CONTACT LEASING
                </a>
                <a 
                  href="/smk/coming-soon" 
                  className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
                >
                  COMING SOON
                </a>
              </>
            ) : (
              <>
                <a 
                  href="/smk" 
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
                  href="/listings?portfolio=smk" 
                  className="text-lg tracking-wide text-white hover:text-zinc-300 transition-colors"
                >
                  CONTACT LEASING
                </a>
              </>
            )}
          </div>
        </div>
        
        {/* Mobile menu */}
        <div className={`md:hidden transition-all duration-300 ease-in-out ${
          isMobileMenuOpen ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
        } overflow-hidden bg-black/95 backdrop-blur-sm`}>
          <div className="px-4 py-4 space-y-4">
            {currentPage === 'home' ? (
              <>
                <a 
                  href="#browse-availability" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={(e) => {
                    e.preventDefault();
                    setIsMobileMenuOpen(false);
                    window.location.href = '/listings?portfolio=smk';
                  }}
                >
                  BROWSE AVAILABILITY
                </a>
                <a 
                  href="#smk-ownership" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  SMK OWNERSHIP AND INTENTIONS
                </a>
                <a 
                  href="#living-in-greenpoint" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  LIVING IN GREENPOINT
                </a>
                <a 
                  href="/listings?portfolio=smk" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  CONTACT LEASING
                </a>
                <a 
                  href="/smk/coming-soon" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  COMING SOON
                </a>
              </>
            ) : (
              <>
                <a 
                  href="/smk" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  HOME
                </a>
                <a 
                  href="/listings?portfolio=smk" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  BROWSE AVAILABILITY
                </a>
                <a 
                  href="/listings?portfolio=smk" 
                  className="block text-base tracking-wide text-white hover:text-zinc-300 transition-colors py-2"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  CONTACT LEASING
                </a>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}; 