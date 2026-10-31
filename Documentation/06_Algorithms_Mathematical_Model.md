# Algorithms & Mathematical Models

## 1. Knowledge Representation & Forward Chaining

### Production Rule Formulation
A production rule $R_i$ is defined as a Horn clause:
$$\bigwedge_{j=1}^{m} P_{i, j} \implies Q_i$$
Where $P_{i, j}$ are antecedent facts, and $Q_i$ is the consequent fact.

### Forward Chaining Algorithm
```text
Algorithm: ForwardChaining(KB, Rules)
Input: Knowledge Base KB with initial facts F, Rule set R
Output: Fixed-point set of derived facts F_derived, Proof trace T

1. F_derived <- empty_set
2. T <- empty_list
3. repeat:
4.    rule_fired <- False
5.    for each Rule r in R:
6.       if r.antecedents subset_of (F union F_derived) and r.consequent not in (F union F_derived):
7.          F_derived.add(r.consequent)
8.          T.append(InferenceStep(r, r.antecedents, r.consequent))
9.          rule_fired <- True
10.         break  // Priority-based re-evaluation
11. until rule_fired is False
12. return F_derived, T
```

---

## 2. Intelligent Heuristic Search ($A^*$)

### Evaluation Function
$$f(n) = g(n) + h(n)$$
- $g(n)$: Exact path cost (number of actions taken from start state $s_0$ to current state $n$).
- $h(n)$: Admissible and consistent heuristic estimating remaining cost to goal state.

### Heuristic Formulation & Admissibility Proof
$$h(s) = d_{\text{Manhattan}}(s.\text{room}, \text{'Escape\_Portal'}) + \sum_{m \in \text{Milestones}} \mathbb{I}(m \notin s.\text{facts})$$

Where $\text{Milestones} = \{\text{portal\_activated}, \text{safe\_opened}, \text{vault\_unlocked}, \text{acid\_synthesized}\}$.

**Theorem**: $h(s)$ is admissible ($\forall s, h(s) \le h^*(s)$).
- **Proof**: 
  1. The minimum number of spatial transitions to reach the Escape Portal from any room is at least $d_{\text{Manhattan}}$.
  2. Each uncompleted milestone strictly requires at least 1 distinct atomic action ($\text{TAKE}, \text{SYNTHESIZE}, \text{UNLOCK}$) that cannot be executed in 0 steps.
  3. Since actions have uniform step cost $c(s, a, s') = 1$, the sum of Manhattan distance and remaining unachieved milestones is a true relaxed lower bound on $h^*(s)$. Hence, $h(s) \le h^*(s)$. $\blacksquare$

---

## 3. Constraint Satisfaction Problem (CSP)

A CSP is formalized as $\langle X, D, C \rangle$:
- **Variables**: $X = \{D_1, D_2, D_3\}$
- **Domains**: $D(D_i) = \{1, 2, \dots, 9\}$
- **Constraints**:
  1. $\text{AllDifferent}(D_1, D_2, D_3)$
  2. $D_1 + D_2 + D_3 = 15$
  3. $D_1 < D_2 < D_3$
  4. $D_2 \in \{2, 3, 5, 7\}$
  5. $D_3 = 2 \cdot D_1 + 1$

### Backtracking Search with MRV Heuristic
At each decision step, the unassigned variable with the **Minimum Remaining Values (MRV)** is selected to minimize branching factor:
$$X^* = \arg\min_{X_i \in X_{\text{unassigned}}} |D(X_i)|$$

---

## 4. Machine Learning Algorithms

### A. K-Means Clustering ($K=3$)
Objective: Minimize total intra-cluster variance (Inertia):
$$J = \sum_{k=1}^{K} \sum_{x \in C_k} \| x - \mu_k \|_2^2$$
Where $\mu_k = \frac{1}{|C_k|} \sum_{x \in C_k} x$.

### B. Silhouette Coefficient (Clustering Quality)
For each sample point $i$:
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}, \quad s(i) \in [-1, 1]$$
- $a(i)$: Mean intra-cluster distance between sample $i$ and all other points in the same cluster.
- $b(i)$: Mean nearest-cluster distance between sample $i$ and points in the closest neighboring cluster.

### C. Decision Tree Classifier (Gini Impurity)
Gini Impurity for a dataset node $D$ with class probabilities $p_i$:
$$I_G(D) = 1 - \sum_{i=1}^{C} p_i^2$$
Information Gain for split on feature $f$ with threshold $\theta$:
$$\Delta I_G(D, f, \theta) = I_G(D) - \left( \frac{|D_L|}{|D|} I_G(D_L) + \frac{|D_R|}{|D|} I_G(D_R) \right)$$
The optimal split maximizes $\Delta I_G$.
