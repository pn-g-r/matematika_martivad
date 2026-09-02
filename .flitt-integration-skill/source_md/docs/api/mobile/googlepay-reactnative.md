## Step by step instruction to implement Google Pay&trade; with React-Native

Use the [Flitt React-Native Android SDK](https://github.com/flittpayments/react-native) to start accepting Google Pay in your Android apps.

See example how to process Google Pay in [Flitt Github repo](https://github.com/flittpayments/react-native/blob/main/Example/ApplePayGpay.tsx)

**1 Installation**

``` sh
npm install @flittpayments/react-native-flitt --save
# or
yarn add @flittpayments/react-native-flitt
```

**2 Add lines to **android/settings.gradle**:**

``` java
include ':flittpayments_react-native-flitt'
project(':flittpayments_react-native-flitt').projectDir = new File(rootProject.projectDir, '../node_modules/@flittpayments/react-native-flitt/android')
```

**3 Add dependencies to **android/app/build.gradle**** 

``` java

implementation project(':flittpayments_react-native-flitt')
implementation 'com.google.android.gms:play-services-base:16.0.1'
implementation 'com.google.android.gms:play-services-wallet:16.0.1'
```

**4 Specify meta-data in AndroidManifest.xml**

``` xml
<application … >

  <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true"
  />

</application>
```

Required permission

``` xml
<uses-permission android:name="android.permission.INTERNET" />
```

**5 Make sure that Google Pay is supported on the device and user account**

``` java
import { Cloudipsp } from '@flittpayments/react-native-flitt';
const supportsGooglePay = await Cloudipsp.supportsGooglePay();
```

Function to check if the device supports Apple Pay or Google Pay:

``` java
// State to manage if the device supports Apple Pay or Google Pay
const [supportedPayments, setSupportedPayments] = useState({
   applePay:false,
   googlePay:false
});

const isSupportingAppleOrGPay = async () => {
    const isIOS = Platform.OS === 'ios';

    // Check for Apple Pay support on iOS devices
    if (isIOS) {
        const supportsApplePay = await Cloudipsp.supportsApplePay();
        if (supportsApplePay) {
            setSupportedPayments({ ...supportedPayments,applePay:true });
            return;
        }
        Alert.alert('Apple Pay is not supported on this device');
    }

    // Check for Google Pay support on Android devices
    const supportsGooglePay = await Cloudipsp.supportsGooglePay();
    if (supportsGooglePay) {
        setSupportedPayments( { ...supportedPayments, googlePay: true } );
        return;
    }
    Alert.alert('Google Pay is not supported on this device');
};

// useEffect to run the payment support check when the component mounts
useEffect(() => {
    isSupportingAppleOrGPay();
}, []);

```

**6 Initiate payment on backend and obtain payment token**

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


**7 Payment process**

``` java
import { CloudipspWebView } from '@flittpayments/react-native-flitt';

       // State to manage the visibility of the WebView
const [webView, setWebView] = useState(0);

// Reference to the Cloudipsp WebView component
const _cloudipspWebViewRef = useRef<CloudipspWebView>(null);
```

Function to initialize the Cloudipsp instance with the Merchant ID ( this function should be called inside `handleGooglePayPress` )
the second param of this class will be called inside `cloudipsp.googlePay(order)`

``` java
const _cloudipsp = (): Cloudipsp => {
    return new Cloudipsp(Merchant, (payConfirmator) => {
        setWebView(1); // Show the WebView for payment confirmation
        return payConfirmator(_cloudipspWebViewRef.current!);
    });
};
```

Process with googlePayToken function. Pass payment token, obtained in step 6 

``` java

// Function to handle the Google Pay button press
const handleGooglePayPressWithToken = async () => {

    const cloudipsp = _cloudipsp(); // Initialize the payment process with the merchant ID

    try {
        // Process the Google Pay transaction and return the receipt
        const receipt = await cloudipsp.googlePayToken('b3c178ad84446ef36eaab365b1e12e6987e9b3d9');
        setWebView(0); // Hide the WebView after payment processing
        console.log('Payment successful:', receipt);
    } catch (error) {
        // Handle payment errors
        console.error('Payment error:', error);
    }
};
```

Full code example can be found in [Flitt Github repo](https://github.com/flittpayments/react-native/blob/main/Example/ApplePayGpay.tsx)

##Google Pay mobile application approval

1. Before integrating Flitt mobile SDK, register merchant in Flitt [Merchant Portal](https://portal.flitt.com) 
and request Flitt support support@flitt.com to enable Google Pay on your account. You will get a merchant ID in test mode.

2. Build your app using Flitt merchant ID in test mode with Flitt SDK. Flitt SDK will use `ENVIRONMENT_TEST` mode and

    ```
    gatewayMerchantId: <your Flitt merchant_id>
    gatewayID: flitt
    ```

3. Follow instructions to request Google for production access: [https://developers.google.com/pay/api/android/guides/test-and-deploy/publish-your-integration](https://developers.google.com/pay/api/android/guides/test-and-deploy/publish-your-integration)
4. Google will review the application according to its integration checklist and provide recommendations if necessary.
5. If all requirements are met, production access is granted.
6. Request Flitt support to switch your merchant ID to live with `ENVIRONMENT_PRODUCTION` mode.
7. Submit production APK pointing to live merchant ID to Google for approval.