import streamlit as st
import random
import pyttsx3
import speech_recognition as sr
import smtplib
from email.message import EmailMessage
from datetime import datetime
import time
import json
import hashlib
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Startovate - AI Startup Generator",
    page_icon="🚀",
    layout="wide"
)

# --- USER AUTHENTICATION & DATA HANDLING ---

USER_DATA_FILE = "users.json"
SAVED_IDEAS_FILE = "saved_ideas.json"

def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_saved_ideas(username):
    try:
        with open(SAVED_IDEAS_FILE, 'r') as f:
            all_saved_ideas = json.load(f)
            return all_saved_ideas.get(username, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_saved_ideas(username, ideas):
    try:
        with open(SAVED_IDEAS_FILE, 'r') as f:
            all_saved_ideas = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        all_saved_ideas = {}
    
    all_saved_ideas[username] = ideas
    with open(SAVED_IDEAS_FILE, 'w') as f:
        json.dump(all_saved_ideas, f, indent=4)


# --- TTS and STT Functions ---
@st.cache_resource # Cache the engine initialization
def init_pyttsx3():
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Try to find an English female voice, otherwise use default
    female_voice = next((v for v in voices if 'en' in v.id and 'female' in v.name.lower()), None)
    if female_voice:
        engine.setProperty('voice', female_voice.id)
    else:
        st.warning("Could not find a suitable female voice. Using default.")
    engine.setProperty('rate', 170) # Adjust speaking rate
    return engine

def clean_text_for_tts(text):
    # Remove markdown for better narration
    cleaned_text = re.sub(r'[*_`]', '', text) 
    return cleaned_text

def speak(text):
    engine = init_pyttsx3()
    clean_text = clean_text_for_tts(text)
    engine.say(clean_text)
    engine.runAndWait()

def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Say something!")
        r.adjust_for_ambient_noise(source) # Adjust for ambient noise
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio)
        st.success(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        st.error("Could not understand audio. Please try again.")
        return ""
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")
        return ""

# ---------- FUNCTION TO EMAIL IDEA ----------
def send_idea_email(to_email, idea_data):
    try:
        msg = EmailMessage()
        msg['Subject'] = f"Your Startup Idea: {idea_data['name']}"
        msg['From'] = 'saniyakhandelwal10446@gmail.com' # Use your actual verified sender email
        msg['To'] = to_email

        content = f"""
        🚀 Startup Name: {idea_data['name']}
        📌 Tagline: {idea_data['tagline']}
        🧠 Idea: A {idea_data['tech']} for {idea_data['audience']} in {idea_data['industry']} to {idea_data['idea']}
        🎯 Goal: {idea_data['goal']}
        💸 Monetization: {' | '.join(idea_data['monetization'])}
        🌍 Region: {idea_data['region']}
        👥 Team Size: {idea_data['team']}
        📊 Feasibility Score: {idea_data['score']} / 100

        Thank you for using Startovate!
        """

        msg.set_content(content)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login('saniyakhandelwal10446@gmail.com', 'vtob imzt pojv fmmg') # Use your App Password here
            smtp.send_message(msg)
        st.success(f"📩 Email sent to {to_email}!")
    except Exception as e:
        st.error(f"Email failed: {e}. Please ensure your email and app password are correct, and less secure app access is enabled if applicable.")


# --- AUTHENTICATION PAGE ---
def authentication_page():
    """Displays the login/signup page and handles all authentication logic."""
    st.markdown("""
    <style>
    /* Gradient background for the authentication page */
    [data-testid="stAppViewContainer"] > .main {
        background: linear-gradient(to right, #00C9FF, #92FE9D); /* Blue to Green gradient */
        min-height: 100vh; /* Ensure it covers the full viewport height */
        display: flex;
        justify-content: center; /* Center horizontally */
        align-items: center; /* Center vertically */
        padding: 20px;
        background-size: cover; /* Ensure gradient covers the area */
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Styles for the login/signup form box */
    /* Target the main block containing tabs, ensuring it's the one that holds the form */
    div[data-testid="stVerticalBlock"] > div.css-1r6dn7c.e1fqkh3o5,
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] { /* More robust target for the form container */
        background-color: rgba(255, 255, 255, 0.9); /* White box for form with slight transparency */
        padding: 40px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        max-width: 500px;
        width: 100%;
        margin-top: 0 !important; /* Reset margin from Streamlit defaults */
        margin-bottom: 0 !important; /* Reset margin from Streamlit defaults */
    }

    /* Black font for all text/labels within the form */
    div[data-testid="stVerticalBlock"] label,
    div[data-testid="stVerticalBlock"] h1,
    div[data-testid="stVerticalBlock"] h3,
    div[data-testid="stVerticalBlock"] h4,
    div[data-testid="stVerticalBlock"] p,
    div[data-testid="stVerticalBlock"] .stTab {
        color: black !important;
    }
    
    /* White background for input fields, black text */
    .stTextInput>div>div>input {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc;
        border-radius: 5px;
        padding: 10px;
    }

    /* Style for buttons within the authentication page forms */
    div[data-testid="stVerticalBlock"] .stButton>button {
        background-color: #6C5CE7; /* A nice purple for auth buttons */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    div[data-testid="stVerticalBlock"] .stButton>button:hover {
        background-color: #8A2BE2; /* Darker purple on hover */
        transform: translateY(-2px);
    }

    /* Center text for titles within the auth form */
    div[data-testid="stVerticalBlock"] h1, div[data-testid="stVerticalBlock"] h3 {
        text-align: center;
    }

    /* Adjust padding for tabs content */
    .stTabs [data-testid="stTabContent"] {
        padding: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])

    with col_center:
        st.markdown("<h1 style='text-align: center;'>🚀 Startovate</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Your AI-Powered Startup Companion</h3>", unsafe_allow_html=True)
        st.write("")

        users = load_user_data()
        
        login_tab, signup_tab = st.tabs(["🔐 Login", "📝 Sign Up"])

        with login_tab:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("#### Welcome Back!")
                username_input = st.text_input("Username").lower()
                password_input = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted:
                    hashed_password = hash_password(password_input)
                    if username_input in users and users[username_input]['password'] == hashed_password:
                        st.session_state["logged_in"] = True
                        st.session_state["username"] = users[username_input]['name'] 
                        st.session_state["user_email"] = users[username_input]['email']
                        st.session_state["user_login_username"] = username_input
                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("😕 Incorrect username or password.")

        with signup_tab:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("#### Create a New Account")
                new_name = st.text_input("Your Name")
                new_username = st.text_input("Choose a Username").lower()
                new_email = st.text_input("Your Email") 
                new_password = st.text_input("Choose a Password", type="password")
                submitted = st.form_submit_button("Sign Up", use_container_width=True)

                if submitted:
                    if not all([new_name, new_username, new_email, new_password]):
                        st.warning("Please fill out all fields.")
                    elif new_username in users:
                        st.error(f"Username '{new_username}' is already taken. Please choose another.")
                    else:
                        users[new_username] = {
                            'name': new_name,
                            'email': new_email, 
                            'password': hash_password(new_password)
                        }
                        save_user_data(users)
                        st.success(f"✅ Account created for {new_name}! Please go to the Login tab to log in.")
    

# --- MAIN APPLICATION ---
def main_app():
    """The main application logic after a user has logged in."""
    
    # ---------- BACKGROUND GRADIENT + BLUR + SLIDE-IN ANIMATION FOR MAIN APP ----------
    st.markdown(f"""
    <style>
    @keyframes slideFadeIn {{
        0% {{ transform: translateY(20px); opacity: 0; }}
        100% {{ transform: translateY(0); opacity: 1; }}
    }}
    [data-testid="stAppViewContainer"] > .main {{
        background: linear-gradient(to right, #00C9FF, #92FE9D); /* Blue to Green gradient */
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        animation: slideFadeIn 1s ease-out;
        /* Apply blur to the gradient background */
        backdrop-filter: blur(10px); /* Increased blur level */
        -webkit-backdrop-filter: blur(10px); /* For Safari support */
        /* background-color: rgba(0, 0, 0, 0.3); Removed or set to transparent if you only want gradient */
    }}

    /* You might also want to adjust the main content area itself to be semi-transparent */
    /* to show the blur effect behind it, rather than just the background image itself */
    /* For instance, if you want the content blocks to be slightly translucent: */
    /*
    div.st-emotion-cache-1pxmztm.ea3g5fb0 {{ /* This targets the main content block, may vary */
        background-color: rgba(255, 255, 255, 0.1); /* Slightly transparent white */
        border-radius: 10px;
        padding: 20px;
    }}
    */

    [data-testid="stSidebar"] > div:first-child {{
        background-color: rgba(0,0,0,0.6);
        animation: slideFadeIn 1.5s ease-out;
    }}
    /* Specific styling for the Main App's buttons as per your request */
    /* Generate Ideas Button - Green */
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Generate Startup Idea")) {{
        background-color: #4CAF50 !important; /* Green */
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Generate Startup Idea")):hover {{
        background-color: #45a049 !important; /* Darker green on hover */
        transform: translateY(-2px);
    }}

    /* Voice and Pitch Deck Buttons - Blue */
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate Idea")),
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Record Suggestions")),
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate This Pitch Deck")) {{
        background-color: #008CBA !important; /* Blue */
        color: white !important;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate Idea")):hover,
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Record Suggestions")):hover,
    .stButton button:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate This Pitch Deck")):hover {{
        background-color: #005f7d !important; /* Darker blue on hover */
        transform: translateY(-2px);
    }}

    /* General button styling for other buttons (e.g., Save, Update, Download) if needed */
    .stButton button:not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Generate Startup Idea"))):not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate Idea"))):not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Record Suggestions"))):not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate This Pitch Deck"))) {{
        background-color: #6C5CE7; /* Default purple for others like Home, Logout, Save, Update, Download */
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }}
    .stButton button:not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Generate Startup Idea"))):not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate Idea"))):not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Record Suggestions"))):not(:has(div[data-testid="stMarkdownContainer"] > p:contains("Narrate This Pitch Deck"))):hover {{
        background-color: #8A2BE2; /* Darker purple on hover */
        transform: translateY(-2px);
    }}

    </style>
    """, unsafe_allow_html=True)

    # --- SIDEBAR ---
    with st.sidebar:
        st.title(f"👋 Welcome, {st.session_state.get('username', 'Guest')}")
        if "user_email" in st.session_state:
            st.write(f"📧 **Email:** {st.session_state['user_email']}")
        st.markdown("---")
        
        if st.button("🏠 Home Page", key="sidebar_home_button"): # Added unique key
            st.session_state["current_page"] = "Startup Generator"
            st.rerun()

        nav = st.radio("🧭 Navigation", ["Startup Generator", "Idea Pitch Deck", "Startup Gallery"], 
                       index=["Startup Generator", "Idea Pitch Deck", "Startup Gallery"].index(st.session_state.get("current_page", "Startup Generator")),
                       key="main_navigation_radio") # Added unique key
        st.markdown("---")
        if st.button("Logout", key="sidebar_logout_button"): # Added unique key
            st.session_state["logged_in"] = False
            del st.session_state["username"]
            del st.session_state["user_email"]
            del st.session_state["user_login_username"]
            if "last_generated_idea_data" in st.session_state:
                del st.session_state["last_generated_idea_data"]
            if "recorded_feedback" in st.session_state:
                del st.session_state["recorded_feedback"]
            st.rerun()

    # The rest of your app logic
    if nav == "Startup Generator":
        st.session_state["current_page"] = "Startup Generator"
        st.title("✨ Intelligent Startup Idea Generator")
        st.write("Unleash your entrepreneurial spirit! Let our AI generate innovative startup ideas for you.")

        col1, col2, col3 = st.columns(3)
        with col1:
            industry = st.selectbox("Industry", ["Healthcare", "Education", "Finance", "Entertainment", "AI/ML", "GreenTech", "Travel"], key="gen_industry")
        with col2:
            audience = st.selectbox("Target Audience", ["Students", "Professionals", "Seniors", "Startups", "Businesses", "Individuals"], key="gen_audience")
        with col3:
            tech = st.selectbox("Technology", ["AI Tool", "Mobile App", "Web App", "IoT", "Blockchain", "SaaS Platform", "VR/AR"], key="gen_tech")

        goal = st.selectbox("Vision Goal", ["Disrupt the market", "Solve social issues", "Go viral", "Generate revenue", "Improve efficiency", "Enhance user experience"], key="gen_goal")
        monetization = st.multiselect("Monetization", ["Subscription", "Ads", "Freemium", "Commission", "Direct Sales", "Licensing"], default=["Subscription"], key="gen_monetization")
        region = st.selectbox("Target Market", ["India", "Global", "US", "Europe", "Asia", "Africa"], key="gen_region")
        team_size = st.slider("Team Size", 1, 50, 5, key="gen_team_size")

        generate_button_clicked = st.button("🚀 Generate Startup Idea", key="generate_idea_button")

        if generate_button_clicked:
            with st.spinner("🚧 Generating brilliant idea..."):
                time.sleep(2)

                names = ["Nexa", "Zeno", "Looma", "Orbit", "Glowr", "Synapse", "Apex", "Nova", "Vortex"]
                suffixes = ["ly", "X", "ify", "Hub", "Flow", "Go", "AI"]
                startup_name = random.choice(names) + random.choice(suffixes)
                tagline_options = [
                    "Revolutionizing the future.", "Power through simplicity.",
                    "Smart ideas, real impact.", "Innovation meets action.",
                    "Your ultimate solution.", "Simplifying complex problems."
                ]
                startup_tagline = random.choice(tagline_options)
                idea_map = {
                    "Healthcare": "analyze health metrics and provide instant AI feedback for personalized wellness plans.",
                    "Education": "deliver smart, adaptive lessons and track learning patterns for optimized student growth.",
                    "Finance": "automate savings, budgets, and investments with intelligent predictive analytics.",
                    "Entertainment": "create customized immersive experiences through interactive storytelling and AI-driven content.",
                    "AI/ML": "build intelligent solutions for automating daily tasks and enhancing productivity across industries.",
                    "GreenTech": "suggest eco-friendly habits and monitor environmental impact using real-time data.",
                    "Travel": "plan smart, personalized trips that adjust on-the-go based on preferences and real-time conditions."
                }
                score = random.randint(70, 95)

                generated_idea_data = {
                    "name": startup_name,
                    "tagline": startup_tagline,
                    "industry": industry,
                    "audience": audience,
                    "tech": tech,
                    "goal": goal,
                    "monetization": monetization,
                    "region": region,
                    "team": team_size,
                    "score": score,
                    "idea": idea_map.get(industry, "solve a pressing problem in the chosen domain.")
                }
                st.session_state["last_generated_idea_data"] = generated_idea_data
                st.success("Idea generated!")

                if "user_email" in st.session_state and st.session_state["user_email"]:
                    send_idea_email(st.session_state["user_email"], generated_idea_data)

        if "last_generated_idea_data" in st.session_state and st.session_state["last_generated_idea_data"]:
            d = st.session_state["last_generated_idea_data"]
            st.markdown("---")
            st.subheader("Your Generated Startup Idea:")
            st.header(f"🚀 {d['name']}")
            st.caption(d['tagline'])
            st.markdown(f"**Core Idea:** A {d['tech']} for {d['audience']} in the {d['industry']} industry to {d['idea']}")
            st.markdown(f"**Vision:** {d['goal']} | **Market:** {d['region']} | **Team Size:** {d['team']}")
            st.markdown(f"**Monetization:** {' | '.join(d['monetization'])}")
            st.markdown(f"**Feasibility Score:** {d['score']} / 100")

            st.markdown("---")
            st.subheader("🗣️ Voice Features")
            col_tts, col_stt = st.columns(2)
            with col_tts:
                if st.button("📢 Narrate Idea (Text-to-Speech)", key="narrate_idea_button"): # Ensure unique key
                    with st.spinner("Narrating..."):
                        full_idea_text = f"Startup name is {d['name']}. Tagline: {d['tagline']}. Core idea: A {d['tech']} for {d['audience']} in the {d['industry']} industry to {d['idea']}. Vision: {d['goal']}. Target Market: {d['region']}. Expected team size: {d['team']} members. Feasibility score: {d['score']} out of 100."
                        speak(full_idea_text)
                    st.success("Narration complete!")
            
            with col_stt:
                if st.button("🎤 Record Suggestions", key="record_suggestions_button"): # Ensure unique key
                    st.session_state["recorded_feedback"] = recognize_speech()
                    if st.session_state["recorded_feedback"]:
                        st.write(f"Thank you for your suggestion: {st.session_state['recorded_feedback']}")
                        # The suggestion is already processed/displayed by recognize_speech,
                        # so no further action needed here unless you want to update the idea.
                        # For now, simply displaying it is sufficient.
            
            if "recorded_feedback" in st.session_state and st.session_state["recorded_feedback"]:
                st.info(f"Last recorded suggestion: {st.session_state['recorded_feedback']}")
                # If you want the suggestion to *persist* on rerun, you'd store it.
                # If it's a one-time display, the current setup is fine.

            st.markdown("---")

    elif nav == "Idea Pitch Deck":
        st.session_state["current_page"] = "Idea Pitch Deck"
        st.title("📊 Startup Pitch Deck Builder")
        if "last_generated_idea_data" not in st.session_state:
            st.warning("Please generate a startup idea first on the 'Startup Generator' page.")
        else:
            d = st.session_state["last_generated_idea_data"]
            st.header(f"Pitch Deck for: {d['name']}")
            st.caption(d['tagline'])

            st.subheader("1. Problem")
            st.write(f"In the **{d['industry']}** sector, **{d['audience']}** often face challenges related to **{d['idea'].replace('solve a pressing problem in the chosen domain.', 'existing inefficiencies or lack of innovative solutions.')}**.")
            
            st.subheader("2. Solution")
            st.write(f"Our solution is a **{d['tech']}** designed to **{d['idea']}**, providing a seamless and effective approach.")
            
            st.subheader("3. Market & Audience")
            st.write(f"We are targeting the **{d['region']}** market, specifically focusing on **{d['audience']}** who are looking for **{d['goal']}**.")
            
            st.subheader("4. Business Model")
            st.write(f"Our primary monetization strategies include **{', '.join(d['monetization'])}**, ensuring sustainable growth.")
            
            st.subheader("5. Team & Feasibility")
            st.write(f"With a dedicated team of **{d['team']}** members, we are well-equipped to achieve our vision. Our idea has a strong feasibility score of **{d['score']} / 100**.")
            st.markdown("---")
            # Narration button for Pitch Deck
            if st.button("📢 Narrate This Pitch Deck", key="narrate_pitch_deck_button"): # Ensure unique key
                with st.spinner("Narrating pitch..."):
                    pitch_text = f"Introducing {d['name']}, {d['tagline']}. Problem: In the {d['industry']} sector, {d['audience']} often face challenges related to {d['idea'].replace('solve a pressing problem in the chosen domain.', 'existing inefficiencies or lack of innovative solutions.')}. Solution: Our solution is a {d['tech']} designed to {d['idea']}. Market and Audience: We are targeting the {d['region']} market, specifically focusing on {d['audience']} who are looking for {d['goal']}. Business Model: Our primary monetization strategies include {', '.join(d['monetization'])}. Team and Feasibility: With a dedicated team of {d['team']} members, and a strong feasibility score of {d['score']} out of 100, we are poised for success."
                    speak(pitch_text)
                st.success("Pitch narration complete!")


    elif nav == "Startup Gallery":
        st.session_state["current_page"] = "Startup Gallery"
        st.title("🖼️ Startup Gallery")

        if "user_login_username" in st.session_state:
            current_user_ideas = load_saved_ideas(st.session_state["user_login_username"])
            if "last_generated_idea_data" in st.session_state:
                # Check if the last generated idea is already in the saved list to avoid duplicates on refresh
                # This needs a more robust check than just `in` for dictionaries. Let's compare keys.
                is_idea_saved = any(
                    all(item in saved_idea.items() for item in st.session_state["last_generated_idea_data"].items())
                    for saved_idea in current_user_ideas
                )

                if not is_idea_saved:
                    if st.button("💾 Save Current Idea to Gallery", key="save_idea_button_gallery"):
                        current_user_ideas.append(st.session_state["last_generated_idea_data"])
                        save_saved_ideas(st.session_state["user_login_username"], current_user_ideas)
                        st.success("Idea saved to gallery!")
                        st.rerun()
                else:
                    st.info("Current idea is already saved in your gallery.")
            else:
                st.info("Generate an idea first to save it to your gallery.")


            if current_user_ideas:
                st.markdown("## 📚 Your Saved Ideas")
                for idx, idea in enumerate(current_user_ideas):
                    with st.expander(f"📌 {idea['name']} ({idea['tagline']})"):
                        st.image("https://source.unsplash.com/random/400x200?startup," + idea['industry'], caption=f"Visual for {idea['name']}", use_column_width=True)
                        st.write(f"**Industry:** {idea['industry']}")
                        st.write(f"**Audience:** {idea['audience']}")
                        st.write(f"**Technology:** {idea['tech']}")
                        st.write(f"**Core Idea:** {idea['idea']}")
                        st.write(f"**Vision Goal:** {idea['goal']}")
                        st.write(f"**Target Market:** {idea['region']}")
                        st.write(f"**Monetization:** {' | '.join(idea['monetization'])}")
                        st.write(f"**Team Size:** {idea['team']}")
                        st.write(f"**Feasibility Score:** {idea['score']} / 100")

                        new_tagline = st.text_input(f"📝 Edit Tagline for {idea['name']}", value=idea['tagline'], key=f"gallery_tag_{idx}")
                        if st.button(f"💡 Update Tagline for {idea['name']}", key=f"gallery_edit_{idx}"):
                            current_user_ideas[idx]['tagline'] = new_tagline
                            save_saved_ideas(st.session_state["user_login_username"], current_user_ideas)
                            st.success("Tagline updated!")
                            st.rerun()

                        buffer = io.BytesIO()
                        pdf = canvas.Canvas(buffer, pagesize=letter)
                        y_pos = 750
                        line_height = 18
                        pdf.setFont("Helvetica-Bold", 14)
                        pdf.drawString(50, y_pos, f"Pitch Deck - {idea['name']}")
                        y_pos -= line_height * 2
                        pdf.setFont("Helvetica", 10)
                        pdf.drawString(50, y_pos, f"Tagline: {idea['tagline']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Industry: {idea['industry']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Audience: {idea['audience']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Technology: {idea['tech']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Core Idea: {idea['idea']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Vision Goal: {idea['goal']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Target Market: {idea['region']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Monetization: {', '.join(idea['monetization'])}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Team Size: {idea['team']}")
                        y_pos -= line_height
                        pdf.drawString(50, y_pos, f"Feasibility Score: {idea['score']} / 100")
                        pdf.save()
                        buffer.seek(0)

                        st.download_button(
                            label="📥 Download Pitch as PDF",
                            data=buffer,
                            file_name=f"{idea['name']}_pitch.pdf",
                            mime="application/pdf",
                            key=f"download_pdf_{idx}"
                        )
            else:
                st.info("No ideas saved yet for this user. Generate one on the 'Startup Generator' page and save it!")
        else:
            st.warning("Please log in to view and save ideas in the gallery.")


# --- SCRIPT ENTRY POINT ---
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Startup Generator"

if not st.session_state["logged_in"]:
    authentication_page()
else:
    main_app()