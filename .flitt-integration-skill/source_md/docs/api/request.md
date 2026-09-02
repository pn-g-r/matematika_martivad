Any request to API must contain root element `request`
    ```
    {
        "request": {
            ...
            {request parameters}
            ...
        }
    }
    ```
Every response will contain root element `response`
    ```
    {
        "response": {
            ...
            {response parameters}
            ...
            "response_status": "success"
        }
    }
    ```
!!! note "Pay attention"
    Parameter `response_status` contains status only for HTTP request, but not for payment or reversal or capture status.<br/>
    Order status will be returned in `order_status` parameter. <br/>
    Reversal status will be returned in `reversal_amount` parameter, which will have not 0 value. <br/>
    Capture status will be returned in `capture_status` parameter. <br/>

!!! Example   
    === "request"

        ```json
        {
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
        }
        ```
    === "response"

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