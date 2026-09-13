----Query 1 — Top 10 Hospitals by Revenue
SELECT *
FROM vw_hospital_performance
LIMIT 10;

----Query 2 — Top Diseases
SELECT *
FROM vw_disease_distribution
LIMIT 10;


-----Query 3 — Top Doctors by Revenue
SELECT
doctor_name,
SUM(billing_amount) revenue
FROM fact_patients fp
JOIN dim_doctor dd USING(doctor_id)
GROUP BY doctor_name
ORDER BY revenue DESC
LIMIT 10;


------Query 4 — Monthly Revenue Growth
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS previous_month,
    ROUND(
        ((revenue - LAG(revenue) OVER (ORDER BY month))
        / NULLIF(LAG(revenue) OVER (ORDER BY month),0)) * 100,
        2
    ) AS growth_percent
FROM vw_revenue_trend;


------Query 5 — Highest Average Billing Disease
SELECT
medical_condition,
ROUND(AVG(billing_amount),2) avg_bill
FROM fact_patients
GROUP BY medical_condition
ORDER BY avg_bill DESC;

------Query 6 — Average Stay per Hospital
SELECT
hospital_name,
avg_stay
FROM vw_hospital_performance
ORDER BY avg_stay DESC;


-----Query 7 — Patient Segmentation
SELECT
CASE
WHEN billing_amount<20000 THEN 'Low Cost'
WHEN billing_amount<40000 THEN 'Medium Cost'
ELSE 'High Cost'
END spending_segment,
COUNT(*) patients
FROM fact_patients
GROUP BY spending_segment;


-----Query 8 — Hospital Ranking
SELECT
hospital_name,
patients,
RANK() OVER(ORDER BY patients DESC) hospital_rank
FROM vw_hospital_performance;


-----Query 9 — Doctor Ranking
SELECT
doctor_name,
patients_treated,
DENSE_RANK() OVER(
ORDER BY patients_treated DESC
) rank
FROM vw_doctor_performance;




------Query 10 — Revenue Contribution %
SELECT
hospital_name,
ROUND(
revenue/
SUM(revenue) OVER()*100,
2
) contribution_percent
FROM vw_hospital_performance;