import { useState, useEffect } from 'react';

export const HeroSection = ({ onAnimationComplete }) => {
  const [phase, setPhase] = useState('black');
  const [finalTypingText, setFinalTypingText] = useState('');
  const finalTypingSequence = 'TIMELESS BROOKLYN,\nTAILORED FOR TODAY';

  useEffect(() => {
    // Reset animation state on component mount
    setPhase('black');
    setFinalTypingText('');
    
    // Start with black screen (1 second instead of 2)
    const timer1 = setTimeout(() => setPhase('initial-logo'), 1000);
    
    // Fade out initial logo (after 2 seconds of display instead of 3)
    const timer2 = setTimeout(() => setPhase('fade-out'), 3000);
    
    // Show image immediately after fade out completes (1 second fade)
    const timer3 = setTimeout(() => setPhase('image'), 4000);
    
    // Start final typing sequence after image appears (0.5 second delay instead of 1)
    const timer4 = setTimeout(() => {
      setPhase('final-typing');
      let currentIndex = 0;
      const finalTypewriterInterval = setInterval(() => {
        if (currentIndex <= finalTypingSequence.length) {
          setFinalTypingText(finalTypingSequence.slice(0, currentIndex));
          currentIndex++;
        } else {
          clearInterval(finalTypewriterInterval);
          // Complete animation
          setTimeout(() => {
            setPhase('complete');
            onAnimationComplete();
          }, 300);
        }
      }, 60); // Faster typing speed (60ms instead of 80ms)
      
      return () => clearInterval(finalTypewriterInterval);
    }, 4500);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
    };
  }, [onAnimationComplete]);

  return (
    <section className="relative h-screen w-full overflow-hidden">
      {/* Initial logo animation phase over black background */}
      <div className={`absolute inset-0 bg-black flex items-center justify-center transition-all duration-1000 ease-in-out ${
        phase === 'black' || phase === 'initial-logo' ? 'opacity-100' : 
        phase === 'fade-out' ? 'opacity-0' : 
        'opacity-0'
      }`}>
        <div className={`transition-all duration-1000 ease-in-out ${
          phase === 'initial-logo' ? 'opacity-100 scale-100 translate-y-0' : 
          'opacity-0 scale-95 translate-y-8'
        }`}>
          <img 
            src="/lovable-uploads/f935332a-65f6-45da-9303-f7fcc78afbce.png" 
            alt="SMK Logo"
            className="w-96 h-auto md:w-[600px] lg:w-[800px] xl:w-[1000px] max-w-[90vw]"
          />
        </div>
      </div>
      
      {/* Image phase */}
      <div className={`absolute inset-0 transition-all duration-1000 ease-in-out ${
        ['image', 'final-typing', 'complete'].includes(phase) ? 'opacity-100 scale-100' : 'opacity-0 scale-105'
      }`}>
        <div 
          className="w-full h-full bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.3)), url('/lovable-uploads/ef7eef99-8d9c-4783-87bb-66c6255016f5.png')`
          }}
        />
        
        {/* Final text overlay on image with typing effect */}
        <div className={`absolute inset-0 flex items-center justify-center transition-all duration-1000 ease-in-out ${
          ['final-typing', 'complete'].includes(phase) ? 'opacity-100 scale-100 translate-y-0' : 'opacity-0 scale-95 translate-y-8'
        }`}>
          <h1 className="text-4xl md:text-6xl lg:text-7xl font-light text-white text-center tracking-[0.2em] leading-tight whitespace-pre-line">
            {finalTypingText}
            {phase === 'final-typing' && <span className="animate-pulse">|</span>}
          </h1>
        </div>
      </div>
      
      {/* Scroll indicator */}
      <div className={`absolute bottom-8 left-1/2 transform -translate-x-1/2 transition-all duration-1000 ease-in-out ${
        phase === 'complete' ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
        <div className="w-6 h-10 border-2 border-white rounded-full flex justify-center">
          <div className="w-1 h-3 bg-white rounded-full mt-2 animate-bounce" />
        </div>
      </div>
    </section>
  );
}; 