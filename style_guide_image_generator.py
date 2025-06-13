import os
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
import openai
import time

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file. Please set it.")

# Create styleguide directory if it doesn't exist
STYLEGUIDE_DIR = "styleguide"
if not os.path.exists(STYLEGUIDE_DIR):
    os.makedirs(STYLEGUIDE_DIR)

# Mustang Panda data
GROUP_DATA = {
    "Region": "China",
    "Name": "Mustang Panda",
    "Aliases": "Mustang Panda, TA416, RedDelta, BRONZE PRESIDENT",
    "Description": (
        "Mustang Panda is a China-based cyber espionage threat actor that was first observed in 2017 but may have been conducting operations since at least 2014. "
        "Mustang Panda has targeted government entities, nonprofits, religious, and other non-governmental organizations in the U.S., Europe, Mongolia, Myanmar, Pakistan, and Vietnam, among others."
    )
}

# Style guide data (from your app)
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

# Image generation function (exact GPT-4o branch from your app)
def generate_image_with_openai(prompt, api_key, model="gpt-4o"):
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
        print(f"Image generation failed: {e}")
        return None

# Generate images for each style
def generate_styleguide_images():
    model = "gpt-4o"
    for style_key, style_desc in STYLE_PROMPT_MAP.items():
        # Construct prompt based on your app's logic
        actor_prompt = (
            f"Create a {style_desc} image representing an advanced persistent threat (APT), bad actor group or cyber adversary group from {GROUP_DATA['Region']} "
            f"known commonly to the intelligence industry as {GROUP_DATA['Name']}, that also goes by the following aliases {GROUP_DATA['Aliases']}. "
            f"This group is known for the following malicious behaviors {GROUP_DATA['Description']}. "
            f"Combine their region, aliases and name with what they are known for in the imagery. "
            f"The image must be visually striking, clean, and professional. "
            f"Background must be fully transparent. No watermarks."
        )
        
        print(f"Generating image for style: {style_key}")
        img_bytes = generate_image_with_openai(actor_prompt, API_KEY, model)
        
        if img_bytes is not None:
            try:
                # Save image to styleguide directory
                filename = style_key.replace(" ", "_") + ".png"
                filepath = os.path.join(STYLEGUIDE_DIR, filename)
                img = Image.open(img_bytes)
                img.save(filepath, format="PNG")
                print(f"Saved image: {filepath}")
            except Exception as e:
                print(f"Failed to save image for {style_key}: {e}")
        else:
            print(f"Failed to generate image for {style_key}")
        
        # Add delay to avoid hitting API rate limits
        time.sleep(2)

if __name__ == "__main__":
    generate_styleguide_images()