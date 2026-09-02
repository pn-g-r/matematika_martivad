# Preparation

During your integration, please follow the Google Pay&trade; API documentation:

For Android:

* [Google Pay Android developer documentation](https://developers.google.com/pay/api/web/overview)
* [Google Pay Android integration checklist](https://developers.google.com/pay/api/android/guides/test-and-deploy/integration-checklist)
* [Google Pay Android brand guidelines](https://developers.google.com/pay/api/android/guides/brand-guidelines)

For web:

* [Google Pay Web developer documentation](https://developers.google.com/pay/api/web/)
* [Google Pay Web integration checklist](https://developers.google.com/pay/api/web/guides/test-and-deploy/integration-checklist)
* [Google Pay Web Brand Guidelines](https://developers.google.com/pay/api/web/guides/brand-guidelines)
 

# Google Pay direct integration 

Google Pay direct integration can be done in two ways

1. [Using decrypted PAN (DPAN)](/api/googlepay-direct/#using-decrypted-pan-dpan)
2. [Using encrypted payment data](/api/googlepay-direct/#using-encrypted-payment-data)


Both types of integration require [Google Pay API](https://developers.google.com/pay/api/web/overview) to be implemented by merchant.

Use the defined values during your integration:

!!! note "Google Pay parameters"

    ```
    gatewayMerchantId: <your Flitt merchant_id>
    gatewayID: flitt
    ```

!!! note " Google Pay"

    Pay attentionm that Flitt supports only following configuration:

    Allowed payment methods : **CARD**

    Allowed authorization methods: **[PAN_ONLY,CRYPTOGRAM_3DS]**

    Allowed card networks: **[MASTERCARD,VISA]**

    Tokenization specification: **PAYMENT_GATEWAY**


    
## Using decrypted PAN (DPAN) 

Integration with DPAN assumes that [Payment Data Cryptography](https://developers.google.com/pay/api/web/guides/resources/payment-data-cryptography) is performed on merchant side.

To create order using DPAN, merchant needs to use [create order with direct](/api/create-order-direct/) method.

While the [parameters](/api/order-parameters-direct/) are still as described, the parameters which are related to card data should contain information from Google Pay decrypted payment data:  


!!! note  "Google Pay DPAN data parameters"

    === "request"
        | Parameters&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Type          | Mandatory | Description|            
        |-----------------------------|---------------|-----------|----------------------------------------------------------------------------|
        | `card_number`              | string(19)  | optional  | `pan` from Google Pay `paymentMethodDetails` object|
        | `expiry_date`              | string(4)  | optional  | DPAN expiry date in format MMYY  |
        | `cavv`   | string(2048)  | optional  | Google Pay one-time `cryptogram`  from `paymentMethodDetails` object        |       
        | `eci`   | string(2048)  | optional  | Google Pay `eciIndicator` from `paymentMethodDetails` object|      
        | `wallet`   | string(2048)  | optional  | Wallet type: `googlepay`       |         
        | `schemeid`   | string(2048)  | optional  | Visa/MasterCard identifier of CIT - client initiated transaction, returned in initial purchase in field `additional_info->schemeid`, see [response parameters](/api/order-parameters/#__tabbed_2_2)    |           
    === "response"
        see [response parameters](/api/order-parameters/#__tabbed_1_2)



!!! warning "Pay attention"

    **Google Pay and 3DSecure**

    3DSecure authentication will be required for Google Pay in Georgia for both authorization methods **PAN_ONLY, CRYPTOGRAM_3DS** and 3DS will be required for **PAN_ONLY** in other regions like Moldova, Armenia.
    
    Consider this when implementing [create order with direct](/api/create-order-direct/) as it can require two-steps flow: 
    
    * create order: `POST /api/3dsecure_step1`
    
    * submit 3DSecure data: `POST /api/3dsecure_step2`

!!! warning "Pay attention"

    **Recurring payments with Google Pay**

    Flitt supports recurring payments for Google Pay.

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
        "wallet": "googlepay",
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
        "wallet": "googlepay",
        "expiry_date": "1135",
        "client_ip": "8.8.8.8",
        "server_callback_url": "https://myserver.com/callback",
        "signature": "0c0c2374c73267e7be560d80834e4ba28ccda7aa"
      }
    }
    ```


## Using encrypted payment data

Integration with encrypted payment data assumes that [Payment Data](https://developers.google.com/pay/api/web/guides/resources/payment-data-cryptography) obtained from Google Pay is not decrypted on merchant side.

Instead of that, `container` parameter must be transferred with method [create order with direct](/api/create-order-direct/) to Flitt.

While the [parameters](/api/order-parameters-direct/) are still as described, the parameters `card_number`, `expiry_date`, `cavv`,  `eci`, `wallet` , `schemeid`  which are related to card data must be replaced with `container` parameter.


!!! note  "Google Pay request example with container"

    ``` json
    {
      "request": {
        "amount": "100",
        "currency": "GEL",
        "merchant_id": "1549901",
        "order_desc": "Test order",
        "order_id": "test_12343243",
        "container": "ewogICJzaWduYXR1cmUiOiAiTUVZQ0lRRE4yYjR5eXdPT0xubmRxWi9kNG5QcmplYnQuLi5Fb05oNVhYUlRKc3JiTThPNE9wUzBrakNMTjNwNSIsCiAgImludGVybWVkaWF0ZVNpZ25pbmdLZXkiOiB7CiAgICAic2lnbmVkS2V5IjogIntcImtleVZhbHVlXCI6XCJNRmt3RXdZSEtvWkl6ajBDQVFZSUtvWkl6ajBEQVFjRC4uLitTb0w2RzhRMzRvUmhFeDVpVXUzS1VBZVRTbDNKakFtaTIyNnRURCtQeTJRXFx1MDAzZFxcdTAwM2RcIixcImtleUV4cGlyYXRpb25cIjpcIjE3NDk4MDQ5NzYwMDBcIn0iLAogICAgInNpZ25hdHVyZXMiOiBbCiAgICAgICJNRVlDSVFEZTdQcXNEa2NnU1cvLy9WL3BKb21BQ3EvM2pQcSt2dmJhLy4uLlBVcnNJWktTYndOYVVaRFpxV0lUMW9BUkNVIgogICAgXQogIH0sCiAgInByb3RvY29sVmVyc2lvbiI6ICJFQ3YyIiwKICAic2lnbmVkTWVzc2FnZSI6ICJ7XCJlbmNyeXB0ZWRNZXNzYWdlXCI6XCJ5TXV3UGFRR1Rqdkw4cENFc0NvbkEwTlNWdzBNUWErSm4yYUpTc2l1UzVyZ0tLVlcybXIyclR2WjhHWVlPTnRuaXpRSGZQd1VUL010dnRrbW9vc1A5YnJ1TjMxRVVIWmY1Nnhla21jUDk3NUVvUG1BZUlXVGNXRzNkejJmUWNPU1hxbkJGY044UEpIVTFNSjBybFhhbUNYNGZ3eVkrOUhiV3cyZUNQTTY5Nk55cXh5eUkwdEpOYzNyTDVxSkltVDguLi5CdkpjVVFIK1FEWHNwbHZRa1lieENqRytxNDQvS2xLdG13NDdKUXRzSnQyYXNZdkdBTTFpSTB3T29zekhpOUxtYjNMRGg2dHVjc2tSSGtmTDM0ODdqelpDQ2hJNi8yVllZL3ZUaitrZWVPV0lOTmtVWkxVZTB1ejFqcWdFRlh1dkZVcnFQMzd5UHJpRWcrN2lMMjJwb1JBSVJXL0YwdVpBeVIvTnNpUXBPQ2VVTUJqcDhcXHUwMDNkXCIsXCJlcGhlbWVyYWxQdWJsaWNLZXlcIjpcIkJBaCtrRXVXWXdRdWxNU1J4aTFYOFdHYXdZWWZoU3BYenJmZEowK3FsbkNMRUE5R2tsRzJEdGwraHltSm5qamJVSHNjUE9lZCtWVDVWcGtySlowRFpBa1xcdTAwM2RcIixcInRhZ1wiOlwiYUVESHpsSGRJMlVoL3BrVDkvRnJRMjg1K0F2U2pkcGtYZnl5eFladTc5SVxcdTAwM2RcIn0iCn0=",
        "signature": "3cfdd28f00ae8f3db6f4dfb816af3a693e0719c8"
      }
    }    
    ```
 
where `container` is BASE64 encoded JSON object which have next structure:

!!! note  "Google Pay container structure"

    ``` json
    {
      "signature": "MEYCIQDN2b4yywOOLnndqZ/d4nPrjebt...EoNh5XXRTJsrbM8O4OpS0kjCLN3p5",
      "intermediateSigningKey": {
        "signedKey": "{\"keyValue\":\"MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcD...+SoL6G8Q34oRhEx5iUu3KUAeTSl3JjAmi226tTD+Py2Q\\u003d\\u003d\",\"keyExpiration\":\"1749804976000\"}",
        "signatures": [
          "MEYCIQDe7PqsDkcgSW///V/pJomACq/3jPq+vvba/...PUrsIZKSbwNaUZDZqWIT1oARCU"
        ]
      },
      "protocolVersion": "ECv2",
      "signedMessage": "{\"encryptedMessage\":\"yMuwPaQGTjvL8pCEsConA0NSVw0MQa+Jn2aJSsiuS5rgKKVW2mr2rTvZ8GYYONtnizQHfPwUT/MtvtkmoosP9bruN31EUHZf56xekmcP975EoPmAeIWTcWG3dz2fQcOSXqnBFcN8PJHU1MJ0rlXamCX4fwyY+9HbWw2eCPM696NyqxyyI0tJNc3rL5qJImT8...BvJcUQH+QDXsplvQkYbxCjG+q44/KlKtmw47JQtsJt2asYvGAM1iI0wOoszHi9Lmb3LDh6tucskRHkfL3487jzZCChI6/2VYY/vTj+keeOWINNkUZLUe0uz1jqgEFXuvFUrqP37yPriEg+7iL22poRAIRW/F0uZAyR/NsiQpOCeUMBjp8\\u003d\",\"ephemeralPublicKey\":\"BAh+kEuWYwQulMSRxi1X8WGawYYfhSpXzrfdJ0+qlnCLEA9GklG2Dtl+hymJnjjbUHscPOed+VT5VpkrJZ0DZAk\\u003d\",\"tag\":\"aEDHzlHdI2Uh/pkT9/FrQ285+AvSjdpkXfyyxYZu79I\\u003d\"}"
    }
    ```