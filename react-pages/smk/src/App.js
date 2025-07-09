import React, { useState, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HeroSection } from './components/HeroSection';
import { KeyHighlights } from './components/KeyHighlights';
import { SMKOwnershipSection } from './components/SMKOwnershipSection';
import { GreenpointSection } from './components/GreenpointSection';
import { ContactSection } from './components/ContactSection';
import { ComingSoonHero } from './components/coming-soon/ComingSoonHero';
import { RenovationShowcase } from './components/coming-soon/RenovationShowcase';
import { UpdatesSection } from './components/coming-soon/UpdatesSection';
import { StickyContactButton } from './components/coming-soon/StickyContactButton';
import { Toaster } from './components/ui/sonner';

function MainPage() {
  const [heroComplete, setHeroComplete] = useState(false);

  const handleAnimationComplete = useCallback(() => {
    setHeroComplete(true);
  }, []);

  return (
    <>
      <Navigation heroComplete={heroComplete} currentPage="home" />
      <HeroSection onAnimationComplete={handleAnimationComplete} />
      <KeyHighlights />
      <SMKOwnershipSection />
      <GreenpointSection />
      <ContactSection />
    </>
  );
}

function ComingSoonPage() {
  return (
    <>
      <Navigation heroComplete={true} currentPage="coming-soon" />
      <ComingSoonHero />
      <RenovationShowcase />
      <UpdatesSection />
      <StickyContactButton />
    </>
  );
}

function App() {
  return (
    <Router basename="/smk">
      <div className="min-h-screen bg-background">
        <Routes>
          <Route path="/" element={<MainPage />} />
          <Route path="/coming-soon" element={<ComingSoonPage />} />
        </Routes>
        <Toaster />
      </div>
    </Router>
  );
}

export default App;