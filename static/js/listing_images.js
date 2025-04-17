/**
 * Random apartment images for listings from Unsplash
 */
// Check if the variable exists already before declaring it
if (typeof window.vectorNYApartmentImages === 'undefined') {
  window.vectorNYApartmentImages = [
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=800&q=80", // Modern living room with large windows
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=800&q=80", // Luxurious apartment with view
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=800&q=80", // Minimalist apartment with city view
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=800&q=80", // Modern kitchen with island
    "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80", // Luxury home exterior
    "https://images.unsplash.com/photo-1567767292278-a4f21aa2d36e?auto=format&fit=crop&w=800&q=80", // Modern bathroom with bathtub
    "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=800&q=80", // Apartment with balcony
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=800&q=80", // Kitchen and living area with high ceiling
    "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=800&q=80", // Contemporary bedroom
    "https://images.unsplash.com/photo-1507149833265-60c372daea22?auto=format&fit=crop&w=800&q=80", // Living room with open floor plan
    "https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&w=800&q=80", // Modern bedroom with large windows
    "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?auto=format&fit=crop&w=800&q=80"  // Cozy bedroom with city view
  ];
}

// Function to assign random image to apartment listings
function getRandomApartmentImage() {
  const randomIndex = Math.floor(Math.random() * window.vectorNYApartmentImages.length);
  return window.vectorNYApartmentImages[randomIndex];
}
