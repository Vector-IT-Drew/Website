export const SMKOwnershipSection = () => {
  return (
    <section id="smk-ownership" className="py-24 bg-zinc-50">
      <div className="container mx-auto px-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <div className="w-24 h-0.5 bg-zinc-600 mx-auto mb-8" />
          </div>
          
          {/* First Banner - Invested in Brooklyn */}
          <div className="relative mb-8 overflow-hidden rounded-lg shadow-lg">
            <div className="h-64 md:h-80">
              <img 
                src="/lovable-uploads/8bd6e677-f43a-4b53-871f-ef9dcb713074.png" 
                alt="Greenpoint Brooklyn Street with Church" 
                className="w-full h-full object-cover" 
              />
            </div>
            <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
              <h2 className="text-4xl md:text-5xl font-light tracking-wider text-white">
                Invested in Brooklyn.
              </h2>
            </div>
          </div>

          {/* Second Banner - Focused on People */}
          <div className="relative mb-12 overflow-hidden rounded-lg shadow-lg">
            <div className="h-64 md:h-80">
              <img 
                src="/lovable-uploads/509060ae-abe9-40a3-bd1c-ae7a3b61231d.png" 
                alt="Greenpoint Brooklyn Waterfront Skyline" 
                className="w-full h-full object-cover" 
              />
            </div>
            <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center">
              <h2 className="text-4xl md:text-5xl font-light tracking-wider text-white">
                Focused on People.
              </h2>
            </div>
          </div>
          
          {/* Content below banners */}
          <div className="space-y-6 text-center max-w-4xl mx-auto">
            <p className="text-lg text-zinc-600 leading-relaxed">
              SMK is a growing real estate investment group built on the belief that great housing starts with great intention. Every property in the portfolio is a reflection of that—renovated, stabilized, and thoughtfully maintained to provide tenants with real homes run by people who genuinely care.
            </p>
            
            <p className="text-lg text-zinc-600 leading-relaxed">
              From modernized interiors to operational upgrades, SMK is committed to doing right by both the neighborhoods it invests in and the people who live there. Their mission is clear: succeed by delivering long-term quality—and do it with integrity, energy, and heart.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}; 