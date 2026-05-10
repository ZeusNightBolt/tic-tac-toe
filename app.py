import streamlit as st
import random
import time

# ── MUST be first Streamlit command ──
st.set_page_config(
    page_title="Tic Tac Toe",
    page_icon="◼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Minimal CSS: board styling only ──
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Board container */
    .stMainBlockContainer {max-width: 420px !important;}

    /* Cell buttons — tile style */
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        height: 96px !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        border: 1px solid #2A2A2A !important;
        background: #141414 !important;
        color: #FAF9F5 !important;
        transition: background 150ms !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button:hover {
        background: #1A1A1A !important;
        border-color: #3A3A3A !important;
    }
    div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] button:disabled {
        color: #FAF9F5 !important;
        opacity: 1 !important;
    }

    /* New Game button — subtle */
    button[kind="secondary"] {
        background: #141414 !important;
        border: 1px solid #2A2A2A !important;
        color: #87867F !important;
    }

    /* Score cards */
    .score-card {
        background: #141414;
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        padding: 16px 8px;
        text-align: center;
    }
    div[data-testid="stMetric"] { background: transparent !important; }

    ::-webkit-scrollbar {width: 6px;}
    ::-webkit-scrollbar-track {background: #0D0D0D;}
    ::-webkit-scrollbar-thumb {background: #2A2A2A; border-radius: 3px;}
</style>
""", unsafe_allow_html=True)

# ── Game Logic ──

def check_winner(board):
    lines = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
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
    winner, _ = check_winner(board)
    if winner == "O": return 10
    if winner == "X": return -10
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

def ai_move(board):
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
    for k in ("x_wins", "o_wins", "ties"):
        if k not in st.session_state:
            st.session_state[k] = 0

if "board" not in st.session_state:
    init_game()

# ── Header ──

st.title("Tic Tac Toe")
st.caption("Minimax AI with alpha-beta pruning")

# ── Mode + Score ──

mode = st.radio("Mode", ["vs AI", "2 Players"], horizontal=True, label_visibility="collapsed")
vs_ai = mode == "vs AI"

sc1, sc2, sc3 = st.columns(3)
sc1.metric("X", st.session_state.x_wins)
sc2.metric("Ties", st.session_state.ties)
sc3.metric("O", st.session_state.o_wins)

# ── Status ──

if st.session_state.game_over:
    w = st.session_state.winner
    if w == "tie":
        st.markdown("##### It's a tie")
    else:
        name = "You win" if (w == "X" and vs_ai) else ("AI wins" if w == "O" and vs_ai else f"{w} wins")
        st.markdown(f"##### {name}")
else:
    label = "Your turn" if (st.session_state.turn == "X" or not vs_ai) else "..."
    st.markdown(f"##### {label}")

# ── Board (3 rows × 3 cols) ──

for r in range(3):
    cols = st.columns(3, gap="small")
    for c in range(3):
        cell = st.session_state.board[r][c]
        win = (r, c) in st.session_state.win_line
        with cols[c]:
            label = cell if cell else " "
            disabled = cell != "" or st.session_state.game_over or (vs_ai and st.session_state.turn == "O")
            # Style: X in terracotta, O in cyan
            if cell == "X":
                st.markdown(f"<div class='cell-x' style='width:100%;height:96px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;font-weight:700;color:#C96442;background:#141414;border:1px solid #2A2A2A;border-radius:6px'>{cell}</div>", unsafe_allow_html=True)
            elif cell == "O":
                st.markdown(f"<div class='cell-o' style='width:100%;height:96px;display:flex;align-items:center;justify-content:center;font-size:2.2rem;font-weight:700;color:#00D4AA;background:#141414;border:1px solid #2A2A2A;border-radius:6px'>{cell}</div>", unsafe_allow_html=True)
            else:
                if st.button(" ", key=f"b{r}{c}", disabled=disabled, use_container_width=True):
                    st.session_state.board[r][c] = "X"
                    winner, win_line = check_winner(st.session_state.board)
                    if winner:
                        st.session_state.winner = winner
                        st.session_state.win_line = win_line
                        st.session_state.game_over = True
                        if winner == "X": st.session_state.x_wins += 1
                        elif winner == "tie": st.session_state.ties += 1
                    else:
                        st.session_state.turn = "O"
                    st.rerun()

# ── AI Move ──

if vs_ai and st.session_state.turn == "O" and not st.session_state.game_over:
    time.sleep(0.3)
    move = ai_move(st.session_state.board)
    if move:
        r, c = move
        st.session_state.board[r][c] = "O"
        winner, win_line = check_winner(st.session_state.board)
        if winner:
            st.session_state.winner = winner
            st.session_state.win_line = win_line
            st.session_state.game_over = True
            if winner == "O": st.session_state.o_wins += 1
            elif winner == "tie": st.session_state.ties += 1
        else:
            st.session_state.turn = "X"
        st.rerun()

# ── Controls ──

if st.button("New Game", use_container_width=True):
    init_game()
    st.rerun()

st.caption("Unbeatable minimax AI • First move randomized for variety")
