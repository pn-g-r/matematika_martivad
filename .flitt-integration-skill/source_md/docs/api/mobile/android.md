# Android SDK

Android SDK allows you to accept Google Pay payments from Android application.

The latest version of Android SDK you can always find in our public repository

[https://github.com/flittpayments/android-sdk](https://github.com/flittpayments/android-sdk)

In the [demo directory](https://github.com/flittpayments/android-sdk/tree/main/app/src/main/java/com/flitt/android/demo) you can find
an example of an application which implements Google Pay functionality

Also, you can refer the central Maven repository: [https://central.sonatype.com/search?q=flitt-android](https://central.sonatype.com/search?q=flitt-android)


=== "Java"

    **1 Initiate payment on backend and obtain payment token**
    
    Create order at your server:
        
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
    
    Receive payment token:
    
    ``` json    
        {
          "response":{
            "response_status":"success",
            "token":"b3c178ad84446ef36eaab365b1e12e6987e9b3d9"
          }
        }
    ```

    **2 Setup your application**

    Add dependencies to your project in app/build.gradle. This implementation requires Google Play services 17.0.0 or greater
    
    ``` java 
    implementation 'com.google.android.gms:play-services-base:17.0.0'
    implementation 'com.google.android.gms:play-services-wallet:19.4.0'
    implementation 'com.flitt:flitt-android:1.2.0'
    ```

    **3 Update AndroidManifest.xml to enable Google Pay API if required**

    Add the following lines:

    ``` java
    <uses-permission android:name="android.permission.INTERNET" />
    <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true"
    >
    ```
    For more information please follow Google Pay API [setup instruction](https://developers.google.com/pay/api/android/guides/setup)

    **4 Setup your MearchantId** 
    
    Create an instance of Cloudipsp with your MerchantID identifier from [Flitt Merchant Portal](https://portal.flitt.com)

    Attach webview, which will responsible for payer redirection to 3DSecure page
    
    ``` java
    webView = findViewById(R.id.web_view);
    cloudipsp = new Cloudipsp(<your merchant_id>, webView);
    ```

    **5 Process payment once payer sumbits data and card object is returned**

    Pass payment token from step 1 to method `payToken` 

    ```
    final Card card = getCard();
        if (card != null) {
           cloudipsp.payToken(card, token, this);
        }
    ```

    **6 Follow Demo folder on our GitHub to see examples on how to add card form to your application** 
    
    [https://github.com/flittpayments/android-sdk/tree/main/app/src/main/java/com/flitt/android/demo](https://github.com/flittpayments/android-sdk/tree/main/app/src/main/java/com/flitt/android/demo)

=== "Kotlin"

    **1 Initiate payment on backend and obtain payment token**
    
    Create order at your server:
        
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
    
    Receive payment token:
    
    ``` json    
        {
          "response":{
            "response_status":"success",
            "token":"b3c178ad84446ef36eaab365b1e12e6987e9b3d9"
          }
        }
    ```


    **2 Setup your application** 
    
    Add dependencies to your project in app/build.gradle.This implementation requires Google Play services 17.0.0 or greater

    
    ``` java
    implementation("com.google.android.gms:play-services-base:17.0.0")
    implementation("com.google.android.gms:play-services-wallet:19.4.0")
    implementation("com.flitt:flitt-android:1.2.0")
    ```

    **3 Update AndroidManifest.xml to enable Google Pay API if required.**

    ``` java
    <uses-permission android:name="android.permission.INTERNET" />
    <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true"
    >
    ```

    **4 Setup your MearchantId** 
    
    Create an instance of Cloudipsp with your MerchantID identifier from [Flitt Merchant Portal](https://portal.flitt.com)

    Attach webview, which will responsible for payer redirection to 3DSecure page
    
    ``` java
    webView = findViewById(R.id.web_view);
    cloudipsp = new Cloudipsp(<your merchant_id>, webView);
    ```

    **5 Process payment once payer sumbits data and card object is returned**

    Pass payment token from step 1 to method `payToken` 

    ```
    final Card card = getCard();
        if (card != null) {
           cloudipsp.payToken(card, token, this);
        }
    ```

    **6 Follow Demo folder on our GitHub to see examples on how to add card form to your application** 
    
    [https://github.com/flittpayments/android-sdk/tree/main/app/src/main/java/com/flitt/android/demo](https://github.com/flittpayments/android-sdk/tree/main/app/src/main/java/com/flitt/android/demo)
