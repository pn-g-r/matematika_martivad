# PCIDSS compliance

## PCIDSS RoC (Report on Compliance)

A Report on Compliance (ROC) tests the standards that are in place to protect the credit card information stored.
ROC & Quarterly External ASV Scans are required for all Level 1 Merchants. A Level 1 Merchant is a retailer that has more 
than 6 million annual transactions with Visa and/or Mastercard.

A Report on Compliance is a report documenting detailed results from a PCI DSS assessment. 
A ROC must be completed by a Qualified Security Assessor (QSA) after an audit, 
and subsequently submitted to the merchant’s acquirer. The acquirer, after accepting the ROC, sends it to the payment brand for verification.

## PCIDSS SAQ A, A-EP, D compliance

There are three Self-Assessment Questionnaire (SAQ) types within the new PCI DSS 4.0 standard available for e-commerce websites. 
They are titled A, A-EP (electronic processing), and D.

| Merchant level | No of transactions annually | Redirect | Iframe/Embedded | Direct POST | JavaScript | 	XML/JSON | 	Other |
|----------------|-----------------------------|----------|-----------------|-------------|------------|:----------|--------|
| 1	             | Over 6 million              | 	RoC^A^   | 	RoC^A^           | 	RoC^A-EP^    | 	RoC^A-EP^   | 	RoC	     | RoC    |
| 2	             | 1 – 6 million	              | SAQ A	   | SAQ A           | 	SAQ A-EP   | 	SAQ A-EP  | 	SAQ D    | 	SAQ D |
| 3	             | 20 000 – 1 million          | 	SAQ A	  | SAQ A           | 	SAQ A-EP   | 	SAQ A-EP  | 	SAQ D    | 	SAQ D |
| 4	             | Under 20 000	               | SAQ A	   | SAQ A           | 	SAQ A-EP   | 	SAQ A-EP  | 	SAQ D    | 	SAQ D |

RoC^A^ – Partial Report on Compliance validating the scope, eligibility, and requirements listed in SAQ A

RoC^A-EP^ – Partial Report on Compliance validating the scope, eligibility, and requirements listed in SAQ A-EP

To identify which type is required, the merchant should analyze several factors.


[![PCIDSS comliance]][PCIDSS comliance]{ width="400" align="left" }

  [PCIDSS comliance]: /static/img/pcidss.png


### SAQ A (not requested by Flitt)

If your website uses an iFrame or Hosted Page implementation, you will be responsible for complying with SAQ A. 
In this case, the user is taken to a payment page that is hosted by the service provider. This can be done by introducing a redirect, 
where the user is taken to another page (i.e., hosted page), or can happen on the same page in the form of an iFrame.

Please refer to description of 

- [hosted page (redirect)](/getting-started/redirect/) 
- [iFrame (embedded)](/getting-started/embedded/)
- [Interaction scheme A (with customer redirection to the payment page)](/api/payment-flow/#interaction-scheme-a-with-customer-redirection-to-payment-page)
- [Interaction scheme B (with host-to-host request to obtain payment page URL)](/api/payment-flow/#interaction-scheme-b-with-preliminary-host-to-host-request-to-get-payment-page-url)

### SAQ A-EP (not requested by Flitt)

If merchant web site is hosting credit card form, it is required to comply with SAQ A-EP. 

This SAQ is applied if merchant uses a [JavaScript](/getting-started/direct/) card form implementation. 

In either case, you are capturing the information via your own form, using actions and methods to push to an API. 

A solution like client-side encryption or tokenization can help merchants to comply with SAQ A-EP.

!!! note 
    Neither SAQ A nor SAQ A-EP allows a merchant to store or transmit credit card data through own servers and network. 
    All processing of cardholder data is outsourced to Flitt as a PCI DSS validated third-party payment processor.

[//]: # (You can find a description on how to use tokenization technology in our documentation here.)

### SAQ D  (requested by Flitt)

These are e-commerce firms that do not meet any of the criteria above. 
Service providers and merchants who do not meet the criteria for any of the above questionnaires.

SAQ D for Merchants applies to SAQ-eligible merchants not meeting the criteria for any other SAQ type. 
Examples of merchant environments that would use SAQ D may include but are not limited to:

- E-commerce merchants who accept cardholder data on their website.
- Merchants with electronic storage of cardholder data
- Merchants that don’t store cardholder data electronically but that do not meet the criteria of another SAQ type
- Merchants with environments that might meet the criteria of another SAQ type, but that have additional PCI DSS requirements applicable to their environment

### Recommendations for Flitt merchants

With SAQ A, D and A-EP you can use any Flitt integrations except [Direct](/getting-started/direct/) method:

- [Hosted Payment Page](/getting-started/redirect/)
- Payment buttons
- Payment links
- [Embedded](/getting-started/embedded/) checkout page
- [JavaScript SDK](/sdk-and-mobile/sdk/js/)
- [Apple Pay](/api/applepay-web/)
- [Google Pay](/api/googlepay-web/)

Direct method requires card data storage on merchant own server. In this case, PCI DSS RoC is mandatory:

Level 1: Merchants processing over 6 million card transactions per year.
Level 2: Merchants processing 1 to 6 million transactions per year.
Level 3: Merchants handling 20,000 to 1 million transactions per year.
Level 4: Merchants handling fewer than 20,000 transactions per year.

If you need to host credit card form on your site, but you do not have RoC, you can use [Embedded](/api/embedded-custom/) or [JavaScript SDK](/sdk-and-mobile/sdk/js/)
checkout page.