Open banking payment is executed in 2 steps

## Step 1: Create payment

Refer to [Create order](/api/create-order/) page to create test order with a simple code.

First, you need to create payment  token from your backend.

To do this in a proper way, choose your integration type: Redirect/Iframe or Embedded 

!!! example ""   
    
    
    === "Redirect/Iframe"

        Send request from backend to /api/checkout/url endpoint:
        ```bash
        curl -L 'https://pay.flitt.com/api/checkout/url' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "server_callback_url": "https://testapi.com/api/callback/",
            "order_id": "test_open_banking4",
            "currency": "GEL",
            "merchant_id": 1549901,
            "payment_systems": "opb",
            "payment_method": "x",
            "order_desc": "Test open banking payment",
            "amount": 99999,
            "response_url": "https://example.com",
            "signature": "035acfeca204b350957f45d3f9f6385eafe9cf6b"
          }
        }'
        ```
    
        The response will contain the checkout URL. Redirect customer to this URL or load it in Iframe.
        
        ```json
        {
           "response": {
               "checkout_url": "https://pay.flitt.com/merchants/7ee242403e07af2d3fe9f208b66faec8bae2fe96/default/index.html?token=93dfba14daaa2cb01916606b54d0f3e935786cf7",
               "payment_id": "150009301",
               "response_status": "success"
           }
        }
        ```
    === "Embedded"

        Send request from backend to /api/checkout/token endpoint:
        ```bash
        curl -L 'https://pay.flitt.com/api/checkout/token' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "server_callback_url": "https://testapi.com/api/callback/",
            "order_id": "test_open_banking4",
            "currency": "GEL",
            "merchant_id": 1549901,
            "payment_systems": "opb",
            "payment_method": "x",
            "order_desc": "Test open banking payment",
            "amount": 99999,
            "response_url": "https://example.com",
            "signature": "035acfeca204b350957f45d3f9f6385eafe9cf6b"
          }
        }'
        ```
    
        The response will contain the payment token.
        
        ```json
        {
            "response": {
                "token": "3bd24c7be3bb750d60c2188df3e392bf9c2d3646",
                "response_status": "success"
            }
        }
        ```

        Follow instructions on [Embedded](api/embedded-custom/#example-with-order-created-on-backend) checkout page to complete integration.

!!! warning "Pay attention"
    
    To create Open Banking Payment, the mandatory parameter `payment_systems = opb` must be sent during create order request.

    Additionally `payment_method` parameter can be sent if payment have to be processed through a specified issuing bank.

Supported values for `payment_method` are:

| Value     | Description                                                          |
|-----------|----------------------------------------------------------------------|
| `tbc`     | TBC Bank                                                             |
| `bog`     | Bank of Georgia                                                      |
| `liberty` | Liberty Bank                                                         |
| `credo`   | Credo Bank                                                           |
| `x`       | Demo Bank for testing purpose only. See [Testing](/api/testing) page |

Order can be created only within [Redirect](/getting-started/redirect/) or [Embedded](/api/embedded-custom/#example-with-order-created-on-backend) flow and yet not supported for [Direct](/getting-started/direct/).

Refer to [create order](/api/create-order/) and [parameters](/api/order-parameters/) specifications to get details on how to create order. 

## Step 2: Strong Customer Authentication (SCA)

After the order is created, customer need to be redirected to `checkout_url` URL for Strong Customer Authentication within his bank. 

## How it works

If only `payment_systems = opb` specified, then customer will be redirected to Flitt checkout page.

On the checkout page customer will choose his bank and will be redirected to SCA page of his bank.

[![Open Banking Checkout page]][Open Banking Checkout page]{ width="400" align="left" }
  
  [Open Banking Checkout page]: /static/img/opb1.1.png


If additionally `payment_method` is sent, customer will be redirected to SCA page of his bank without visiting Flitt checkout page:

[![Open Banking Checkout page 2]][Open Banking Checkout page 2]{ width="400" align="left" }
  
  [Open Banking Checkout page 2]: /static/img/opb2.png