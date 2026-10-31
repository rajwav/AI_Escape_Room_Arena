"""
AI ESCAPE ROOM — Core Game Module (3-Column Layout & Tactical HUD)
Features:
- 3-Column Tactical HUD (Facility Map, Active Sector, Operative Inventory & Working Memory)
- Forward Chaining Knowledge Representation (Horn Clauses & Proof Tree)
- CSP Backtracking Vault & Reagent Locks
- "WATCH AI SOLVE" A* Heuristic Search & Automated Planner Simulation
- Real A* Telemetry (g(s), h(s), f(s), nodes explored, runtime ms)
- Adaptive Difficulty & Deterministic Scoring
"""

import streamlit as st
import time
import os
import sys

src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from environment import EscapeRoomEnvironment, GameState
from search_algorithms import EscapeRoomSearchPlanner
from scoring_engine import ScoringEngine
from adaptive_difficulty import PlayerTelemetry


def render_escape_room_game():
    """Renders the 3-Column Escape Room Game HUD & AI Search Simulation."""
    st.markdown("""
<div class="hud-card">
<div class="card-title">🔐 AI ESCAPE ROOM: AUTONOMOUS REASONING & SEARCH</div>
<p style="color:#94a3b8; font-size:0.85rem; margin:0;">
Navigate sectors, synthesize clues via Forward Chaining, solve CSP locks, or engage <b>Watch AI Solve</b> to see A* Path Planning in action.
</p>
</div>
""", unsafe_allow_html=True)

    if "er_env" not in st.session_state:
        st.session_state.er_env = EscapeRoomEnvironment()
        st.session_state.er_state = st.session_state.er_env.get_initial_state()
        st.session_state.er_telemetry = PlayerTelemetry()
        st.session_state.er_action_log = ["System initialized in Sector 01: Foyer."]
        st.session_state.er_start_time = time.time()
        st.session_state.er_completed_time = None
        st.session_state.er_feedback = None
        st.session_state.er_ai_step = 0
        st.session_state.er_ai_plan = None

    env: EscapeRoomEnvironment = st.session_state.er_env
    state: GameState = st.session_state.er_state

    _render_human_play_mode(env, state)

    if st.session_state.get("er_show_how_ai_solves", False):
        st.divider()
        _render_ai_autoplay_mode(env)


def _render_human_play_mode(env: EscapeRoomEnvironment, state: GameState):
    col_map, col_puzzle, col_hud = st.columns([1.1, 2.0, 1.2])

    # --------------------------------------------------------------------------
    # COLUMN 1: LEFT — FACILITY MAP
    # --------------------------------------------------------------------------
    with col_map:
        st.markdown("""
<div class="hud-card">
<div class="card-title">🗺️ FACILITY BLUEPRINT</div>
</div>
""", unsafe_allow_html=True)

        facility_rooms = [
            ("Foyer", "Sector 01", "Entrance & Grand Hall"),
            ("Library", "Sector 02", "Ancient Manuscripts & Archive"),
            ("Laboratory", "Sector 03", "Chemical Synthesis Bench"),
            ("Secret_Vault", "Sector 04", "Heavy Titanium Vault Lock"),
            ("Escape_Portal", "Sector 05", "Exit Wormhole Matrix")
        ]

        facts_set = set(state.world_facts)
        inv_set = set(state.inventory)

        for room_id, sector_code, room_desc in facility_rooms:
            is_current = (state.current_room == room_id)
            is_completed = False
            is_locked = False
            lock_reason = ""

            if room_id == "Foyer":
                is_completed = "has(brass_key)" in facts_set or "brass_key" in inv_set
            elif room_id == "Library":
                is_completed = "has(uv_torch)" in facts_set or "revealed(cipher_formula)" in facts_set
            elif room_id == "Laboratory":
                is_completed = "known(vault_code_375)" in facts_set and ("has(corrosion_acid)" in facts_set or "corrosion_acid" in inv_set)
            elif room_id == "Secret_Vault":
                if not ("known(vault_code_375)" in facts_set or "vault_unlocked" in facts_set):
                    is_locked = True
                    lock_reason = "Requires Vault Code 375"
                is_completed = "has(master_crystal)" in facts_set or "master_crystal" in inv_set
            elif room_id == "Escape_Portal":
                if not ("has(master_crystal)" in facts_set or "master_crystal" in inv_set):
                    is_locked = True
                    lock_reason = "Requires Master Crystal"
                is_completed = "portal_activated" in facts_set

            if is_current:
                node_class = "room-node room-node-active"
                badge = '<span class="room-badge" style="background:#00ffcc; color:#050811;">📍 CURRENT LOCATION</span>'
            elif is_completed:
                node_class = "room-node room-node-completed"
                badge = '<span class="room-badge" style="background:rgba(16,185,129,0.25); color:#34d399;">✓ SECURED</span>'
            elif is_locked:
                node_class = "room-node room-node-locked"
                badge = f'<span class="room-badge" style="background:rgba(239,68,68,0.2); color:#f87171;">🔒 {lock_reason}</span>'
            else:
                node_class = "room-node"
                badge = '<span class="room-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">🔓 UNLOCKED</span>'

            st.markdown(f"""
            <div class="{node_class}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.75rem; color:#94a3b8; font-family:monospace;">{sector_code}</span>
                    {badge}
                </div>
                <div class="room-name">{room_id.replace('_', ' ')}</div>
                <div style="font-size:0.75rem; color:#64748b;">{room_desc}</div>
            </div>
            """, unsafe_allow_html=True)

        completed_count = sum(1 for r, _, _ in facility_rooms if r == state.current_room or (r == "Foyer" and "has(brass_key)" in facts_set) or (r == "Library" and "revealed(cipher_formula)" in facts_set) or (r == "Laboratory" and "known(vault_code_375)" in facts_set) or (r == "Secret_Vault" and "has(master_crystal)" in facts_set) or (r == "Escape_Portal" and "portal_activated" in facts_set))
        pct = min(100, int((completed_count / 5.0) * 100))
        st.markdown(f"""
        <div style="margin-top:12px;">
            <div style="display:flex; justify-content:space-between; font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">
                <span>SECTOR BREACH PROGRESS</span>
                <span><b>{pct}%</b></span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(pct / 100.0)

    # --------------------------------------------------------------------------
    # COLUMN 2: CENTER — GAMEPLAY ARENA
    # --------------------------------------------------------------------------
    with col_puzzle:
        curr = state.current_room

        if env.is_goal_state(state):
            if st.session_state.er_completed_time is None:
                st.session_state.er_completed_time = int(time.time() - st.session_state.er_start_time)

            final_time = st.session_state.er_completed_time
            score_res = ScoringEngine.calculate_game_score(
                game_id="escape_room",
                solved=True,
                time_seconds=final_time,
                moves_count=st.session_state.er_telemetry.total_actions
            )

            st.balloons()
            st.markdown(f"""
            <div class="hud-card" style="border: 2px solid #00ffcc; text-align:center; background:rgba(0,255,204,0.08);">
                <h2 style="color:#00ffcc; margin:0 0 6px 0;">🎉 MISSION ACCOMPLISHED!</h2>
                <h4 style="color:#f8fafc; margin-top:0;">WORMHOLE PORTAL STABILIZED & ESCAPE SUCCESSFUL</h4>
                <div style="display:flex; justify-content:center; gap:36px; margin:20px 0;">
                    <div>
                        <div style="color:#94a3b8; font-size:0.8rem;">FINAL SCORE</div>
                        <div style="font-size:2.2rem; font-weight:900; color:#00ffcc; font-family:monospace;">{score_res['score']:,}</div>
                    </div>
                    <div>
                        <div style="color:#94a3b8; font-size:0.8rem;">ESCAPE TIME</div>
                        <div style="font-size:2.2rem; font-weight:900; color:#38bdf8; font-family:monospace;">{final_time // 60:02d}:{final_time % 60:02d}</div>
                    </div>
                    <div>
                        <div style="color:#94a3b8; font-size:0.8rem;">ACTIONS LOGGED</div>
                        <div style="font-size:2.2rem; font-weight:900; color:#a855f7; font-family:monospace;">{st.session_state.er_telemetry.total_actions}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚀 RESTART ESCAPE ROOM", key="er_restart_btn"):
                st.session_state.er_env = EscapeRoomEnvironment()
                st.session_state.er_state = st.session_state.er_env.get_initial_state()
                st.session_state.er_telemetry = PlayerTelemetry()
                st.session_state.er_action_log = ["System restarted by operator."]
                st.session_state.er_start_time = time.time()
                st.session_state.er_completed_time = None
                st.session_state.er_feedback = None
                st.rerun()

        else:
            room_objectives = {
                "Foyer": {
                    "objective": "Locate the antique Brass Key hidden inside the entrance hall to unlock the Library archives.",
                    "clue": "An ornate brass key rests on the foyer mantelpiece.",
                    "icon": "🏛️"
                },
                "Library": {
                    "objective": "Inspect the Ancient Manuscript and find the UV Torch inside the locked cabinet to illuminate the hidden cipher.",
                    "clue": "An ancient manuscript sits on the study desk. An antique glass cabinet is locked with a brass mechanism.",
                    "icon": "📚"
                },
                "Laboratory": {
                    "objective": "Collect Chemical Reagents to synthesize Corrosion Acid, and cross-reference the Lab Notebook to solve the 3-Digit Vault CSP PIN.",
                    "clue": "Chemical synthesis apparatus is online. Lab notebook contains notes correlating with the UV cipher.",
                    "icon": "🧪"
                },
                "Secret_Vault": {
                    "objective": "Apply the potent Corrosion Acid to dissolve the safe's titanium hinges and extract the Master Crystal.",
                    "clue": "A massive reinforced vault safe houses the primary power crystal.",
                    "icon": "🔐"
                },
                "Escape_Portal": {
                    "objective": "Slot the Master Crystal into the central pedestal to energize the dimensional exit wormhole.",
                    "clue": "The escape gateway is dormant, awaiting the resonance frequency of the Master Crystal.",
                    "icon": "🌀"
                }
            }

            info = room_objectives.get(curr, {"objective": "Explore and solve room puzzles.", "clue": "Sensors nominal.", "icon": "📍"})

            st.markdown(f"""
            <div class="hud-card">
                <div class="card-title">{info['icon']} SECTOR ACTIVE: {curr.replace('_', ' ').upper()}</div>
                <div style="margin-bottom:12px;">
                    <span style="color:#00ffcc; font-weight:700; font-size:0.85rem; text-transform:uppercase;">🎯 Mission Objective:</span>
                    <div style="color:#f8fafc; font-size:0.95rem; margin-top:2px;">{info['objective']}</div>
                </div>
                <div style="background:rgba(15,23,42,0.6); border-left:3px solid #38bdf8; padding:8px 12px; border-radius:4px; font-size:0.85rem; color:#cbd5e1;">
                    <b>📡 Sensor Feed:</b> {info['clue']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.er_feedback:
                st.markdown(st.session_state.er_feedback, unsafe_allow_html=True)

            successors = env.get_successors(state)

            st.markdown("""
<div style="font-family:'Consolas',monospace; font-size:0.9rem; font-weight:700; color:#38bdf8; margin:14px 0 8px 0;">
⚡ AVAILABLE TACTICAL ACTIONS
</div>
""", unsafe_allow_html=True)

            if successors:
                def format_action_label(raw_action: str) -> str:
                    if raw_action.startswith("MOVE("):
                        target = raw_action[5:-1].replace('_', ' ')
                        return f"🚪 ENTER {target.upper()}"
                    elif "TAKE(brass_key)" in raw_action:
                        return "🗝️ TAKE BRASS KEY"
                    elif "EXAMINE(ancient_manuscript)" in raw_action:
                        return "📜 EXAMINE ANCIENT MANUSCRIPT"
                    elif "UNLOCK_CABINET_AND_TAKE(uv_torch)" in raw_action:
                        return "🔦 UNLOCK CABINET & TAKE UV TORCH"
                    elif "EXAMINE(lab_notebook)" in raw_action:
                        return "📓 EXAMINE LAB NOTEBOOK"
                    elif "TAKE(chemical_reagents)" in raw_action:
                        return "🧪 COLLECT CHEMICAL REAGENTS"
                    elif "SYNTHESIZE_ACID_CSP" in raw_action:
                        return "⚗️ SYNTHESIZE CORROSION ACID (CSP SOLVER)"
                    elif "UNLOCK_VAULT_DOOR" in raw_action:
                        return "🔐 UNLOCK VAULT DOOR (CODE 3-5-7)"
                    elif "MELT_SAFE_AND_TAKE" in raw_action:
                        return "💎 DISSOLVE SAFE HINGES & TAKE MASTER CRYSTAL"
                    elif "ACTIVATE_ESCAPE_PORTAL" in raw_action:
                        return "🌀 ENERGIZE & ACTIVATE ESCAPE PORTAL"
                    return f"👉 {raw_action}"

                for idx, (raw_act, next_s, cost) in enumerate(successors):
                    btn_label = format_action_label(raw_act)
                    if st.button(btn_label, key=f"er_act_{idx}"):
                        st.session_state.er_telemetry.log_action(raw_act, valid=True, room=next_s.current_room)
                        st.session_state.er_action_log.append(f"Executed {btn_label}")

                        new_facts = set(next_s.world_facts) - set(state.world_facts)
                        if new_facts:
                            facts_str = ", ".join([f"<code>{f}</code>" for f in new_facts])
                            st.session_state.er_feedback = f"""
                            <div class="feedback-success">
                                <b>✓ ACTION EXECUTED:</b> {btn_label}<br>
                                <span style="font-size:0.8rem;">🧠 <b>AI Inference Derived New Facts:</b> {facts_str}</span>
                            </div>
                            """
                        else:
                            st.session_state.er_feedback = f"""
                            <div class="feedback-info">
                                <b>✓ NAVIGATED:</b> Moved to {next_s.current_room.replace('_', ' ')}.
                            </div>
                            """
                        st.session_state.er_state = next_s
                        st.rerun()

    # --------------------------------------------------------------------------
    # COLUMN 3: RIGHT — OPERATIVE HUD
    # --------------------------------------------------------------------------
    with col_hud:
        st.markdown(f"""
        <div class="hud-card">
            <div class="card-title">👤 OPERATIVE STATUS</div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#94a3b8; font-size:0.8rem;">Vital Status:</span>
                <span style="color:#34d399; font-weight:700; font-size:0.8rem;">100% NOMINAL</span>
            </div>
            <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                <span style="color:#94a3b8; font-size:0.8rem;">Actions Executed:</span>
                <span style="color:#38bdf8; font-weight:700; font-size:0.8rem;">{st.session_state.er_telemetry.total_actions}</span>
            </div>
            <div style="display:flex; justify-content:space-between;">
                <span style="color:#94a3b8; font-size:0.8rem;">Puzzles Solved:</span>
                <span style="color:#a855f7; font-weight:700; font-size:0.8rem;">{len(state.solved_puzzles)} / 2 CSP</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
<div class="hud-card">
<div class="card-title">🎒 TACTICAL INVENTORY</div>
""", unsafe_allow_html=True)

        inv_items_meta = {
            "brass_key": ("🗝️ Brass Key", "Unlocks Library Antique Cabinet"),
            "uv_torch": ("🔦 UV Torch", "Illuminates Invisible Ultraviolet Ink"),
            "reagent_a": ("🧪 Chemical Reagent Alpha", "Acid Precursor Component"),
            "reagent_b": ("🧪 Chemical Reagent Beta", "Acid Precursor Component"),
            "corrosion_acid": ("⚗️ Corrosion Acid", "Dissolves Titanium Safe Hinges"),
            "master_crystal": ("💎 Master Crystal", "Resonance Core for Escape Portal")
        }

        if state.inventory:
            for item in state.inventory:
                item_name, item_desc = inv_items_meta.get(item, (f"📦 {item}", "Inventory Object"))
                st.markdown(f"""
                <div class="inv-item-card">
                    <div>
                        <div class="inv-item-name">{item_name}</div>
                        <div style="font-size:0.72rem; color:#94a3b8;">{item_desc}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div style="color:#64748b; font-size:0.8rem; font-style:italic;">Inventory empty. Collect sector items.</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="hud-card">
            <div class="card-title">🧠 WORKING MEMORY ({len(state.world_facts)})</div>
            <div style="max-height: 160px; overflow-y: auto; padding-right: 4px;">
        """, unsafe_allow_html=True)

        for f in sorted(state.world_facts):
            is_derived = any(f.startswith(p) for p in ["revealed", "known", "cabinet", "synthesized", "safe", "portal", "vault"])
            chip_class = "fact-chip fact-derived" if is_derived else "fact-chip fact-observed"
            st.markdown(f'<span class="{chip_class}">{f}</span>', unsafe_allow_html=True)

        st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.divider()
        if st.button("🧠 HOW AI SOLVES", key="btn_er_how_ai_solves"):
            st.session_state.er_show_how_ai_solves = not st.session_state.get("er_show_how_ai_solves", False)
            st.rerun()


def _render_ai_autoplay_mode(env: EscapeRoomEnvironment):
    st.markdown("""
<div style="background:rgba(15,23,42,0.8); padding: 15px; border-radius: 8px; border: 1px solid #38bdf8; margin-top:10px;">
<h4 style="color:#38bdf8; margin-top:0;">🤖 HOW AI SOLVES: A* HEURISTIC SEARCH</h4>
<b>ALGORITHM:</b> A* Search Algorithm & Forward Chaining.<br/><br/>
<b>WHY THIS ALGORITHM?</b><br/>
The Escape Room is a complex state-space planning problem. A* search optimally finds the shortest path of actions by minimizing $f(s) = g(s) + h(s)$. Forward chaining handles implicit knowledge discovery (e.g., combining items to unlock new facts) without exploding the search space.<br/><br/>
<b>STATE REPRESENTATION:</b><br/>
A `GameState` object containing: Current Room, Inventory (Set), and World Facts (Set).<br/><br/>
<b>HOW IT SEARCHES:</b><br/>
1. Explores valid transitions (Move, Interact, Synthesize).<br/>
2. Applies rules via Forward Chaining to derive new facts.<br/>
3. Evaluates $h(s)$ based on uncompleted milestones (keys needed, rooms unvisited).<br/>
4. Expands the node with the lowest $f(s)$ cost in the priority queue.<br/><br/>
<hr style="border-top:1px solid rgba(56,189,248,0.3); margin: 10px 0;"/>
<b>⏱️ COMPLEXITY ANALYSIS</b><br/><br/>
<b>Time Complexity:</b> O(b^d) worst case<br/>
<b>Space Complexity:</b> O(bd)<br/><br/>
<i style="color:#94a3b8; font-size:0.85rem;">b = branching factor<br/>d = search depth</i>
</div>
""", unsafe_allow_html=True)

    planner = EscapeRoomSearchPlanner(env)

    if st.session_state.er_ai_plan is None:
        if st.button("▶ INITIALIZE & PLAN OPTIMAL A* PATH", key="er_init_ai_plan_btn"):
            res = planner.a_star_search(env.get_initial_state())
            st.session_state.er_ai_plan = res
            st.session_state.er_ai_step = 0
            st.rerun()
    else:
        plan = st.session_state.er_ai_plan
        path = plan.solution_path
        curr_step = st.session_state.er_ai_step
        total_steps = len(path)

        # Controls
        c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.5, 1.2])
        with c1:
            if st.button("⏭ Next Action", key="er_ai_nxt_btn", disabled=curr_step >= total_steps - 1):
                st.session_state.er_ai_step = min(total_steps - 1, curr_step + 1)
                st.rerun()
        with c2:
            if st.button("⏮ Prev Action", key="er_ai_prv_btn", disabled=curr_step <= 0):
                st.session_state.er_ai_step = max(0, curr_step - 1)
                st.rerun()
        with c3:
            if st.button("⚡ Autoplay to End", key="er_ai_ff_btn"):
                st.session_state.er_ai_step = total_steps - 1
                st.rerun()
        with c4:
            if st.button("🔄 Reset Plan", key="er_ai_rst_btn"):
                st.session_state.er_ai_plan = None
                st.session_state.er_ai_step = 0
                st.rerun()

        st.progress((curr_step + 1) / total_steps, text=f"A* Plan Step {curr_step + 1} of {total_steps}")

        action_name, state_snapshot = path[curr_step]
        h_val = planner.calculate_heuristic(state_snapshot)
        g_val = curr_step
        f_val = g_val + h_val

        col_left, col_right = st.columns([1.5, 1.2])

        with col_left:
            st.markdown(f"""
            <div class="hud-card" style="border-color:#38bdf8;">
                <div class="card-title">📍 SECTOR: {state_snapshot.current_room.upper()}</div>
                <div style="font-size:1.1rem; color:#00ffcc; font-weight:bold; margin-bottom:8px;">
                    Action: <code>{action_name}</code>
                </div>
                <p style="color:#cbd5e1; font-size:0.9rem;">
                    <b>Inventory Held:</b> {', '.join(state_snapshot.inventory) if state_snapshot.inventory else 'None'}<br>
                    <b>Puzzles Solved:</b> {', '.join(state_snapshot.solved_puzzles) if state_snapshot.solved_puzzles else 'None'}<br>
                    <b>Total Facts:</b> {len(state_snapshot.world_facts)} active in knowledge base.
                </p>
            </div>
            """, unsafe_allow_html=True)

        with col_right:
            with st.container(border=True):
                st.markdown("#### 📊 A* Search Metrics")
                st.markdown(f"• **Heuristic $h(s)$:** `{h_val}` (Remaining Milestones)")
                st.markdown(f"• **Path Cost $g(s)$:** `{g_val}` (Steps Taken)")
                st.markdown(f"• **Evaluation $f(s)$:** `{f_val}`")
                st.markdown(f"• **Nodes Explored:** `{plan.nodes_explored}`")
                st.markdown(f"• **Peak Frontier:** `{plan.max_frontier_size}`")
                st.markdown(f"• **Execution Time:** `{plan.execution_time_ms:.3f} ms`")
