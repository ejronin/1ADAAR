"""Validate 4-hour snapshot storage and the refusal to synthesize price bars."""
import datetime as dt
import unittest
from src import gold_observations as mod

class GoldObservationTests(unittest.TestCase):
    def setUp(self):
        self.now = int(dt.datetime(2026, 10, 25, 16, tzinfo=dt.timezone.utc).timestamp()*1000)
        self.day = self.now - (self.now % mod.DAY_MS)

    def payload(self, price=862150):
        return {"latest": {"ts": self.day, "price":price},
                "points": [[self.day,price]]}

    def test_valid_quote(self):
        self.assertEqual(mod.validate(self.payload(),self.now),(self.day,862150))

    def test_old_quote_rejected(self):
        with self.assertRaises(ValueError):
            mod.validate({"latest":{"ts":self.day-3*mod.DAY_MS,"price":1200},
                          "points":[[self.day-3*mod.DAY_MS,1200]]},self.now)

    def test_mismatch_fails(self):
        with self.assertRaises(ValueError):
            mod.validate({"latest":{"ts":self.day,"price":9},
                          "points":[[self.day,8]]},self.now)

    def test_repeat_readings_keep_observed_times_and_do_not_make_hilo(self):
        state={}
        for hours in (0,4,8,12,16,20):
            ms=self.day+hours*3600000
            state=mod.append(state,ms,self.day,862150)
        readings=state["observations"]
        self.assertEqual(len(readings),6)
        self.assertEqual({r["price"] for r in readings},{862150})
        self.assertEqual({r["priceDay"] for r in readings},{self.day})
        self.assertEqual([r["observedAt"] for r in readings],
                         [self.day+h*3600000 for h in (0,4,8,12,16,20)])
        self.assertNotIn("high",state)
        self.assertNotIn("low",state)

    def test_retention_expires_and_missed_checks_not_imputed(self):
        stale=mod.append({},self.now-401*mod.DAY_MS,self.day-401*mod.DAY_MS,1234)
        result=mod.append(stale,self.now,self.day,862150)
        self.assertEqual(len(result["observations"]),1)
