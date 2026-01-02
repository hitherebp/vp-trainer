import streamlit as st
import random
from collections import Counter

# --- PAGE SETUP ---
st.set_page_config(page_title="VP Mobile Trainer", layout="centered")

# --- CSS STYLING ---
st.markdown("""
<style>
    /* Card Styling */
    .card {
        background-color: white;
        border: 2px solid #333;
        border-radius: 8px;
        padding: 5px;
        width: 100%; /* Fill column */
        aspect-ratio: 2/3;
        text-align: center;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        font-size: 20px;
        font-weight: bold;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }
    .card-red { color: #D32F2F; border-color: #D32F2F; }
    .card-black { color: #212121; border-color: #212121; }
    .suit { font-size: 28px; display: block; margin-top: 0px; }
    
    /* Mobile Button Styling */
    div.stButton > button {
        width: 100%;
        padding: 10px 0px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- STRATEGY LOGIC (The Brain) ---
def get_strategy_holds(hand):
    ranks = sorted([c[0] for c in hand]); suits = [c[1] for c in hand]; counts = Counter(ranks)
    is_flush = len(set(suits)) == 1
    is_str = (ranks[-1]-ranks[0]==4 and len(set(ranks))==5) or (ranks==[2,3,4,5,14])
    high = [i for i,c in enumerate(hand) if c[0]>=11]
    
    # Logic Helpers
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

    # 16-Point Priority List
    if 4 in counts.values(): return [i for i,c in enumerate(hand) if c[0]==[k for k,v in counts.items() if v==4][0]], "Four of a Kind"
    if is_flush and is_str: return [0,1,2,3,4], "Straight Flush"
    if is_n_royal(4): return is_n_royal(4), "4 to a Royal Flush"
    if (3 in counts.values() and 2 in counts.values()) or is_flush or is_str: return [0,1,2,3,4], "Pat Hand"
    if 3 in counts.values(): return [i for i,c in enumerate(hand) if c[0]==[k for k,v in counts.items() if v==3][0]], "Three of a Kind"
    if is_n_sf(4): return is_n_sf(4), "4 to a Straight Flush"
    if list(counts.values()).count(2)==2: return [i for i,c in enumerate(hand) if c[0] in [k for k,v in counts.items() if v==2]], "Two Pair"
    for r in counts: 
        if counts[r]==2 and r>=11: return [i for i,c in enumerate(hand) if c[0]==r], "High Pair (Jacks+)"
    if is_n_royal(3): return is_n_royal(3), "3 to a Royal Flush"
    for s in ['H','D','C','S']: 
        if suits.count(s)==4: return [i for i,c in enumerate(hand) if c[1]==s], "4 to a Flush"
    for r in counts:
        if counts[r]==2 and r<=10: return [i for i,c in enumerate(hand) if c[0]==r], "Low Pair"
    for i in range(len(ranks)-3):
        if ranks[i+3]-ranks[i]==3 and len(set(ranks[i:i+4]))==4: return [idx for idx,c in enumerate(hand) if c[0] in ranks[i:i+4]], "4 to Outside Straight"
    if len(high)>=2:
        for i in range(len(high)):
            for j in range(i+1, len(high)):
                if hand[high[i]][1] == hand[high[j]][1]: return [high[i], high[j]], "2 Suited High Cards"
    if is_n_sf(3): return is_n_sf(3), "3 to a Straight Flush"
    if len(high)>=2: 
        s_high = sorted([(i, hand[i][0]) for i in high], key=lambda x:x[1])
        return [s_high[0][0], s_high[1][0]], "2 Unsuited High Cards (Lowest)"
    ten = [i for i,c in enumerate(hand) if c[0]==10]
    for t in ten:
        for i,c in enumerate(hand):
            if c[0]>=11 and c[1]==hand[t][1]: return sorted([t, i]), "Suited 10 with J/Q/K"
    if high: return [sorted([(i, hand[i][0]) for i in high], key=lambda x:x[0])[0][0]], "One High Card"
    
    return [], "Discard Everything"

# --- GAME HELPERS ---

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
        <div>{display_rank}</div>
        <div class="suit">{display_suit}</div>
    </div>
    """

# --- SESSION STATE ---
if 'deck' not in st.session_state:
    st.session_state.deck = create_deck()
if 'hand' not in st.session_state:
    st.session_state.hand = []
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'DEAL' # DEAL, CHECK, RESULT
if 'streak' not in st.session_state:
    st.session_state.streak = 0
if 'feedback' not in st.session_state:
    st.session_state.feedback = ""
if 'holds' not in st.session_state:
    st.session_state.holds = [False] * 5

# --- CALLBACK FUNCTIONS (The fix for resets) ---

def start_new_hand():
    # 1. Logic for dealing
    random.shuffle(st.session_state.deck)
    st.session_state.hand = st.session_state.deck[:5]
    st.session_state.game_state = 'CHECK'
    st.session_state.feedback = ""
    # 2. Logic for clearing buttons
    st.session_state.holds = [False] * 5

def toggle_hold(i):
    st.session_state.holds[i] = not st.session_state.holds[i]

def check_answer():
    user_indices = [i for i, h in enumerate(st.session_state.holds) if h]
    correct_indices, reason = get_strategy_holds(st.session_state.hand)
    
    if set(user_indices) == set(correct_indices):
        st.session_state.streak += 1
        st.session_state.feedback = f"✅ **Correct!** ({reason})"
    else:
        st.session_state.streak = 0
        st.session_state.feedback = f"❌ **Incorrect.** The best play was: **{reason}**"
    
    st.session_state.game_state = 'RESULT'

# --- MAIN APP UI ---

st.title("📱 VP Trainer")
st.caption("9/6 Jacks or Better • Simple Strategy")

# Streak Counter
st.metric("Streak", st.session_state.streak)

# Initialize first hand
if not st.session_state.hand:
    start_new_hand()

# CARD DISPLAY (Mobile Friendly)
cols = st.columns(5)
for i, card in enumerate(st.session_state.hand):
    with cols[i]:
        # 1. Render Card
        st.markdown(render_card_html(card[0], card[1]), unsafe_allow_html=True)
        
        # 2. Render Button (Toggle)
        # We disable buttons if we are in the 'RESULT' phase so user can't change answer
        btn_disabled = (st.session_state.game_state == 'RESULT')
        
        label = "🛑 HELD" if st.session_state.holds[i] else "HOLD"
        type_btn = "primary" if st.session_state.holds[i] else "secondary"
        
        st.button(label, key=f"btn_{i}", type=type_btn, 
                  on_click=toggle_hold, args=(i,), 
                  disabled=btn_disabled)

st.markdown("---")

# ACTION BUTTONS
if st.session_state.game_state == 'CHECK':
    st.button("Check Hand", type="primary", use_container_width=True, on_click=check_answer)

elif st.session_state.game_state == 'RESULT':
    st.markdown(st.session_state.feedback)
    
    # Show correction visualization if wrong
    correct_indices, _ = get_strategy_holds(st.session_state.hand)
    user_indices = [i for i, h in enumerate(st.session_state.holds) if h]
    
    if set(user_indices) != set(correct_indices):
        c1, c2 = st.columns(2)
        c1.warning("You Held")
        c1.write([f"Card {i+1}" for i in user_indices] if user_indices else "Nothing")
        c2.success("Best Play")
        c2.write([f"Card {i+1}" for i in correct_indices] if correct_indices else "Discard All")
        
    st.markdown("---")
    # This button triggers the safe reset callback
    st.button("Deal Next Hand", type="primary", use_container_width=True, on_click=start_new_hand)