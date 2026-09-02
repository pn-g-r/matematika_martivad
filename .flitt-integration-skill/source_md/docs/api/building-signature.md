# Signature generation for request and response

## Signature algorithm

Parameter `signature` in [create order](/api/create-order/) request and response and in [callbacks](/api/callbacks/)
is generated with `sha1` function. `sha1` is applied to the string, which contains merchant payment secret key and all 
request or response parameters, concatenated in alphabetic order and separated by `|` symbol.

!!! example "Example"
    Merchant request:
    
    ``` sh  
    curl -i -X POST \
    -H "Content-Type:application/json" \
    -d \
    '{
    "request": {
    "server_callback_url": "http://myshop/callback/",
    "order_id": "TestOrder2",
    "currency": "GEL",
    "merchant_id": 1549901,
    "order_desc": "Test payment",
    "amount": 1000,
    "signature": "91ea7da493a8367410fe3d7f877fb5e0ed666490"
    }
    }' \
    'https://pay.flitt.com/api/checkout/url'
    ```

String used for signature build: 

``` bash
test|1000|GEL|1549901|Test payment|TestOrder2|http://myshop/callback/
``` 

Where `test` is payment secret key from [test data](/api/testing/)

If parameter is absent or is empty then there is no need to add `|` symbol.

Signature validation example for `response_url` and `server_callback_url` POST response:

=== "php"

    ``` php-inline
    namespace Ipsp;
    /**
     * Class Signature
       * @package Ipsp
       */
    class Signature {
          /**
           * @var
           */
          private static $password;
          /**
           * @var
           */
          private static $merchant;
          /**
           * Set merchant password
           * @param String $password
           * @return mixed
           */
          public static function password($password){
              self::$password = $password;
          }
          /**
           * Set merchant id
           * @param String $merchant
           * @return mixed
           */
          public static function merchant( $merchant ){
              self::$merchant = $merchant;
          }
          /**
           * Generate request params signature
           * @param array $params
           * @return string
           */
          public static function generate(Array $params){
              $params['merchant_id'] = self::$merchant;
              $params = array_filter($params,'strlen');
              ksort($params);
              $params = array_values($params);
              array_unshift( $params , self::$password );
              $params = join('|',$params);
              return(sha1($params));
          }
          /**
           * Sign params with signature
           * @param array $params
           * @return array
           */
          public static function sign(Array $params){
              if(array_key_exists('signature',$params)) return $params;
              $params['signature'] = self::generate($params);
              return $params;
          }
          /**
           * Clean array params
           * @param array $data
           * @return array
           */
          public static function clean(Array $data){
              if( array_key_exists('response_signature_string',$data) )
                  unset( $data['response_signature_string'] );
              unset( $data['signature'] );
              return $data;
          }
          /**
           * Check response params signature
           * @param array $response
           * @return bool
           */
          public static function check(Array $response){
              if(!array_key_exists('signature',$response)) return FALSE;
              $signature = $response['signature'];
              $response  = self::clean($response);
              return $signature == self::generate($response);
          }
    }
    ```

=== "python"

    ``` python
    from hashlib import sha1
    
    def get_signature(secret_key, params):
        """
        :param secret_key: merchant secret
        :param params: POST parameters
        :return: signature string
        """
        data = [secret_key]
        data.extend([str(params[key]) for key in sorted(iter(params.keys()))
                     if params[key] != '' and not params[key] is None
                     and key != 'signature'])
        return sha1('|'.join(data).encode('utf-8')).hexdigest()
    ```

## Solving problems with `signature` generation and validation 

There are two typical cases when the `signature` parameter verification error occurs.

### Case 1: in response to Flitt API call 

When request for the create order, reverse, get status or any other request with the parameter `signature` is
sent from merchant to the Flitt API, and the response  is returned: 

``` json
    {
        "response": {
            "error_code": 1014,
            "error_message": "Invalid signature",
            "request_id": "3mwpcKoenYZ0w",
            "response_status": "failure"
        }
    }
```
 
If the request is sent to the Flitt API, and the response is returned as `"error_message": "Invalid signature"`, 
perform the following checks:

- check that you used the correct payment secret key from the Technical Settings menu in the [Merchant Portal](https://portal.flitt.com):

- if the request contains non-Latin encoding, then it is sent in encoding UTF-8 

- make sure that a parameter with a value of 0 is not null by your programming language 

- log the line in the program code to which you apply SHA1 during the generation of the signature parameter. Compare it with the string that returned in the error text (marked in red):
`“Invalid signature signature: ``6bd069be8a6e2f2bbe176df00ba63cc681ca38aa``; response_signature_string: ``**********|125|GEL|1549901|demo order 789|Demo123456``“.` Note that in the text of the error
the merchant’s payment key will be masked with `*` symbol

- check if you send empty parameters in the API request. If yes, then in the line that participates in the signature, the
| separator symbol for each such empty parameter does not need to be included 

- if you are developing with the PHP programming language, use the example function 
[```php-inline public static function generate(Array $params)```](/api/building-signature/#__tabbed_1_1):

- make sure that the result of the SHA1 function is lowercase.
Correct: `6bd069be8a6e2f2bbe176df00ba63cc681ca38aa`. Incorrect: `6BD069BE8A6E2F2BBE176DF00BA63CC681CA38AA` 

- make sure that the signature parameter is not included in your signature calculation 

- make sure that if you use the API endpoint /api/recurring, then you only include the necessary parameters in the signature, 
but not those from the /api/redirect endpoint 

### Case 2: in callback to `server_callback_url` or redirect to `response_url`

When the Flitt server returned a POST response or callback to `server_callback_url` or `response_url` 
and you try to generate own signature and compare it with the `signature` parameter from the POST response, 
the `signatures` do not match 

If the Flitt API returned a POST response to the pages specified in the `server_callback_url` or `response_url`
parameters, but when you try to generate a signature and compare it with the signature parameter in the POST response,
the signature does not match 

=== "Response example from Flitt"

    ```json
    {
        "response": {
            "rrn": "",
            "masked_card": "",
            "sender_cell_phone": "",
            "sender_account": "",
            "currency": "GEL",
            "fee": "",
            "reversal_amount": "0",
            "settlement_amount": "0",
            "actual_amount": "",
            "response_description": "",
            "sender_email": "",
            "order_status": "expired",
            "response_status": "success",
            "order_time": "28.02.2018 19:18:16",
            "actual_currency": "",
            "order_id": "TestOrder2",
            "tran_type": "purchase",
            "eci": "",
            "settlement_date": "",
            "payment_system": "",
            "approval_code": "",
            "merchant_id": 1549901,
            "settlement_currency": "",
            "payment_id": 83456044,
            "card_bin": "",
            "response_code": "",
            "card_type": "",
            "amount": "1000",
            "signature": "268b8f189f97c85696134fe6ae0f7f5ab93f28d5",
            "product_id": "",
            "merchant_data": "",
            "rectoken": "",
            "rectoken_lifetime": "",
            "verification_status": "",
            "parent_order_id": "",
            "fee_oplata": "0",
            "additional_info": "{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": null, \"transaction_id\": null, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": null, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": null, \"card_product\": null, \"card_category\": null, \"timeend\": \"01.03.2018 05:18:17\", \"ipaddress_v4\": \"52.30.149.20\", \"payment_method\": null}",
            "response_signature_string": "**********|{\"capture_status\": null, \"capture_amount\": null, \"reservation_data\": null, \"transaction_id\": null, \"bank_response_code\": null, \"bank_response_description\": null, \"client_fee\": null, \"settlement_fee\": 0.0, \"bank_name\": null, \"bank_country\": null, \"card_type\": null, \"card_product\": null, \"card_category\": null, \"timeend\": \"01.03.2018 05:18:17\", \"ipaddress_v4\": \"52.30.149.20\", \"payment_method\": null}|1000|GEL|0|1549901|TestOrder2|expired|28.02.2018 19:18:16|83456044|success|0|0|purchase"
        }
    }
    ```

To diagnose the cause of a signature mismatch, follow these steps:

- make sure that the parameter with a value of 0 is not brought to empty or null in your programming language 
- make sure that the response_signature_string and signature parameters are not included in the signature calculation (the
response_signature_string parameter is returned only if the merchant is in test mode and contains hint how the signature
was formed in response)
- if the request contains non-Latin letters, then it is sent in UTF-8 
- in the program code, pledge a line to which you apply SHA1 during the formation of the signature parameter. 
Compare it with the string that returned in the `response_signature_string` parameter
- check if empty parameters are returned in the response. If yes, then in the string which participates in the signature,
it is not necessary to include the symbol separator | for each empty parameter 
- make sure that the result of the SHA1 function is lowercase.
Correct: `6bd069be8a6e2f2bbe176df00ba63cc681ca38aa`. Incorrect: `6BD069BE8A6E2F2BBE176DF00BA63CC681CA38AA`