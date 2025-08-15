from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, FloatField, IntegerField, BooleanField, DateField
from wtforms.validators import DataRequired, Email, Length, Optional

class LoginForm(FlaskForm):
    """Admin login form"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ListingForm(FlaskForm):
    """Form for adding/editing property listings"""
    title = StringField('Title', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    unit = StringField('Unit/Apt #', validators=[Optional()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired(), Length(min=2, max=2)])
    zip_code = IntegerField('ZIP Code', validators=[DataRequired()])
    price = IntegerField('Price ($)', validators=[DataRequired()])
    beds = FloatField('Bedrooms', validators=[DataRequired()])
    baths = FloatField('Bathrooms', validators=[DataRequired()])
    sq_ft = IntegerField('Square Footage', validators=[DataRequired()])
    property_type = SelectField('Property Type', 
                               choices=[
                                   ('Apartment', 'Apartment'),
                                   ('House', 'House'),
                                   ('Condo', 'Condo'),
                                   ('Townhouse', 'Townhouse'),
                                   ('Multi-family', 'Multi-family'),
                                   ('Land', 'Land'),
                                   ('Other', 'Other')
                               ],
                               validators=[DataRequired()])
    floor = StringField('Floor', validators=[Optional()])
    total_floors = IntegerField('Total Floors in Building', validators=[Optional()])
    exposure = SelectField('Exposure',
                          choices=[
                              ('', 'Select Exposure'),
                              ('North', 'North'),
                              ('South', 'South'),
                              ('East', 'East'),
                              ('West', 'West'),
                              ('Northeast', 'Northeast'),
                              ('Northwest', 'Northwest'),
                              ('Southeast', 'Southeast'),
                              ('Southwest', 'Southwest')
                          ],
                          validators=[Optional()])
    pets_policy = SelectField('Pets Policy',
                             choices=[
                                 ('', 'Select Pets Policy'),
                                 ('No Pets', 'No Pets'),
                                 ('Cats Only', 'Cats Only'),
                                 ('Dogs Only', 'Dogs Only'),
                                 ('Cats & Dogs', 'Cats & Dogs'),
                                 ('Case by Case', 'Case by Case')
                             ],
                             validators=[Optional()])
    availability_date = DateField('Available From', format='%Y-%m-%d', validators=[Optional()])
    building_amenities = TextAreaField('Building Amenities (one per line)', validators=[Optional()])
    neighborhood = StringField('Neighborhood', validators=[Optional()])
    description = TextAreaField('Description', validators=[DataRequired()])
    features = TextAreaField('Features (one per line)', validators=[DataRequired()])
    contact_email = StringField('Contact Email', validators=[DataRequired(), Email()])
    contact_phone = StringField('Contact Phone', validators=[DataRequired()])
    submit = SubmitField('Save Listing')

class ApplicationForm(FlaskForm):
    """Form for applying to a property"""
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    move_in_date = DateField('Move-in Date', validators=[DataRequired()], format='%Y-%m-%d')
    lease_term = SelectField('Lease Term', choices=[
        ('12', '12 Months'),
        ('6', '6 Months'),
        ('3', '3 Months'),
        ('month-to-month', 'Month-to-Month')
    ], validators=[DataRequired()])
    message = TextAreaField('Additional Information', validators=[Optional()])
    agree_terms = BooleanField('Agree to Terms', validators=[DataRequired()])
    submit = SubmitField('Submit Application')
