export const KeyHighlights = () => {
  return (
    <section id="highlights" className="py-24">
      <div className="container mx-auto px-0">
        <div className="grid lg:grid-cols-2 min-h-screen">
          {/* Text Content - Left Side */}
          <div className="bg-zinc-200 px-12 py-24 flex flex-col justify-center">
            <h2 className="text-3xl md:text-4xl font-light tracking-wider text-black mb-8">
              Property Highlights
            </h2>
            <div className="w-24 h-0.5 bg-black mb-12" />
            
            <p className="text-lg text-black leading-relaxed">
              The SMK Greenpoint portfolio features boutique low-rise properties that balance character with comfort. Across locations like Meeker Avenue and Sutton Street, tenants enjoy renovated layouts with hardwood floors, oversized windows, and premium finishes. Amenities such as in-unit laundry, virtual doorman access, and shared lounges support a modern lifestyle, while proximity to McGolrick Park, shops, and transit puts the best of Brooklyn within easy reach. It's city living with a neighborhood soul—designed for convenience, built to last.
            </p>
          </div>
          
          {/* Background Image - Right Side */}
          <div 
            className="bg-cover bg-center bg-no-repeat min-h-full" 
            style={{ backgroundImage: "url('/lovable-uploads/c47c7e0c-431d-4375-80d7-cfe684728dec.png')" }}
          />
        </div>
      </div>
    </section>
  );
}; 