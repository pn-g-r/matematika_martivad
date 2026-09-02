## API general

All requests are sent over HTTPS with POST method.

Request and response format is JSON.

The response JSON structure is always a dict (associative array).

If the `err_code` or `error` key is present, the request is not completed. In this case, `err_code` and `error` parameter in response is a error description message.

Key error codes:

- `Authorization token required` – the `token` is not passed in the request header
- `Invalid auth token` – the `token` is either invalid or outdated
- `Merchant not found` – merchant not found
- `you have no access to this report` – either `report_id` is invalid or you have no access to the report

!!! example "Example of response in case of error"

    ```json
    {
       "error": "Authorization token required",
       "err_code": "Authorization token required"
    }
    ```

The authorization token must be sent in the `Authorization` HTTP header of your request. 

!!! example "Example of a request header with access token"

    ```sh
    curl 'https://portal.flitt.com/api/extend/company/report/' \
    -H "Authorization: Token 4cDY6LgviVN85g70eDHXygrmYTourFAT"
    ```

## Authentication

Before getting data from report, you need to obtain access token.

A JSON POST request should be sent to endpoint: https://portal.flitt.com/authorizer/token/application/get

!!! note  "Parameters of authentication request"
  
    | Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;	 | Mandatory| Type          | 	Description  | 	Example|
    |------------------|-----------|---------------|---------------|-----------|
    | `application_id` | 	mandatory    | string(20)    |	Company ID. Please contact Flitt support to obtain ID and secret key.|1234|
    | `date`           | mandatory     | 	string(1024) |	Date in any format. Date is a salt for sha512 signature hash|2020-04-06 11:15:27 or 1586171872 or any other string|
    | `signature`	     | mandatory     | string(128)   |	Signature|7eec02ed1088b47da639549a109c0e98<br/>a75e2d8c76dfa33db4ee18359b2ea677<br/>dda37516abc0e439b286261a48d49d3e<br/>2fd885d9f09c8ff5c7308afe4180688a|
     

The `signature` is formed by concatenating the application private key, application id, and date parameter through a vertical bar | (in utf-8 encoding). 

Sha512 hash function should be applied to the resulting string.

!!! Code "Code example of obtaining a signature"

    === "python"
    
        ```python
        from datetime import datetime
        import hashlib
        
        date = str(datetime.now())
        company_id = str(%your_company_id%)
        signature = hashlib.sha512('|'.join(['%your_company_private_key%', company_id, date]).encode('utf-8')).hexdigest()
        ```
    
    === "php"
    
        ```php
        <?php
        $date = strtotime("now");
        $company_id = %application_id%;
        $signature = hash('sha512', join('|',array('%your_company_private_key%', $company_id, $date)));
        ```

If request is successful, the token will be contained in the `token` parameter of the JSON response and will expire in 1 hour
Otherwise, the response will contain the keys `error_code` and `error_message`.



<div class="grid" markdown style="width:120%;">

!!! example "Example of curl request"

    ```bash
    curl 'https://portal.flitt.com/authorizer/token/application/get' \
        -H "Content-Type: application/json; charset=utf-8" \
        -X POST  --data-binary @- <<EOF
        {
            "signature": "5124cef4e69a015c1662f0ff963adc9f85ff60e365445ffcf6688737da726becb298211e5040c9ac74e3f56ff1065b42c281e300370436bec539f6b2679b91ee",
            "application_id": "2",
            "date": "2024-04-06 11:15:27"
        }
    EOF
    ```

<div markdown style="width:60%; margin-top: -22px;">

!!! example "Example of response in case of error"

    === "success response"
        ```json
        {
          "request_id": "SuVhZRMS7JDD2iGS",
          "token": "Yq0GXWeOZ1m8BsiCa4iQPDB84Wjw346",
          "expires_in": 3602
        }
        ```
    
    === "response with error"
    
        ```json
        {
          "error_code": 403,
          "error_message": "Incorrect signature",
          "request_id": "cGeC7PH59ESqQw30"
        }
        ``` 


</div>
</div>

##Obtain report data

The request should be sent as POST to the endpoint: https://portal.flitt.com/api/extend/company/report/

!!! example "Parameters of request of obtaining report data"

    === "Request parameters"
        
        |Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|	Mandaroty| Type            |	Description|	Example|
        |---------|----------|-----------------|------------|----------|
        |`filters`|mandatory| 	JSON objects[] |	A set of filters, individual within each report (report_id)|“filters”: [ { “s”: “settlement_date”, “m”: “dateis”, “v”: “2019-01-24” } ]|
        |`merchant_id`|mandatory| 	integer(12)    |	Merchant unique ID. Generated by Flitt during merchant registration.|1549901|
        |`report_id`|mandatory| 	integer(12)    |	Report unique ID (see List of available reports)|688|
        |`on_page`|mandatory|	integer(12)|	The limit of records that are returned in the context of single request (from 10 to 500 recommended)|500|
        |`page`|mandatory|	integer(12)|	Records page offset. For example, with on_page = 50, to get data from 51 to 100, you need to pass page = 2|2|
    
    === "Response parameters"
      
        |Parameter&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|	Mandaroty| Type            |	Description|	Example|
        |---------|----------|-----------------|------------|----------|
        |`data`|mandatory|	JSON objects[][]|	Dataset as a sorted two-dimensional JSON array|	“data”: [ [ 1234567890, 10000000001 ], [ 1234567891, 10000000002 ] ]|
        |`fields`|mandatory|	string[]|	List of returned fields|	“fields”: [ “payment_id”, “order_time”, “order_status”, “actual_amount”, “currency”, “fee”, “order_id”, “settlement_amount”, “settlement_currency”, “settlement_date”, “settlement_status”, “odb_ref”, “tran_time”, “settlement_type”, “payment_system”, “sender_email”, “order_desc”, “merchant_data”, “settlement_desc”, “transaction_id” ]|
        |`rows_count`|mandatory|	integer(12)|	Number of records in the full data set|	500|
        |`rows_on_page`|mandatory|	integer(12)|	Number of records returned in the context of this request|	50|
        |`rows_page`|mandatory|	integer(12)|	Range offset in the full data set. For example, if rows_on_page = 50 and rows_page = 2, then records from 51 to 100 are returned in the context of this request|	2|


!!! example "Example of request and response"

    === "Request"

        ```bash
        curl 'https://portal.flitt.com/api/extend/company/report/' \
        -H "Authorization: Token k1y0qXZ6KgO4GIfkeRlEznao0zbzYdhf" \
        -d @- << EOF
        {
          "on_page": 10,
          "page": 1,
          "filters": [
            {
              "s": "settlement_date",
              "m": "from",
              "v": "2019-01-24"
            },
            {
              "s": "settlement_date",
              "m": "to",
              "v": "2019-01-27"
            },
            {
              "s": "actual_amount",
              "m": "=",
              "v": "630.00"
            }
          ],
          "merchant_id": 1398432,
          "report_id": "403"
        }
        EOF
        ```

    === "Response"

        ```json
        {
          "data": [
            [
              1234567890,
              "2025-01-23 10:58:38",
              "approved",
              "630.00",
              "GEL",
              "11.97",
              "test-25697841-1",
              "618.03",
              "EUR",
              "2025-01-24 08:00:00",
              "completed",
              "2426012568",
              "2025-01-23 10:58:38",
              "purchase",
              "Visa/MC",
              "test@test.com",
              "Test order 1",
              "[]",
              "Test payment 1",
              10000000001
            ],
            [
              1234567891,
              "2025-01-23 10:56:51",
              "approved",
              "572.86",
              "GEL",
              "10.88",
              "test-94341241-1",
              "561.98",
              "EUR",
              "2025-01-24 08:00:00",
              "completed",
              "2426012568",
              "2025-01-23 10:56:51",
              "purchase",
              "Visa/MC",
              "test2@test.com",
              "Test order 2",
              "[]",
              "Test payment 2",
              10000000002
            ]
          ],
          "rows_count": 2,
          "fields": [
            "payment_id",
            "order_time",
            "order_status",
            "actual_amount",
            "currency",
            "fee",
            "order_id",
            "settlement_amount",
            "settlement_currency",
            "settlement_date",
            "settlement_status",
            "odb_ref",
            "tran_time",
            "settlement_type",
            "payment_system",
            "sender_email",
            "order_desc",
            "merchant_data",
            "settlement_desc",
            "transaction_id"
          ],
          "rows_page": 1,
          "rows_on_page": 10
        }
        ```
 

##Use filters

`filter` is an array of JSON objects.

Each `filter` object must contain following attributes:

**s** – field name, to which the filter is applied

**m** – search operand (=, <, > etc., depending on field type )

**v** – field value to be filtered

!!! example "Filter example"

    ```json
    [
        {
          "s": "settlement_date",
          "m": "dateis",
          "v": "2019-01-24"
        }
    ]
    ```

###Operands depending on field type

!!! example

    **float**: ‘=’, ‘>’, ‘<‘, ‘!=’, ‘isnull’, ‘notnull’

    **int**: ‘=’, ‘>’, ‘<‘, ‘!=’, ‘any’, ‘isnull’, ‘notnull’

    **date**: ‘dateis’, ‘from’, ‘to’, ‘isnull’, ‘notnull’, ‘notdate’

    **text**: ‘=’, ‘!=’, ‘like’, ‘!like’, ‘start’, ’empty’, ‘any’, ‘notnull’

    **bool**: istrue

    **select**: ‘=’, ‘!=’, ‘any’

    **array**: in_array

    **daterange**: ‘daterange’
 

###Unobvious search modes

!!! example

    **any**:
    
    ``` {“s”: “id”, “m”: “=”, “v”: “10,20,30”}``` – filter values specified with comma separator
    
    filter is applied as id in (10,20,30)
    
    **from**:
    
    ``` {“s”: “timestart”, “m”: “from”, “v”: “2020-01-10”}``` - filter is applied as timestart >= ‘2020-01-10’
    
    ``` {“s”: “timestart”, “m”: “from”, “v”: “-2”}``` - filter is applied as timestart >= now() – 2 days
    
    **to**:
    
    ``` {“s”: “timestart”, “m”: “to”, “v”: “2020-01-10”}``` - filter is applied as timestart < ‘2020-01-11‘
    
    **dateis** – “daye equal” – data filtered from specified day start (00:00) till next day start (00:00) (not including next day)
    
    **like** – filters partial fragment match
    
    **!like** – partial fragment must not match
    
    **start** – “starting from”

###List of available reports


!!! example "Parameters of request of obtaining report data"

      |Report ID|	Fields&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|	Mandatory filter fields|	Filter example|Description|	
      |---------|--------|-------|----------------|---|
      |500|`chargeback_createtime` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`tran_id` - integer(12)<br/>`sender_email` - string(1000)<br/>`status` - string(1000)<br/>`tran_timestart` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`tran_timeend` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`tran_type` - string(1000)<br/>`protocol` - string(1000)<br/>`currency` - string(3)<br/>`amount` - decimal(19,2)<br/>`payout_date` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`payout_amoun` - datetime(YYYY-MM-DD HH24:MI:SS)|`tran_id`<br/>OR<br/>`chargeback_createtime`|[<br/>{<br/> "on_page": 5,<br/> "page": 1,<br/> "filters": [<br/> {<br/> "s": "chargeback_createtime",<br/> "m": "from",<br/> "v": "2019-12-11"<br/> },<br/> {<br/> "s": "chargeback_createtime",<br/> "m": "to",<br/> "v": "2019-12-13"<br/> }<br/> ],<br/> "merchant_id": 1549901,<br/> "report_id": "500"<br/>}<br/>]<br/>|Chargebacks report|
      |528|`tran_id` - integer(12)<br/>`parent_tran_id` - integer(12)<br/>`sender_email` - string(1000)<br/>`status` - string(1000)<br/>`tran_timestart` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`tran_timeend` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`tran_type` - string(1000)<br/>`currency` - string(3)<br/>`actual_amount` - decimal(19,2)<br/>`payout_date` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`payout_amoun` - decimal(19,2)<br/>`order_desc` - string(1000)<br/>`checkout_url` - string(1000)|`tran_id`<br/>OR<br/>`tran_timestart`|[<br/>{<br/>  "on_page": 5,<br/>  "page": 1,<br/>  "filters": [<br/>    {<br/>      "s": "tran_timestart",<br/>      "m": "from",<br/>      "v": "2019-12-11"<br/>    },<br/>    {<br/>      "s": "tran_timeend",<br/>      "m": "to",<br/>      "v": "2019-12-13"<br/>    }<br/>  ],<br/>  "merchant_id": 1549901,<br/><br/>  "report_id": "528"<br/>}<br/>]<br/>|Success transactions report|
      |745|`payment_id` - integer(12)<br/>`order_timestart` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`order_timeend` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`order_status` - string(1000)<br/>`amount` - decimal(19,2)<br/>`actual_amount` - decimal(19,2)<br/>`transaction_id` - integer(19)<br/>`currency` - string(3)<br/>`actual_currency` - string(3)<br/>`order_type` - string(1000)<br/>`approval_code` - string(6)<br/>`card_bin` - string(6)<br/>`eci` - string(2)<br/>`fee` - decimal(19,2)<br/>`masked_card` - string(19)<br/>`order_id` - string(1000)<br/>`payment_system` - string(1000)<br/>`response_code` - integer(4)<br/>`response_description` - string(1000)<br/>`reversal_amount` - decimal(19,2)<br/>`rrn` - string(1000)<br/>`sender_email` - string(1000)<br/>`settlement_amount` - decimal(19,2)<br/>`settlement_currency` - string(3)<br/>`settlement_date` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`merchant_data` - string(1000)<br/>`order_desc` - string(1000)<br/>`payer_country` - string(1000)<br/>`bank_name` - string(1000)<br/>`bank_country` - string(3)<br/>`card_expire_date` - datetime(MM/YYYY)<br/>`card_brand` - string(1000)<br/>`fee_name` - string(1000)<br/>`fee_type` - string(1000)<br/>`fee_percent_value` - decimal(19,3)<br/>`fee_fix_value` - decimal(19,3)|`order_timestart`<br/>OR<br/>`order_timeend`<br/>OR<br/>`payment_id`<br/>OR<br/>`order_id`|[<br/>{<br/>  "on_page": 5,<br/>  "page": 1,<br/>  "filters": [<br/>    {<br/>      "s": "order_timestart_from",<br/>      "m": "dateis",<br/>      "v": "2026-05-01"<br/>    },<br/>    {<br/>      "s": "order_timestart_to",<br/>      "m": "dateis",<br/>      "v": "2026-05-04"<br/>    }<br/>  ],<br/>  "merchant_id": 1549901,<br/>  "report_id": "745"<br/>}<br/>]|All transactions report|
      |969|`payment_id` - integer(12)<br/>`tran_id` - integer(12)<br/>`order_id` - string(1000)<br/>`tran_timeend` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`actual_amount` - decimal(19,2)<br/>`settlement_currency` - string(3)<br/>`fee` - decimal(19,2)<br/>`settlement_amount` - decimal(19,2)<br/>`settlement_date` - datetime(YYYY-MM-DD HH24:MI:SS)<br/>`batch_id` - integer(12)<br/>`order_type` - string(1000)<br/>`order_status` - string(1000)<br/>`card_brand` - string(1000)<br/>`payment_system` - string(1000)<br/>`masked_card` - string(19)<br/>`rrn` - integer(12)<br/>`approval_code` - string(6)<br/>`order_desc` - string(1000)<br/>`merchant_data` - string(1000)<br/>`payer_country` - string(1000)<br/>`bank_name` - string(1000)<br/>`card_expire_date` - datetime(MM/YYYY)<br/>`card_brand` - string(1000)<br/>`fee_name` - string(1000)<br/>`fee_type` - string(1000)<br/>`fee_percent_value` - decimal(19,3)<br/>`fee_fix_value` - decimal(19,3)|`settlement_date`<br/>OR<br/>`tran_timeend`<br/>OR<br/>`payment_id`<br/>OR<br/>`order_id`|[<br/>{<br/>  "on_page": 5,<br/>  "page": 1,<br/>  "filters": [<br/>    {<br/>      "s": "settlement_date",<br/>      "m": "from",<br/>      "v": "2025-03-11"<br/>    },<br/>    {<br/>      "s": "settlement_date",<br/>      "m": "to",<br/>      "v": "2025-03-12"<br/>    }<br/>  ],<br/>  "merchant_id": 1549901,<br/>  "report_id": "969"<br/>}<br/>]|Reimbursement report|
