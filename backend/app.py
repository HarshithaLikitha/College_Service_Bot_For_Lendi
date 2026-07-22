from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import google.generativeai as genai
import os
import re
import time

app = Flask(__name__)
CORS(app)

# Configure Gemini API (replace with env var for production)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'Paste_Your_API_Key_Here')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-flash-latest")

# Load college information
with open('../data/info.json', 'r') as f:
    college_data = json.load(f)
# Conversational responses
GREETINGS = {
    'hi': 'Hello! 👋 How can I help you today?',
    'hello': 'Hi there! 😊 What would you like to know about Lendi Institute?',
    'hey': 'Hey! How can I assist you?',
    'good morning': 'Good morning! ☀️ How may I help you?',
    'good afternoon': 'Good afternoon! How can I assist you?',
    'good evening': 'Good evening! 🌆 What can I do for you?',
    'good night': 'Good night! 🌙 Feel free to ask if you need anything!',
    'thanks': 'You\'re welcome! 😊 Anything else I can help with?',
    'thank you': 'Happy to help! Let me know if you need more information.',
    'bye': 'Goodbye! Have a great day! 👋',
    'goodbye': 'Take care! Feel free to come back anytime! 😊'
}

def is_greeting(query):
    """Check if the query is a greeting or conversational phrase"""
    query_lower = query.lower().strip()
    for greeting in GREETINGS.keys():
        if query_lower == greeting or query_lower.startswith(greeting):
            return True, GREETINGS.get(greeting, "Hello! How can I help you?")
    conversational_patterns = [
        r'^(how are you|how\'s it going|what\'s up|wassup)',
        r'^(ok|okay|alright|fine)',
        r'^(yes|yeah|yep|no|nope)',
    ]
    for pattern in conversational_patterns:
        if re.match(pattern, query_lower):
            return True, "I'm here to help you with information about Lendi Institute! What would you like to know?"
    return False, None

def normalize_category(category_str):
    if not category_str:
        return None
    category_str = category_str.upper().strip()
    category_map = {
        'OC': 'OC', 'EWS': 'EWS', 'SC': 'SC', 'ST': 'ST',
        'BC-A': 'BC_A','BC-B': 'BC_B','BC-C': 'BC_C','BC-D': 'BC_D','BC-E': 'BC_E',
        'BCA': 'BC_A','BCB': 'BC_B','BCC': 'BC_C','BCD': 'BC_D','BCE': 'BC_E',
        'BC_A': 'BC_A','BC_B': 'BC_B','BC_C': 'BC_C','BC_D': 'BC_D','BC_E': 'BC_E',
        'BC A': 'BC_A','BC B': 'BC_B','BC C': 'BC_C','BC D': 'BC_D','BC E': 'BC_E'
    }
    return category_map.get(category_str)

def normalize_branch(branch_str):
    if not branch_str:
        return None
    branch_str = branch_str.upper().strip()
    branch_map = {
        'CSE': 'CSE','COMPUTER SCIENCE': 'CSE','CS': 'CSE',
        'CSIT': 'CSIT','COMPUTER SCIENCE AND INFORMATION TECHNOLOGY': 'CSIT','CS IT': 'CSIT','CIT': 'CSIT','IT': 'CSIT','INFORMATION TECHNOLOGY': 'CSIT',
        'CSS': 'CSS','COMPUTER SCIENCE AND SYSTEMS': 'CSS','CSSE': 'CSS','CS SYSTEMS': 'CSS',
        'CSM': 'CSM','AIML': 'CSM','AI ML': 'CSM','AI': 'CSM','ARTIFICIAL INTELLIGENCE': 'CSM','MACHINE LEARNING': 'CSM','AI AND ML': 'CSM',
        'ECE': 'ECE','ELECTRONICS': 'ECE','ELECTRONICS AND COMMUNICATION': 'ECE',
        'EEE': 'EEE','ELECTRICAL': 'EEE','ELECTRICAL AND ELECTRONICS': 'EEE',
        'MECH': 'Mechanical','MECHANICAL': 'Mechanical','MECHANICAL ENGINEERING': 'Mechanical'
    }
    return branch_map.get(branch_str)

def extract_eligibility_info(query):
    """Extract rank, category, gender, and branch from query"""
    query_lower = query.lower()
    negative_patterns = [r'not eligible', r'can\'t get', r'cannot get', r'didn\'t get', r'did not get', r'won\'t get']
    is_negative_statement = any(re.search(pattern, query_lower) for pattern in negative_patterns)

    rank = None
    rank_patterns = [
        r'\b(\d{3,6})\b',  # 3-6 digit numbers
        r'rank\s+(?:is\s+)?(\d{3,6})',
        r'my\s+rank\s+(?:is\s+)?(\d{3,6})',
    ]
    for pattern in rank_patterns:
        match = re.search(pattern, query_lower)
        if match:
            rank = int(match.group(1))
            break

    category = None
    category_patterns = [
        (r'\b(oc|open)\b', 'OC'),
        (r'\b(ews)\b', 'EWS'),
        (r'\b(sc)\b', 'SC'),
        (r'\b(st)\b', 'ST'),
        (r'\b(bc[-_\s]?a|bca)\b', 'BC_A'),
        (r'\b(bc[-_\s]?b|bcb)\b', 'BC_B'),
        (r'\b(bc[-_\s]?c|bcc)\b', 'BC_C'),
        (r'\b(bc[-_\s]?d|bcd)\b', 'BC_D'),
        (r'\b(bc[-_\s]?e|bce)\b', 'BC_E'),
    ]
    for pattern, cat in category_patterns:
        if re.search(pattern, query_lower):
            category = cat
            break

    gender = None
    if re.search(r'\b(girl|girls|female|women|female student|girl student|gir|gril)\b', query_lower):
        gender = 'girls'
    elif re.search(r'\b(boy|boys|male|men|male student|boy student)\b', query_lower):
        gender = 'boys'

    branch = None
    branch_patterns = [
        (r'\b(cse|computer science|cs)\b', 'CSE'),
        (r'\b(csit|cs it|cit|information technology|it)\b', 'CSIT'),
        (r'\b(css|csse|computer science and systems|cs systems)\b', 'CSS'),
        (r'\b(csm|aiml|ai ml|artificial intelligence|machine learning|ai and ml|ai)\b', 'CSM'),
        (r'\b(ece|electronics and communication|electronics)\b', 'ECE'),
        (r'\b(eee|electrical and electronics|electrical)\b', 'EEE'),
        (r'\b(mech|mechanical)\b', 'Mechanical')
    ]
    for pattern, br in branch_patterns:
        if re.search(pattern, query_lower):
            branch = br
            break

    return {
        'rank': rank,
        'category': category,
        'gender': gender,
        'branch': branch,
        'is_negative_statement': is_negative_statement
    }

def is_eligibility_query(query):
    """Robust eligibility detection: handles typos like 'cutt' and short queries"""
    query_lower = query.lower()
    eligibility_keywords = [
        'eligible', 'eligibility', 'cutoff', 'cut off', 'cut-off',
        'can i get', 'will i get', 'chances', 'my rank',
        'what is the cutoff', 'cutoff for', 'rank required',
        'minimum rank', 'required rank', 'admission',
        'which branch', 'what branch', 'qualify',
        'i got', 'i have', 'with rank', 'secured'
    ]
    # direct keyword check
    if any(keyword in query_lower for keyword in eligibility_keywords):
        return True
    # look for words starting with 'cut' to catch 'cutt', 'cutof', 'cutoff'
    words = re.findall(r'\w+', query_lower)
    for w in words:
        if w.startswith('cut') or w == 'rank' or w == 'ranks':
            return True
    return False

def get_cutoff_for_branch_category(branch, category, gender=None):
    cutoff_data = college_data.get('cutoff_marks', {})
    branch = normalize_branch(branch) if branch else None
    category = normalize_category(category) if category else None
    if not branch or branch not in cutoff_data:
        return None
    branch_cutoffs = cutoff_data[branch]
    if not category or category not in branch_cutoffs:
        return None
    category_cutoffs = branch_cutoffs[category]
    if gender:
        return {
            'branch': branch,
            'category': category,
            'gender': gender,
            'cutoff': category_cutoffs.get(gender)
        }
    else:
        return {
            'branch': branch,
            'category': category,
            'boys': category_cutoffs.get('boys'),
            'girls': category_cutoffs.get('girls')
        }

def find_eligible_branches(rank, category, gender):
    cutoff_data = college_data.get('cutoff_marks', {})
    category = normalize_category(category)
    if not category:
        return []
    eligible_branches = []
    for branch, categories in cutoff_data.items():
        if category in categories:
            cutoff = categories[category].get(gender)
            if cutoff and rank <= cutoff:
                eligible_branches.append({
                    'branch': branch,
                    'cutoff': cutoff,
                    'your_rank': rank,
                    'difference': cutoff - rank
                })
    eligible_branches.sort(key=lambda x: x['difference'], reverse=True)
    return eligible_branches

def format_eligibility_response(info, query):
    """Format eligibility response and also return list of missing fields when applicable"""
    rank = info.get('rank')
    category = info.get('category')
    gender = info.get('gender')
    branch = info.get('branch')
    query_lower = query.lower()

    cutoff_only_patterns = [
        'what is the cutoff', 'what is cutoff', 'tell me cutoff',
        'cutoff for', 'cutoff rank', 'what are the cutoffs',
        'show cutoff', 'give cutoff', 'cutoff marks'
    ]
    is_cutoff_only = any(pattern in query_lower for pattern in cutoff_only_patterns)
    personal_patterns = [
        'my rank', 'i got', 'i have', 'i am', 'can i get',
        'will i get', 'am i eligible', 'eligible for'
    ]
    is_personal = any(pattern in query_lower for pattern in personal_patterns)

    # If asking for cutoff WITHOUT personal info
    if is_cutoff_only and not is_personal and not rank:
        if branch:
            cutoff_data = college_data.get('cutoff_marks', {})
            branch = normalize_branch(branch)
            if branch and branch in cutoff_data:
                branch_cutoffs = cutoff_data[branch]
                if category:
                    category = normalize_category(category)
                    if category in branch_cutoffs:
                        cat_data = branch_cutoffs[category]
                        if gender:
                            cutoff = cat_data.get(gender)
                            return f"📊 The cutoff rank for **{branch}** in **{category}** category for **{gender}** is: **{cutoff:,}**", []
                        else:
                            return f"📊 The cutoff ranks for **{branch}** in **{category}** category are:\n• **Boys**: {cat_data['boys']:,}\n• **Girls**: {cat_data['girls']:,}", []
                    else:
                        return f"Sorry, I don't have cutoff data for {category} category in {branch}.", []
                response = f"📊 **Cutoff ranks for {branch} branch:**\n\n"
                for cat, cutoffs in branch_cutoffs.items():
                    response += f"**{cat}:**\n• Boys: {cutoffs['boys']:,}\n• Girls: {cutoffs['girls']:,}\n\n"
                return response, []
            else:
                return f"Sorry, I don't have cutoff data for {branch} branch.", []
        else:
            return "Please specify which branch you'd like to know the cutoff for. Available branches: CSE, CSIT, CSS, CSM, ECE, EEE, Mechanical", []

    # If specific branch cutoff with category but no rank
    if branch and category and not rank and not is_personal:
        cutoff_info = get_cutoff_for_branch_category(branch, category, gender)
        if cutoff_info:
            if gender:
                return f"📊 The cutoff rank for **{branch}** in **{category}** category for **{gender}** is: **{cutoff_info['cutoff']:,}**", []
            else:
                return f"📊 The cutoff ranks for **{branch}** in **{category}** category are:\n• **Boys**: {cutoff_info['boys']:,}\n• **Girls**: {cutoff_info['girls']:,}", []
        else:
            return f"Sorry, I don't have cutoff data for {branch} in {category} category.", []

    # Personal eligibility check
    if is_personal or rank:
        missing = []
        if not rank:
            missing.append('rank')
        if not category:
            missing.append('category')
        if not gender:
            missing.append('gender')
        if missing:
            human_readable = []
            for m in missing:
                if m == 'rank':
                    human_readable.append('your rank')
                elif m == 'category':
                    human_readable.append('your category (OC/EWS/SC/ST/BC-A/BC-B/BC-C/BC-D/BC-E)')
                elif m == 'gender':
                    human_readable.append('your gender (boy/girl)')
            return f"To check your eligibility, I need: {', '.join(human_readable)}. Please provide these details.", missing

    # Full eligibility check
    if branch:
        cutoff_info = get_cutoff_for_branch_category(branch, category, gender)
        if not cutoff_info or not cutoff_info.get('cutoff'):
            return f"Sorry, I don't have cutoff data for {branch} in {category} category for {gender}.", []
        cutoff = cutoff_info['cutoff']
        if rank <= cutoff:
            difference = cutoff - rank
            return f"🎉 **Great news!** With your rank of **{rank}** in **{category}** category ({gender}), you are eligible for **{branch}** at Lendi Institute!\n\nThe cutoff rank is **{cutoff}**, and you're comfortably within range by **{difference}** ranks.", []
        else:
            difference = rank - cutoff
            return f"Based on last year's cutoffs, your rank **{rank}** is above the cutoff of **{cutoff}** for **{branch}** in **{category}** category ({gender}) by **{difference}** ranks.\n\nHowever, cutoffs can vary each year. Would you like to check other branches where you might be eligible?", []

    else:
        eligible = find_eligible_branches(rank, category, gender)
        if eligible:
            response = f"🎉 Based on your rank of **{rank}** in **{category}** category ({gender}), you are eligible for the following branches:\n\n"
            for i, br in enumerate(eligible, 1):
                response += f"{i}. **{br['branch']}** (Cutoff: {br['cutoff']}, You're ahead by {br['difference']} ranks)\n"
            return response, []
        else:
            return f"Based on last year's cutoffs, your rank **{rank}** in **{category}** category ({gender}) doesn't meet the cutoff for any branch. However, cutoffs vary each year. I recommend:\n\n1. Applying anyway as cutoffs can change\n2. Considering other colleges\n3. Exploring different admission rounds\n\nWould you like to know the closest cutoffs?", []

def extract_keywords_and_intent(user_query):
    """Use Gemini to extract keywords and determine intent from user query"""
    prompt = f"""
You are analyzing a query for Lendi Institute of Engineering & Technology chatbot.

Query: "{user_query}"

Analyze this query and return ONLY a JSON object with these fields:
- "category": one of [academic, faculty, administration, facilities, general, courses, admissions, placements, eligibility]
- "keywords": list of important keywords from the query (lowercase)
- "intent": brief description of what user wants to know
- "is_specific": true if asking about specific item (like "girls hostel", "library"), false if general

Response (JSON only):"""
    try:
        response = model.generate_content(prompt)
        result = response.text.strip()
        if result.startswith('```'):
            result = result.split('```')[1]
            if result.startswith('json'):
                result = result[4:]
        result = result.strip()
        return json.loads(result)
    except Exception as e:
        print(f"Error in keyword extraction: {e}")
        # Fallback to simple keyword matching (improved to normalize cut variants)
        query_lower = user_query.lower()
        words = re.findall(r'\w+', query_lower)
        keywords = []
        for w in words:
            if len(w) > 2:
                # normalize cut variants
                if w.startswith('cut'):
                    keywords.append('cutoff')
                else:
                    keywords.append(w)
        category = "eligibility" if is_eligibility_query(user_query) else "general"
        return {
            "category": category,
            "keywords": keywords,
            "intent": "general information",
            "is_specific": False
        }

def search_college_data(extracted_info, original_query=''):
    """Search through college data based on extracted information"""
    # If keywords suggest cutoff/rank (even if category not set), treat as eligibility
    keywords = [k.lower() for k in extracted_info.get('keywords', [])]
    if (extracted_info.get('category') == 'eligibility'
        or is_eligibility_query(original_query)
        or any(k in ('cutoff', 'rank', 'ranks') or k.startswith('cut') for k in keywords)):
        info = extract_eligibility_info(original_query)
        response_text, missing = format_eligibility_response(info, original_query)
        return {'eligibility_response': response_text, 'eligibility_missing': missing, 'eligibility_info': info}

    category = extracted_info.get('category', 'general')
    keywords = [k.lower() for k in extracted_info.get('keywords', [])]
    is_specific = extracted_info.get('is_specific', False)
    results = {}
    if category in college_data:
        category_data = college_data[category]
        if is_specific:
            for key, value in category_data.items():
                key_lower = key.lower()
                value_str = str(value).lower()
                match_score = sum(1 for kw in keywords if kw in key_lower or kw in value_str)
                if match_score > 0:
                    results[key] = value
            if results:
                return results
        else:
            return category_data
    if not results:
        for cat_name, cat_data in college_data.items():
            if cat_name == 'cutoff_marks':
                continue
            for key, value in cat_data.items():
                key_lower = key.lower()
                value_str = str(value).lower()
                match_score = sum(1 for kw in keywords if kw in key_lower or kw in value_str)
                if match_score >= len(keywords) * 0.5 and keywords:
                    results[key] = value
    return results if results else {"message": "No information found"}

def format_response_with_ai(search_results, user_query, intent):
    if 'eligibility_response' in search_results:
        return search_results['eligibility_response']
    if not search_results or search_results.get("message") == "No information found":
        return "I couldn't find specific information about that. Could you please rephrase your question or ask about something else?"
    data_str = json.dumps(search_results, indent=2)
    prompt = f"""
You are a helpful college chatbot assistant for Lendi Institute of Engineering & Technology.

User asked: "{user_query}"
Intent: {intent}

Here is the relevant data from our database:
{data_str}

Format this information into a natural, conversational response. Guidelines:
- Be friendly and concise
- Answer the specific question asked
- Use bullet points only when listing multiple items
- Don't include all data if user asked for something specific
- Keep it under 150 words unless there's a lot of relevant information

Response:"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error in AI formatting: {e}")
        return format_response_basic(search_results)

def format_response_basic(search_results):
    response_parts = []
    for key, value in search_results.items():
        if isinstance(value, dict):
            response_parts.append(f"**{key}:**")
            for sub_key, sub_value in value.items():
                response_parts.append(f"  • {sub_key}: {sub_value}")
        else:
            response_parts.append(f"**{key}:** {value}")
    return "\n".join(response_parts)

# Simple in-memory context store for short follow-ups (rank/gender/category)
context_store = {}
CONTEXT_TTL = 5 * 60  # 5 minutes

def cleanup_context():
    now = time.time()
    keys_to_delete = [k for k, v in context_store.items() if now - v.get('timestamp', 0) > CONTEXT_TTL]
    for k in keys_to_delete:
        del context_store[k]

def get_client_key():
    # Prefer an explicit header (frontend can set X-Client-Id), otherwise fallback to IP
    return request.headers.get('X-Client-Id') or request.remote_addr

@app.route('/chat', methods=['POST'])
def chat():
    cleanup_context()
    try:
        data = request.json
        user_query = data.get('message', '').strip()
        if not user_query:
            return jsonify({"reply": "Please ask a question!"}), 400

        client_key = get_client_key()
        # If there's a pending eligibility context, try to merge short follow-ups
        pending = context_store.get(client_key)
        if pending:
            # If user replies with just a number, treat as rank
            if re.fullmatch(r'\d{3,6}', user_query):
                reconstructed = pending['original_query'] + f" rank {user_query}"
                user_query = reconstructed
                del context_store[client_key]
            # If user replies with gender or close misspellings, attach gender
            elif re.search(r'\b(girl|gril|girls|female|female student|gir)\b', user_query.lower()):
                reconstructed = pending['original_query'] + " girl"
                user_query = reconstructed
                del context_store[client_key]
            elif re.search(r'\b(boy|boys|male|men)\b', user_query.lower()):
                reconstructed = pending['original_query'] + " boy"
                user_query = reconstructed
                del context_store[client_key]
            # If user replies with a category like "BC_A" or "BC-A" etc., attach it
            elif re.search(r'\b(bc[-_\s]?[abcde]|oc|ews|sc|st)\b', user_query.lower()):
                reconstructed = pending['original_query'] + " " + user_query
                user_query = reconstructed
                del context_store[client_key]
            # Otherwise, leave as-is (normal query)

        # Check if it's a greeting or conversational query
        is_conv, greeting_response = is_greeting(user_query)
        if is_conv:
            return jsonify({"reply": greeting_response, "category": "conversational"})

        # Step 1: Extract keywords and intent using Gemini (or fallback)
        extracted_info = extract_keywords_and_intent(user_query)

        # Step 2: Search college database
        search_results = search_college_data(extracted_info, user_query)

        # If eligibility path returned missing fields, save context and ask user plainly
        if 'eligibility_missing' in search_results and search_results.get('eligibility_missing'):
            # Save pending context to allow short follow-ups (rank / gender / category)
            context_store[client_key] = {
                'timestamp': time.time(),
                'original_query': user_query,
                'missing': search_results['eligibility_missing'],
                'extracted_info': search_results.get('eligibility_info', {})
            }
            reply = search_results['eligibility_response']
            return jsonify({
                "reply": reply,
                "category": "eligibility",
                "debug": extracted_info
            })

        # Step 3: Format response using AI (or fallback)
        reply = format_response_with_ai(search_results, user_query, extracted_info.get('intent'))

        # If this was a full eligibility answer, clear any related pending context
        if 'eligibility_response' in search_results:
            if client_key in context_store:
                del context_store[client_key]

        return jsonify({
            "reply": reply,
            "category": extracted_info.get('category'),
            "debug": extracted_info
        })

    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({
            "reply": "I apologize, but I encountered an error. Please try rephrasing your question."
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "message": "Lendi Institute College Bot is running",
        "college": "Lendi Institute of Engineering & Technology"
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)