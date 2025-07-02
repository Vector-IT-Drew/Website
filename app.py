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

DASH_SERVICES_ENDPOINT = 'https://dash-production-b25c.up.railway.app'

UNIQUE_VALUES_API_ENDPOINT = "https://dash-production-b25c.up.railway.app" + "/unique-values"

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
    return render_template('investor_services.html', DASH_SERVICES_ENDPOINT=DASH_SERVICES_ENDPOINT)

@app.route('/vector-highlights')
def vectorHighlights():
    return render_template('vectorHighlights.html')




@app.route('/smk')
@app.route('/SMK')
def smk_redirect():
    """Redirect /smk or /SMK to external Greenpoint Vista landing page"""
    from flask import redirect
    return redirect('https://greenpoint-vista-landing.lovable.app/', code=302)

@app.route('/about')
def about():
    """About Us page for Vector New York"""
    return render_template('about.html', DASH_SERVICES_ENDPOINT=DASH_SERVICES_ENDPOINT)

@app.route('/listings')
def listings():
    """Display all available listings with advanced filtering and sorting"""
    # Fetch unique neighborhoods and addresses
    try:
        response = requests.get(UNIQUE_VALUES_API_ENDPOINT)
        unique_values = response.json()
        print("Unique values response:", unique_values)  # Debugging line
    except Exception as e:
        unique_values = {"unique_neighborhoods": [], "unique_addresses": []}
        print(f"Error fetching unique values: {e}")

    # Extract filter parameters from the request
    address = request.args.get('address')
    unit = request.args.get('unit')
    neighborhood = request.args.get('neighborhood')
    availability = request.args.get('availability')
    portfolio = request.args.get('portfolio')

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
    else:
        available = False

    # Determine sort option and map to SQL ORDER BY clause
    sort_option = request.args.get('sort', 'price_asc')

    # Get filtered and sorted listings from database/API
    listings_data = get_all_listings(address=address,
                                     unit=unit,
                                     neighborhood=neighborhood,
                                     min_price=min_price,
                                     max_price=max_price,
                                     beds=beds,
                                     baths=baths,
                                     available=available,
                                     portfolio=portfolio,
                                     sort=sort_option)

    return render_template(
        'listings.html',
        listings=listings_data,
        unique_neighborhoods=unique_values.get('unique_neighborhoods', []),
        unique_addresses=unique_values.get('unique_addresses', [])
    )

@app.route('/listings/<listing_id>')
def listing_detail(listing_id):
    """Display detail page for a specific listing"""
    listing = get_listing(listing_id)
    if not listing:
        flash('Listing not found', 'danger')
        return redirect(url_for('index'))
    return render_template('listing.html', listing=listing, DASH_SERVICES_ENDPOINT=DASH_SERVICES_ENDPOINT)


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

# Add this to ensure session is cleared when browser is closed
@app.before_request
def clear_session_on_new_visit():
    # Check if this is a new browser session
    if 'visited' not in session:
        # Clear any existing session data
        session.clear()
        # Set visited flag
        session['visited'] = True

@app.route('/payment-success')
def payment_success():
    # Get parameters from URL
    stripe_total = request.args.get('stripe_total', '0')
    payment_method = request.args.get('payment_method', 'card')
    address = request.args.get('address', '')
    unit = request.args.get('unit', '')
    
    # Convert stripe_total to float and format as currency
    try:
        total_amount = float(stripe_total)
        formatted_amount = "${:,.2f}".format(total_amount)
    except ValueError:
        formatted_amount = stripe_total
    
    
    return render_template('payment_success.html', 
                          amount=formatted_amount, 
                          payment_method=payment_method,
                          address=address,
                          unit=unit)
