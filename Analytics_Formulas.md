# Analytics Calculations 

## MTBF (Mean Time Between Failures)
Average time between the start of consecutive failure periods
(Health Score < 50), measured in seconds.

## MTTR (Mean Time To Repair)
Average duration of each failure period — from when Health Score
drops below 50 until it recovers above 50 — measured in seconds.

## RUL (Remaining Useful Life)
Linear extrapolation of the last 10 health-score readings' decline
rate, estimating minutes remaining until Health Score reaches 50.

## Output Topics
- MTBF/MTTR: nti_smartfactory_teamX/analytics/reliability
- RUL: nti_smartfactory_teamX/analytics/rul
