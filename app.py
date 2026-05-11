import streamlit as st
import random
import time

st.set_page_config(
    page_title="Tic Tac Toe",
    page_icon="◼",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS: Scale cells from viewport — width AND height ──
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}

    /* ── Container: tight, no fixed height ── */
    section.main > div.block-container {
        max-width: 480px !important;
        padding: 8px 16px 8px 16px !important;
    }

    /* ── Force 3-column grid, never stack ── */
    div[data-testid="stHorizontalBlock"] {
        flex-wrap: nowrap !important;
        gap: 4px !important;
    }
    div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0 !important;
    }

    /* ── Cell buttons: scale to fit viewport ──
       Cell width  = (viewport - 40px padding) / 3
       Cell height = (viewport height - 280px chrome) / 4  (header+scores+status+controls+board)
       Pick the SMALLER so cells always fit without scrolling */
    div[data-testid="stHorizontalBlock"] button {
        width: 100% !important;
        height: min(
            calc((100vw - 40px) / 3),
            calc((100dvh - 260px) / 4)
        ) !important;
        font-size: min(2.2rem, 7vw, calc((100dvh - 260px) / 8)) !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        border: 1px solid #2A2A2A !important;
        background: #141414 !important;
        color: #FAF9F5 !important;
        padding: 0 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 44px !important;
        min-width: 44px !important;
        -webkit-tap-highlight-color: transparent;
        touch-action: manipulation;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        background: #1A1A1A !important;
        border-color: #3A3A3A !important;
    }
    div[data-testid="stHorizontalBlock"] button:disabled {
        color: #FAF9F5 !important;
        opacity: 1 !important;
    }

    /* ── Compact typography ── */
    h1 {
        font-size: min(1.5rem, 5.5vw) !important;
        margin: 0 0 2px 0 !important;
        padding: 0 !important;
    }
    h4, h5 {
        font-size: min(1rem, 4vw) !important;
        margin: 4px 0 !important;
    }
    .stCaptionContainer, .stCaptionContainer p {
        font-size: 0.7rem !important;
        margin: 1px 0 !important;
    }

    /* ── Metrics: compact ── */
    div[data-testid="stMetric"] { padding: 4px 0 !important; }
    div[data-testid="stMetric"] label { font-size: 0.6rem !important; }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-size: min(1.3rem, 4.5vw) !important;
    }

    /* ── Radio: compact ── */
    div[data-testid="stHorizontalBlock"] label {
        font-size: 0.8rem !important;
        padding: 2px 6px !important;
    }

    /* ── New Game button ── */
    button[kind="secondary"] {
        background: #141414 !important;
        border: 1px solid #2A2A2A !important;
        color: #87867F !important;
        min-height: 44px !important;
        touch-action: manipulation;
        font-size: 0.85rem !important;
    }

    /* ── Trim Streamlit gaps ── */
    div[data-testid="stVerticalBlock"] { gap: 3px !important; }
    .stMarkdown { margin: 1px 0 !important; }
    div.block-container { gap: 4px !important; }

    /* ── Safari ── */
    body { overscroll-behavior: contain; }
    @supports (-webkit-touch-callout: none) {
        .stApp { min-height: -webkit-fill-available; }
    }

    ::-webkit-scrollbar {width: 4px;}
    ::-webkit-scrollbar-track {background: #0D0D0D;}
    ::-webkit-scrollbar-thumb {background: #2A2A2A; border-radius: 2px;}
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

# ── Layout ──

st.title("Tic Tac Toe")
st.caption("Minimax AI")

mode = st.radio("", ["vs AI", "2 Players"], horizontal=True, label_visibility="collapsed", key="mode")
vs_ai = mode == "vs AI"

sc1, sc2, sc3 = st.columns(3)
sc1.metric("X", st.session_state.x_wins)
sc2.metric("Ties", st.session_state.ties)
sc3.metric("O", st.session_state.o_wins)

if st.session_state.game_over:
    w = st.session_state.winner
    if w == "tie":
        st.markdown("#### Tie")
    else:
        name = "You win" if (w == "X" and vs_ai) else ("AI wins" if w == "O" and vs_ai else f"{w} wins")
        st.markdown(f"#### {name}")
else:
    label = "Your turn" if (st.session_state.turn == "X" or not vs_ai) else "..."
    st.markdown(f"#### {label}")

# ── Board ──
for r in range(3):
    cols = st.columns(3, gap="small")
    for c in range(3):
        cell = st.session_state.board[r][c]
        disabled = cell != "" or st.session_state.game_over or (vs_ai and st.session_state.turn == "O")
        with cols[c]:
            if cell == "X":
                st.markdown(
                    '<div style="width:100%;'
                    'height:min(calc((100vw - 40px)/3), calc((100dvh - 260px)/4));'
                    'display:flex;align-items:center;justify-content:center;'
                    'font-size:min(2.2rem,7vw,calc((100dvh - 260px)/8));'
                    'font-weight:700;color:#C96442;background:#141414;'
                    'border:1px solid #2A2A2A;border-radius:6px">X</div>',
                    unsafe_allow_html=True)
            elif cell == "O":
                st.markdown(
                    '<div style="width:100%;'
                    'height:min(calc((100vw - 40px)/3), calc((100dvh - 260px)/4));'
                    'display:flex;align-items:center;justify-content:center;'
                    'font-size:min(2.2rem,7vw,calc((100dvh - 260px)/8));'
                    'font-weight:700;color:#00D4AA;background:#141414;'
                    'border:1px solid #2A2A2A;border-radius:6px">O</div>',
                    unsafe_allow_html=True)
            else:
                if st.button("", key=f"b{r}{c}", disabled=disabled, use_container_width=True):
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

if vs_ai and st.session_state.turn == "O" and not st.session_state.game_over:
    time.sleep(0.3)
    move = ai_move(st.session_state.board)
    if move is not None:
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

if st.button("New Game", use_container_width=True):
    init_game()
    st.rerun()
