# Heat extraction surrogate for hydraulic fracture spacing optimization: v0 implementation notes

*pydfnworks.thermal, branch `feature/thermal-mpf-surrogate`, 8 September 2026*

## 1. Purpose and scope

The `pydfnworks.thermal` subpackage adds a heat-extraction capability to dfnWorks that supports optimizing the spacing of hydraulic fractures, following the two-phase plan agreed for this effort: a fast analytic surrogate based on the Gringarten, Witherspoon and Ohnishi (1975) multiple parallel fractures (MPF) model that is usable immediately, and a DFN-based, particle-consistent heat transport model built on the existing graph transport infrastructure, both placed behind one stable interface so that an optimizer can call either backend interchangeably. The v0 delivery implements the surrogate in full, implements the interface of the DFN backend together with the parameter mapping it will need, provides a minimal spacing optimizer, two example drivers, verification scripts, and a Sphinx page, and records where the delivered work departs from the feature specification.

The remainder of these notes gives the package layout and interface (Section 2), the governing equations and dimensionless groups of the surrogate with the two limits used for verification (Section 3), the numerical Laplace inversion and its measured accuracy (Section 4), the verification results (Section 5), the optimizer and the monotonicity result that governs what a spacing optimization can and cannot return with the surrogate alone (Section 6), the Phase 2 interface and the thermal-to-TDRW parameter mapping (Section 7), the example drivers (Section 8), and the deviations from the specification and open items (Section 9).

## 2. Package layout and interface

The subpackage lives at `pydfnworks/pydfnworks/thermal/` and is discovered by `find_packages()` in `setup.py`, which is how every pydfnworks subpackage is registered (the specification refers to a `packages` list in `release.py`; that file builds and uploads the distribution and carries no package list, so no change to it was needed). The modules are

| Module | Role |
|---|---|
| `common.py` | argument validation shared by both backends (raises `ValueError`), representative granite and water property sets, `SECONDS_PER_YEAR` |
| `mpf_gringarten.py` | Phase 1 surrogate: Laplace-domain solution, numerical inversion, `heat_extraction()`, `production_temperature()`, dimensionless groups |
| `dfn_heat.py` | Phase 2 backend: same positional signature, validation, `thermal_to_tdrw_parameters()`, `NotImplementedError` for the kernel |
| `optimize_spacing.py` | `optimize_spacing()` over any backend, objectives `cumulative_heat()` and `time_to_drawdown()` |
| `__init__.py` | `BACKENDS` registry, `get_backend()`, re-exports |

Both backends implement

```python
heat_extraction(spacing, m_dot, T_res, T_inj, rock_props, fluid_props,
                n_fractures, fracture_height, t_eval) -> Q(t)  [W]
```

with `rock_props = {"rho", "c", "k"}` and `fluid_props = {"rho", "c"}` in SI units, temperatures in degrees Celsius, and `t_eval` in seconds. Backend-specific arguments are keyword-only, so the nine positional arguments are the stable contract: the surrogate adds `fracture_width` (default equal to `fracture_height`, a square fracture), `method`, and `stehfest_n`; the DFN backend adds `dfn`, `G`, `nparticles`, `tdrw_model`, `initial_positions`, and pass-through keywords for `run_graph_transport()`. The optimizer receives the backend as a callable argument, and its only backend-specific line is that argument, which was confirmed by pointing it at the Phase 2 stub in the verification script and in both examples.

## 3. The Gringarten multiple parallel fractures model

### 3.1 Geometry and assumptions

The reservoir consists of $n$ identical planar vertical fractures of height $H$ in the flow direction $z$ and width $w$ normal to it, spaced a uniform distance $D$ apart in an infinite rock mass. The total mass flow rate $\dot m$ is shared equally, so each fracture carries a volumetric rate $Q_f = \dot m/(\rho_f n)$ and a rate per unit width $q_w = Q_f/w$. Water enters every fracture at $T_\mathrm{inj}$, the rock is initially at $T_\mathrm{res}$, and heat reaches the fracture only by conduction normal to the fracture plane, so by symmetry each fracture draws on a slab of half-thickness $D/2$ with an insulated mid-plane. Heat storage in the fracture fluid and conduction along $z$ in the rock are neglected, which are the assumptions of Gringarten et al. (1975) and of the GEOPHIRES-X implementation (Beckers and McCabe 2019).

### 3.2 Governing equations

With $x$ the coordinate normal to the fracture (the fracture at $x=0$) and the dimensionless drawdown $\theta = (T_\mathrm{res} - T)/(T_\mathrm{res} - T_\mathrm{inj})$, the rock slab obeys

$$
(\rho c)_r \frac{\partial \theta_r}{\partial t} = k \frac{\partial^2 \theta_r}{\partial x^2}, \qquad 0 < x < D/2, \qquad
\theta_r(x, z, 0) = 0, \qquad \left.\frac{\partial \theta_r}{\partial x}\right|_{x = D/2} = 0, \qquad \theta_r(0, z, t) = \theta_w(z, t),
$$

and the fluid energy balance along the fracture, heated through both faces, is

$$
(\rho c)_f\, q_w \frac{\partial \theta_w}{\partial z} = 2k \left.\frac{\partial \theta_r}{\partial x}\right|_{x=0^+}, \qquad \theta_w(0, t) = 1 .
$$

Taking the Laplace transform in a dimensionless time $t_D = t/t_s$ and scaling $x$ by $\ell = \sqrt{\alpha\, t_s}$, where $\alpha = k/(\rho c)_r$ is the rock thermal diffusivity, the slab solution with the insulated mid-plane is $\bar\theta_r = \bar\theta_w \cosh\!\big(\sqrt{s}\,(\beta - x/\ell)\big)/\cosh(\beta\sqrt{s})$ with $\beta = (D/2)/\ell$, and the wall flux is $-\partial_x \bar\theta_r|_0 = (\bar\theta_w/\ell)\sqrt{s}\tanh(\beta\sqrt s)$. Substituting into the fluid balance gives an exponential decay along the fracture, and choosing $\ell = 2kH/((\rho c)_f q_w)$ so that the exponent at the outlet $z = H$ is unity yields the Gringarten et al. (1975) Equation A17 for the outlet drawdown,

$$
\bar T_{wD}(s) = \frac{1}{s}\exp\!\Big[-\sqrt{s}\,\tanh\!\big(\beta\sqrt{s}\big)\Big],
$$

with

$$
t_s = \frac{\ell^2}{\alpha} = \frac{4k(\rho c)_r H^2}{\big((\rho c)_f q_w\big)^2} = \frac{4k(\rho c)_r (wH)^2}{\big((\rho c)_f Q_f\big)^2}, \qquad
\beta = \frac{D/2}{\ell} = \frac{(\rho c)_f\, q_w\, D}{4kH}.
$$

These are exactly the groupings used in GEOPHIRES-X `MPFReservoir.py`, which was the reference implementation reused for this work. The produced water temperature and heat extraction rate follow as

$$
T_\mathrm{out}(t) = T_\mathrm{res} - T_{wD}(t/t_s;\beta)\,(T_\mathrm{res} - T_\mathrm{inj}), \qquad
\dot Q(t) = \dot m\, c_f\,(T_\mathrm{res} - T_\mathrm{inj})\,\big[1 - T_{wD}(t/t_s;\beta)\big].
$$

### 3.3 Limits used for verification

Two limits anchor the model and are the basis of the unit tests. For wide spacing, $\beta \to \infty$ and $\tanh \to 1$, so $\bar T_{wD} = e^{-\sqrt s}/s$, whose inverse is the semi-infinite single-fracture solution of Lauwerier (1955) and Bödvarsson and Tsang (1982) with negligible fracture storage,

$$
T_{wD}(t_D) = \operatorname{erfc}\!\left(\frac{1}{2\sqrt{t_D}}\right)
= \operatorname{erfc}\!\left(\frac{kH}{(\rho c)_f\, q_w \sqrt{\alpha t}}\right).
$$

For close spacing, $\beta \to 0$ and $\tanh(\beta\sqrt s) \to \beta\sqrt s$, so $\bar T_{wD} \to e^{-\beta s}/s$, a unit step at $t_D = \beta$. The corresponding dimensional time is the piston-displacement time of one slab,

$$
t_p = \beta\, t_s = \frac{(\rho c)_r\, D\, w\, H}{(\rho c)_f\, Q_f} = \frac{(\rho c)_r\, n\, D\, w\, H}{(\rho c)_f\, \dot m/\rho_f},
$$

the heat stored per unit temperature difference in the $n$ slabs divided by the heat-capacity flow rate of the injected water, which provides an energy-balance check independent of GEOPHIRES-X: the cumulative heat extracted must approach $(\rho c)_r\, n D w H\,(T_\mathrm{res} - T_\mathrm{inj})$.

## 4. Numerical Laplace inversion

GEOPHIRES-X inverts $\bar T_{wD}$ with `mpmath.invertlaplace(..., method='stehfest')` at 15 significant digits, which costs about 0.9 s for a 200-point curve on this machine and is too slow for an optimizer inner loop. The v0 implementation instead uses the double-precision Gaver-Stehfest algorithm already shared by the finite matrix-diffusion TDRW models in `pydfnworks.dfnGraph.transport.tdrw.stehfest`,

$$
T_{wD}(t_D) \approx \frac{\ln 2}{t_D}\sum_{i=1}^{N} V_i\, \bar T_{wD}\!\left(\frac{i \ln 2}{t_D}\right), \qquad
V_i = (-1)^{i + N/2} \sum_{k = \lfloor (i+1)/2 \rfloor}^{\min(i, N/2)} \frac{k^{N/2}\,(2k)!}{(N/2 - k)!\,k!\,(k-1)!\,(i-k)!\,(2k-i)!},
$$

vectorized over the evaluation times so that a 361-point curve costs about 100 microseconds. The mpmath route is retained as `method="mpmath"` for cross-checks and is the only vendored GEOPHIRES-X logic; it sits behind `heat_extraction()` and can be replaced without touching callers.

The number of terms was chosen against a 40-digit de Hoog reference (mpmath) over $t_D \in [0.1\beta, 100\beta] \cup [10^{-2}, 10^{2}]$:

| $\beta$ | $N=14$ | $N=16$ | $N=18$ | $N=20$ | $N=22$ |
|---|---|---|---|---|---|
| 0.1 | 1.9e-2 | 1.1e-2 | 6.2e-3 | 3.3e-3 | 2.1e-3 |
| 0.3 | 2.0e-3 | 1.0e-3 | 4.7e-4 | 2.0e-4 | 7.8e-4 |
| 1 | 2.1e-4 | 7.2e-5 | 3.1e-5 | 7.1e-5 | 1.1e-3 |
| 3 | 3.8e-5 | 1.4e-5 | 6.3e-6 | 5.6e-5 | 7.7e-4 |
| 10 | 1.2e-5 | 4.0e-6 | 3.8e-6 | 5.3e-5 | 1.3e-3 |
| 100 | 1.2e-5 | 4.0e-6 | 4.3e-6 | 7.7e-5 | 1.4e-3 |

$N = 18$ is uniformly at least as accurate as 16 and is the default; 20 or more terms lose accuracy at large $\beta$ through double-precision cancellation. Below $\beta \approx 0.05$ the response is close to a step at $t_D = \beta$ and Stehfest ringing of a few percent is visible around it, which is the known behaviour of the algorithm at discontinuities; the integrated heat remains correct to better than $10^{-3}$, and this is the regime in which the fixed-lateral example produces the visible dip near the piston front. The output is clipped to $[0, 1]$ and $t = 0$ is handled analytically ($T_{wD} = 0$).

## 5. Verification

The tests live in `pydfnworks/tests/thermal/`, following the existing pattern of standalone verify scripts with a `run_thermal_verification.py` runner (there is no pytest in the pydfnworks environment; the `test_*` functions also run under pytest if it is present). All 14 tests pass. The FORGE-representative parameters are granite ($\rho = 2750$ kg/m³, $c = 790$ J/kg/K, $k = 3.05$ W/m/K), water ($\rho = 1000$ kg/m³, $c = 4200$ J/kg/K), $\dot m = 60$ kg/s, $T_\mathrm{res} = 226$ °C, $T_\mathrm{inj} = 40$ °C, $n = 20$, $H = w = 60$ m.

| Test | Result |
|---|---|
| Laplace limits $s\bar T_{wD} \to 1$ ($s \to 0$), $\bar T_{wD} \to 0$ ($s \to \infty$) | pass |
| Wide-spacing asymptote ($D = 10^6$ m) vs Bödvarsson-Tsang erfc form, dimensional and dimensionless | max relative error 6e-6 and 2e-6 |
| Close spacing (5 m) vs wide (100 m) at the same flow | never higher; 30-year cumulative heat ratio 0.069; time to 75 % decline 51 d vs 123 d; time to 10 % decline equal (4.6 d, single-fracture regime) |
| Energy balance at $D = 2$ and 5 m over $6 t_p$ | cumulative heat / heat in place = 1.0001 and 0.9988 |
| numpy Stehfest vs GEOPHIRES-X mpmath at $\beta = 0.5, 1.5, 6$ | max difference 1.2e-4, 1.3e-5, 4.5e-6 |
| Physical bounds, $\dot Q(0) = \dot m c_f \Delta T$ | pass |
| Runtime, 361 times | 101 microseconds per call |
| Shared validation, Phase 2 stub, TDRW mapping | 6 bad inputs rejected identically by both backends; stub raises `NotImplementedError` |
| Finite spacing ($\beta = 1$): independent finite-difference solution of the coupled slab-conduction and fracture-advection equations (Crank-Nicolson in $x$, implicit wall coupling along $z$) vs Stehfest | max difference 9.1e-3 on a 50 x 100 grid, 4.6e-3 on 100 x 200, converging toward the inversion |
| Optimizer objectives, grid, `bounded`, `differential_evolution`, candidate spacings, backend swap, argument errors | pass |

No elementary closed form exists at finite $\beta$ (Gringarten et al. inverted Equation A17 numerically as well), so the finite-spacing check is the finite-difference solution of the governing equations of Section 3.2, which is independent of the Laplace transform, its inversion, and GEOPHIRES-X; together with the two closed-form limits and the energy balance this covers the whole $\beta$ range. The 10 % decline check is informative: the first 10 % of drawdown occurs in the single-fracture (erfc) regime before the slab depletion front is felt, so close and wide spacing coincide there, and the separation appears only at deep drawdown. The test asserts the 75 % point.

## 6. Spacing optimizer

`optimize_spacing(bounds, m_dot, ..., t_eval, heat_extraction=..., objective=..., n_fractures=..., method=...)` evaluates the objective on a log-spaced grid (or on explicit candidate spacings) and, for `method="bounded"` or `"differential_evolution"`, refines from there with SciPy. Objectives are callables $f(t, \dot Q) \to$ scalar that are maximized; the two provided are the cumulative heat over the evaluation window and the time to a specified thermal drawdown,

$$
E(T) = \int_0^{T} \dot Q(t)\,dt, \qquad
t_\mathrm{dd}(\phi) = \min\{t : \dot Q(t) \le \phi\, \dot Q(0)\},
$$

with $t_\mathrm{dd}$ interpolated linearly between samples and censored at $t_\mathrm{eval}[-1]$ when the threshold is not reached. The fracture count is either fixed or a function of spacing, which is how a stage-count coupling such as $n = L/D$ for stages filling a lateral of length $L$ is expressed. The result carries the best spacing, $\dot Q(t)$ at that spacing, and the objective at every evaluated spacing.

With the surrogate alone the objectives are monotone in spacing, and this is a property of the physics rather than of the optimizer. For stages filling a fixed lateral at fixed total flow, $nD = L$ makes the piston time independent of spacing,

$$
t_p = \frac{(\rho c)_r\, L\, w\, H}{(\rho c)_f\, \dot m/\rho_f},
$$

so every spacing extracts the same heat in place and differs only in the shape of the decline: many closely spaced fractures approach the ideal piston displacement (constant $\dot Q$ until $t_p$, then collapse), and few widely spaced fractures follow the early erfc decline. Cumulative heat over any window and time to any drawdown are therefore maximized by the closest allowed spacing. At fixed fracture count, wider spacing adds rock volume and both objectives increase monotonically to the semi-infinite limit. An interior optimum requires a term the surrogate does not contain, either a cost per stage (techno-economic modeling, explicitly deferred) or the Phase 2 DFN backend, where the flow partition among fractures and network connectivity enter. The optimizer accepts either through the `objective` and `heat_extraction` arguments without change.

## 7. Phase 2 interface and the thermal-to-TDRW mapping

The finite-slab matrix-diffusion return-time work referred to in the specification is already on master (dfnWorks v2.12, PR #156) under `pydfnworks/dfnGraph/transport/tdrw/`, with the Dentz slab, annulus, Roubinet and from-file models and the shared Stehfest module, and `run_graph_transport()` already accepts `tdrw_model`, `matrix_porosity`, `matrix_diffusivity` and `fracture_spacing`. Phase 2 therefore does not need a second Laplace-inversion implementation. Heat obeys the same fracture and matrix equations as a solute with a change of coefficients. For a solute in a fracture of half-aperture $b$ with matrix porosity $\phi_m$ and diffusivity $D_m$,

$$
\frac{\partial c}{\partial t} + v\frac{\partial c}{\partial z} = \frac{\phi_m D_m}{b}\left.\frac{\partial c_m}{\partial x}\right|_{x=b}, \qquad
\frac{\partial c_m}{\partial t} = D_m \frac{\partial^2 c_m}{\partial x^2},
$$

while for heat

$$
(\rho c)_f\left(\frac{\partial T}{\partial t} + v\frac{\partial T}{\partial z}\right) = \frac{k}{b}\left.\frac{\partial T_r}{\partial x}\right|_{x=b}, \qquad
(\rho c)_r\frac{\partial T_r}{\partial t} = k \frac{\partial^2 T_r}{\partial x^2}.
$$

Dividing the fracture equation by $(\rho c)_f$ and writing $k = (\rho c)_r \alpha$ puts the thermal problem in solute form with

$$
\phi_m \;\to\; \frac{(\rho c)_r}{(\rho c)_f}, \qquad D_m \;\to\; \alpha = \frac{k}{(\rho c)_r},
$$

so that the TDRW exchange parameter $\phi_m\sqrt{D_m}/b$ becomes $\sqrt{k(\rho c)_r}/((\rho c)_f\, b)$, the Lauwerier group. For granite and water the porosity-like ratio is 0.517 and the diffusivity is $1.40\times10^{-6}$ m²/s, inside the ranges enforced by `check_tdrw_params()`. `dfn_heat.thermal_to_tdrw_parameters()` implements this mapping and `dfn_heat.heat_extraction()` validates its arguments, builds the planned `run_graph_transport()` call, and raises `NotImplementedError` whose message states that call. One finding from the `thermal_graph_transport` example bears directly on Phase 2. The finite-slab models sample matrix excursions as Poisson trapping events at a rate (`tdrw/trapping.py`)

$$
\gamma = \frac{2\,\phi_m D_m}{b\,\varepsilon\,B}
$$

per unit advective time, with $b$ the edge aperture, $B = D/2$ the slab half-width and $\varepsilon = 10^{-4}$ the release position. Under the thermal mapping $\phi_m D_m \approx 7\times10^{-7}$ m²/s, some $10^{7}$ times the solute value, so a particle with an advective time of $10^{3}$ s undergoes of order $10^{6}$ to $10^{7}$ excursions and a single particle took minutes on the example DFN (a run with $10^{3}$ particles never reached its first progress mark). The infinite-matrix model, which draws one closed-form retention time per edge, ran $10^{4}$ particles in under two seconds. The Phase 2 backend must therefore sample the total slab retention time per edge from the finite-slab kernel directly rather than event by event, and the finite `tdrw` models should not be run with thermal parameters at production particle counts. This is recorded in the `dfn_heat` module notes.

What remains for Phase 2 is the thermal post-processing: converting the particle arrival-time distribution at the production well into $T_\mathrm{out}(t)$ and $\dot Q(t)$, the tracer-to-thermal mapping of Shook (2001), with the per-fracture flow partition taken from the graph flow solution rather than the equal split assumed by the surrogate.

## 8. Example drivers

Two examples were added under `examples/`, each with a `driver.py` and a README and each registered in `examples/README.md`.

`thermal_spacing_optimization` follows the specification: a FORGE-representative DFN (600 m block of Utah FORGE granitoid at about 2.3 km, one set parallel to the hydraulic fractures with its normal along the lateral and one natural set of strike about 300 and dip about 70) with an injection lateral and a production lateral 100 m above it placed through the well package on a reduced mesh. The fracture count and mean diameter seen by the injection lateral and the lateral length inside the domain set the surrogate geometry, and the driver runs the surrogate at the DFN-derived spacing, three optimization cases, the backend swap, and writes $\dot Q(t)$ and the objective curves as CSV and a figure. No FORGE DFN existed locally, so the setup was written for this feature with representative parameters.

`thermal_graph_transport` follows `examples/graph_transport` at the user's request: the same DFN and graph flow, the fractures on the inflow face and `compute_dQ` supplying the surrogate geometry and the characteristic spacing $1/dQ$, graph particle transport with the Dentz slab TDRW model driven by the thermal parameter mapping of Section 7, the surrogate and optimizer, and the Phase 2 backend called with the DFN and flow graph.

Results of the runs on this machine (8 September 2026) are summarized below; both drivers exit cleanly and write their CSV files and figure.

| Quantity | `thermal_spacing_optimization` | `thermal_graph_transport` |
|---|---|---|
| Fractures in the DFN | 167 | 935 |
| Fractures seen by the injection well or inflow face | 5 (7 on the production lateral) | 22 |
| Surrogate fracture height (mean diameter) | 218.8 m | 25.9 m |
| DFN-derived spacing | 150 m (600 m lateral) | 2.23 m ($1/dQ$; $1/p_{32}$ = 1.33 m) |
| Mass flow rate | 20 kg/s (scaled design rate) | 1.79 kg/s (graph flow, 1 MPa drop) |
| $\beta$, piston time at that spacing | 4.3, 29 yr | 0.093, 0.30 yr |
| $\dot Q(0)$, $\dot Q(30\ \mathrm{yr})$ | 15.6 MW, 4.1 MW | 1.40 MW, 0 |
| Time to 10 % drawdown, stages filling the lateral or domain | best at the smallest spacing, 5 m (120 stages) | best at the smallest spacing, 2 m (200 stages) |
| Cumulative 30-year heat, stages filling the lateral | 7.7 m (78 stages), 11.6 PJ, flat within ringing below 10 m | not run |
| Cumulative 30-year heat, fixed count | best at the upper bound (200 m), 6.43 PJ | best at the upper bound (100 m), 0.41 PJ |
| Thermal TDRW ($10^{4}$ particles, infinite matrix) | not run | 1.7 s; advective time 1, 10, 50 % quantiles 1.7e5, 2.1e5, 2.7e5 s; retarded 2.4e11, 6.8e11, 4.7e12 s |

The monotone behaviour of Section 6 is visible in both: at fixed total flow and rock volume the closest spacing wins, and at fixed count the widest does. In the graph example the block is small (400 x 50 x 50 m with 26 m fractures) relative to the flow the stimulated network carries, so the surrogate depletes it within a year at the DFN spacing; the retarded arrival times from the infinite-matrix TDRW are $10^{6}$ to $10^{7}$ times the advective times and heavy-tailed, which is the expected behaviour of an unbounded rock mass and the reason the early quantiles rather than the median are reported.

## 9. Deviations from the specification and open items

- `release.py` carries no `packages` list; registration is by `find_packages()` and an `__init__.py`. Nothing else was needed for `pip install` to pick the subpackage up.
- Tests follow the repository's verify-script pattern rather than pytest, which is not installed in the pydfnworks environment; the functions are pytest-compatible.
- The surrogate needs a fracture width as well as a height; `fracture_width` was added as a keyword-only argument defaulting to the height, keeping the nine positional arguments of the interface unchanged.
- Validation raises `ValueError` rather than calling `print_log(..., 'error')`, which exits the interpreter and would be inappropriate inside an optimizer loop.
- The reference PDFs were not available at the time of writing; the Laplace solution was validated against the erfc limit and the energy balance, and its parameter grouping against GEOPHIRES-X, which reproduces Gringarten et al. (1975) Equation A17.
- Stehfest ringing below $\beta \approx 0.05$ is documented rather than removed; a de Hoog inversion would remove it at some cost in speed if the near-piston regime becomes important.
- Objectives are monotone with the surrogate alone (Section 6); an interior spacing optimum needs a stage cost or the Phase 2 backend.
- The finite-slab TDRW sampler is impractical at thermal diffusivity (Section 7); Phase 2 needs a per-edge kernel sample instead of event-by-event trapping.
- The Phase 2 kernel, any DFN generation or meshing change, and techno-economic modeling remain deferred as specified.

## References

Beckers, K. F., and McCabe, K. (2019). GEOPHIRES v2.0: updated geothermal techno-economic simulation tool. Geothermal Energy, 7, 5. Source reused: NREL/GEOPHIRES-X, `src/geophires_x/MPFReservoir.py` (MIT licence).

Bödvarsson, G. S., and Tsang, C. F. (1982). Injection and thermal breakthrough in fractured geothermal reservoirs. Journal of Geophysical Research: Solid Earth, 87(B2), 1031-1048.

Gringarten, A. C., Witherspoon, P. A., and Ohnishi, Y. (1975). Theory of heat extraction from fractured hot dry rock. Journal of Geophysical Research, 80(8), 1120-1124.

Lauwerier, H. A. (1955). The transport of heat in an oil layer caused by the injection of hot fluid. Applied Scientific Research, A5, 145-150.

Shook, G. M. (2001). Predicting thermal breakthrough in heterogeneous media from tracer tests. Geothermics, 30(6), 573-589.
