import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';

export const UpdatesSection = () => {
  const [email, setEmail] = useState('');

  const handleEmailSubmit = (e) => {
    e.preventDefault();
    if (!email) return;
    alert('Thanks for subscribing! You\'ll receive updates about our renovation progress.');
    setEmail('');
  };

  return (
    <section className="py-24 bg-zinc-700">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl tracking-wider mb-6 font-thin text-zinc-50 md:text-4xl">
              Stay Updated
            </h2>
            <div className="w-24 h-0.5 mx-auto mb-8 bg-zinc-50" />
            <p className="text-lg text-zinc-300 max-w-2xl mx-auto">
              Be the first to know about renovation progress, timeline updates, and new amenity announcements.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <Card className="bg-zinc-800 border-zinc-600">
              <CardHeader>
                <CardTitle className="text-zinc-100 text-xl font-medium">
                  Want updates and alerts for upcoming renovations?
                </CardTitle>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleEmailSubmit} className="space-y-4">
                  <div>
                    <Label htmlFor="email" className="text-zinc-300">
                      Email Address
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your.email@example.com"
                      required
                      className="mt-1 border-zinc-600 text-zinc-100 placeholder:text-zinc-400 bg-zinc-700"
                    />
                  </div>
                  <Button
                    type="submit"
                    className="w-full text-zinc-100 bg-zinc-600 hover:bg-zinc-500 text-base font-extrabold"
                  >
                    Subscribe for Updates
                  </Button>
                </form>
                <p className="text-xs text-zinc-400 mt-3">
                  We respect your privacy. Unsubscribe at any time.
                </p>
              </CardContent>
            </Card>

            <Card className="bg-zinc-800 border-zinc-600">
              <CardHeader>
                <CardTitle className="text-zinc-100 text-xl font-medium">
                  Have questions on renovations? feedback?
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <p className="text-zinc-300">
                  Our team is here to answer any questions about upcoming improvements and how they might affect your daily routine.
                </p>
                
                <div className="space-y-3">
                  <Button
                    variant="outline"
                    onClick={() => window.location.href = '/'}
                    className="w-full border-zinc-600 font-extrabold text-zinc-50 bg-zinc-600 hover:bg-zinc-500"
                  >
                    Return to Main Site
                  </Button>
                  
                  <Button
                    variant="outline"
                    className="w-full border-zinc-600 text-zinc-50 bg-zinc-600 hover:bg-zinc-500 font-extrabold"
                  >
                    Contact Management
                  </Button>
                </div>
                
                <p className="text-xs text-zinc-400">
                  Office hours: Monday-Friday, 9AM-6PM
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </section>
  );
}; 