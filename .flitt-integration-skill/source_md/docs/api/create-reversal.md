# Reverse the order

Order can be reversed fully or partially. Parameter `amount` must be passed in [reverse request](../reversal-parameters/#__tabbed_2_1) 
equal to [order](../order-parameters/#__tabbed_2_2) `actual_amount` value if full reverse is required. 
Multiple partial reverses are allowed while sum of all partial reverses is less or equal to order `actual_amount`.   

##Idempotent reversal key

Idempotent reversal key `reverse_id` in [reverse request](../reversal-parameters/) is used to provide safe reverse retries. Usually it is not required for full reverse.
In case of partial reverse, idempotent key can protect from multiple retries in case of error. 

!!! note ""
    For example, if order amount is 1000 GEL and partial reversal with amount 100 GEL is sent and failed due to network error, 
    to be sure, that one more attempt of 100 GEL reverse will lead to single partial reversal and not a duplicate (100 + 100 = 200 GEL),
    each attempt must be sent with the same `reverse_id` parameter value.


*Endpoint for order reverse*


<div class="grid" markdown style="width:100%">


!!! note "Reverse the order"

    `POST /api/reverse/order_id`

    This endpoint expects `POST` request in `JSON` format with [parameters](/api/reversal-parameters/#__tabbed_2_1).

    Normal response will contain `reverse_status` parameter which indicates if reversal is successful or not.

!!! note "Request and response examples"

    === "Request"
    
        ``` sh  
        curl -L 'https://pay.flitt.com/api/reverse/order_id' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "order_id": "test_12343242111",
            "currency": "GEL",
            "amount": "1",
            "signature": "29a569275265925c2ec356d3adada1929fd8bb8c",
            "merchant_id": "1549901"
          }
        }'
        ```


    === "Normal response"
    
        ``` json
        {
            "response": {
                "reverse_status": "approved",
                "order_id": "test_12343242111",
                "response_description": "",
                "response_code": "",
                "merchant_id": 1549901,
                "response_status": "success",
                "signature": "c703b3ce82aecfd2de633319685223347140717d",
                "reverse_id": "",
                "reversal_amount": "1",
                "transaction_id": "2011273408"
            }
        }
        ```

    === "Response in case of error"
      
        ``` json
        {
            "response": {
                "error_code": 1007,
                "error_message": "Parameter `signature` is incorrect",
                "request_id": "HGh7ami3WN0ci",
                "response_status": "failure"
            }
        }
        ```
</div>

