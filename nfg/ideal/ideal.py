#!/usr/bin/python

#
# simple iDEAL python interface to the www.mollie.nl xmlrpc webservice
#
# based on ideal.class.php by Mollie BV
#
# license: GPLv3
#
# copyright 2009, NFG Net Facilities Group BV, www.nfg.nl
#
# Paul Stevens, paul@nfg.nl

import httplib, urllib, urlparse
import xml.etree.ElementTree as ET

class idealPayment:

    min_trans_amount = 118
    partner_id       = None
    testmode         = False

    bank_id          = None
    amount           = 0
    description      = None
    return_url       = None
    report_url       = None

    bank_url         = None
    transaction_id   = None
    paid_status      = False
    consumer_info    = {}

    def __init__(self, partner_id):
        self.setPartnerID(partner_id)

    def getBanks(self):
        xml = self._sendRequest('www.mollie.nl', '/xml/ideal/', 
            urllib.urlencode(dict(
                a="banklist",
                testmode=self.getTestmodeString())
                )
            )
        if not xml: return None
        r = {}
        for b in self._parse_xml(xml).getiterator('bank'): 
            r[b.find('bank_id').text] = b.find('bank_name').text
        return r

    def _parse_xml(self, xml):
        return ET.XML(xml)
        
    def getTestmodeString(self):
        if self.testmode: return "true"
        return "false" 

    def _sendRequest(self, host, path, data):
        conn = httplib.HTTPConnection(host)
        conn.request("POST", path, data, {'Content-type':'application/x-www-form-urlencoded'})
        return conn.getresponse().read()

    def createPayment(self, bank_id, amount, description, return_url, report_url):
        """
        @bank_id must be a valid Bank-ID, as returned by getBanks

        @amount is a number of cents (!!) to be payed.

        @description of the transaction as reported in the bank records. Max-length 
        is 30 characters (ascii).

        the @return_url is the landing page redirecting the client after iDEAL
        transaction has been completed.

        the @report_url is hit by mollie to allow the application developer
        to check and register the payment status. This url needs to be reachable
        by mollie of course.

        separating the payment checking from the @return_url page is a security 
        mechanism, not an enforced step. This means you can make it a dummy page, 
        or even a non-existing page. In that case, you can and should check the 
        payment status in the @return_url page, but caveat emptor!

        """
        self.setBankID(bank_id)
        self.setAmount(amount)
        self.setDescription(description)
        self.setReturnURL(return_url)
        self.setReportURL(report_url)
        xml = self._sendRequest('www.mollie.nl',
            '/xml/ideal/',
            urllib.urlencode(dict(
                a='fetch',
                partnerid=self.getPartnerID(),
                bank_id=self.getBankID(),
                amount=self.getAmount(),
                reporturl=self.getReportURL(),
                description=self.getDescription(),
                returnurl=self.getReturnURL(),
                )))
        if not xml: return False
        for b in self._parse_xml(xml).getiterator('order'):
            self.bank_url = b.find('URL').text
            self.transaction_id = b.find('transaction_id').text
        if self.bank_url and self.transaction_id: return True
        return False

    def checkPayment(self, transaction_id):
        self.setTransactionID(transaction_id)
        xml = self._sendRequest('www.mollie.nl',
            '/xml/ideal/',
            urllib.urlencode(dict(
                a='check',
                partnerid=self.getPartnerID(),
                transaction_id=self.getTransactionID(),
                )))
        if not xml: return False
        r = {}
        for b in self._parse_xml(xml).getiterator('order'):
            c =  b.find('consumer')
            self.amount = int(b.find('amount').text)
            self.payed_status = b.find('payed').text
            self.consumer_info['name'] = c.find('consumerName').text
            self.consumer_info['account'] = c.find('consumerAccount').text
            self.consumer_info['city'] = c.find('consumerCity').text

        if self.amount and self.payed_status: return True
        return False

### accessors:

    def setPartnerID(self, id):
        assert(type(id) == type(123))
        self.partner_id = id
    
    def getPartnerID(self):
        return self.partner_id

    def setBankID(self, id):
        assert(type(id) == type(123))
        self.bank_id = id

    def getBankID(self):
        return self.bank_id

    def setAmount(self, amount):
        assert(type(amount) == type(123))
        assert(self.min_trans_amount <= amount)
        self.amount = amount

    def getAmount(self):
        return self.amount

    def setDescription(self, description):
        self.description = description[:30]

    def getDescription(self):
        return self.description

    def setReturnURL(self, url):
        urlparse.urlparse(url)
        self.return_url = url

    def getReturnURL(self):
        return self.return_url

    def setReportURL(self, url):
        urlparse.urlparse(url)
        self.report_url = url

    def getReportURL(self):
        return self.report_url

    def setTransactionID(self, id):
        assert(id)
        self.transaction_id = id

    def getTransactionID(self):
        return self.transaction_id

    def getBankURL(self):
        return self.bank_url

    def getPaidStatus(self):
        return self.paid_status

    def getConsumerInfo(self):
        return self.consumer_info


