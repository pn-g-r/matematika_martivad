Installment payment is executed in 2 steps (only TBC bank is supported as for now)

## Step 1: Create payment

Refer to [Create order](/api/create-order/) page to create an order with a simple code.

First, you need to create payment token or checkout URL from your backend.

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
            "order_id": "test_installment_1",
            "currency": "GEL",
            "merchant_id": 1549901,
            "payment_systems": "installments",
            "payment_method": "x",
            "order_desc": "Test installment payment",
            "amount": 10000,
            "response_url": "https://example.com",
            "signature": "1570574166888217a8d5fb78227ff17c1488be72"
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
            "order_id": "test_installment_1",
            "currency": "GEL",
            "merchant_id": 1549901,
            "payment_systems": "installments",
            "payment_method": "x",
            "order_desc": "Test installment payment",
            "amount": 10000,
            "response_url": "https://example.com",
            "signature": "1570574166888217a8d5fb78227ff17c1488be72"
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

    To create installment payment, the mandatory parameters

    `payment_systems = installments`

    `payment_method = tbc|x`

    must be sent during create order request.

Supported values for `payment_method` are:

| Value     | Description                                                          |
|-----------|----------------------------------------------------------------------|
| `tbc`     | TBC Bank                                                             |
| `x`       | Demo Bank for testing purpose only. See [Testing](/api/testing) page |

Order can be created only within [Redirect](/getting-started/redirect/) or [Embedded](/api/embedded-custom/#example-with-order-created-on-backend) flow and yet not supported for [Direct](/getting-started/direct/).

Refer to [create order](/api/create-order/) and [parameters](/api/order-parameters/) specifications to get details on how to create order.

## Step 2: Strong Customer Authentication (SCA)

After the order is created, in case of [Redirect](/getting-started/redirect/) flow customer need to be redirected to `checkout_url` URL for Strong Customer Authentication within TBC bank.

