Android SDK allows you to accept Google Pay&trade; payments from Android application.

# Google Pay Android SDK

Android SDK allows you to accept Google Pay payments from Android application.

The latest version of Android SDK you can always find in our public repository

[https://github.com/flittpayments/android-sdk](https://github.com/flittpayments/android-sdk)

In the [demo directory](https://github.com/flittpayments/android-sdk/tree/main/app/src/main/java/com/flitt/android/demo) you can find
an example of an application which implements Google Pay functionality

Also, you can refer the central Maven repository: [https://central.sonatype.com/artifact/com.flitt/flitt-android](https://central.sonatype.com/artifact/com.flitt/flitt-android)
and use SDK as maven dependency.



=== "Java"

    **1 Setup your application**

    Add dependencies to your project in app/build.gradle. This implementation requires Google Play services 17.0.0 or greater
    
    ``` java 
    implementation 'com.google.android.gms:play-services-base:17.0.0'
    implementation 'com.google.android.gms:play-services-wallet:19.4.0'
    implementation 'com.flitt:flitt-android:1.2.0'
    ```

    **2 Update AndroidManifest.xml to enable Google Pay API.**

    Add the following lines:

    ``` java
    <uses-permission android:name="android.permission.INTERNET" />
    <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true"
    >
    ```
    For more information please follow Google Pay API [setup instruction](https://developers.google.com/pay/api/android/guides/setup)

    **3 Setup your MearchantId** 
    
    Create an instance of Cloudipsp with your MerchantID identifier from [Flitt Merchant Portal](https://portal.flitt.com)
    
    ``` java
    cloudipsp = new Cloudipsp(<your merchant_id>, webView);
    ```

    **4 Create Google Pay button in your application layout** 
    
    ``` java    
    <Button
        android:id="@+id/google_pay_button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Pay with Google Pay" />
    ```
    
    And add CloudIpspdWebView Component 
    
    ``` java    
    <com.flittpayments.android.CloudipspWebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:visibility="gone" 
    />
    ```
    
    **5 Implement the Activity.java file as follows:**  
    
    ``` java    
    import com.flittpayments.android.Cloudipsp
    
    Public class MainActivity extends AppCompatActivity implements
            View.OnClickListener, // Implementing OnClickListener for handling button clicks
            Cloudipsp.PayCallback, // Implementing Cloudipsp.PayCallback for payment callbacks
            Cloudipsp.GooglePayCallback { // Implementing Cloudipsp.GooglePayCallback for Google Pay callbacks
    
    }
    ```

    **6 Make sure that Google Pay is supported on the device and user account**
    
    ``` java
    googlePayButton = findViewById(R.id.google_pay_button); // Initialize Button from layout
    
    // Check if Google Pay is supported and set button visibility accordingly
    if (Cloudipsp.supportsGooglePay(this)) {
        googlePayButton.setVisibility(View.VISIBLE); // Show Google Pay button
    } else {
        googlePayButton.setVisibility(View.GONE); // Hide Google Pay button if unsupported
        Toast.makeText(this, R.string.e_google_pay_unsupported, Toast.LENGTH_LONG).show(); // Show unsupported message
    }
    ```

    **7 Initiate payment on backend and obtain payment token**
    
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


    **8 Add click listener on Google Pay button** 
    
    ``` java    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); // Set the layout for this activity
    
        // Initialize UI elements
        webView = findViewById(R.id.webView); // Initialize CloudipspWebView from layout
        googlePayButton = findViewById(R.id.google_pay_button); // Initialize Button from layout
    
        googlePayButton.setOnClickListener(this); // Set click listener for Google Pay button
    
        if (Cloudipsp.supportsGooglePay(this)) {
            googlePayButton.setVisibility(View.VISIBLE); 
        } else {
            googlePayButton.setVisibility(View.GONE); 
            Toast.makeText(this, R.string.e_google_pay_unsupported, Toast.LENGTH_LONG).show();
        }
    }
    
    @Override
    public void onClick(View v) {
        if (v.getId() == R.id.google_pay_button) {
            processGooglePay(); 
        }
    }
    ```
    
    **9 Process googlePay**

    Declare and initialize CloudipspWebView
    
    ``` java    
    private CloudipspWebView webView;
    ```

    Initialize CloudipspWebView from Layout
    
    ``` java    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); 
    
        webView = findViewById(R.id.webView); // Initialize CloudipspWebView 
    
    }
    ```
    
    Initialize Cloudipsp with 0 merchant ID and WebView (token instead of merchant ID will be taken from step 7)


    ``` java    
    private void processGooglePay() {
        cloudipsp = new Cloudipsp(0, webView);
    }
    ```
    
    Handle Google Pay initialization if needed
    
    ``` java    
    @Override
    public void onGooglePayInitialized(GooglePayCall result) {
        Toast.makeText(this, "Google Pay initialized", Toast.LENGTH_LONG).show(); // Show Google Pay initialization message
        this.googlePayCall = result; // Store Google Pay call result
    }
    ```
    
    Initiate the payment process, call method – `googlePayInitialize` with token

    ``` java
    if (Cloudipsp.supportsGooglePay(context)) {
        cloudipsp?.googlePayInitialize(
            paymentToken,
            context.findActivity(),
            MainActivity.RC_GOOGLE_PAY,
            googlePayCallback
        )
    }
    ```
    
    cloudipsp.googlePayInitialize get 4 params : paymentToken , activity , request code And Google Pay callback
    
    WebView 3DSecure confirmation
    
    After initiating the payment process, the configured 3DS WebView will open. In test mode, it should look like this : 

    ![Image title](/static/img/3dstest.jpg)

    Handle payment failure
    
    ``` java    
    @Override
    public void onPaidFailure(Cloudipsp.Exception e) {
        if (e instanceof Cloudipsp.Exception.Failure) {
            Cloudipsp.Exception.Failure f = (Cloudipsp.Exception.Failure) e;
            Toast.makeText(this, "Failure\nErrorCode: " +
                    f.errorCode + "\nMessage: " + f.getMessage() + "\nRequestId: " + f.requestId, Toast.LENGTH_LONG).show(); // Show specific failure details
        } else if (e instanceof Cloudipsp.Exception.NetworkSecurity) {
            Toast.makeText(this, "Network security error: " + e.getMessage(), Toast.LENGTH_LONG).show(); // Show network security error
        } else if (e instanceof Cloudipsp.Exception.ServerInternalError) {
            Toast.makeText(this, "Internal server error: " + e.getMessage(), Toast.LENGTH_LONG).show(); // Show internal server error
        } else if (e instanceof Cloudipsp.Exception.NetworkAccess) {
            Toast.makeText(this, "Network error", Toast.LENGTH_LONG).show(); // Show network access error
        } else {
            Toast.makeText(this, "Payment Failed", Toast.LENGTH_LONG).show(); // Show generic payment failure
        }
        e.printStackTrace(); // Print stack trace for debugging
    }
    ```    
    
    **10 Complete payment**

    Pass the result from onActivityResult to the SDK.
    
    ``` java    
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        switch (requestCode) {
            case RC_GOOGLE_PAY:
                if (!cloudipsp.googlePayComplete(resultCode, data, googlePayCall, this)) {
                    Toast.makeText(this, R.string.e_google_pay_canceled, Toast.LENGTH_LONG).show(); // Show payment canceled message
                }
                break;
        }
    }
    ```
    
    Handle Result of payment 
    
    ``` java
    @Override
    public void onPaidProcessed(Receipt receipt) {
        Toast.makeText(this, "Paid " + receipt.status.name() + "\nPaymentId:" + receipt.paymentId, Toast.LENGTH_LONG).show(); // Show payment success message
    }
    ```
    
    Handle back navigation 
    
    ``` java    
    @Override
    public void onBackPressed() {
        if (webView.waitingForConfirm()) {
            webView.skipConfirm(); // Skip confirmation in WebView if waiting
        } else {
            super.onBackPressed(); // Otherwise, perform default back button behavior
        }
    }
    ```
     
    If your activity is destroyed and recreated (e.g., due to a screen rotation), onSaveInstanceState() ensures that googlePayCall, 
    which is presumably a critical object related to payment processing, is saved (`putParcelable()`) and restored (`onRestoreInstanceState()`) properly.
    
    ``` java    
    private GooglePayCall googlePayCall; // <- this should be serialized on saving instance state
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main); // Set the layout for this activity
    
        if (savedInstanceState != null) {
            googlePayCall = savedInstanceState.getParcelable(K_GOOGLE_PAY_CALL);
        }
    }
    ```

    Save instance

    ``` java    
    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        outState.putParcelable(K_GOOGLE_PAY_CALL, googlePayCall);
    }
    ```

    Complete example of MainActivity code ( java )

    ``` java    
    package com.example.cloudipspAndroidSdkExampleJava;
    
    import android.content.Intent;
    import android.os.Bundle;
    import android.view.View;
    import android.widget.Button;
    import android.widget.Toast;
    
    import androidx.annotation.Nullable;
    import androidx.appcompat.app.AppCompatActivity;
    
    import com.flittpayments.android.Cloudipsp;
    import com.flittpayments.android.CloudipspWebView;
    import com.flittpayments.android.GooglePayCall;
    import com.flittpayments.android.Order;
    import com.flittpayments.android.Receipt;
    
    public class MainActivity extends AppCompatActivity implements
            View.OnClickListener, // Implementing OnClickListener for handling button clicks
            Cloudipsp.PayCallback, // Implementing Cloudipsp.PayCallback for payment callbacks
            Cloudipsp.GooglePayCallback { // Implementing Cloudipsp.GooglePayCallback for Google Pay callbacks
    
        private static final int RC_GOOGLE_PAY = 100500;
        private static final String K_GOOGLE_PAY_CALL = "google_pay_call";
        private Cloudipsp cloudipsp;
        private GooglePayCall googlePayCall; // <- this should be serialized on saving instance state
        private CloudipspWebView webView;
        private Button googlePayButton;
    
        @Override
        protected void onCreate(Bundle savedInstanceState) {
            super.onCreate(savedInstanceState);
            setContentView(R.layout.activity_main); // Set the layout for this activity
    
            // Initialize UI elements
            webView = findViewById(R.id.webView); // Initialize CloudipspWebView from layout
            googlePayButton = findViewById(R.id.google_pay_button); // Initialize Button from layout
            googlePayButton.setOnClickListener(this); // Set click listener for Google Pay button
    
            // Check if Google Pay is supported and set button visibility accordingly
            if (Cloudipsp.supportsGooglePay(this)) {
                googlePayButton.setVisibility(View.VISIBLE); // Show Google Pay button
            } else {
                googlePayButton.setVisibility(View.GONE); // Hide Google Pay button if unsupported
                Toast.makeText(this, R.string.e_google_pay_unsupported, Toast.LENGTH_LONG).show(); // Show unsupported message
            }
    
            if (savedInstanceState != null) {
                googlePayCall = savedInstanceState.getParcelable(K_GOOGLE_PAY_CALL);
            }
        }
    
        @Override
        public void onBackPressed() {
            if (webView.waitingForConfirm()) {
                webView.skipConfirm(); // Skip confirmation in WebView if waiting
            } else {
                super.onBackPressed(); // Otherwise, perform default back button behavior
            }
        }
    
    
        @Override
        public void onClick(View v) {
            if (v.getId() == R.id.google_pay_button) {
                processGooglePay(); // Handle click on Google Pay button
            }
        }
    
        private void processGooglePay() {
            cloudipsp = new Cloudipsp(0, webView);
        }

        @Override
        protected void onSaveInstanceState(Bundle outState) {
            super.onSaveInstanceState(outState);
            outState.putParcelable(K_GOOGLE_PAY_CALL, googlePayCall);
        }
    
        @Override
        protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
            super.onActivityResult(requestCode, resultCode, data);
            switch (requestCode) {
                case RC_GOOGLE_PAY:
                    if (!cloudipsp.googlePayComplete(resultCode, data, googlePayCall, this)) {
                        Toast.makeText(this, R.string.e_google_pay_canceled, Toast.LENGTH_LONG).show(); // Show payment canceled message
                    }
                    break;
            }
        }
    
        @Override
        public void onPaidProcessed(Receipt receipt) {
            Toast.makeText(this, "Paid " + receipt.status.name() + "\nPaymentId:" + receipt.paymentId, Toast.LENGTH_LONG).show(); // Show payment success message
        }
    
        @Override
        public void onPaidFailure(Cloudipsp.Exception e) {
            if (e instanceof Cloudipsp.Exception.Failure) {
                Cloudipsp.Exception.Failure f = (Cloudipsp.Exception.Failure) e;
                Toast.makeText(this, "Failure\nErrorCode: " +
                        f.errorCode + "\nMessage: " + f.getMessage() + "\nRequestId: " + f.requestId, Toast.LENGTH_LONG).show(); // Show specific failure details
            } else if (e instanceof Cloudipsp.Exception.NetworkSecurity) {
                Toast.makeText(this, "Network security error: " + e.getMessage(), Toast.LENGTH_LONG).show(); // Show network security error
            } else if (e instanceof Cloudipsp.Exception.ServerInternalError) {
                Toast.makeText(this, "Internal server error: " + e.getMessage(), Toast.LENGTH_LONG).show(); // Show internal server error
            } else if (e instanceof Cloudipsp.Exception.NetworkAccess) {
                Toast.makeText(this, "Network error", Toast.LENGTH_LONG).show(); // Show network access error
            } else {
                Toast.makeText(this, "Payment Failed", Toast.LENGTH_LONG).show(); // Show generic payment failure
            }
            e.printStackTrace(); // Print stack trace for debugging
        }
    
        @Override
        public void onGooglePayInitialized(GooglePayCall result) {
            // Handle Google Pay initialization if needed
            Toast.makeText(this, "Google Pay initialized", Toast.LENGTH_LONG).show(); // Show Google Pay initialization message
            this.googlePayCall = result; // Store Google Pay call result
        }
    }
    ```

=== "Kotlin"

    **1 Setup your application** 
    
    Add dependencies to your project in app/build.gradle.This implementation requires Google Play services 17.0.0 or greater

    
    ``` java
    implementation("com.google.android.gms:play-services-base:17.0.0")
    implementation("com.google.android.gms:play-services-wallet:19.4.0")
    implementation("com.flittpayments:android:+")
    ```

    **2 Update AndroidManifest.xml to enable Google Pay API.**

    ``` java
    <uses-permission android:name="android.permission.INTERNET" />
    <meta-data
        android:name="com.google.android.gms.wallet.api.enabled"
        android:value="true"
    >
    ```

    **3 Setup your MearchantId** 
    
    Create an instance of Cloudipsp with your MerchantID identifier from [Flitt Merchant Portal](https://portal.flitt.com)

    ``` java
    cloudipsp = new Cloudipsp(<your merchant_id>, webView);
    ```

    **4 Create Google Pay button in your application layout** 
    
    ``` java    
    <Button
        android:id="@+id/google_pay_button"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Pay with Google Pay" />
    ```
    
    And add CloudIpspdWebView Component 
    
    ``` java    
    <com.flittpayments.android.CloudipspWebView
        android:id="@+id/webView"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        android:visibility="gone" 
    />
    ```
    
    **5 Implement the Activity.kt file as follows**
    
    ``` java    
    import com.flittpayments.android.Cloudipsp
    class MainActivity : AppCompatActivity(), View.OnClickListener, Cloudipsp.PayCallback, Cloudipsp.GooglePayCallback {
    }
    ```

    **6 Make sure that Google Pay is supported on the device and user account**
    
    ``` java
    googlePayButton = findViewById(R.id.google_pay_button); // Initialize Button from layout
    
    // Check if Google Pay is supported and set button visibility accordingly
    if (Cloudipsp.supportsGooglePay(this)) {
        googlePayButton.setVisibility(View.VISIBLE); // Show Google Pay button
    } else {
        googlePayButton.setVisibility(View.GONE); // Hide Google Pay button if unsupported
        Toast.makeText(this, R.string.e_google_pay_unsupported, Toast.LENGTH_LONG).show(); // Show unsupported message
    }
    ```
    
    
    **7 Initiate payment on backend and obtain payment token**
    
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
    
    **8 Add click listener on Google Pay button**
    
    ``` java  
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // Set the layout for this activity
    
        // Initialize UI elements
        webView = findViewById(R.id.webView) // Initialize CloudipspWebView from layout
        googlePayButton = findViewById(R.id.google_pay_button) // Initialize Button from layout
        googlePayButton.setOnClickListener(this) // Set click listener for Google Pay button
    
        // Check if Google Pay is supported and set button visibility accordingly
        if (Cloudipsp.supportsGooglePay(this)) {
            googlePayButton.visibility = View.VISIBLE // Show Google Pay button
        } else {
            googlePayButton.visibility = View.GONE // Hide Google Pay button if unsupported
            Toast.makeText(this, R.string.e_google_pay_unsupported, Toast.LENGTH_LONG).show() // Show unsupported message
        }
    }
    
    override fun onClick(v: View) {
        if (v.id == R.id.google_pay_button) {
            processGooglePay() // Handle click on Google Pay button
        }
    }
    ```
    
    **9 Process googlePay** 

    Declare and initialize CloudipspWebView
    
    ``` java
    private lateinit var webView: CloudipspWebView
    ```
    
    Initialize CloudipspWebView from Layout
    
    ``` java    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // Set the layout for this activity
        webView = findViewById(R.id.webView) // Initialize CloudipspWebView from layout
    }
    ```
    
    Initialize Cloudipsp with 0 merchant ID and WebView (token instead of merchant ID will be taken from step 7)
    
    ``` java    
    private fun processGooglePay() {
        cloudipsp = Cloudipsp(0, webView) 
    }
    ```
    
    Handle Google Pay initialization if needed
    
    ``` java    
    override fun onGooglePayInitialized(result: GooglePayCall) {
        // Handle Google Pay initialization if needed
        Toast.makeText(this, "Google Pay initialized", Toast.LENGTH_LONG).show() // Show Google Pay initialization message
        googlePayCall = result // Store Google Pay call result
    }
    ```
    
    Initiate the payment process, call method – `googlePayInitialize` with token 
    
    ``` java    
    if (Cloudipsp.supportsGooglePay(context)) {
        cloudipsp?.googlePayInitialize(
            paymentToken,
            context.findActivity(),
            MainActivity.RC_GOOGLE_PAY,
            googlePayCallback
        )
    }
    ```
    cloudipsp.googlePayInitialize get 4 params : paymentToken , activity , request code And Google Pay callback

    WebView 3DSecure confirmation
    
    After initiating the payment process, the configured 3DS WebView will open. In test mode, it should look like this : 

    ![Image title](/static/img/3dstest.jpg)
    
    Handle payment failure
    
    ``` java    
    override fun onPaidFailure(e: Cloudipsp.Exception) {
        when (e) {
            is Cloudipsp.Exception.Failure -> {
                Toast.makeText(this, "Failure\nErrorCode: ${e.errorCode}\nMessage: ${e.message}\nRequestId: ${e.requestId}", Toast.LENGTH_LONG).show() // Show specific failure details
            }
            is Cloudipsp.Exception.NetworkSecurity -> {
                Toast.makeText(this, "Network security error: ${e.message}", Toast.LENGTH_LONG).show() // Show network security error
            }
            is Cloudipsp.Exception.ServerInternalError -> {
                Toast.makeText(this, "Internal server error: ${e.message}", Toast.LENGTH_LONG).show() // Show internal server error
            }
            is Cloudipsp.Exception.NetworkAccess -> {
                Toast.makeText(this, "Network error", Toast.LENGTH_LONG).show() // Show network access error
            }
            else -> {
                Toast.makeText(this, "Payment Failed", Toast.LENGTH_LONG).show() // Show generic payment failure
            }
        }
        e.printStackTrace() // Print stack trace for debugging
    }
    ```
    
    **10 Complete payment** 

    Pass the result from onActivityResult to the SDK.
    
    ``` java
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        when (requestCode) {
            RC_GOOGLE_PAY -> {
                if (!cloudipsp?.googlePayComplete(resultCode, data, googlePayCall, this)!!) {
                    Toast.makeText(this, R.string.e_google_pay_canceled, Toast.LENGTH_LONG).show() // Show payment canceled message
                }
            }
        }
    }
    ```
    
    
    Handle Result of payment 
    
    ``` java    
    override fun onPaidProcessed(receipt: Receipt) {
        Toast.makeText(this, "Paid ${receipt.status.name}\nPaymentId:${receipt.paymentId}", Toast.LENGTH_LONG).show() // Show payment success message
    }
    ```
    
    Handle back navigation 

    ``` java    
    override fun onBackPressed() {
        if (webView.isWaitingForConfirm) {
            webView.skipConfirm() // Skip confirmation in WebView if waiting
        } else {
            super.onBackPressed() // Otherwise, perform default back button behavior
        }
    }
    ```
    
    Save instance
    
    ``` java    
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putParcelable(K_GOOGLE_PAY_CALL, googlePayCall)
    }
    ```

    Complete example of MainActivity code
    
    ``` java
    package com.example.cloudipspAndroidSdkExampleKotlin
    
    import android.content.Intent
    import android.os.Bundle
    import android.view.View
    import android.widget.Button
    import android.widget.Toast
    import androidx.appcompat.app.AppCompatActivity
    import com.flittpayments.android.Cloudipsp
    import com.flittpayments.android.CloudipspWebView
    import com.flittpayments.android.GooglePayCall
    import com.flittpayments.android.Order
    import com.flittpayments.android.Receipt
    
    class MainActivity : AppCompatActivity(), View.OnClickListener, Cloudipsp.PayCallback, Cloudipsp.GooglePayCallback {
    
        private val RC_GOOGLE_PAY = 100500
        private val K_GOOGLE_PAY_CALL = "google_pay_call"
        private var cloudipsp: Cloudipsp? = null
        private var googlePayCall: GooglePayCall? = null // <- this should be serialized on saving instance state
        private lateinit var webView: CloudipspWebView
        private lateinit var googlePayButton: Button
    
        override fun onCreate(savedInstanceState: Bundle?) {
            super.onCreate(savedInstanceState)
            setContentView(R.layout.activity_main) // Set the layout for this activity
    
            // Initialize UI elements
            webView = findViewById(R.id.webView) // Initialize CloudipspWebView from layout
            googlePayButton = findViewById(R.id.google_pay_button) // Initialize Button from layout
            googlePayButton.setOnClickListener(this) // Set click listener for Google Pay button
    
            // Check if Google Pay is supported and set button visibility accordingly
            if (Cloudipsp.supportsGooglePay(this)) {
                googlePayButton.visibility = View.VISIBLE // Show Google Pay button
            } else {
                googlePayButton.visibility = View.GONE // Hide Google Pay button if unsupported
                Toast.makeText(this, R.string.e_google_pay_unsupported, Toast.LENGTH_LONG).show() // Show unsupported message
            }
            if (savedInstanceState != null) {
                googlePayCall = savedInstanceState.getParcelable(K_GOOGLE_PAY_CALL)
            }
        }
    
        override fun onBackPressed() {
            if (webView.waitingForConfirm()) {
                webView.skipConfirm() // Skip confirmation in WebView if waiting
            } else {
                super.onBackPressed() // Otherwise, perform default back button behavior
            }
        }
    
        override fun onClick(v: View) {
            if (v.id == R.id.google_pay_button) {
                processGooglePay() // Handle click on Google Pay button
            }
        }
    
    
        if (Cloudipsp.supportsGooglePay(context)) {
            cloudipsp?.googlePayInitialize(
                paymentToken,
                context.findActivity(),
                MainActivity.RC_GOOGLE_PAY,
                googlePayCallback
            )
        }
        override fun onSaveInstanceState(outState: Bundle) {
            super.onSaveInstanceState(outState)
            outState.putParcelable(K_GOOGLE_PAY_CALL, googlePayCall)
        }
    
        override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
            super.onActivityResult(requestCode, resultCode, data)
            when (requestCode) {
                RC_GOOGLE_PAY -> {
                    if (!cloudipsp?.googlePayComplete(resultCode, data, googlePayCall, this)!!) {
                        Toast.makeText(this, R.string.e_google_pay_canceled, Toast.LENGTH_LONG).show() // Show payment canceled message
                    }
                }
            }
        }
    
        override fun onPaidProcessed(receipt: Receipt) {
            Toast.makeText(this, "Paid ${receipt.status.name}\nPaymentId:${receipt.paymentId}", Toast.LENGTH_LONG).show() // Show payment success message
        }
    
        override fun onPaidFailure(e: Cloudipsp.Exception) {
            when (e) {
                is Cloudipsp.Exception.Failure -> {
                    Toast.makeText(this, "Failure\nErrorCode: ${e.errorCode}\nMessage: ${e.message}\nRequestId: ${e.requestId}", Toast.LENGTH_LONG).show() // Show specific failure details
                }
                is Cloudipsp.Exception.NetworkSecurity -> {
                    Toast.makeText(this, "Network security error: ${e.message}", Toast.LENGTH_LONG).show() // Show network security error
                }
                is Cloudipsp.Exception.ServerInternalError -> {
                    Toast.makeText(this, "Internal server error: ${e.message}", Toast.LENGTH_LONG).show() // Show internal server error
                }
                is Cloudipsp.Exception.NetworkAccess -> {
                    Toast.makeText(this, "Network error", Toast.LENGTH_LONG).show() // Show network access error
                }
                else -> {
                    Toast.makeText(this, "Payment Failed", Toast.LENGTH_LONG).show() // Show generic payment failure
                }
            }
            e.printStackTrace() // Print stack trace for debugging
        }
    
        override fun onGooglePayInitialized(result: GooglePayCall) {
            // Handle Google Pay initialization if needed
            Toast.makeText(this, "Google Pay initialized", Toast.LENGTH_LONG).show() // Show Google Pay initialization message
            googlePayCall = result // Store Google Pay call result
        }
    }
    ```

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