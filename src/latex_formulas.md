Fitness:
\begin{equation}
    \Phi = \begin{cases}
        0 & w \leq 0 \\
        q^+ (a, a_{\frac{1}{2}}) \times q^-(w, w_{\frac{1}{2}}) & \text{elsewhere}
    \end{cases}
\end{equation}

\begin{equation}
    q^\pm (x, x_{\frac{1}{2}}, \phi) = \frac{1}{1 + e^{\pm \phi(x-x_{\frac{1}{2}})}}
\end{equation}

where $\phi$ is a species-dependent constant and $0 \leq \Phi \leq 1$.

Carnivores kill a herbivore with a probability:

\begin{equation}
    p = \begin{cases}
        0 & \text{if } \Phi_{\text{carn}} \leq \Phi_{\text{herb}} \\
        \frac{\Phi_{\text{carn}} - \Phi_{\text{herb}}}{\Delta \Phi_{\text{max}}} & \text{if } 0 < \Phi_{\text{carn}} - \Phi_{\text{herb}} < \Delta \Phi_{\text{max}} \\
        1 & \text{otherwise}
    \end{cases}
\end{equation}

For "lognorm"-function:

\begin{equation}
    \mu = \log \left( \frac{{w_{\text{birth}}^2}}{{\sqrt{{\sigma_{\text{birth}}^2 + w_{\text{birth}}^2}}}} \right)
\end{equation}

\begin{equation}
    \sigma = \sqrt{\log \left( 1 + \frac{{\sigma_{\text{birth}}^2}}{{w_{\text{birth}}^2}} \right)}
\end{equation}

Where $w_{\text{birth}}$ and $\sigma_{\text{birth}}$ are species-dependent constants.