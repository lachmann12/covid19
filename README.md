## Correcting under-reported COVID-19 case numbers: estimating the true scale of the pandemic

The COVID-19 virus has spread worldwide in a matter of a few months, while healthcare systems struggle to monitor and report current cases. Testing results have struggled with the relative capabilities, testing policies and preparedness of each affected country, making their comparison a non-trivial task. Since severe cases, which more likely lead to fatal outcomes, are detected at a higher rate than mild cases, the reported virus mortality is likely inflated in most countries. Lockdowns and changes in human behavior modulate the underlying growth rate of the virus. Under-sampling of infection cases may lead to the under-estimation of total cases, resulting in systematic mortality estimation biases.

For healthcare systems worldwide it is important to know the expected number of cases that will need treatment. In this manuscript, we propose a method to correct the reported COVID-19 cases and death numbers by using a benchmark country (South Korea) with near-optimal testing coverage, with considerations on population demographics. We propose a method to extrapolate expected deaths and hospitalizations with respect to observations in countries that passed the exponential growth curve. By applying our correction, we predict that the number of cases is highly under-reported in most countries and a significant burden on worldwide hospital capacity. 

### Predicting COVID-19 cases from death rates

This code uses reported deaths for a given country and extrapolates expected deaths using known growth rate dynamics from other countries. The average time of death after infection is estimated to be 23 days. Deaths reported today mean that this number of people got infected with COVID-19 23 days ago. The algorithm uses the case fatality rate (CFR) to predict the actual cases. This number will be more accurate than the confirmed cases as they are in most countries under-reported by an order of magnitude.

A full description of the method can currently be found here:
https://www.medrxiv.org/content/10.1101/2020.03.14.20036178v2.article-metrics

A version of an executable python notebook is available on Kaggle:
https://www.kaggle.com/lachmann12/predict-exponential

There is a live API for direct programmatic access to predictions. The API returns JSON documents. 

### List all countries for which predictions are available
http://34.226.139.235/listcountries

### Return information for the specified country
http://34.226.139.235/country?name=Italy

### Predicting behavioral change in COVID-19 infected populations

In order to accurately estimate the response of a population to the virus we combine information from China, Italy, and Iran. These three countries underwent through significant lockdowns which affect the growth rate to decay over time. 

![Image description](https://github.com/lachmann12/covid19/blob/master/images/spline.png)

The image above highlights the estimated growth rate progression after significant counter measures are taken to control the virus spread.

### Current cases and predictions 

The current reported cases are shown in the plot below. For China, which successfully controlled the spread of the COVID-19 outbreak, the reported number of cases is 80,000 and about 3,000 fatalities.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/current_cases_fig1.png)

Estimates derived from reported death rates indicate significanlty higher case numbers. The predicted deaths are shown below. The algorithm can also be used to predict the hospitalizations at future time points. The actual numbers will vary on death to hospitalization ratio. This method currently only calculates the new expected number of hospitalizations per day that will end in a fatality. The actual number of hospitalizations will be much higher than this predicted number.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/country_predictions.png)


### Refinements and implementation details

The algorithm uses an estimated death rate observed in South Korea. The CFR is currently reported to be 1.5%. Other countries report significanlty variable CFRs over time. This is most likely due to the under-reporting of cases caused by unavailable testing capacity. The picture below is already slightly outdated. The CFR in South Korea increased since. This is most likely due to long disease progressions ending fatally outnumber new cases.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/country_compare.png)

The algorithm relies on a benchmark country from which important parameters are derived. These parameters are the overall CFR (1.5%) and the relative risk per age group. South Korea reported variing CFRs with significantly higher risk in age groups older than 60.

The algorithm uses demographic information to calculate a Vulnerability Factor (VF). It compares the relative suseptability of a country to COVID-19 compared to the South Korean population. Below is a comparison of three countries to South Korea. A country such as Italy, with a much older population than South Korea has a VF of 1.57. They are likely to have a significantly higher death rate. The US is comparable to South Korea with similar age structure. China has a much younger population, which should result in a much lower CFR.

![Image description](https://github.com/lachmann12/covid19/blob/master/images/country_pop.png)

### Comments

This is for scientific purposes only. The error bars on the predictions are very large and can be off by a large amount. There is significant limitations and assumptions that had to be made which will make the predictions deviate from the true progression. The main driving force is the exponential growth of infected individuals. At a doubling rate every 3 days the model is volatile to small changes in parameters used. This method tries to make few assumptions and the predicted decay of growth rate only requires 2 parameters and seems to fit observations well. As more information becomes available the predictions should become more accurate.

### Limitations

Limitations This method makes a series of assumptions in order to adjust reported COVID-19 cases compared with the benchmark country (South Korea). As the pandemic is still evolving, many parameters are not sufficiently known.
 
• Deaths are confirmed: It is assumed that if a death occurs due to COVID-19, the case will be confirmed. When there is under-reporting, the reported CFR would be lower than the true CFR.
 
• The population is infected uniformly We assume that the probability of infection is uniformly distributed across all age groups. The probability of an 80-year-old person to become infected is equal to the probability of a 30-year-old to become infected.
 
• Changes in healthcare load are not modeled The provided healthcare in countries is comparable. For developed countries such as Italy and South Korea, it is assumed that the population has similar access to treatment. The death rates reported by age group are thus applicable in all countries.

• The virus is identical in all countries This is supported by the very low mutational rate of SARS-CoV-2, which allows conjecturing identical etiologies across countries (PMID 32027036).

• Conservative modeling Our method relies on estimating future cumulative deaths for a period of at least 23 days. In most countries in this study there has been no observed change in growth rate up to the day of writing. The model assumes that the growth rate will start falling on the next day and follow our precomputed spline.

### Authors
Kathleen M. Jagodnik, Forest Ray, Federico M. Giorgi, Alexander Lachmann
