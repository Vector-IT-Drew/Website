import { Button } from './ui/button';

export const ContactSection = () => {
  return (
    <section id="contact" className="py-24 bg-zinc-800">
      <div className="container mx-auto px-6 text-center">
        <h2 className="text-3xl md:text-4xl font-light tracking-wider text-white mb-6">
          READY TO CALL SMK HOME?
        </h2>
        <div className="w-24 h-0.5 bg-white mx-auto mb-8" />
        
        <p className="text-lg text-zinc-300 mb-8 max-w-2xl mx-auto leading-relaxed">
          Join our community of residents who've discovered the perfect blend of modern luxury and Brooklyn authenticity.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Button 
            size="lg"
            className="bg-white text-zinc-800 hover:bg-zinc-100 px-8 py-3 tracking-wide transition-all hover:scale-105"
            onClick={() => window.location.href = '/listings?portfolio=smk'}
          >
            BROWSE AVAILABILITY
          </Button>
          <Button 
            size="lg"
            className="border-2 border-white bg-transparent text-white hover:bg-white hover:text-zinc-800 px-8 py-3 tracking-wide transition-all hover:scale-105"
            onClick={() => window.open('https://dash-production-b25c.up.railway.app/tour-schedule?email_address=Brooklyn@VectorNY.com', '_blank')}
          >
            SCHEDULE A TOUR
          </Button>
        </div>
        
        <div className="pt-8 border-t border-zinc-600">
          <p className="text-sm text-zinc-400">
            Professional leasing team available Monday-Friday, 9AM-6PM
          </p>
        </div>
      </div>
    </section>
  );
}; 