cp /usr/local/apps/harvest-scheduler/run_scheduler.py.template schedule.py


drop table fvs_stands;

create index ix_fvaggregate_cond ON fvsaggregate (cond);
create index ix_fvaggregate_carbon ON fvsaggregate (total_stand_carbon);
create index ix_fvaggregate_standidyear ON fvsaggregate (cond, year);

create table fvs_stands as 
	select  
		total_stand_carbon * acres as carbon,
		removed_merch_bdft * acres / 1000.0 as timber,
		NSONEST * acres as owl,
		removed_merch_bdft * slope * acres / 1000.0 as cost, -- mbf-slope-acres? wierd unit but OK as proxy
	    year,
	    standid,
        fvs.rx as rx,
        "offset",
	    climate,
	    acres
	from fvsaggregate fvs
	join stands as s
	on s.standid = fvs.cond
	WHERE fvs.total_stand_carbon is not null -- should remove any blanks
	ORDER BY cond, year; 

-- add indexes for year and climate
create index ix_fvs_stands_rxoff ON fvs_stands (rx, "offset");
create index ix_fvs_stands_all ON fvs_stands (standid, rx, "offset", climate);


-- scheduler.prep_data will loop through all mgmts, stands and run this query
select year, carbon, timber, owl, cost 
from fvs_stands
WHERE standid = 26139
and rx = 5
and "offset" = 10  --'rx5,offset10'
and climate = 'Ensemble-rcp60'; -- original table MUST be ordered by standid, year
