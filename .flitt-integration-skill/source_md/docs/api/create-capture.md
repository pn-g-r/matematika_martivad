# Capture the order

Order can be captured fully or partially. Parameter `amount` must be passed in [capture request](../capture-parameters/#__tabbed_2_1) 
equal to [order](../order-parameters/#__tabbed_2_2) `actual_amount` value if full capture is required. 

!!! warning "Pay attention"
    
    Multiple captures are not allowed.   

## The correct sequence of steps for the capture operation

The capture operation is designed to charge the amount previously held on the card.

Hold must be done with [pre-payment request](../order-parameters/) with the parameter `preauth = Y` .

This payment flow is executed with two stages. 
The first stage is a payment operation with preliminary hold of the amount. 
The second stage is the capture of a held amount.

The capture can be performed both with full and partial amount.

!!! note "Note"

    The pre-payment and capture operations are available only for the card payment method.
    The other payment methods do not support these operations and the full amount will be automatically charged according to the one-stage flow:

## Reverse of pre-payment

If the capture operation has not yet been completed, then acquiring fee is not charged for pre-payment and reverse operations. 

Instant cancellation of the held amount takes place when reverse is performed for pre-payment.

If the capture operation has not yet been completed, then only reversal of the full holding amount is available. Partial reverse is not allowed for pre-payment.

If a partial capture operation is performed, the rest of the amount will be automatically returned to the payer’s card and reverse operation is no longer necessary.

!!! note "Example"

    For example, if the pre-payment amount is 1000 and 200 amount should be reversed, then payment must be captured with amount 800.\
    The rest of amount of 200 should not be reversed, otherwise the amount 200 will be reversed twice.

Only single full/partial capture is available for pre-payment operation.
For a captured payment operation, several sequential partial reverses are available.

## Idempotent capture key

Capture operation does not require idempotent key as capture can be securely retried. 
When capture with the same `amount` is retried, current `capture_status` of the payment is returned.

### Endpoint for order capture


<div class="grid" markdown style="width:100%">


!!! note "Capture the order"

    `POST /api/capture/order_id`

    This endpoint expects `POST` request in `JSON` format with [parameters](/api/capture-parameters/#__tabbed_2_1).

    Normal response will contain `capture_status` parameter which indicates if capture is successful or not.

!!! note "Request and response examples"

    === "Request"
    
        ``` sh  
        curl -L 'https://pay.flitt.com/api/capture/order_id' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "version": "1.0.1",
            "order_id": "test_12343242113",
            "currency": "GEL",
            "merchant_id": 1549901,
            "amount": 100,
            "signature": "1efcb015c89da38977ae1e734aade413b95ca900"
          }
        }'
        ```


    === "Normal response"
    
        ``` json
        {
            "response": {
                "capture_status": "captured",
                "order_id": "test_12343242113",
                "response_description": "",
                "response_code": "",
                "merchant_id": 1549901,
                "response_status": "success"
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

