To create subscription, please refer to comon instruction on how to [create order](/api/create-order/).

!!! warning "Pay attention"
    
    Subscription payments does not work for [Direct](/getting-started/direct/) integration type.
    
    Also, [Open Banking](/api/opb_intro/) method does not suport subscription yet.

    For enabling subscription payments for JavaScrip type of integration, please refer to [Embedded example with subscription](/api/embedded-custom/#example-with-subscription)


In order to create subscritpion, additional parameters must be sent in request to `/api/checkout/redirect`, `/api/checkout/token` or `/api/checkout/url` endpoints.

 

```json
{
  ...
  "subscription": "Y",
  "recurring_data": {
    "every": 5,
    "period": "day",
    "amount": 1000,
    "state": "Y",
    "readonly": "Y",
    "quantity": 100,
    "trial_period": "month",
    "trial_quantity": 1
  }
}
```


!!! note  "`recurring_data` properties description"
    
    |Property&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;| Default falue                                                   | Type&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;                                  | Description                                                                                                          |
    |--------|-----------------------------------------------------------------|----------------------------------------|----------------------------------------------------------------------------------------------------------------------|
    |`start_time`| Time of payment aproval                                         | Date in format `YYYY-MM-DD HH24:MI:SS` | Don't specify if you need to make forst charge not from a particular date, but from date of customer initial payment |
    |`end_time`| Time of payment aproval + quantity * period * every             | Date in format `YYYY-MM-DD HH24:MI:SS` | If not specified, it is calculated as the date of the last period, considering quantity, every and poeriod values    |
    |`amount`|  No default value, property is mandatory                              | Integer(12)                            | Amount of each schedulled charge. Amount without separator. 1020 (GEL) means 10 lari and 20 tetri                    |
    |`period`| No default value, property is mandatory                         | `day` or `week` or `month`               | Frequency, provided as on of the available values: `day`, `week`, `month`                                            |
    |`every`| No default value, property is mandatory                         | Integer(12)                            | Number of days, weeks, months between schedulled charges.                                                            |
    |`quantity`| No default value, either `quantity` or `end_time` must be specified | Integer(6)                             | Number of schedulled charges                                                                                         |
    |`trial_period`| Trial is disabled by default                                   | `day` or `week` or `month`               | Number of days, weeks, months for trial period between initial order approval and first scheduilled payment          |
    |`trial_quantity`| No default value, must be specifiedm if `trial_period` not empty  | Integer(12)                            | Number of trial periods, when customer is not charged                                                                |
    |`state`| Y                                                               | `y` or `Y` <br> `n` or `N` <br>`hidden` <br>`shown_readonly`                                   | Property to display or hide form with other properties on checkout page                                              |
    

!!! note  "`state` parameter can accept the following values:"


    | Value | Description                                                            |
    |-------|------------------------------------------------------------------------|
    | `y` or `y`   | Enable calendar on checkout page and allow client to disable it        |
    | `n` or `N`   | Disable calendar on checkout page and allow client to enable it        |
    | `hidden`   | Enable calendar on checkout page but do not show it to client          |
    | `shown_readonly`   | Enable calendar on checkout page and do not allow client to disable it |


!!! Code example   
    
    === "curl"

        ```bash
        curl -L 'https://pay.flitt.com/api/checkout/url' \
        -H 'Content-Type: application/json' \
        -d '{
          "request": {
            "order_id": "test_subscription5",
            "currency": "GEL",
            "merchant_id": 1549901,
            "order_desc": "Test payment",
            "amount": 100,
            "subscription": "Y",
            "recurring_data": {
              "every": 5,
              "period": "day",
              "amount": 1000,
              "state": "Y",
              "readonly": "Y",
              "quantity": 100,
              "trial_period": "month",
              "trial_quantity": 1
            },
            "signature": "4120ca8501b8003bb4860c6fc354c9e3ceb85d0c"
          }
        }'
        ```


    === "php"


        ```php

        <?php
        require_once '../configuration.php';
        require_once SDK_ROOTPATH . '/../vendor/autoload.php';
        
        
        //Payment subscription url scheme B(host-to-host)
        try {
          //Minimal data set, all other required params will generated automatically
          $data = [
              'currency' => 'GEL',
              'amount' => 1000, // convert to 10.00$
              'recurring_data' => [
                  'start_time' => '2021-12-24',
                  'amount' => 1000,
                  'every' => 30,
                  'period' => 'day',
                  'state' => 'y',
                  'readonly' => 'y'
              ]
        
          ];
          //Call method to generate url
          \Flitt\Configuration::setApiVersion('2.0'); //allow only json, api protocol 2.0
          $url = Flitt\Subscription::url($data);
          //getting returned data
          ?>
          <!doctype html>
          <html lang="en-US">
          <head>
              <meta charset="UTF-8">
              <title>Generate subscription Payment Url</title>
              <style>
                  table tr td, table tr th {
                      padding: 10px;
                  }
              </style>
          </head>
          <body>
          <table style="margin: auto;" border="1">
              <thead>
              <tr>
                  <th style="text-align: center" colspan="2">Request Data</th>
              </tr>
              <tr>
                  <th style="text-align: left"
                      colspan="2"><?php printf("<pre>%s</pre>", json_encode(['request' => $data], JSON_PRETTY_PRINT)) ?></th>
              </tr>
              </thead>
              <tbody>
              <tr>
                  <td>Payment id:</td>
                  <td><?= $url->getData()['payment_id'] ?></td>
              </tr>
              <tr>
                  <td>Normal response:</td>
                  <td>
                      <pre><?php print_r($url->getData()) ?></pre>
                  </td>
              </tr>
              <tr>
                  <td>Response subscription url:</td>
                  <td><a href="<?php print_r($url->getUrl()) ?>"><?php print_r($url->getUrl()) ?></a></td>
              </tr>
              </tbody>
          </table>
          </body>
          </html>
          <?php
        } catch (\Exception $e) {
          echo "Fail: " . $e->getMessage();
        }
        ```

    === "node.js"

        ```js
        'use strict'
        
        const FlittPay = require('../lib')
        const util = require('../lib/util')
        
        const flitt = new FlittPay(
          {
            merchantId: 1549901,
            secretKey: 'test'
          }
        )
        const date = new Date().toISOString().slice(0, 10)
        const OrderId = util.generateOrderId()
        
        const data = {
          order_desc: 'test order',
          order_id: OrderId,
          currency: 'GEL',
          amount: 1000,
          recurring_data:
          {
            every: 5,
            period: 'day',
            amount: 1000,
            start_time: date,
            state: 'y',
            Readonly: 'n'
          }
        }
        flitt.Subscription(data).then(data => {
          console.log(data)
        }).catch((error) => {
          console.log(error)
        })
        const StopData = {
          order_id: OrderId,
          action: 'stop'
        }
        
        flitt.SubscriptionActions(StopData).then(data => {
          console.log(data)
        }).catch((error) => {
          console.log(error)
        })
        ```

    === "c#"
    
        See:
        - [checkout_subscription.aspx](https://github.com/flittpayments/c-sharp-sdk/blob/main/FlittSDKSamples/checkout_subscription.aspx)
        - [checkout_subscription.aspx.cs](https://github.com/flittpayments/c-sharp-sdk/blob/main/FlittSDKSamples/checkout_subscription.aspx.cs)
        - [checkout_settlement.aspx.designer.cs](https://github.com/flittpayments/c-sharp-sdk/blob/main/FlittSDKSamples/checkout_settlement.aspx.designer.cs)

    