# Solving UE model of traffic allocation based on Frank Wolfe algorithm (Python & NetWorkX)
This project takes SiouxFalls traffic network as an example and solves the user equilibrium model of traffic allocation based on Frank Wolfe algorithm.
## A brief introduction to user equilibrium model
### First Principle of Wardrop
The users of the road know exactly the traffic state of the network and try to choose the shortest path. When the network reaches a balanced state, the routes used by each OD pair have the same travel time and the shortest travel time. The travel time of an unused path is greater than or equal to the minimum travel time.
### User equilibrium model
The traffic allocation model that satisfies the first principle of Wardrop is called the user equilibrium model.

In 1956, Beckmann proposed a mathematical programming model that satisfies Wardrop's first principle. The core of the model is that all users in the traffic network try to choose the shortest path, and eventually make the impedance of the chosen path minimum and equal. The mathematical programming model is as follows:

$$
\min Z\left( X \right) =\sum_a{\int_0^{x_a}{t_a\left( w \right) dw}}
\\
\quad s.t. \begin{cases}
	\sum_k{f_{k}^{rs}=q_{k}^{rs},\forall r,s}\\
	f_{k}^{rs}\geqslant 0,\forall r,s\\
\end{cases}
$$
### BPR function
In the user equilibrium model, $t_a$ is the path resistance function, and we generally use the BPR function, that is:

$$
t_a\left( x_a \right) =FFT_a*\left[ 1+\alpha *\left( \frac{x_a}{C_a} \right) ^{\beta} \right] \\
$$

+ $FFT_𝑎$ indicates the fastest time to cross section a
+ 𝛼 is usually 0.15,
+ 𝛽 is usually 4.0
+ $𝐶_𝑎$ indicates the capacity of section a
+ $x_𝑎$ indicates the traffic flow on section a

### Integration term of user equilibrium model
In order to facilitate subsequent solution, we substitute the BPR function into $\int_0^{x_a}{t_a\left( w \right) dw}$ for integral calculation, the process is as follows:


$$
\begin{aligned} \int_0^{x_a}{t_a(w) dw} &= \int_0^{x_a}{FFT_a \cdot \left[ 1 + \alpha \left( \frac{w}{C_a} \right) ^{\beta} \right] dw} \ =\ C_a \cdot FFT_a \int_0^{x_a}{\left[ 1 + \alpha \left( \frac{w}{C_a} \right) ^{\beta} \right] d\left( \frac{w}{C_a} \right)} \ =\ C_a \cdot FFT_a \int_0^{\frac{x_a}{C_a}}{\left( 1 + \alpha x^{\beta} \right) \ dx} \ =\ FFT_a \left[ x_a + \frac{\alpha C_a}{\beta + 1} \left( \frac{x_a}{C_a} \right) ^{\beta + 1} \right] \\  \end{aligned}   \\
$$

Therefore, our objective function is

$$
\min Z\left( X \right) =\sum_a{FFT_a\left[ x_a+\frac{\alpha C_a}{\beta +1}\left( \frac{x_a}{C_a} \right) ^{\beta +1} \right]}
$$

## Frank Wolfe algorithm solution steps
**Step 1: Initialize.** Based on the road resistance of the zero flow diagram, the shortest path corresponding to each OD to r,s is searched successively, and all OD traffic between r,s is allocated to the corresponding shortest path to obtain the initial section flow $X_1$.

**Step 2: Update the block.** According to the BPR function, the initial flow of each section is substituted to obtain the impedance $W_1$.

**Step 3: Descending direction.** Based on the impedance $W_1$, the traffic is redistributed to the corresponding path according to the method described in Step 1 (the shortest all and none distribution), and the temporary section flow ${X_1}^*$ is obtained.

**Step 4: Search for the best Uber size and update the traffic.** Using dichotomy, search for the optimal step size $step^{*}$, and make 

$$
X_1+step^**({X_1}^*-X_1)
$$

Where the optimal step size satisfies $\min Z\left[ X_1+step^**({X_1}^*-X_1) \right] , step \in \left( 0,1 \right]$

**Step 5: End condition.** If 

$$
\sqrt{\sum_a{\left( x_{a}^{n+1}-x_{a}^{n} \right) ^2}}/\sum_a{x_{a}^{n}}\leqslant \varepsilon 
$$

the algorithm ends. Otherwise n=n+1, go to Step 2. This 𝜀 represents the error threshold, which is represented in the code section by max_err.




