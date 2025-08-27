#!/usr/bin/env python3
"""
Create clean summary of projection correlation analysis results
"""

print("=== DRAFT PROJECTION vs ACTUAL RESULTS ANALYSIS ===")
print("")

# Results from the analysis
results = {
    2015: {"corr": 0.402, "win_corr": 0.648, "p_val": 0.250, "teams": 10},
    2016: {"corr": -0.279, "win_corr": -0.160, "p_val": 0.435, "teams": 10},
    2017: {"corr": 0.143, "win_corr": 0.092, "p_val": 0.658, "teams": 12},
    2018: {"corr": 0.188, "win_corr": 0.168, "p_val": 0.604, "teams": 10},
    2019: {"corr": None, "win_corr": 0.657, "p_val": None, "teams": 10},  # NaN due to constant input
    2020: {"corr": -0.191, "win_corr": -0.310, "p_val": 0.598, "teams": 10},
    2021: {"corr": -0.292, "win_corr": -0.276, "p_val": 0.413, "teams": 10},
    2022: {"corr": -0.191, "win_corr": 0.064, "p_val": 0.597, "teams": 10},
    2023: {"corr": 0.123, "win_corr": -0.024, "p_val": 0.735, "teams": 10},
    2024: {"corr": 0.129, "win_corr": -0.003, "p_val": 0.722, "teams": 10}
}

print("YEAR-BY-YEAR RESULTS:")
print("Year | Teams | Proj vs Standing | Proj vs Win% | P-Value | Significant?")
print("-" * 75)

significant_count = 0
valid_correlations = []

for year in sorted(results.keys()):
    r = results[year]
    corr_str = f"{r['corr']:.3f}" if r['corr'] is not None else "N/A"
    win_corr_str = f"{r['win_corr']:.3f}"
    p_str = f"{r['p_val']:.3f}" if r['p_val'] is not None else "N/A"
    sig_str = "YES" if r['p_val'] is not None and r['p_val'] < 0.05 else "NO"
    
    if r['corr'] is not None:
        valid_correlations.append(r['corr'])
    
    if r['p_val'] is not None and r['p_val'] < 0.05:
        significant_count += 1
    
    print(f"{year} | {r['teams']:5} | {corr_str:15} | {win_corr_str:11} | {p_str:7} | {sig_str}")

print("")
print("SUMMARY STATISTICS:")
print(f"Years analyzed: {len(results)}")
print(f"Valid correlations: {len(valid_correlations)}")

if valid_correlations:
    import numpy as np
    avg_corr = np.mean(valid_correlations)
    min_corr = min(valid_correlations)
    max_corr = max(valid_correlations)
    
    print(f"Average correlation (projection vs standing): {avg_corr:.3f}")
    print(f"Correlation range: {min_corr:.3f} to {max_corr:.3f}")
    print(f"Best year: 2015 ({max_corr:.3f})")
    print(f"Worst year: 2021 ({min_corr:.3f})")

print(f"Statistically significant years: {significant_count}/{len(results)}")

print("")
print("KEY FINDINGS:")

if valid_correlations:
    avg_corr = np.mean(valid_correlations)
    
    if avg_corr > 0.3:
        print("- MODERATE predictive power: Draft projections show meaningful correlation")
    elif avg_corr > 0.1:
        print("- WEAK predictive power: Draft projections show limited correlation")  
    else:
        print("- MINIMAL predictive power: Draft projections show very weak correlation")
else:
    print("- Unable to calculate meaningful correlations")

print("- No years achieved statistical significance (p < 0.05)")
print("- Results vary considerably by year (-0.292 to +0.402 range)")
print("- Win percentage correlation is sometimes stronger than standing correlation")
print("- 2015 showed the strongest correlation (0.402)")
print("- 2021 showed the weakest correlation (-0.292)")

print("")
print("IMPLICATIONS:")
print("1. Draft projections have LIMITED predictive power for regular season success")
print("2. Other factors beyond player projections significantly influence team performance")
print("3. League competitiveness and parity may be reducing projection accuracy")
print("4. Strategy, roster management, and luck play important roles")
print("5. Projections may be more useful for player evaluation than team success prediction")

print("")
print("RECOMMENDATIONS:")
print("- Use projections as ONE factor among many in draft strategy")
print("- Focus on value identification rather than absolute team projection totals")
print("- Consider season-long roster management as equally important as draft")
print("- Investigate other factors that correlate with championship success")

print("")
print("Files generated:")
print("- simple_projection_correlation.png (visualization)")
print("- Analysis shows fantasy basketball success involves more than just player projections")