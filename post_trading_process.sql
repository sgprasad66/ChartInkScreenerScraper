SELECT * FROM chartinktradelog.dailytrades ;  24061400916125,24061201236671,24061401036812,24061401037801,24061401039785
delete from chartinktradelog.dailytrades where OrderId = '24061401209944';
ROLLBACK;
SELECT * FROM chartinktradelog.dailytrades
WHERE DailyTrades.OrderId = "24060700341058"

delete from chartinktradelog.dailytrades;

CREATE TABLE HISTORYDAILYTRADES LIKE chartinktradelog.dailytradeshistorydailytrades

INSERT INTO chartinktradelog.historydailytrades VALUES 

CREATE TABLE chartinktradelog.historydailytradesnew AS SELECT * FROM chartinktradelog.historydailytrades

SELECT * FROM chartinktradelog.historydailytradesnew

INSERT INTO chartinktradelog.historydailytradesnew
    SELECT *
    FROM dailytrades
    WHERE TpHit = 1 or SlHit = 1;

delete from chartinktradelog.dailytrades where TpHit = 1 or SlHit = 1;

UPDATE chartinktradelog.dailytrades SET TpHit=1 WHERE FinalPrice <= 6.0

UPDATE chartinktradelog.dailytrades SET Qty=600 WHERE OrderId = '24061400916125';

24061400184446=BEL

UPDATE chartinktradelog.dailytrades SET FinalPrice=8.60  WHERE OrderId = '24061400184446';