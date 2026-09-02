#Create an embedded checkout page with an individual design. Version 2.0

Project at GitHub: [https://github.com/flittpayments/checkout-vue](https://github.com/flittpayments/checkout-vue)

You can design your own checkout page hosted on your website as a regular HTML + CSS code.

We developed pre-designed example (HTML/CSS/JavaScript) which you can try to use on your site:

!!! note "Google Pay policy"

    Before integrating Google Pay&trade; with the Flitt embedded method, please adhere to [Google Pay APIs Acceptable Use Policy](https://payments.developers.google.com/terms/aup)

    By starting the integration you confirm that you accept the terms defined in the [Google Pay API Terms of Service](https://payments.developers.google.com/terms/sellertos).


## Basic checkout design example. Card, Apple Pay, Google Pay&trade;

<p class="codepen" data-height="800" data-theme-id="light" data-default-tab="result" data-slug-hash="OJeYwvO" 
data-pen-title="Flitt -  custom checkout light" data-user="flitt" style="height: 800px; box-sizing: border-box; display: flex; align-items: center; 
justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/OJeYwvO">
  Flitt -  custom checkout light</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
<script async src="https://cpwebassets.codepen.io/assets/embed/ei.js"></script>

First, you need to import JavaScript SDK:

``` html 
https://pay.flitt.com/latest/checkout-vue/checkout.js
```

Then CSS files:

``` html
https://pay.flitt.com/latest/checkout-vue/checkout.css
```

Checkout page is configured with JavaScript code:

!!! example  "Configuration example"

    ``` js 
    var Options = {
        options: {
            methods: ['card'],
            methods_disabled: [],
            card_icons: ['mastercard', 'visa', 'maestro'],
            active_tab: 'card',
            fields: false,
            title: 'my_title',
            link: 'https://shop.com',
            full_screen: true,
            button: true,
            email: true
        },
        params: {
            merchant_id: 1549901,
            required_rectoken: 'y',
            currency: 'GEL',
            amount: 500,
            order_desc: 'my_order_desc',
            response_url: 'http://shop.com/thankyoupage'
        }
    }
    checkout("#app", Options);
    ```

 
JavaScript configuration has the following structure:

!!! note  "Configuration structure"

    ``` js 
    {
      options: {},
      params: {},
      button: {}, // button config 
      fields_custom: [],
      messages: {},
      css_variable: {},
    }
    ```
 
 
=== "options"

    Configure payment page form customization options

    |Parameter name|Parameter type|Default value|Description| 
    |-----------------------------|---------------|-----------|----------------------------------------------------------------------------|
    |`methods`             | Array       | ['card']                | support `card`, `most_popular`, `banks`, `wallets`.                                         |
    |`methods_disabled`    | Array       | []                      | support `card`, `most_popular`, `banks`, `wallets`.                                         |
    |`wallet_methods_enabled`| Array     | ['apple', 'google']     | support `apple`, `google`.                                                          |
    |`card_icons`          | Array       | ['mastercard', 'visa']  | support `mastercard`, `visa`, `prostir`, `diners`, `american_express` , `jcb`, `maestro`, `union_pay`|
    |`banks_icons`         | Array       | []                      |                                                                                     |
    |`local_methods_icons` | Array       | []                      |                                                                                     |
    |`crypto_icons`        | Array       | []                      |                                                                                     |
    |`loans_icons`         | Array       | []                      |                                                                                     |
    |`emoney_icons`        | Array       | []                      |                                                                                     |
    |`wallets_icons`       | Array       | []                      |                                                                                     |
    |`title`               | String      |                         |                                                                                     |
    |`link`                | String      |                         | format url                                                                          |
    |`full_screen`         | Boolean     | true                    |                                                                                     |
    |`locales`             | Array       | [all]                   | support  `az`, `cs`, `da`, `de`, `en`, `es`, `fi`, `fr`, `hu`, `it`, `ka`, `ko`, `lv`, `nl`, `pl`, `ro`, `ru`, `sk`, `uk`, `zh`|
    |`api_domain`          | String      | 'pay.flitt.com'         |                                                                                     |
    |`endpoint`            | Object      |                         |                                                                                     |
    |`active_tab`          | String      | 'card'                  | support `card`, `most_popular`, `banks`, `wallets`                                                             |
    |`active_method`       | String      | ''                      |                                                                                     |
    |`logo_url`            | String      |                         | format url                                                                          |
    |`offerta_url`         | String      |                         | format url                                                                          |
    |`default_country`     | String      |                         |                                                                                     |
    |`countries`           | Array       |                         |                                                                                     |
    |`theme`               | Object      |                         |                                                                                     |
    |`show_menu_first`     | Boolean     | false                   |                                                                                     |
    |`disable_request`     | Boolean     | false                   | no requests are sent to the server                                                  |
    |`subscription`        | Object      |                         |                                                                                     |
    |`loading`             | String      |                         | format url                                                                          |
    |`amount_readonly`     | Boolean     | true                    |                                                                                     |
    |`autosubmit`          | Boolean     | false                   |                                                                                     |
    |`show_amount`         | Boolean     | true                    |                                                                                     |
    |`show_email`          | Boolean     | false                   |                                                                                     |
    |`show_fee`            | Boolean     | true                    |                                                                                     |
    |`show_lang`           | Boolean     | true                    |                                                                                     |
    |`show_link`           | Boolean     | true                    |                                                                                     |
    |`show_order_desc`     | Boolean     | true                    |                                                                                     |
    |`show_pay_button_amount`| Boolean     | true                    | displaying the amount on the button                                               |
    |`show_pay_button`     | Boolean     | true                    |                                                                                     |
    |`show_processed`      | Boolean     | true                    |                                                                                     |
    |`show_secure_message` | Boolean     | true                    |                                                                                     |
    |`show_test_mode`      | Boolean     | true                    |                                                                                     |
    |`show_title`          | Boolean     | true                    |                                                                                     |

    **options.theme**

    Name                  | Type        | Default                 | Description
    ---                   | ---         | ---                     | ---
    `type`                | String      | 'light'                 | support `light`, `dark`.
    `preset`              | String      | 'black'                 | support `reset`, `black`, `silver`, `vibrant_silver`, `vibrant_gold`, `solid_black`, `black_and_white`, `euphoric_pink`, `heated_steel`, `nude_pink`, `tropical_gold`, `navy_shimmer`.
    `layout`              | String      | 'default'               | support `default`, `plain`, `wallets_only`.

    **options.subscription**


    Name                  | Type1        | Default                 | Description
    ---                   | ---         | ---                     | ---
    `type`                | String      | 'disable'               | support `disable`, `hidden`, `shown_edit_on`, `shown_edit_off`, `shown_readonly`
    `periods`             | Array       | ['day', 'week', 'month']| support `day`, `week`, `month`.
    `quantity`            | Boolean     | false                   |
    `trial`               | Boolean     | false                   |
    `unlimited`           | Boolean     | true                    |
    `readonly`            | Boolean     | false                   |
 



=== "params"

    Order parameters described in [Request parameters](/api/order-parameters/#__tabbed_2_1)

    |Parameter name|Parameter type|Default value|Description| 
    |-----------------------------|---------------|-----------|----------------------------------------------------------------------------|
    |`merchant_id`         | Integer     | 1549901                 |                             |
    |`order_desc`          | String      |                         |                             | 
    |`amount`              | Integer     | null                    |                             |
    |`currency`            | String      | 'GEL'                   |                             |
    |`response_url`        | String      |                         | format url                  |
    |`lang`                | String      | browser language        |                             | 
    |`required_rectoken`   | String      |                         | support `Y`, `N`, `y`, `n`. |
    |`verification`        | String      |                         | support `Y`, `N`, `y`, `n`. |
    |`token`               | String      |                         | length 40                   | 
    |`button`              | String      |                         | length 20-80                | 
    |`offer`               | Boolean     | false                   |                             |
    |`recurring_data`      | Object      |                         |                             |
    |`custom`              | Object      |                         |                             |
    |`customer_data`       | Object      |                         |                             |

    **params.recurring_data**

    Subscription parameters values: period, frequency, start date, end date, regular amount

    Name                  | Type        | Default                 | Description
    ---                   | ---         | ---                     | ---
    `every`               | Integer     | 1                       |
    `period`              | String      | 'month'                 | support `day`, `week`, `month`.
    `amount`              | Integer     | 0                       |
    `end_time`            | String      |                         | format YYYY-MM-DD
    `start_time`          | String      |                         | format YYYY-MM-DD
    `quantity`            | Integer     | 0                       |
    `trial_period`        | String      | ''                      |
    `trial_quantity`      | Integer     | 0                       |

    **params.customer_data**

    Name                  | Type        | Default                 | Description
    ---                   | ---         | ---                     | ---
    `customer_name`       | String      |                         |
    `customer_address`    | String      |                         |
    `customer_zip`        | String      |                         |
    `customer_city`       | String      |                         |
    `customer_country`    | String      |                         | dictionary countries
    `customer_state`      | String      |                         |
    `phonemobile`         | String      |                         | format phone
    `email`               | String      |                         | format email
    
=== "messages"

    Messages localization 
 
    ``` js 
    {
      messages: {
        {en}: {
          {id}: {value},
          ...
        },
        ...
      },
    }
    ``` 
 
=== "css_variable"

    ``` js 

    {
      css_variable: {
        main: {hex color value},
        card_bg: {hex color value},
        card_shadow: {hex color value}
      }
    }       
    ``` 

=== "fields_custom"

    ``` js
    {
      fields_custom: {
        id-1: {
          name: 'id-1',
          label: 'label1',
          value: 'value1',
          readonly: true,
          p: 1
        },
        id-2: {
          name: 'id-2',
          label: 'label2',
          value: 'value2',
          p: 2
        },
        id-3: {
          name: 'id-3',
          label: 'label3',
          type: 'checkbox',
          required: true,
          p: 3
        }
      }
    }
    ```
Below are examples of ready-made designs of payment pages in different styles.


## Plain checkout design example for cards

<p class="codepen" data-height="500" data-default-tab="js,result" data-slug-hash="vEEmoOw" data-pen-title="Flitt - layout plain" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/vEEmoOw">
  Flitt - layout plain</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
<script async src="https://public.codepenassets.com/embed/index.js"></script>


## Plain checkout design example for cards with JS code submit button

<p class="codepen" data-height="500" data-default-tab="js,result" data-slug-hash="qEONWoY" data-pen-title="Flitt - layout plain with submit button" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/qEONWoY">
  Flitt - layout plain with submit button</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
<script async src="https://public.codepenassets.com/embed/index.js"></script>

##Example style light background, blue card

<p class="codepen" data-height="650" data-theme-id="light" data-default-tab="result" data-slug-hash="KKjLBdo" data-pen-title="Flitt -  custom checkout light" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/KKjLBdo">
  Flitt -  custom checkout light</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
 

##Example style dark background, blue card

<p class="codepen" data-height="650" data-theme-id="light" data-default-tab="result" data-slug-hash="ZEdZwRR" data-pen-title="Flitt -  custom checkout dark" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/ZEdZwRR">
  Flitt -  custom checkout dark</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>



##Example for compact region 

With parameters `full_screen: false`, `hide_title: true`, `hide_link: true`

<div style="width: 400px">
<p class="codepen" data-height="700" data-theme-id="light" data-default-tab="result" data-slug-hash="BaggpVw" data-pen-title="Flitt -  custom checkout. Additional fields. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/BaggpVw">
  Flitt -  custom checkout. Additional fields. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
    
</div>
 
##Example with additional merchant fields

<p class="codepen" data-height="900" data-theme-id="light" data-default-tab="result" data-slug-hash="bGPyOWz" data-pen-title="Flitt -  custom checkout. Additional fields. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/bGPyOWz">
  Flitt -  custom checkout. Additional fields. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>

 
##Example with subscription

After the first successful payment, payment gateway will create a calendar with scheduled regular payments. The frequency and frequency are set in the parameters of the payment page.

<p class="codepen" data-height="1000" data-theme-id="light" data-default-tab="result" data-slug-hash="eYwabEJ" data-pen-title="Flitt -  custom checkout. Subscription. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/eYwabEJ">
  Flitt -  custom checkout. Subscription. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>

 
##Example with subscription and localization of custom fields

<p class="codepen" data-height="1200" data-theme-id="light" data-default-tab="result" data-slug-hash="vYqwvWj" data-pen-title="Flitt -  custom checkout. Subscription. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/vYqwvWj">
  Flitt -  custom checkout. Subscription. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>

 
##Example with extended payment methods

<p class="codepen" data-height="800" data-theme-id="light" data-default-tab="result" data-slug-hash="VwJOqQQ" data-pen-title="Flitt -  custom checkout. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/VwJOqQQ">
  Flitt -  custom checkout. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>

 
##Example with handling of pay-button click event

<p class="codepen" data-height="550" data-theme-id="light" data-default-tab="js" data-slug-hash="oNrRJyp" data-pen-title="Flitt - checkout with own submit buttons. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/oNrRJyp">
  Flitt - checkout with own submit buttons. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>

 
##Example with JavaScript callbacks

You can catch `response_code` value and replace a code message with yours custom.
See all [codes](/api/response-codes/#javascript-response-codes).

<p class="codepen" data-height="600" data-theme-id="light" data-default-tab="js" data-slug-hash="vYqwwXP" data-pen-title="Flitt -  custom checkout.  Javascript calbacks. Version 2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/vYqwwXP">
  Flitt -  custom checkout.  Javascript calbacks. Version 2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
 
## Example of Apple Pay and Google Pay buttons

<div style="width: 400px">
<p class="codepen" data-height="300" data-theme-id="light" data-default-tab="result" data-slug-hash="PorvvEw" data-pen-title="Flitt -  Apple, Google Pay buttons" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
  <span>See the Pen <a href="https://codepen.io/flitt/pen/PorvvEw">
  Flitt -  Apple, Google Pay buttons</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
  on <a href="https://codepen.io">CodePen</a>.</span>
</p>
</div>

##Example with order created on backend

**Create order at your server:**

``` sh 
curl -i -X POST \
 -H "Content-Type:application/json" \
 -d \
'{
  "request": {
    "server_callback_url": "http://myshop/callback/",
    "order_id": "TestOrder_JSSDK_v2",
    "currency": "GEL",
    "merchant_id": 1549901,
    "order_desc": "Test payment",
    "lifetime" : 999999,
    "amount": 1000,
    "signature": "91ea7da493a8367410fe3d7f877fb5e0ed666490"
  }
}' \
 'https://pay.flitt.com/api/checkout/token' 
```

**Receive order token:**

``` json
{
  "response":{
    "response_status":"success",
    "token":"b3c178ad84446ef36eaab365b1e12e6987e9b3d9"
  }
} 
``` 
 
**Load checkout page with order token as a parameter:**

``` js

var Options = {
  options: {
    methods: ['card'],
    methods_disabled: [],
    card_icons: ['mastercard', 'visa', 'maestro'],
    active_tab: 'card',
    fields: false,
    title: 'Demo checkout',
    link: 'https://shop.com',
    full_screen: true,
    button: true,
    email: true
  },
  params: {
    token: "13c178ad84446ef36eaab365b1e12e6987e9b3d9"
  }
}
checkout("#checkout-container", Options);

```
 
##Using color presets and  personal log

You can use gradient color presets with object **theme** in the **options** section.

``` js 
options: {
  methods: ['card'],
  ...
  ,
  theme: {
    type: "light",
    preset: "black"
}
``` 

**type** attribute can have "light" or "dark" value.

**preset** attribute can have one of the following values:

``` html
vibrant_gold
vibrant_silver
euphoric_pink
black
solid_black
silver
black_and_white
heated_steel
nude_pink
tropical_gold
navy_shimmer
```

!!! example "euphoric_pink preset example"

    <p class="codepen" data-height="600" data-theme-id="light" data-default-tab="result" data-slug-hash="RwzzKMo" data-pen-title="Flitt -  minimal checkout ligt euphoric_pink v2.0" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
      <span>See the Pen <a href="https://codepen.io/flitt/pen/RwzzKMo">
      Flitt -  minimal checkout ligt euphoric_pink v2.0</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
      on <a href="https://codepen.io">CodePen</a>.</span>
    </p>

All gradients naming you can match as follows (click to enlarge image):

[![Presets]][Presets]{ width="400" align="left" }
[Presets]:/static/img/preset_namings.png

You can use custom flat colors with `css_variable` parameter (to use it, you need to set `preset: "reset"`) as well as own logo with `logo_url` parameter:

!!! example "Example with main color: valencia #D94343 for card background and fuchsia_blue: #7054C7 for button color"

    <p class="codepen" data-height="700" data-theme-id="light" data-default-tab="js,result" data-slug-hash="YzobowX" data-pen-title="Flit - custom colors" data-user="flitt" style="height: 300px; box-sizing: border-box; display: flex; align-items: center; justify-content: center; border: 2px solid; margin: 1em 0; padding: 1em;">
      <span>See the Pen <a href="https://codepen.io/flitt/pen/YzobowX">
      Flit - custom colors</a> by Flitt.com (<a href="https://codepen.io/flitt">@flitt</a>)
      on <a href="https://codepen.io">CodePen</a>.</span>
    </p>


We recommend to use such colors: 

<div style="color: white; background: #D94343">valencia:			#D94343</div>

<div style="color: white; background: #DF583D">flame_pea:			#DF583D</div>
<div style="color: white; background: #E86F33">jaffa:				#E86F33</div>
<div style="color: white; background: #E58626">zest:				#E58626</div>
<div style="color: white; background: #EBA212">gamboge:			    #EBA212</div>
<div style="color: white; background: #A9B221">citron:				#A9B221</div>
<div style="color: white; background: #82B536">sushi:				#82B536</div>
<div style="color: white; background: #6BA854">chelsea_cucumber:	#6BA854</div>
<div style="color: white; background: #54A868">fruit_salad:		    #54A868</div>
<div style="color: white; background: #54A199">breaker_bay:		    #54A199</div>
<div style="color: white; background: #43ABBF">pelorous:			#43ABBF</div>
<div style="color: white; background: #57A4DC">havelock_blue:		#57A4DC</div>
<div style="color: white; background: #4F8BE0">curious_blue:		#4F8BE0</div>
<div style="color: white; background: #6073D1">indigo:				#6073D1</div>
<div style="color: white; background: #7054C7">fuchsia_blue:		#7054C7</div>
<div style="color: white; background: #8453B5">studio:				#8453B5</div>
<div style="color: white; background: #9D55B5">wisteria:			#9D55B5</div>
<div style="color: white; background: #BA5BB2">fuchsia_pink:		#BA5BB2</div>
<div style="color: white; background: #C74E8A">mulberry:			#C74E8A</div>
<div style="color: white; background: #D4486B">cabaret:			    #D4486B</div>
