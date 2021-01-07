# Tasker

Tasker on sovellus, jonka on tarkoitus auttaa tehtävien hallinassa ja projektien tehtävien jakamisessa.

* Käyttäjä voi luoda projekteja ja luoda projekteihin liittyviä tehtäviä.
* Projekteilla on aina vähintään yksi tai useampi ylläpitäjä. Projektin luojasta tulee aluksi ylläpitäjä ja hän voi lisätä projektiin muita käyttäjiä, joille hän voi myös halutessaan antaa ylläpitäjän oikeudet halutessaan.
* Projektit näkyvät vain niille henkilöille, joille on annettu niihin pääsy.
* Myös sivulle luodut on käyttäjät jakautuvat joko ylläpitäjiin tai käyttäjiin.
* Tehtäviä voi luoda ja muokata. Lisäksi tehtäviä voi määritellä muiden projektiin kuuluvien henkilöiden tehtäväksi.


## Tunnistautuminen

Sovellusta pääsee käyttämään, kun on ensin tehnyt tilin ja varmentanut rekisteröitymisen yhteydessä antamansa sähköpostinsa. Tätä edellytetään siksi, että koko sivun ylläpito-oikeudet annetaan sille käyttäjälle, jonka sähköpostiosoite vastaa ympäristömuuttujissa ylläpitäjän sähköpostiksi määriteltyä osoitetta.

Sähköpostien lähettäminen Herokusta on vähintäänkin hankalaa ja välillä sähköpostien lähettäminen onnistuu hyvinkin ja välillä taas ei. Itse toteutin sähköpostien lähettämisen luomalla ylimääräisen gmail-tilin. Aina välillä Google saattaa estää Heroku-sovellusta lähettämästä sähköposteja, jolloin on käytävä tarkistamassa, pyytääkö Google tarkistamaan "epäilyttäviä tapahtumia". Välillä tämäkään ei riitä vaan on käytävä seuraavassa osoitteessa https://accounts.google.com/DisplayUnlockCaptcha hyväksymässä viimeaikaiset tapahtumat.