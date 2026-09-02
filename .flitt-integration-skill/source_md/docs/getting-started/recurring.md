Payment with saved card is also called **recurring payment**

Recurring payment is executed in 2 steps

## Step 1: save card and obtain card token

Before executing recurring payments, `rectoken` must be received. 
`rectoken` is a token which references card data, securely stored on the payment gateway side.

To obtain `rectoken`, the parameter `required_rectoken=Y` must be sent during [create order](/api/create-order/) request.
There are two options to obtain token:

**Option 1. During card verification.** 

Send parameter `verification=Y` among with `required_rectoken=Y` during [create order](/api/create-order/) request with small amount value (for example amount = 100). 
In this case, amount value will be held on the card, and will be reversed. 
`rectoken` will be returned in response to `response_url` and in server callback response to `server_callback_url`

**Option 2. During the first purchase.**
During [create order](/api/create-order/) request send amount value of the actual purchase value. 
In this case, amount value will be charged from the card, and `rectoken` will be returned in response to `response_url` and in server callback response to `server_callback_url`.


## Step 2: execute recurring payment without customer participation

[Create payment with saved card](/api/create-order-recurring/) passing recurring token in  `rectoken` parameter 

[//]: # (This flow works for all the cases:)

[//]: # ()
[//]: # (**On web**: you can save cards during payment with [Redirect]&#40;/getting-started/redirect/&#41;, [Embedded]&#40;/getting-started/embedded/&#41;, [Direct]&#40;/getting-started/direct/&#41; integrations.)

[//]: # (**In mobile app**: Save cards )

[//]: # (- with cards)

[//]: # (- with Apple Pay and Google Pay)