# Future Scope & Limitations

## 1. Current Limitations
1. **Discrete Deterministic Physics**: The environment models discrete state steps with deterministic action outcomes. Real-world escape rooms feature continuous physical interactions and stochastic sensor noise.
2. **Synchronous Single-Agent Mode**: The current planner handles single-agent navigation. Multi-agent cooperative escape scenarios where two agents must simultaneously hold levers in separate rooms require distributed planning.
3. **Synthetic Telemetry Scaling**: While the synthetic telemetry distribution closely mirrors empirical human gameplay studies, real-world human data collection across large player pools would further refine cluster boundaries.

---

## 2. Future Research Extensions
1. **Partial-Order Planning (POP) & PDDL Parser**:
   Integrating an automated PDDL (Planning Domain Definition Language) parser to allow non-technical puzzle designers to create new escape rooms via text specifications.
2. **Reinforcement Learning (Q-Learning / PPO Agent)**:
   Training a deep reinforcement learning agent to learn escape policies through trial-and-error rewards rather than classical state-space search.
3. **Ontology Web Language (OWL) & DL Reasoners**:
   Expanding propositional Horn clauses to Description Logic ontologies evaluated via HermiT or Pellet reasoners.
4. **VR/AR Spatial Integration**:
   Porting the state machine and inference engine as a backend brain for Unity/Unreal-based Virtual Reality escape rooms.
