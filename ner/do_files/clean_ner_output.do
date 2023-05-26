*-----------------------------------------------------------------------------------*
///// This .do file cleans the output from running the NER inference file linked
///// at https://github.com/matthewleechen/ner_patents/blob/main/inference.ipynb.
*-----------------------------------------------------------------------------------*
///// To run this code, you require a working directory containing the NER output
///// and a subfolder of this directory called "ner_output" containing all outputted
///// .csv files from "inference.ipynb", patent quality data as .csv files.
*-----------------------------------------------------------------------------------* 
/// Dependencies:
/// ssc install egenmore
*-----------------------------------------------------------------------------------*
/// Change working directory 
*-----------------------------------------------------------------------------------*

clear all
cd "/path/to/directory" // set working directory here
set more off

*-----------------------------------------------------------------------------------*
/// Clean NER output files
*-----------------------------------------------------------------------------------*

****** Import and append NER output csv files

* Import files and drop empty obs
local list : dir ner_output files "*.csv"
foreach f of local list {
    qui: import delimited "ner_output/`f'", clear varnames(1)
	gen file_name = "`f'"
	qui: save "`f'.dta", replace
    local append `append' "`f'.dta"
}
clear
append using `append', force

* Delete intermediary .dta files from directory
local list : dir . files "*.csv.dta"
foreach f of local list {
    erase "`f'"
}

****** Clean file name variable
gen pos_start = strpos(file_name, "_")
gen pos_end = strrpos(file_name, "_")
replace file_name = substr(file_name, pos_start+ 1, pos_end- 7) // file name cleanly record the year for 1852-1871
drop pos_*

****** Clean patent dates

*** Clean date variable
egen cleaned_date = sieve(date), omit(#&.()-,)
replace date = cleaned_date
replace date = strtrim(date)
drop cleaned_date 

*** Create month variable 
gen month = 0
local months "jan feb mar apr may jun jul aug sep oct nov dec"
local m = 0
foreach x of local months {
    local ++m
    replace month = `m' if strpos(date, "`x'") > 0 & month == 0
}
replace month = . if month == 0 

*** Create year variable 
gen year = regexs(0) if(regexm(date, "[0-9][0-9][0-9][0-9]")) // Extract four-digit string as year

replace year = file_name if file_name != "1617_1852_vol1" & ///
file_name != "1617_1852_vol2" & file_name != "1852_oct-dec" // use cleaner file name as year variable if file name sufficient to know year
replace year = "1852" if file_name == "1852_oct-dec"

destring year, replace
drop file_name 

*** Generate day variable (1617-1868)
gen day = substr(date, 1, 1) if regexm(date, "[0-9](th|rd|st|nd)") & ///
year != 1869 & year != 1870 & year != 1871
replace day = substr(date, 1, 2) if regexm(date, "[0-9][0-9](th|rd|st|nd)") & ///
year != 1869 & year != 1870 & year != 1871

*** Generate day variable (1869-1871)
replace day = ustrregexs(0) if ustrregexm(date, " [0-9]{1,2} ") & ///
(year == 1869 | year == 1870 | year == 1871)

* Clean up days
egen clean_day = sieve(day), keep(n)
replace day = clean_day
drop clean_day
destring day, replace
replace day = . if day < 1 | day > 31

* Create numeric date variable
gen edate = mdy(month, day, year)
format edate %dM_d,_CY
drop date
rename edate date

****** Create communication indicator

* Create comm dummy
gen comm_indicator = 0
replace comm_indicator = 1 if strpos(comm, "com") > 0
drop comm
rename comm_indicator comm

****** Clean names

* Append continuations of names (based on ##)
forvalues i = 1/11 {
	qui replace per_`i' = per_`i' + substr(per_`=`i'+1', 3, .) if ///
	strpos(per_`=`i'+1', "##") == 1
}

* Append continuations of names (based on single words)
forvalues i = 1/11 {
	qui replace per_`=`i'+1' = "" if strpos(per_`=`i'+1', "##") == 1
	qui replace per_`i' = per_`i' + per_`=`i'+1' if strpos(per_`i', " ") == 0
}

* Remove substrings of other person variables
forvalues i = 1/12 {
	 forvalues j = 1/12 {
	 	if `i' != `j' {
			qui replace per_`i' = "" if ///
			strpos(ustrtrim(per_`j'), ustrtrim(per_`i')) > 0 
		} 
	} 
}

* Remove erroneous substrings
foreach var of varlist per_1-per_12 {
	qui replace `var' = subinstr(`var', ".", "", .)
	qui replace `var' = subinstr(`var', "#", "", .)
	qui replace `var' = subinstr(`var', ":", "", .)
	qui replace `var' = subinstr(`var', "westm", "", .)
	qui replace `var' = "" if length(`var') < 3
	qui replace `var' = "" if strpos(`var', " ") == 0
	qui replace `var' = "" if `var' == "h m"
}

* Ignore empty entries and shift dataset to left-most variables
qui gen byte imiss = .
forval  j = 1/12  {  
    forval i = 1/11 {
       qui replace imiss = missing(per_`i')
       local next = `i' + 1
       qui replace per_`i' = per_`next' if imiss
       qui replace per_`next' = "" if imiss
    }
}    
drop imiss
missings dropvars, force 

****** Clean patent numbers

egen cleaned_num = sieve(num), keep(n) // use sieve function from egenmore
replace num = cleaned_num 
drop cleaned_num 
destring num, replace

****** Encode info 

* Clean info
replace info = subinstr(info, "& ##", "",.)
replace info = subinstr(info, "##", "",.)
replace info = subinstr(info, "&", "",.)
replace info = subinstr(info, ".", "",.)

* Convert Roman-like numericals to numbers
replace info = subinstr(info, "xxj ", "21 ", .)
replace info = subinstr(info, "xx ", "21 ", .)
replace info = subinstr(info, "xj ", "11 ",.)
local replacements_num "xxtie xiiij xiiijteen xiiijen xiiiien xiiije xiii xiiin xiiiien xiiij"
foreach rep of local replacements_num {
    qui replace info = subinstr(info, "`rep'", "14 ", .)
}
replace info = strtrim(info)

* Create encode variable
gen enc_info = "14 years" if strpos(info, "14") > 0 | ///
strpos(info, "fourteen") > 0 | strpos(info, "four teen") > 0 | ///
strpos(info, "14 yrs") > 0 | strpos(info, "14e") > 0 | ///
strpos(info, "14 t") > 0 | info == "14" | strpos(info, "four  teen") > 0 | ///
strpos(info, "four een") > 0

replace enc_info = "12 years" if strpos(info, "twelve y") > 0 & enc_info == ""

replace enc_info = "21 years" if (strpos(info, "21 y") > 0 | info == "xx") ///
& enc_info == ""

replace enc_info = "6 months" if (strpos(info, "6 mo") > 0 | ///
strpos(info, "six m") > 0 | strpos(info, "ix m") > 0 | ///
strpos(info, "six c") > 0) & enc_info == ""

replace enc_info = "2 months" if (strpos(info, "2 mo") > 0 | ///
strpos(info, "two m") > 0 | info == "two" | strpos(info, "2 c") > 0 | ///
strpos(info, "two c") > 0) & enc_info == ""

replace enc_info = "4 months" if (strpos(info, "4 mo") > 0 | ///
strpos(info, "four m") > 0 | strpos(info, "4 c") > 0) & enc_info == ""

replace enc_info = "Stopped at fiat" if (strpos(info, "stopped") > 0 | ///
strpos(info, "fiat") > 0) & enc_info == ""

replace enc_info = "Provisional protection NOT granted" if ///
strpos(info, "not") > 0 & enc_info == ""

replace enc_info = "Letters patent sealed" if (strpos(info, "letter") > 0 | ///
strpos(info, "patent sealed") > 0) & enc_info == ""

replace enc_info = "Provisional protection only" if (strpos(info, "prov") > 0 | ///
strpos(info, "protec") > 0 | strpos(info, "on only") > 0) & enc_info == ""

replace info = subinstr(info, "mos", "months",.)
local replacements_yr "yeares year yeers yeeres yrs"
foreach rep of local replacements_yr {
    qui replace info = subinstr(info, "`rep'", "years", .)
}

replace enc_info = info if regexm(info, "[0-9] (months|years)") 
drop info 
rename enc_info info 

* Clean up
gen pos = strpos(info, regexs(0)) if regexm(info, "[0-9]") 
replace info = substr(info, pos, .) if pos > 1 & !missing(pos)
replace info = substr(info, 1, strpos(info, "s")) if pos == 1 & !missing(pos)
drop pos
replace info = itrim(strtrim(info))

****** Clean occupations

replace occ = subinstr(occ, " . -", "",.)
replace occ = subinstr(occ, "& -", "",.)
replace occ = subinstr(occ, ".", "",.)
replace occ = subinstr(occ, "-", "",.)
replace occ = subinstr(occ, "& .", "",.)
replace occ = subinstr(occ, "& ##", "",.)
replace occ = subinstr(occ, "#", "",.)
replace occ = subinstr(occ, char(34), "",.)
replace occ = "" if length(occ) == 1
replace occ = itrim(strtrim(occ))
replace occ = substr(occ, 1, strrpos(occ, "&")-1) if substr(occ,-1,1) == "&"

****** Clean locations 

replace loc = subinstr(loc, "& ##", "",.)
replace loc = subinstr(loc, "#", "",.)
replace loc = subinstr(loc, "-", "",.)
replace loc = subinstr(loc, ".", "",.)
replace loc = subinstr(loc, "", "",.)
replace loc = subinstr(loc, char(34), "",.)
replace loc = itrim(strtrim(loc))

