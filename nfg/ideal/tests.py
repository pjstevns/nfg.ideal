

import cgi
import unittest
import urlparse
import httplib
from ideal import idealPayment

partner_id = 9999999   # please use a valid partner ID
testsite = 'http://mysite.nl'
returnurl = '%s/ideal/return' % testsite
reporturl = '%s/ideal/report' % testsite


class TestIdealPayment(unittest.TestCase):

    def setUp(self):
        self.c = idealPayment(partner_id)
        self.c.testmode = True

    def test_getBanks(self):
        b = self.c.getBanks()
        self.assertEqual(b, {'9999': 'TBM Bank'})

    def test_createPayment(self):
        r = self.c.createPayment(9999, 128, 'test payment',
                                 returnurl, reporturl)
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
        r = self.c.createPayment(9999, 128, 'test payment',
                                 returnurl, reporturl)
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
        self.failUnless(r)
        self.assertEquals(d.consumer_info,
                          {'city': 'Testdorp', 'account': '0123456789',
                           'name': 'T. TEST'})

        # re-check
        r = d.checkPayment(tid)
        self.failIf(r)

if __name__ == '__main__':
    unittest.main()

#EOF
