# Get capture status

Capture status should be obtained through `capture_amount` attribute in `additional_info` in [Get order status](../order-status/) request.
In case when full capture is processed, `capture_amount` will be equal to order `actual_amount`.
In case when partial capture is processed, `capture_amount` will be lower then `actual_amount`.

!!! note "Example of partially captured order"  

    **Order status request:**

    ``` sh 
    curl -L 'https://pay.flitt.com/api/status/order_id' \
    -H 'Content-Type: application/json' \
    -d '{
      "request": {
        "order_id": "test_12343242113",
        "version": "1.0.1",
        "merchant_id": "1549901",
        "signature": "28abd3db20cad9b8257b5cca88f0bf1c450bd2fd"
      }
    }'
    ```

    **Order status response:**

    `additional_info` with `capture_status` and `capture_amount` is highlighted. It is less, than order `actual_amount`, what mean, that order was partially captured.

    ``` json hl_lines="11 39"
    {
        "response": {
            "rrn": "111111111111",
            "masked_card": "444455XXXXXX6666",
            "sender_cell_phone": "",
            "sender_account": "",
            "currency": "GEL",
            "fee": "",
            "reversal_amount": "0",
            "settlement_amount": "0",
            "actual_amount": "15118",
            "response_description": "",
            "sender_email": "",
            "order_status": "approved",
            "response_status": "success",
            "order_time": "30.08.2024 12:39:48",
            "actual_currency": "GEL",
            "order_id": "test_12343242113",
            "tran_type": "purchase",
            "eci": "7",
            "settlement_date": "",
            "payment_system": "card",
            "approval_code": "123456",
            "merchant_id": 1549901,
            "settlement_currency": "",
            "payment_id": 814543587,
            "card_bin": 444455,
            "response_code": "",
            "card_type": "VISA",
            "amount": "1000",
            "signature": "c7cac63ddb9bf54b0511ddbf9ddab1351f8260b6",
            "product_id": "",
            "merchant_data": "",
            "rectoken": "",
            "rectoken_lifetime": "",
            "verification_status": "",
            "parent_order_id": "",
            "fee_oplata": "0",
            "additional_info": "{\"capture_status\": \"captured\", \"capture_amount\": 1.0, \"reservation_data\": null, \"transaction_id\": 2011462103, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"30.08.2024 12:40:32\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"is_test\": true}",
            "response_signature_string": "**********|15118|GEL|{\"capture_status\": \"captured\", \"capture_amount\": 1.0, \"reservation_data\": null, \"transaction_id\": 2011462103, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"30.08.2024 12:40:32\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"is_**********\": true}|1000|123456|444455|VISA|GEL|7|0|444455XXXXXX6666|1549901|**********_12343242113|approved|30.08.2024 12:39:48|814543587|card|success|0|111111111111|0|purchase"
        }
    }
    ```
    