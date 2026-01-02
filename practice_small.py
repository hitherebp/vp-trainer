import streamlit as st
import random
from collections import Counter

# --- PAGE CONFIG (Compact) ---
st.set_page_config(page_title="VP Trainer", layout="centered")

# --- CSS FOR COMPACT LAYOUT ---
st.markdown("""
<style>
    /* 1. REMOVE STREAMLIT PADDING (Crucial for mobile) */
    div.block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 0.5rem;
        padding-right: 0.5rem;
    }
    
    /* 2. COMPACT CARD STYLE */
    .card {
        background-color: white;
        border: 2px solid #333;
        border-radius: 6px;
        width: 100%;
        /* Narrower aspect ratio for portrait */
        aspect-ratio: 0.6; 
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.2);
        margin-bottom: 2px; /* Pull button closer */
        line-height: 1.1;
    }
    .card-rank { font-size: 18px; font-weight: bold; }
    .card-suit { font-size: 24px; }
    
    .card-red { color: #D32F2F; border-color: #D32F2F; }
    .card-black { color: #212121; border-color: #212121; }

    /* 3. COMPACT BUTTONS */
    div.stButton > button {
        width: 100%;
        padding: 0px !important;
        height: 40px; /* Shorter buttons */
        font-size: 14px;
        margin-top: 0px;
    }
    
    /* 4. TIGHTEN COLUMNS */
    div[data-testid="column"] {
        padding: 0px 2px; /* Less space between columns */
    }
    
    /* Hide the 'made with streamlit' footer to save space */
    footer {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- LOGIC (Standard) ---
def get_strategy_holds(hand):
    ranks = sorted([c[0] for c in hand]); suits = [c[1] for c in hand]; counts = Counter(ranks)
    is_flush = len(set(suits)) == 1
    is_str = (ranks[-1]-ranks[0]==4 and len(set(ranks))==5) or (ranks==[2,3,4,5,14])
    high = [i for i,c in enumerate(hand) if c[0]>=11]
    def is_n_royal(n):
        target={10,11,12,13,14}
        for s in ['H','D','C','S']:
            if suits.count(s)>=n:
                suited=[i for i,c in enumerate(hand) if c[1]==s]
                if len([i for i in suited if hand[i][0] in target])>=n: return [i for i in suited if hand[i][0] in target]
        return None
    def is_n_sf(n):
        for s in ['H','D','C','S']:
            if suits.count(s)>=n:
                idx=[i for i,c in enumerate(hand) if c[1]==s]; r=sorted([hand[i][0] for i in idx])
                if (r[-1]-r[0]<=4 and len(set(r))==n) or (14 in r and sorted([x if x!=14 else 1 for x in r])[-1]-sorted([x if x!=14 else 1 for x in r])[0]<=4): return idx
        return None

    if 4 in counts.values(): return [i for i,c in enumerate(hand) if c[0]==[k for k,v in counts.items() if v==4][0]], "Four of a Kind"
    if is_flush and is_str: return [0,1,2,3,4], "Straight Flush"
    if is_n_royal(4): return is_n_royal(4), "4 to Royal"
    if (3 in counts.values() and 2 in counts.values()) or is_flush or is_str: return [0,1,2,3,4], "Pat Hand"
    if 3 in counts.values(): return [i for i,c in enumerate(hand) if c[0]==[k for k,v in counts.items() if v==3][0]], "Three of a Kind"
    if is_n_sf(4): return is_n_sf(4), "4 to Str. Flush"
    if list(counts.values()).count(2)==2: return [i for i,c in enumerate(hand) if c[0] in [k for k,v in counts.items() if v==2]], "Two Pair"
    for r in counts: 
        if counts[r]==2 and r>=11: return [i for i,c in enumerate(hand) if c[0]==r], "High Pair"
    if is_n_royal(3): return is_n_royal(3), "3 to Royal"
    for s in ['H','D','C','S']: 
        if suits.count(s)==4: return [i for i,c in enumerate(hand) if c[1]==s], "4 to Flush"
    for r in counts:
        if counts[r]==2 and r<=10: return [i for i,c in enumerate(hand) if c[0]==r], "Low Pair"
    for i in range(len(ranks)-3):
        if ranks[i+3]-ranks[i]==3 and len(set(ranks[i:i+4]))==4: return [idx for idx,c in enumerate(hand) if c[0] in ranks[i:i+4]], "4 to Outside Str."
    if len(high)>=2:
        for i in range(len(high)):
            for j in range(i+1, len(high)):
                if hand[high[i]][1] == hand[high[j]][1]: return [high[i], high[j]], "2 Suited High"
    if is_n_sf(3): return is_n_sf(3), "3 to Str. Flush"
    if len(high)>=2: 
        s_high = sorted([(i, hand[i][0]) for i in high], key=lambda x:x[1])
        return [s_high[0][0], s_high[1][0]], "2 Unsuited High"
    ten = [i for i,c in enumerate(hand) if c[0]==10]
    for t in ten:
        for i,c in enumerate(hand):
            if c[0]>=11 and c[1]==hand[t][1]: return sorted([t, i]), "Suited 10+Face"
    if high: return [sorted([(i, hand[i][0]) for i in high], key=lambda x:x[0])[0][0]], "High Card"
    return [], "Discard All"

# --- HELPERS ---
def create_deck():
    return [(r, s) for r in range(2, 15) for s in ['H', 'D', 'C', 'S']]

def render_card_html(rank_val, suit_char):
    suit_map = {'H': '♥', 'D': '♦', 'C': '♣', 'S': '♠'}
    rank_map = {11: 'J', 12: 'Q', 13: 'K', 14: 'A'}
    display_rank = rank_map.get(rank_val, str(rank_val))
    display_suit = suit_map[suit_char]
    css_class = "card-red" if suit_char in ['H', 'D'] else "card-black"
    return f"""
    <div class="card {css_class}">
        <div class="card-rank">{display_rank}</div>
        <div class="card-suit">{display_suit}</div>
    </div>
    """

# --- SESSION ---
if 'deck' not in st.session_state: st.session_state.deck = create_deck()
if 'hand' not in st.session_state: st.session_state.hand = []
if 'game_state' not in st.session_state: st.session_state.game_state = 'DEAL'
if 'streak' not in st.session_state: st.session_state.streak = 0
if 'feedback' not in st.session_state: st.session_state.feedback = ""
if 'holds' not in st.session_state: st.session_state.holds = [False]*5

# --- CALLBACKS ---
def start_new_hand():
    random.shuffle(st.session_state.deck)
    st.session_state.hand = st.session_state.deck[:5]
    st.session_state.game_state = 'CHECK'
    st.session_state.feedback = ""
    st.session_state.holds = [False]*5

def toggle_hold(i):
    st.session_state.holds[i] = not st.session_state.holds[i]

def check_answer():
    user = [i for i, h in enumerate(st.session_state.holds) if h]
    correct, reason = get_strategy_holds(st.session_state.hand)
    if set(user) == set(correct):
        st.session_state.streak += 1
        st.session_state.feedback = f"✅ **Correct!** ({reason})"
    else:
        st.session_state.streak = 0
        st.session_state.feedback = f"❌ **Best Play:** {reason}"
    st.session_state.game_state = 'RESULT'

# --- UI RENDER ---

# 1. Header (Compact)
# Using columns to put title and streak side-by-side to save vertical space
top_c1, top_c2 = st.columns([3, 1])
top_c1.subheader("VP Trainer")
top_c2.metric("Streak", st.session_state.streak, label_visibility="collapsed") # Hidden label saves space

if not st.session_state.hand: start_new_hand()

# 2. Cards (Gap='small' pulls columns tighter)
cols = st.columns(5, gap="small")
for i, card in enumerate(st.session_state.hand):
    with cols[i]:
        st.markdown(render_card_html(card[0], card[1]), unsafe_allow_html=True)
        
        btn_disabled = (st.session_state.game_state == 'RESULT')
        label = "HELD" if st.session_state.holds[i] else "HOLD"
        type_btn = "primary" if st.session_state.holds[i] else "secondary"
        
        st.button(label, key=f"btn_{i}", type=type_btn, 
                  on_click=toggle_hold, args=(i,), 
                  disabled=btn_disabled, use_container_width=True)

# 3. Action Area
# Add a little spacing
st.write("") 

if st.session_state.game_state == 'CHECK':
    st.button("CHECK HAND", type="primary", use_container_width=True, on_click=check_answer)

elif st.session_state.game_state == 'RESULT':
    # Compact Feedback
    st.info(st.session_state.feedback)
    
    # Only show detailed correction if wrong
    correct, _ = get_strategy_holds(st.session_state.hand)
    user = [i for i, h in enumerate(st.session_state.holds) if h]
    
    if set(user) != set(correct):
        c1, c2 = st.columns(2)
        c1.caption(f"You: {[f'Card {i+1}' for i in user] if user else 'None'}")
        c2.caption(f"Best: {[f'Card {i+1}' for i in correct] if correct else 'None'}")
        
    st.button("NEXT HAND", type="primary", use_container_width=True, on_click=start_new_hand)