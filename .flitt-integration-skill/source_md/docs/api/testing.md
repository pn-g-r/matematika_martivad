## Test merchant data

| Parameter                            | Value                                                      |
|--------------------------------------|------------------------------------------------------------|
| merchant_id                          | 1549901                                                    |
| test secret key for purchases | test                                                       |
| test secret key for payouts  | testcredit                                                 |
| currency                             | See full list of [supported currencies](/api/currencies/). |


## Test payment data

!!! note "Testing with cards"
    
    | Card number         | Brand      | Expiry date | CVV2 | 3DSecure                                | Response type |
    |---------------------|------------|-------------|------|-----------------------------------------|---------------|
    | `4444555566661111`  | Visa       | any         | any  | yes                                     | approve       |
    | `4444111166665555`  | Visa       | any         | any  | yes                                     | decline       |
    | `4444555511116666`  | Visa       | any         | any  | no                                      | approve       |
    | `4444111155556666`  | Visa       | any         | any  | no                                      | decline       |
    | `5555666644441111`  | MasterCard | any         | any  | yes                                     | approve       |
    | `6666444455551111`  | MasterCard | any         | any  | yes                                     | approve       |
    | `4444555566669999`  | Visa       | any         | any  | yes, frictionless                       | approve       |
    | `4444666655559999`  | Visa       | any         | any  | yes, challenge                          | approve       |
    | `4444999966665555`  | Visa       | any         | any  | yes, frictionless                       | decline       |
    | `4444666699995555`  | Visa       | any         | any  | yes, challenge                          | decline       |
    | `2222555566663333`  | MasterCard | any         | any  | yes                                     | decline       |
    | `4444777799991111`  | Visa       | any         | any  | managed by `reservation_data` parameter | approve       |
    | `9860010099998881`  | Humo       | any         | any  | yes                                     | approve      |
    | `8600202020202023`  | UzCard     | any         | any  | yes                                     | approve       |
    | `9860010088889992`  | Humo       | any         | any  | OTP = 111111                            | approve      |
    | `8600202020202023`  | UzCard     | any         | any  | OTP = 111111                            | approve       |


## Testing Apple Pay on web

!!! note "Testing Apple Pay on web"

    If your merchant is in test mode, Flitt will automaticaly convert any real wallet tokenized card into test token.

    You just need to make a test payment and use your real Apple wallet card.

## Testing Apple Pay in app

!!! note "Testing Apple Pay in app"

    Please refer to [Apple Pay sandbox instruction](https://developer.apple.com/apple-pay/sandbox-testing/)

    1. Register in Apple Pay developer account. You will need to make enrollment and pay $99.
    2. Register a Merchant ID in your developer account.
    3. Create your Payment Processing Certificate.
    4. Create your Merchant Identity Certificate.
    5. Upload your certificates in Flitt Merchant Portal in Merchant settings->>Payment methods->>Apple
    6. Sign in to App Store Connect.
    7. On the homepage, click Users and Access.
    8. Under Sandbox, click Testers.
    9. Click “+” to set up your tester accounts.
    10. Complete the tester information form and click Invite.
    11. Sign out of your Apple Account on all testing devices and sign back in with your new sandbox tester account. 
    12. Add test card to your Apple wallet:
        ```        
        4761 1200 1000 0492
        01/27
        CVV: 480
        ```
    13. Wait will card will be added to your wallet as Visa Test Card
    14. Test payment with Visa Test Card

## Testing Open Banking

!!! note "Testing with Open Banking"

    |Parameter|Value|Comment|
    |----|----|---|
    |payment_method|x| Testing is possible only with Demo Bank|


    To test Open Banking, create payment with parameter `payment_method = x` or click Demo Bank icon on checkout page.


    [![Open Banking Checkout page]][Open Banking Checkout page]{ width="300px" align="left" }
      
      [Open Banking Checkout page]: /static/img/opb3.jpg
