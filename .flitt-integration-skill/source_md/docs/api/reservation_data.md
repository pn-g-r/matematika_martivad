Additional parameter `reservation_data` can be sent with [create purchase](/api/order-parameters) request.

Example:

```json

{
  "request": {
    "response_url": "https://site.com/responsepage/",
    "order_id": "test_reservation_data_12345",
    "order_desc": "Test payment",
    "currency": "GEL",
    "amount": "100",
    "signature": "dcf5a9a582872bf0ba89bb77a25c3894671b423a",
    "merchant_id": "1549901",
    "reservation_data": "ewogICJwaG9uZW1vYmlsZSI6ICIrMTIzNDU2NzgiLAogICJjdXN0b21lcl9hZGRyZXNzIjogIjE1IGdhbm5ldCBzdHJlZXQgZWxzcGFyayIsCiAgImN1c3RvbWVyX2NvdW50cnkiOiAiVVMiLAogICJjdXN0b21lcl9zdGF0ZSI6ICJOWSIsCiAgImN1c3RvbWVyX25hbWUiOiAiQnJhbmRvbiBOeWF0aGkiLAogICJjdXN0b21lcl9jaXR5IjogIk5ldyBZb3JrIiwKICAiY3VzdG9tZXJfemlwIjogIjE0MDEiLAogICJhY2NvdW50IjogImlkMzI2NDg0ODAiCn0="
  }
}
 
```

`reservation_data` – it is JSON data, encoded with BASE64 algorithm. It has the following structure:

JSON:

```json

{
  "phonemobile": "+12345678",
  "customer_address": "15 gannet street elspark",
  "customer_country": "US",
  "customer_state": "NY",
  "customer_name": "Brandon Nyathi",
  "customer_city": "New York",
  "customer_zip": "1401",
  "account": "id32648480",
  "uuid": "00002415-0000-1000-8000-00805F9B34FB"
}
```

All parameters must be alphanumeric, and contain latin characters, digits and separator symbols

| Parameter name&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Mandatory| Type        | Description                                                                                   | Example                              |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|------------|-------------|-----------------------------------------------------------------------------------------------|--------------------------------------|
| `phonemobile`                                                                                                                                            | no | AN(16)      | Cllient mobile phone                                                                          | +12345678                            |
| `customer_address`                                                                                                                                       | no | AN(1024)    | Client address                                                                                | 15 gannet street elspark             |
| `customer_country`                                                                                                                                       | no | AN(2)       | Client billing country ISO  code                                                              | UK                                   |
| `customer_name`                                                                                                                                          | no | AN(1024)    | Payer name                                                                                    | Brandon Nyathi                       |
| `customer_city`                                                                                                                                          | no | AN(1024)    | Payer city                                                                                    | New York                             |
| `customer_zip`                                                                                                                                           | no | AN(250)     | ZIP code                                                                                      | 1401                                 |
| `account`                                                                                                                                                | no | AN(250)     | Client account id in merchant system                                                          | id32648480                           |
| `uuid`                                                                                                                                                   | no | AN(250)     | Device UUID                                                                                   | 00002415-0000-1000-8000-00805F9B34FB |
| `settlement_id`                                                                                                                                          | no | AN(32)      | ID to be passed to settlements reports for reconciliation process automation                  | SettlementID::12311233443            |
| `3ds_mandatory`                                                                                                                                          | no | boolean     | Parameter to force payment without 3DS. Can be used only after approval from Flitt risk team. | `true` or `false`                        |
| `fields_custom[]`                                                                                                                                        | no | JSON object | JSON list of additional fields to be displayed on checkout                                    |                                      |
| `products[]`                                                                                                                                             | no | JSON object | JSON list of products to be fiscalised                                                        |                                      |


`fields_custom` is a JSON object which allows to add custom input fields to checkout page

``` json

"fields_custom": [
    {
      "name": "id-1",
      "label": "label1",
      "value": "1",
      "valid": {
        "pattern": "^[0-9]+$",
        "max_length": 222,
        "min_length": 10
      },
      "readonly": false,
      "required": true,
      "type": "input",
      "p": 1
    },
    {
      "name": "id-2",
      "label": "label2",
      "value": "",
      "p": 2
    },
    {
      "name": "id-3",
      "label": "label3",
      "type": "checkbox",
      "required": true,
      "p": 3
    }
  ]
```


`products` is a JSON object which contains data to be fiscalised

``` json

    "products": [
        {
            "id": 1,
            "name": "Product A",
            "price": 100.00,
            "quantity": 2,
            "vat_percent": 20,
            "code": "00702001001000001",
            "units": 1,
            "discount": 10.00,
            "package_code": "5678",
            "total_amount": 190.00
        },
        {
            "id": 1,
            "name": "Product B",
            "price": 100.00,
            "quantity": 2,
            "vat_percent": 20,
            "code": "00702001001000001",
            "units": 1,
            "discount": 10.00,
            "package_code": "5679",
            "total_amount": 190.00
        }
    ]
```
Description of `products` JSON object:

| Parameter name&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; | Mandatory| Type  | Description                                               | Example           |
|----------------------------------------------------------------------------------------------------------------------------------------------------------|------------|-------|-----------------------------------------------------------|-------------------|
| `id`                                                                                                                                                     | no | number | ID of product                                             | 1                 |
| `discount`                                                                                                                                               | no | number     | Discount based on quantity of goods or services in tiyins | 100.20            |
| `name`                                                                                                                                                   | no | string | Product name                                              | Scooters rental   |
| `price`                                                                                                                                                  | no | number  | Price per unit of goods or services in tiyins             | 122.56            |
| `quantity`                                                                                                                                               | no | number | Quantity of goods or services                             | 2                 |
| `code`                                                                                                                                                   | no | number | Product and service identification code                   | 00702001001000001 |
| `units`                                                                                                                                                  | no | number | Unit code                                                 | 241092            |
| `vat_percent`                                                                                                                                            | no | number | Percentage of VAT paid for this product                   | 20                |
| `package_code`                                                                                                                                           | no | number | Product packaging code                                    | 123456            |
| `total_amount`                                                                                                                                          | no | number | Total amount of all products and services                 | 245.12            |
