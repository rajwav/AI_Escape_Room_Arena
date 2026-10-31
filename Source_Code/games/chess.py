"""
AI ESCAPE ROOM ARENA — Quantum Chess Module (Clickable Board & Automatic Adversarial AI)
Features:
- Large Centered 8x8 Chessboard (Responsive 560-640px square presentation)
- 100% Direct Click Interaction (Select piece ➔ View legal move dots ➔ Execute move)
- Automatic Adversarial Black AI Response (Evaluates all legal moves, material, center control)
- Real Search Telemetry Panel (Branches evaluated, search depth, evaluation score, rationale)
- Captured Pieces Trays & Check / Checkmate Detection
- 2-Player Local (Pass & Play) and Human vs AI Adversarial Modes
"""

import streamlit as st
import time
import os
import sys

src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from chess_engine import ChessEngine
from scoring_engine import ScoringEngine


def render_chess_game():
    """Renders the Large 8x8 Clickable Chessboard & AI Adversarial Arena."""
    st.markdown("""
<div class="hud-card">
<div class="card-title">♟️ QUANTUM CHESS: STATE-SPACE ADVERSARIAL ARENA</div>
<p style="color:#94a3b8; font-size:0.85rem; margin:0;">
Click any White piece to reveal legal move destinations (●), then tap the target square. In AI mode, Black automatically calculates and executes its response move.
</p>
</div>
""", unsafe_allow_html=True)

    if "chess_engine" not in st.session_state:
        st.session_state.chess_engine = ChessEngine()
        st.session_state.chess_mode = "ai"  # default Human vs AI
        st.session_state.chess_selected = None  # (r, c)
        st.session_state.chess_legal_dests = []
        st.session_state.chess_feedback = "Select a White piece to move."
        st.session_state.chess_start_time = time.time()

    engine: ChessEngine = st.session_state.chess_engine

    # Controls Header
    col_m, col_turn, col_chk, col_rst = st.columns([1.5, 1.2, 1.2, 1.0])

    with col_m:
        m_choice = st.selectbox(
            "Game Mode:",
            ["Human (White) vs AI (Black)", "2-Player Local (Pass & Play)"],
            index=0 if st.session_state.chess_mode == "ai" else 1,
            key="chess_mode_sel"
        )
        new_mode = "ai" if "AI" in m_choice else "2p"
        if new_mode != st.session_state.chess_mode:
            st.session_state.chess_mode = new_mode
            engine.reset(new_mode)
            st.session_state.chess_selected = None
            st.session_state.chess_legal_dests = []
            st.session_state.chess_feedback = "New game initiated."
            st.rerun()

    with col_turn:
        turn_color = "#38bdf8" if engine.current_turn == "white" else "#a855f7"
        st.markdown(f"<div style='padding-top:10px;'><span style='color:#94a3b8; font-size:0.8rem;'>ACTIVE TURN:</span><br><b style='color:{turn_color}; font-size:1.1rem;'>{engine.current_turn.upper()}</b></div>", unsafe_allow_html=True)

    with col_chk:
        in_chk_w = engine.is_in_check("white")
        in_chk_b = engine.is_in_check("black")
        if in_chk_w:
            st.markdown("<div style='padding-top:10px;'><b style='color:#ef4444; font-size:1.0rem;'>⚠️ WHITE IN CHECK</b></div>", unsafe_allow_html=True)
        elif in_chk_b:
            st.markdown("<div style='padding-top:10px;'><b style='color:#ef4444; font-size:1.0rem;'>⚠️ BLACK IN CHECK</b></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='padding-top:10px;'><span style='color:#10b981; font-size:0.9rem;'>● King Safe</span></div>", unsafe_allow_html=True)

    with col_rst:
        if st.button("🔄 Reset Board", key="chess_rst_btn"):
            engine.reset(st.session_state.chess_mode)
            st.session_state.chess_selected = None
            st.session_state.chess_legal_dests = []
            st.session_state.chess_feedback = "Board reset."
            st.rerun()

    # Compact Victory / Checkmate Banner
    if engine.is_game_over:
        st.balloons()
        st.markdown(f"""
        <div class="hud-card" style="border: 2px solid #00ffcc; text-align:center; background:rgba(0,255,204,0.08); padding: 10px 16px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <span style="color:#00ffcc; font-size:1.15rem; font-weight:900;">🏆 CHECKMATE — {engine.winner.upper()} WINS!</span>
                <span style="color:#94a3b8; font-size:0.85rem; margin-left:12px;">King eliminated via adversarial state-space search.</span>
            </div>
            <div style="color:#00ffcc; font-family:monospace; font-weight:800; font-size:1.1rem;">
                SCORE: 10,000 pts
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Main Chessboard (68%) + Telemetry Panel (32%)
    col_board, col_side = st.columns([1.75, 0.85])

    with col_board:
        # Dynamic CSS generation for Chess pieces and Grid
        css_rules = []
        for r in range(8):
            for c in range(8):
                piece = engine.board[r][c]
                is_light_square = (r + c) % 2 == 0
                bg_color = "#334155" if is_light_square else "#182234"
                
                # 9 elements per row (1 label + 8 buttons).
                btn_index = r * 9 + c + 2
                
                sel_base = f"div[data-testid='stVerticalBlock']:has(> div.element-container .chess-grid-marker) > div.element-container:nth-child({btn_index}) button"
                sel_inner = f"{sel_base}, {sel_base} p, {sel_base} div, {sel_base} span"
                
                # Checkerboard background
                css_rules.append(f"{sel_base} {{ background-color: {bg_color} !important; }}")
                
                if piece.isupper():
                    # White Piece: light fill, dark outline
                    css_rules.append(f"{sel_inner} {{ color: #ffffff !important; text-shadow: 0px 1px 4px rgba(0,0,0,0.9), 0px -1px 2px rgba(0,0,0,0.6) !important; }}")
                elif piece.islower():
                    # Black Piece: dark charcoal fill, light outline
                    css_rules.append(f"{sel_inner} {{ color: #111827 !important; text-shadow: 0px 1px 3px rgba(255,255,255,0.7) !important; }}")

        full_chess_css = "\n".join(css_rules)

        st.markdown(f"""
        <style>
            /* 8x8 Seamless Chessboard Container */
            .chess-outer-box {{
                background: #0b1120;
                border: 3px solid #1e293b;
                border-radius: 12px;
                padding: 10px 14px 14px 10px;
                box-shadow: 0 15px 35px rgba(0, 0, 0, 0.7), 0 0 20px rgba(56, 189, 248, 0.12);
                margin-bottom: 12px;
                width: 600px;
                margin-left: auto;
                margin-right: auto;
            }}
            .chess-row-label {{
                display: flex;
                align-items: center;
                justify-content: center;
                color: #64748b;
                font-family: 'JetBrains Mono', monospace;
                font-weight: 800;
                font-size: 1.15rem;
                height: 64px;
                min-height: 64px;
            }}
            
            /* Center Board Column */
            div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: flex-start !important;
            }}

            /* True CSS Grid for 8x8 Chessboard + Labels */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) {{
                display: grid !important;
                grid-template-columns: 32px repeat(8, 64px) !important;
                grid-template-rows: repeat(8, 64px) 32px !important;
                gap: 0px !important;
                width: 544px !important;
                height: 544px !important;
                margin: 0 auto !important;
                padding: 0px !important;
                align-items: center !important;
                justify-content: center !important;
            }}



            /* Reset Element Container inside Grid */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) > div.element-container {{
                margin: 0 !important;
                padding: 0 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                height: 100% !important;
            }}

            /* Chess Square Buttons */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) > div.element-container button {{
                width: 64px !important;
                height: 64px !important;
                min-width: 64px !important;
                max-width: 64px !important;
                min-height: 64px !important;
                max-height: 64px !important;
                padding: 0px !important;
                margin: 0px !important;
                border-radius: 0px !important;
                border: 1px solid rgba(255, 255, 255, 0.04) !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                transition: all 0.1s ease !important;
                box-sizing: border-box !important;
                overflow: hidden !important;
            }}
            
            /* Override inner elements to prevent shrinking or misaligning */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) > div.element-container button p,
            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) > div.element-container button div,
            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) > div.element-container button span {{
                font-size: 50px !important;
                line-height: 1 !important;
                font-weight: 700 !important;
                font-family: "DejaVu Sans", "Segoe UI Symbol", "Noto Sans Symbols 2", "Arial Unicode MS", sans-serif !important;
                padding: 0px !important;
                margin: 0px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                height: 100% !important;
                transform: none !important;
                box-sizing: border-box !important;
            }}

            div[data-testid="stVerticalBlock"]:has(> div.element-container .chess-grid-marker) > div.element-container button:hover {{
                border: 2px solid #38bdf8 !important;
                z-index: 5;
            }}

            {full_chess_css}
        </style>
        """, unsafe_allow_html=True)

        selected_pos = st.session_state.chess_selected
        legal_dests = set(st.session_state.chess_legal_dests)

        with st.container():
            for r in range(8):
                # Row number label (8 down to 1) perfectly aligned with rank height
                # We inject the marker on the very first label so it doesn't create an extra grid item
                marker_class = " chess-grid-marker" if r == 0 else ""
                st.markdown(f'<div class="chess-row-label{marker_class}">{8 - r}</div>', unsafe_allow_html=True)

                for c in range(8):
                    piece = engine.board[r][c]
                    u_piece = engine.UNICODE_PIECES.get(piece, " ")
                    is_selected = (r, c) == selected_pos
                    is_legal_dest = (r, c) in legal_dests
                    target_piece = engine.board[r][c]
                    is_capture = is_legal_dest and target_piece != "."

                    if is_selected:
                        btn_label = f"[{u_piece}]" if u_piece.strip() else "[·]"
                    elif is_capture:
                        btn_label = f"⚔️"
                    elif is_legal_dest:
                        btn_label = "●"
                    else:
                        btn_label = u_piece if u_piece.strip() else " "

                    if st.button(
                        btn_label,
                        key=f"ch_cell_{r}_{c}",
                        disabled=engine.is_game_over
                    ):
                        _handle_square_click(engine, r, c)

            # Bottom Column File Labels (A to H) perfectly aligned with columns
            st.markdown("<div class='chess-row-label'></div>", unsafe_allow_html=True) # Empty corner
            for char in ["A", "B", "C", "D", "E", "F", "G", "H"]:
                st.markdown(f"<div style='text-align:center; color:#64748b; font-family:monospace; font-weight:800; font-size:1.1rem; padding-top:6px; width:64px;'>{char}</div>", unsafe_allow_html=True)

    with col_side:
        with st.container(border=True):
            st.markdown("#### 📜 Match Status")
            if st.session_state.chess_feedback:
                st.markdown(f"**Latest:** `{st.session_state.chess_feedback}`")

            # Captured Pieces Trays
            cap_w = " ".join([engine.UNICODE_PIECES.get(p, p) for p in engine.captured_white]) or "None"
            cap_b = " ".join([engine.UNICODE_PIECES.get(p, p) for p in engine.captured_black]) or "None"
            st.markdown(f"• **White Lost:** `{cap_w}`")
            st.markdown(f"• **Black Lost:** `{cap_b}`")

            if engine.last_move:
                lm = engine.last_move
                st.markdown(f"• **Last Move:** `{engine.get_square_label(lm[0], lm[1])} → {engine.get_square_label(lm[2], lm[3])}`")

            st.divider()
            st.markdown("##### 📜 Recent Move History")
            for m in engine.move_history[-4:]:
                st.caption(f"• {m}")

        # Real Adversarial AI Search Telemetry Card & Educational Panel
        if engine.last_ai_eval and st.session_state.chess_mode == "ai":
            st.divider()
            if st.button("🧠 HOW AI SOLVES", key="chess_how_ai_btn"):
                st.session_state.chess_show_ai = not st.session_state.get("chess_show_ai", False)
                st.session_state.chess_sim_step = 0
                st.rerun()

            if st.session_state.get("chess_show_ai"):
                st.markdown("""
<div style="background:rgba(15,23,42,0.8); padding: 15px; border-radius: 8px; border: 1px solid #38bdf8; margin-top:10px;">
<h4 style="color:#38bdf8; margin-top:0;">🤖 2-PLY MINIMAX ALGORITHM</h4>
<b>WHY THIS ALGORITHM?</b><br/>
Chess is an adversarial, perfect-information game. Minimax evaluates the game tree by maximizing the AI's score while assuming the opponent minimizes it. Alpha-Beta Pruning cuts off branches that are mathematically guaranteed to be worse, saving computation.<br/><br/>

<b>STATE REPRESENTATION:</b><br/>
An 8x8 matrix. The heuristic evaluates material value (Queen=900, Rook=500, etc.) and positional control.<br/><br/>

<b>HOW IT SEARCHES:</b><br/>
1. Generate all legal moves for Black (Ply 1).<br/>
2. For each, simulate the move and generate White's replies (Ply 2).<br/>
3. Evaluate the resulting leaf node and propagate scores up.<br/>
4. Prune branches if minimum White reply is already worse than the best Black move so far.<br/><br/>
<hr style="border-top:1px solid rgba(56,189,248,0.3); margin: 10px 0;"/>
<b>⏱️ COMPLEXITY ANALYSIS</b><br/><br/>
<b>Time Complexity:</b> O(b²)<br/>
<b>Space Complexity:</b> O(b)<br/><br/>
<i style="color:#94a3b8; font-size:0.85rem;">b = branching factor (average legal moves)</i>
</div>
""", unsafe_allow_html=True)
                
                ev = engine.last_ai_eval
                st.markdown("##### 🔬 LIVE SIMULATION")
                
                branches = ev.get("top_branches", [])
                if branches:
                    sim_step = st.session_state.get("chess_sim_step", 0)
                    col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
                    with col_ctrl1:
                        if st.button("⏮ Prev", key="ch_sim_prev", disabled=sim_step <= 0):
                            st.session_state.chess_sim_step -= 1
                            st.rerun()
                    with col_ctrl2:
                        if st.button("⏭ Next", key="ch_sim_next", disabled=sim_step >= len(branches)-1):
                            st.session_state.chess_sim_step += 1
                            st.rerun()
                    with col_ctrl3:
                        if st.button("↻ Restart", key="ch_sim_rst"):
                            st.session_state.chess_sim_step = 0
                            st.rerun()

                    b = branches[sim_step]
                    st.markdown(f"**Step {sim_step+1}/{len(branches)}:** Evaluating Candidate Move")
                    st.markdown(f"**Action:** `{b['notation']}` ➔ Score: `{b['score']:+}`")
                    st.markdown(f"**Rationale:** `{b.get('rationale', '')}`")
                    
                    # Simulation Mini-Board
                    board_copy = [row[:] for row in engine.board]
                    
                    html_board = "<table style='width:180px; text-align:center; margin:auto; border-collapse:collapse;'>"
                    for rr in range(8):
                        html_board += "<tr>"
                        for cc in range(8):
                            val = board_copy[rr][cc]
                            disp = engine.UNICODE_PIECES.get(val, " ") if val != "." else " "
                            
                            # Highlight the move in simulation
                            bg = "#1e293b" if (rr+cc)%2==0 else "#0f172a"
                            if (rr, cc) == (b["move"][0], b["move"][1]):
                                bg = "#ef4444"
                            elif (rr, cc) == (b["move"][2], b["move"][3]):
                                bg = "#3b82f6"
                                
                            html_board += f"<td style='border:1px solid #475569; width:22px; height:22px; font-size:16px; background:{bg};'>{disp}</td>"
                        html_board += "</tr>"
                    html_board += "</table><br/>"
                    st.markdown(html_board, unsafe_allow_html=True)
                
                st.markdown(f"**FINAL DECISION:** Chooses `{ev.get('best_notation', 'None')}`")
                st.markdown(f"**METRICS:** Nodes: `{ev.get('nodes_expanded', 0)}` | Cutoffs: `{ev.get('alpha_beta_cutoffs', 0)}`")


def _handle_square_click(engine: ChessEngine, r: int, c: int):
    """Direct Click Square Handler with Automatic AI Response."""
    selected = st.session_state.chess_selected
    piece = engine.board[r][c]
    is_curr_turn_piece = (engine.is_white_piece(piece) if engine.current_turn == "white" else engine.is_black_piece(piece))

    # If no piece is currently selected:
    if selected is None:
        if is_curr_turn_piece:
            st.session_state.chess_selected = (r, c)
            st.session_state.chess_legal_dests = engine.get_legal_moves(r, c)
            st.session_state.chess_feedback = f"Selected {engine.PIECE_NAMES.get(piece, piece)} at {engine.get_square_label(r, c)}"
            st.rerun()
        else:
            st.session_state.chess_feedback = "Select one of your own active pieces."
            st.rerun()

    # If a piece is already selected:
    else:
        sel_r, sel_c = selected
        # If player clicked one of the legal destinations:
        if (r, c) in st.session_state.chess_legal_dests:
            res = engine.make_move(sel_r, sel_c, r, c)
            st.session_state.chess_selected = None
            st.session_state.chess_legal_dests = []

            # AUTOMATIC AI RESPONSE IN HUMAN VS AI MODE
            if st.session_state.chess_mode == "ai" and engine.current_turn == "black" and not engine.is_game_over:
                ai_res = engine.evaluate_and_execute_ai_move()
                st.session_state.chess_feedback = f"You: {res.get('notation', '')} | AI: {ai_res.get('notation', '')}"
            else:
                st.session_state.chess_feedback = f"✓ Moved {res.get('notation', '')}"
            st.rerun()

        # If player clicked another of their own pieces: switch selection
        elif is_curr_turn_piece:
            st.session_state.chess_selected = (r, c)
            st.session_state.chess_legal_dests = engine.get_legal_moves(r, c)
            st.session_state.chess_feedback = f"Switched to {engine.PIECE_NAMES.get(piece, piece)} at {engine.get_square_label(r, c)}"
            st.rerun()

        # Clicked elsewhere: deselect
        else:
            st.session_state.chess_selected = None
            st.session_state.chess_legal_dests = []
            st.session_state.chess_feedback = "Deselected."
            st.rerun()
