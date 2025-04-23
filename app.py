import os
import logging
import datetime
import json
import requests
from flask import Flask, render_template, redirect, url_for, flash, request, session, abort, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoginForm, ListingForm, ApplicationForm
from database import get_listing, get_all_listings, filter_listings_by_budget, filter_listings_by_bedrooms, filter_listings_by_location
from functools import wraps
import markdown2
from dotenv import load_dotenv
load_dotenv()

# Initialize requests session for API calls to maintain cookies and state
api_session = requests.Session()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

app.config['DASH_SERVICES_ENDPOINT'] = 'https://dash-production-b25c.up.railway.app'


@app.template_filter('markdown')
def markdown_filter(text):
    return markdown2.markdown(text)


# Custom Jinja filter to parse JSON strings
@app.template_filter('from_json')
def from_json(value):
    try:
        return json.loads(value)
    except:
        return []


# Add context processor to inject current date into all templates
@app.context_processor
def inject_now():
    return {'now': datetime.datetime.now()}


# Admin credentials (in a real app, these would be stored securely)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash(
    "admin123")  # Default password, would be changed in production


# Authentication decorator
def admin_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('You need to be logged in as admin to access this page',
                  'danger')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)

    return decorated_function


# Routes
@app.route('/')
def index():
    # Clear any existing session data on page load
    logging.debug("Accessing the homepage")
    session.clear()

    logging.debug("Returning Homepage")
    return render_template('index.html')


@app.route('/investor-services')
def investor_services():
    """Display investor services page"""
    return render_template('investor_services.html')


@app.route('/listings')
def listings():
    """Display all available listings with advanced filtering and sorting"""
    # Extract filter parameters from the request
    address = request.args.get('address')
    unit = request.args.get('unit')
    neighborhood = request.args.get('neighborhood')
    availability = request.args.get('availability')

    # Get min/max price as integers if provided
    min_price = None
    max_price = None
    if request.args.get('min_price'):
        try:
            min_price = int(request.args.get('min_price'))
        except ValueError:
            pass
    if request.args.get('max_price'):
        try:
            max_price = int(request.args.get('max_price'))
        except ValueError:
            pass

    # Get beds/baths as floats if provided
    beds = None
    baths = None
    if request.args.get('beds'):
        try:
            beds = float(request.args.get('beds'))
        except ValueError:
            pass
    if request.args.get('baths'):
        try:
            baths = float(request.args.get('baths'))
        except ValueError:
            pass

    # Parse availability as boolean
    available = None
    if availability == 'available':
        available = True
    elif availability == 'coming_soon':
        available = False

    # We removed the property_type filter as requested

    # Determine sort option and map to SQL ORDER BY clause
    sort_option = request.args.get('sort', 'price_asc')

    # # Map the sort options to SQL ORDER BY clauses to send to the API
    # sort_sql = ''
    # if sort_option == 'price_asc':
    #     sort_sql = "ORDER BY d.`actual_rent ASC"
    # elif sort_option == 'price_desc':
    #     sort_sql = "ORDER BY d.actual_rent DESC"
    # elif sort_option == 'newest':
    #     # You could add a date-based sorting here if the API supports it
    #     sort_sql = "ORDER BY d.expiry DESC"
    # elif sort_option == 'size_desc':
    #     sort_sql = "ORDER BY u.sqft DESC"

    # Get filtered and sorted listings from database/API
    listings_data = get_all_listings(address=address,
                                     unit=unit,
                                     beds=beds,
                                     baths=baths,
                                     neighborhood=neighborhood,
                                     min_price=min_price,
                                     max_price=max_price,
                                     available=available,
                                     sort=sort_option)

    return render_template('listings.html', listings=listings_data)

@app.route('/listings/<listing_id>')
def listing_detail(listing_id):
    """Display detail page for a specific listing"""
    listing = get_listing(listing_id)
    if not listing:
        flash('Listing not found', 'danger')
        return redirect(url_for('index'))
    return render_template('listing.html', listing=listing)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page for Vector New York"""
    if request.method == 'POST':
        # In a real app, you would process the form data here
        # For now, just flash a success message
        flash(
            'Your message has been sent successfully! We will get back to you soon.',
            'success')
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard to manage listings"""
    listings = get_all_listings()
    return render_template('admin/dashboard.html', listings=listings)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# Vector Assistant Routes
@app.route('/start_chat', methods=['POST'])
def start_chat():
    """Initialize chat session with Vector Assistant"""
    # Clear all existing chat data
    session.clear()
    
    # Initialize session variables for chat
    session['chat_history'] = []
    
    # Add the welcome message to chat history
    welcome_message = "Hi there! I'm Vector Assistant, your personal NYC apartment hunting guide. Let's start with the basics - how many bedrooms are you looking for in your new apartment?"
    session['chat_history'].append({'role': 'assistant', 'message': welcome_message})
    
    # Initialize empty preferences
    session['chat_preferences'] = {}
    
    # Don't initialize the backend chat yet - we'll do that when the user responds
    
    return jsonify({
        'status': 'success',
        'initial_message': welcome_message
    })


@app.route('/chat', methods=['POST'])
def chat():
    """Process chat message and return response using external AI recommendation system"""
    data = request.json
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({
            'response': "I'm sorry, I didn't receive a message. How can I help you?"
        })

    # Initialize chat history if not exists
    if 'chat_history' not in session:
        session['chat_history'] = []
        session['chat_preferences'] = {}

    # Add user message to history
    session['chat_history'].append({'role': 'user', 'message': user_message})

    # Check if this is the first user message (after welcome)
    is_first_message = len(session['chat_history']) <= 2

    try:
        # If this is the first message, initialize the backend chat
        if is_first_message:
            try:
                # Reset the API session to start fresh
                global api_session
                api_session = requests.Session()
                
                # Initialize the backend chat
                start_url = "http://dash-production-b25c.up.railway.app/start-chat"
                api_session.post(
                    start_url,
                    headers={'Content-Type': 'application/json'},
                    data=json.dumps({}),  # Send empty JSON object
                    timeout=10
                )
                print("Backend chat initialized")
            except Exception as e:
                logging.error(f"Error initializing backend chat: {str(e)}")

        # Send message to external API
        api_url = "http://dash-production-b25c.up.railway.app/chat"
        
        # Include preferences from previous interactions if they exist
        payload = {'message': user_message}
        
        if 'chat_preferences' in session and session['chat_preferences']:
            payload['preferences'] = session['chat_preferences']
        
        # IMPORTANT: Set the correct headers
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        # Log only that we're sending a message, not the full payload
        print(f"Request method: POST")
        print(f"Request headers: {headers}")
        print(f"Request payload: {json.dumps(payload)}")
        
        # Call the external API using session to maintain cookies and state
        response = api_session.post(
            api_url, 
            data=json.dumps(payload),
            headers=headers,
            timeout=10
        )
        
        # Log only the status code, not the response content
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text[:200]}...")
        
        # Parse the JSON response
        api_data = response.json()

        # Extract response message
        assistant_message = api_data.get('response', api_data.get('message', 
            "I'm sorry, I'm having trouble processing your request right now."))

        # Store preferences if provided by the API
        if 'preferences' in api_data:
            session['chat_preferences'] = api_data.get('preferences', {})

        # Add assistant message to history
        session['chat_history'].append({
            'role': 'assistant',
            'message': assistant_message
        })

        # Get the listing count if available
        listing_count = api_data.get('listing_count', 0)

        # Trim history if it gets too long
        if len(session['chat_history']) > 20:
            session['chat_history'] = session['chat_history'][-20:]

        # Debug the response
        print(f"API response keys: {api_data.keys()}")
        print(f"Listings in response: {len(api_data.get('listings', []))}")
        print(f"Show listings flag: {api_data.get('preferences', {}).get('show_listings', False)}")

        return jsonify({
            'response': assistant_message,
            'listings': api_data.get('listings', []),
            'listing_count': listing_count,
            'show_listings': api_data.get('show_listings', api_data.get('preferences', {}).get('show_listings', False))
        })

    except requests.exceptions.Timeout:
        # Handle timeout specifically
        logging.error("Timeout connecting to recommendation API")
        fallback_response = (
            "I'm sorry, our recommendation system is taking longer than expected to respond. "
            "Please try again in a moment."
        )
        
        # Add fallback response to history
        session['chat_history'].append({
            'role': 'assistant',
            'message': fallback_response
        })
        
        return jsonify({'response': fallback_response, 'listings': []})
        
    except Exception as e:
        # Log the error with detailed information but limit traceback
        logging.error(f"Error communicating with recommendation API: {str(e)}")
        
        # Fallback to basic response
        fallback_response = (
            "I'm sorry, I'm having trouble connecting to our recommendation system right now. "
            "Please try again later or contact our support team for assistance."
        )

        # Add fallback response to history
        session['chat_history'].append({
            'role': 'assistant',
            'message': fallback_response
        })

        return jsonify({'response': fallback_response, 'listings': []})


@app.route('/reset_chat', methods=['POST'])
def reset_chat():
    """Reset the chat session and start a new one"""
    # Clear all existing chat data
    session.clear()
    
    try:
        # Reset the API session to start fresh
        global api_session
        api_session = requests.Session()
        
        # Call the backend to reset and start a new chat
        start_url = "http://dash-production-b25c.up.railway.app/start-chat"
        response = api_session.post(
            start_url,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        # Get the welcome message from the response
        welcome_data = response.json()
        welcome_message = welcome_data.get('message', "Welcome! How many bedrooms are you looking for?")
        
        # Initialize new session
        session['chat_history'] = []
        session['chat_preferences'] = {}
        
        # Add welcome message to history
        session['chat_history'].append({'role': 'assistant', 'message': welcome_message})
        
        return jsonify({
            'status': 'success',
            'welcome_message': welcome_message
        })
        
    except Exception as e:
        logging.error(f"Error resetting chat: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': "There was an error resetting the chat. Please try again."
        })


# Helper functions for the chat functionality
def filter_listings_by_budget(message):
    """Extract budget constraints and filter listings"""
    all_listings = get_all_listings()
    filtered_listings = []
    alternative_listings = []
    response = ""

    # Very basic filtering - in a real app, use proper NLP
    try:
        # Try to extract a price
        import re
        price_match = re.search(r'(\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?)', message)
        if price_match:
            price_str = price_match.group(1).replace('$', '').replace(',', '')
            price = int(float(price_str))

            # Determine if this is max or min budget
            if any(term in message.lower()
                   for term in ['maximum', 'max', 'under', 'less than']):
                filtered_listings = [
                    l for l in all_listings if l['price'] <= price
                ]
                response = f"I've found these apartments under ${price:,}. Each one fits within your budget!"
            elif any(term in message.lower()
                     for term in ['minimum', 'min', 'at least', 'more than']):
                filtered_listings = [
                    l for l in all_listings if l['price'] >= price
                ]
                response = f"Here are some luxury options starting at ${price:,}. Top-of-the-line amenities included!"
            else:
                # If unclear, assume it's around that price (±20%)
                min_price = price * 0.8
                max_price = price * 1.2
                filtered_listings = [
                    l for l in all_listings
                    if min_price <= l['price'] <= max_price
                ]
                response = f"I've found these apartments around ${price:,}. How do these match your expectations?"

                # Add alternative listings outside of the range
                for l in all_listings:
                    if l not in filtered_listings and (
                            l['price'] < min_price or l['price'] > max_price):
                        alternative_listings.append(l)
                alternative_listings = alternative_listings[:
                                                            2]  # Limit to 2 alternatives
        else:
            # If no specific price, return some listings
            filtered_listings = all_listings[:3]
            response = "I'd be happy to help you find apartments in your price range. Can you tell me your budget, like '$2,500 per month' or 'up to $3,000'?"
    except Exception as e:
        # Fallback to some listings if parsing fails
        filtered_listings = all_listings[:3]
        response = "I'd be happy to help you find apartments in your price range. Can you tell me your budget, like '$2,500 per month' or 'up to $3,000'?"

    # If no listings found
    if not filtered_listings:
        response = f"I couldn't find any apartments matching your budget criteria. Would you like to try a different price range?"
        filtered_listings = all_listings[:3]  # Return some default options

    return response, filtered_listings, alternative_listings


def filter_listings_by_bedrooms(message):
    """Extract bedroom requirements and filter listings"""
    all_listings = get_all_listings()
    filtered_listings = []
    alternative_listings = []
    response = ""

    # Very basic filtering - in a real app, use proper NLP
    try:
        # Try to extract number of bedrooms
        import re
        bed_match = re.search(r'(\d+)\s*(?:bed|bedroom|br)', message.lower())
        if bed_match:
            beds = float(bed_match.group(1))
            filtered_listings = [l for l in all_listings if l['beds'] == beds]

            if filtered_listings:
                if beds <= 1:
                    response = f"Here are the {beds} bedroom apartments I found. Perfect for individuals or couples!"
                elif beds == 2:
                    response = f"I found these {beds} bedroom apartments, great for small families or roommates!"
                else:
                    response = f"Check out these spacious {beds} bedroom apartments, ideal for larger families!"

                # Alternative listings with one more or one less bedroom
                alt_beds = [beds - 1, beds + 1]
                for l in all_listings:
                    if l not in filtered_listings and l['beds'] in alt_beds:
                        alternative_listings.append(l)
                alternative_listings = alternative_listings[:2]
            else:
                response = f"I couldn't find any {beds} bedroom apartments in our current listings. Would you like to see some alternatives?"
                # Return apartments with close to the requested number of bedrooms
                filtered_listings = [
                    l for l in all_listings if abs(l['beds'] - beds) <= 1
                ][:3]
        elif 'studio' in message.lower():
            filtered_listings = [l for l in all_listings if l['beds'] <= 1]
            if filtered_listings:
                response = "Here are the studio apartments I found. Compact and efficient living in the heart of the city!"
                # Add some 1-bedroom alternatives
                alternative_listings = [
                    l for l in all_listings
                    if l['beds'] == 1 and l not in filtered_listings
                ][:2]
            else:
                response = "I couldn't find any studio apartments in our current listings. Would you like to see other options?"
                filtered_listings = all_listings[:3]
        else:
            # If unclear, ask for clarification and return some diverse listings
            response = "I'd be happy to help you find an apartment with the right number of bedrooms. Could you specify how many bedrooms you need?"

            # Get a diverse set of listings with different bedroom counts
            bed_counts = set()
            for l in all_listings:
                if l['beds'] not in bed_counts and len(filtered_listings) < 3:
                    bed_counts.add(l['beds'])
                    filtered_listings.append(l)

            if len(filtered_listings) < 3:
                # Add more if needed
                for l in all_listings:
                    if l not in filtered_listings and len(
                            filtered_listings) < 3:
                        filtered_listings.append(l)
    except Exception as e:
        # Fallback to some listings if parsing fails
        response = "I'd be happy to help you find an apartment with the right number of bedrooms. Could you specify how many bedrooms you need?"
        filtered_listings = all_listings[:3]

    return response, filtered_listings, alternative_listings


def filter_listings_by_location(message):
    """Extract location preferences and filter listings"""
    all_listings = get_all_listings()
    filtered_listings = []
    alternative_listings = []
    response = ""

    # Check for common NYC neighborhoods (very basic)
    neighborhoods = {
        'manhattan':
        "Manhattan offers iconic city living with world-class dining, shopping, and cultural attractions.",
        'brooklyn':
        "Brooklyn combines urban energy with a neighborhood feel, featuring diverse communities and creative spaces.",
        'queens':
        "Queens is NYC's most diverse borough, offering authentic international cuisine and more affordable housing options.",
        'bronx':
        "The Bronx has a rich cultural heritage with attractions like the Bronx Zoo and Yankee Stadium, plus more space for your money.",
        'staten island':
        "Staten Island offers a more suburban feel with green spaces, while still providing access to Manhattan via the ferry.",
        'upper east side':
        "The Upper East Side is known for its elegant brownstones, Museum Mile, and proximity to Central Park.",
        'upper west side':
        "The Upper West Side combines cultural institutions, family-friendly parks, and diverse dining options.",
        'midtown':
        "Midtown is NYC's business and entertainment hub, home to iconic skyscrapers and world-famous attractions.",
        'downtown':
        "Downtown Manhattan offers historic neighborhoods with cobblestone streets alongside modern luxury buildings.",
        'east village':
        "The East Village has a bohemian history and now offers trendy shops, diverse dining, and a vibrant nightlife.",
        'west village':
        "The West Village features charming tree-lined streets, historic townhouses, and a laid-back atmosphere.",
        'chelsea':
        "Chelsea is known for its art galleries, High Line park, and a mix of historic and modern architecture.",
        'soho':
        "SoHo combines cast-iron architecture with high-end shopping, galleries, and trendy restaurants.",
        'tribeca':
        "TriBeCa offers converted industrial lofts, upscale dining, and a more relaxed downtown vibe."
    }

    found_neighborhood = None
    message_lower = message.lower()

    for neighborhood, description in neighborhoods.items():
        if neighborhood in message_lower:
            # Filter listings by this neighborhood
            filtered_listings = [
                l for l in all_listings
                if neighborhood in l.get('city', '').lower()
                or neighborhood in l.get('address', '').lower()
            ]

            if filtered_listings:
                found_neighborhood = neighborhood
                response = f"Great choice! {description} Here are some listings in {neighborhood.title()}:"

                # Find alternatives in other nearby neighborhoods
                if neighborhood in [
                        'upper east side', 'upper west side', 'midtown',
                        'east village', 'west village', 'chelsea', 'soho',
                        'tribeca'
                ]:
                    # All in Manhattan, so get other Manhattan neighborhoods
                    for l in all_listings:
                        if (l not in filtered_listings and
                            ('manhattan' in l.get('city', '').lower() or any(
                                n in l.get('address', '').lower() for n in [
                                    'upper east side', 'upper west side',
                                    'midtown', 'east village', 'west village',
                                    'chelsea', 'soho', 'tribeca'
                                ]))):
                            alternative_listings.append(l)
                else:
                    # Borough level, get some from other boroughs
                    for l in all_listings:
                        if l not in filtered_listings:
                            alternative_listings.append(l)

                alternative_listings = alternative_listings[:2]
                break

    # If no matches or no listings found
    if not found_neighborhood:
        response = "I'd be happy to help you find an apartment in your preferred neighborhood. Could you tell me which area of NYC interests you? Popular options include Manhattan, Brooklyn, or specific neighborhoods like SoHo or Chelsea."
        filtered_listings = all_listings[:3]
    elif not filtered_listings:
        response = f"I couldn't find any listings in {found_neighborhood.title()} right now. Would you like to explore properties in other neighborhoods?"
        filtered_listings = all_listings[:3]

    return response, filtered_listings, alternative_listings


def format_listings_for_chat(listings):
    """Format listings for the chat interface"""
    formatted_listings = []

    for listing in listings:
        # Format the title based on address and unit
        unit_text = f", Unit {listing.get('unit')}" if listing.get(
            'unit') else ""
        title = f"{listing.get('address')}{unit_text}"

        formatted_listing = {
            'id':
            listing.get('unit_id',
                        listing.get('id',
                                    '')),  # Prefer unit_id, fallback to id
            'title': title,
            'price': listing.get('price', 0),
            'beds': listing.get('beds', 0),
            'baths': listing.get('baths', 0),
            'address': listing.get('address', ''),
            'city': listing.get('city', 'New York'),
            'state': listing.get('state', 'NY'),
            'sq_ft': listing.get('sq_ft', 0),
            'image_url': listing.get('image_url',
                                     '')  # Add image URL to formatted listing
        }

        formatted_listings.append(formatted_listing)

    return formatted_listings


@app.route('/apply/<listing_id>', methods=['GET', 'POST'])
def apply(listing_id):
    """Application form for a specific listing"""
    # Get the listing
    listing = get_listing(listing_id)
    if not listing:
        flash('Listing not found', 'danger')
        return redirect(url_for('index'))

    # Create the application form
    form = ApplicationForm()

    if form.validate_on_submit():
        # In a real app, you would process the form data here
        # For now, just flash a success message
        flash(
            'Your application has been submitted successfully! Our team will contact you soon.',
            'success')
        return redirect(url_for('listing_detail', listing_id=listing_id))

    return render_template('apply.html', form=form, listing=listing)


@app.route('/about')
def about():
    """About Us page for Vector New York"""
    return render_template('about.html')

# Add this to ensure session is cleared when browser is closed
@app.before_request
def clear_session_on_new_visit():
    # Check if this is a new browser session
    if 'visited' not in session:
        # Clear any existing session data
        session.clear()
        # Set visited flag
        session['visited'] = True
