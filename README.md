Tasker-Kanban-järjestelmän käyttäminen
======================================

- [Lyhyt kuvaus Taskerista](#tasker)
- [Heroku](#heroku)
- [Käyttötapauksista](#käyttötapauksista)
- [Sovelluksen asennusohje](#sovelluksen-asennusohje)
- [Käyttöohjeet](#käyttöohjeet)
- [Työn ja sovelluksen rajoitteet](#työn-ja-sovelluksen-rajoitteet)
- [Tietokantakaavio](#tietokantakaavio)
- [Tunnistautuminen](#tunnistautuminen)

# Tasker

Tasker on tiimipohjainen Kanban-palvelu, jota voi hyödyntää esimerkiksi tiimin tehtävien hallinnassa ja tiimin jäsenten välisessä työnjaossa. Käyttäjät voivat luoda tiimejä vapaasti ja kutsua muita käyttäjiä tiiminsä jäseniksi. 

Tiimejä voi luoda mihin tarkoitukseen tahansa - esimerkiksi projektikohtaisesti tai pysyvämpien tiimien tehtävienhallintaan. Palvelun käyttäjät – sivuston ylläpitäjiä lukuunottamatta – näkevät vain niiden tiimien tiedot, joiden jäseniä he ovat.

## Heroku

Sovellus löytyy Herokusta seuraavasta osoitteesta: https://tsohatasker.herokuapp.com/

Tietoja sovelluksen Herokuun asentamisesta löytyy tarkemmin [käyttöohjeet](#)

## Käyttötapauksista

### [Käyttötapauksista tarkemmin](docs/käyttötapaukset.md)

Kaikki tiimin jäsenet voivat luoda tiimin Kanban-tauluihin tehtäviä sekä ottaa tehtävän hoidettavakseen ('claim task'). Tiimin omistaja voi antaa tiimiläisilleen erilaisia "tiimirooleja" ('TeamRole' tietokannassa) riippuen tarpeistaan. Muut roolit sallivat esimerkiksi tehtävien delegoinnin jonkun muun tiimiläisen hoidettavaksi ('Team member with assign' -tiimirooli) ja esimerkiksi tiimin moderaattorit ovat tiimin jäseniä, joiden oikeudet lähentelevät tiimin omistajan omia oikeuksia: moderaattorit voivat kutsua tiimiin jäseniä, määrittää tehtävien tekijän uudelleen sekä poistaa tiimistä jäseniä. Omistaja voi lisäksi poistaa tiimin.

## Sovelluksen asennusohje

### [Tarkemmat asennusohjeet](docs/asennusohje.md)

#### [Asentaminen Docker-ympäristössä](docs/asennusohje#-asentaminen-docker-ympäristössä)

Järjestelmän nopeaa katselmointi onnistunee parhaiten käyttämällä docker-kansion sisältämiä Dockerfile- ja docker-compose.yml -tiedostoja. Tällöin ei tarvitse asentaa Postgresql:ää tai luoda uutta tietokantaa sovellusta varten. Tämä kuitenkin edellyttää [Dockerin]('https://docs.docker.com/engine/install/') ja [docker-composen]('https://docs.docker.com/compose/install/') asentamista, mikä on dokumentoitu kattavasti eri käyttöjärjestelmille Dockerin omilla sivuilla.

#### [Asentaminen Python-ympäristöön](docs/asennusohje#-asentaminen-python-ympäristössä)
Toisena vaihtoehtona on käyttää esimerkiksi virtualenv- tai pipenv -ympäristöä Python-pakettien asentamiseen ja luoda tietokanta esimerkiksi postgresql:ään tai Sqliteen. Sovelluksen kehityksessä käytetty Python-versio on 3.8.7 (määritelty myös [runtime.txt]('runtime.txt')-tiedostossa). Luultavasti myös Python-versiot >= 3.8.1 toimivat, sillä kyseistä versiota käytetään esimerkiksi Docker-ympäristössä.

Asentaminen on käsitelty tarkemmin ylle linkitetyissä osioissa.

## Käyttöohjeet

### [Käyttöohjeet tarkemmin](docs/käyttöohje.md)

* Kirjautuminen onnistuu sivun oikeasta ylälaidasta löytyvän Login-painikkeen kautta
* Rekisteröitymisvaihtoehto löytyy kirjautumissivun alalaidasta.
* Tiimin luonti: Kirjautumisen jälkeen sivun navbarille ilmestyy dropdown-valikko "Teams", jossa luetellaan tiimit, joihin käyttäjä kuuluu, ja viimeisenä vaihtoehtona on tiimin luominen.

## Työn ja sovelluksen rajoitteet

Olisin halunnut saada Kanban-taulujen tehtävistä esim. JQuerylla toimivia, joita olisi helposti voinut vetää taulusta toiseen. Käytinkin tähän kohtuullisen paljon aikaa, mutta FullStack-kurssia käymättä en saanut sovelluksesta riittävän käyttökelpoista - paljolti tästä syystä sovelluksesta löytyy API-määrittelyt, joita hyödynsin tietojen hakemiseen ajaxilla.

Tämä olisi selvä jatkokehityskohde.

## [Tietokantakaavio](docs/tietokantakaavio.md)

## Tunnistautuminen


Käyttäjät tarvitsevat sähköpostin voidakseen toimia sivustolla. Palveluun rekisteröityminen on mahdollista keksitylläkin sähköpostilla, mutta sähköpostiosoite varmennetaan sähköpostiin lähetettävällä tokenilla, jota käytettyään palvelun käyttäminen on mahdollista aloittaa. Ongelmatapauksissa käyttäjämahdollista hyväksyä käyttäjäksi myös ilman sähköpostivarmennusta.

Tavoitteena sähköpostin varmentamisella on varmistaa, ettei kukaan käyttäjä kaappaa ylläpitäjän oikeuksia, sillä ylläpitäjä tunnistetaan tämän sähköpostiosoitteen perusteella, joka on asetettu ympäristömuuttujaksi ADMIN='sähköpostiosoite@verkko.fi'

Sovellusta pääsee käyttämään, kun on ensin tehnyt tilin ja varmentanut rekisteröitymisen yhteydessä antamansa sähköpostin. Tätä edellytetään siksi, että koko sivun ylläpito-oikeudet annetaan sille/niille käyttäjälle/käyttäjille, jonka sähköpostiosoite vastaa ympäristömuuttujissa ylläpitäjän sähköpostiksi määriteltyä osoitetta.

Sähköpostien lähettäminen Herokusta on vähintäänkin hankalaa ja välillä sähköpostien lähettäminen onnistuu hyvinkin ja välillä taas ei. Itse toteutin sähköpostien lähettämisen luomalla ylimääräisen gmail-tilin. Aina välillä Google saattaa estää Heroku-sovellusta lähettämästä sähköposteja, jolloin on käytävä tarkistamassa, pyytääkö Google tarkistamaan "epäilyttäviä tapahtumia". Välillä tämäkään ei riitä, vaan on käytävä seuraavassa osoitteessa https://accounts.google.com/DisplayUnlockCaptcha hyväksymässä viimeaikaiset tapahtumat.

