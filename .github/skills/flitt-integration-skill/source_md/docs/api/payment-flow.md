## Interaction scheme A (with customer redirection to payment page)

``` mermaid
sequenceDiagram
  Customer->>Merchant: 1. Customer populates shopping cart
  Merchant-->>Customer: 2. Merchant creates HTML form with order details
  Customer->>Merchant: 3. Customer submits payment form
  Merchant->>Flitt: 4. Merchant creates order and <br/>redirects customer to Flitt hosted page
  Flitt-->>Customer: 5. Flitt displays payment page to Customer
  Customer->>Flitt: 6. Customer provides payment details
  Flitt->>Customer`s PI: 7. Flitt checks if 3DSecure or SCA required 
  loop 3DSecure/SCA
    Customer`s PI-->>Customer`s PI: 8. Customer is authenticated if required <br/>by his payment institution
  end
  Customer`s PI->>Flitt: 9. Customer's PI returns authentication result  
  Flitt->>Customer`s PI: 10. Flitt initiates the charge by sending payment request to customer's PI
  Customer`s PI->>Flitt: 11. Customer's PI returns payment result to Flitt
  Flitt-->>Merchant: 12. Flitt redirects customer back to Merchant <br/>with order status  
  Merchant-->>Customer: 13. Merchants shows result page to customer with order status
  Flitt-->>Merchant: 14. Flitt sends server-to-server callback <br/>to Merchant with order status   
```

1. Customer chooses products or services in merchant online shop or mobile app and adds them to his cart.
2. Merchant creates HTML form with [request parameters](/api/create-order/) to be submitted to Flitt.
3. At merchant site customer submits HTML form in browser or mobile application.
4. Merchant redirects customer in browser to Flitt url https://pay.flitt.com/api/checkout/redirect/, sending parameters with HTTPS POST method.
5. Flitt creates order and renders hosted payment page with all available methods.
6. Customer provides payment details at payment page on Flitt site.
7. Flitt checks if strong customer authentication is requires.
8. Flitt redirects customer to his payment institution for authentication (3DSecure/password/OTP) via browser.
9. Payment institution returns customer back to Flitt with authentication result.
10. Flitt initiates payment by sending request to customer payment institution (PI).
11. Customer's payment institution returns payment result to Flitt.
12. Flitt redirects customer to merchant site by sending payment result using HTTPS POST or GET. 
13. Merchant shows result page with payment details. 
14. To ensure that merchant received response with payment details, Flitt also sends callback with payment result
parameters to merchant site using host-to-host HTTPS POST.

## Interaction scheme B (with preliminary host-to-host request to get payment page URL)

``` mermaid
sequenceDiagram
  Customer->>Merchant: 1. Customer populates shopping cart
  Merchant-->>Flitt: 2. Merchant submits JSON request to Flitt url https://pay.flitt.com/api/checkout/url/.
  Flitt->>Merchant: 3. Flitt returns to merchant `checkout_url` parameter
  Merchant->>Customer: 4. Merchant creates order and <br/>redirects customer to Flitt hosted page
  Flitt-->>Customer: 5. Flitt displays payment page to Customer
  Customer->>Flitt: 6. Customer provides payment details
  Flitt->>Customer`s PI: 7. Flitt checks if 3DSecure or SCA required 
  loop 3DSecure/SCA
    Customer`s PI-->>Customer`s PI: 8. Customer is authenticated if required <br/>by his payment institution
  end
  Customer`s PI->>Flitt: 9. Customer's PI returns authentication result  
  Flitt->>Customer`s PI: 10. Flitt initiates the charge by sending payment request to customer's PI
  Customer`s PI->>Flitt: 11. Customer's PI returns payment result to Flitt
  Flitt-->>Merchant: 12. Flitt redirects customer back to Merchant <br/>with order status  
  Merchant-->>Customer: 13. Merchants shows result page to customer with order status
  Flitt-->>Merchant: 14. Flitt sends server-to-server callback <br/>to Merchant with order status   
```

1. Customer chooses products or services in merchant online shop or mobile app and adds them to his cart.
2. Merchant creates JSON request with [request parameters](/api/create-order/) and submit it host-to-host to Flitt url https://pay.flitt.com/api/checkout/url/.
3. Flitt returns to merchant [interim response](/api/create-order/#__tabbed_1_2) with `checkout_url` parameter with URL were customer should be redirected to provide payment details.
4. Merchant redirect customer to Flitt hosted payment page with all available methods.
5. Customer provides payment details at payment page on Flitt site.
7. Flitt checks if strong customer authentication is requires.
8. Flitt redirects customer to his payment institution for authentication (3DSecure/password/OTP) via browser.
9. Payment institution returns customer back to Flitt with authentication result.
10. Flitt initiates payment by sending request to customer payment institution (PI).
11. Customer's payment institution returns payment result to Flitt.
12. Flitt redirects customer to merchant site by sending payment result using HTTPS POST or GET. 
13. Merchant shows result page with payment details. 
14. To ensure that merchant received response with payment details, Flitt also sends callback with payment result
parameters to merchant site using host-to-host HTTPS POST.