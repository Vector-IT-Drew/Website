import React from 'react';
import { Navigation } from './components/Navigation';
import { ComingSoonHero } from './components/coming-soon/ComingSoonHero';
import { RenovationShowcase } from './components/coming-soon/RenovationShowcase';
import { UpdatesSection } from './components/coming-soon/UpdatesSection';
import { StickyContactButton } from './components/coming-soon/StickyContactButton';
import { Toaster } from './components/ui/sonner';

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation heroComplete={true} />
      <ComingSoonHero />
      <RenovationShowcase />
      <UpdatesSection />
      <StickyContactButton />
      <Toaster />
    </div>
  );
}

export default App;