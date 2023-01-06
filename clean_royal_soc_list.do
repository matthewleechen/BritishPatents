*** Cleans the list of Royal Society members processed in Tabula ***

* Files were split into 30-page documents for loading into Tabula
* Tabula output was saved as .csv files with names corresponding to page numbers from the original pdf
* Tabula output was manually corrected in several cases with cross reference to the original pdf


* Import *csv files and append into Stata
cd "/Users/matthewleechen/Documents/learned_societies"
local list : dir "/Users/matthewleechen/Documents/learned_societies" files "*.csv"
foreach f of local list {
    import delimited "`f'", clear
	save "`f'.dta", replace
    local append `append' "`f'.dta"
}
clear
append using `append'


* Drop duplicates: there are 2 duplicates, both have been cross-referenced with the original pdf
* They both appear as duplicates in the original pdf in error
duplicates drop

* Rename default variables
rename v1 name_years
rename v2 fellow_type
rename v3 election_date



*** Clean fellow_type

* Drop foreign members and fellows not appointed for scientific reasons
keep if fellow_type == "Fellow" | fellow_type == "Founder Fellow" | ///
fellow_type == "Original Fellow"



*** Clean election_date

* Resolve uncertainty about election date by using chronologically earliest 
* and add extra variable to encode info on disputes
gen date_info = "dispute: " + substr(election_date, strpos(election_date, "or") + 3, .) ///
if strpos(election_date, "or") > 0
replace election_date = substr(election_date, 1, strpos(election_date, "or") - 1) ///
if strpos(election_date, "or") > 0

replace date_info = date_info + "dispute: " + substr(election_date, strpos(election_date, ";") + 1,.) ///
if strpos(election_date, ";") > 0
replace election_date = substr(election_date, 1, strpos(election_date, "(") - 1) ///
if strpos(election_date, ";") > 0

* Resolve twice elected individuals
replace date_info = date_info + "elected 2nd time: " + ///
substr(election_date, strpos(election_date, "and") + 4, .) if strpos(election_date, "and") > 0
replace election_date = substr(election_date, 1, strpos(election_date, "and") - 1) ///
if strpos(election_date, "and") > 0

* Split election_date into election year, month and day
gen stata_date = date(election_date, "DMY")
gen year_elected = year(stata_date)
gen month_elected = month(stata_date)
gen day_elected = day(stata_date)
drop stata_date election_date



*** Clean name_years

* Extract years active
gen years_active = substr(name_years, strpos(name_years, "(") + 1, strpos(name_years, ")") - strpos(name_years, "(") - 1)
gen before = substr(name_years, 1, strpos(name_years, "(") - 1)
gen after = substr(name_years, strpos(name_years, ")") + 1, .)
gen new_string = before + after
drop new_string before after
* Note that if the years_active variable is empty, the individual was alive as of 2019 

* Split years_active
split years_active, parse(-)
rename years_active1 birth_year
rename years_active2 death_year

* Split name_years
split name_years, parse(;) 

* Clean up name_years by deleting redundant information
replace name_years1 = substr(name_years1, 1, strpos(name_years, "(") - 1) ///
if strpos(name_years1, "(") > 0
rename name_years1 surname

* Extract "Sir" or "Dame" information
gen sir_dame = 1 if strpos(name_years2, "Sir") > 0 
replace sir_dame = 1 if strpos(name_years2, "Dame") > 0 

* Extract forenames
replace name_years2 = name_years3 if strpos(name_years2, "Sir") > 0
replace name_years3 = "" if name_years2 == name_years3
replace name_years2 = substr(name_years2, 1, strpos(name_years2, "(") - 1) ///
if strpos(name_years2, "(") > 0
rename name_years2 forenames

* Extract extra information
gen extra_info = name_years3 + " " + name_years4
drop name_years3 name_years4

* Tidy up
replace forenames = extra_info if strpos(forenames, "Dame") > 0
replace extra_info = "" if extra_info == forenames
replace extra_info = "" if strpos(extra_info, "Sir") > 0
replace extra_info = "" if strpos(extra_info, "Dame") > 0
replace forenames = extra_info if strpos(extra_info, "(") > 0
replace forenames = substr(forenames, 1, strpos(forenames, "(") - 1) ///
if strpos(forenames, "(") > 0
replace extra_info = "" if strpos(extra_info, "(") > 0

* Generate id variable
sort surname
gen id = _n
order id name_years surname forenames years_active birth_year death_year

* Save and finish
save "/Users/matthewleechen/Documents/learned_societies/cleaned_rsfellows.dta", replace
clear all


