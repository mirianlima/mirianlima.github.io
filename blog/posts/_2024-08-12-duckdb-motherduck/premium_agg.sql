-- Step 1: Create the `c_age1` table by loading the CSV data
CREATE TABLE c_age1 AS 
SELECT * 
FROM read_csv_auto('/Users/mlima/Code/mirianlima.github.io/blog/posts/2024-08-12-duckdb-motherduck/data/c_age1.csv');

-- Step 2: Create the `c_dem` table by loading the CSV data
CREATE TABLE c_dem AS 
SELECT * 
FROM read_csv_auto('/Users/mlima/Code/mirianlima.github.io/blog/posts/2024-08-12-duckdb-motherduck/data/c_dem.csv');

-- Step 3: Filter, group, and aggregate the `c_age1` data
CREATE TEMP TABLE filtered_age_data AS 
SELECT 
    "iso3_code", 
    "time", 
    CASE 
        WHEN "age_labor" = 'Younger Prime-age Workers (25-34)' THEN 'prime_younger'
        WHEN "age_labor" = 'Older Prime-age Workers (35-54)' THEN 'prime_older'
    END AS age_labor_group,
    SUM("pop_total") AS total_population
FROM 
    c_age1
WHERE 
    "age_labor" IN ('Younger Prime-age Workers (25-34)', 'Older Prime-age Workers (35-54)')
GROUP BY 
    "iso3_code", 
    "time", 
    age_labor_group;

-- Step 4: Pivoting the data to create wide format
CREATE TEMP TABLE pivoted_age_data AS 
SELECT 
    "iso3_code", 
    "time",
    SUM(CASE WHEN age_labor_group = 'prime_younger' THEN total_population ELSE 0 END) AS prime_younger,
    SUM(CASE WHEN age_labor_group = 'prime_older' THEN total_population ELSE 0 END) AS prime_older
FROM 
    filtered_age_data
GROUP BY 
    "iso3_code", 
    "time";

-- Step 5: Merging and saving the pivoted data with `c_dem` using `iso3_code` and `time` into a CSV
COPY (
    SELECT 
        p."iso3_code",
        p."time",
        p.prime_younger,
        p.prime_older,
        d.*
    FROM 
        pivoted_age_data p
    INNER JOIN 
        c_dem d
    ON 
        p."iso3_code" = d."iso3_code" AND
        p."time" = d."time"
) 
TO '/Users/mlima/Code/mirianlima.github.io/blog/posts/2024-08-12-duckdb-motherduck/data/c_dem_premium.csv' 
WITH (HEADER, DELIMITER ',');
