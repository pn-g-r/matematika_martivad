# Get reversal status

Reversal status should be obtained through [Get order status](../order-status/) request. 
`reversal_amount` in the order status response accumulates all the reverses, which were successfully processed for the order.
In case when full reversal is processed, `reversal_amount` will be equal to `actual_amount`.
In case when partial reversal or several reversals are processed, `reversal_amount` will be equal to the sum of all partial reversals been processed.

!!! note "Example of partially reversed order"  

    **Order status request:**

    ``` sh 
    curl -L 'https://pay.flitt.com/api/status/order_id' \
    -H 'Content-Type: application/json' \
    -d '{
      "request": {
        "order_id": "test_12343242111",
        "version": "1.0.1",
        "merchant_id": "1549901",
        "signature": "64bbd2d53ee60f88b8184751cc05bd0a846f5768"
      }
    }'
    ```

    **Order status response:**

    `reversal_amount` is highlighted. It is less, than order `actual_amount`, what mean, that order was partially reversed. 

    ``` json hl_lines="9 10"
    {
        "response": {
            "rrn": "111111111111",
            "masked_card": "444455XXXXXX6666",
            "sender_cell_phone": "",
            "sender_account": "",
            "currency": "GEL",
            "fee": "",
            "reversal_amount": "48",
            "actual_amount": "15118",
            "settlement_amount": "0",
            "response_description": "",
            "sender_email": "",
            "order_status": "approved",
            "response_status": "success",
            "order_time": "28.08.2024 21:20:02",
            "actual_currency": "GEL",
            "order_id": "test_12343242111",
            "tran_type": "purchase",
            "eci": "7",
            "settlement_date": "",
            "payment_system": "card",
            "approval_code": "123456",
            "merchant_id": 1549901,
            "settlement_currency": "",
            "payment_id": 814277784,
            "card_bin": 444455,
            "response_code": "",
            "card_type": "VISA",
            "amount": "1000",
            "signature": "8c06dd297c43833ded498b342a6225423f8494b3",
            "product_id": "",
            "merchant_data": "",
            "rectoken": "",
            "rectoken_lifetime": "",
            "verification_status": "",
            "parent_order_id": "",
            "fee_oplata": "0",
            "additional_info": "{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": null, \"transaction_id\": 2011273408, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"28.08.2024 21:20:05\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"is_test\": true}",
            "response_signature_string": "**********|15118|GEL|{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": null, \"transaction_id\": 2011273408, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"28.08.2024 21:20:05\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"is_**********\": true}|1000|123456|444455|VISA|GEL|7|0|444455XXXXXX6666|1549901|**********_12343242111|approved|28.08.2024 21:20:02|814277784|card|success|48|111111111111|0|purchase"
        }
    }
    
    ```
