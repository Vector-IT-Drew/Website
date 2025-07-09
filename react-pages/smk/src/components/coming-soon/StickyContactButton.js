import { Button } from '../ui/button';

export const StickyContactButton = () => {
  const handleContactClick = () => {
    // Navigate to listings page with SMK portfolio filter
    window.location.href = '/listings?portfolio=smk';
  };

  return (
    <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
      <Button 
        onClick={handleContactClick}
        className="bg-zinc-800 hover:bg-zinc-700 text-white px-8 py-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 text-lg font-medium"
      >
        Contact Leasing
      </Button>
    </div>
  );
}; 