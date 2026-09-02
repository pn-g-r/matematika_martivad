You can use the <strong>Redirect</strong> integration type if you are fine with redirecting customer from your site to
payment page hosted on Flitt side. Redirect is a good option if you want the customer to see all payment methods on a
single page.

[![Redirect page]][Redirect page]{ width="400" align="left" }

  [Redirect page]: /static/img/intro/redirect.png

If you do not want the customer to leave your site during the checkout process and prefer to have a seamless process
without redirections, look at [Embedded](/getting-started/embedded/) or [Direct](/getting-started/direct/) integration type.

The main difference between Redirect and Embedded/Direct is that customers will see `https://pay.flitt.com` page with the
payment form instead of your site domain name.

Redirect checkout page can be customized with [Design presets](/getting-started/presets/) which can be combined with
your brand logo and colors. This will improve the user experience of your customers during online payments and will not
distract them from the checkout process.

## For developers

To implement Redirect integration type please see API reference [create order](/api/create-order/) section.

We prepared code examples and [SDK](/sdk-and-mobile/sdk/about-sdk/) for different programming languages to make
integration for you more simple.

- [JavaScript](/sdk-and-mobile/sdk/js)
- [PHP](/sdk-and-mobile/sdk/php)
- [Python](/sdk-and-mobile/sdk/python)
- [C#](/sdk-and-mobile/sdk/csharp)
- [Node.js](/sdk-and-mobile/sdk/nodejs)

!!! example   
=== "JavaScript"

    ```html
    <script type="text/x-vue-template" id="f-fields">
      <div>
        <input-amount name="amount" label="my_amount"></input-amount>
        <input-text
          name="order_desc"
          value="order_desc"
          label="Product Description"
          description="description"
          custom
        ></input-text>
      </div>
    </script>

    <script>
      checkout('#app', {
        options: {
          fields: true,
        },
        params: {
          currency: 'GEL',
          merchant_id: 1549901,
          amount: 100,
          response_url: 'http://example.com/result/',
          api_domain: 'pay.flitt.com',
        },
      })
    </script>
    ```

=== "PHP"

    ```php
    require 'vendor/autoload.php';
    \Cloudipsp\Configuration::setMerchantId(1549901);
    \Cloudipsp\Configuration::setSecretKey('test');
    
    $checkoutData = [
        'currency' => 'GEL',
        'amount' => 1000
    ];
    $data = \Cloudipsp\Checkout::url($data);
    $url = $data->getUrl();
    //$data->toCheckout() - redirect to checkout
    ```

=== "Python"

    ```python
    from cloudipsp import Api, Checkout
    api = Api(merchant_id=1549901,
              secret_key='test')
    checkout = Checkout(api=api)
    data = {
        "currency": "GEL",
        "amount": 10000
    }
    url = checkout.url(data).get('checkout_url')
    ```

=== "C#"

    ```c#
    using CloudIpspSDK;
    using CloudIpspSDK.Checkout;
    
    Config.MerchantId = 1549901;
    Config.SecretKey = "test";
    
    var req = new CheckoutRequest {
      order_id = Guid.NewGuid().ToString("N"),
      amount = 100000,
      order_desc = "checkout json demo",
      currency = "GEL"
    };
    var resp = new Url().Post(req);
    if (resp.Error == null) {
     string url = resp.checkout_url;
    }
    ```

=== "Node.js"

    ```nodejsrepl
    const CloudIpsp = require('cloudipsp-node-js-sdk')
    
    const checkout = new CloudIpsp(
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
    checkout.Checkout(requestData).then(data => {
      console.log(data)
    }).catch((error) => {
      console.log(error)
    })
    ```

Also, you can use Redirect with any [CMS&CRM](/no-code/cms-plugins) system which we support. 