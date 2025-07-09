export const GreenpointSection = () => {
  const highlights = [
    "Waterfront parks and East River promenade with Manhattan skyline views",
    "Thriving arts scene with galleries, studios, and creative spaces",
    "Farm-to-table restaurants and artisanal coffee shops",
    "Historic charm with converted warehouses and cobblestone streets",
    "Easy commute to Manhattan via multiple subway lines and ferry",
    "Growing tech and creative professional community",
    "Weekend farmers markets and community events",
    "Proximity to McCarren Park and Transmitter Park"
  ];

  return (
    <section id="living-in-greenpoint" className="py-24 bg-zinc-700">
      <div className="container mx-auto px-6">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left side - Text content */}
          <div>
            <h2 className="text-3xl md:text-4xl font-light tracking-wider text-zinc-100 mb-6">
              WHY WE LOVE GREENPOINT
            </h2>
            <div className="w-24 h-0.5 bg-zinc-600 mb-8" />
            
            <p className="text-lg text-zinc-300 mb-8 leading-relaxed">
              Greenpoint offers the perfect blend of Brooklyn's industrial heritage and modern urban living. 
              This vibrant waterfront neighborhood has transformed into one of NYC's most sought-after communities.
            </p>
            
            <div className="space-y-4">
              {highlights.map((highlight, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-zinc-600 rounded-full mt-2 flex-shrink-0" />
                  <p className="text-zinc-300 leading-relaxed">{highlight}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Right side - Image */}
          <div className="relative">
            <div className="aspect-[4/5] overflow-hidden rounded-lg">
              <img 
                src="/lovable-uploads/f0aa78af-541e-4207-a843-5b1693cb3eb8.png" 
                alt="Greenpoint Brooklyn Street Scene" 
                className="w-full h-full object-cover" 
              />
            </div>
            {/* Optional overlay accent */}
            <div className="absolute -bottom-4 -right-4 w-24 h-24 bg-zinc-600/10 rounded-lg -z-10" />
          </div>
        </div>
      </div>
    </section>
  );
}; 