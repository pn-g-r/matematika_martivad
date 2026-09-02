 Split payments

API allows splitting the payment to multiple recipients. The example shows the work with two recipients, although there may be several. 
The requisites of all recipients are transmitted in the request in the parameter receiver and can be any of the following entities: 
- bank account details 
- details stored under a certain merchant_id in the Flitt system 

To split the payment you should follow steps:

1. Create a server-server request (Flitt hosted page purchase request: https://portal.flitt.com/ru/info/api/v1.0/3 or merchant hosted page (PCI DSS) https://docs.flitt.com/docs/page/4/) 
2. Redirect the client in the browser to payment page and request card details
3. Process the response of the result of the payment to the page in the browser response response_url and callback to the server page server_callback_url
4. Send splitting request at https://pay.flitt.com/api/settlement passing it the parameter operation_id equal to the order_id from step 1 and the splitting instruction in the parameter receiver.

## Splitting request

The request is sent using the POST method in the JSON format to the URL: `https://pay.flitt.com/api/settlement`

**Request**:

``` json
{
  "request": {
    "version": 2.0,
    "data": "ewogIm9yZ...Qp9",
    "signature": "943571471619207087eb57e2b4ef69affd337b1a"
  }
}
```

`data` is a base64 encoded format data set:

``` json
{
  "order": {
    "server_callback_url": "http://site.com/callback",
    "currency": "GEL",
    "amount": 300,
    "order_type": "settlement",
    "response_url": "http://site.com/test/responsepage/",
    "order_id": "settlement_test1234561467462099.19",
    "operation_id": "test1234561467462099.19",
    "order_desc": "test order",
    "merchant_id": 700001,
    "receiver": [
      {
        "requisites": {
          "amount": 100,
          "settlement_description": "Purpose of payment for bank transfer",
          "merchant_id": 500001,
          "fee_partner_amount": 102
        },
        "type": "merchant"
      },
      {
        "requisites": {
          "amount": 200,
          "settlement_description": "Purpose of payment for bank transfer",
          "merchant_id": 600001,
          "fee_partner_amount": 102
        },
        "type": "merchant"
      }
    ]
  }
}
```

### Final response (financial result) 

The response is returned in JSON format to `server_callback_url` and `response_url` after the client completes the payment.
Response format:

``` json
{
  "response": {
    "version": "2.0",
    "data": "...",
    "signature": "54aeeadf05b04e2e4097a4aa5907c3a62684d058"
  }
}
```

where `data` is a base64 encoded data set containing information about all financial transactions and their status

``` json
{
  "order": {
    "rrn": "",
    "masked_card": "444455XXXXXX6666",
    "sender_cell_phone": "",
    "response_status": "success",
    "sender_account": "",
    "fee": "",
    "rectoken_lifetime": "",
    "reversal_amount": "0",
    "settlement_amount": "0",
    "actual_amount": "2000",
    "order_status": "approved",
    "response_description": "",
    "verification_status": "",
    "order_time": "07/02/2016 15:21:39",
    "actual_currency": "GEL",
    "order_id": "test1234561467462099.19",
    "parent_order_id": "",
    "merchant_data": "",
    "tran_type": "purchase",
    "eci": "",
    "settlement_date": "",
    "payment_system": "card",
    "rectoken": "",
    "approval_code": "478450",
    "merchant_id": 600001,
    "settlement_currency": "",
    "payment_id": 1586193,
    "transaction": [
      {
        "status": "approved",
        "amount": 20.0,
        "fee": 0.0,
        "reversal_amount": 0.0,
        "parent_tran_id": null,
        "receiver": {},
        "merchant_id": 600001,
        "type": "purchase",
        "id": 1001543960,
        "doc_no": null
      }
    ],
    "product_id": "",
    "currency": "GEL",
    "card_bin": 444455,
    "response_code": "",
    "card_type": "VISA",
    "amount": "2000",
    "sender_email": "demo@flitt.com"
  }
}
```

## Signature calculation

Parameter is calculated as function sha1(password + '|' + data)

## Return of funds

When returning funds you must specify in the parameters  `receiver-> requisites->` from which merchant which part of the original amount should be refunded.
The amount will be returned to the payer's card either online or according to the rules of the bank within a few days if void is not possible.

POST: `https://pay.flitt.com/api/reverse/order_id` 

### Example parameter data:

``` json
{
  "order": {
    "order_id": "test1234561467462099.19",
    "currency": "GEL",
    "amount": "300",
    "merchant_id": "700001",
    "receiver": [
      {
        "requisites": {
          "amount": 100,
          "merchant_id": "500001"
        },
        "type": "merchant"
      },
      {
        "requisites": {
          "amount": 200,
          "merchant_id": "600001"
        },
        "type": "merchant"
      }
    ]
  }
}{
  "order": {
    "order_id": "test1234561467462099.19",
    "currency": "GEL",
    "amount": "300",
    "merchant_id": "700001",
    "receiver": [
      {
        "requisites": {
          "amount": 100,
          "merchant_id": "500001"
        },
        "type": "merchant"
      },
      {
        "requisites": {
          "amount": 200,
          "merchant_id": "600001"
        },
        "type": "merchant"
      }
    ]
  }
}
```

where:
`order_id` and `merchant_id` are the identifiers of the original payment.

### Example of a response for a successful reverse:

``` json
{
  "order": {
    "reverse_status": "approved",
    "reversal_amount": "300",
    "order_id": " test1234561467462099.19 ",
    "response_status": " success ",
    "response_code": " ",
    "response_description": " ",
    "merchant_id": 700001
  }
}
```

### Example of a response in the event of a failure:

``` json
{
  " order ": {
    "reverse_status": "declined",
    "reversal_amount": "300",
    "order_id": "test1234561467462099.19",
    "response_status": "success",
    "response_code": "1016",
    "response_description": "Merchant not found",
    "merchant_id ": 700001
  }
}
```
