# JavaScript SDK

JavaScript SDK provides customizable card form to be securely embedded into any html-page.

![JS SDK](/static/img/jssdk.png){ width="350"}


Example: [https://jsfiddle.net/flitt/0sqtb43m/4/](https://jsfiddle.net/flitt/0sqtb43m/4/)


**1.Installation**

**Node**
If you’re using [Npm](https://npmjs.com/) in your project, you can add ```@flittpayments/js-sdk``` dependency to ```package.json``` with following command:

```bash
npm i --save @flittpayments/js-sdk
```

or add dependency manually:

```json
{
  "dependency": {
    "@flittpayments/js-sdk":"^1.2"
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

Documentation: [create order](/api/create-order/#merchant-embedded-checkout-page-with-payment-token).

Save ```token``` parameter from response.

``` json  
{
    "response": {
        "response_status": "success",
        "token": "7ddb3fbb03d60787b3972ef8d6fad0f97f7d2f86"
    }
}
```

**4. Load host-to-host token from step 3 into your card details form.**

```json
{
 "payment_system":"card",
 "token":"host-to-host generated token",
 "card_number":"16/19-digits number",
 "expiry_date":"Supported formats: MM/YY, MM/YYYY, MMYY, MMYYYY",
 "cvv2":"3-digits number"
 }
```


**5. Use ```.on('success')``` and ```.on('error')``` JavaScript callbacks to get result on payment processing.**

```success``` – order is approved and amount will be charged
```error``` – order is declined and amount will not be charged

```model.attr('error.message')``` will contain localized error message in case of payment decline. Order information on order status and details will be returned in ```model.data.order.order_data```

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

**6. Process final response received as server callbacks to `server_callback_url`.**

Format of final response: [Response](/api/order-parameters/#__tabbed_1_2)
