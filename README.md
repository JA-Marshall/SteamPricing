# SteamPricing
Various scripts/functions i used in older project for pricing steam market data accurately. 


-  fetchsaleedata
returns a tuple of the last 30 days of sales data of a given steam item. Attempts to removie pricing anomalies from the data using a hampel filter green, red = original data, green = sanitized. 

![image](https://github.com/JA-Marshall/SteamPricing/assets/9871373/b5fc75c4-6a23-40d2-af8f-e2e873dd13f0)
