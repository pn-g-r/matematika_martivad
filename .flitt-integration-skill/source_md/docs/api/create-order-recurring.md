# Create recurring order with saved card

*Endpoint for order creation*


<div class="grid" markdown style="width:100%">


!!! note "Flitt host-to-host enpoint"

    `POST /api/recurring`

    This endpoint expects `POST` request in `JSON` format with [request parameters](/api/order-parameters-recurring/#__tabbed_1_1).

    Normal response will contain [response parameters](/api/order-parameters/#__tabbed_2_2).

    Request is always executed as host-to-host and response is returned in the context of the same request. 

    Redirect and 3DSecure flows are not available for this enpoint.

    If 3DSecure flow is required, follow [payment direct](/api/order-parameters-direct/) specifications.

!!! note "Request and response examples"

    === "Request"
    
        ``` sh  
        curl -L 'https://pay.flitt.com/api/recurring/' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "order_id": "test_recurring_payment123",
            "order_desc": "Debit by token transaction",
            "currency": "GEL",
            "amount": "4600",
            "rectoken": "I0wh7fBmFIdcY6K3Px2QugVrVR65sPafeZkPmRanOiRnXG",
            "signature": "34cda2e7a60c5aee343515fde5deef5403f87f86",
            "merchant_id": "1549901"
          }
        }'
        ```


    === "Normal response"
    
        ``` json
        {
            "response": {
                "rrn": "332518927710",
                "masked_card": "444455XXXXXX6666",
                "sender_cell_phone": "",
                "sender_account": "",
                "currency": "GEL",
                "fee": "",
                "reversal_amount": "0",
                "settlement_amount": "0",
                "actual_amount": "4600",
                "response_description": "",
                "sender_email": "",
                "order_status": "approved",
                "response_status": "success",
                "order_time": "09.10.2024 21:20:46",
                "actual_currency": "GEL",
                "order_id": "test_recurring_payment123",
                "tran_type": "purchase",
                "eci": "7",
                "settlement_date": "",
                "payment_system": "card",
                "approval_code": "418900",
                "merchant_id": 1549901,
                "settlement_currency": "",
                "payment_id": 822895805,
                "card_bin": 444455,
                "response_code": "",
                "card_type": "VISA",
                "amount": "4600",
                "signature": "bb62bd1236695ba6f2252d1cec18ce04d2005559",
                "product_id": "",
                "merchant_data": "",
                "rectoken": "I0wh7fBmFIdcY6K3Px2QugVrVR65sPafeZkPmRanOiRnXG",
                "rectoken_lifetime": "",
                "verification_status": "",
                "parent_order_id": "",
                "additional_info": "{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": null, \"transaction_id\": 2025817355, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"09.10.2024 21:20:47\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"is_test\": true, \"schemeid\": \"mBS8MDuWOpyhdw8aveS\"}",
                "response_signature_string": "**********|4600|GEL|{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": null, \"transaction_id\": 2025817355, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": 0.0, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": \"VISA\", \"card_product\": \"empty_visa\", \"card_category\": null, \"timeend\": \"09.10.2024 21:20:47\", \"ipaddress_v4\": \"178.54.60.26\", \"payment_method\": \"card\", \"is_**********\": true, \"schemeid\": \"mBS8MDuWOpyhdw8aveS\"}|4600|418900|444455|VISA|GEL|7|444455XXXXXX6666|1549901|**********_recurring_payment123|approved|09.10.2024 21:20:46|822895805|card|I0wh7fBmFIdcY6K3Px2QugVrVR65sPafeZkPmRanOiRnXG|success|0|332518927710|0|purchase"
            }
        }
        ```

    === "Response in case of error"
      
        ``` json
        {
            "response": {
                "error_code": 1016,
                "error_message": "Merchant not found",
                "request_id": "3bplo0AeRPxlP",
                "response_status": "failure"
            }
        }
        ```
</div>

