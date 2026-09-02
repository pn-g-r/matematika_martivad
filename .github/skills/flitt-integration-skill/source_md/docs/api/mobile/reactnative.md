
Use the [Flitt React Native](https://github.com/flittpayments/react-native) to start accepting Google Pay, Apple Pay and cards in your apps.

**Installation**

``` sh
npm install @flittpayments/react-native-flitt --save
# or
yarn add @flittpayments/react-native-flitt
```

###Android Setup

**1 Add lines to **android/settings.gradle**:**

``` java
include ':flittpayments_react-native-flitt'
project(':flittpayments_react-native-flitt').projectDir = new File(rootProject.projectDir, '../node_modules/@flittpayments/react-native-flitt/android')
```

**2 Add dependencies to **android/app/build.gradle**** 

``` java

dependencies {
    implementation project(':flittpayments_react-native-flitt')
    // Important: This specific version is required for GooglePayButton to work correctly
    implementation 'com.google.android.gms:play-services-wallet:19.4.0'
}

```

**3 MainApplication.java**

Register the package in your MainApplication.java file:

``` java
@Override
protected List<ReactPackage> getPackages() {
    @SuppressWarnings("UnnecessaryLocalVariable")
    List<ReactPackage> packages = new PackageList(this).getPackages();
    packages.add(new RNFlittPackage());
    return packages;
}
```


**4 Specify meta-data in AndroidManifest.xml**

``` xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />

<application ... >
<meta-data
android:name="com.google.android.gms.wallet.api.enabled"
android:value="true" />
        </application>
```

###iOS Setup

**1 Register as an Apple Developer**

To implement Apple Pay, you need to [Register Apple Merchant ID](/api/applepay-getting-started/#register-apple-merchant-id) and [Create Apple Pay certificates](/api/applepay-getting-started/#create-new-apple-pay-certificates)


**2 Configure Apple Pay in Xcode**

* In Xcode, select your project 
* Go to the "Signing & Capabilities" tab 
* Click "+ Capability" and add "Apple Pay"
* Add your Merchant ID to the Apple Pay section 
* Configure your payment processing certificate in the Apple Developer portal

**3 Update Info.plist**
Add the following to your Info.plist:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

** Check exaple folder on our GitHub on how to implement payments with cards and wallets**

- [Basic Usage](https://github.com/flittpayments/react-native#basic-usage)

- [card form](https://github.com/flittpayments/react-native/blob/master/Example/index.tsx)

- [Apple and Google Pay](https://github.com/flittpayments/react-native/blob/master/Example/ApplePayGpay.tsx)

** If you need Google and Apple Pay, refer to these articles:**

- [Apple Pay](/api/applepay-getting-started/)

- [Google Pay](/api/googlepay-getting-started/)