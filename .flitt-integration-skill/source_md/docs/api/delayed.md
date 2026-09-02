## Delayed payments (customer re-pays payment without new payment request)

**Payment conversion**

The most common decline reasons for payments by card are:

1. insufficient funds
2. invalid card details (cvv2, expiry date, card number)
3. internet payments are not allowed for the card or internet limit is low
4. issuing bank declined payment by other reasons
5. Flitt/bank antifraud system declined payment

In cases 1-3 customer usually can solve the issue promptly enough contacting bank support to: clarify correct expiry date, CVV2, recharge card, increase limit. Therefore, to allow the customer to retry without re-creating the order parameter delayed=Y is added in the protocol .

**Delayed order**

The delayed payment (this is by default, `delayed=Y`) differs from the non-delayed payment (`delayed=N`) in that the client can try to pay it many times until 
the payment lifetime specified in the `lifetime` parameter expires. 

In this case, the merchant will receive the response to `server_callback_url` as many times as the customer tries to pay the payment. 

The client is redirected to response_url only after the expiration of the order’s lifetime (`lifetime` parameter) if at that moment the client 
is trying to make a re-payment. If the client is not at the time of payment on the payment page, the merchant may never receive a response 
to `response_url`. Therefore, for payments with the `delayed = Y` parameter, we recommend that you use the `server_callback_url` parameter.

Returned `order_status` status with `delayed = Y`

* processing – the client tried to make a payment attempt but received a refusal from the bank, non-empty parameters 
`response_code`, `response_description` are returned to `server_callback_url`, the `lifetime` of the order lifetime has not yet expired
* created – the client was redirected to the payment page but has not yet entered payment details
* expired – the client did not enter payment details and the order expired
* declined – is the same as processing, but the lifetime of the order has expired

Returned `order_status` status with `delayed = N`

* declined – the client tried to make an attempt to pay, but received a refusal from the bank, non-empty parameters `response_code`, `response_description` 
are returned to `response_url` and `server_callback_url`
* created – the client was redirected to the payment page but has not yet entered payment details
* expired – the client did not enter payment details and the order expired