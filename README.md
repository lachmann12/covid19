## Correcting under-reported COVID-19 case numbers: estimating the true scale of the pandemic

The COVID-19 virus has spread worldwide in a matter of a few months, while healthcare systems struggle to monitor and report current cases. Testing results have struggled with the relative capabilities, testing policies and preparedness of each affected country, making their comparison a non-trivial task. Since severe cases, which more likely lead to fatal outcomes, are detected at a higher rate than mild cases, the reported virus mortality is likely inflated in most countries. Lockdowns and changes in human behavior modulate the underlying growth rate of the virus. Under-sampling of infection cases may lead to the under-estimation of total cases, resulting in systematic mortality estimation biases.

For healthcare systems worldwide it is important to know the expected number of cases that will need treatment. In this manuscript, we propose a method to correct the reported COVID-19 cases and death numbers by using a benchmark country (South Korea) with near-optimal testing coverage, with considerations on population demographics. We propose a method to extrapolate expected deaths and hospitalizations with respect to observations in countries that passed the exponential growth curve. By applying our correction, we predict that the number of cases is highly under-reported in most countries and a significant burden on worldwide hospital capacity. 

### Predicting COVID-19 cases from death rates

This code uses reported deaths for a given country and extrapolates expected deaths using known growth rate dynamics from other countries. The average time of death after infection is estimated to be 23 days. Deaths reported today mean that this number of people got infected with COVID-19 23 days ago. The algorithm uses the case fatality rate (CFR) to predict the actual cases. This number will be more accurate than the confirmed cases as they are in most countries under-reported by an order of magnitude.

A full description of the method can currently be found here:
https://figshare.com/s/758084c4fc684ee18a8f

### Predicting behavioral change in COVID-19 infected populations

In order to accurately estimate the response of a population to the virus we combine information from China, Italy, and Iran. These three countries underwent through significant lockdowns which affect the growth rate to decay over time. 

![Image description](https://github.com/lachmann12/covid19/blob/master/images/spline.png)

The image above highlights the estimated growth rate progression after significant counter measures are taken to control the virus spread.

### Current cases and predictions 

The current reported cases are shown in the plot below. For China, which successfully controlled the spread of the COVID-19 outbreak, the reported number of cases is 80,000 and about 3,000 fatalities.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/current_cases_fig1.png)

Estimates derived from reported death rates indicat significanlty higher case numbers. The predicted deaths are shown below.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/predictions_fig4.png)


### Refinements and implementation details

The algorithm uses an estimated death rate observed in South Korea. The CFR is currently reported to be 1.5%. Other countries report significanlty variable CFRs over time. This is most likely due to the under-reporting of cases caused by unavailable testing capacity.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/country_compare.png)

The algorithm relies on a benchmark country from which important parameters are derived. These parameters are the overall CFR (1.5%) and the relative risk per age group. South Korea reported variing CFRs with significantly higher risk in age groups older than 60.
