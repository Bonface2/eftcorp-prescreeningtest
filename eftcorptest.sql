-- These SQL statements query a dummy table, eftcorptest_dummydata, from MySQL database (Using MySQL Dialect)

-- Top 5 banks by transaction volume in the last 7 days

SELECT TOP 5 bankid
FROM eftcorptest_dummydata
WHERE DATEDIFF(DAY, timestamp, GETDATE()) <= 7
ORDER BY amount DESC;



-- Average transaction value per customer for a given month, where customer = bank

SELECT 
    bankid,
    MONTHNAME(`timestamp`) AS txn_month,
    AVG(amount) AS avg_amount
FROM eftcorptest_dummydata
GROUP BY 
    bankid, 
    MONTHNAME(`timestamp`)
