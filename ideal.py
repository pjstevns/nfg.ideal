#!/usr/bin/python

import httplib
import xml.etree.ElementTree as ET
import unittest

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
    consumer_info    = None

    def __init__(self, partner_id):
        self.partner_id = partner_id

    def getBanks(self):
        xml = self._sendRequest('www.mollie.nl', '/xml/ideal/', 'a=banklist&testmode=%s' % self.getTestmodeString());
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

class TestIdealPayment(unittest.TestCase):

    def setUp(self):
        partner_id = 269845
        self.c = idealPayment(partner_id)
        self.c.testmode = True

    def test_getBanks(self):
        b = self.c.getBanks()
        self.assertEqual(b, {'9999': 'TBM Bank'})

if __name__ == '__main__':
    unittest.main()
