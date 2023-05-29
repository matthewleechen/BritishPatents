*-----------------------------------------------------------------------------------*
///// This .do file links the patents from "cleaned_ner_output.dta" with the patent
///// quality and industry classes data from Nuvolari, Tartari & Tranchero (2021),
///// available at: https://www.openicpsr.org/openicpsr/project/142801/version/V1/view.
///// Their paper is available at: 
///// https://www.sciencedirect.com/science/article/pii/S0014498321000413#sec0014
*-----------------------------------------------------------------------------------*

* Set working directory
clear all
cd "/Users/matthewleechen/Documents/patent_characteristics" // set working directory here; make sure the cleaned NER output file "cleaned_ner_output.dta" is in the directory.
set more off

* Create .dta file for 1700-1850

use "cleaned_ner_output.dta"
drop if year < 1700 | year > 1850 
keep num misc 
drop if num == .
save "ner_output_1700-1850.dta", replace

import excel "Patent_Quality_England_1700_1850.xlsx", ///
sheet("Patent Quality Indicators") firstrow clear
rename Patentnumebr num
keep num Industry
save "industries_1700-1850.dta", replace

* Exact match on numbers
merge m:m num using "ner_output_1700-1850.dta" // only patents that can be exactly matched on their numbers will be used as the labelled data
keep if _merge == 3
drop _merge
drop if misc == ""
rename misc text

* Output excel file as labelled data
export excel using "labelled_data_patents.xlsx", firstrow(variables) replace
erase "ner_output_1700-1850.dta"



