# Evaluation Metrics & Theoretical Formulations

## 1. Search Algorithm Metrics

### A. Solution Path Optimality
The path cost $C^*$ is defined as the sum of step costs along the optimal path:
$$C^* = \min_{\pi \in \Pi} \sum_{e \in \pi} c(e)$$
In this system, both BFS and $A^*$ find $C^* = 11$ steps.

### B. Search Node Expansion Ratio
The search efficiency gain $\eta_{\text{search}}$ of informed $A^*$ search over uninformed BFS:
$$\eta_{\text{search}} = \frac{N_{\text{BFS}} - N_{A^*}}{N_{\text{BFS}}} \times 100\% = \frac{34 - 20}{34} \times 100\% = 41.18\%$$

### C. Peak Frontier Memory Footprint
Measures the maximum memory consumption of the open list during search exploration.

---

## 2. Machine Learning Evaluation Metrics

### A. Confusion Matrix Terms
- **True Positives ($TP_c$)**: Predicted class $c$, Actual class $c$.
- **False Positives ($FP_c$)**: Predicted class $c$, Actual class $\neq c$.
- **False Negatives ($FN_c$)**: Predicted class $\neq c$, Actual class $c$.
- **True Negatives ($TN_c$)**: Predicted class $\neq c$, Actual class $\neq c$.

### B. Multi-Class Precision, Recall, and F1
For class $c \in \{\text{Assist}, \text{Standard}, \text{Challenge}\}$:
$$\text{Precision}_c = \frac{TP_c}{TP_c + FP_c}, \quad \text{Recall}_c = \frac{TP_c}{TP_c + FN_c}$$
$$F1_c = 2 \cdot \frac{\text{Precision}_c \cdot \text{Recall}_c}{\text{Precision}_c + \text{Recall}_c}$$

**Macro-Averaged F1**:
$$\text{Macro } F1 = \frac{1}{|C|} \sum_{c \in C} F1_c = 0.9688$$

**Weighted F1**:
$$\text{Weighted } F1 = \sum_{c \in C} \left( \frac{N_c}{N_{\text{total}}} \right) F1_c = 0.9667$$

### C. Silhouette Coefficient Formula
For sample vector $\mathbf{x}_i \in C_I$:
$$a(i) = \frac{1}{|C_I| - 1} \sum_{j \in C_I, j \neq i} \|\mathbf{x}_i - \mathbf{x}_j\|_2$$
$$b(i) = \min_{J \neq I} \frac{1}{|C_J|} \sum_{j \in C_J} \|\mathbf{x}_i - \mathbf{x}_j\|_2$$
$$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$
**Global Silhouette Score**:
$$S = \frac{1}{N} \sum_{i=1}^{N} s(i) = 0.5842$$
