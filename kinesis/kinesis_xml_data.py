# below is the sample data for consignment collector tdf(tgx)

cc_input_records = [
        {
        "input_record": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <connoteMsg id="TGEX123456_TDF">
                <connote action="UN">
                    <consignmentNumber>TGEX123456</consignmentNumber>
                    <actionDate>2025-05-21T11:00:00+10:00</actionDate>
                    <shipDate>2025-05-21T00:00:00+10:00</shipDate>
                    <senderAccount>123456</senderAccount>
                    <senderName>TestSender</senderName>
                    <senderAddress>
                        <addressLine1>123 Street</addressLine1>
                        <suburb>SYDNEY</suburb>
                        <state>NSW</state>
                        <country>AU</country>
                        <postCode>2000</postCode>
                    </senderAddress>
                    <receiverName>TestReceiver</receiverName>
                    <receiverAddress>
                        <addressLine1>456 Avenue</addressLine1>
                        <suburb>MELBOURNE</suburb>
                        <state>VIC</state>
                        <country>AU</country>
                        <postCode>3000</postCode>
                    </receiverAddress>
                    <serviceType>General</serviceType>
                    <mode>ROAD</mode>
                    <busunit>TEST</busunit>
                    <containsDangerousGoods>false</containsDangerousGoods>
                    <pickupManifestId>PM123456</pickupManifestId>
                    <totalItems>1</totalItems>
                    <totalWeight UOM="Kg">20</totalWeight>
                </connote>
                <srcSystem>TW</srcSystem>
                <origin>MYTOLL</origin>
            </connoteMsg>
        """
    },
    # ✅ Valid record with minimal XML
    {
    "input_record": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><connoteMsg id="2470399967_TDF"><connote action="UN"><consignmentNumber>2470399967</consignmentNumber><actionDate>2025-05-19T11:37:54+10:00</actionDate><shipDate>2025-05-19T00:00:00+10:00</shipDate><senderAccount>614060</senderAccount><senderName>TNQXSENWorkIng</senderName><senderAddress><addressLine1>245 Kevin Livingston Dr</addressLine1><suburb>ISIS CENTRAL</suburb><state>QLD</state><country>AU</country><postCode>4660</postCode></senderAddress><senderMobile>61-412345654</senderMobile><senderPhone>61-412345654</senderPhone><receiverName>TNQXRECVWorking</receiverName><receiverAddress><addressLine1>2 Metal Cct</addressLine1><suburb>MALAGA</suburb><state>WA</state><country>AU</country><postCode>6090</postCode></receiverAddress><receiverMobile>61-412345654</receiverMobile><receiverPhone>61-412345654</receiverPhone><involvedParties><partyRole>billTo</partyRole><partyAccount>614060</partyAccount><partyAddress><addressLine1>245 Kevin Livingston Dr</addressLine1><suburb>ISIS CENTRAL</suburb><state>QLD</state><country>AU</country><postCode>4660</postCode></partyAddress></involvedParties><totalPallets>0</totalPallets><totalItems>1</totalItems><totalCubic UOM="m3">0.001</totalCubic><totalWeight UOM="Kg">5</totalWeight><isFood>false</isFood><serviceType>General</serviceType><serviceCode>G</serviceCode><mode>ROAD</mode><busunit>TNQX</busunit><containsDangerousGoods>false</containsDangerousGoods><pickupManifestId>MYT1111997</pickupManifestId><notifications><milestones><milestone><name>PCKDUP</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>DELVERD</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>OUTFDL</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>SHPCRE</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>COLLCTD</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>PRTDEL</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>EXCEPTION</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>INTRNST</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone><milestone><name>AWTCOL</name><subscriberEmail><EMail>sundaradivya.ramalalitha@teamglobalexp.com</EMail><EMail>lalithalalli036@gmail.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail><EMail>saidileep.athimamula@hcltech.com</EMail></subscriberEmail><subscriberSMS><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-7993863656</MobileNumber><MobileNumber>91-9966271870</MobileNumber><MobileNumber>91-8639185908</MobileNumber><MobileNumber>91-9700746930</MobileNumber><MobileNumber>91-8800421412</MobileNumber><MobileNumber>91-9700746930</MobileNumber></subscriberSMS></milestone></milestones></notifications><additionalAttributes><attribName>atl</attribName><attribValue>false</attribValue></additionalAttributes><additionalAttributes><attribName>tesFlg</attribName><attribValue>false</attribValue></additionalAttributes><additionalAttributes><attribName>tesAmt</attribName><attribValue>0.0</attribValue></additionalAttributes><additionalAttributes><attribName>isGlencoreShipment</attribName><attribValue>false</attribValue></additionalAttributes><additionalAttributes><attribName>purchaseOrder</attribName><attribValue>PO</attribValue></additionalAttributes></connote><srcSystem>TW</srcSystem><origin>MYTOLL</origin></connoteMsg>"""
    },
    # ✅ Valid record with minimal XML
    {
    "input_record": """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><connoteMsg id="2470399974_TDF"><connote action="UN"><consignmentNumber>2470399974</consignmentNumber><actionDate>2025-05-19T12:16:35+10:00</actionDate><splInstructions>Special Instruction - Automation</splInstructions><shipDate>2025-05-19T00:00:00+10:00</shipDate><senderAccount>614060</senderAccount><senderName>Aarohi Agency</senderName><senderAddress><addressLine1>Lane A</addressLine1><addressLine2>Monforte Viennoiserie</addressLine2><suburb>PARLIAMENT HOUSE</suburb><state>SA</state><country>AU</country><postCode>5000</postCode></senderAddress><senderMobile>61-412345678</senderMobile><senderPhone>61-412345678</senderPhone><receiverName>GEETIKA</receiverName><receiverAddress><addressLine1>Address Line 1</addressLine1><addressLine2>Address Line 2</addressLine2><suburb>MELBOURNE WHARF</suburb><state>VIC</state><country>AU</country><postCode>3000</postCode></receiverAddress><receiverMobile>61-412345678</receiverMobile><receiverPhone>61-412345678</receiverPhone><involvedParties><partyRole>billTo</partyRole><partyAccount>614060</partyAccount><partyAddress><addressLine1>Lane A</addressLine1><addressLine2>Monforte Viennoiserie</addressLine2><suburb>PARLIAMENT HOUSE</suburb><state>SA</state><country>AU</country><postCode>5000</postCode></partyAddress></involvedParties><totalPallets>0</totalPallets><totalItems>1</totalItems><totalCubic UOM="m3">0.001</totalCubic><totalWeight UOM="Kg">50</totalWeight><isFood>false</isFood><serviceType>Express</serviceType><serviceCode>E</serviceCode><mode>ROAD</mode><busunit>TNQX</busunit><containsDangerousGoods>false</containsDangerousGoods><pickupManifestId>MYT1112000</pickupManifestId><notifications><milestones><milestone><name>PCKDUP</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>DELVERD</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>OUTFDL</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>SHPCRE</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>COLLCTD</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>PRTDEL</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>EXCEPTION</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>INTRNST</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone><milestone><name>AWTCOL</name><subscriberEmail><EMail>ats_normaluser@mailinator.com</EMail><EMail>ats_normaluser@mailinator.com</EMail></subscriberEmail></milestone></milestones></notifications><additionalAttributes><attribName>atl</attribName><attribValue>false</attribValue></additionalAttributes><additionalAttributes><attribName>tesFlg</attribName><attribValue>false</attribValue></additionalAttributes><additionalAttributes><attribName>tesAmt</attribName><attribValue>0.0</attribValue></additionalAttributes><additionalAttributes><attribName>isGlencoreShipment</attribName><attribValue>false</attribValue></additionalAttributes><additionalAttributes><attribName>purchaseOrder</attribName><attribValue>12345</attribValue></additionalAttributes></connote><srcSystem>TW</srcSystem><origin>MYTOLL</origin></connoteMsg>"""
    }
    
]

# below is the event collector tdf(tgx) data

ec_input_records = [
    # New data added below
    {
        "input_record": """<?xml version="1.0" encoding = "UTF-8" ?>
<eventMsg xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" consignmentNumber = "BCBL466193" consignmentId = "BCBL466193_PRIO">
    <srcSystem>PRIO</srcSystem>
    <event action = "UN">
        <type>item</type>
        <itemId>00693529785144661945</itemId>
        <eventCode>65</eventCode>
        <eventDescription>Transfer Out to C100</eventDescription>
        <itemCount>1</itemCount>
        <eventLocation>
            <addressLine1>PERTH DOMESTIC AIRPORT</addressLine1>
            <suburb>PERTH</suburb>
            <state>WA</state>
            <postCode>6104</postCode>
        </eventLocation>
        <businessUnit>PRIO</businessUnit>
        <eventDateTime>2025-01-21T19:59:11Z</eventDateTime>
        <eventTimezone>+08:00</eventTimezone>
        <alternateDeliveryPoint>
            <address>
                <addressLine1>Shop 5/760 Berrigan</addressLine1>
                <suburb>South Lake</suburb>
                <state>WA</state>
                <postCode>6164</postCode>
                <latitude>-32.111020</latitude>
                <longitude>115.839277</longitude>
            </address>
            <name>Freechoice South Lakes</name>
            <openingHours>Mon-Sun: 07:00-20:00</openingHours>
            <newsAgentCodeTP>C100</newsAgentCodeTP>
            <newsAgentCodeTF>C100</newsAgentCodeTF>
            <accepts>Standard</accepts>
        </alternateDeliveryPoint>
        <containerId/>
        <routeId>PER__FS5</routeId>
        <scanType>Physical</scanType>
    </event>
</eventMsg>"""
    },
]