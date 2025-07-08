export const ComingSoonHero = () => {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background image with overlay */}
      <div 
        className="absolute inset-0 bg-cover bg-center bg-no-repeat"
        style={{
          backgroundImage: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.3)), url('/lovable-uploads/ef7eef99-8d9c-4783-87bb-66c6255016f5.png')`
        }}
      />
      
      {/* Animated gradient overlay */}
      <div 
        className="absolute inset-0 bg-gradient-to-br from-zinc-50/20 via-zinc-100/10 to-zinc-200/20 animate-gradient"
        style={{ backgroundSize: '400% 400%' }}
      />
      
      {/* Subtle overlay pattern */}
      <div className="absolute inset-0 opacity-5 bg-[radial-gradient(circle_at_20%_20%,_theme(colors.zinc.600)_1px,_transparent_1px)] bg-[length:20px_20px]" />
      
      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        <div className="animate-fade-in">
          <h1 className="text-5xl md:text-7xl font-light tracking-wider text-white mb-8">
            Coming Soon to
            <span className="block text-zinc-200 mt-2">SMK Greenpoint</span>
          </h1>
          
          <div className="w-32 h-0.5 bg-white/60 mx-auto mb-12" />
          
          <p className="text-xl md:text-2xl text-zinc-200 leading-relaxed max-w-3xl mx-auto">
            Exciting renovations and enhancements are on the horizon. We're thoughtfully upgrading our Greenpoint properties to deliver an even better living experience for our community.
          </p>
          
          <div className="mt-12">
            <a 
              href="/listings?portfolio=smk" 
              className="inline-flex items-center px-8 py-4 bg-white/10 hover:bg-white/20 backdrop-blur-sm border border-white/20 rounded-full text-white font-medium text-lg tracking-wide transition-all duration-300 hover:scale-105 hover:shadow-lg"
            >
              <span>Browse Availability</span>
              <svg className="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </a>
          </div>
        </div>
        
        <div className="mt-16 animate-bounce">
          <div className="w-6 h-10 border-2 border-white/60 rounded-full mx-auto">
            <div className="w-1 h-3 bg-white/60 rounded-full mx-auto mt-2 animate-scroll" />
          </div>
        </div>
      </div>
    </section>
  );
}; 