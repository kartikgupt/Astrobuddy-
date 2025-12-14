"""
Convert Kundali JSON file to comprehensive, human-readable HTML format
Shows ALL data from JSON in organized tables and sections
"""

import json
import os
import sys
from datetime import datetime


def format_degree(degree_value):
    """Convert degree value to degrees, minutes, seconds format"""
    if degree_value is None:
        return "N/A"
    
    try:
        degree = float(degree_value)
        deg = int(degree)
        minutes = int((degree - deg) * 60)
        seconds = int(((degree - deg) * 60 - minutes) * 60)
        return f"{deg}°{minutes}'{seconds}\""
    except (ValueError, TypeError):
        return "N/A"


def format_date(date_str):
    """Format ISO date string to readable format"""
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y')
    except:
        return date_str


def generate_html(kundali_data, output_path):
    """Generate comprehensive HTML file from kundali JSON data"""
    
    # Extract person information
    person = kundali_data.get('person', {})
    name = person.get('name', 'Unknown')
    birth_date = person.get('birthDate', '')
    birth_place = person.get('birthPlace', {})
    geo = birth_place.get('geo', {})
    latitude = geo.get('latitude', 'N/A')
    longitude = geo.get('longitude', 'N/A')
    
    # Extract chart data
    d1_chart = kundali_data.get('d1Chart', {})
    panchanga = kundali_data.get('panchanga', {})
    ayanamsa = kundali_data.get('ayanamsa', {})
    planets = d1_chart.get('planets', [])
    houses = d1_chart.get('houses', [])
    dasha = kundali_data.get('dasha', {})
    
    # Planet names
    planet_names = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter", 
        "Venus", "Saturn", "Rahu", "Ketu"
    ]
    
    # House names and meanings
    house_info = [
        ("1st House (Lagna)", "Self, Personality, Physical Appearance"),
        ("2nd House (Dhana)", "Wealth, Family, Speech, Food"),
        ("3rd House (Sahaja)", "Siblings, Courage, Communication, Short Journeys"),
        ("4th House (Sukha)", "Mother, Home, Education, Property, Vehicles"),
        ("5th House (Putra)", "Children, Creativity, Education, Romance"),
        ("6th House (Ripu)", "Enemies, Diseases, Debts, Service"),
        ("7th House (Kalatra)", "Spouse, Partnership, Marriage, Business"),
        ("8th House (Ayushya)", "Longevity, Occult, Transformation, Obstacles"),
        ("9th House (Bhagya)", "Fortune, Father, Higher Learning, Spirituality"),
        ("10th House (Karma)", "Career, Profession, Status, Reputation"),
        ("11th House (Labha)", "Gains, Friends, Desires, Income"),
        ("12th House (Vyaya)", "Expenses, Losses, Spirituality, Foreign Lands")
    ]
    
    # Start HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Kundali Report - {name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #2c3e50;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            padding: 40px;
        }}
        
        .header {{
            text-align: center;
            border-bottom: 4px solid #8b4513;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        
        .header h1 {{
            font-size: 2.8em;
            color: #8b4513;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }}
        
        .section {{
            margin-bottom: 50px;
            page-break-inside: avoid;
        }}
        
        .section-title {{
            font-size: 1.8em;
            color: #8b4513;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #d4a574;
            text-transform: uppercase;
        }}
        
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .info-card {{
            background: #fafafa;
            padding: 15px;
            border-left: 4px solid #8b4513;
            border-radius: 4px;
        }}
        
        .info-card strong {{
            display: block;
            color: #8b4513;
            margin-bottom: 8px;
            font-size: 0.9em;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            font-size: 0.9em;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        
        thead {{
            background: #8b4513;
            color: white;
        }}
        
        th {{
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
        }}
        
        td {{
            padding: 10px 8px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 0.9em;
        }}
        
        tbody tr:hover {{
            background: #f9f9f9;
        }}
        
        .sign {{
            font-weight: 600;
            color: #8b4513;
        }}
        
        .degree {{
            font-family: 'Courier New', monospace;
            color: #555;
            font-size: 0.85em;
        }}
        
        .planet-name {{
            font-weight: 700;
            color: #2c3e50;
        }}
        
        .sub-table {{
            margin: 10px 0;
            font-size: 0.85em;
        }}
        
        .sub-table th {{
            background: #d4a574;
            padding: 8px;
        }}
        
        .sub-table td {{
            padding: 6px 8px;
        }}
        
        .house-detail {{
            background: #fafafa;
            padding: 15px;
            margin-bottom: 15px;
            border-left: 4px solid #d4a574;
            border-radius: 4px;
        }}
        
        .house-detail h4 {{
            color: #8b4513;
            margin-bottom: 10px;
        }}
        
        .json-viewer {{
            background: #2c3e50;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.85em;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .footer {{
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid #e0e0e0;
            text-align: center;
            color: #888;
            font-size: 0.9em;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🪐 {name.upper()}'s COMPLETE KUNDALI</h1>
            <p style="font-size: 1.2em; color: #666;">Complete Vedic Astrology Birth Chart Report</p>
        </div>
        
        <!-- Birth Information -->
        <div class="section">
            <h2 class="section-title">📋 Birth Information</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>Name</strong>
                    <span>{name}</span>
                </div>
                <div class="info-card">
                    <strong>Birth Date & Time</strong>
                    <span>{format_date(birth_date)}</span>
                </div>
                <div class="info-card">
                    <strong>Birth Location</strong>
                    <span>Lat: {latitude}, Long: {longitude}</span>
                </div>
                <div class="info-card">
                    <strong>Ayanamsa</strong>
                    <span>{ayanamsa.get('name', 'N/A')} ({ayanamsa.get('value', 0):.4f}°)</span>
                </div>
            </div>
        </div>
        
        <!-- Panchanga Section -->
        <div class="section">
            <h2 class="section-title">📅 Panchanga (Five Limbs)</h2>
            <div class="info-grid">
                <div class="info-card">
                    <strong>Tithi</strong>
                    <span>{panchanga.get('tithi', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Nakshatra</strong>
                    <span>{panchanga.get('nakshatra', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Yoga</strong>
                    <span>{panchanga.get('yoga', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Karana</strong>
                    <span>{panchanga.get('karana', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Vaara</strong>
                    <span>{panchanga.get('vaara', 'N/A')}</span>
                </div>
            </div>
        </div>
        
        <!-- Ascendant Section -->
        <div class="section">
            <h2 class="section-title">🌅 Ascendant (Lagna)</h2>
"""
    
    # Ascendant details
    if houses:
        first_house = houses[0]
        html_content += f"""
            <div class="info-grid">
                <div class="info-card">
                    <strong>Sign</strong>
                    <span class="sign">{first_house.get('sign', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Degree</strong>
                    <span class="degree">{format_degree(first_house.get('signDegrees'))}</span>
                </div>
                <div class="info-card">
                    <strong>Lord</strong>
                    <span>{first_house.get('lord', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Nakshatra</strong>
                    <span>{first_house.get('nakshatra', 'N/A')} (Pada {first_house.get('pada', 'N/A')})</span>
                </div>
                <div class="info-card">
                    <strong>Nakshatra Deity</strong>
                    <span>{first_house.get('nakshatraDeity', 'N/A')}</span>
                </div>
                <div class="info-card">
                    <strong>Lord Placed</strong>
                    <span>House {first_house.get('lordPlacedHouse', 'N/A')} ({first_house.get('lordPlacedSign', 'N/A')})</span>
                </div>
            </div>
"""
    
    html_content += """
        </div>
        
        <!-- Planets Detailed Table -->
        <div class="section">
            <h2 class="section-title">🪐 Complete Planetary Positions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Planet</th>
                        <th>Sign</th>
                        <th>Degree</th>
                        <th>House</th>
                        <th>Nakshatra</th>
                        <th>Pada</th>
                        <th>Deity</th>
                        <th>Motion</th>
                        <th>Lordships</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add planets rows with all details
    for i, planet in enumerate(planets):
        if i < len(planet_names):
            planet_name = planet_names[i]
            sign = planet.get('sign', 'N/A')
            degree = format_degree(planet.get('signDegrees'))
            house = planet.get('house', 'N/A')
            nakshatra = planet.get('nakshatra', 'N/A')
            pada = planet.get('pada', 'N/A')
            deity = planet.get('nakshatraDeity', 'N/A')
            motion = planet.get('motion_type', 'N/A')
            lordships = planet.get('hasLordshipHouses', [])
            lordship_str = ', '.join([f"H{ls}" for ls in lordships]) if lordships else 'None'
            
            html_content += f"""
                    <tr>
                        <td class="planet-name">{planet_name}</td>
                        <td class="sign">{sign}</td>
                        <td class="degree">{degree}</td>
                        <td>{house}</td>
                        <td>{nakshatra}</td>
                        <td>{pada}</td>
                        <td>{deity}</td>
                        <td>{motion}</td>
                        <td>{lordship_str}</td>
                    </tr>
"""
    
    html_content += """
                </tbody>
            </table>
        </div>
        
        <!-- Planets Shadbala -->
        <div class="section">
            <h2 class="section-title">💪 Planetary Shadbala (Six-fold Strength)</h2>
"""
    
    # Shadbala for each planet
    for i, planet in enumerate(planets):
        if i < len(planet_names):
            planet_name = planet_names[i]
            shadbala = planet.get('shadbala', {})
            if shadbala:
                shadbala_total = shadbala.get('Shadbala', {}).get('Total', 0)
                shadbala_rupas = shadbala.get('Shadbala', {}).get('Rupas', 0)
                min_required = shadbala.get('Shadbala', {}).get('MinRequired', 0)
                meets_req = shadbala.get('Shadbala', {}).get('MeetsRequirement', 'N/A')
                
                sthanabala = shadbala.get('Sthanabala', {})
                digbala = shadbala.get('Digbala', 0)
                kaalabala = shadbala.get('Kaalabala', {})
                cheshtabala = shadbala.get('Cheshtabala', 0)
                naisargikabala = shadbala.get('Naisargikabala', 0)
                drikbala = shadbala.get('Drikbala', 0)
                
                html_content += f"""
            <h3 style="color: #8b4513; margin-top: 20px; margin-bottom: 10px;">{planet_name}</h3>
            <table class="sub-table">
                <thead>
                    <tr>
                        <th>Component</th>
                        <th>Value</th>
                        <th>Details</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Sthanabala</strong></td>
                        <td>{sthanabala.get('Total', 0):.2f}</td>
                        <td>Uchha: {sthanabala.get('Uchhabala', 0):.2f}, Saptavarga: {sthanabala.get('Saptavargajabala', 0):.2f}, Kendradhi: {sthanabala.get('Kendradhibala', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Digbala</strong></td>
                        <td>{digbala:.2f}</td>
                        <td>Directional Strength</td>
                    </tr>
                    <tr>
                        <td><strong>Kaalabala</strong></td>
                        <td>{kaalabala.get('Total', 0):.2f}</td>
                        <td>Natonnata: {kaalabala.get('Natonnatabala', 0):.2f}, Paksha: {kaalabala.get('Pakshabala', 0):.2f}, Ayana: {kaalabala.get('Ayanabala', 0):.2f}</td>
                    </tr>
                    <tr>
                        <td><strong>Cheshtabala</strong></td>
                        <td>{cheshtabala:.2f}</td>
                        <td>Motion Strength</td>
                    </tr>
                    <tr>
                        <td><strong>Naisargikabala</strong></td>
                        <td>{naisargikabala:.2f}</td>
                        <td>Natural Strength</td>
                    </tr>
                    <tr>
                        <td><strong>Drikbala</strong></td>
                        <td>{drikbala:.2f}</td>
                        <td>Aspect Strength</td>
                    </tr>
                    <tr style="background: #fff3cd;">
                        <td><strong>Total Shadbala</strong></td>
                        <td><strong>{shadbala_total:.2f}</strong></td>
                        <td><strong>{shadbala_rupas:.2f} Rupas (Min: {min_required:.2f}, Status: {meets_req})</strong></td>
                    </tr>
                </tbody>
            </table>
"""
    
    html_content += """
        </div>
        
        <!-- Planets Dignities and Aspects -->
        <div class="section">
            <h2 class="section-title">⭐ Planetary Dignities & Aspects</h2>
"""
    
    # Dignities and Aspects for each planet
    for i, planet in enumerate(planets):
        if i < len(planet_names):
            planet_name = planet_names[i]
            dignities = planet.get('dignities', {})
            aspects = planet.get('aspects', {})
            conjuncts = planet.get('conjuncts', [])
            
            html_content += f"""
            <h3 style="color: #8b4513; margin-top: 20px; margin-bottom: 10px;">{planet_name}</h3>
            <table class="sub-table">
                <thead>
                    <tr>
                        <th>Attribute</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Dignity</strong></td>
                        <td>{dignities.get('dignity', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Planet Tattva</strong></td>
                        <td>{dignities.get('planetTattva', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Rashi Tattva</strong></td>
                        <td>{dignities.get('rashiTattva', 'N/A')}</td>
                    </tr>
                    <tr>
                        <td><strong>Friendly Tattvas</strong></td>
                        <td>{', '.join(dignities.get('friendlyTattvas', [])) or 'N/A'}</td>
                    </tr>
                    <tr>
                        <td><strong>Conjunctions</strong></td>
                        <td>{', '.join(conjuncts) if conjuncts else 'None'}</td>
                    </tr>
                    <tr>
                        <td><strong>Aspects Given</strong></td>
                        <td>
"""
            # Aspects given
            aspects_given = aspects.get('gives', [])
            if aspects_given:
                aspect_list = []
                for asp in aspects_given:
                    if 'to_house' in asp:
                        aspect_list.append(f"House {asp['to_house']} ({asp.get('aspect_type', '')})")
                    elif 'to_planet' in asp:
                        aspect_list.append(f"{asp['to_planet']} ({asp.get('aspect_type', '')})")
                html_content += ', '.join(aspect_list) if aspect_list else 'None'
            else:
                html_content += 'None'
            
            html_content += """
                        </td>
                    </tr>
                    <tr>
                        <td><strong>Aspects Received</strong></td>
                        <td>
"""
            # Aspects received
            aspects_received = aspects.get('receives', [])
            if aspects_received:
                aspect_list = [f"{asp.get('from_planet', 'Unknown')} ({asp.get('aspect_type', '')})" for asp in aspects_received]
                html_content += ', '.join(aspect_list)
            else:
                html_content += 'None'
            
            html_content += """
                        </td>
                    </tr>
                </tbody>
            </table>
"""
    
    html_content += """
        </div>
        
        <!-- Houses Detailed -->
        <div class="section">
            <h2 class="section-title">🏠 Complete House Analysis</h2>
"""
    
    # Houses with all details
    for i, house in enumerate(houses):
        if i < len(house_info):
            house_name, house_meaning = house_info[i]
            house_num = house.get('number', i + 1)
            sign = house.get('sign', 'N/A')
            lord = house.get('lord', 'N/A')
            lord_placed_house = house.get('lordPlacedHouse', 'N/A')
            lord_placed_sign = house.get('lordPlacedSign', 'N/A')
            occupants = house.get('occupants', [])
            aspects = house.get('aspectsReceived', [])
            purposes = house.get('purposes', [])
            nakshatra = house.get('nakshatra', 'N/A')
            bhava_bala = house.get('bhavaBala', 0)
            
            html_content += f"""
            <div class="house-detail">
                <h4>{house_name} - {house_meaning}</h4>
                <table class="sub-table">
                    <tr>
                        <td><strong>Sign:</strong></td>
                        <td class="sign">{sign}</td>
                        <td><strong>Lord:</strong></td>
                        <td>{lord}</td>
                    </tr>
"""
            if house.get('signDegrees'):
                html_content += f"""
                    <tr>
                        <td><strong>Degree:</strong></td>
                        <td class="degree">{format_degree(house.get('signDegrees'))}</td>
                        <td><strong>Bhava Bala:</strong></td>
                        <td>{bhava_bala:.2f}</td>
                    </tr>
"""
            html_content += f"""
                    <tr>
                        <td><strong>Lord Placed:</strong></td>
                        <td>House {lord_placed_house} ({lord_placed_sign})</td>
                        <td><strong>Nakshatra:</strong></td>
                        <td>{nakshatra} (Pada {house.get('pada', 'N/A')})</td>
                    </tr>
                    <tr>
                        <td><strong>Purposes:</strong></td>
                        <td colspan="3">{', '.join(purposes) if purposes else 'N/A'}</td>
                    </tr>
"""
            if occupants:
                html_content += f"""
                    <tr>
                        <td><strong>Occupants:</strong></td>
                        <td colspan="3">
"""
                for occ in occupants:
                    occ_body = occ.get('celestialBody', 'Unknown')
                    occ_sign = occ.get('sign', 'N/A')
                    occ_degree = format_degree(occ.get('signDegrees'))
                    html_content += f"{occ_body} in {occ_sign} ({occ_degree}), "
                html_content = html_content.rstrip(', ') + "</td></tr>"
            
            if aspects:
                html_content += f"""
                    <tr>
                        <td><strong>Aspects Received:</strong></td>
                        <td colspan="3">
"""
                aspect_list = [f"{asp.get('aspecting_planet', 'Unknown')} ({asp.get('aspect_type', '')})" for asp in aspects]
                html_content += ', '.join(aspect_list) + "</td></tr>"
            
            html_content += """
                </table>
            </div>
"""
    
    html_content += """
        </div>
        
        <!-- Dasha Information -->
        <div class="section">
            <h2 class="section-title">⏳ Complete Dasha Information</h2>
"""
    
    # Complete Dasha information
    if dasha:
        current_dasha = dasha.get('currentDasha', {})
        if current_dasha:
            html_content += f"""
            <h3 style="color: #8b4513; margin-top: 20px;">Current Dasha Periods</h3>
            <table>
                <thead>
                    <tr>
                        <th>Level</th>
                        <th>Planet</th>
                        <th>Start Date</th>
                        <th>End Date</th>
                    </tr>
                </thead>
                <tbody>
"""
            # Mahadasha
            for planet, period in current_dasha.items():
                if isinstance(period, dict) and 'start' in period and 'end' in period:
                    html_content += f"""
                    <tr>
                        <td><strong>Mahadasha</strong></td>
                        <td class="planet-name">{planet}</td>
                        <td>{format_date(period.get('start', ''))}</td>
                        <td>{format_date(period.get('end', ''))}</td>
                    </tr>
"""
                    # Antardasha
                    antardashas = period.get('antardashas', {})
                    if antardashas:
                        for ant_planet, ant_period in antardashas.items():
                            if isinstance(ant_period, dict) and 'start' in ant_period:
                                html_content += f"""
                    <tr>
                        <td style="padding-left: 30px;">Antardasha</td>
                        <td>{ant_planet}</td>
                        <td>{format_date(ant_period.get('start', ''))}</td>
                        <td>{format_date(ant_period.get('end', ''))}</td>
                    </tr>
"""
                                # Pratyantardasha
                                pratyantardashas = ant_period.get('pratyantardashas', {})
                                if pratyantardashas:
                                    for prat_planet, prat_period in pratyantardashas.items():
                                        if isinstance(prat_period, dict) and 'start' in prat_period:
                                            html_content += f"""
                    <tr>
                        <td style="padding-left: 60px;">Pratyantardasha</td>
                        <td>{prat_planet}</td>
                        <td>{format_date(prat_period.get('start', ''))}</td>
                        <td>{format_date(prat_period.get('end', ''))}</td>
                    </tr>
"""
            
            html_content += """
                </tbody>
            </table>
"""
    
    html_content += """
        </div>
        
        <!-- Complete JSON View -->
        <div class="section">
            <h2 class="section-title">📄 Complete JSON Data</h2>
            <div class="json-viewer">
                <pre id="json-content"></pre>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>Report Generated:</strong> """ + datetime.now().strftime('%B %d, %Y at %I:%M %p') + """</p>
            <p>Generated by AstroBuddy - Complete Vedic Astrology Kundali Generator</p>
        </div>
    </div>
    
    <script>
        // Display formatted JSON
        const jsonData = """ + json.dumps(kundali_data, indent=2) + """;
        document.getElementById('json-content').textContent = JSON.stringify(jsonData, null, 2);
    </script>
</body>
</html>
"""
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def main():
    """Main function to convert JSON to HTML"""
    if len(sys.argv) < 2:
        print("\n" + "="*60)
        print("  JSON TO HTML CONVERTER - KUNDALI")
        print("="*60 + "\n")
        print("Usage: python json_to_html.py <json_file_path>")
        print("\nOr enter JSON file path interactively:")
        json_path = input("Enter JSON file path: ").strip().strip('"')
    else:
        json_path = sys.argv[1]
    
    if not os.path.exists(json_path):
        print(f"\n✗ Error: File not found: {json_path}")
        sys.exit(1)
    
    try:
        # Read JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            kundali_data = json.load(f)
        
        # Generate output HTML path
        base_name = os.path.splitext(os.path.basename(json_path))[0]
        output_dir = os.path.dirname(json_path) or "kundali_outputs"
        html_path = os.path.join(output_dir, f"{base_name}.html")
        
        print(f"\n{'='*60}")
        print("  Converting JSON to HTML...")
        print(f"{'='*60}")
        
        # Generate HTML
        output_path = generate_html(kundali_data, html_path)
        
        print(f"\n✓ Successfully converted to HTML!")
        print(f"  HTML file saved to: {output_path}")
        print(f"\n  Complete kundali report with all data is ready to view!\n")
        
    except json.JSONDecodeError as e:
        print(f"\n✗ Error: Invalid JSON file - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
