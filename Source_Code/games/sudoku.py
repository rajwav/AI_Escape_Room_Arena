"""
AI ESCAPE ROOM ARENA — Quantum Sudoku Module (Classical UI & CSP Engine)
Features:
- Substantially Larger True 9x9 Square Matrix (1:1 Aspect Ratio, Zero Gaps)
- Classical Sudoku Visual Hierarchy with Distinct 3x3 Box Boundaries
- Universal Number Highlighting (Fixed & Player matching digits highlight on click)
- Dynamic Completed-Number Removal from Keypad (Disables digits placed 9 times)
- Interactive ✏️ Notes / Pencil Mode (Toggles 3x3 candidate scratchpad in empty cells)
- Accurate Synchronized Game Timer (Starts on puzzle start, freezes on complete)
- Clean Compact Top Bar & Victory HUD
- Dedicated "WATCH AI SOLVE" CSP + MRV Step Simulation Tab
"""

import streamlit as st
import time
import os
import sys

src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from sudoku_engine import SudokuEngine
from scoring_engine import ScoringEngine


def render_sudoku_game():
    """Renders the Classical 9x9 Sudoku Game & CSP Simulation."""
    if "sudoku_engine" not in st.session_state:
        st.session_state.sudoku_difficulty = "medium"
        st.session_state.sudoku_engine = SudokuEngine(difficulty="medium")
        st.session_state.sudoku_start_time = time.time()
        st.session_state.sudoku_completed_time = None
        st.session_state.sudoku_selected = (0, 0)
        st.session_state.sudoku_notes = {}  # (r, c) -> Set[int]
        st.session_state.sudoku_pencil_mode = False
        st.session_state.sudoku_feedback = None
        st.session_state.sudoku_sim_step = 0
        st.session_state.sudoku_sim_trace = None
        st.session_state.sudoku_sim_stats = None

    if "sudoku_notes" not in st.session_state:
        st.session_state.sudoku_notes = {}
    if "sudoku_pencil_mode" not in st.session_state:
        st.session_state.sudoku_pencil_mode = False

    engine: SudokuEngine = st.session_state.sudoku_engine

    # Main Tabs: Classical Play Mode vs Watch AI Solve
    _render_play_mode(engine)

    if st.session_state.get("sdk_show_how_ai_solves", False):
        st.divider()
        _render_ai_sim_mode(engine)


def _render_play_mode(engine: SudokuEngine):
    # Synchronized Timer
    if engine.is_completed:
        if st.session_state.sudoku_completed_time is None:
            st.session_state.sudoku_completed_time = int(time.time() - st.session_state.sudoku_start_time)
        final_time = st.session_state.sudoku_completed_time
    else:
        final_time = int(time.time() - st.session_state.sudoku_start_time)

    elapsed_min = final_time // 60
    elapsed_sec = final_time % 60
    timer_display = f"{elapsed_min:02d}:{elapsed_sec:02d}"

    # Clean, Classical Header Bar
    col_d, col_mis, col_tim = st.columns([1.3, 1.2, 1.1])

    with col_d:
        diff = st.selectbox(
            "Difficulty:",
            ["Easy", "Medium", "Hard"],
            index=["easy", "medium", "hard"].index(st.session_state.sudoku_difficulty),
            key="sdk_diff_sel_play"
        )
        if diff.lower() != st.session_state.sudoku_difficulty:
            st.session_state.sudoku_difficulty = diff.lower()
            st.session_state.sudoku_engine = SudokuEngine(difficulty=diff.lower())
            st.session_state.sudoku_start_time = time.time()
            st.session_state.sudoku_completed_time = None
            st.session_state.sudoku_notes = {}
            st.session_state.sudoku_feedback = None
            st.session_state.sudoku_selected = (0, 0)
            st.rerun()

    with col_mis:
        strikes = "❌ " * engine.mistakes + "⚪ " * (engine.max_mistakes - engine.mistakes)
        st.markdown(f"<div style='padding-top:10px;'><span style='color:#94a3b8; font-size:0.8rem;'>MISTAKES:</span><br><b style='font-size:1.05rem;'>{strikes}</b></div>", unsafe_allow_html=True)

    with col_tim:
        st.markdown(f"<div style='padding-top:10px;'><span style='color:#94a3b8; font-size:0.8rem;'>TIME:</span><br><b style='color:#10b981; font-family:monospace; font-size:1.25rem;'>⏱ {timer_display}</b></div>", unsafe_allow_html=True)

    st.markdown("<hr style='border:none; border-top:1px solid #334155; margin:8px 0 16px 0;'>", unsafe_allow_html=True)

    # Compact Victory / Failure HUD
    if engine.is_completed:
        score_res = ScoringEngine.calculate_game_score(
            game_id="sudoku",
            solved=True,
            time_seconds=final_time,
            mistakes=engine.mistakes,
            difficulty=st.session_state.sudoku_difficulty
        )
        st.balloons()
        st.markdown(f"""
        <div class="hud-card" style="border: 2px solid #10b981; background: rgba(16,185,129,0.08); padding: 12px 20px; margin-bottom:14px; border-radius:10px; text-align:center;">
            <div style="display:flex; justify-content:space-around; align-items:center; flex-wrap:wrap; gap:16px;">
                <div>
                    <div style="font-size:1.3rem; font-weight:900; color:#10b981;">🏆 SOLVED!</div>
                    <div style="font-size:0.8rem; color:#94a3b8;">All 81 cells satisfy Sudoku constraints.</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#94a3b8;">SCORE</div>
                    <div style="font-size:1.6rem; font-weight:900; color:#10b981; font-family:monospace;">{score_res['score']:,}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#94a3b8;">TIME</div>
                    <div style="font-size:1.6rem; font-weight:900; color:#38bdf8; font-family:monospace;">{timer_display}</div>
                </div>
                <div>
                    <div style="font-size:0.75rem; color:#94a3b8;">MISTAKES</div>
                    <div style="font-size:1.6rem; font-weight:900; color:#a855f7; font-family:monospace;">{engine.mistakes}/3</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    elif engine.is_game_over:
        st.markdown("""
<div class="hud-card" style="border: 2px solid #ef4444; background: rgba(239,68,68,0.08); padding: 10px 18px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">
<div>
<h3 style="color:#ef4444; margin:0; font-size:1.15rem;">💥 MISSION FAILED — 3 STRIKES REACHED</h3>
<p style="color:#94a3b8; font-size:0.8rem; margin:0;">Exceeded maximum constraint violations.</p>
</div>
<div style="font-size:1.3rem; font-weight:800; color:#ef4444; font-family:monospace;">SCORE: 0 / 10,000</div>
</div>
""", unsafe_allow_html=True)

    # 9x9 Classical Board (65%) + Smart Keypad Tray (35%)
    col_board, col_side = st.columns([1.7, 0.9])

    sel_r, sel_c = st.session_state.sudoku_selected if st.session_state.sudoku_selected else (-1, -1)
    sel_val = engine.current_board[sel_r][sel_c] if (0 <= sel_r < 9 and 0 <= sel_c < 9) else 0

    with col_board:
        # Dynamic CSS Generation for all 81 cells — 4-tier hierarchy, NO row/col highlight
        css_rules = []
        for r in range(9):
            for c in range(9):
                val = engine.current_board[r][c]
                is_fixed = (r, c) in engine.initial_fixed
                is_sel = (r, c) == (sel_r, sel_c)

                # Tier 2: Matching number — only fires when selected cell contains a number
                is_same_num = (sel_val != 0 and val != 0 and val == sel_val and not is_sel)

                # Tier 3: Selected 3×3 box (excludes selected cell and matching-number cells)
                # Tier 3: Selected 3×3 box
                is_in_sel_box = (
                    0 <= sel_r < 9 and 0 <= sel_c < 9
                    and (r // 3 == sel_r // 3) and (c // 3 == sel_c // 3)
                    and not is_sel and not is_same_num
                )

                # Select the exact button in the grid: 1-indexed, flattened index (r*9 + c + 1)
                # Note: The marker adds +1 to the nth-child count.
                btn_index = r * 9 + c + 2
                sel = f"div[data-testid='stVerticalBlock']:has(> div.element-container .sudoku-grid-marker) > div.element-container:nth-child({btn_index}) button"

                has_notes = (val == 0 and len(st.session_state.sudoku_notes.get((r, c), set())) > 0)

                if is_sel:
                    # Tier 1 — SELECTED CELL: strongest glow
                    css_rules.append(f"{sel} {{ background: #2563eb !important; color: #ffffff !important; font-weight: 900 !important; box-shadow: inset 0 0 0 2.5px #38bdf8, inset 0 0 18px rgba(56,189,248,0.65) !important; z-index: 6 !important; }}")
                elif is_same_num:
                    # Tier 2 — MATCHING NUMBERS: vibrant blue, both fixed and player
                    css_rules.append(f"{sel} {{ background: #1e40af !important; color: #ffffff !important; font-weight: 800 !important; box-shadow: inset 0 0 0 2px #60a5fa, inset 0 0 10px rgba(96,165,250,0.4) !important; z-index: 5 !important; }}")
                elif is_in_sel_box:
                    # Tier 3 — SELECTED 3×3 BOX
                    if is_fixed:
                        css_rules.append(f"{sel} {{ background: #152035 !important; color: #f8fafc !important; font-weight: 800 !important; }}")
                    elif val != 0:
                        css_rules.append(f"{sel} {{ background: #13203a !important; color: #38bdf8 !important; font-weight: 700 !important; }}")
                    else:
                        css_rules.append(f"{sel} {{ background: #0f1a2e !important; color: #475569 !important; }}")
                elif is_fixed:
                    # Tier 4 — DEFAULT FIXED CLUE
                    css_rules.append(f"{sel} {{ background: #0f172a !important; color: #f8fafc !important; font-weight: 800 !important; }}")
                elif val != 0:
                    # Tier 4 — DEFAULT PLAYER NUMBER
                    css_rules.append(f"{sel} {{ background: #0a1122 !important; color: #38bdf8 !important; font-weight: 700 !important; }}")
                else:
                    # Tier 4 — DEFAULT EMPTY CELL
                    css_rules.append(f"{sel} {{ background: #070c18 !important; color: #475569 !important; }}")

                if has_notes:
                    css_rules.append(f"{sel} {{ font-size: 0.85rem !important; line-height: 1.1 !important; font-family: monospace !important; color: #94a3b8 !important; white-space: pre-line !important; font-weight: 600 !important; }}")

                # Thick 3x3 Boundaries
                if c == 2 or c == 5:
                    css_rules.append(f"{sel} {{ border-right: 3.5px solid #cbd5e1 !important; }}")
                if r == 2 or r == 5:
                    css_rules.append(f"{sel} {{ border-bottom: 3.5px solid #cbd5e1 !important; }}")

        full_custom_css = "\n".join(css_rules)

        st.markdown(f"""
        <style>
            /* Center Board Column */
            div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:first-child {{
                display: flex !important;
                flex-direction: column !important;
                align-items: center !important;
                justify-content: flex-start !important;
            }}

            /* True CSS Grid for 9x9 Sudoku */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) {{
                display: grid !important;
                grid-template-columns: repeat(9, 68px) !important;
                grid-template-rows: repeat(9, 68px) !important;
                gap: 0px !important;
                width: 612px !important;
                height: 612px !important;
                margin: 0 auto !important;
                padding: 0px !important;
                border: 3.5px solid #cbd5e1 !important;
                border-radius: 8px !important;
                overflow: hidden !important;
                background: #1e293b !important;
                box-shadow: 0 10px 25px rgba(0,0,0,0.5), 0 0 15px rgba(56,189,248,0.1) !important;
            }}

            /* Hide the marker itself so it doesn't take up a grid slot */
            div.element-container:has(.sudoku-grid-marker) {{
                display: none !important;
            }}

            /* Reset Element Container inside Grid */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container {{
                width: 68px !important;
                height: 68px !important;
                margin: 0 !important;
                padding: 0 !important;
            }}

            /* 9x9 Individual Square Cell Button */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container button {{
                width: 68px !important;
                height: 68px !important;
                min-width: 68px !important;
                max-width: 68px !important;
                min-height: 68px !important;
                max-height: 68px !important;
                padding: 0px !important;
                margin: 0px !important;
                border-radius: 0px !important;
                font-family: 'JetBrains Mono', -apple-system, sans-serif !important;
                font-size: 2.5rem !important;
                font-weight: 900 !important;
                line-height: 1 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                text-align: center !important;
                box-sizing: border-box !important;
                border: none !important;
                border-right: 1px solid #1e293b !important;
                border-bottom: 1px solid #1e293b !important;
                transition: background 0.1s ease, color 0.1s ease, box-shadow 0.1s ease !important;
            }}

            /* Override inner elements to prevent shrinking or misaligning */
            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container button p,
            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container button div,
            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container button span {{
                font-size: inherit !important;
                font-weight: inherit !important;
                line-height: inherit !important;
                font-family: inherit !important;
                color: inherit !important;
                padding: 0px !important;
                margin: 0px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                width: 100% !important;
                height: 100% !important;
            }}

            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container button:hover {{
                box-shadow: inset 0 0 0 2px #38bdf8 !important;
                z-index: 3 !important;
            }}

            div[data-testid="stVerticalBlock"]:has(> div.element-container .sudoku-grid-marker) > div.element-container button:disabled {{
                opacity: 1 !important;
                cursor: default !important;
            }}

            /* Keypad Tray Styling */
            div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child button {{
                font-family: 'JetBrains Mono', -apple-system, sans-serif !important;
                font-size: 1.25rem !important;
                font-weight: 700 !important;
                border-radius: 8px !important;
                background: #0f172a !important;
                border: 1px solid #1e293b !important;
                color: #38bdf8 !important;
                transition: all 0.15s ease !important;
            }}
            div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"]:last-child button:hover {{
                border-color: #38bdf8 !important;
                background: #1e293b !important;
            }}

            /* Dynamic Cell State Highlights */
            {full_custom_css}
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown("<div class='sudoku-grid-marker'></div>", unsafe_allow_html=True)
            for r in range(9):
                for c in range(9):
                    val = engine.current_board[r][c]
                    if val != 0:
                        btn_label = str(val)
                    else:
                        notes = st.session_state.sudoku_notes.get((r, c), set())
                        if notes:
                            # 3x3 notes grid
                            lines = []
                            for nr in range(3):
                                row_str = ""
                                for nc in range(3):
                                    n = nr * 3 + nc + 1
                                    row_str += str(n) if n in notes else " "
                                    row_str += " "
                                lines.append(row_str.rstrip())
                            btn_label = "\n".join(lines)
                        else:
                            btn_label = " "

                    if st.button(
                        btn_label,
                        key=f"su_cell_{r}_{c}",
                        disabled=engine.is_game_over or engine.is_completed
                    ):
                        st.session_state.sudoku_selected = (r, c)
                        st.rerun()

        # Board Legend
        st.markdown("""
<div style="width: 612px; margin: 12px auto 0 auto; display:flex; justify-content:space-between; font-size:0.8rem; color:#94a3b8; padding: 6px 14px; background: rgba(15,23,42,0.6); border-radius: 6px; box-sizing: border-box;">
<span>⚪ <b>Fixed Numbers</b></span>
<span>🔵 <b>Player Numbers</b></span>
<span>🟦 <b>Selected / All Matching</b></span>
</div>
""", unsafe_allow_html=True)

    with col_side:
        with st.container(border=True):
            is_fixed_sel = (sel_r, sel_c) in engine.initial_fixed
            cell_type_label = "🔒 Fixed Starting Number" if is_fixed_sel else ("Empty Cell" if sel_val == 0 else f"Current Value: {sel_val}")

            st.markdown(f"""
            <div style="margin-bottom:8px;">
                <span style="color:#94a3b8; font-size:0.8rem;">SELECTED CELL:</span><br>
                <b style="color:#38bdf8; font-size:1.1rem;">Row {sel_r+1}, Column {sel_c+1}</b>
                <div style="color:#64748b; font-size:0.8rem;">{cell_type_label}</div>
            </div>
            """, unsafe_allow_html=True)

            # Smart Keypad (Completed numbers disabled/removed)
            completed_numbers = engine.get_completed_numbers()

            # 3x3 Digit Numpad
            np1, np2, np3 = st.columns(3)
            for num, col in zip([1, 2, 3], [np1, np2, np3]):
                is_num_done = num in completed_numbers
                with col:
                    btn_text = f"{num} ✓" if is_num_done else str(num)
                    if st.button(btn_text, key=f"np_{num}", disabled=is_num_done or is_fixed_sel or engine.is_game_over or engine.is_completed):
                        _handle_keypad_digit(engine, sel_r, sel_c, num)

            np4, np5, np6 = st.columns(3)
            for num, col in zip([4, 5, 6], [np4, np5, np6]):
                is_num_done = num in completed_numbers
                with col:
                    btn_text = f"{num} ✓" if is_num_done else str(num)
                    if st.button(btn_text, key=f"np_{num}", disabled=is_num_done or is_fixed_sel or engine.is_game_over or engine.is_completed):
                        _handle_keypad_digit(engine, sel_r, sel_c, num)

            np7, np8, np9 = st.columns(3)
            for num, col in zip([7, 8, 9], [np7, np8, np9]):
                is_num_done = num in completed_numbers
                with col:
                    btn_text = f"{num} ✓" if is_num_done else str(num)
                    if st.button(btn_text, key=f"np_{num}", disabled=is_num_done or is_fixed_sel or engine.is_game_over or engine.is_completed):
                        _handle_keypad_digit(engine, sel_r, sel_c, num)

            st.divider()

            # Pencil Mode Toggle & Action Controls
            col_pencil, col_clr = st.columns(2)
            with col_pencil:
                pencil_active = st.session_state.sudoku_pencil_mode
                pencil_label = "✏️ Notes: ON" if pencil_active else "✏️ Notes: OFF"
                if st.button(pencil_label, key="sdk_toggle_pencil"):
                    st.session_state.sudoku_pencil_mode = not pencil_active
                    st.rerun()

            with col_clr:
                if st.button("⌫ Clear", key="np_clr", disabled=is_fixed_sel or engine.is_game_over or engine.is_completed):
                    _handle_clear(engine, sel_r, sel_c)

            col_hnt, col_und = st.columns(2)
            with col_hnt:
                if st.button("💡 Hint", key="np_hnt", disabled=engine.is_game_over or engine.is_completed):
                    _handle_hint(engine)

            with col_und:
                if st.button("↶ Undo", key="np_und", disabled=engine.is_game_over or engine.is_completed):
                    _handle_undo(engine)

            st.divider()

            st.divider()
            if st.button("🧠 HOW AI SOLVES", key="btn_sdk_how_ai_solves"):
                st.session_state.sdk_show_how_ai_solves = not st.session_state.get("sdk_show_how_ai_solves", False)
                st.rerun()

            if st.button("🔄 New Puzzle", key="sdk_rst_btn_side"):
                st.session_state.sudoku_engine = SudokuEngine(difficulty=st.session_state.sudoku_difficulty)
                st.session_state.sudoku_start_time = time.time()
                st.session_state.sudoku_completed_time = None
                st.session_state.sudoku_notes = {}
                st.session_state.sudoku_feedback = None
                st.session_state.sudoku_selected = (0, 0)
                st.rerun()

            if st.session_state.sudoku_feedback:
                st.info(st.session_state.sudoku_feedback)


def _handle_keypad_digit(engine: SudokuEngine, r: int, c: int, num: int):
    """Handles digit input for either normal move or pencil notes."""
    if (r, c) in engine.initial_fixed or engine.is_game_over or engine.is_completed:
        return

    # Notes / Pencil Mode Active
    if st.session_state.sudoku_pencil_mode:
        if engine.current_board[r][c] == 0:
            cell_notes = st.session_state.sudoku_notes.setdefault((r, c), set())
            if num in cell_notes:
                cell_notes.remove(num)
                st.session_state.sudoku_feedback = f"✏️ Removed note {num} at R{r+1}C{c+1}."
            else:
                cell_notes.add(num)
                st.session_state.sudoku_feedback = f"✏️ Added note {num} at R{r+1}C{c+1}."
            st.rerun()
    else:
        # Normal Placement Mode
        res = engine.make_move(r, c, num)
        # Clear notes on this cell upon placing number
        st.session_state.sudoku_notes.pop((r, c), None)

        if res.get("status") == "mistake":
            st.session_state.sudoku_feedback = f"❌ Incorrect digit at R{r+1}C{c+1}. Strike {res['mistakes']}/3!"
        elif res.get("status") == "valid":
            st.session_state.sudoku_feedback = f"✓ Placed {num} at R{r+1}C{c+1}."
            # Remove placed number from notes of peers
            for i in range(9):
                st.session_state.sudoku_notes.get((r, i), set()).discard(num)
                st.session_state.sudoku_notes.get((i, c), set()).discard(num)
            br, bc = (r // 3) * 3, (c // 3) * 3
            for i in range(br, br + 3):
                for j in range(bc, bc + 3):
                    st.session_state.sudoku_notes.get((i, j), set()).discard(num)
        elif res.get("status") == "completed":
            st.session_state.sudoku_completed_time = int(time.time() - st.session_state.sudoku_start_time)
            st.session_state.sudoku_feedback = "🏆 Matrix Completely Satisfied!"
        st.rerun()


def _handle_clear(engine: SudokuEngine, r: int, c: int):
    """Clears either placed number or candidate notes on selected cell."""
    if (r, c) in engine.initial_fixed or engine.is_game_over or engine.is_completed:
        return
    st.session_state.sudoku_notes.pop((r, c), None)
    engine.make_move(r, c, 0)
    st.session_state.sudoku_feedback = f"Cleared cell at R{r+1}C{c+1}."
    st.rerun()


def _handle_undo(engine: SudokuEngine):
    """Undoes the previous move."""
    if engine.is_game_over or engine.is_completed:
        return
    res = engine.undo_move()
    if res.get("status") == "undone":
        st.session_state.sudoku_feedback = f"↶ Reverted move at R{res['cell'][0]+1}C{res['cell'][1]+1}."
        st.rerun()


def _handle_hint(engine: SudokuEngine):
    """Generates an accurate solution hint for one unassigned cell."""
    if engine.is_game_over or engine.is_completed:
        return
    hint = engine.get_hint()
    if hint:
        st.session_state.sudoku_feedback = f"💡 Hint: R{hint['row']+1}C{hint['col']+1} is **{hint['correct_value']}**"
        st.session_state.sudoku_selected = (hint['row'], hint['col'])
        st.rerun()


def _render_ai_sim_mode(engine: SudokuEngine):
    """Renders the Step-by-Step AI CSP Backtracking & MRV Simulation."""



    st.markdown("""
<div style="background:rgba(15,23,42,0.6); padding: 16px; border-radius: 8px; margin-bottom: 20px;">
<h3 style="color:#38bdf8; margin-top:0;">🧠 HOW AI SOLVES: QUANTUM SUDOKU</h3>

<b>ALGORITHM:</b> Constraint Satisfaction Problem (CSP) + Backtracking Search + Minimum Remaining Values (MRV) Heuristic.<br/><br/>

<b>WHY THIS ALGORITHM?</b><br/>
Sudoku is a classic CSP. While naive backtracking (brute-force) would evaluate an astronomically large state space, applying constraints (row, col, 3x3 box) drastically prunes invalid paths. The MRV heuristic optimally selects the cell with the fewest possible legal moves, accelerating the search.<br/><br/>

<b>STATE REPRESENTATION:</b><br/>
An 81-variable grid where each cell variable $X_{i,j}$ has an initial domain $D \in \{1..9\}$. Fixed clues are assigned single-value domains.<br/><br/>

<b>HOW IT SEARCHES / REASONS:</b><br/>
1. <b>MRV Selection:</b> Scans all empty cells and selects the one with the smallest legal domain.<br/>
2. <b>Assignment:</b> Attempts a valid digit.<br/>
3. <b>Forward Checking / Constraint Propagation:</b> Checks if assigning the digit violates any adjacent constraints. If it hits a dead-end, it backtracks to the previous decision node.<br/><br/>
<hr style="border-top:1px solid rgba(56,189,248,0.3); margin: 10px 0;"/>
<b>⏱️ COMPLEXITY ANALYSIS</b><br/><br/>
<b>Time Complexity:</b> O(9^N)<br/>
<b>Space Complexity:</b> O(N)<br/><br/>
<i style="color:#94a3b8; font-size:0.85rem;">N = number of unknown/unassigned variables or cells</i>
</div>
""", unsafe_allow_html=True)

    if st.session_state.sudoku_sim_trace is None:
        if st.button("▶ INITIALIZE & GENERATE AI CSP TRACE", key="sdk_init_sim_btn"):
            res = engine.solve_csp_with_trace(max_trace_steps=120)
            st.session_state.sudoku_sim_trace = res["trace"]
            st.session_state.sudoku_sim_stats = res["stats"]
            st.session_state.sudoku_sim_solution = res["solution"]
            st.session_state.sudoku_sim_step = 0
            st.rerun()
    else:
        trace = st.session_state.sudoku_sim_trace
        stats = st.session_state.sudoku_sim_stats
        curr_step_idx = st.session_state.sudoku_sim_step
        max_steps = len(trace)

        # Simulation Controls
        c_ctrl1, c_ctrl2, c_ctrl3, c_ctrl4 = st.columns([1.2, 1.2, 1.5, 1.5])
        with c_ctrl1:
            if st.button("⏭ Next Step", key="sdk_sim_next_btn", disabled=curr_step_idx >= max_steps - 1):
                st.session_state.sudoku_sim_step = min(max_steps - 1, curr_step_idx + 1)
                st.rerun()
        with c_ctrl2:
            if st.button("⏮ Prev Step", key="sdk_sim_prev_btn", disabled=curr_step_idx <= 0):
                st.session_state.sudoku_sim_step = max(0, curr_step_idx - 1)
                st.rerun()
        with c_ctrl3:
            if st.button("⚡ Fast Forward to End", key="sdk_sim_ff_btn"):
                st.session_state.sudoku_sim_step = max_steps - 1
                if st.session_state.sudoku_sim_solution:
                    pass # Removed engine mutation to comply with isolated simulation rules
                    pass
                st.rerun()
        with c_ctrl4:
            if st.button("🔄 Reset Simulation", key="sdk_sim_rst_btn"):
                st.session_state.sudoku_sim_trace = None
                st.session_state.sudoku_sim_stats = None
                st.session_state.sudoku_sim_step = 0
                st.rerun()

        # Step Progress
        st.progress((curr_step_idx + 1) / max_steps, text=f"Step {curr_step_idx + 1} of {max_steps}")

        curr_event = trace[curr_step_idx] if curr_step_idx < max_steps else trace[-1]

        # Layout: Live AI Board + Step Rationale Box
        col_b, col_info = st.columns([1.6, 0.95])

        with col_b:
            active_board = curr_event.get("board_snapshot", engine.current_board)
            active_cell = curr_event.get("cell", (-1, -1))

            for r in range(9):
                row_cols = st.columns(9)
                for c in range(9):
                    val = active_board[r][c]
                    is_active = (r, c) == active_cell
                    label = str(val) if val != 0 else " "
                    with row_cols[c]:
                        st.button(label, key=f"sim_c_{r}_{c}", disabled=True)

        with col_info:
            with st.container(border=True):
                st.markdown(f"#### 🔍 Current Step: `{curr_event.get('action', '').upper()}`")
                st.markdown(f"**Target Cell:** `R{curr_event.get('cell', (0,0))[0]+1}C{curr_event.get('cell', (0,0))[1]+1}`")
                st.markdown(f"**Decision Detail:**\n\n`{curr_event.get('desc', '')}`")

                st.divider()
                st.markdown("##### 📊 Authentic CSP Solver Telemetry")
                st.markdown(f"• **Solve Time:** `{stats.get('elapsed_ms', 0)} ms`")
                st.markdown(f"• **Variable Assignments:** `{stats.get('assignments', 0)}`")
                st.markdown(f"• **Backtracks Executed:** `{stats.get('backtracks', 0)}`")
                st.markdown(f"• **MRV Variable Selections:** `{stats.get('mrv_selections', 0)}`")
                st.markdown(f"• **Search Nodes Expanded:** `{stats.get('nodes_expanded', 0)}`")
