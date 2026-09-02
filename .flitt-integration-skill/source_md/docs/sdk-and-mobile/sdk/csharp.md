# C# SDK

C# SDK allows you to accept payment with Visa/MasterCard cards on your website.

Lates version of C# SDK you can always find in our public repository: 

[https://github.com/flittpayments/c-sharp-sdk](https://github.com/flittpayments/c-sharp-sdk)

# Step by step implementation case 

You will find all code examples by [link](https://github.com/flittpayments/c-sharp-sdk/tree/main/FlittSDKSamples)

- [create order](/api/create-order/#__tabbed_2_1) and obtain payment token:

    for this step you need ``` class Token ```

    if you are planing to use recurring payments in future, add parameter `recurring = 'y'` in request:
    
    ``` java 
    using FlittSDK;
    using FlittSDK.Checkout;
    
    Config.MerchantId = 1549901;
            Config.SecretKey = "test";
    
            var req = new TokenRequest {
                order_id = Guid.NewGuid().ToString("N"),
                amount = 100000,
                order_desc = "checkout json demo",
                currency = "GEL"
            };
            var resp = new Token().Post(req);
            if (resp.Error == null) {
                string token = resp.token;
            };
    ```

    in response you will receive payment token in parameter `resp.token`:
  
  - send payment token from `resp.token` to frontend. 

    You can choose 2 solutions for web payment form implementation on frontend: [Embedded iframe](/api/embedded-custom/) 
    or [JavaScript native](/sdk-and-mobile/sdk/js/) form both for cards and Apple/Google Pay

    For JavaScript native frontend form pass payment token to JavaScript payment form in dictionary

    ```  json hl_lines="3"
        {
         "payment_system":"card",
         "token": `resp.token`,
         "card_number":"16/19-digits number",
         "expiry_date":"Supported formats: MM/YY, MM/YYYY, MMYY, MMYYYY",
         "cvv2":"3-digits number"
         }
    ```

    For Embedded IFrame form pass payment token to payment form in `Options` object (see [example](/api/embedded-custom/#example-with-order-created-on-backend))
  
    ```  json hl_lines="15"
    var Options = {
      options: {
        methods: ['card'],
        methods_disabled: [],
        card_icons: ['mastercard', 'visa', 'maestro'],
        active_tab: 'card',
        fields: false,
        title: 'Demo checkout',
        link: 'https://shop.com',
        full_screen: true,
        button: true,
        email: true
      },
      params: {
        token: `resp.token`
      }
    }
    checkout("#checkout-container", Options);
    ``` 
  
    Solution for mobile application you can choose depending on programming language framework you application is developed:
  
- [Apple Pay](/api/applepay-getting-started/)
  
- [Google Pay](/api/googlepay-getting-started/)
  