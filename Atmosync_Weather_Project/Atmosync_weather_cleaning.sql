--DataBase Name
create Database weather_Analytics
--use DataBase weather_Analytics
--directly import the Dataset through Flat files in ssms

select * from atmosync_weather_raw

--count the rows 
select count(*) as raw_rows from  atmosync_weather_raw

--location wise count and order by location 
select  location, count(*) as rows_per_location,min(time) as first_time,max(time) as last_time
from atmosync_weather_raw 
group by location
order by  location;

---missing value count by weather metric --(nullif can't work because column data types are in float )
select 
  sum(case when  precipitation is null then 1 else 0 end) as precipitation_blank,
  sum(case when wind_speed_10m is null then 1 else 0 end) as wind_speed_blank,
  sum(case when apparent_temperature is null then 1 else 0 end) as apparent_temperature_blank,
  sum(case when cloud_cover is null then 1 else 0 end) as cloud_cover_blank,
  sum(case when pressure_msl is null then 1 else 0 end) as pressure_blank
from atmosync_weather_raw;

--Duplicate weather records by time and location 
select time, location,count(*) AS copies
from atmosync_weather_raw 
group by time, location 
having count(*) > 1;

--Rebuild the cleaned weather table while preserving the datetime value
BEGIN TRANSACTION;

DROP VIEW IF EXISTS weather_analysis;
DROP TABLE IF EXISTS weather_clean;

select 
  time,
  temperature_2m,
  relative_humidity_2m,
  precipitation,
  wind_speed_10m,
  apparent_temperature,
  cloud_cover,
  pressure_msl,
  nullif(trim(location), '') as location,
  requested_latitude,
  requested_longitude,
  grid_latitude,
  grid_longitude
into weather_clean
from atmosync_weather_raw;

COMMIT TRANSACTION;

--select * from weather_clean

--The five all-empty fields or columns remain available as NULL columns in weather_clean

create view weather_analysis as
select time, temperature_2m, relative_humidity_2m, location,
       requested_latitude, requested_longitude, grid_latitude, grid_longitude
FROM weather_clean;


select * from weather_analysis

--Retrieve cleaned weather analysis data using a CTE

with weather_analysis AS (
  select
    time,
    temperature_2m,
    relative_humidity_2m,
    location,
    requested_latitude,
    requested_longitude,
    grid_latitude,
    grid_longitude
  from weather_clean

)
SELECT *
FROM weather_analysis;

--
CREATE OR ALTER VIEW weather_analysis AS
SELECT
  [time],
  temperature_2m,
  relative_humidity_2m,
  location,
  requested_latitude,
  requested_longitude,
  grid_latitude,
  grid_longitude
FROM weather_clean;

select * from weather_analysis

--Validate row counts, required fields
SELECT COUNT(*) AS clean_rows,
       COUNT(DISTINCT time || '|' || location) AS distinct_location_hours,
       SUM(CASE WHEN time IS NULL OR location IS NULL
                     OR temperature_2m IS NULL OR relative_humidity_2m IS NULL
                THEN 1 ELSE 0 END) AS rows_missing_required_values,
       SUM(CASE WHEN time IS NULL THEN 1 ELSE 0 END) AS invalid_times
FROM weather_clean;


--Export weather_analysis as atmosync_weather_clean.csv
SELECT * FROM weather_analysis ORDER BY time, location;