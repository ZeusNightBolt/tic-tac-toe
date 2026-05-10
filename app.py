import streamlit as st
import random
import time

# ── MUST be first Streamlit command ──
st.set_page_config(
    page_title="Tic Tac Toe",
    page_icon="◼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Minimal CSS: board grid + card treatment only ──
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .board {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 2px;
        background: #2A2A2A;
        border: 2px solid #2A2A2A;
        border-radius: 8px;
        overflow: hidden;
        max-width: 360px;
        margin: 0 auto;
    }
    .cell {
        aspect-ratio: 1;
        background: #141414;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        font-weight: 700;
        transition: background 150ms;
        cursor: pointer;
    }
    .cell:hover {
        background: #1A1A1A;
    }
    .cell.x { color: #C96442; }
    .cell.o { color: #00D4AA; }
    .cell.win { background: #1A2A1A; }

    .score-card {
        background: #141414;
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
    }
    .score-card h3 {
        font-size: 0.85rem;
        color: #87867F;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0;
    }
    .score-card .value {
        font-size: 2.5rem;
        font-weight: 700;
        font-variant-numeric: tabular-nums;
    }

    ::-webkit-scrollbar {width: 6px;}
    ::-webkit-scrollbar-track {background: #0D0D0D;}
    ::-webkit-scrollbar-thumb {background: #2A2A2A; border-radius: 3px;}
</style>
""", unsafe_allow_html=True)

# ── Game Logic ──

def check_winner(board):
    """Return 'X', 'O', 'tie', or None."""
    lines = [
        # rows
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        # cols
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        # diags
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)],
    ]
    for line in lines:
        a, b, c = line
        if board[a[0]][a[1]] == board[b[0]][b[1]] == board[c[0]][c[1]] != "":
            return board[a[0]][a[1]], line
    if all(board[r][c] != "" for r in range(3) for c in range(3)):
        return "tie", []
    return None, []

def minimax(board, is_maximizing, alpha=-float("inf"), beta=float("inf")):
    """Minimax with alpha-beta pruning. AI is 'O' (maximizing)."""
    winner, _ = check_winner(board)
    if winner == "O": return 10 - count_empty(board)
    if winner == "X": return count_empty(board) - 10
    if winner == "tie": return 0

    if is_maximizing:
        best = -float("inf")
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "O"
                    score = minimax(board, False, alpha, beta)
                    board[r][c] = ""
                    best = max(best, score)
                    alpha = max(alpha, score)
                    if beta <= alpha: break
        return best
    else:
        best = float("inf")
        for r in range(3):
            for c in range(3):
                if board[r][c] == "":
                    board[r][c] = "X"
                    score = minimax(board, True, alpha, beta)
                    board[r][c] = ""
                    best = min(best, score)
                    beta = min(beta, score)
                    if beta <= alpha: break
        return best

def count_empty(board):
    return sum(1 for r in range(3) for c in range(3) if board[r][c] == "")

def ai_move(board):
    """AI ('O') picks best move via minimax. First move is random for variety."""
    empty = [(r,c) for r in range(3) for c in range(3) if board[r][c] == ""]
    if not empty: return None
    if len(empty) == 9:
        return random.choice([(0,0), (0,2), (1,1), (2,0), (2,2)])
    best_score = -float("inf")
    best_move = empty[0]
    for r, c in empty:
        board[r][c] = "O"
        score = minimax(board, False)
        board[r][c] = ""
        if score > best_score:
            best_score = score
            best_move = (r, c)
    return best_move

# ── Init State ──

def init_game():
    st.session_state.board = [["", "", ""] for _ in range(3)]
    st.session_state.turn = "X"
    st.session_state.winner = None
    st.session_state.win_line = []
    st.session_state.game_over = False
    if "x_wins" not in st.session_state:
        st.session_state.x_wins = 0
    if "o_wins" not in st.session_state:
        st.session_state.o_wins = 0
    if "ties" not in st.session_state:
        st.session_state.ties = 0

if "board" not in st.session_state:
    init_game()

# ── Mode Selector ──

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    mode = st.radio("Mode", ["vs AI (Minimax)", "2 Players"], horizontal=True, label_visibility="collapsed")
    vs_ai = mode.startswith("vs")

# ── Scoreboard ──

sc1, sc2, sc3 = st.columns(3)
with sc1:
    st.markdown(f"""<div class="score-card"><h3>X {'(You)' if vs_ai else ''}</h3><div class="value" style="color:#C96442">{st.session_state.x_wins}</div></div>""", unsafe_allow_html=True)
with sc2:
    st.markdown(f"""<div class="score-card"><h3>Ties</h3><div class="value" style="color:#87867F">{st.session_state.ties}</div></div>""", unsafe_allow_html=True)
with sc3:
    st.markdown(f"""<div class="score-card"><h3>O {'(AI)' if vs_ai else ''}</h3><div class="value" style="color:#00D4AA">{st.session_state.o_wins}</div></div>""", unsafe_allow_html=True)

# ── Status ──

st.markdown("<br>", unsafe_allow_html=True)
if st.session_state.game_over:
    if st.session_state.winner == "tie":
        st.markdown("<p style='text-align:center;color:#87867F;font-size:1.1rem'>It's a tie.</p>", unsafe_allow_html=True)
    elif st.session_state.winner:
        color = "#C96442" if st.session_state.winner == "X" else "#00D4AA"
        name = "You" if (st.session_state.winner == "X" and vs_ai) else ("AI" if st.session_state.winner == "O" and vs_ai else st.session_state.winner)
        st.markdown(f"<p style='text-align:center;color:{color};font-size:1.3rem;font-weight:700'>{name} won</p>", unsafe_allow_html=True)
else:
    turn_name = "Your turn" if (st.session_state.turn == "X" or not vs_ai) else "AI is thinking..."
    st.markdown(f"<p style='text-align:center;color:#B0AEA5;font-size:1.1rem'>{turn_name}</p>", unsafe_allow_html=True)

# ── Board ──

st.markdown("<div class='board'>", unsafe_allow_html=True)

for r in range(3):
    for c in range(3):
        cell = st.session_state.board[r][c]
        win = (r, c) in st.session_state.win_line
        cls = f"cell {'x' if cell == 'X' else 'o' if cell == 'O' else ''} {'win' if win else ''}"
        display = cell if cell else " "
        st.markdown(f"<div class='{cls}'>{display}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── Click Buttons ──

st.markdown("<br>", unsafe_allow_html=True)
if not st.session_state.game_over:
    cols = st.columns(3)
    for i, (r, c) in enumerate([(r,c) for r in range(3) for c in range(3)]):
        with cols[i % 3]:
            cell_val = st.session_state.board[r][c]
            disabled = cell_val != "" or (vs_ai and st.session_state.turn == "O")
            label = cell_val if cell_val else "·"
            if st.button(label, key=f"cell_{r}_{c}", disabled=disabled, use_container_width=True):
                # Player X move
                st.session_state.board[r][c] = "X"
                winner, win_line = check_winner(st.session_state.board)
                if winner:
                    st.session_state.winner = winner
                    st.session_state.win_line = win_line
                    st.session_state.game_over = True
                    if winner == "X":
                        st.session_state.x_wins += 1
                    elif winner == "tie":
                        st.session_state.ties += 1
                else:
                    st.session_state.turn = "O"
                st.rerun()

# ── AI Move ──

if vs_ai and st.session_state.turn == "O" and not st.session_state.game_over:
    time.sleep(0.4)  # Brief think pause — human feel
    move = ai_move(st.session_state.board)
    if move:
        r, c = move
        st.session_state.board[r][c] = "O"
        winner, win_line = check_winner(st.session_state.board)
        if winner:
            st.session_state.winner = winner
            st.session_state.win_line = win_line
            st.session_state.game_over = True
            if winner == "O":
                st.session_state.o_wins += 1
            elif winner == "tie":
                st.session_state.ties += 1
        else:
            st.session_state.turn = "X"
        st.rerun()

# ── Controls ──

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    if st.button("New Game", use_container_width=True):
        # Track the current winner before resetting
        if st.session_state.game_over and st.session_state.winner not in (None, "tie"):
            pass  # already counted above
        init_game()
        st.rerun()

st.markdown("<p style='text-align:center;color:#87867F;font-size:0.75rem;margin-top:2rem'>AI uses minimax with alpha-beta pruning — unbeatable in theory. First move is randomized for variety.</p>", unsafe_allow_html=True)
