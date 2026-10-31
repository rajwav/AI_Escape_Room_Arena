"""
AI ESCAPE ROOM ARENA — Quantum Minesweeper Module (Logic & Deduction)
Features:
- 100% Clickable 9x9 Grid with 10 hidden mines
- Mode switch: ◉ REVEAL vs ⚑ FLAG
- Exactly ONE Life (Instant Game Over on mine trigger)
- ONE Initial AI Safe Move Hint (No further hints permitted in Human Mode)
- "WATCH AI PLAY" Non-Cheating Propositional Logic & CSP Simulation
- Step-by-Step AI Reasoning Telemetry & Highlight Matrix
- Deterministic Time-Based Scoring (0 pts on mine failure)
"""

import streamlit as st
import time
import os
import sys

src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from minesweeper_engine import MinesweeperEngine
from scoring_engine import ScoringEngine


def render_minesweeper_game():
    """Renders the 9x9 Quantum Minesweeper Game & AI Simulation."""
    st.markdown("""
<div class="hud-card">
<div class="card-title">💣 QUANTUM MINESWEEPER: PROPOSITIONAL LOGIC & CSP ARENA</div>
<p style="color:#94a3b8; font-size:0.85rem; margin:0;">
9×9 Grid with 10 hidden mines. 1 Life only. Use the first safe hint, then solve independently or engage <b>Watch AI Play</b>.
</p>
</div>
""", unsafe_allow_html=True)

    if "ms_engine" not in st.session_state:
        st.session_state.ms_engine = MinesweeperEngine()
        st.session_state.ms_action_mode = "reveal"  # "reveal" or "flag"
        st.session_state.ms_start_time = time.time()
        st.session_state.ms_completed_time = None
        st.session_state.ms_feedback = None
        st.session_state.ms_ai_step_history = []
        st.session_state.ms_active_ai_step = None

    engine: MinesweeperEngine = st.session_state.ms_engine

    _render_human_mode(engine)

    if st.session_state.get("ms_show_how_ai_solves", False):
        st.divider()
        _render_ai_mode(engine)


def _render_human_mode(engine: MinesweeperEngine):
    # Status Bar
    col_stat, col_mode, col_time, col_rst = st.columns([1.5, 1.5, 1.2, 1.0])

    with col_stat:
        if engine.is_won:
            st.markdown("<div style='color:#00ffcc; font-weight:bold; font-size:1.1rem; padding-top:8px;'>STATUS: 🏆 CLEARED</div>", unsafe_allow_html=True)
        elif engine.is_game_over:
            st.markdown("<div style='color:#ef4444; font-weight:bold; font-size:1.1rem; padding-top:8px;'>STATUS: 💥 FAILED</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#34d399; font-weight:bold; font-size:1.1rem; padding-top:8px;'>STATUS: ● ACTIVE (1 LIFE)</div>", unsafe_allow_html=True)

    with col_mode:
        mode_radio = st.radio(
            "Action Mode:",
            ["◉ REVEAL CELL", "⚑ TOGGLE FLAG"],
            index=0 if st.session_state.ms_action_mode == "reveal" else 1,
            horizontal=True,
            key="ms_mode_radio"
        )
        st.session_state.ms_action_mode = "reveal" if "REVEAL" in mode_radio else "flag"

    with col_time:
        elapsed = int(time.time() - st.session_state.ms_start_time) if st.session_state.ms_completed_time is None else st.session_state.ms_completed_time
        st.metric("Elapsed Time", f"{elapsed // 60:02d}:{elapsed % 60:02d}")

    with col_rst:
        if st.button("🔄 New Grid", key="ms_rst_btn_human"):
            st.session_state.ms_engine = MinesweeperEngine()
            st.session_state.ms_start_time = time.time()
            st.session_state.ms_completed_time = None
            st.session_state.ms_feedback = None
            st.session_state.ms_ai_step_history = []
            st.session_state.ms_active_ai_step = None
            st.rerun()

    # Initial AI Hint Card (Single Safe First Move)
    if not engine.initial_hint_consumed and not engine.is_game_over and not engine.is_won:
        st.markdown(f"""
        <div style="background:rgba(56,189,248,0.12); border:1px solid #38bdf8; border-radius:8px; padding:12px 16px; margin:10px 0;">
            <div style="color:#00ffcc; font-weight:bold; font-family:monospace;">🧠 INITIAL AI SAFE MOVE HINT</div>
            <div style="color:#e2e8f0; font-size:0.9rem; margin-top:2px;">
                {engine.get_initial_hint_str()} <span style="color:#94a3b8; font-size:0.8rem;">(This is the ONLY hint provided; all further cells must be solved independently).</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Victory / Failure Banner
    if engine.is_won:
        if st.session_state.ms_completed_time is None:
            st.session_state.ms_completed_time = int(time.time() - st.session_state.ms_start_time)

        final_time = st.session_state.ms_completed_time
        score_res = ScoringEngine.calculate_game_score(
            game_id="minesweeper",
            solved=True,
            time_seconds=final_time,
            flags_placed=len(engine.flagged),
            cells_revealed=len(engine.revealed)
        )
        st.balloons()
        st.markdown(f"""
        <div class="hud-card" style="border:2px solid #00ffcc; text-align:center; background:rgba(0,255,204,0.08);">
            <h2 style="color:#00ffcc; margin:0 0 6px 0;">🏆 MISSION COMPLETE — ALL 71 SAFE CELLS REVEALED!</h2>
            <div style="display:flex; justify-content:center; gap:36px; margin-top:12px;">
                <div>
                    <div style="color:#94a3b8; font-size:0.8rem;">FINAL SCORE</div>
                    <div style="font-size:2.2rem; font-weight:900; color:#00ffcc; font-family:monospace;">{score_res['score']:,}</div>
                </div>
                <div>
                    <div style="color:#94a3b8; font-size:0.8rem;">COMPLETION TIME</div>
                    <div style="font-size:2.2rem; font-weight:900; color:#38bdf8; font-family:monospace;">{final_time}s</div>
                </div>
                <div>
                    <div style="color:#94a3b8; font-size:0.8rem;">FLAGS PLACED</div>
                    <div style="font-size:2.2rem; font-weight:900; color:#a855f7; font-family:monospace;">{len(engine.flagged)} / 10</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif engine.is_game_over:
        st.markdown("""
<div class="hud-card" style="border:2px solid #ef4444; text-align:center; background:rgba(239,68,68,0.08);">
<h2 style="color:#ef4444; margin:0 0 6px 0;">💥 MINE TRIGGERED — MISSION FAILED!</h2>
<p style="color:#94a3b8; margin-bottom:6px;">Detonated an active mine. Zero lives remaining.</p>
<div style="font-size:1.6rem; font-weight:800; color:#ef4444; font-family:monospace;">SCORE: 0 / 10,000</div>
</div>
""", unsafe_allow_html=True)

    # 9x9 Interactive Grid
    col_grid, col_side = st.columns([1.65, 1.1])

    with col_grid:
        for r in range(9):
            row_cols = st.columns(9)
            for c in range(9):
                pos = (r, c)
                is_rev = pos in engine.revealed
                is_flag = pos in engine.flagged
                is_mine = pos in engine.mines

                if is_rev:
                    if is_mine:
                        btn_label = "💣"
                    else:
                        adj = engine.get_adjacent_mines_count(r, c)
                        btn_label = str(adj) if adj > 0 else "·"
                elif is_flag:
                    btn_label = "🚩"
                else:
                    btn_label = " "

                disabled = engine.is_game_over or engine.is_won or is_rev

                with row_cols[c]:
                    if st.button(
                        btn_label,
                        key=f"ms_h_tile_{r}_{c}",
                        disabled=disabled
                    ):
                        if st.session_state.ms_action_mode == "flag":
                            engine.toggle_flag(r, c)
                        else:
                            engine.reveal_cell(r, c)
                        st.rerun()

    with col_side:
        with st.container(border=True):
            st.markdown("#### 📊 Sector Telemetry")
            st.markdown(f"• **Grid Matrix:** `9×9 (81 Sectors)`")
            st.markdown(f"• **Active Mines:** `10 Total`")
            st.markdown(f"• **Sectors Flagged:** `{len(engine.flagged)} / 10`")
            st.markdown(f"• **Safe Sectors Cleared:** `{len(engine.revealed - engine.mines)} / 71`")

            st.markdown(f"• **Actions Logged:** `{engine.moves_count}`")

            st.divider()
            if st.button("🧠 HOW AI SOLVES", key="btn_ms_how_ai_solves"):
                st.session_state.ms_show_how_ai_solves = not st.session_state.get("ms_show_how_ai_solves", False)
                st.rerun()


def _render_ai_mode(engine: MinesweeperEngine):
    st.markdown("""
<div style="background:rgba(15,23,42,0.8); padding: 15px; border-radius: 8px; border: 1px solid #38bdf8; margin-top:10px; margin-bottom:14px;">
<h4 style="color:#38bdf8; margin-top:0;">🤖 HOW AI SOLVES: PROPOSITIONAL LOGIC</h4>
<b>ALGORITHM:</b> Propositional Logic & Constraint-Based Deduction.<br/><br/>
<b>WHY THIS ALGORITHM?</b><br/>
Minesweeper is a local information game. The AI cannot "search" the future safely; it must deduce states deterministically. By turning known clues into constraint equations, it can isolate guaranteed safes and mines.<br/><br/>
<b>STATE REPRESENTATION:</b><br/>
Only revealed numbers and flags. A cell with number N implies the sum of mines in its 8 neighbors equals N.<br/><br/>
<b>HOW IT REASONS:</b><br/>
Rule 1: If remaining hidden neighbors == remaining needed mines -> All are mines (Flag).<br/>
Rule 2: If remaining needed mines == 0 -> All remaining hidden neighbors are safe (Reveal).<br/>
<i>Note: Zero Cheating Guarantee - The AI never accesses the underlying hidden matrix.</i><br/><br/>
<hr style="border-top:1px solid rgba(56,189,248,0.3); margin: 10px 0;"/>
<b>⏱️ COMPLEXITY ANALYSIS</b><br/><br/>
<b>Time Complexity:</b> O(2^N) worst case<br/>
<b>Space Complexity:</b> O(N)<br/><br/>
<i style="color:#94a3b8; font-size:0.85rem;">N = number of unknown/unassigned variables or cells</i>
</div>
""", unsafe_allow_html=True)

    # Generate isolated trace
    if st.button("▶ GENERATE ISOLATED AI TRACE", key="ms_gen_trace"):
        import copy
        sim_engine = copy.deepcopy(engine)
        trace = []
        for _ in range(30):
            step = sim_engine.compute_next_ai_reasoning_step()
            if not step:
                break
            
            # Record state before action
            step["sim_revealed"] = set(sim_engine.revealed)
            step["sim_flagged"] = set(sim_engine.flagged)
            trace.append(step)
            
            act = step["action"]
            tr, tc = step["target_cell"]
            if act == "flag":
                sim_engine.toggle_flag(tr, tc)
            elif act == "reveal":
                sim_engine.reveal_cell(tr, tc)
                
            if sim_engine.is_game_over or sim_engine.is_won:
                break
        
        st.session_state.ms_ai_trace = trace
        st.session_state.ms_ai_sim_step = 0
        st.rerun()

    trace = st.session_state.get("ms_ai_trace", [])
    if trace:
        sim_step = st.session_state.get("ms_ai_sim_step", 0)
        c_step1, c_step2, c_step3 = st.columns(3)
        with c_step1:
            if st.button("⏮ Prev", key="ms_sim_prev", disabled=sim_step <= 0):
                st.session_state.ms_ai_sim_step -= 1
                st.rerun()
        with c_step2:
            if st.button("⏭ Next", key="ms_sim_next", disabled=sim_step >= len(trace)-1):
                st.session_state.ms_ai_sim_step += 1
                st.rerun()
        with c_step3:
            if st.button("🔄 Restart Sim", key="ms_sim_rst"):
                st.session_state.ms_ai_sim_step = 0
                st.rerun()
                
        active_step = trace[sim_step]
        st.session_state.ms_active_ai_step = active_step
    else:
        active_step = None

    # Layout: Live AI Board + Step Rationale Box
    col_grid, col_side = st.columns([1.65, 1.2])

    active_step = st.session_state.ms_active_ai_step
    analyzed_cell = active_step.get("analyzed_cell") if active_step else None
    target_cell = active_step.get("target_cell") if active_step else None

    with col_grid:
        for r in range(9):
            row_cols = st.columns(9)
            for c in range(9):
                pos = (r, c)
                if active_step:
                    is_rev = pos in active_step.get("sim_revealed", set())
                    is_flag = pos in active_step.get("sim_flagged", set())
                else:
                    is_rev = pos in engine.revealed
                    is_flag = pos in engine.flagged
                    
                is_mine = pos in engine.mines
                is_analyzed = (pos == analyzed_cell)
                is_target = (pos == target_cell)

                if is_rev:
                    if is_mine:
                        btn_label = "💣"
                    else:
                        adj = engine.get_adjacent_mines_count(r, c)
                        btn_label = str(adj) if adj > 0 else "·"
                elif is_flag:
                    btn_label = "🚩"
                elif is_analyzed:
                    btn_label = "🔵"
                elif is_target:
                    btn_label = "🟣"
                else:
                    btn_label = " "

                with row_cols[c]:
                    st.button(btn_label, key=f"ms_ai_tile_{r}_{c}", disabled=True)

        st.markdown("""
<div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8; margin-top:8px;">
<span>🔵 <b>Analyzed Cell</b></span>
<span>🟣 <b>Target Deduction</b></span>
<span>🚩 <b>Flagged Mine</b></span>
<span>· <b>Safe Cell</b></span>
</div>
""", unsafe_allow_html=True)

    with col_side:
        if active_step:
            with st.container(border=True):
                st.markdown(f"#### 🤖 AI Reasoning Cycle")
                st.markdown(f"**Target Cell:** `{engine.get_cell_label(*active_step['target_cell'])}`")
                st.markdown(f"**Action:** `{active_step['action'].upper()}`")
                st.markdown(f"**Constraint Rule:**\n`{active_step['deduction_rule']}`")
                st.markdown(f"**Mathematical Rationale:**\n\n{active_step['rationale']}")
                
                st.divider()
                st.markdown(f"• **Neighbors:** `{len(active_step['neighbors'])}`")
                st.markdown(f"• **Known Flags:** `{len(active_step['known_mines'])}`")
                st.markdown(f"• **Unknown Sectors:** `{len(active_step['unknowns'])}`")
        else:
            with st.container(border=True):
                st.markdown("#### 🤖 AI Idle")
                st.info("Click 'EXECUTE NEXT AI REASONING STEP' to begin non-cheating constraint propagation.")
