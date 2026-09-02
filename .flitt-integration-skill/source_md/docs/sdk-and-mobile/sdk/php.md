# PHP SDK

PHP SDK allows you to accept payment with Visa/MasterCard cards on your website.

Lates version of PHP SDK you can always find in our public repository:

[https://github.com/flittpayments/php-sdk](https://github.com/flittpayments/php-sdk)

SDK documentation:

[https://flittpayments.github.io/php-docs/](https://flittpayments.github.io/php-docs/)



=== "Usage example"

    **Composer installation**
    ```bash
    composer require flittpayments/php-sdk
    ```
    **Manual installation**
    ```bash
    git clone -b master https://github.com/flittpayments/php-sdk.git
    ```

    **Simple Start**

    ```php-inline

    require 'vendor/autoload.php';
    \Flitt\Configuration::setMerchantId(1549901);
    \Flitt\Configuration::setSecretKey('test');
    
    $checkoutData = [
        'currency' => 'GEL',
        'amount' => 1000
    ];
    $data = \Flitt\Checkout::url($checkoutData);
    $url = $data->getUrl();
    //$data->toCheckout() - redirect to checkout
    ```
    
    **Example**

    ```bash
    cd ~/php-sdk
    php -S localhost:8000
    ```

    [Checkout example](https://github.com/flittpayments/php-sdk/tree/master/examples)
