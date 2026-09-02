# Create order

Create order - it actually were most of the integrations start off.

*Endpoints for order creation*

## Flitt hosted checkout page with checkout url
<div class="grid" markdown style="width:100%">

!!! note "Flitt hosted checkout page with checkout url"

    `POST /api/checkout/url`

    This endpoint expects `POST` request in `JSON` format with [parameters](/api/order-parameters/#__tabbed_1_1).

    Normal response will contain `checkout_url` parameter - the URL of checkout page where payer should be redirected.

!!! note "Request and response examples"

    === "Request"
    
        ``` sh  
        curl -i -X POST \
        -H "Content-Type:application/json" \
        -d \
        '{
        "request": {
        "server_callback_url": "http://myshop/callback/",
        "order_id": "TestOrder2",
        "currency": "GEL",
        "merchant_id": 1549901,
        "order_desc": "Test payment",
        "amount": 1000,
        "signature": "91ea7da493a8367410fe3d7f877fb5e0ed666490"
        }
        }' \
        'https://pay.flitt.com/api/checkout/url'
        ```


    === "Normal response"
    
        ``` json
        {
            "response":{
                "response_status":"success",
                "checkout_url":"https://pay.flitt.com/merchants/5ad6b888f4becb0c33d543d54e57d86c/default/index.html?token=8a09f9d937f43ad6fb40d6b40282d7277a48582a"
            }
        }
        ```

    === "Response in case of error"
      
        ``` json
        {
            "response":{
                "response_status":"failure",
                "error_message":"Parameter `amount` is mandatory",
                "error_code":"1008"
            }
        }
        ```
</div>

## Merchant embedded checkout page with payment token

This endpoint is preferred to be used for mobile application which process: 

- [Apple Pay](/api/applepay-getting-started/)
- [Google Pay](/api/googlepay-getting-started/)
- [Mobile card form](/sdk-and-mobile/sdk/about-sdk/) 
- [JavaScript SDK](/sdk-and-mobile/sdk/js/)  


<div class="grid" markdown style="width:100%">

!!! note "Merchant embedded checkout page with payment token"

    `POST /api/checkout/token`

    This endpoint expects `POST` request in `JSON` format with [parameters](/api/order-parameters/#__tabbed_1_1) similar to `#!urlencoded /api/checkout/url/` endpoint.

    The difference is that normal response will contain `token` parameter - the payment token, which can be further used in JavaScript and mobile SDKs.

!!! note "Request and response examples"

    === "Request"
    
        ``` sh  
        curl -i -X POST \
        -H "Content-Type:application/json" \
        -d \
        '{
        "request": {
        "server_callback_url": "http://myshop/callback/",
        "order_id": "TestOrder2",
        "currency": "GEL",
        "merchant_id": 1549901,
        "order_desc": "Test payment",
        "amount": 1000,
        "signature": "91ea7da493a8367410fe3d7f877fb5e0ed666490"
        }
        }' \
        'https://pay.flitt.com/api/checkout/token'
        ```


    === "Normal response"
    
        ``` json
        {
            "response": {
                "token": "9f0124be2b72333fb0e809f82c8f7e4eaeb6ec6e",
                "response_status": "success"
            }
        }
        ```

    === "Response in case of error"
      
        ``` json
        {
            "response":{
                "response_status":"failure",
                "error_message":"Parameter `amount` is mandatory",
                "error_code":"1008"
            }
        }
        ```
</div>

## Flitt hosted checkout page with redirect

<div class="grid" markdown style="width:100%">

!!! note "Flitt hosted checkout page with redirect"

    `POST /api/checkout/redirect`

    This endpoint expects `POST` request wit HTML form with [parameters](/api/order-parameters/#__tabbed_1_1).

    Normal response will contain HTTP code `302 Found` and `Location` url where payer will be automaticaly redirected by his browser.

    In case of error, `/api/checkout/redirect` page will contain html content with Request ID, 4-digit 2XXX error code and error localized description.

!!! note "Request and response examples"

    === "Request"
    
        ``` html  
        <form method="POST" action="https://pay.flitt.com/api/checkout/redirect">
            <input type="text" class="form-input" id="order_id" name="order_id" value="test8651190566">
            <input type="text" class="form-input" id="merchant_id" name="merchant_id" value="1549901">
            <input type="text" class="form-input" id="order_desc" name="order_desc" value="Test order">
            <input type="text" class="form-input" id="amount" name="amount" value="200">
            <input type="text" class="form-input" id="currency" name="currency" value="GEL">
            <input type="text" class="form-input" id="response_url" name="response_url" value="https://site.com/test/responsepage/">
            <input type="text" class="form-input" id="signature" name="signature" value="31c758a76a5dae87f087df171092684130a12bf3">
            <button type="submit">Pay</button>
        </form>
        ```


    === "Normal response"
    
        ``` py
        Request URL: https://pay.flitt.com/api/checkout/redirect/
        Request Method: POST
        Status Code: 302 Found
        Location: https://pay.flitt.com/merchants/5ad6b888f4becb0c33d543d54e57d86c/default/index.html?token=8a09f9d937f43ad6fb40d6b40282d7277a48582a
        ```

    === "Response in case of error"
      
        [![Redirect page]][Redirect page]{ width="400" align="left" }
    
         [Redirect page]: /static/img/redirect_request.png
</div>


!!! Code example   
    
    === "curl"

        ```bash
        $ curl -L 'https://pay.flitt.com/api/checkout/url' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "version": "1.0.1",
            "order_id": "test_order_id_132412412",
            "currency": "GEL",
            "merchant_id": 1549901,
            "order_desc": "Test order",
            "amount": 10025,
            "response_url": "https://example.com/thankyoupage",
            "server_callback_url": "https://example.com/api/callback",
            "signature": "7f52380cefaf3cb793746e2deeb56cf7cd75d532"
          }
        }'
        ```
        response:
        ```json
        {
          "response": {
            "checkout_url": "https://pay.flitt.com/merchants/5ad6b888f4becb0c33d543d54e57d86c/default/index.html?token=03fb1c589f8fcabc80f609c70af541fc636df112",
            "payment_id": "805230052",
            "response_status": "success"
          }
        }
        ```

    === "php"

        **Composer installation**
        ```bash
        composer require flittpayments/php-sdk
        ```
        **Manual installation**
        ```bash
        git clone -b master https://github.com/flittpayments/php-sdk.git
        ```
    
        **Simple Start**
    
        ```php-inline
    
        require 'vendor/autoload.php';
        \Flitt\Configuration::setMerchantId(1549901);
        \Flitt\Configuration::setSecretKey('test');
        
        $checkoutData = [
            'currency' => 'GEL',
            'amount' => 1000
        ];
        $data = \Flitt\Checkout::url($data);
        $url = $data->getUrl();
        //$data->toCheckout() - redirect to checkout
        ```
        
        **Example**

        ```bash
        cd ~/php-sdk
        php -S localhost:8000
        ```

        [Checkout example](https://github.com/flittpayments/php-sdk/tree/master/examples)


    === "vue.js"

        **Simple Start**
        Include checkout.js file 
        ```js
        <script src="https://pay.flitt.com/latest/checkout-vue/checkout.js"></script>
        ```
        Add CSS:
        ```css
        <link rel="preload" href="https://pay.flitt.com/latest/checkout-vue/checkout.css" as="style">
        <link href="https://pay.flitt.com/latest/checkout-vue/checkout.css" rel="stylesheet">
        ```
        HTML congtainer:
        ```html
        <div id="checkout-container"></div>
        ```
        JavaScript code:

        ```js
        var Options = {
          options: {
            methods: ["card"],
            methods_disabled: [],
            card_icons: ["mastercard", "visa"],
            theme: {
              type: "light",
              preset: "reset"
            }
          },
          params: {
            merchant_id: 1549901,
            currency: "GEL",
            amount: 500,
            order_desc: "Demo order"
          },
          css_variable: {
            main: '#7d8ff8',
            card_bg: '#353535',
            card_shadow: '#9ADBE8'
          }
        };
        checkout("#checkout-container", Options);

        ```

    === "JavaScript"

        **1.Installation**

        **Node**
        If you’re using [Npm](https://npmjs.com/) in your project, you can add @flittpayments/js-sdk dependency to package.json with following command:

        ```bash
        npm i --save @flittpayments/js-sdk
        ```

        or add dependency manually:

        ```json
        {
          "dependency": {
            "@flittpayments/js-sdk":"^2.0"
          }
        }
        ```

        **Manual installation**
        If you do not use NodeJS, you can download the latest release. Or clone from GitHub the latest developer version
        ```basg
        git clone git@github.com:flittpayments/js-sdk.git
        ```

        **Quick start**
        ```
        <script src="https://cdn.jsdelivr.net/npm/@flittpayments/js-sdk"></script>
        ```
        **2. Develop html card form using your own design.**

        **Basic template**

        ```html
        <!DOCTYPE html>
        <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
          </head>
          <body>
            <script src="https://cdn.jsdelivr.net/npm/@flittpayments/js-sdk"></script>
            <script>
            $checkout('Api').scope(function(){
                this.request('api.checkout.form','request', { Parameters } ).done(function(model){
                    model.sendResponse();
                    console.log(model.attr('order'));
                }).fail(function(model){
                    console.log(model.attr('error'));
                });
            });
            </script>
          </body>
        </html>
        ```

        Basic template example: [https://github.com/flittpayments/js-sdk#basic-template](https://github.com/flittpayments/js-sdk#basic-template)
        
        **3. Create order using Integration Schema C for JavaScript SDK.**

        Add parameters `required_rectoken=Y` and `server_callback_url` in your request to obtain recurring token (if you are planning recurring payments) 
        in server callback (`rectoken` parameter).

   
        ``` sh  
        curl -i -X POST \
        -H "Content-Type:application/json" \
        -d \
        '{
        "request": {
        "server_callback_url": "http://myshop/callback/",
        "order_id": "TestOrder2",
        "currency": "GEL",
        "merchant_id": 1549901,
        "order_desc": "Test payment",
        "amount": 1000,
        "signature": "91ea7da493a8367410fe3d7f877fb5e0ed666490"
        }
        }' \
        'https://pay.flitt.com/api/checkout/token'
        ```
        
        Documentation: https://docs.flitt.com/docs/page/3/?la=en#chapter-3-6-c.
        Save host-to-host token parameter from response.
        
        **4. Load host-to-host token from step 3 in your card details form.**

        ```json
        {
         "payment_system":"card",
         "token":"host-to-host generated token",
         "card_number":"16/19-digits number",
         "expiry_date":"Supported formats: MM/YY, MM/YYYY, MMYY, MMYYYY",
         "cvv2":"3-digits number"
         }
        ```

        from card form to payment gateway using JavaScript API $checkout('Api').
        https://github.com/flittpayments/js-sdk#host-to-host-token

        **5. Use .on('success') and .on('error') JavaScript callbacks to get result on payment processing.**

        success – order is approved and amount will be charged
        error – order is declined and amount will not be charged
        
        model.attr('error.message') will contain localized error message in case of payment decline. Order information on order status and details will be returned in model.data.order.order_data
        
        JavaScript callback example:

        ```js
        console.log('success',JSON.stringify(model.attr("order").order_data));
        ```

        ```json
        {
          "response": {
            "rrn": "111111111111",
            "masked_card": "444455XXXXXX1111",
            "sender_cell_phone": "",
            "sender_account": "",
            "currency": "GEL",
            "fee": "",
            "reversal_amount": "0",
            "settlement_amount": "0",
            "actual_amount": "200",
            "response_description": "",
            "sender_email": "test@test.com",
            "order_status": "approved",
            "response_status": "success",
            "order_time": "13.07.2024 01:23:59",
            "actual_currency": "GEL",
            "order_id": "test33694502191",
            "tran_type": "purchase",
            "eci": "5",
            "settlement_date": "",
            "payment_system": "card",
            "approval_code": "123456",
            "merchant_id": 1549901,
            "settlement_currency": "",
            "payment_id": 805243692,
            "card_bin": 444455,
            "response_code": "",
            "card_type": "VISA",
            "amount": "200",
            "signature": "b7884b5c4906956fbac4d20390388d913a78c0b0",
            "product_id": "",
            "merchant_data": "Test merchant data",
            "rectoken": "",
            "rectoken_lifetime": "",
            "verification_status": "",
            "parent_order_id": "",
            "fee_oplata": "0",
            "additional_info": "{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": \"{}\", \"transaction_id\": 1994930931, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"13.07.2024 01:24:08\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"version_3ds\": 1, \"is_test\": true}",
            "response_signature_string": "**********|200|GEL|{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": \"{}\", \"transaction_id\": 1994930931, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"13.07.2024 01:24:08\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"version_3ds\": 1, \"is_**********\": true}|200|123456|444455|VISA|GEL|5|0|444455XXXXXX1111|Test merchant data|1549901|**********33694502191|approved|13.07.2024 01:23:59|805243692|card|success|0|111111111111|**********@**********.com|0|purchase"
          }
        }
        ```

        Example: [https://jsfiddle.net/flitt/on8ydsgq/1/](https://jsfiddle.net/flitt/on8ydsgq/1/)


        **6. Process final response received as server callbacks to `server_callback_url`.**
        
        Format of final response: [Response](/api/order-parameters/#__tabbed_1_2)


    === "c#"

        **Installation**
        SDK availble on [NuGet](https://www.nuget.org/packages/FlittSDK/)

        **Simple start**
        ```c#
        using FlittSDK;
        using FlittSDK.Checkout;
        
        Config.MerchantId = 1549901;
        Config.SecretKey = "test";
        
        var req = new CheckoutRequest {
          order_id = Guid.NewGuid().ToString("N"),
          amount = 100000,
          order_desc = "checkout json demo",
          currency = "GEL"
        };
        var resp = new Url().Post(req);
        if (resp.Error == null) {
         string url = resp.checkout_url;
        }
        ```

        To check example: you can use build-in ISS server [http://localhost:7777/](http://localhost:7777/)


    === "node.js"

        **Installation**
        ```bash
        npm install @flittpayments/flitt-node-js-sdk
        ```

        **Manual installation**
        ```basg
        git clone -b master https://github.com/flittpayments/node-js-sdk.git
        ```

        **Simple start**
        ```js
        const FlittPay = require('@flittpayments/flitt-node-js-sdk')
        
        const flitt = new FlittPay(
          {
            merchantId: 1549901,
            secretKey: 'test'
          }
        )
        const requestData = {
          order_id: 'Your Order Id',
          order_desc: 'test order',
          currency: 'GEL',
          amount: '1000'
        }
        flitt.Checkout(requestData).then(data => {
          console.log(data)
        }).catch((error) => {
          console.log(error)
        })

        ```

        [Example checkout](https://github.com/flittpayments/node-js-sdk/tree/master/examples)

    === "python"

        **Installation**
        ```bash
        pip install flittpayments
        ```

        **Simple start**
        ```py
        from flittpayments import Api, Checkout
        api = Api(merchant_id=1549901,
                  secret_key='test')
        checkout = Checkout(api=api)
        data = {
            "currency": "USD",
            "amount": 10000
        }
        url = checkout.url(data).get('checkout_url')
        ```