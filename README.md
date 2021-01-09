# Tasker

Tasker on tiimipohjainen Kanban-palvelu, jota voi hyödyntää esimerkiksi tiimin tehtävien hallinnassa ja tiimin jäsenten välisessä työnjaossa. Käyttäjät voivat luoda tiimejä vapaasti ja kutsua tiimiinsä muita käyttäjiä tiiminsä jäseniksi. 

Tiimejä voi luoda mihin tarkoitukseen tahansa - esimerkiksi projektikohtaisesti tai pysyvämpien tiimien tehtävienhallintaan. Palvelun käyttäjät – sivuston ylläpitäjiä lukuunottamatta – näkevät vain niiden tiimien tiedot, joiden jäseniä he ovat.

## Käyttötapauksista

### [Käyttötapauksista tarkemmin]('docs/käyttötapaukset.md')

Kaikki tiimin jäsenet voivat luoda tiimin Kanban-tauluihin tehtäviä sekä ottaa tehtävän hoidettavakseen ('claim task'). Tiimin omistaja voi kuitenkin antaa tiimiläisilleen erilaisia "tiimirooleja" ('TeamRole' tietokannassa) riippuen tarpeistaan. Muut roolit sallivat esimerkiksi tehtävien delegoinnin jonkun muun tiimiläisen hoidettavaksi ('Team member with assign') ja esimerkiksi tiimin moderaattorit ovat tiimin jäseniä, joiden oikeudet lähentelevät tiimin omistajan omia oikeuksia; he voivat kutsua tiimiin jäseniä, määrittää tehtävien tekijän uudelleen sekä poistaa tiimistä jäseniä.

# TODO: Jos lisäät käyttäjille omat taulut, lisää tähän.

Tasker on sovellus, jonka on tarkoitus auttaa esimerkiksi tiimejä tehtävien hallinassa ja tehtävien jakamisessa.

* Käyttäjä voi luoda projekteja ja luoda projekteihin liittyviä tehtäviä.
* Tiimillä on aina vähintään yksi tai useampi omistaja. Projektin luojasta tulee aluksi omistaja ja hän voi lisätä projektiin muita käyttäjiä, joille hän voi myös halutessaan antaa ylläpitäjän oikeudet halutessaan.
* Projektit näkyvät vain niille henkilöille, joille on annettu niihin pääsy.
* Myös sivulle luodut on käyttäjät jakautuvat joko ylläpitäjiin tai käyttäjiin.
* Tehtäviä voi luoda ja muokata. Lisäksi tehtäviä voi määritellä muiden projektiin kuuluvien henkilöiden tehtäväksi.


## Tunnistautuminen

Sovellusta pääsee käyttämään, kun on ensin tehnyt tilin ja varmentanut rekisteröitymisen yhteydessä antamansa sähköpostinsa. Tätä edellytetään siksi, että koko sivun ylläpito-oikeudet annetaan sille käyttäjälle, jonka sähköpostiosoite vastaa ympäristömuuttujissa ylläpitäjän sähköpostiksi määriteltyä osoitetta.

Sähköpostien lähettäminen Herokusta on vähintäänkin hankalaa ja välillä sähköpostien lähettäminen onnistuu hyvinkin ja välillä taas ei. Itse toteutin sähköpostien lähettämisen luomalla ylimääräisen gmail-tilin. Aina välillä Google saattaa estää Heroku-sovellusta lähettämästä sähköposteja, jolloin on käytävä tarkistamassa, pyytääkö Google tarkistamaan "epäilyttäviä tapahtumia". Välillä tämäkään ei riitä, vaan on käytävä seuraavassa osoitteessa https://accounts.google.com/DisplayUnlockCaptcha hyväksymässä viimeaikaiset tapahtumat.

## Käyttötapaukset

Tasker on tiimipohjainen (alkeellinen) Kanban-palvelu. Käyttäjä voi luoda tiimejä, kutsua tiimeihin jäseniä sekä määritellä näille erilaisia käyttöoikeuksia. Tällä hetkellä Kanban-tauluja on tarjolla Todos, Doing ja Done, mutta periatteessa niitä olisi mahdollista lisätä pienin muutoksin.

Palvelussa on mahdollista lähettää viestejä käyttäjille sekä vastata viesteihin.

Ongelmatapauksissa on mahdollista pyytää sivuston ylläpitäjää (Administrator), moderoimaan tai auttamaan ongelmissa. 

## Tunnistautuminen.

Käyttäjät tarvitsevat sähköpostin voidakseen toimia sivustolla. Palveluun rekisteröityminen on mahdollista keksitylläkin sähköpostilla, mutta sähköpostiosoite varmennetaan sähköpostiin lähetettävällä tokenilla, jota käytettyään palvelun käyttäminen on mahdollista aloittaa. Ongelmatapauksissa käyttäjämahdollista hyväksyä käyttäjäksi myös ilman sähköpostivarmennusta.

Tavoitteena sähköpostin varmentamisella on varmistaa, ettei kukaan käyttäjä kaappaa ylläpitäjän oikeuksia, sillä ylläpitäjä tunnistetaan tämän sähköpostiosoitteen perusteella, joka on asetettu ympäristömuuttujaksi ADMIN='sähköpostiosoite@verkko.fi'