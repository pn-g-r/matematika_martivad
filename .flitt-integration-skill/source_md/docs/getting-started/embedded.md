You can use the **Embedded** integration type if you do not want the customer to leave your site during the
checkout process and prefer to have a seamless process without redirections. Embedded is a good option if you want the
customer to provide payment details on your site and do not process and do not store sensitive payment data.

!!! example "Embedded"

    <p class="codepen" data-height="600" data-theme-id="light" data-default-tab="result" data-slug-hash="BaggpVw" data-pen-title="Flitt -  custom checkout. Compact region" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
      <span>See the Pen <a href="https://codepen.io/flitt/pen/BaggpVw">
      Flitt -  custom checkout. Compact region</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
      on <a href="https://codepen.io">CodePen</a>.</span>
    </p>
    <script async src="https://cpwebassets.codepen.io/assets/embed/ei.js"></script>


Embedded integration type usually requires skills of frontend developer to integrate source of Javascript + HTML + CSS
code in your site. But, if you do not have the ability to develop the code, and your system allows easily to embed
JavaScript code, you can use [Embedded Custom checkout](/api/embedded-custom/)  prebuild JavaScript + HTML + CSS
fragment and insert it into your site.

The main difference between Embedded and Redirect is that customer will see only your site pages with the payment form
seamlessly embedded in your site. Instead of been redirected to `https://pay.flitt.com` during Redirect type integration,
checkout payment form will be loaded in iframe, natively integrated in your site. Embedded checkout page can be
customized with your brand logo and colors in order your customers experienced a frictionless flow and were not
distracted from the checkout process.

[//]: # (![Embedded Custom checkout]&#40;/static/img/customization_4.png&#41;{ width="600" align="right" })

If you do not want to involve developer to integrate payments in your site or your CMS/CRM/Landing builder/Blog platform
does not allow embedded JavaScript code, look at [Redirect](/getting-started/redirect/)

We prepared a set of [Design presets](/getting-started/presets/) for your Embedded checkout page in order you could make
a quick decision with a good combination of payment page design which will interflow with your site native design.

For frontend developer to implement Embedded integration please see API
reference [Embedded/Custom checkout](/api/embedded-custom/) section. Also, we implemented the Embedded checkout
version in our [CRM&CMS plugins](/no-code/cms-plugins) which we have developed.

<h4>For developers</h4>

Embedded checkout allows customising the design of checkout page with JavaScript code. With JavaScript, you can:

* Enable or disable payment methods, change order and priority to display to a customer
* Change design drastically or just change theme or amend some components style
* Enable and configure subscription payments
* Set payment attributes, such as order parameters, language, default payment methods countries
* Add additional fields to the checkout page
* Enable Apple Pay and Google Pay
* Handle JavaScript callbacks and events

See full description of possibilities in [Embedded/Custom checkout](/api/embedded-custom/) section.
