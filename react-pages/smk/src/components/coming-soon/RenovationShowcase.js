import { motion } from 'framer-motion';
import { SimpleCarousel } from './SimpleCarousel';
import { SpecSheet } from './SpecSheet';

export const RenovationShowcase = () => {
  // Spec sheet data
  const specSections = [
    {
      title: 'Kitchen Specs',
      specs: [
        {
          title: 'Floor & Wall Tile',
          description: 'Vigo White 12″ × 24″ Matte Ceramic Marble-Look'
        },
        {
          title: 'Tub & Shower Combo',
          description: 'Glacier Bay Modern Single-Handle 1-Spray Faucet'
        },
        {
          title: 'Fixtures',
          description: 'Matte Black Stainless Steel Hardware Set (4-piece)'
        },
        {
          title: 'Door Handles',
          description: 'Probrico Matte Black Privacy Levers (10-pack)'
        },
        {
          title: 'Medicine Cabinet',
          description: 'KOHLER 30″×26″ Rectangular Mirrored Cabinet'
        },
        {
          title: 'Vanity Light',
          description: 'Maxim Spec 24″ LED Bath Bar (ADA-Compliant)'
        }
      ]
    },
    {
      title: 'Bathroom Specs',
      specs: [
        {
          title: 'Floor Tile',
          description: 'Florida Tile Home Collection 12″× 24 Porcelain'
        },
        {
          title: 'Backsplash',
          description: 'Satori Blanco 11″×12″ Marble Herringbone (0.9 sqft/pc)'
        },
        {
          title: 'Cabinet Pulls',
          description: 'Ravinte Matte Black Solid Handles (10-pack)'
        },
        {
          title: 'Vanity Light',
          description: 'Maxim Spec 24 LD Bath Bar (ADA-Compliant)'
        },
        {
          title: 'Faucet',
          description: 'JEAREY 375″ Black Waterfall Sink Faucet'
        },
        {
          title: 'Vanity',
          description: 'JEAREY 55.5″ Gray Chenille Loveseat-Style Vanity'
        }
      ]
    }
  ];

  return (
    <section className="py-24 bg-gradient-to-br from-zinc-600 via-zinc-700 to-zinc-800 bg-transparent">
      <div className="container mx-auto px-6 bg-transparent rounded">
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-3xl tracking-wider text-zinc-100 mb-6 font-thin md:text-4xl">
            Renovation Showcase
          </h2>
          <div className="w-24 h-0.5 bg-zinc-300 mx-auto mb-8" />
          <p className="text-zinc-200 max-w-2xl mx-auto text-lg font-normal">
            Discover the exciting improvements coming to your community
          </p>
        </motion.div>

        {/* SimpleCarousel */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="bg-transparent"
        >
          <SimpleCarousel autoplay={true} autoplayDelay={5000} />
        </motion.div>

        {/* Spec Sheet */}
        <SpecSheet sections={specSections} />
      </div>
    </section>
  );
}; 