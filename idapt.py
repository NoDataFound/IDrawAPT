import os
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import requests
from io import BytesIO
from PIL import Image
from colorthief import ColorThief
import openai
import re
from dotenv import load_dotenv
import tempfile
import base64
import random
import glob
import json
from collections import Counter
import base64
import time
import io



# --- CONFIGURATION ---
MITRE_JSON_URL = "https://github.com/mitre-attack/attack-stix-data/raw/refs/heads/master/enterprise-attack/enterprise-attack.json"
MITRE_LOCAL_PATH = "enterprise-attack.json"
MITRE_FRESHNESS_DAYS = 7

st.set_page_config(
    page_title="Professional APT Hacker Art",
    page_icon="favicon.png",  
    layout="wide",
    initial_sidebar_state="expanded",
)

# Create styleguide directory if it doesn't exist
if not os.path.exists("styleguide"):
    os.makedirs("styleguide")

# Custom CSS for visual flair
st.markdown(
    """
    <style>
    .main { background-color: #1e1e2e; color: #ffffff; }
    .sidebar .sidebar-content { background-color: #2a2a3a; }
    .stExpander { background-color: #2a2a3a; border-radius: 10px; }
    .stCheckbox { margin-bottom: 10px; }
    h1, h2, h3 { color: #ff007a; font-family: 'Courier New', monospace; }
    .stMarkdown { font-family: 'Arial', sans-serif; }
    .glow-text {
        text-shadow: 0 0 10px #ff007a, 0 0 20px #ff007a;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown("<h3 class='glow-text'>Pro Level APT Hacker ART</h3>", unsafe_allow_html=True)

# Side-by-side checkboxes
col1, col2 = st.sidebar.columns(2)
with col1:
    show_instructions = st.checkbox("`Show Instructions`", value=False)
with col2:
    show_styles = st.checkbox("`Show Style Guide`", value=False)

# Instructions section
if show_instructions:
    with st.expander("How to Use the APT Hacker Art Generator", expanded=True):
        st.info(
            "**Step 1: Choose Your MITRE ATT&CK Region & Group**\n\n"
            "Select a region to filter threat actor groups, then pick one or more APT groups to focus on. "
            "Want to channel APT28’s Russian bear energy? This is your spot."
        )
        st.info(
            "**Step 2: Upload a Logo (Optional)**\n\n"
            "Drop a logo to extract its dominant colors. These will spice up your generated image, "
            "making it match your brand or the threat actor’s vibe. No logo? No problem—go rogue!"
        )
        st.info(
            "**Step 3: Pick Your Style**\n\n"
            "Choose a visual style from our wild lineup (check the Style Guide below). "
            "From photorealistic to Howard the Duck chaos, we’ve got it all. Or describe your own!"
        )
        st.info(
            "**Step 4: Add Additional Context**\n\n"
            "Throw in extra details—technical specs, hacker memes, or creative vibes. "
            "Want a cyber ninja with a floppy disk shuriken? Tell us!"
        )
        st.info(
            "**Step 5: API Key**\n\n"
            "Use the free OpenAI API (limited, might ghost you) or enter your own for reliable, "
            "high-octane generation. Pro tip: bring your own key for max control."
        )
        st.info(
            "**Step 6: Draw & Download**\n\n"
            "Smash the 'Draw APT' button to generate your masterpiece. Download the transparent PNG "
            "and flex your gallery in the sidebar. Hack the planet!"
        )

# Style guide data
STYLE_PROMPT_MAP = {
    "Photorealistic": (
        "A jaw-droppingly realistic, photorealistic logo that could fool your grandma into thinking it’s a National Geographic cover. If it’s an animal, it’s so lifelike you’d swear you could pet it—every whisker, feather, or scale is meticulously detailed. No cartoons, no illustrations, no stylized nonsense. This logo belongs in a top-secret intelligence report or a museum exhibit. It’s so credible and plausible, you’d bet your life savings it was snapped by a high-end DSLR. Perfect for when you need to impress suits or convince someone you’ve seen Bigfoot."
    ),
    "Corporate": (
        "A photorealistic, ultra-sleek, modern corporate logo that screams 'we have a corner office and a coffee machine that costs more than your car.' No cartoons, no goofy vibes—just pure, polished professionalism. Think glass skyscrapers, minimalist boardrooms, and PowerPoint slides that make people cry. It’s the kind of logo you’d see on a Fortune 500 company’s letterhead or a shady megacorp in a cyberpunk flick. Credible, sharp, and so professional it might just fire you for not wearing a tie."
    ),
    "Cartoon": (
        "A wildly colorful, cartoon-style logo with a hand-drawn, Sunday-morning-cereal-box energy. Features are exaggerated to the max—eyes the size of hubcaps, grins that defy physics, and colors so bright they’d make a rainbow jealous. Playful and chaotic, it’s the opposite of realistic, like something doodled by a sugar-high kid with a crayon obsession. Perfect for when you want a logo that screams 'fun' and probably has its own Saturday morning theme song."
    ),
    "8bit": (
        "A retro 8-bit pixel art logo that drags you back to the days of blowing into NES cartridges and praying they’d work. Blocky, low-res, and gloriously simplistic, it’s like a sprite ripped straight from an arcade cabinet. Colors are limited but punchy, evoking the charm of early computer games like Pac-Man or Space Invaders. Bonus points: it might come with a chiptune jingle stuck in your head for weeks. Warning: may cause nostalgia-induced tears."
    ),
    "Pixel Sprite": (
        "A pixel art sprite logo straight out of the 16-bit golden age of gaming. Think Sega Genesis or SNES vibes—bright, bold colors, simple yet expressive shapes, and a retro video game aesthetic that screams 'insert coin.' Perfect for a character or icon that could star in its own platformer. If it’s a hacker, they’re probably wielding a pixelated floppy disk like a shuriken. Pro tip: don’t let it near a Game Genie, or it’ll start glitching into next week."
    ),
    "90sNFO": (
        "A text-based ASCII/ANSI art logo inspired by the gritty 90s warez scene, when hackers were trading cracked games on floppy disks and BBS forums. Monospaced characters, stark contrast, and intricate designs built from nothing but keyboard symbols. It’s like a digital cave painting for the dial-up era—raw, nerdy, and dripping with underground cred. If this logo could talk, it’d ask you for a 28.8k modem and a Mountain Dew. Bonus: might include a hidden .nfo file with a shoutout to 'xX_Hackz0r_Xx.'"
    ),
    "Hacker Art": (
        "A dark, cyberpunk glitch-art logo that looks like it was coded in a neon-lit basement at 3 a.m. Think hacker scene aesthetics: glowing green terminal screens, digital distortion, and enough neon lights to make a synthwave album cover jealous. It’s gritty, chaotic, and screams 'I just breached your firewall and left a meme on your desktop.' Perfect for a logo that needs to intimidate script kiddies and impress the 1337 hax0rs. Warning: may cause spontaneous urges to wear a hoodie and type furiously."
    ),
    "Minimal": (
        "A minimalist logo so clean and simple it could star in a Scandinavian furniture catalog. Crisp lines, a max of three colors (probably black, white, and a smug accent shade), and enough whitespace to make a zen garden jealous. It’s the kind of logo that says 'less is more' while secretly judging your cluttered desk. Ultra-simplified but still iconic, it’s perfect for when you want to look effortlessly cool without trying too hard. Bonus: might come with a free yoga session."
    ),
    "Vector": (
        "A vector illustration logo that’s crisp, clean, and infinitely scalable—like the lovechild of an infographic and a geometry textbook. Built from smooth, geometric shapes, it’s modern, precise, and looks like it was designed in a lab by a team of perfectionists. Ideal for tech startups, data visualizations, or anything that needs to scream 'I’m futuristic and I know what SVG stands for.' Pro tip: don’t stare too long, or you’ll start seeing hexagons in your sleep."
    ),
    "80s Movies": (
        "A vivid, over-the-top logo inspired by 1980s movie posters—think Tron’s glowing circuits, Blade Runner’s neon-soaked cityscapes, or The Running Man’s cheesy action-hero vibes. Neon lighting, bold fonts, and dramatic compositions that scream 'this summer, one logo will change everything.' It’s cinematic, retro, and so 80s it might come with a mullet and a keytar solo. Perfect for when you want a logo that feels like it’s about to save the world—or at least the local arcade."
    ),
    "Max Headroom": (
        "A Max Headroom-inspired logo that’s pure 1980s digital fever dream. Cyberpunk glitch art, VHS scanlines, and high-contrast colors that look like they were beamed from a dystopian TV studio. Expect distorted faces, stuttering animations, and a vibe that screams 'the future is now, but it’s also super glitchy.' It’s like a hacker’s brainchild after too many energy drinks and a Blade Runner marathon. Bonus: might include a snarky AI host who keeps interrupting with bad puns."
    ),
    "HOWARD THE DUCK": (
        "A logo where EVERYTHING is Howard the Duck, and we mean EVERYTHING. Hackers? Ducks in trench coats. Code? Ducks typing with their webbed feet. An APT? Just Howard, angrier than usual, wielding a keyboard like a cosmic baseball bat. This surreal, absurd logo is drenched in Howard’s cigar-chomping, wise-quacking energy. Expect cosmic cubes, hacker conference badges, and maybe a duck-sized leather jacket. It’s so bizarre it might just save the multiverse—or at least make everyone laugh at DEF CON."
    ),
    "Darkwing Duck": (
        "A logo where every pixel channels Darkwing Duck, the terror that flaps in the night. Hackers? They’re Darkwing in his signature cape and fedora. Code? Written by a mallard with a flair for dramatics. APTs? Just a purple-masked duck perched on a binary thunderstorm. This heroic, cartoonish logo radiates 1990s Duckburg chaos, with a touch of vigilante swagger. Bonus points for the Ratcatcher motorcycle, Negaduck sneering in the shadows, or gadgets so over-the-top they’d make Q jealous. When cybercrime strikes, let’s get dangerous!"
    ),
    "Gremlin Themed": (
        "A mischievous, chaotic logo inspired by the Gremlins films. Picture green, scaly creatures with toothy grins, tearing through 1980s movie monster mayhem. Cartoonish but with a wicked edge, it’s all about attitude—think gremlins spiking your punch at a hacker con or hotwiring your server rack. Neon lights, torn wires, and a vibe that says 'don’t feed us after midnight.' Perfect for a logo that’s equal parts cute and catastrophic. Warning: keep it away from water."
    ),
    "SecKC": (
        "A logo bursting with Kansas City hacker pride, shaped like a glorious hexagon to honor the iconic SecKC badge. It’s DIY to the core—think black hoodies, makerspace soldering irons, payphones repurposed as WiFi hotspots, and powergloves hacked to run Doom. Every pixel screams 'KC weirdness,' from barbecue-stained keyboards to a skyline of neon-lit silos. It’s the kind of logo that high-fives you at a hacker meetup and then challenges you to a lockpicking duel. Pure Midwestern cyber-soul."
    ),
    "Shinobi": (
        "A Shinobi-style logo for an elite AI hacking and pentesting crew. At its heart: a futuristic blue cyber ninja with angular, glowing eyes, a masked face, and gear so high-tech it probably hacks your dreams. Digital circuit lines snake through the design, paired with shield or blade motifs and vibrant neon gradients. It’s bold, professional, and just intimidating enough to make script kiddies weep. Dark blue, purple, and black dominate, with a fully transparent background. This logo doesn’t just break into networks—it does it with style."
    ),
    "STRIKE": (
        "A logo that’s all sharp angles and aggressive swagger, like a lovechild of 1980s laser tag and synthwave album art. Built from shadowed geometry and glowing gradients, it features a stylized bat with a hidden cat face, pulsing with deep pink-to-red neon. Set against a dark, moody background, it channels black-ops vibes, 80s action flicks, and clandestine hacker culture. This is the logo for a digital strike force—fast, elite, and ready to take down cyber threats with a boombox blasting Vangelis. Pure underground attitude."
    ),
    "Matrix": (
        "A logo ripped straight from a 1999 hacker’s fever dream in The Matrix. Cascading green digital rain, infinite wireframe grids, glowing pill bottles (red or blue, you choose), and trench-coated figures who probably know kung fu. It’s anonymous, mysterious, and loaded with hidden meaning—like a secret handshake for the underground hacker cell. Glitchy, angular, and drenched in matrix-green, it feels like it’s one keystroke away from rewriting reality. Bonus: might include a white rabbit or a phone booth that’s suspiciously out of service."
    ),
    "DOOM": (
        "A brutal, metallic logo inspired by DOOM (1993), where everything is designed to rip and tear. Think pixelated chainsaws, double-barreled shotguns, and BFGs glowing with hellfire. Big, blocky text screams heavy metal, with red and orange gradients that look like they were forged in a demonic furnace. Expect pentagrams, cybernetic demon skulls, or a Cacodemon with a WiFi antenna. The background is dark, smoky, and pulsing with infernal energy. If this logo was a person, it’d be headbanging to Slayer while fragging imps."
    ),
    "Larry and the Lounge Lizards": (
        "A logo dripping with 1980s Vegas sleaze, inspired by Leisure Suit Larry and the Lounge Lizards. Think tacky polyester tuxedos, martinis with questionable olives, and gaudy fonts that scream 'casino carpet.' Neon lights, checkered dance floors, and disco balls set the scene, with palm trees and velvet ropes for extra kitsch. Hackers? They’re Larry, rocking a pencil mustache and striking out at the bar. It’s hilarious, awkward, and so 1987 it might try to sell you a timeshare. Perfect for a logo that’s one bad pickup line away from glory."
    ),
    "Whatever": (
        "A logo that’s completely unhinged and unpredictable, like the AI was given a triple espresso and a Ouija board. It could be a goat in a three-piece suit, a firewall rocking a mullet, or a cyberpunk sloth cruising on a Segway. No rules, no limits—just pure, chaotic creativity that’s guaranteed to make you snort-laugh. This is the logo equivalent of a fever dream after binge-watching X-Files and eating expired yogurt. Buckle up, because it’s gonna be weird and glorious."
    ),
    "Choose Your Own Adventure": (
        "A logo crafted entirely from the user’s wildest imagination. Whether it’s cyberpunk pirates wielding USB cutlasses, a jazz band of hacker sloths, or a boardroom of sentient firewalls debating patch notes, this logo is 100% driven by the user’s context, memes, or in-jokes. Every element—colors, styles, references—reflects the user’s input, no matter how absurd or specific. Want a logo of your dog as a hacker? Done. A sentient burrito running a pentest? On it. No watermarks, transparent background, and pure, unfiltered creativity."
    ),
    "Vaporwave": (
        "A logo drenched in vaporwave aesthetics, like a nostalgic fever dream of 1980s mall culture. Think pastel pinks, teals, and purples, with retro-futuristic palm trees, VHS glitches, and a lonely bust of Socrates glowing under neon lights. The vibe is chill but eerie, like you’re hacking a server inside a dead shopping mall at 2 a.m. Text is bold, often in Japanese katakana for no reason. Bonus: might include a dolphin or a can of New Coke floating in a wireframe void."
    ),
    "Pirate Hacker": (
        "A logo that fuses swashbuckling pirate energy with hacker swagger. Picture a cyber-pirate with a glowing eyepatch, a parrot that squawks in binary, and a cutlass made of circuit boards. The design is gritty yet adventurous, with stormy digital seas, treasure chests full of crypto, and Jolly Roger flags with a WiFi symbol. It’s the kind of logo that says 'arr, matey, I just phished yer mainframe.' Perfect for when you want to sail the high seas of cyberspace with a bottle of virtual rum."
    ),
    "Cat Meme": (
        "A logo built entirely around the chaotic energy of internet cat memes. Think grumpy cats typing code, keyboard cats shredding on a synthwave soundtrack, or Nyan Cat leaving a rainbow trail of binary. It’s colorful, absurd, and packed with feline attitude—every hacker is a cat, every server is a litter box, and every APT is just a very cranky tabby. Bonus: might include a laser pointer that causes the entire logo to go feral. Meow your way to cybersecurity glory!"
    ),
    "Retro Sci-Fi Paperback": (
        "A logo inspired by the garish covers of 1970s sci-fi paperbacks. Bold, clashing colors, wonky spaceships, and aliens with way too many eyes. The text is chunky and slightly tilted, like it’s trying to escape the cover. Expect ray guns, starfields, and a vibe that screams 'this book costs 95 cents at a used bookstore.' If there’s a hacker, they’re wearing a silver jumpsuit and fighting a tentacled AI. Perfect for a logo that feels like it was illustrated by a caffeine-addicted artist in a basement."
    ),
}
style_options = [
    ("8bit", "8bit"),
    ("Hacker Art", "Hacker Art"),
    ("90sNFO", "90sNFO"),
    ("Pixel Sprite", "Pixel Sprite"),
    ("Photorealistic", "Photorealistic"),
    ("Corporate", "Corporate"),
    ("Cartoon", "Cartoon"),
    ("Minimal", "Minimal"),
    ("Vector", "Vector"),
    ("80s Movies", "80s Movies"),
    ("Max Headroom", "Max Headroom"),
    ("HOWARD THE DUCK", "HOWARD THE DUCK"),
    ("Gremlin Themed", "Gremlin Themed"),
    ("SecKC", "SecKC"),
    ("Shinobi", "Shinobi"),
    ("STRIKE", "STRIKE"),
    ("Darkwing Duck", "Darkwing Duck"),
    ("Matrix", "Matrix"),
    ("DOOM", "DOOM"),
    ("Larry and the Lounge Lizards", "Larry and the Lounge Lizards"),
    ("Whatever", "Whatever"),
    ("Choose Your Own Adventure", "Choose Your Own Adventure"),
]
# Style guide section
if show_styles:
    st.markdown("<h2 class='glow-text'>Style Guide: Visual Styles for Your APT Art</h2>", unsafe_allow_html=True)
    st.caption("Explore all visual styles for your APT Hacker Art, from photorealistic to pure chaos. Images are loaded from the `styleguide` directory (e.g., `Photorealistic.png`, `Hacker_Art.png`).")
    
    # Simulate loading for dramatic effect
    with st.spinner("Loading style guide..."):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        # Initialize session state for toggling descriptions
    if "style_desc_toggle" not in st.session_state:
        st.session_state.style_desc_toggle = {key: False for key in STYLE_PROMPT_MAP.keys()}
    # Grid layout for styles (3 columns by default)
    NUM_COLS = 7
    style_keys = list(STYLE_PROMPT_MAP.keys())
    num_rows = (len(style_keys) + NUM_COLS - 1) // NUM_COLS  # Ceiling division for rows
    
    for row in range(num_rows):
        cols = st.columns(NUM_COLS)
        for col_idx in range(NUM_COLS):
            style_idx = row * NUM_COLS + col_idx
            if style_idx >= len(style_keys):
                break  # No more styles to display
            style_key = style_keys[style_idx]
            style_desc = STYLE_PROMPT_MAP[style_key]
            
            with cols[col_idx]:
                st.markdown(f"<div class='style-card'>", unsafe_allow_html=True)
                st.markdown(f"**{style_key}**")
                
                # Load and validate image
                image_filename = style_key.replace(" ", "_") + ".png"
                image_path = os.path.join("styleguide", image_filename)
                try:
                    if os.path.exists(image_path) and os.path.getsize(image_path) > 0:
                        with open(image_path, "rb") as f:
                            img_bytes = io.BytesIO(f.read())
                        img = Image.open(img_bytes)  # Validate image
                        img.verify()  # Ensure it’s a valid image
                        img = Image.open(img_bytes)  # Reopen after verify
                        st.image(img, use_container_width=True)
                    else:
                        placeholder_path = os.path.join("styleguide", "placeholder.png")
                        if os.path.exists(placeholder_path) and os.path.getsize(placeholder_path) > 0:
                            with open(placeholder_path, "rb") as f:
                                img_bytes = io.BytesIO(f.read())
                            img = Image.open(img_bytes)
                            img.verify()
                            img = Image.open(img_bytes)
                            st.image(img, caption=f"No {style_key} Image Found", use_container_width=True)
                        else:
                            st.warning(f"No {style_key} image found and no placeholder available.")
                except Exception as e:
                    placeholder_path = os.path.join("styleguide", "placeholder.png")
                    if os.path.exists(placeholder_path) and os.path.getsize(placeholder_path) > 0:
                        with open(placeholder_path, "rb") as f:
                            img_bytes = io.BytesIO(f.read())
                        img = Image.open(img_bytes)
                        img.verify()
                        img = Image.open(img_bytes)
                        st.image(img, caption=f"Invalid {style_key} Image ({e})", use_container_width=True)
                    else:
                        st.warning(f"Invalid {style_key} image ({e}) and no placeholder available.")

                TRUNCATE_LENGTH = 100
                truncated_desc = style_desc[:TRUNCATE_LENGTH] + "..." if len(style_desc) > TRUNCATE_LENGTH else style_desc
                if st.session_state.style_desc_toggle[style_key]:
                    st.caption(style_desc)
                    if st.button("Show Less", key=f"less_{style_key}"):
                        st.session_state.style_desc_toggle[style_key] = False
                        st.rerun()
                else:
                    st.caption(truncated_desc)
                    if len(style_desc) > TRUNCATE_LENGTH:
                        if st.checkbox("Show More", key=f"more_{style_key}"):
                            st.session_state.style_desc_toggle[style_key] = True
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)            
 

load_dotenv()
DEFAULT_API_KEY = os.getenv("OPENAI_API_KEY", "")


def download_mitre_json():
    resp = requests.get(MITRE_JSON_URL, timeout=60)
    resp.raise_for_status()
    with open(MITRE_LOCAL_PATH, "w") as f:
        f.write(resp.text)
    return True


def last_updated():
    if os.path.exists(MITRE_LOCAL_PATH):
        return datetime.fromtimestamp(os.path.getmtime(MITRE_LOCAL_PATH))
    return None


def is_stale():
    ts = last_updated()
    if not ts:
        return True
    return datetime.now() - ts > timedelta(days=MITRE_FRESHNESS_DAYS)


def extract_region(description):
    region_keywords = [
        ("China", ["china", "prc", "chinese", "people's republic"]),
        ("Russia", ["russia", "russian", "moscow"]),
        ("Iran", ["iran", "iranian", "tehran"]),
        ("North Korea", ["north korea", "dprk", "korea", "north korean", "pyongyang"]),
        ("Vietnam", ["vietnam", "vietnamese"]),
        ("Pakistan", ["pakistan", "pakistani"]),
        ("India", ["india", "indian"]),
        ("United States", ["united states", "usa", "american"]),
        ("UK", ["united kingdom", "britain", "uk", "british"]),
        ("Israel", ["israel", "israeli"]),
        ("Turkey", ["turkey", "turkish"]),
        ("Other", ["global", "multiple", "various"]),
    ]
    description_lower = (description or "").lower()
    for region, keywords in region_keywords:
        if any(k in description_lower for k in keywords):
            return region
    return "Unknown"


def parse_mitre_json(path=MITRE_LOCAL_PATH):
    if not os.path.exists(path):
        import streamlit as st

        st.error(
            "MITRE ATT&CK group data not found. Please use the sidebar to download the latest data."
        )
        st.stop()
    with open(path, "r") as f:
        obj = json.load(f)
    data = []
    for entry in obj["objects"]:
        if entry.get("type") != "intrusion-set":
            continue
        desc = entry.get("description", "")
        region = extract_region(desc)
        data.append(
            {
                "Region": region,
                "Name": entry.get("name"),
                "Aliases": ", ".join(entry.get("aliases", [])),
                "Description": desc,
                "id": entry.get("external_references", [{}])[0].get("external_id", ""),
            }
        )
    df = pd.DataFrame(data)
    return df


def get_group_data():
    try:
        from mitreattack.attackdata import MitreAttackData

        attack = MitreAttackData()
        group_list = []
        for group in attack.groups:
            desc = group.get("description", "")
            region = extract_region(desc)
            group_list.append(
                {
                    "Region": region,
                    "Name": group["name"],
                    "Aliases": ", ".join(group.get("aliases", [])),
                    "Description": desc,
                    "id": group["id"],
                }
            )
        return pd.DataFrame(group_list)
    except Exception:
        return parse_mitre_json()


def get_palette_from_logo(uploaded_logo):
    if uploaded_logo is None:
        return []
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
        tmp.write(uploaded_logo.read())
        tmp.flush()
        ct = ColorThief(tmp.name)
        palette = ct.get_palette(color_count=5)
    return [f"rgb{color}" for color in palette]


def generate_image_with_openai(prompt, api_key, model="dall-e-3"):
    if model == "dall-e-3":
        headers = {"Authorization": f"Bearer {api_key}"}
        json_payload = {
            "model": "dall-e-3",
            "prompt": prompt,
            "n": 1,
            "size": "1024x1024",
            "response_format": "b64_json",
        }
        endpoint = "https://api.openai.com/v1/images/generations"
        try:
            r = requests.post(endpoint, headers=headers, json=json_payload, timeout=60)
            r.raise_for_status()
            image_b64 = r.json()["data"][0]["b64_json"]
            img_bytes = BytesIO(base64.b64decode(image_b64))
            return img_bytes
        except Exception as e:
            st.error(f"DALL-E image generation failed: {e}")
            return None

    elif model == "gpt-4o":
        try:
            client = openai.OpenAI(api_key=api_key)
            response = client.responses.create(
                model="gpt-4o",
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
                    }
                ],
                text={"format": {"type": "text"}},
                reasoning={},
                tools=[
                    {
                        "type": "image_generation",
                        "size": "1024x1024",
                        "quality": "high",
                        "output_format": "png",
                        "background": "transparent",
                        "moderation": "auto",
                    }
                ],
                temperature=1,
                max_output_tokens=2048,
                top_p=1,
                store=True,
            )
            image_b64 = response.output[0].result
            img_bytes = BytesIO(base64.b64decode(image_b64))
            return img_bytes
        except Exception as e:
            st.error(f"GPT-4o image generation failed: {e}")
            return None

    else:
        st.error("Unknown model selected.")
        return None


def save_to_gallery(
    image_bytes, group_names, style, region="Unknown", pretty_name=None
):
    import json

    group = group_names[0] if isinstance(group_names, list) else group_names

    safe_group = group.replace(" ", "_")
    safe_region = region.replace(" ", "_")
    safe_style = style.replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    folder = os.path.join("gallery", safe_region)
    os.makedirs(folder, exist_ok=True)
    fname = f"{safe_group}_{safe_style}_{ts}.png"
    path = os.path.join(folder, fname)
    with open(path, "wb") as f:
        f.write(image_bytes.getbuffer())
    meta_path = os.path.join("gallery", "gallery_meta.json")
    try:
        with open(meta_path, "r") as mf:
            meta = json.load(mf)
    except Exception:
        meta = {}
    meta[safe_group] = pretty_name or group.replace("_", " ")
    with open(meta_path, "w") as mf:
        json.dump(meta, mf)
    return path


def load_gallery():
    if not os.path.exists("gallery"):
        return []
    files = sorted(
        [
            os.path.join("gallery", f)
            for f in os.listdir("gallery")
            if f.endswith(".png")
        ],
        reverse=True,
    )
    return files


def random_apt_name():
    apt_prefixes = [
        "APT",
        "Chimera",
        "Cobalt",
        "Shadow",
        "Ghost",
        "Red",
        "Blue",
        "Emerald",
        "Night",
        "Golden",
        "Silent",
        "Frost",
        "Dark",
        "Phantom",
        "Cyber",
        "Dragon",
        "Specter",
    ]
    apt_suffixes = [
        "Panda",
        "Bear",
        "Falcon",
        "Jackal",
        "Fox",
        "Wolverine",
        "Hawk",
        "Tiger",
        "Serpent",
        "Scorpion",
        "Hornet",
        "Mantis",
        "Wolf",
        "Wasp",
        "Raven",
        "Owl",
        "Phoenix",
        "Orchid",
    ]
    numbers = [str(random.randint(10, 99)), "Prime", "Zero", "Black", "Alpha", "Storm"]
    formats = [
        lambda: f"{random.choice(apt_prefixes)} {random.choice(apt_suffixes)}",
        lambda: f"{random.choice(apt_prefixes)}-{random.choice(numbers)}",
        lambda: f"{random.choice(apt_suffixes)} Group",
        lambda: f"Operation {random.choice(apt_suffixes)}",
        lambda: f"{random.choice(apt_prefixes)} {random.choice(apt_suffixes)} {random.choice(numbers)}",
    ]
    return random.choice(formats)()


def img_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()


def clean_group_name(filename):
    base = os.path.basename(filename)
    group_part = base.split("_")[0]
    return group_part.replace("_", " ")


from collections import defaultdict


def get_group_name_from_file(img_path):
    base = os.path.basename(img_path)
    # Extract the slug (first part before style/timestamp)
    slug = "_".join(base.split("_")[:-2])
    # Load the mapping
    meta_path = os.path.join("gallery", "gallery_meta.json")
    try:
        with open(meta_path, "r") as mf:
            meta = json.load(mf)
    except Exception:
        meta = {}
    pretty = meta.get(slug)
    if pretty:
        return pretty
    return slug.replace("_", " ")



def load_images():
    image_files = glob.glob("gallery/*/*.png")
    regions = set()
    for image_file in image_files:
        parts = image_file.replace("\\", "/").split("/")
        if len(parts) >= 3:
            regions.add(parts[1])
    regions = sorted(regions)
    return image_files, regions

st.sidebar.image("favicon.png", width=80)


updated = last_updated()
with st.sidebar.expander(f"MITRE Data - `{updated.strftime('%Y-%m-%d') if updated else 'Never'}`", expanded=False):

    mitre_stale = is_stale()
    updated = last_updated()
    if mitre_stale:
        st.caption(
            f"MITRE group data is stale or missing. Last update: {updated if updated else 'Never'}"
        )
    else:
        st.caption(
            f"MITRE group data last updated: {updated.strftime('%Y-%m-%d') if updated else 'Never'}"
        )

    if st.button("Download/Refresh MITRE Group Data"):
        try:
            download_mitre_json()
            st.success("MITRE group data downloaded/refreshed.")
        except Exception as e:
            st.error(f"Failed to download MITRE group data: {e}")

# API Key management
with st.sidebar.expander("AI Config", expanded=False):
    api_key = st.text_input("OpenAI API Key", value=DEFAULT_API_KEY, type="password")
    use_free = st.checkbox("Use Free OpenAI API (low limits)", value=not bool(api_key))

# Logo upload and palette extraction
with st.sidebar.expander("Image Generation Config", expanded=False):
    st.caption(
        "Generate your APT using the color pallate of your logo so that everyone will know you did it"
    )
    uploaded_logo = st.file_uploader(
        "Upload Logo for Color Palette", type=["png", "jpg", "jpeg"]
    )
    palette = []
    if uploaded_logo is not None:
        uploaded_logo.seek(0)
        palette = get_palette_from_logo(uploaded_logo)
        st.sidebar.markdown("**Palette Preview:**")
        for color in palette:
            st.sidebar.markdown(
                f'<div style="width:30px;height:30px;display:inline-block;border-radius:4px;background:{color};margin-right:3px;"></div>',
                unsafe_allow_html=True,
            )

groups_df = get_group_data()
if groups_df.empty:
    st.error(
        "MITRE group data is missing or failed to load. Use the sidebar to download or refresh."
    )
    st.stop()

image_files, regions_list = load_images()
col_logo, col_metrics1, col_metrics2, col_metrics3 = st.columns([3, 1, 1, 1])
with col_logo:
    st.image("logo.png")

from collections import Counter

image_files, regions_list = load_images()
image_meta = []
for image_file in image_files:
    region = image_file.split("/")[1] if "/" in image_file else "Unknown"
    base = os.path.basename(image_file)
    style = "Unknown"
    if "_" in base:
        parts = base.split("_")
        if len(parts) >= 3:
            style = parts[-2]
    group = get_group_name_from_file(image_file)
    image_meta.append({"Region": region, "Style": style, "Group": group})

style_counts = Counter([m["Style"] for m in image_meta])
region_counts = Counter([m["Region"] for m in image_meta])
group_counts = Counter([m["Group"] for m in image_meta])

top_style, style_count = ("", 0)
if style_counts:
    top_style, style_count = style_counts.most_common(1)[0]

top_region, region_count = ("", 0)
if region_counts:
    top_region, region_count = region_counts.most_common(1)[0]

top_group, group_count = ("", 0)
if group_counts:
    top_group, group_count = group_counts.most_common(1)[0]

with col_metrics1:
    st.metric("Top Style", f"{top_style or 'N/A'}", f"{style_count} images")
with col_metrics2:
    st.metric("Top Region", f"{top_region or 'N/A'}", f"{region_count} images")
with col_metrics3:
    st.metric("Top Group", f"{top_group or 'N/A'}", f"{group_count} images")



col1, col2, col3, col4, col5 = st.columns([2, 2, 3, 2, 2])
with col1:
    model_picker = st.selectbox(
        "`Choose Model`",
        options=["GPT-4o", "DALL-E"],
        index=0,
        help="DALL-E for images, GPT-4o for advanced multi-modal",
    )

with col2:
    region = st.selectbox(
        "`Filter by Geo Region`",
        sorted(groups_df["Region"].unique()),
        key="main_region",
    )
with col3:
    filtered_groups = groups_df[groups_df["Region"] == region]
    group_names = st.multiselect(
        "`Select APT Groups`",
        filtered_groups["Name"].tolist(),
        max_selections=3,
        key="main_group_names",
    )
with col4:
    additional_context = st.text_input(
        "`Additional Context (optional)`", key="main_context"
    )

style_labels = [label for label, _ in style_options]
style_map = {label: key for label, key in style_options}
with col5:
    image_style_display = st.selectbox("`Image Style`", style_labels, key="main_style")
    custom_style = ""
    if image_style_display == "Choose Your Own Adventure":
        custom_style = st.text_area(
            "Describe your APT, theme, data, memes, or wild scenario (be as specific as you want):",
            key="main_custom_style",
            height=160,
            placeholder="Example: A gang of sentient Commodore 64s running a cryptocurrency scam inside your moms house."
        )
    image_style_key = style_map[image_style_display]


def get_style_prompt(style_key, custom_style=""):
    if style_key == "Choose Your Own Adventure":
        return custom_style.strip() or "unique, distinctive"
    return STYLE_PROMPT_MAP.get(style_key, style_key)



style_desc = get_style_prompt(image_style_key, custom_style)






if group_names:
    selected_df = groups_df[groups_df["Name"].isin(group_names)][
        ["Region", "Name", "Aliases", "Description"]
    ]
    st.dataframe(selected_df, hide_index=True, use_container_width=True)

    if st.button("Draw APT", help="Generate images for all actors in the table."):
        style = (
            custom_style
            if image_style_key == "Your Own" and custom_style
            else image_style_key
        )
        color_prompt = ""
        if palette:
            color_prompt = "Use this color palette: " + ", ".join(palette) + "."
        context_prompt = f" {additional_context.strip()}" if additional_context else ""
        key_to_use = None if use_free else api_key.strip()
        chosen_model = model_picker

        chosen_model = "gpt-4o" if model_picker == "GPT-4o" else "dall-e-3"
        for idx, row in selected_df.iterrows():
            actor_prompt = (
                f"Create a {style_desc} image representing an advanced persistent threat (APT), bad actor group or cyber adversary group from {row['Region']} known commonly to the intelligence industry as {row['Name']}, that also goes by the following aliases {row['Aliases']}. This group is known for the following malicious behaviors {row['Description']}. "
                f"Combine their region, aliases and name with what they are known for in the imagery."
                f"{color_prompt} {context_prompt} "
                "The image must be visually striking, clean, and professional. "
                "Background must be fully transparent. No watermarks."
            )
            st.caption(
                f"+ Generating image for APT Group: `{row['Name']}`\n\n + Using the following prompt: `{actor_prompt}`"
            )
            img_bytes = generate_image_with_openai(
                actor_prompt, key_to_use, model=chosen_model
            )
            if img_bytes is not None:
                img = Image.open(img_bytes)
                st.image(img, use_container_width=False, width=256, caption=row["Name"])
                region = row["Region"]
                fname = save_to_gallery(
                    img_bytes,
                    [row["Name"].replace(" ", "_")],
                    style,
                    region=region,
                    pretty_name=row["Name"],
                )
                with open(fname, "rb") as f:
                    st.download_button(
                        label=f"Download {row['Name']} PNG",
                        data=f,
                        file_name=os.path.basename(fname),
                        mime="image/png",
                        key=f"dl_{row['Name']}",
                    )
            else:
                st.error(f"Failed to generate image for {row['Name']}.")

        if img_bytes is not None:
            img = Image.open(img_bytes)
            st.image(img, use_container_width=True)
            st.success("Image generated. Transparent background enforced.")
            region = row["Region"]
            fname = save_to_gallery(
                img_bytes,
                [row["Name"].replace(" ", "_")],
                style,
                region=region,
                pretty_name=row["Name"],
            )

            with open(fname, "rb") as f:
                st.download_button(
                    label="Download PNG",
                    data=f,
                    file_name=os.path.basename(fname),
                    mime="image/png",
                )
        else:
            st.error(
                "Failed to generate image. Please check your API key or try again later."
            )
with st.sidebar.expander("Make up a new APT group", expanded=False):
    if "fake_apt_stage" not in st.session_state:
        st.session_state.fake_apt_stage = 0
    if "fake_apt_name" not in st.session_state:
        st.session_state.fake_apt_name = ""
    if "fake_apt_region" not in st.session_state:
        st.session_state.fake_apt_region = ""
    if "fake_apt_prompt" not in st.session_state:
        st.session_state.fake_apt_prompt = ""
    if "fake_apt_image" not in st.session_state:
        st.session_state.fake_apt_image = None

    if st.session_state.fake_apt_stage == 0:
        if st.button("PUSH THE BUTTON"):
            st.session_state.fake_apt_stage = 1

    if st.session_state.fake_apt_stage == 1:
        regions = sorted(groups_df["Region"].unique())
        fake_region = st.selectbox(
            "`Choose a region for your new APT group`",
            regions,
            key="fake_apt_region_sel",
        )
        if st.button("Find out", key="gen_fake_apt_name"):
            st.session_state.fake_apt_name = random_apt_name()
            st.session_state.fake_apt_region = fake_region
            st.session_state.fake_apt_stage = 2

    if st.session_state.fake_apt_stage == 2:
        st.caption(
            f"Your generated APT group: \n\n `{st.session_state.fake_apt_name}` hacks from `{st.session_state.fake_apt_region}`"
        )
        if st.button("Prove it"):
            style = (
                custom_style
                if image_style_key == "Your Own" and custom_style
                else image_style_key
            )
            color_prompt = ""
            if palette:
                color_prompt = "Use this color palette: " + ", ".join(palette) + "."
            context_prompt = (
                f" {additional_context.strip()}" if additional_context else ""
            )
            fake_prompt = (
                f"Draw a high-resolution transparent PNG logo for a fictional APT group called {st.session_state.fake_apt_name}. "
                f"Region: {st.session_state.fake_apt_region}. Style: {style}. "
                f"{color_prompt} {context_prompt} Background must be transparent. No watermarks."
            )
            st.session_state.fake_apt_prompt = fake_prompt
            key_to_use = None if use_free else api_key.strip()
            img_bytes = generate_image_with_openai(fake_prompt, key_to_use)
            if img_bytes is not None:
                img = Image.open(img_bytes)
                st.session_state.fake_apt_image = img
            else:
                st.session_state.fake_apt_image = None
            st.session_state.fake_apt_stage = 3

    if st.session_state.fake_apt_stage == 3:
        st.caption(f"`Prompt used:`\n\n{st.session_state.fake_apt_prompt}")
        if st.session_state.fake_apt_image is not None:
            st.sidebar.image(
                st.session_state.fake_apt_image,
                use_container_width=False,
                width=128,
                caption=f"APT: {st.session_state.fake_apt_name}",
            )
            buf = BytesIO()
            st.session_state.fake_apt_image.save(buf, format="PNG")
            style = (
                custom_style
                if image_style_key == "Your Own" and custom_style
                else image_style_key
            )
            fname = save_to_gallery(buf, [st.session_state.fake_apt_name], style)
            with open(fname, "rb") as f:
                st.sidebar.download_button(
                    label="Download PNG",
                    data=f,
                    file_name=os.path.basename(fname),
                    mime="image/png",
                )

        else:
            st.error(
                "Failed to generate image. Please check your API key or try again later."
            )
        if st.button("Make another new APT group", key="reset_fake_apt"):
            st.session_state.fake_apt_stage = 0
            st.session_state.fake_apt_name = ""
            st.session_state.fake_apt_region = ""
            st.session_state.fake_apt_prompt = ""
            st.session_state.fake_apt_image = None


with st.expander("`𝚃𝙾𝙿 𝚂𝙴𝙲𝚁𝙴𝚃 𝙰𝙿𝚃 𝙳𝙾𝚂𝚂𝙸𝙴𝚁𝚂`", expanded=False):
    image_files, regions = load_images()
    selected_regions = st.multiselect("Select Region(s)", regions, default=regions)
    n = st.slider("Select Grid Width", 1, 6, 3)

    image_meta = []
    for image_file in image_files:
        region = image_file.split("/")[1] if "/" in image_file else "Unknown"
        group = get_group_name_from_file(image_file)
        image_meta.append({"path": image_file, "region": region, "group": group})
    filtered = [m for m in image_meta if m["region"] in selected_regions]
    filtered = sorted(filtered, key=lambda x: (x["region"], x["group"]))

    images_by_region = defaultdict(list)
    for meta in filtered:
        images_by_region[meta["region"]].append(meta)

    if "gallery_checked" not in st.session_state:
        st.session_state["gallery_checked"] = {}

    show_large = st.checkbox("Show Large Image", value=True, key="show_large_image_toggle")

    if show_large:
        col_gallery, col_large = st.columns([1, 1], gap="small")
        with col_gallery:
            for region in selected_regions:
                if images_by_region[region]:
                    st.code(region)
                    region_images = images_by_region[region]
                    groups = [
                        region_images[i : i + n] for i in range(0, len(region_images), n)
                    ]
                    for group in groups:
                        cols = st.columns(len(group))
                        for i, meta in enumerate(group):
                            img_path = meta["path"]
                            group_name = meta["group"]
                            cols[i].image(
                                img_path, use_container_width=True, caption=group_name
                            )
                            cb_key = f"gallery_cb_{img_path}"
                            checked = st.session_state["gallery_checked"].get(cb_key, False)
                            st.session_state["gallery_checked"][cb_key] = cols[i].checkbox(
                                group_name, value=checked, key=cb_key
                            )

        with col_large:
            checked_imgs = [
                k.split("gallery_cb_")[1]
                for k, v in st.session_state["gallery_checked"].items()
                if v
            ]
            if checked_imgs:
                selected_img = checked_imgs[0]
                st.image(selected_img, use_container_width=True)
                with open(selected_img, "rb") as f:
                    st.download_button(
                        label="Download Image",
                        data=f,
                        file_name=os.path.basename(selected_img),
                        mime="image/png",
                        key="download_large_image",
                    )
            else:
                st.info("Check a box next to a thumbnail to view and download.")
    else:
        for region in selected_regions:
            if images_by_region[region]:
                st.code(region)
                region_images = images_by_region[region]
                groups = [
                    region_images[i : i + n] for i in range(0, len(region_images), n)
                ]
                for group in groups:
                    cols = st.columns(len(group))
                    for i, meta in enumerate(group):
                        img_path = meta["path"]
                        group_name = meta["group"]
                        cols[i].image(
                            img_path, use_container_width=True, caption=group_name
                        )
                        cb_key = f"gallery_cb_{img_path}"
                        checked = st.session_state["gallery_checked"].get(cb_key, False)
                        st.session_state["gallery_checked"][cb_key] = cols[i].checkbox(
                            group_name, value=checked, key=cb_key
                        )

