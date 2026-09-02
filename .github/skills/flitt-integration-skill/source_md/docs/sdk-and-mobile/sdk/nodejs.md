# Node.js SDK

Node.js SDK allows you to accept payment with Visa/MasterCard cards on your website.

The latest version of Node.js SDK you can always find in our public repository: 

[https://github.com/flittpayments/node-js-sdk](https://github.com/flittpayments/node-js-sdk)


=== "Usage example"

    **Installation**
    ```bash
    npm install @flittpayments/flitt-node-js-sdk
    ```

    **Manual installation**
    ```basg
    git clone -b master https://github.com/flittpayments/node-js-sdk.git
    ```

    **Simple start**
    ```js
    const FlittPay = require('@flittpayments/flitt-node-js-sdk')
    
    const flitt = new FlittPay(
      {
        merchantId: 1549901,
        secretKey: 'test'
      }
    )
    const requestData = {
      order_id: 'Your Order Id',
      order_desc: 'test order',
      currency: 'GEL',
      amount: '1000'
    }
    flitt.Checkout(requestData).then(data => {
      console.log(data)
    }).catch((error) => {
      console.log(error)
    })

    ```