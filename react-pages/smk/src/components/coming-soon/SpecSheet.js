import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export const SpecSheet = ({ sections }) => {
  return (
    <motion.div 
      className="w-full max-w-4xl mx-auto mt-16"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.3 }}
    >
      <div className="text-center mb-12">
        <h2 className="tracking-wider mb-4 text-4xl font-thin text-zinc-400">
          Renovation Specifications
        </h2>
        <div className="w-24 h-0.5 mx-auto bg-slate-600" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {sections.map((section, sectionIndex) => (
          <motion.div 
            key={section.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 + sectionIndex * 0.2 }}
          >
            <Card className="bg-white border-zinc-200 shadow-lg hover:shadow-xl transition-shadow duration-300">
              <CardHeader className="pb-4">
                <CardTitle className="text-xl font-medium text-zinc-800 flex items-center">
                  <div className="w-2 h-2 bg-zinc-600 rounded-full mr-3"></div>
                  {section.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="py-[32px]">
                <ul className="space-y-4">
                  {section.specs.map((spec, index) => (
                    <motion.li 
                      key={index}
                      className="text-zinc-600 leading-relaxed"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: 0.6 + index * 0.1 }}
                    >
                      <div className="flex items-start">
                        <span className="inline-block w-2 h-2 bg-zinc-600 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                        <div>
                          <span className="font-medium text-zinc-700">{spec.title}:</span>{' '}
                          <span className="text-zinc-600">{spec.description}</span>
                        </div>
                      </div>
                    </motion.li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Additional Notes */}
      <motion.div 
        className="mt-8 text-center"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 1.2 }}
      >
        <p className="text-sm text-zinc-500 italic">
          All specifications are subject to change. Final selections may vary by unit.
        </p>
      </motion.div>
    </motion.div>
  );
}; 