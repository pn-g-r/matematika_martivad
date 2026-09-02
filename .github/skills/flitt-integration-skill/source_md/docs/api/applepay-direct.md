# Apple Pay direct integration 

Direct integration can be done in two ways

1. [Using decrypted PAN (DPAN)](/api/applepay-direct/#using-decrypted-pan-dpan)
2. [Using encrypted payment data](/api/applepay-direct/#using-encrypted-payment-data)


Both types of integration require [Apple Pay API](https://developer.apple.com/documentation/applepayontheweb) to be implemented by merchant.


## Using decrypted PAN (DPAN) 

Integration with DPAN assumes that [Payment Data Cryptography](https://developer.apple.com/documentation/PassKit/payment-token-format-reference#Verify-the-signature-and-decrypt-the-payment-data) is performed on merchant side.

To create order using DPAN, merchant needs to use [create order with direct](/api/create-order-direct/) method.

While the [parameters](/api/order-parameters-direct/) are still as described, the parameters which are related to card data should contain information from Apple Pay decrypted payment data:  


!!! note  "Apple Pay DPAN data parameters"

    === "request"
        | Parameters&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Type          | Mandatory | Description|            
        |-----------------------------|---------------|-----------|----------------------------------------------------------------------------|
        | `card_number`              | string(19)  | optional  | `applicationPrimaryAccountNumber` from Apple Pay `data` object|
        | `expiry_date`              | string(4)  | optional  | DPAN expiry date in format MMYY  |
        | `cavv`   | string(2048)  | optional  | Apple Pay one-time `onlinePaymentCryptogram`  from `data.paymentData` dictionary        |       
        | `eci`   | string(2048)  | optional  | Apple Pay `eciIndicator` from `data.paymentData` dictionary|      
        | `wallet`   | string(2048)  | optional  | Wallet type: `applepay`   |         
        | `schemeid`   | string(2048)  | optional  | Visa/MasterCard identifier of CIT - client initiated transaction, returned in initial purchase in field `additional_info->schemeid`, see [response parameters](/api/order-parameters/#__tabbed_2_2)    |           
    === "response"
        see [response parameters](/api/order-parameters/#__tabbed_1_2)



!!! note "Pay attention"

    **Apple Pay and 3DSecure**

    3DSecure authentication is never triggered for Apple Pay payments on Flitt side

!!! warning "Pay attention"

    **Recurring payments with Apple Pay**

    Flitt supports recurring payments for Apple Pay.

    Depending on the parameters which are sent during [order creation](/api/create-order-direct/), order is considered as CIT (client initiated transaction) or MIT (merchant initiated transaction)

    CIT: `cavv` is mandatory, `schemeid` must not be present

    MIT: `schemeid` is mandatory, `cavv` must not be present

!!! note "Examples"

    **Request example of client initiated transaction:**
    
    ``` json
    {
      "request": {
        "order_id": "test_12343242",
        "merchant_id": "1549901",
        "order_desc": "Test order",
        "amount": 1000,
        "currency": "GEL",
        "card_number": "4111111111111111",
        "cavv": "AEH2lSgIQ9/OAALA1DWsGgADFA==",
        "eci": "05",
        "wallet": "applelepay",
        "expiry_date": "1135",
        "client_ip": "8.8.8.8",
        "server_callback_url": "https://myserver.com/callback",
        "signature": "0c0c2374c73267e7be560d80834e4ba28ccda7aa"
      }
    }
    ```

    **Request example of merchant initiated transaction:**
    
    ``` json
    {
      "request": {
        "order_id": "test_12343243",
        "merchant_id": "1549901",
        "order_desc": "Test order",
        "amount": 1000,
        "currency": "GEL",
        "card_number": "4111111111111111",
        "schemeid":"885056510569385"
        "eci": "05",
        "wallet": "applelepay",
        "expiry_date": "1135",
        "client_ip": "8.8.8.8",
        "server_callback_url": "https://myserver.com/callback",
        "signature": "0c0c2374c73267e7be560d80834e4ba28ccda7aa"
      }
    }
    ```


## Using encrypted payment data

Integration with encrypted payment data assumes that [Payment Data](https://developer.apple.com/documentation/PassKit/payment-token-format-reference#Payment-token-structure) obtained from Apple Pay is not decrypted on merchant side.

Instead of that, `container` parameter must be transferred with method [create order with direct](/api/create-order-direct/) to Flitt.

While the [parameters](/api/order-parameters-direct/) are still as described, the parameters `card_number`, `expiry_date`, `cavv`,  `eci`, `wallet` , `schemeid`  which are related to card data must be replaced with `container` parameter.


!!! note  "Apple Pay request example with container"

    ``` json
    {
      "request": {
        "amount": "100",
        "currency": "GEL",
        "merchant_id": "1549901",
        "order_desc": "Test order",
        "order_id": "test_12343244",
        "sender_email": "inga.abashidze123@gmail.com",
        "container": "ewogICJ0b2tlbiI6IHsKICAgICJwYXltZW50TWV0aG9kIjogewogICAgICAibmV0d29yayI6ICJNYXN0ZXJDYXJkIiwKICAgICAgInR5cGUiOiAiQ3JlZGl0IiwKICAgICAgImRpc3BsYXlOYW1lIjogIk1hc3RlckNhcmQgMzA0MSIKICAgIH0sCiAgICAidHJhbnNhY3Rpb25JZGVudGlmaWVyIjogIjIzYTJmMGZjYjYxODU1OTQ4NDNjMzA4N2NhNmUzOTFlZmE0NGE2ZjZmMjcyMzMzYzdhMmFlOWI5NDEyMzc4NTUiLAogICAgInBheW1lbnREYXRhIjogewogICAgICAiZGF0YSI6ICI2dzRrUjF0dDdVNTE5Li4udlV6KzBRb3RSTGRtOWVsdi9LTFNIdVBhMWc4RXpoOWREY0Z5OEZIQ05NTDY5bGNjb3BaVHc5NC9Qa1pyN2l4ZVh0ZXIxOHFkQXl1SnNHVnY4ZWdmTWlSQjMrd09Hb3NIcSIsCiAgICAgICJzaWduYXR1cmUiOiAiTUlBR0NTcUdTSWIzRFFFSEFxQ0FNSUFDQVFFeEQuLi5HMnVTd0NJRURIbS9aTzJmQXFEUmV6b3J5cGhKd1BjSnBRa0xweU4xSVEvRy9wSDRhMUFBQUFBQUFBIiwKICAgICAgImhlYWRlciI6IHsKICAgICAgICAicHVibGljS2V5SGFzaCI6ICJMWm94YVZBU2h2cFFLa0owLi4uWTNJYkNrMVlRZmFnV1dRPSIsCiAgICAgICAgImVwaGVtZXJhbFB1YmxpY0tleSI6ICJNRmt3RXdZSEtvWkl6ajBDLi5pU3piazV1dUUvZzFWRkNoZz09IiwKICAgICAgICAidHJhbnNhY3Rpb25JZCI6ICIyM2EyZjBmY2I2MTg1NTk0OC4uMzkxZWZhNDRhNmY2ZjI3MjMzM2M3YTJhZTliOTQxMjM3ODU1IgogICAgICB9LAogICAgICAidmVyc2lvbiI6ICJFQ192MSIKICAgIH0KICB9Cn0=",
        "signature": "fc30eee74814ad64bfbc153f8f9f1387821beb57"
      }
    }

    ```
 
where `container` is BASE64 encoded JSON object which have next structure:

!!! note  "Apple Pay container structure"

    ``` json
    {
      "token": {
        "paymentMethod": {
          "network": "MasterCard",
          "type": "Credit",
          "displayName": "MasterCard 3041"
        },
        "transactionIdentifier": "23a2f0fcb6185594843c3087ca6e391efa44a6f6f272333c7a2ae9b941237855",
        "paymentData": {
          "data": "6w4kR1tt7U519...vUz+0QotRLdm9elv/KLSHuPa1g8Ezh9dDcFy8FHCNML69lccopZTw94/PkZr7ixeXter18qdAyuJsGVv8egfMiRB3+wOGosHq",
          "signature": "MIAGCSqGSIb3DQEHAqCAMIACAQExD...G2uSwCIEDHm/ZO2fAqDRezoryphJwPcJpQkLpyN1IQ/G/pH4a1AAAAAAAA",
          "header": {
            "publicKeyHash": "LZoxaVAShvpQKkJ0...Y3IbCk1YQfagWWQ=",
            "ephemeralPublicKey": "MFkwEwYHKoZIzj0C..iSzbk5uuE/g1VFChg==",
            "transactionId": "23a2f0fcb61855948..391efa44a6f6f272333c7a2ae9b941237855"
          },
          "version": "EC_v1"
        }
      }
    }
    ```