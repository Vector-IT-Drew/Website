import os
from replit import db
from database import seed_sample_data

# Clear all keys from the database
for key in db.keys():
    del db[key]

print("Database cleared successfully.")

# Seed the database with sample data
seed_sample_data()
print("Database seeded with sample data.")