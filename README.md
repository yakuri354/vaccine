## Moscow QR code bypass
In June 2021 the Moscow government announced that all restaurants and food-courts are only allowed to serve citizens with QR codes, 
which the government handed out to citizens who had vaccinated against COVID-19 or submitted a negative PCR test result.  
There were 5 apps for checking the validity of the QR codes.  
These apps employed basic URL host checks which could be easily mitigated by using a malformed URL.  
### The code in this repo achieves successful CSRF on 3 of 5 apps in the list.
