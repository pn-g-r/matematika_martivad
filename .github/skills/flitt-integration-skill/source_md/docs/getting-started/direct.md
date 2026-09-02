<strong>Direct</strong> integration type allows to accept payments with card data collected on your site and passed to Flitt API. 

Direct integration will require from merchant the PCIDSS [SAQ D](/pcidss-compliance/#saq-d-requested-by-flitt) compliance.

How it works:

- A merchant website or mobile application creates the payment form with card number, cvv2 and expiry date fields and collects card data
- A merchant website or mobile application sends card data to merchant backend API
- Merchant backend stores and transits or only transmits without storage the card data to Flitt API (step 1)
- If card is enrolled in 3D-Secure, Flitt API returns to the merchant URL and the data which need to be submitted for 3DS-Secure cardholder authentication
- Merchant backend transmit 3D-Secure data to its website or mobile application with instruction to redirect customer to his bank's 3D-Secure authentication page
- Merchant backend application receives 3D-Secure authentication result and transmits it to Flitt API  (step 2)
- Merchant backend receives callback with payment final result

Refer to API description on how to procceed with direct integration:

- [Parameters](/api/order-parameters-direct/) required to be passed to Flitt API endpoint
- Endpoints to [create order](/api/create-order-direct/) and proceed with 3D-Secure authentication
