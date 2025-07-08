import { useState, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Pause, Play } from 'lucide-react';
import { Button } from '../ui/button';

export const SimpleCarousel = ({ autoplay = true, autoplayDelay = 5000 }) => {
  const images = [
    {
      src: '/lovable-uploads/f0aa78af-541e-4207-a843-5b1693cb3eb8.png',
      alt: 'Modern Kitchen Design - White Cabinets with Island',
      category: 'Kitchen',
      description: 'Vigo White 12"×24" Marble-Look Tile • Matte Black Hardware'
    },
    {
      src: '/lovable-uploads/9e6896ff-4e57-4a28-825c-79aea3b5b459.png',
      alt: 'Contemporary Kitchen - Stainless Steel Appliances',
      category: 'Kitchen',
      description: 'Vigo White Ceramic Flooring • Stainless Steel Appliances'
    },
    {
      src: '/lovable-uploads/c47c7e0c-431d-4375-80d7-cfe684728dec.png',
      alt: 'Premium Kitchen Renovation - Corner Design',
      category: 'Kitchen',
      description: 'Satori Bianco 11"×12" Marble Herringbone • KOHLER Cabinet'
    },
    {
      src: '/lovable-uploads/8bd6e677-f43a-4b53-871f-ef9dcb713074.png',
      alt: 'Elegant Bathroom - Wood Vanity with Modern Fixtures',
      category: 'Bathroom',
      description: 'JEAREY 55.5" Gray Chenille Vanity • Florida Tile Porcelain'
    },
    {
      src: '/lovable-uploads/509060ae-abe9-40a3-bd1c-ae7a3b61231d.png',
      alt: 'Luxury Bathroom Design - Contemporary Style',
      category: 'Bathroom',
      description: 'JEAREY Black Waterfall Faucet • Probrico Privacy Levers'
    },
    {
      src: '/lovable-uploads/d3b0d8c3-11b7-4521-b627-57bd55926a0b.png',
      alt: 'Sleek Kitchen Layout - Modern Galley Style',
      category: 'Kitchen',
      description: 'Vigo White 12"×24" Ceramic • Matte Black Hardware Set'
    }
  ];

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(autoplay);
  const [isHovered, setIsHovered] = useState(false);

  // Auto-play functionality
  useEffect(() => {
    if (!isPlaying || isHovered) return;
    const interval = setInterval(() => {
      setCurrentIndex(prev => (prev + 1) % images.length);
    }, autoplayDelay);
    return () => clearInterval(interval);
  }, [isPlaying, currentIndex, images.length, autoplayDelay, isHovered]);

  const goToNext = () => {
    setCurrentIndex(prev => (prev + 1) % images.length);
  };

  const goToPrevious = () => {
    setCurrentIndex(prev => (prev - 1 + images.length) % images.length);
  };

  const goToSlide = (index) => {
    setCurrentIndex(index);
  };

  return (
    <div className="w-full max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-4xl tracking-wider text-zinc-100 mb-4 font-semibold md:text-5xl">
          Premium Renovation Showcase
        </h2>
        <p className="text-lg text-zinc-200">
          Featuring KOHLER, JEAREY, and Glacier Bay Premium Fixtures
        </p>
      </div>

      {/* Main Carousel Container */}
      <div 
        className="relative h-[500px] md:h-[600px] lg:h-[700px] bg-gradient-to-br from-zinc-700 to-zinc-800 rounded-2xl overflow-hidden shadow-2xl"
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
      >
        {/* Image Container */}
        <div className="relative w-full h-full">
          {images.map((image, index) => (
            <div
              key={index}
              className={`absolute inset-0 transition-all duration-700 ease-in-out ${
                index === currentIndex
                  ? 'opacity-100 translate-x-0'
                  : index < currentIndex
                  ? 'opacity-0 -translate-x-full'
                  : 'opacity-0 translate-x-full'
              }`}
            >
              <img 
                src={image.src} 
                alt={image.alt} 
                className="w-full h-full object-cover"
                loading={index === 0 ? 'eager' : 'lazy'}
              />
              
              {/* Overlay with information */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent">
                <div className="absolute bottom-0 left-0 right-0 p-8 text-white">
                  <div className="inline-block px-3 py-1 mb-3 text-sm font-semibold uppercase tracking-wider bg-white/20 rounded-full backdrop-blur-sm">
                    {image.category}
                  </div>
                  <h3 className="text-2xl md:text-3xl font-semibold mb-2 leading-tight">
                    {image.alt}
                  </h3>
                  <p className="text-lg text-zinc-200 leading-relaxed">
                    {image.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Navigation Buttons */}
        <Button
          variant="outline"
          size="icon"
          className="absolute left-6 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/90 hover:bg-white border-none shadow-lg backdrop-blur-sm transition-all duration-300 hover:scale-110"
          onClick={goToPrevious}
          aria-label="Previous image"
        >
          <ChevronLeft className="h-6 w-6 text-zinc-800" />
        </Button>

        <Button
          variant="outline"
          size="icon"
          className="absolute right-6 top-1/2 -translate-y-1/2 w-12 h-12 bg-white/90 hover:bg-white border-none shadow-lg backdrop-blur-sm transition-all duration-300 hover:scale-110"
          onClick={goToNext}
          aria-label="Next image"
        >
          <ChevronRight className="h-6 w-6 text-zinc-800" />
        </Button>

        {/* Autoplay Toggle */}
        <Button
          variant="outline"
          size="icon"
          className="absolute top-6 right-6 w-12 h-12 bg-white/90 hover:bg-white border-none shadow-lg backdrop-blur-sm transition-all duration-300 hover:scale-110"
          onClick={() => setIsPlaying(!isPlaying)}
          aria-label={isPlaying ? "Pause autoplay" : "Start autoplay"}
        >
          {isPlaying ? (
            <Pause className="h-5 w-5 text-zinc-800" />
          ) : (
            <Play className="h-5 w-5 text-zinc-800" />
          )}
        </Button>

        {/* Progress Bar */}
        <div className="absolute bottom-0 left-0 right-0 h-1 bg-black/20">
          <div 
            className="h-full bg-gradient-to-r from-zinc-100 to-white transition-all duration-300 ease-linear"
            style={{ width: `${(currentIndex + 1) / images.length * 100}%` }}
          />
        </div>
      </div>

      {/* Dots Indicator */}
      <div className="flex justify-center mt-6 space-x-2">
        {images.map((_, index) => (
          <button
            key={index}
            onClick={() => goToSlide(index)}
            className={`h-2 rounded-full transition-all duration-300 ${
              index === currentIndex
                ? 'w-8 bg-zinc-300'
                : 'w-2 bg-zinc-500 hover:bg-zinc-400'
            }`}
            aria-label={`Go to slide ${index + 1}`}
          />
        ))}
      </div>
    </div>
  );
}; 