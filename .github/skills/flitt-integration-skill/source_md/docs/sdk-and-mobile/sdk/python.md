# Python SDK

Python SDK allows you to accept payment with Visa/MasterCard cards on your website.

Lates version of Python SDK you can always find in our public repository:

[https://github.com/flittpayments/python](https://github.com/flittpayments/python)

=== "Usage example"

    **Installation**
    ```bash
    pip install flittpayments
    ```

    **Simple start**
    ```py
    from flittpayments import Api, Checkout
    api = Api(merchant_id=1549901,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "USD",
        "amount": 10000
    }
    url = checkout.url(data).get('checkout_url')
    ```