# Integration

Integrating Google Pay&trade; into a website can be done either through:

- [Redirect method](/getting-started/redirect/)
- [Embedded method](/getting-started/embedded/)
- Directly with [Google Pay API](https://developers.google.com/pay/api/web/guides/tutorial).

Redirect and embedded methods require integration only with Flitt's API or SDK and thus less coding and complexity.

Integrating Google Pay with Google Pay API directly requires additional Apple certificates management and encryption/decryption procedures coding. 

Direct method also involves different approaches depending on tokenized Primary Account Number (DPAN) or an encrypted payment container is used during payment flow processing.

## Google Pay with redirect to Flitt checkout page 

Refer to [create order](/api/create-order/) to create order on your backend or frontend and redirect payer to the checkout page.
Google Pay button will automatically appear at checkout page.
The payment is processed on Flitt’s secure platform, reducing complex coding and the risk of handling sensitive data.


## Google Pay button, embedded to merchant website

Embedded method provides a seamless checkout experience without leaving the merchant website, which can increase conversion rate.

Embedded Google Pay button can be placed in a way to fit the look and feel of the website, providing a more cohesive brand experience.

This type of integration also gives greater control over the checkout process and design.

Meanwhile, this method is more complex than redirect method to implement, requiring more development resources and expertise.

**Example Google Pay button:**

<div style="width: 400px">
<p class="codepen" data-height="300" data-theme-id="light" data-default-tab="result" data-slug-hash="PorvvEw" data-pen-title="Flitt -  Apple, Google Pay buttons" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/PorvvEw">
  Flitt -  Apple, Google Pay buttons</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
</div>

**Verify your domain in Google Pay developer account**

- [x] To embedd Google Pay button from Flitt, you must register all of your web domains where button will be displayed. 
This relates to top-level domains (for example, site.com) and subdomains (for example, shop.site.com, www.site.com), both production and development sites.
- [x] Tell Flitt to activate your domain with Google.


## Google Pay direct integration

Please follow [Google Pay direct](/api/googlepay-direct/) instructions.