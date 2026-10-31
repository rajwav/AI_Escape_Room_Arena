"""
AI ESCAPE ROOM ARENA — Tic Tac Toe Module (Minimax Adversarial Game Search)
Features:
- 100% Clickable 3x3 Visual Grid
- Local 2-Player (Pass & Play) and Human vs AI Modes
- Minimax Algorithm with Game Tree Evaluation & Decision Trace
- Real-Time Adversarial Search Telemetry (Nodes evaluated, candidate branch scores)
"""

import streamlit as st
import os
import sys

src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ttt_engine import TicTacToeEngine


def render_tic_tac_toe_game():
    """Renders the 3x3 Tic Tac Toe game with Minimax AI."""
    st.markdown("""
<div class="hud-card">
<div class="card-title">❌⭕ QUANTUM TIC TAC TOE: MINIMAX GAME TREE ARENA</div>
<p style="color:#94a3b8; font-size:0.85rem; margin:0;">
Play local 2-player or challenge the zero-sum Minimax adversarial game tree AI engine.
</p>
</div>
""", unsafe_allow_html=True)

    if "ttt_engine" not in st.session_state:
        st.session_state.ttt_engine = TicTacToeEngine()
        st.session_state.ttt_mode = "ai"

    engine: TicTacToeEngine = st.session_state.ttt_engine

    # Controls Bar
    col_m, col_turn, col_rst = st.columns([1.5, 1.5, 1.0])
    with col_m:
        m_choice = st.selectbox(
            "Game Mode:",
            ["Human (X) vs AI (O) [Minimax]", "2-Player Local (Pass & Play)"],
            index=0 if st.session_state.ttt_mode == "ai" else 1,
            key="ttt_mode_sel"
        )
        new_mode = "ai" if "AI" in m_choice else "2p"
        if new_mode != st.session_state.ttt_mode:
            st.session_state.ttt_mode = new_mode
            engine.reset(new_mode)
            st.rerun()

    with col_turn:
        if engine.is_game_over:
            if engine.winner:
                st.markdown(f"<div style='color:#00ffcc; font-weight:bold; font-size:1.1rem; padding-top:10px;'>🏆 Winner: Player {engine.winner}!</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='color:#38bdf8; font-weight:bold; font-size:1.1rem; padding-top:10px;'>🤝 Stalemate / Draw!</div>", unsafe_allow_html=True)
        else:
            turn_color = "#38bdf8" if engine.current_player == "X" else "#a855f7"
            st.markdown(f"<div style='color:{turn_color}; font-weight:bold; font-size:1.1rem; padding-top:10px;'>Current Turn: <b>Player {engine.current_player}</b></div>", unsafe_allow_html=True)

    with col_rst:
        if st.button("🔄 Restart Match", key="ttt_rst_btn"):
            engine.reset(st.session_state.ttt_mode)
            st.rerun()

    # Main Grid + AI Telemetry Layout
    col_board, col_side = st.columns([1.4, 1.2])

    with col_board:
        st.markdown("""
<style>
div[data-testid="stHorizontalBlock"] button {
font-size: 2.2rem !important;
font-weight: 900 !important;
height: 70px !important;
}
</style>
""", unsafe_allow_html=True)

        for row in range(3):
            cols = st.columns(3)
            for col in range(3):
                idx = row * 3 + col
                cell_val = engine.board[idx]
                btn_text = cell_val if cell_val != " " else " "

                with cols[col]:
                    if st.button(
                        btn_text,
                        key=f"ttt_cell_{idx}",
                        disabled=(engine.is_game_over or cell_val != " ")
                    ):
                        engine.make_move(idx)
                        st.rerun()

    with col_side:
        pass

    st.divider()
    if st.button("🧠 HOW AI SOLVES", key="ttt_how_ai_btn"):
        st.session_state.ttt_show_ai = not st.session_state.get("ttt_show_ai", False)
        st.session_state.ttt_sim_step = 0
        st.rerun()

    if st.session_state.get("ttt_show_ai"):
        st.markdown("""
<div style="background:rgba(15,23,42,0.8); padding: 15px; border-radius: 8px; border: 1px solid #38bdf8; margin-top:15px;">
<h4 style="color:#38bdf8; margin-top:0;">🤖 MINIMAX ALGORITHM</h4>
<b>WHY THIS ALGORITHM?</b><br/>
Tic-Tac-Toe is a zero-sum, perfect information game. Minimax perfectly solves it by exploring all possible future moves to the end of the game, assuming optimal play by the opponent.<br/><br/>
<b>STATE REPRESENTATION:</b><br/>
A 9-element array representing the board. Player is MAX, opponent is MIN.<br/><br/>
<b>HOW IT SEARCHES:</b><br/>
It builds a game tree. At each node, if it's MAX's turn, it picks the move with the highest score. If MIN's turn, it picks the lowest score. Leaf nodes are evaluated: Win (+10/-10) or Draw (0).<br/><br/>
<hr style="border-top:1px solid rgba(56,189,248,0.3); margin: 10px 0;"/>
<b>⏱️ COMPLEXITY ANALYSIS</b><br/><br/>
<b>Time Complexity:</b> O(b^d)<br/>
<b>Space Complexity:</b> O(bd)<br/><br/>
<i style="color:#94a3b8; font-size:0.85rem;">b = branching factor<br/>d = search depth</i>
</div>
""", unsafe_allow_html=True)
        
        tel = engine.last_ai_telemetry
        if tel and "candidate_branches" in tel and len(tel["candidate_branches"]) > 0:
            st.markdown("##### 🔬 LIVE SIMULATION")
            branches = tel["candidate_branches"]
            sim_step = st.session_state.get("ttt_sim_step", 0)
            
            col_ctrl1, col_ctrl2, col_ctrl3, col_ctrl4 = st.columns(4)
            with col_ctrl1:
                if st.button("⏮ Prev", key="ttt_sim_prev", disabled=sim_step <= 0):
                    st.session_state.ttt_sim_step -= 1
                    st.rerun()
            with col_ctrl2:
                if st.button("⏭ Next", key="ttt_sim_next", disabled=sim_step >= len(branches)-1):
                    st.session_state.ttt_sim_step += 1
                    st.rerun()
            with col_ctrl3:
                if st.button("↻ Restart", key="ttt_sim_rst"):
                    st.session_state.ttt_sim_step = 0
                    st.rerun()
                    
            b = branches[sim_step]
            st.markdown(f"**Step {sim_step+1}/{len(branches)}:** Candidate Move at `{b['label']}` (Index {b['cell_index']})")
            st.markdown(f"**Minimax Evaluation Score:** `{b['minimax_utility']:+d}`")
            
            # Mini board
            board_copy = list(engine.board)
            board_copy[b['cell_index']] = "<span style='color:#38bdf8; font-weight:bold;'>?</span>"
            
            html_board = "<table style='width:150px; text-align:center; margin:auto; border-collapse:collapse;'>"
            for r in range(3):
                html_board += "<tr>"
                for c in range(3):
                    val = board_copy[r*3+c]
                    html_board += f"<td style='border:1px solid #94a3b8; width:50px; height:50px; font-size:20px;'>{val}</td>"
                html_board += "</tr>"
            html_board += "</table><br/>"
            st.markdown(html_board, unsafe_allow_html=True)
            
            st.markdown(f"**FINAL DECISION:** Chooses {tel['chosen_move']} with score {tel['chosen_score']:+d}")
            st.markdown(f"**METRICS:** Nodes Expanded: {tel['total_nodes_expanded']}")
        else:
            st.info("Play a move against the AI to generate a search trace.")

        if engine.last_ai_telemetry and st.session_state.ttt_mode == "ai":
            with st.container(border=True):
                tel = engine.last_ai_telemetry
                st.markdown("#### 🤖 Minimax Search Telemetry")
                st.markdown(f"• **Game Tree States Evaluated:** `{tel['total_nodes_expanded']}`")
                st.markdown(f"• **Optimal Move Chosen:** `{tel['chosen_move']} ({engine.POSITION_LABELS.get(tel['chosen_move'])})`")
                st.markdown(f"• **Minimax Utility Score:** `{tel['chosen_score']:+d}`")

                st.divider()
                st.markdown("##### 🌲 Candidate Move Evaluation Tree:")
                for b in tel["candidate_branches"]:
                    score_icon = "🟢" if b["minimax_utility"] > 0 else ("🟡" if b["minimax_utility"] == 0 else "🔴")
                    st.caption(f"{score_icon} **{b['label']}** (Cell {b['cell_index']}) ➔ Score: `{b['minimax_utility']:+d}`")
        else:
            with st.container(border=True):
                st.markdown("#### 🎮 Match Information")
                st.markdown(f"• **Mode:** `{st.session_state.ttt_mode.upper()}`")
                st.markdown(f"• **Moves Taken:** `{engine.moves_count}`")
                st.markdown("• **Player X:** Human")
                st.markdown("• **Player O:** Minimax AI / Local Player")
