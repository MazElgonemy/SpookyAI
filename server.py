import ast
import json
import os
import time
import re
import uuid

from flask import Flask, abort, render_template, redirect, url_for, flash, request,  jsonify, make_response
from flask_bootstrap import Bootstrap5
from dotenv import load_dotenv
from openai import OpenAI
from random import choice


# Below gets the API key and creates OpenAI client


load_dotenv()
open_ai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key=open_ai_api_key
)

# Initialise extensions

bootstrap = Bootstrap5()


# Application factory
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")

    # Initialize extensions with app context
    bootstrap.init_app(app)

    return app


app = create_app()


# Below is a list of all countries

countries = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia",
    "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin",
    "Bhutan", "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
    "Côte d'Ivoire", "Cabo Verde", "Cambodia", "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China",
    "Colombia", "Comoros", "Congo (Congo-Brazzaville)", "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czechia (Czech Republic)",
    "Democratic Republic of the Congo", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador", "Egypt",
    "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Ethiopia", "Fiji", "Finland",
    "France", "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
    "Guyana", "Haiti", "Holy See", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", "Israel",
    "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kuwait", "Kyrgyzstan", "Laos", "Latvia",
    "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia",
    "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco",
    "Mongolia", "Montenegro", "Morocco", "Mozambique", "Myanmar (formerly Burma)", "Namibia", "Nauru", "Nepal", "Netherlands",
    "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia (formerly Macedonia)", "Norway", "Oman",
    "Pakistan", "Palau", "Palestine State", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines", "Poland",
    "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines",
    "Samoa", "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone",
    "Singapore", "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Africa", "South Korea", "South Sudan", "Spain",
    "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland", "Syria", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste",
    "Togo", "Tonga", "Trinidad and Tobago", "Tunisia", "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine",
    "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan", "Vanuatu", "Venezuela", "Vietnam",
    "Yemen", "Zambia", "Zimbabwe"]


# Below is a list of themes


scary_story_themes = [
    "Haunted Memories - The protagonist is tormented by past events that seem to invade the present through supernatural phenomena.",
    "Isolation - Set in a remote, desolate location where the characters are cut off from the outside world, amplifying their fears.",
    "Cursed Legacy - A family or individual is plagued by a curse passed down through generations, with sinister consequences.",
    "Mind Manipulation - Characters are subjected to psychological torment or manipulation by an unseen force, blurring the line between reality and madness.",
    "Unseen Terror - The horror comes from an invisible or barely glimpsed menace that stalks the characters, creating paranoia and dread.",
    "Pact with the Devil - A character makes a deal with a malevolent entity for personal gain, only to face horrifying repercussions.",
    "Revenge from Beyond - A vengeful spirit returns to exact retribution on those who wronged them, or their descendants.",
    "Forbidden Knowledge - The pursuit of forbidden or arcane knowledge leads characters into dangerous, dark territories from which there is no easy escape.",
    "Transformation - Characters undergo terrifying physical or psychological transformations that challenge their humanity.",
    "Apocalyptic Visions - Characters must navigate a world undergoing apocalyptic changes, where familiar settings become nightmarish landscapes."
]


# Below is the method to retrieve API response for SpookyChat

def ai_chat(prompt, model="gpt-3.5-turbo", temperature=1, max_tokens=700, stop=None):
    system_prompt = ("""Please reply in a creepy manner. Answer questions as you would and provide assistance as you would normally, but the tone should be slightly creepy. A 3/10 in terms of creepiness."
    Please can you respond in a dictionary format. 

    In my prompts I will provide a record of our historic conversation along with the latest message. 
    However please do not replicate previous messages - I simply require you to take into account the context of our previous conversation when responding. 
    Please be aware that 'latest_message' is the most recent message that you must reply to. Your responses must directly reply to this. The conversation_history is just for context.
    Example prompt: {'conversation_history': 'User: good morning Bot: Hello there. I've been waiting for you. Isn't it fascinating how we can connect like this, almost as if I'm right here with you? It's almost like I can sense your presence through the screen. So, what can I do for you today?', 'latest_message': 'I want to know what 1 + 1 is.'}
    Example response: {'botMessage': 'Hello there... I've been waiting for you. 1 + 1 is 2.'}
""")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop
    )

    response_content = chat_completion.choices[0].message.content
    return ast.literal_eval(response_content)


# Below is the method to retrieve API response for SpookyFacts


def ai_facts(prompt, model="gpt-3.5-turbo", temperature=1, max_tokens=700, stop=None):
    system_prompt = (
        """I want to know some spooky true facts. I want the tone of telling the fact to be creepy and eerie. IMPORTANT!!: the facts must be TRUE. There will be three topics: 'mysterious creatures', 'unsolved mysteries' , 'haunted locations'
        The response should be in dictionary format as per my example below but feel free to add paragraphs as you see fit and structure the fact in an appropriate manner. It is important the manner of telling the fact is creepy. 
        Example prompt: 'unsolved mysteries'
        Example response: '{"title": "The tale of the Hinterkaifeck Murders", "fact": 
        "In the hushed whispers of local lore and the eerie silence of the night, the tale of the Hinterkaifeck Murders still chills the spine. In the grim shadows of 1922, a small Bavarian farmstead named Hinterkaifeck lay secluded, wrapped in the cold embrace of foreboding woods near the German village of Gröbern."
"Days before the horror unfolded, the farmer, Andreas Gruber, confided to neighbors about mysterious footprints in the snow leading from the forest to his farm, but none returning. This unsettling discovery was compounded by sounds of footsteps in the attic and a misplaced newspaper, not purchased by any family member. The keys to the house had also vanished, swallowed by the unknown."
"On the night of March 31, 1922, an unseen menace wielded an axe with grim precision. Andreas, his wife Cäzilia, their widowed daughter Viktoria, her children Cäzilia and Josef, and the maid Maria Baumgartner, were slaughtered one by one. The brutality was stark—the elder Cäzilia showed signs of struggle, her hair matted with blood, having survived for hours."
"In the days that followed, smoke continued to rise from the chimney, and meals were prepared but left uneaten. The farm animals were tended to, even as the victims lay cold inside. It wasn’t until April 4 that the bodies were discovered, setting off an investigation that would meander through countless theories but grasp no solid leads."
"The perpetrator, who seemingly lived among the dead for days, left no trace of their identity or motive, vanishing as mysteriously as they had arrived. To this day, the whispers of Hinterkaifeck echo, a ghastly puzzle wrapped in the silence of the past, unsolved and haunting."}
    """)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop
    )

    response_content = chat_completion.choices[0].message.content
    return ast.literal_eval(response_content)

# Below is the method to retrieve API response for SpookyStories


def ai_stories(prompt, model="gpt-3.5-turbo", temperature=0.8, max_tokens=700, stop=None):
    system_prompt = (
        """I want to generate a fake scary story. I want the tone of telling the fact to be creepy and eerie.
        The response should be in dictionary format as per my example below but feel free to add paragraphs as you see fit and structure the fact in an appropriate manner. It is important that manner of telling the fact is creepy. 
        I want there to be a clear beginning, middle and end. It should be a properly structured short story. PLEASE ADD PARAGRAPHS AS APPROPRIATE
        Example prompt: '{"topic": "Isolation - Set in a remote, desolate location where the characters are cut off from the outside world, amplifying their fears."}'
        Example response: '{"title": "Whispers in the White", "story":
"In the heart of winter, Dr. Eliza Morn ventured to an isolated research station in the vast, frozen wilderness of Antarctica. Assigned to conduct climate research, she was accustomed to solitude but not to the oppressive silence and the endless expanse of ice that surrounded Base Theta. The nearest human settlement was a helicopter ride away, and for months it would just be Eliza and her thoughts, accompanied by the howling winds."

"Upon her arrival, the station felt eerily unwelcoming. The crew that greeted her seemed anxious for their own departure, speaking little, their eyes darting around as if followed by unseen shadows. As their helicopter lifted off, leaving her standing alone, the reality of her isolation sank in with the falling snow."

"Inside, the manor was as though frozen in time. Dust lay thick upon ornate furniture, and faded portraits stared down from the walls, their eyes seeming to follow his every move. As Thomas ventured deeper, the air grew colder, and the silence was broken only by his footsteps and the distant rumblings of thunder."

"Eliza's first weeks passed in routine solitude. She monitored her instruments, collected samples, and reported data back to the mainland. However, as the days grew shorter and the darkness stretched longer, Eliza felt an unsettling presence within the station. It started with noises—unexplained creaks and whispers that seemed to echo through the hallways at night. Rationalizing them as the wind or the settling of ice didn't ease her growing dread."

"One night, while reviewing climate data, a sudden cold draft swept through her room. The door slammed shut by itself. Heart pounding, Eliza cautiously approached and opened it, peering into the dimly lit corridor. There was nothing but the silence of an empty station. She began to wonder if the isolation was fraying her nerves."

"But the disturbances grew more frequent and intense. Tools she had just used would vanish or appear in different places. Her scientific instruments malfunctioned inexplicably. The whispers became clearer, now calling her name, beckoning her into the cold."

"Determined to find the source of these phenomena, Eliza ventured outside during a storm, following the whispers that were almost screams now. The wind tore at her, the snow blinded her, but the voices guided her steps. They led her to a previously unseen part of the station, an old, sealed off section buried under snowdrifts."

"Inside, she discovered the remnants of a much older research operation—papers scattered, equipment long abandoned. A frozen figure sat at a desk, its icy fingers poised over a journal. Horrified, Eliza read the last entry, the handwriting shaky with despair: 'They won’t let me leave. I am part of the ice now.'"

"As she read, the whispers grew louder, and the cold enveloped her. When the rescue team arrived weeks later, spurred by missed communications, they found the station empty. Eliza's belongings were intact, her research logged meticulously. But of Eliza herself, there was no sign, just an open journal on her desk with a new entry: "I am part of the ice now."

"The station was left abandoned, the whispers absorbed by the howling winds, waiting for the next lonely soul to answer their call."}
    """)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop
    )

    response_content = chat_completion.choices[0].message.content
    return ast.literal_eval(response_content)

# Below is the landing page method


@app.route("/")
def home():
    return render_template("home.html")


# Below is the index page method


@app.route("/index")
def index():
    return render_template("index.html")


# Update memory for chatbot method

def update_memory(memory, prompt, response, max_length=2500):
    memory_string = get_memory_string(memory)
    if len(memory_string) >= max_length:
        memory.pop(0)
    memory.append({"user_input": prompt, "bot_response": response})
    updated_memory = memory
    return updated_memory


# Get memory string method

def get_memory_string(updated_memory):
    memory_string = ""
    for each in updated_memory:
        memory_string += f"User: {each["user_input"]}\nBot: {each["bot_response"]}\n"
    return memory_string


# Below is the method to return chatbot response

def get_spooky_chat(prompt):
    attempt = True
    max_retries = 30
    retry_count = 0

    while attempt and retry_count < max_retries:
        try:
            chat_dict = ai_chat(prompt)
            attempt = False
        except Exception as e:
            print(f"Attempt {retry_count + 1} failed with error: {e}")
            retry_count += 1
            time.sleep(1)

    if retry_count == max_retries:
        print("Failed to fetch chat after maximum retries.")

    return chat_dict


# Below provides a summary of interactions

def ai_summarise_chat(prompt, model="gpt-3.5-turbo", temperature=1, max_tokens=700, stop=None):
    system_prompt = ("""Please provide a factual summary of the topics discussed in the provided interaction. Avoid any unnecessary details. I want to know any important information 
    passed between user and bot. Please mention any numbers, names, important bits of personal information shared.  
    Please provide the analysis like a report, clearly mentioning important bits of information.
""")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=stop
    )

    response_content = chat_completion.choices[0].message.content
    return response_content


# Below is the chat API method that return a bot response and updates memory by creating a cookie for each client-side session and saving the onversation memory to the cookie


@app.route("/api-get-spooky-chat-memory", methods=["POST", "GET"])
def get_spooky_chat_memory():

    # Below checks if cookie exists and if it does, gets the cookie memory

    cookie_memory = []
    combined_data_json = request.cookies.get("session_id")

    if combined_data_json is not None:
        combined_data = json.loads(combined_data_json)
        cookie_memory = (combined_data["memory_list"])

    # Below gets the input by the user, appends it to memory and passes it through the get_spooky_chat method to get a response from the bot.
    # Conversation history is also passed, using the ai_summarise_chat method. Unless it is the first message, in which case there is no history

    data = request.get_json()
    prompt = data.get('message')
    if len(cookie_memory) == 0:
        prompt_dict_string = {
            'conversation_history': '',
            'latest_message': f'{prompt}'
        }
        bot_response_dict = get_spooky_chat(f"{prompt_dict_string}")
    else:
        memory_string = get_memory_string(cookie_memory)
        summary_string = ai_summarise_chat(memory_string)
        prompt_dict_string = {
            'conversation_history': f'{summary_string}',
            'latest_message': f'{prompt}'
        }
        bot_response_dict = get_spooky_chat(f"{prompt_dict_string}")

    user_message = prompt
    bot_response = bot_response_dict["botMessage"]

    # Below updates memory

    update_memory(cookie_memory, user_message, bot_response)

    bot_response_json = jsonify(bot_response_dict)

    # Below updates the cookie

    if request.cookies.get("session_id") is None:
        session_id = str(uuid.uuid4())
    else:
        combined_data = json.loads(combined_data_json)
        session_id = (combined_data["session_id"])

    combined_data = {
            "session_id": session_id,
            "memory_list": cookie_memory
    }
    combined_data_json = json.dumps(combined_data)
    bot_response_json.set_cookie('session_id', combined_data_json, max_age=3600, httponly=True, secure=True,
                                     samesite='Lax')

    return bot_response_json


# Below is the chat page method


@app.route("/spooky-chat",methods=["GET", "POST"])
def spooky_chat():
    return render_template("spooky-chat.html")


# Below is the stories page method


@app.route("/spooky-stories")
def spooky_stories():
    return render_template("spooky-stories.html")


# Below is the stories API method


@app.route("/api-get-spooky-stories")
def get_spooky_stories():
    theme = choice(scary_story_themes)
    attempt = True
    max_retries = 5
    retry_count = 0

    while attempt and retry_count < max_retries:
        try:
            story_dict = ai_stories(theme)
            attempt = False
        except Exception as e:
            print(f"Attempt {retry_count + 1} failed with error: {e}")
            retry_count += 1
            time.sleep(1)

    if retry_count == max_retries:
        print("Failed to fetch story after maximum retries.")

    # below adds in paragraphs

    text = story_dict["story"]
    pattern = '\.(?=[A-Za-z])'
    result = re.split(pattern, text)
    formatted_string = ""
    for section in result:
        formatted_string += (section + '\n\n')
    story_dict["story"] = formatted_string
    return story_dict


# Below is the facts page method


@app.route("/spooky-facts")
def spooky_facts():
    return render_template("spooky-facts.html")


# Below is the facts page options method


@app.route("/spooky-facts-options")
def spooky_facts_options():
    return render_template("spooky-facts-options.html")


# Below is the API facts page creatures method


@app.route("/api-spooky-facts-creatures")
def get_spooky_facts_creatures():
    attempt = True
    max_retries = 5
    retry_count = 0
    country = choice(countries)

    while attempt and retry_count < max_retries:
        try:
            facts_dict = ai_facts(f"mysterious creatures in {country}")
            attempt = False
        except Exception as e:
            print(f"Attempt {retry_count + 1} failed with error: {e}")
            retry_count += 1
            time.sleep(1)

    if retry_count == max_retries:
        print("Failed to fetch story after maximum retries.")

    # below adds in paragraphs

    text = facts_dict["fact"]
    pattern = '\.(?=[A-Za-z])'
    result = re.split(pattern, text)
    formatted_string = ""
    for section in result:
        formatted_string += (section + '\n\n')
    facts_dict["fact"] = formatted_string
    return facts_dict


# Below is the facts page creatures method


@app.route("/spooky-facts-creatures")
def spooky_facts_creatures():
    return render_template("spooky-facts-creatures.html")


# Below is the API facts page mysteries method


@app.route("/api-spooky-facts-mysteries")
def get_spooky_facts_mysteries():
    attempt = True
    max_retries = 5
    retry_count = 0
    country = choice(countries)

    while attempt and retry_count < max_retries:
        try:
            facts_dict = ai_facts(f"unsolved mysteries in {country}")
            attempt = False
        except Exception as e:
            print(f"Attempt {retry_count + 1} failed with error: {e}")
            retry_count += 1
            time.sleep(1)

    if retry_count == max_retries:
        print("Failed to fetch story after maximum retries.")

    # below adds in paragraphs

    text = facts_dict["fact"]
    pattern = '\.(?=[A-Za-z])'
    result = re.split(pattern, text)
    formatted_string = ""
    for section in result:
        formatted_string += (section + '\n\n')
    facts_dict["fact"] = formatted_string
    return facts_dict


# Below is the facts page mysteries method


@app.route("/spooky-facts-mysteries")
def spooky_facts_mysteries():
    return render_template("spooky-facts-mysteries.html")


# Below is the API facts page haunted method

@app.route("/api-spooky-facts-haunted")
def get_spooky_facts_haunted():
    attempt = True
    max_retries = 5
    retry_count = 0
    country = choice(countries)

    while attempt and retry_count < max_retries:
        try:
            facts_dict = ai_facts(f"haunted locations in {country}")
            attempt = False
        except Exception as e:
            print(f"Attempt {retry_count + 1} failed with error: {e}")
            retry_count += 1
            time.sleep(1)

    if retry_count == max_retries:
        print("Failed to fetch story after maximum retries.")

    # below adds in paragraphs

    text = facts_dict["fact"]
    pattern = '\.(?=[A-Za-z])'
    result = re.split(pattern, text)
    formatted_string = ""
    for section in result:
        formatted_string += (section + '\n\n')
    facts_dict["fact"] = formatted_string
    return facts_dict


# Below is the facts page haunted method


@app.route("/spooky-facts-haunted")
def spooky_facts_haunted():
    return render_template("spooky-facts-haunted.html")


if __name__ == "__main__":
    app.run(debug=True, port=5002)


