Fiscalisation process consist of several steps

``` mermaid
sequenceDiagram
  Merchant->>Flitt API: 1. create purchase with reservation_data.products parameter
  Flitt API->>Merchant: 2. Purchase is approved  
  loop Fiscalisation
    Flitt API->>Goverment fiscal server: 3. Sending payment data to goverment fiscal server
    Goverment fiscal server->>Flitt API: 4. Succesfull fiscalisation
  end
  Merchant->>Flitt API: 5. Polling purchase fiscal data     
```

1. You should create purchase. Additional attribute `products` of parameter `reservation_data` must be provided when creating purchase. Check [description](/api/reservation_data/) of this parameter.
2. Flitt approves payments through payment institution and send response to `server_callback_url` ad `response_url`
3. After payment is completed successfully, Flitt sends attribute `products` of parameter `reservation_data` along with other payment data to the government fiscal server.
4. Government fiscalises payment and provide receipt URL with detailed data.
5. You should pool fiscal data using `POST https://pay.flitt.com/api/fiscal_data` request described bellow

##Creating order##

Create order with [redirect](/api/create-order/), [direct](/api/order-parameters-direct/) or any other [type of integration](/).
Pass BASE64 parameter `reservation_data` in order purchase could be fiscalised.

!!! warning "Pay attention" 

    Fiscalisation is available only in Uzbekistan.

    Fiscalisation is available only for purchase without pre-authorisation (parameter `preauth = N` or empty).

!!! Example of request to create purchase   
    
    === "Direct method"
        ```bash
        
            curl -L 'https://pay.flitt.com/api/checkout/3dsecure_step1' \
            -H 'Content-Type: application/json' \
            -d '{
                  "request": {
                    "merchant_id": 1549901,
                    "order_desc": "test order",
                    "amount": "200000",
                    "currency": "UZS",
                    "card_number": "860049XXXXXX6478",
                    "expiry_date": "0399",
                    "cvv2": "***",
                    "preauth": "N",
                    "reservation_data": "ewogICJwcm9kdWN0cyI6IFsKICAgIHsKICAgICAgImlkIjogMSwKICAgICAgIm5hbWUiOiAiUHJvZHVjdCBBIiwKICAgICAgInByaWNlIjogMTAwLjAwLAogICAgICAicXVhbnRpdHkiOiAyLAogICAgICAidmF0X3BlcmNlbnQiOiAyMCwKICAgICAgImNvZGUiOiAiMDA3MDIwMDEwMDEwMDAwMDEiLAogICAgICAidW5pdHMiOiAxLAogICAgICAiZGlzY291bnQiOiAxMC4wMCwKICAgICAgInBhY2thZ2VfY29kZSI6ICI1Njc4IiwKICAgICAgInRvdGFsX2Ftb3VudCI6IDE5MC4wMAogICAgfSwKICAgIHsKICAgICAgImlkIjogMSwKICAgICAgIm5hbWUiOiAiUHJvZHVjdCBCIiwKICAgICAgInByaWNlIjogMTAwLjAwLAogICAgICAicXVhbnRpdHkiOiAyLAogICAgICAidmF0X3BlcmNlbnQiOiAyMCwKICAgICAgImNvZGUiOiAiMDA3MDIwMDEwMDEwMDAwMDEiLAogICAgICAidW5pdHMiOiAxLAogICAgICAiZGlzY291bnQiOiAxMC4wMCwKICAgICAgInBhY2thZ2VfY29kZSI6ICI1Njc5IiwKICAgICAgInRvdGFsX2Ftb3VudCI6IDE5MC4wMAogICAgfQogIF0KfQ==",
                    "order_id": "flittpg16968413",
                    "signature": "0d75c7ea9c0f2d6ada857fe5c462d0c232513f34"
                  }
                }'
        
        ```

    === "Redirect method"
        ```bash
        
            curl -L 'https://pay.flitt.com/api/checkout/url' \
            -H 'Content-Type: application/json' \
            -d '{
                  "request": {
                    "merchant_id": 1549901,
                    "order_desc": "test order",
                    "amount": "200000",
                    "currency": "UZS",
                    "preauth": "N",
                    "reservation_data": "ewogICJwcm9kdWN0cyI6IFsKICAgIHsKICAgICAgImlkIjogMSwKICAgICAgIm5hbWUiOiAiUHJvZHVjdCBBIiwKICAgICAgInByaWNlIjogMTAwLjAwLAogICAgICAicXVhbnRpdHkiOiAyLAogICAgICAidmF0X3BlcmNlbnQiOiAyMCwKICAgICAgImNvZGUiOiAiMDA3MDIwMDEwMDEwMDAwMDEiLAogICAgICAidW5pdHMiOiAxLAogICAgICAiZGlzY291bnQiOiAxMC4wMCwKICAgICAgInBhY2thZ2VfY29kZSI6ICI1Njc4IiwKICAgICAgInRvdGFsX2Ftb3VudCI6IDE5MC4wMAogICAgfSwKICAgIHsKICAgICAgImlkIjogMSwKICAgICAgIm5hbWUiOiAiUHJvZHVjdCBCIiwKICAgICAgInByaWNlIjogMTAwLjAwLAogICAgICAicXVhbnRpdHkiOiAyLAogICAgICAidmF0X3BlcmNlbnQiOiAyMCwKICAgICAgImNvZGUiOiAiMDA3MDIwMDEwMDEwMDAwMDEiLAogICAgICAidW5pdHMiOiAxLAogICAgICAiZGlzY291bnQiOiAxMC4wMCwKICAgICAgInBhY2thZ2VfY29kZSI6ICI1Njc5IiwKICAgICAgInRvdGFsX2Ftb3VudCI6IDE5MC4wMAogICAgfQogIF0KfQ==",
                    "order_id": "flittpg16968414",
                    "signature": "1fdb9eb25a985960a86585aa856218dca90e86f9"
                  }
                }'
        
        ```

    === "Recurring payments"
        ```bash
        
            curl -L 'https://pay.flitt.com/api/recurring' \
            -H 'Content-Type: application/json' \
            -d '{
                  "request": {
                    "merchant_id": 1549901,
                    "order_desc": "test order",
                    "amount": "200000",
                    "currency": "UZS",
                    "preauth": "N",
                    "rectoken": "6aDyYLI2n7aq6ZHBBIiwwglz97emriquch",
                    "reservation_data": "ewogICJwcm9kdWN0cyI6IFsKICAgIHsKICAgICAgImlkIjogMSwKICAgICAgIm5hbWUiOiAiUHJvZHVjdCBBIiwKICAgICAgInByaWNlIjogMTAwLjAwLAogICAgICAicXVhbnRpdHkiOiAyLAogICAgICAidmF0X3BlcmNlbnQiOiAyMCwKICAgICAgImNvZGUiOiAiMDA3MDIwMDEwMDEwMDAwMDEiLAogICAgICAidW5pdHMiOiAxLAogICAgICAiZGlzY291bnQiOiAxMC4wMCwKICAgICAgInBhY2thZ2VfY29kZSI6ICI1Njc4IiwKICAgICAgInRvdGFsX2Ftb3VudCI6IDE5MC4wMAogICAgfSwKICAgIHsKICAgICAgImlkIjogMSwKICAgICAgIm5hbWUiOiAiUHJvZHVjdCBCIiwKICAgICAgInByaWNlIjogMTAwLjAwLAogICAgICAicXVhbnRpdHkiOiAyLAogICAgICAidmF0X3BlcmNlbnQiOiAyMCwKICAgICAgImNvZGUiOiAiMDA3MDIwMDEwMDEwMDAwMDEiLAogICAgICAidW5pdHMiOiAxLAogICAgICAiZGlzY291bnQiOiAxMC4wMCwKICAgICAgInBhY2thZ2VfY29kZSI6ICI1Njc5IiwKICAgICAgInRvdGFsX2Ftb3VudCI6IDE5MC4wMAogICAgfQogIF0KfQ==",
                    "order_id": "flittpg16968414",
                    "signature": "1fdb9eb25a985960a86585aa856218dca90e86f9"
                  }
                }'
        
        ```

##Pooling fiscal data##

To obtain fiscal data, order must be either [captured](/api/capture-parameters/) or approved without `preauth = Y` parameter. 

###Parameters

!!! note  "Request parameters"
    `POST https://pay.flitt.com/api/fiscal_data`

    | Parameter name&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Type               | Description                                                                  | Example                              |
    |-----------------------------|--------------------|------------------------------------------------------------------------------|--------------------------------------|
    | `order_id`                  | string(1024)  | mandatory | Order ID which is generated by merchant                                   | ID1234                                   |
    | `merchant_id`               | integer(12)   | mandatory | Merchant unique ID. Generated by Flitt during merchant registration       | 1549901                                  |
    | `signature`                 | string(40)    | mandatory | Order signature. Required to verify merchant request consistency and authenticity. Signature generation algorithm please see at [Signature generation for request and response](/api/building-signature/) and response                                                                                                         |


!!! note "Request eamples"  
    
    ```curl
    
    curl -L 'https://pay.flitt.com/api/fiscal_data' \
    -H 'Content-Type: application/json' \
    -d '{
      "request": {
        "merchant_id": 1549901,
        "order_id": "6120b190-2a39-4fde-acae-a9761e7e58bd",
        "signature": "b8f84562d3e2a971aea7d173c6fb59084f414d23"
      }
    }'
         
    ```

!!! note "Response examples"  
    
    === "Response in case of Flitt API error"

        ```json
        
        {
            "response": {
                "error": "Merchant account not found",
                "response_status": "success"
            }
        }
        ```

    === "Response in case if fiscal data is not processed yet"

        ```json
        
        {
            "response": {
                "order_id": "6120b190-2a39-4fde-acae-a9761e7e58bd",
                "fiscalisation_data": {
                    "2079125283": {
                        "message": {
                            "ru": "Фискальные данные не найдены.",
                            "uz": "Fiskal ma`lumotlar topilmadi.",
                            "en": "Fiscal data not found."
                        },
                        "code": -31603
                    }
                },
                "response_status": "success"
            }
        }
        
        ```


    === "Response in case if fiscal data is processed successfully"
    
        ```json
        
        {
            "response": {
                "order_id": "pgtest000-1_02",
                "fiscalisation_data": {
                    "9002999267": {
                        "status_code": 0,
                        "message": "",
                        "terminal_id": "EZ000000000658",
                        "date": "",
                        "fiscal_sign": "",
                        "qr_code_url": "https://ofd.soliq.uz/epi?t=XXX&r=XXX&c=XXX&s=XXX",
                        "type": 0,
                        "receipt_id": 3340,
                        "external": true,
                        "processed_date": 1736320610322
                    }
                },
                "response_status": "success"
            }
        }
        
        ```