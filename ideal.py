#!/usr/bin/python

#
# simple iDEAL python interface to the www.mollie.nl xmlrpc webservice
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
        et = self._parse_xml(xml)
        r = {}
        for b in et.getiterator('bank'):
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
        
        et = self._parse_xml(xml)
        for b in et.getiterator('order'):
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
 
        et = self._parse_xml(xml)
        r = {}
        for b in et.getiterator('order'):
            self.amount = int(b.find('amount').text)
            self.payed_status = b.find('payed').text
            consumer_info = {}
            c =  b.find('consumer')
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


if __name__ == '__main__':

    import cgi, unittest

    #partner_id = 999999 ## please use a valid partner ID

    class TestIdealPayment(unittest.TestCase):

        def setUp(self):
            self.c = idealPayment(partner_id)
            self.c.testmode = True

        def test_getBanks(self):
            b = self.c.getBanks()
            self.assertEqual(b, {'9999': 'TBM Bank'})

        def test_createPayment(self):
            r = self.c.createPayment(9999, 128, 'test payment', 'http://test.nfg.nl/ideal/return.php', 'http://test.nfg.nl/ideal/report.php')
            self.assert_(r)
            transaction_id = self.c.getTransactionID()
            url = self.c.getBankURL()
            self.assert_(transaction_id)
            self.assert_(url)
            url = urlparse.urlparse(url)
            purl = cgi.parse_qs(url.query)
            self.assert_(transaction_id in purl['transaction_id'])

        def test_checkPayment(self):
            # prepare payment
            r = self.c.createPayment(9999, 128, 'test payment', 'http://test.nfg.nl/ideal/return.php', 'http://test.nfg.nl/ideal/report.php')
            self.assert_(r)
            tid = self.c.getTransactionID()
            url = self.c.getBankURL()

            # confirm payment
            purl = urlparse.urlparse(url)
            conn = httplib.HTTPConnection(purl.netloc)
            conn.request("GET", url + '&payed=true')
            conn.getresponse().read()

            # check payment
            d = idealPayment(partner_id)
            d.testmode = True
            r = d.checkPayment(tid)
            self.assert_(r)
            self.assertEquals(d.consumer_info, {'city': 'Testdorp', 'account': '123456789', 'name': 'T. TEST'})


    if 'partner_id' in dir():
        unittest.main()
    else:
        print "Skipping unittests. Please specify a partner ID"
