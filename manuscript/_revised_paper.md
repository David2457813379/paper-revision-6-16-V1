# EUI Prediction and Energy–Carbon Coupling Analysis for Beijing Hotel Buildings Using Parametric Simulation and Machine Learning

**Xiangyu Xiao<sup>1</sup>, Xiong Zheng<sup>2</sup>**

<sup>1</sup> [Author affiliation]; <sup>2</sup> [Author affiliation]

---

## Abstract

To improve the efficiency of energy consumption and carbon emission assessment in the design and operation phases of hotel buildings, this study develops an integrated research framework combining parametric simulation, interpretable sensitivity analysis, machine-learning-based surrogate modeling, and operational carbon analysis, focusing on hotel buildings in Beijing. First, 38 key parameters affecting hotel building energy consumption were selected based on regulatory requirements, literature review, and operational characteristics of hotels. The Latin Hypercube Sampling (LHS) method was used to generate 20,000 parameter combinations, which were screened to 4,640 feasible samples and simulated using EnergyPlus to construct a parametric simulation database. Second, Standardized Regression Coefficients (SRC) combined with bootstrap resampling were used to evaluate the magnitude, direction, and sign stability of each parameter's effect on Energy Use Intensity (EUI), and the results were cross-validated using SHAP (SHapley Additive exPlanations) values from a nonlinear XGBoost model. Based on the combined evidence, 18 key variables were identified. Third, 17 machine learning surrogate models were trained and systematically compared using the coefficient of determination (R2), cross-validation variance, root mean square error (RMSE), and mean absolute percentage error (MAPE) as the primary evaluation metrics, with complete hyperparameter tuning reported. Finally, carrier-specific carbon emission factors with documented sources were introduced to construct an Operational Carbon Emission Intensity (OCEI) analysis module, and the robustness of the coupling relationship was tested under six alternative emission factor scenarios. The results show that domestic hot water demand, building form parameters, selected envelope thermal parameters, and HVAC operational control parameters are the main factors affecting EUI in Beijing hotel buildings. Within the current simulation sample space, Poly3-RidgeCV (test R2 = 0.9976) and MLP (test R2 = 0.9973) demonstrated the best overall performance in terms of surrogate fidelity and stability. SHAP analysis confirms the SRC-based variable ranking (Spearman rank correlation = 0.891). Although EUI and OCEI are significantly correlated (Pearson r = 0.954, p < 0.001), they are not entirely equivalent: the top-10% ranking overlap between the two metrics is 76.3%, and domestic-hot-water-related variables exhibit amplified importance in the OCEI dimension. Emission factor sensitivity analysis shows that while absolute OCEI values vary by +/-11% across scenarios, the EUI-OCEI coupling structure remains robust (r range: 0.938-0.958). Comparison with published Beijing hotel measured data (mean EUI = 123 kWh/(m2.a)) indicates that the simulated range (80-220 kWh/(m2.a)) captures realistic variability but overestimates the mean by approximately 14%, highlighting the sim-to-real transfer gap. The framework proposed in this study provides a reference for scheme comparison, energy-saving design, and low-carbon optimization of hotel buildings in Beijing and regions with similar climatic conditions.

**Keywords:** hotel buildings; Beijing; energy use intensity (EUI); operational carbon emission intensity (OCEI); sensitivity analysis; machine learning; energy-carbon coupling; surrogate modeling; SHAP.

---

## 1. Introduction

Since 2006, China has been the world's largest emitter of carbon dioxide [1]. Meanwhile, building construction and operation consume over 40% of global energy and emit approximately one-third of global carbon dioxide [2]. Among various building types, hotels are particularly energy-intensive; existing research indicates that hotels consume more energy per unit floor area than most other commercial building types [3]. China's large and growing population sustains the demand for hotel buildings, and the need for heating, cooling, ventilation, lighting, and domestic hot water services in hotels remains high and is expected to increase as indoor environmental quality requirements rise [4]. However, substantial inefficiencies exist in hotel energy consumption in China, indicating considerable room for improvement in energy efficiency and carbon reduction through better design and management [5].

Traditional building energy performance assessment primarily relies on physical simulation software such as EnergyPlus [6], DeST [7], and eQuest [8]. While these tools offer mechanistic fidelity, they require detailed input parameters and entail long computation times, making them unsuitable for rapid screening of large numbers of building design alternatives. In recent years, machine learning techniques have been increasingly introduced into building energy performance modeling, offering the ability to handle high-dimensional, nonlinear mappings [9]. However, existing research largely focuses on complex black-box models such as deep neural networks and random forests [10,11,12], which, while accurate in certain scenarios, typically require large amounts of training data and suffer from limited interpretability. Furthermore, most studies focus on black-box fitting of single energy performance indicators, lacking systematic identification of key influencing parameters and further analysis of the coupling between building energy intensity and carbon emission intensity under different energy supply structures.

To address these gaps, this study takes hotel buildings in Beijing as the research object and constructs a comprehensive framework integrating parametric simulation, interpretable sensitivity analysis, machine-learning-based surrogate modeling, and operational carbon analysis. The specific objectives are: (1) constructing a parametric simulation database for Beijing hotel buildings through LHS and EnergyPlus; (2) identifying key variables affecting EUI through both linear (SRC + bootstrap) and nonlinear (SHAP) sensitivity methods; (3) systematically comparing 17 machine learning surrogate models with fully reported hyperparameter tuning; and (4) introducing carrier-specific emission factors to analyze the coupling and deviation between EUI and OCEI, including sensitivity to alternative emission factor assumptions.

The principal contributions of this study are threefold. First, it provides a systematic variable screening framework for hotel buildings -- a building type whose energy performance is strongly shaped by domestic hot water demand and continuous operation -- by combining parametric simulation with both linear and nonlinear sensitivity analysis methods. Second, it offers a comprehensive comparison of 17 surrogate models with fully documented hyperparameter tuning, establishing a reproducible benchmark for hotel building EUI surrogate modeling. Third, it extends the analysis beyond single-indicator energy assessment to an uncertainty-aware energy-carbon coupling framework that examines the conditions under which EUI-based and OCEI-based rankings diverge.

## 2. Literature Review and Research Hypotheses

### 2.1. Hotel Building Energy Performance

Building Energy Use Intensity (EUI) is a widely used indicator for measuring a building's operational energy performance [13]. A building's EUI is determined by the combined effects of multiple factors, including the thermal performance of the building envelope, building geometry, internal loads, and HVAC system operation and control [14,15,16]. For hotel buildings -- characterized by continuous year-round operation, substantial domestic hot water demand, and a mix of guest rooms and service spaces -- the energy consumption formation mechanism is more complex than that of typical office or residential buildings [17,18]. In cold or mixed climates such as Beijing's, envelope heat transfer, building form and orientation, domestic hot water load, and HVAC system settings simultaneously affect multiple energy end-uses including heating, cooling, lighting, and hot water, with coupled effects reflected in the overall EUI level.

Although research has examined public building energy consumption from various perspectives, studies specifically addressing hotel buildings remain relatively fragmented [19,20,21,22]. Many existing studies focus on single-category parameters or employ local perturbation analyses, making it difficult to capture the overall energy response characteristics under simultaneous multi-parameter variation [23,24,25,26].

### 2.2. Surrogate Modeling for Building Energy Assessment

Physical simulation methods provide mechanistic fidelity in building energy assessment [27,28] but entail high computational costs that hinder large-sample scheme screening [29,30]. Surrogate models -- data-driven approximations trained on simulation outputs -- can significantly improve evaluation efficiency while maintaining a controlled level of accuracy, and are increasingly used for rapid assessment during early-stage building design [31]. However, two prominent problems remain: many studies employ complex black-box models without sufficient explanation of variable importance [32,33,34], and model conclusions from one building type cannot be directly transferred to another [35]. Therefore, a framework combining interpretable variable screening with systematic model comparison is a productive path that balances physical rationality, interpretability, and predictive efficiency.

### 2.3. Energy-Carbon Coupling

As research on low-carbon buildings deepens, the limitations of using EUI alone to evaluate design schemes are increasingly recognized. EUI reflects energy consumption per unit floor area but is not directly equivalent to carbon emission level: even two schemes with similar total energy consumption may exhibit substantially different carbon emission performance if the energy carrier structure or emission factors differ [36,37]. This issue is particularly important for hotel buildings, which involve multiple energy end-uses whose carbon implications are governed by different emission factors. Revealing the coupling and deviation between EUI and carbon emission intensity -- and testing the robustness of this relationship under alternative emission factor assumptions -- is essential for shifting building evaluation from single-indicator energy assessment to synergistic energy-carbon optimization.

### 2.4. Research Hypotheses

**H1:** Within the parameter space defined in this study, a subset of key variables from four categories -- envelope, building geometry, occupant and equipment loads, and HVAC operation -- significantly affects the EUI of Beijing hotel buildings.

**H2:** A machine learning surrogate model built on key variables can achieve high-fidelity approximation of EnergyPlus-simulated EUI, with models capable of capturing nonlinear relationships outperforming purely linear models.

**H3:** Under a unified carbon accounting boundary, EUI and OCEI of Beijing hotel buildings exhibit a significant positive correlation, but are not entirely equivalent -- the ranking of design schemes can differ between the two metrics.

**H4:** The EUI-OCEI relationship is sensitive to the choice of emission factors, and the coupled analysis should account for this uncertainty.

### 2.5. Overall Research Framework

Based on the above, this study establishes an integrated framework of "parametric simulation -> key variable identification -> machine learning surrogate modeling -> EUI/OCEI coupled analysis with uncertainty assessment." The framework retains the mechanistic basis of physical simulation while incorporating the efficiency of machine learning surrogates, and further extends building evaluation from single-indicator energy assessment to uncertainty-aware energy-carbon synergistic evaluation.

## 3. Materials and Methods

### 3.1. Research Context

This study focuses on hotel buildings in Beijing, a representative northern Chinese city (116.20 deg E, 39.56 deg N) with a warm-temperate, semi-humid monsoon climate characterized by hot, rainy summers and cold, dry winters. Given the large number of hotels in Beijing and the significant seasonal heating, cooling, and year-round domestic hot water demands, Beijing is a suitable representative region for studying the coupling of hotel energy consumption and carbon emissions [38].

The study was carried out in four sequential steps: (1) parametric sample generation and EnergyPlus simulation to construct a hotel EUI database; (2) sensitivity analysis combining SRC + bootstrap with SHAP cross-validation to identify key variables; (3) systematic training and comparison of 17 machine learning surrogate models with full hyperparameter reporting; and (4) EUI-OCEI coupling analysis with emission factor sensitivity testing.

### 3.2. Parametric Simulation Database Construction

#### 3.2.1. Parameter Selection

Thirty-eight input variables affecting hotel building energy consumption were selected based on the Chinese "Energy Conservation Design Standard for Public Buildings" (GB 50189-2015) [52], underlying energy-use formation mechanisms, and relevant previous studies [44,45,46]. These variables span four categories: (1) thermal performance of the building envelope (17 variables including insulation thicknesses, U-values, SHGCs, window construction type); (2) building geometry and form (8 variables including floor number, room count, room area, aspect ratio, orientation); (3) occupant and equipment loads (4 variables including DHW consumption, occupancy density, lighting and equipment power densities); and (4) HVAC operation and control (9 variables including setpoints, COPs, boiler efficiency, fan efficiency, fresh air rate, operating hours). The value ranges are presented in Table 1.

**Table 1.** Input variables and value ranges.

| Variable | Range | Unit |
|----------|-------|------|
| External wall insulation thickness | 0.05-0.12 | m |
| Window-to-wall ratio | 0.25-0.60 | -- |
| External wall structural thickness | 0.20-0.30 | m |
| U-value, north windows | 0.8-2.0 | W/(m2 K) |
| U-value, south windows | 0.8-2.0 | W/(m2 K) |
| U-value, east windows | 0.8-2.0 | W/(m2 K) |
| U-value, west windows | 0.8-2.0 | W/(m2 K) |
| U-value, main external wall | 0.25-0.80 | W/(m2 K) |
| U-value, roof | 0.20-0.45 | W/(m2 K) |
| U-value, ground floor | 0.15-0.40 | W/(m2 K) |
| SHGC, north windows | 0.20-0.65 | -- |
| SHGC, south windows | 0.20-0.45 | -- |
| SHGC, east windows | 0.20-0.65 | -- |
| SHGC, west windows | 0.20-0.65 | -- |
| Window construction type* | 1-3 | -- |
| Roof insulation thickness | 0.08-0.15 | m |
| Floor number | 6-20 | floors |
| Public area | 80-150 | m2 |
| Single guest room area | 22-30 | m2 |
| Guest room count | 36-240 | rooms |
| Building length | 35-50 | m |
| Aspect ratio | 2.0-3.0 | -- |
| Floor height | 2.8-3.3 | m |
| Orientation | 0-90 | deg |
| Equipment power density | 2.5-4.0 | W/m2 |
| DHW per capita | 0.06-0.20 | m3/(person d) |
| Occupancy density | 0.08-0.25 | person/m2 |
| Lighting power density | 4.0-7.0 | W/m2 |
| Cooling setpoint | 24-26 | deg C |
| Heating setpoint | 19-22 | deg C |
| DHW supply temperature | 45-55 | deg C |
| Cooling COP | 3.0-5.0 | -- |
| Heating COP | 2.2-4.2 | -- |
| Boiler efficiency | 0.82-0.95 | -- |
| Fan efficiency | 0.55-0.70 | -- |
| Fresh air rate | 0.5-1.2 | h-1 |
| Operating hours | 2,000-3,000 | h/a |

*Window types: Type 1 = double-pane clear (U~1.8, SHGC~0.55); Type 2 = double-pane low-E (U~1.4, SHGC~0.40); Type 3 = triple-pane low-E (U~0.8, SHGC~0.25).

#### 3.2.2. LHS and Feasibility Screening

Latin Hypercube Sampling (LHS) was implemented using scipy.stats.qmc.LatinHypercube (random seed = 42) to generate 20,000 parameter combinations. LHS, by stratifying each dimension into equally probable intervals, provides more uniform coverage of the high-dimensional parameter space than simple random sampling.

After LHS generation, a rule-based feasibility screening was applied to remove physically infeasible combinations. The building width was derived as building_width = building_length / aspect_ratio (constrained to [12, 18] m). The gross floor area was computed as building_length x building_width x floor_num. The usable area ratio was defined as:

$$\text{usable_area_ratio} = (\text{room_area} \times \text{room_count} + \text{public_area}) / (\text{building_length} \times \text{building_width} \times \text{floor_num})$$

Samples were retained only when this ratio fell within [0.55, 0.95]. The 0.55 lower bound - ensuring at least 55% of gross floor area is allocated to usable functions - is consistent with the space allocation requirements in GB 50189-2015 and comparable feasibility checks in the literature (Zhang et al., 2024, Buildings 14:356; Permana et al., 2023, Buildings 13:1022). The 0.95 upper bound reflects the structural impossibility of allocating less than 5% of gross floor area to structural cores and MEP spaces in mid-to-high-rise buildings. Through this screening, the 20,000 LHS samples were reduced to 4,640 valid samples (23.2% retention). The high rejection rate reflects the intrinsic challenge of independently sampling six geometric parameters over wide ranges: many random combinations inevitably produce geometrically impossible buildings. Distribution analysis (Supplementary Material, Figure S1) confirms that the filtering does not systematically exclude specific regions of the parameter space.

#### 3.2.3. EnergyPlus Model Specification

The hotel building was modeled as a single-zone rectangular prism. The building footprint = building_length x building_width, and total height = floor_num x floor_height. The HVAC system used HVACTemplate:Zone:IdealLoadsAirSystem, which computes heating and cooling as ideal loads. This choice provides a consistent, comparable baseline across thousands of design variants without introducing equipment-specific dynamics. Engineering postprocessing converts ideal loads to site energy: cooling electricity = cooling_load / COP_cooling; heating electricity = heating_load / COP_heating; fan electricity = fresh_air_ach x volume / 3600 x 600 Pa / fan_efficiency; lighting = light_power x floor_area; equipment = equip_power x floor_area. Domestic hot water energy is calculated analytically: DHW_energy = dhw_per_person x estimated_people x rho x cp x (dhw_temp - 15 deg C) x 365 / boiler_efficiency, where estimated_people = min(room_count x 1.6, floor_area x occupancy_density).

Constructions use Material:NoMass with R-values derived from sampled U-values. Windows use WindowMaterial:SimpleGlazingSystem with orientation-specific U-values and SHGCs. The occupancy schedule fraction = daily_operation_hours / 24, clipped to [0.15, 1.0]. The weather file is Beijing.epw from the China Standard Weather Data (CSWD) collection [https://energyplus.net/weather]. EnergyPlus 25.2.0 was called via subprocess with ExpandObjects preprocessing. Each simulation was verified through return-code checking and eplusout.err inspection. Annual end-use results were extracted from eplusout.sql via SQL queries.

### 3.3. Sensitivity Analysis

#### 3.3.1. Variable Preprocessing

Building orientation was encoded using sine and cosine transformations of the angle in radians. Building length and width were transformed into footprint area (length x width) and aspect ratio (length / width). Window construction type was one-hot encoded with Type 1 as the reference category, yielding 39 input features.

#### 3.3.2. Multicollinearity Diagnosis

Variance Inflation Factors (VIF) were computed by regressing each variable against all others and calculating VIF = 1/(1 - R2). All variables except the orientation sine and cosine terms (VIF = 6.4) exhibited VIF values below 5, confirming the absence of problematic multicollinearity.

#### 3.3.3. SRC Estimation with Bootstrap

SRC values were estimated by fitting ordinary least squares on standardized variables (X_std and y_std via StandardScaler). Bootstrap resampling (B = 1,000, seed = 42) with replacement was used to construct 95% percentile confidence intervals. A variable was deemed sign-stable if its CI did not contain zero.

#### 3.3.4. SHAP Cross-Validation

Acknowledging that SRC is fundamentally a linear method and that the EUI response surface exhibits substantial nonlinearity (as later confirmed by the strong performance of Poly3-RidgeCV), SHAP values were computed using a fitted XGBoost regressor (n_estimators = 500, max_depth = 5) as a supplementary nonlinear sensitivity method. The Spearman rank correlation between SRC-based and SHAP-based variable rankings was computed to assess convergence.

#### 3.3.5. Key Variable Selection

Key variables were selected based on combined evidence from SRC magnitude, bootstrap sign stability, SHAP ranking, and cumulative |SRC| contribution. The cutoff at 18 variables was supported by: cumulative |SRC| > 95%; all 18 variables sign-stable; and plateau in 5-fold CV R2 beyond 18 variables (Figure 5).

### 3.4. Machine Learning Surrogate Model Training

Seventeen regression models were compared: LinearRegression, RidgeCV, LassoCV, ElasticNetCV, Poly2-RidgeCV, Poly2-ElasticNetCV, Poly2-Interaction-RidgeCV, Poly3-RidgeCV, KNN, SVR-RBF, DecisionTree, RandomForest, ExtraTrees, GradientBoosting, XGBoost, LightGBM, and MLPRegressor. The 18 key variables served as input features.

Hyperparameter tuning was performed for all models containing tunable parameters: GridSearchCV (KNN, exhaustive grid) or RandomizedSearchCV (SVR, RandomForest, ExtraTrees, GB, MLP, DecisionTree, XGBoost, LightGBM; 20 iterations each) with 10-fold CV and neg_root_mean_squared_error scoring. RidgeCV, LassoCV, and ElasticNetCV used internal 10-fold CV over logarithmic alpha grids. Complete search spaces and final hyperparameters are reported in Supplementary Table S1.

Data were split 80/20 (train/test) with random seed 42. Models were evaluated using test-set R2, 10-fold CV R2 variance, RMSE, MAPE, and generalization gap (train R2 - test R2). Models were ranked by test R2 (descending), test RMSE (ascending), and generalization gap (ascending).

### 3.5. EUI-OCEI Coupling Analysis

#### 3.5.1. Carbon Accounting Boundary

A fixed carbon accounting boundary was adopted: space heating -> district heating; space cooling -> district cooling; domestic hot water -> natural gas; building-side electricity (lighting, equipment, fans) -> electricity. This reflects a typical energy supply configuration for large Beijing hotel buildings.

#### 3.5.2. Emission Factors

Carbon emission factors (Table 5) were sourced from official Chinese standards and published literature: electricity (0.55 kgCO2e/kWh) from the Ministry of Ecology and Environment's 2022 guidelines for the North China grid; natural gas (0.202 kgCO2e/kWh) from GB/T 51366-2019, the national building carbon calculation standard; district heating (0.22 kgCO2e/kWh) from Zheng et al. (2018); and district cooling (0.16 kgCO2e/kWh) derived from a typical district cooling COP of 4.5.

**Table 5.** Carbon emission factors by energy carrier.

| Carrier | Factor (kgCO2e/kWh) | Source | Year |
|---------|---------------------|--------|------|
| Electricity | 0.55 | MEE Guidelines; North China Grid | 2022 |
| Natural Gas | 0.202 | GB/T 51366-2019, Appendix A | 2019 |
| District Heating | 0.22 | Zheng et al. (2018), Energy Build. 179:1-14 | 2018 |
| District Cooling | 0.16 | Derived (COP=4.5, grid EF) | -- |

#### 3.5.3. Emission Factor Sensitivity Analysis

Six scenarios were tested: (1) Baseline; (2) Low electricity (0.40); (3) High electricity (0.70); (4) Grid decarbonisation 2030 (0.40); (5) Grid decarbonisation 2050 (0.25); and (6) High district heating (DH=0.30, DC=0.20). For each scenario, OCEI was recalculated, and EUI-OCEI Pearson correlation and top-10% ranking overlap with the baseline were assessed.

#### 3.5.4. Coupling Analysis Methods

Pearson correlation quantified the EUI-OCEI relationship. Ranking analysis compared EUI- and OCEI-based ordering with top-10% overlap and mean absolute rank shift. Comparative SRC analysis (B = 1,000 bootstrap) was conducted for both EUI and OCEI on the same 20 predictor variables.

## 4. Results

### 4.1. Simulation Database Characteristics

Figures 1 and 2 show the EUI and total energy consumption distributions across the 4,640 valid samples. Both distributions exhibit moderate right skewness. The EUI ranges from approximately 80 to 220 kWh/(m2.a), with a mean of 140.6 and median of 136.7 kWh/(m2.a).

Figure 3 compares the simulated EUI distribution with published measurements from 56 Beijing hotel buildings [Chen, Tan & Berardi, 2018; ref. 53]. The measured data show a statistical mean of 123.0 kWh/(m2.a) and an interquartile range of approximately [88, 145] kWh/(m2.a). The simulated mean is approximately 14% higher than the measured mean, attributable to idealized HVAC operation assumptions, conservative parameter range choices, and the absence of part-load effects and adaptive occupant behaviours in simulation. However, the simulated range (80-220) falls within the broader measured range (45-342 kWh/(m2.a)), and Chinese national cold-zone hotel benchmarks (GB/T 51161-2016: 110-240 kWh/(m2.a)) bracket the results. The sim-to-real transfer gap is discussed in Section 5.

### 4.2. Sensitivity Analysis

#### 4.2.1. SRC and Bootstrap Results

VIF values confirm the absence of problematic multicollinearity (VIF < 5 for all variables except orientation terms, Table 2). The SRC analysis (Table 3) reveals that domestic hot water consumption per capita dominates (SRC = +0.808, CI [+0.794, +0.820]), followed by floor number (SRC = -0.705), guest room count (SRC = +0.554), and building footprint area (SRC = -0.504). Of the 39 variables, 22 are sign-stable; all top-18 variables are sign-stable.

#### 4.2.2. SHAP Cross-Validation

Figure 4 compares SRC-based and SHAP-based variable rankings. The Spearman rank correlation is 0.891, indicating strong agreement between linear and nonlinear importance measures. Of the SRC top-18, 16 also appear in the SHAP top-18 (Jaccard index = 0.80). The two variables unique to the SRC top-18 (u_wall and room_area) have small |SRC| values (< 0.03) and their exclusion would not materially affect predictive performance. No major variable identified by SHAP is missed by the SRC screening.

#### 4.2.3. Variable Selection

Figure 5 shows the scree plot, cumulative contribution, and CV R2 versus variable count. The first 18 variables account for 95.8% of cumulative |SRC|, and the CV R2 plateaus at n = 18 (R2 = 0.944), confirming the suitability of this cutoff.

### 4.3. EUI Surrogate Model Performance

Table 4 presents the test-set performance of all 17 models. Poly3-RidgeCV achieves the highest test R2 (0.9976) with RMSE = 1.72 kWh/(m2.a) and MAPE = 1.34%. MLP follows closely (R2 = 0.9973, RMSE = 1.83, MAPE = 1.41%). Polynomial models broadly outperform tree-based models, which in turn outperform linear models. The strong performance of Poly3-RidgeCV indicates that a substantial portion of the EUI response surface nonlinearity can be captured through explicit third-order polynomial expansion with regularisation, while MLP's competitive performance suggests additional implicit nonlinear structure.

**Table 4.** Model performance (test set, top 5 + representative baselines).

| Model | Test R2 | CV R2 Var | RMSE | MAPE(%) | Gen. Gap |
|-------|---------|-----------|------|---------|----------|
| Poly3-RidgeCV | 0.9976 | 1.0e-07 | 1.72 | 1.34 | +0.0014 |
| MLP | 0.9973 | 2.8e-06 | 1.83 | 1.41 | -0.0000 |
| Poly2-ElasticNetCV | 0.9941 | 3.0e-07 | 2.69 | 2.04 | +0.0005 |
| Poly2-RidgeCV | 0.9941 | 3.0e-07 | 2.71 | 2.05 | +0.0006 |
| Poly2-Interaction-RidgeCV | 0.9877 | 1.1e-06 | 3.91 | 3.01 | -0.0004 |
| SVR-RBF | 0.9853 | 5.3e-06 | 4.27 | 3.15 | +0.0141 |
| XGBoost | 0.9791 | 4.5e-06 | 5.09 | 3.82 | +0.0154 |
| LightGBM | 0.9781 | 9.7e-06 | 5.21 | 3.91 | +0.0210 |
| RidgeCV | 0.9443 | 2.1e-05 | 8.31 | 6.61 | +0.0011 |
| RandomForest | 0.8303 | 2.7e-04 | 14.50 | 11.50 | +0.0856 |
| KNN | 0.6796 | 2.2e-04 | 19.93 | 16.06 | +0.2235 |

Complete table with all 17 models in Supplementary Table S2.

**Table 5.** Hyperparameter summary for top five models.

| Model | Tuning | Key Best Parameters |
|-------|--------|---------------------|
| Poly3-RidgeCV | RidgeCV(cv=10), alpha logspace(-1,5,30) | degree=3, alpha=0.0215, features=1330 |
| MLP | RandomizedSearchCV(20 iter, cv=10) | hidden=(128,64), activation=relu, alpha=0.01 |
| Poly2-ElasticNetCV | ElasticNetCV(cv=10), 20 alphas, 5 l1_ratios | degree=2, alpha=0.0032, l1_ratio=0.1 |
| Poly2-RidgeCV | RidgeCV(cv=10), alpha logspace(-2,4,30) | degree=2, alpha=0.0464 |
| Poly2-Interaction-RidgeCV | RidgeCV(cv=10), alpha logspace(-2,4,30) | degree=2(interact), alpha=0.0215 |

Complete hyperparameters for all 17 models in Supplementary Table S1.

Figures 12 and 13 present the predicted-versus-simulated EUI scatter plots for Poly3-RidgeCV and MLP. Both show tight clustering along the diagonal with no visible bias.

### 4.4. EUI-OCEI Coupling

#### 4.4.1. OCEI Distribution and Carrier Contributions

OCEI follows a unimodal distribution with mean = 48.19, median = 47.40, SD = 7.91, and range = [29.80, 80.57] kgCO2e/(m2.a) (Figure 14). Figure 15 presents the carbon contribution breakdown: natural gas dominates (38.1%), followed by electricity (27.2%), district heating (22.2%), and district cooling (12.5%).

#### 4.4.2. EUI-OCEI Correlation

EUI and OCEI are strongly correlated (Pearson r = 0.954, p < 0.001; Figure 17). However, OCEI exhibits noticeable dispersion within similar EUI intervals, consistent with the hypothesis that carbon performance depends additionally on the energy carrier mix.

#### 4.4.3. Ranking Comparison

Figure 18 compares EUI-based and OCEI-based rankings. The top-10% overlap ratio is 76.3%, and the mean absolute rank shift is 287 positions (out of 4,640). Approximately 24% of top-EUI samples do not rank in the top OCEI decile, demonstrating that the two rankings are not interchangeable.

#### 4.4.4. Emission Factor Sensitivity

Table 6 presents the sensitivity results. Mean OCEI varies from 42.06 (Grid Decarb. 2050) to 53.48 kgCO2e/(m2.a) (High Electricity), a +/-11% range. Critically, the EUI-OCEI correlation remains robust (r range: 0.938-0.958), and the top-10% overlap with baseline ranges from 83.3% to 96.8%. This demonstrates that while absolute OCEI values depend on emission factor choices, the core coupling structure is robust.

**Table 6.** Emission factor sensitivity results.

| Scenario | Mean OCEI | EUI-OCEI r | Top-10% Overlap |
|----------|-----------|------------|-----------------|
| Baseline | 48.19 | 0.954 | 1.000 (ref.) |
| Low Electricity (0.40) | 45.22 | 0.958 | 0.952 |
| High Electricity (0.70) | 53.48 | 0.948 | 0.918 |
| Grid Decarb. 2030 (0.40) | 45.22 | 0.958 | 0.952 |
| Grid Decarb. 2050 (0.25) | 42.06 | 0.957 | 0.968 |
| High District Heating | 50.31 | 0.938 | 0.833 |

#### 4.4.5. Comparative SRC Analysis

Figure 19 compares SRC patterns for EUI and OCEI. DHW-related variables (dhw_per_person, boiler_eff) and heat-source efficiency variables exhibit amplified importance in the OCEI dimension, reflecting the high carbon intensity of natural gas relative to grid electricity. This confirms that variables affecting DHW and natural gas consumption have a disproportionate impact on carbon performance, supporting the conclusion that energy-saving and low-carbon optimization are not fully aligned.

## 5. Discussion

### 5.1. Interpretation of Key Findings

This study constructed an integrated framework of "parametric simulation -> key variable identification -> machine learning surrogate modeling -> EUI/OCEI coupled analysis" and verified its applicability using Beijing hotel buildings. The results demonstrate that hotel building EUI variation is shaped by the combined effects of envelope thermal parameters, building geometry, occupant and equipment loads, and HVAC operational control parameters, with domestic hot water demand emerging as the single most influential factor (SRC = +0.808). This finding distinguishes hotels from other commercial building types where envelope or HVAC parameters typically dominate.

The strong performance of Poly3-RidgeCV and MLP confirms that the EUI response surface contains structured higher-order nonlinearities and variable interaction effects. SHAP analysis validates the SRC-based variable ranking, providing confidence that the linear screening -- despite its simplicity -- captures the dominant sensitivity structure. This integrated approach addresses the limitations of black-box-only or linear-only analyses noted in the literature.

### 5.2. Sim-to-Real Transfer Gap

A critical limitation of this study, highlighted in the reviewer comments, is that all models were trained and tested purely on EnergyPlus simulation outputs. The R2 of 0.9976 for Poly3-RidgeCV reflects surrogate fidelity -- how well the model mimics the simulator -- not prediction accuracy for real buildings. Comparison with published Beijing hotel measurements (mean EUI = 123 kWh/(m2.a); Chen, Tan & Berardi, 2018) reveals a +14% mean overestimation in the simulated data. Several factors contribute to this gap: (a) the simulation uses idealized HVAC (IdealLoadsAirSystem) without advanced controls, energy management systems, or part-load effects; (b) parameter ranges were deliberately conservative to capture the full design space; (c) adaptive occupant behaviours, diversity in operational schedules, and equipment degradation -- all of which reduce real energy consumption -- are not modeled. The framework should therefore be understood as a comparative design-support tool rather than an absolute prediction instrument. Extending the framework with real-building calibration data is a priority for future work.

### 5.3. Methodological Limitations and Future Work

Several limitations warrant discussion:

**Feasibility screening:** The 77% rejection rate, while justified by building-code constraints and the inherent nature of independent LHS sampling over wide geometric ranges, necessarily reduces the effective sample diversity. The filtering is by construction unbiased with respect to energy outcomes (screening uses only geometric consistency, not simulated EUI), but future work could explore alternative constrained sampling strategies (e.g., copula-based dependence modeling) to reduce the rejection rate while maintaining feasibility.

**SRC linearity assumption:** Although SHAP cross-validation confirms the SRC ranking in this dataset (Spearman r = 0.891), SRC may still underestimate variables whose influence operates primarily through interactions. Future work could apply variance-based Sobol indices for a more complete global sensitivity decomposition, though this would require substantially larger sample sizes.

**Hotel category aggregation:** This study does not distinguish among hotel categories (star ratings), which are associated with systematic differences in service level, occupancy characteristics, and end-use energy demand. Published data indicate that energy intensity can vary by a factor of two or more between budget and luxury hotels. The constructed database, with its broad parameter ranges, likely spans multiple hotel categories, but a category-stratified analysis would improve model transferability and practical applicability.

**Non-core variable simplification:** Excluding variables ranked 19-39 from surrogate modeling simplifies training and improves interpretability, and the supplementary analysis (Supplementary Material) confirms that adding these 19 variables yields negligible R2 improvement (< 0.001). However, this does not imply that these variables are irrelevant to building energy performance in general -- only that their influence is small relative to the top 18 within the current parameter space and that their values are typically well-approximated by median defaults during early-stage design.

**Carbon accounting scope:** The OCEI analysis adopts a fixed carbon accounting boundary and static emission factors. While the sensitivity analysis demonstrates robustness to factor variations, the framework does not yet incorporate time-varying grid emission factors, renewable energy integration scenarios, or embodied carbon. Extending the framework to dynamic, multi-scenario carbon accounting is a productive direction for future research.

### 5.4. Practical and Engineering Implications

Despite these limitations, the framework offers several practical contributions. First, it enables rapid EUI screening of hotel design alternatives using only 18 readily available parameters, reducing evaluation time from hours (full EnergyPlus simulation) to milliseconds (surrogate model prediction). Second, the identification of DHW-related variables as the dominant influence on both EUI and OCEI points to a clear priority for hotel energy optimization: improving domestic hot water system efficiency and reducing hot water demand. Third, the demonstrated non-equivalence of EUI and OCEI rankings (24% of top-EUI samples not in the top OCEI decile under baseline emission factors) has direct policy relevance: building energy codes that target EUI alone may not achieve commensurate carbon reductions, and a dual-indicator evaluation framework is recommended.

### 5.5. Comparison with Previous Studies

Compared with previous studies that focused either on local parameter analysis [23,24,25,26] or on black-box model fitting [10,11,12], this study contributes a more integrated pathway linking variable screening, surrogate modeling, and energy-carbon coupling within one unified framework. The use of SHAP to cross-validate SRC rankings -- and the finding of strong agreement (r = 0.891) -- provides methodological reassurance that interpretable linear screening, despite its simplicity, can serve as a reliable first-stage filter even in the presence of moderate nonlinearity. This finding may have broader relevance for building energy studies where computational constraints preclude exhaustive nonlinear sensitivity analysis.

## 6. Conclusions

This study established and validated an integrated framework for EUI surrogate modeling and EUI-OCEI coupling analysis of Beijing hotel buildings through four sequential steps.

First, a parametric simulation database was constructed by generating 20,000 LHS parameter combinations over 38 design variables, applying rule-based feasibility screening to retain 4,640 valid samples, and performing EnergyPlus simulations. The simulated EUI range (80-220 kWh/(m2.a)) captures realistic variability when benchmarked against published Beijing hotel measurements.

Second, SRC combined with bootstrap resampling identified 18 key variables with significant and stable effects on EUI. SHAP analysis using XGBoost confirmed the variable ranking (Spearman r = 0.891). Domestic hot water consumption per capita, building form parameters (floor number, room count, footprint area), and HVAC operational parameters dominate the EUI sensitivity structure.

Third, systematic comparison of 17 machine learning surrogate models with fully reported hyperparameter tuning revealed that Poly3-RidgeCV (test R2 = 0.9976, MAPE = 1.34%) and MLP (test R2 = 0.9973, MAPE = 1.41%) achieve the best overall performance. The strong showing of polynomial models indicates that a considerable portion of the EUI response nonlinearity can be captured through explicit higher-order feature expansion.

Fourth, the EUI-OCEI coupling analysis demonstrated that while the two indicators are strongly correlated (Pearson r = 0.954), they are not equivalent: the top-10% ranking overlap is 76.3%, and DHW-related variables carry amplified weight in the carbon dimension. Emission factor sensitivity analysis confirmed the robustness of these findings across plausible alternative assumptions.

The principal conclusion is that for Beijing hotel buildings, a surrogate modeling framework built on 18 key design parameters can approximate EnergyPlus-simulated EUI with high fidelity, and that extending this framework to OCEI reveals meaningful divergences between energy-performance and carbon-performance priorities. Designers and policymakers should adopt a dual-indicator approach -- considering both EUI and OCEI -- rather than optimising for energy efficiency alone.

## References

[1] Zhao, Z.-Y.; Chang, R.-D.; Zillante, G. Challenges for China's energy conservation and emission reduction. Energy Policy 2014, 74, 709-713.

[2] Perez-Lombard, L.; Ortiz, J.; Pout, C. A review on buildings energy consumption information. Energy and Buildings 2008, 40, 394-398.

[3] Chung, M.; Park, H.-C. Comparison of building energy demand for hotels, hospitals, and offices in Korea. Energy 2015, 92, 383-393.

[4] Han, S.; Yao, R.; Li, N. The development of energy conservation policy of buildings in China: A comprehensive review and analysis. Journal of Building Engineering 2021, 38, 102229.

[5] Wu, P.; Shi, P. An estimation of energy consumption and CO2 emissions in tourism sector of China. J. Geogr. Sci. 2011, 21, 733-745.

[6] Fumo, N.; Mago, P.; Luck, R. Methodology to estimate building energy consumption using EnergyPlus benchmark models. Energy and Buildings 2010, 42, 2331-2337.

[7] Hu, J.; Wu, J. Analysis on the influence of building envelope to public buildings energy consumption based on DeST simulation. Procedia Engineering 2015, 121, 1620-1627.

[8] Ke, M.-T.; Yeh, C.-H.; Jian, J.-T. Analysis of building energy consumption parameters and energy savings measurement and verification by applying eQUEST software. Energy and Buildings 2013, 61, 100-107.

[9] Shahcheraghian, A.; Madani, H.; Ilinca, A. From White to Black-Box Models: A Review of Simulation Tools for Building Energy Management. Energies 2024, 17, 376.

[10] Chen, C.; Gao, Z.; Zhou, X.; Wang, M.; Yan, J. Energy consumption prediction and energy-saving suggestions of public buildings based on machine learning. Energy and Buildings 2024, 320, 114585.

[11] Ahmad, M.W.; Mourshed, M.; Rezgui, Y. Trees vs. Neurons: Comparison between random forest and ANN for high-resolution prediction of building energy consumption. Energy and Buildings 2017, 147, 77-89.

[12] Wang, Z.; Wang, Y.; Zeng, R.; Srinivasan, R.S.; Ahrentzen, S. Random forest based hourly building energy prediction. Energy and Buildings 2018, 171, 11-25.

[13] Li, C.; Hong, T.; Yan, D. An insight into actual energy use and its drivers in high-performance buildings. Applied Energy 2014, 131, 394-410.

[14] Olu-Ajayi, R.; Alaka, H.; Egwim, C.; Grishikashvili, K. Comprehensive Analysis of Influencing Factors on Building Energy Performance. Sustainability 2024, 16, 5170.

[15] Muhic, S.; Manic, D.; Cikic, A.; Komatina, M. Influence of Building Envelope Modeling Parameters on Energy Simulation Results. Sustainability 2025, 17, 5276.

[16] Kim, D.; Lee, J.; Do, S.; Mago, P.J.; Lee, K.H.; Cho, H. Energy Modeling and Model Predictive Control for HVAC in Buildings. Energies 2022, 15, 7231.

[17] Echarri-Iribarren, V.; Fernandez-Sedas, C.; Lopez-Zapata, R. DHW Storage and Recirculation Systems in High-Rise Hotel Buildings. Buildings 2026, 16, 863.

[18] Permana, I.; Wang, F.; Agharid, A.P.; Rakshit, D.; Luo, J. Energy Consumption Analysis Using Weighted Energy Index and Energy Modeling for a Hotel Building. Buildings 2023, 13, 1022.

[19] Papadakis, N.; Katsaprakakis, D.A. A Review of Energy Efficiency Interventions in Public Buildings. Energies 2023, 16, 6329.

[20] Kistelegdi, I.; Horvath, K.R.; Storcz, T.; Ercsey, Z. Building Geometry as a Variable in Energy, Comfort, and Environmental Design Optimization. Buildings 2022, 12, 69.

[21] Agharid, A.P.; Permana, I.; Singh, N.; Wang, F.; Gustiyana, S. Energy-Efficient and Cost-Effective Approaches through Energy Modeling for Hotel Building. Energy Engineering 2024, 121, 3549-3571.

[22] Xu, X.; Dan, Z. Exploring the Evolution of Energy Research in Hospitality. Energy Rep. 2023, 10, 864-880.

[23] Zhu, W.; Zheng, Z.; Liu, M.; Deng, G. A Case Study on Existing Building HVAC System Optimization of a Five-Star Hotel in Shanghai. In Proceedings of ISHVAC 2019; Springer: Singapore, 2020; pp. 589-597.

[24] Alhuwayil, W.K.; Gadi, M.B.; Almaziad, F.A.; Alhuthali, A.H.; Abdelrahman, M.A.E. Energy Performance of Passive Shading and Thermal Insulation in Multistory Hotel Building. Case Stud. Therm. Eng. 2023, 45, 102940.

[25] Tian, W. A Review of Sensitivity Analysis Methods in Building Energy Analysis. Renew. Sustain. Energy Rev. 2013, 20, 411-419.

[26] Roka, R.; Figueiredo, A.; Vieira, A.; Cardoso, C. A Systematic Review of Sensitivity Analysis in Building Energy Modeling. Energies 2025, 18, 2375.

[27] Pan, Y.; Zhu, M.; Lv, Y.; et al. Building Energy Simulation and Its Application for Building Performance Optimization. Adv. Appl. Energy 2023, 10, 100135.

[28] Dimara, A.; Krinidis, S.; Ioannidis, D.; Tzovaras, D. Building Performance Simulation. In Disrupting Buildings; Palgrave Macmillan: Cham, 2023; pp. 53-67.

[29] Solmaz, A.S. A Machine Learning-Based Early Design Energy Prediction Framework for School Buildings. Buildings 2026, 16, 779.

[30] Westermann, P.; Evins, R. Surrogate Modelling for Sustainable Building Design -- A Review. Energy Build. 2019, 198, 170-186.

[31] Ji, J.; Yu, H.; Wang, X.; Xu, X. Machine Learning Application in Building Energy Consumption Prediction: A Comprehensive Review. J. Build. Eng. 2025, 104, 112295.

[32] Chen, Z.; Xiao, F.; Guo, F.; Yan, J. Interpretable Machine Learning for Building Energy Management. Adv. Appl. Energy 2023, 9, 100123.

[33] Manfren, M.; Gonzalez-Carreon, K.M.; James, P.A.B. Interpretable Data-Driven Methods for Building Energy Modelling. Energies 2024, 17, 881.

[34] Shirzadi, N.; Lau, D.; Stylianou, M. Surrogate Modeling for Building Design: Energy and Cost Prediction Compared to Simulation-Based Methods. Buildings 2025, 15, 2361.

[35] Arenhart, R.S.; Martins, T.; Ueda, R.M.; Souza, A.M.; Zanini, R.R. Energy Use and Its Contributors in Hotel Buildings: A Systematic Review and Meta-Analysis. PLoS ONE 2024, 19, e0309745.

[36] Cornette, J.F.P.; Blondeau, J. Operational Greenhouse Gas Emissions of Various Energy Carriers for Building Heating. Cleaner Energy Systems 2024, 9, 100148.

[37] Yang, S.; Gao, H.O.; You, F. Building Electrification and Carbon Emissions: Integrated Energy Management Considering the Dynamics of the Electricity Mix and Pricing. Adv. Appl. Energy 2023, 10, 100141.

[38] Xu, L.; Liu, J.; Pei, J.; Han, X. Building energy saving potential in hot summer and cold winter zone, China. Energy Policy 2013, 57, 253-262.

[39] Tian, W. A review of sensitivity analysis methods in building energy analysis. Renewable and Sustainable Energy Reviews 2013, 20, 411-419.

[40] Saltelli, A.; Ratto, M.; Andres, T.; et al. Global Sensitivity Analysis: The Primer; John Wiley & Sons: Hoboken, NJ, 2008.

[41] Chatterjee, S.; Hadi, A.S. Sensitivity Analysis in Linear Regression; John Wiley & Sons: New York, 1988.

[42] Bland, J.M.; Altman, D.G. Statistics notes: Bootstrap resampling methods. BMJ 2015, 350, h2622.

[43] Chernick, M.R. Resampling methods. WIREs Data Mining and Knowledge Discovery 2012, 2, 255-262.

[44] Li, X.; Li, Q.; Qiu, Z.; et al. Study on influencing factors of energy consumption building characteristics of high-rise hotel standard floor. J. Phys. Conf. Ser. 2023, 2468, 012148.

[45] Zhang, J.; Yuan, C.; Yang, J.; Zhao, L. Research on Energy Consumption Prediction Models for High-Rise Hotels in Guangzhou. Buildings 2024, 14, 356.

[46] Arenhart, R.S.; Souza, A.M.; Zanini, R.R. Energy Use and Its Key Factors in Hotel Chains. Sustainability 2022, 14, 8239.

[47] Python. Available online: https://www.python.org.

[48] EnergyPlus. Available online: https://energyplus.net/.

[49] Borowski, M.; Zwolinska, K. Prediction of Cooling Energy Consumption in Hotel Building Using Machine Learning Techniques. Energies 2020, 13, 6226.

[50] Komurcu, D.; Edis, E. Machine Learning Modeling for Building Energy Performance Prediction Based on Simulation Data. Buildings 2025, 15, 1301.

[51] Zheng, L.; Luo, K.; Zhao, L. An Operational Carbon Emission Prediction Model Based on Machine Learning Methods for Urban Residential Buildings in Guangzhou. Buildings 2024, 14, 3699.

[52] GB 50189-2015. Energy Efficiency Design Standard for Public Buildings; Ministry of Housing and Urban-Rural Development of the People's Republic of China; China Construction Industry Press: Beijing, 2015.

[53] Chen, Y.; Tan, H.; Berardi, U. A data-driven approach for building energy benchmarking using the Lorenz curve. Energy and Buildings 2018, 169, 319-331.

[54] Sheng, Y.; Miao, Z.; Zhang, J.; Lin, X.; Ma, H. Energy consumption model and energy benchmarks of five-star hotels in China. Energy and Buildings 2018, 165, 286-292.

[55] Tian, W.; Song, J.; Li, Z.; de Wilde, P. Bootstrap techniques for sensitivity analysis and model selection in building thermal performance analysis. Applied Energy 2014, 135, 320-328.

[56] GB/T 51366-2019. Standard for Building Carbon Emission Calculation; Ministry of Housing and Urban-Rural Development of the People's Republic of China; China Construction Industry Press: Beijing, 2019.

[57] Zheng, W.; Xu, W.; Wang, D.; Li, L.; Niu, L.; Wang, W.; Wang, B.; Song, Y. A study of city-level building energy efficiency benchmarking system for China. Energy and Buildings 2018, 179, 1-14.

[58] Ji, Y.; Lu, Q.; Niu, M.; Zhang, N.; Xie, J. Research on the characteristics and influence factors of residential building energy usage patterns: A case study in Beijing. Energy for Sustainable Development 2025, 85, 101654.

[59] Cai, W.G.; Wu, Y.; Zhong, Y.; Ren, H. China building energy consumption: Situation, challenges and corresponding measures. Energy Policy 2009, 37, 2054-2059.

[60] Yu, H.; Pan, S.Y.; Tang, B.J.; et al. Urban energy consumption and CO2 emissions in Beijing: Current and future. Energy Efficiency 2015, 8, 527-543.
