with open('templates/listings.html', 'r') as f:
    content = f.read()

# Fix availability tag
old_availability_tag = '''                                <div class="available-tag">
                                    {% if listing.expiry and listing.expiry|datetimeformat('U') > "now"|now_datetime('U') %}
                                        {% set expiry_date = listing.expiry|datetimeformat("m/d") %}
                                        Available on {{ expiry_date }}
                                    {% else %}
                                        Available Now
                                    {% endif %}
                                </div>'''

new_availability_tag = '''                                <div class="available-tag">
                                    {% if listing.expiry and listing.expiry != None and 'GMT' in listing.expiry %}
                                        {% set expiry_parts = listing.expiry.split(' ') %}
                                        Available on {{ expiry_parts[1] }} {{ expiry_parts[2] }}
                                    {% else %}
                                        Available Now
                                    {% endif %}
                                </div>'''

# Fix floor tag
old_floor_tag = '''                            {% if listing.floor %}
                            <span class="badge bg-info">Floor {{ listing.floor }}</span>
                            {% endif %}'''

new_floor_tag = '''                            {% if listing.floor and listing.floor != 0 %}
                            <span class="badge bg-info">Floor {{ listing.floor }}</span>
                            {% endif %}'''

# Fix exposure tag
old_exposure_tag = '''                            {% if listing.exposure %}
                            <span class="badge bg-secondary">{{ listing.exposure }} Exposure</span>
                            {% endif %}'''

new_exposure_tag = '''                            {% if listing.exposure and listing.exposure != '0' and listing.exposure != '' %}
                            <span class="badge bg-secondary">{{ listing.exposure }} Exposure</span>
                            {% endif %}'''

# Fix square footage tag
old_sqft_tag = '''                            <div class="feature-badge">
                                <i class="fas fa-vector-square"></i> {% if listing.sq_ft and listing.sq_ft != 'N/A' %}{{ listing.sq_ft }} ft²{% else %}N/A{% endif %}
                            </div>'''

new_sqft_tag = '''                            {% if listing.sq_ft and listing.sq_ft != 'N/A' and listing.sq_ft != 0 %}
                            <div class="feature-badge">
                                <i class="fas fa-vector-square"></i> {{ listing.sq_ft }} ft²
                            </div>
                            {% endif %}'''

# Replace all the patterns
content = content.replace(old_availability_tag, new_availability_tag)
content = content.replace(old_floor_tag, new_floor_tag)
content = content.replace(old_exposure_tag, new_exposure_tag)
content = content.replace(old_sqft_tag, new_sqft_tag)

with open('templates/listings.html', 'w') as f:
    f.write(content)

print("File updated successfully!")
