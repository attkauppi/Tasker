# Käyttöohje

## Rekisteröityminen

Palveluun pääsee rekisteröitymään painamalla oikean ylälaidan "Login"-painiketta. Tämän jälkeen aukeavan ikkunan alalaidassa on vaihtoehto rekisteröityä, mikäli käyttäjätunnuksia ei vielä ole. Jos sähköpostivarmennus on päällä, on käyttäjätietoihin syötettävä oikea sähköpostiosoite käyttäjänimen ja salasanan lisäksi. Jos mitään virheitä ei tule vastaan ja rekisteröinti onnistuu, on käyttäjätili luotu.

Sähköpostivarmennuksen ollessa käytössä on tässä vaiheessa hyvä kirjautua ja avata sitten sähköpostiin tullut varmennusviestin linkki (tilin varmentaessaan täytyy olla kirjautunut, jotta sähköpostiosoitteen varmistaminen onnistuu). Kun sähköposti on varmennettu käyttäen sähköpostilinkkiä, on palvelua mahdollista alkaa käyttää.

Jos sähköpostiin tullut varmennuslinkki ehtii vanhentua, on sisäänkirjautumisen jälkeen mahdollista pyytää uuden varmennusviestin lähettämistä. Jos sähköpostien lähettämisessä on vikaa, kannattaa sähköpostivarmenteet ottaa pois päältä lisäämällä ympäristömuuttujatiedostoon .env Tasker-kansiossa asetus ```EMAIL_CONFIGURED=0``` . Ympäristömuuttujista tarkemmin [asennusohjeessa](docs/asennusohje#-ympäristömuuttujat).

Alla on havainnollistettu rekisteröityminen gif-muodossa:

<a href="https://drive.google.com/uc?export=view&id=1q_AghVLqdSJx_KpioH9Zlmjb-I-qQAM2"><img src="https://drive.google.com/uc?export=view&id=1q_AghVLqdSJx_KpioH9Zlmjb-I-qQAM2" style="width: 650px; max-width: 100%; height: auto" title="Click to enlarge picture"/></a>


## Tiimit

Palvelussa on mahdollista luoda tiimejä. Mikäli tiimin haluaa luoda, on sivun yläreunassa kulkevassa navbarissa "Teams"-niminen dropdown-valikko, joka sisältää tiimit, joihin käyttäjä kuuluu, sekä mahdollisuuden luoda uusia tiimejä.

Käyttäjän luodessa tiimin hänestä tulee tiimin "omistaja". Käyttäjän luomaan tiimiin on mahdollista kutsua muita palvelun käyttäjiä, joista tulee tiimiläisiä. Tiimiläisten tiimirooleja on mahdollista määritellä tarkemmin, kun nämä ovat liittyneet tiimiin.

Tiimirooleja ja tiimirooleihin liittyviä oikeuksia ovat:

* **Team member**: voi ottaa suoritettavakseen tehtäviä, joihin ei ole määritelty vielä tekijää, sekä luoda uusia tehtäviä.
* **Team member with assign**: voi edellisten lisäksi määritellä tehtäviä muiden tiimiläisten suoritettaviksi
* **Team moderator**: voi edellisten lisäksi kutsua ja poistaa tiimistä jäseniä sekä muuttaa muiden tiimiläisten rooleja. Voi korkeintaan antaa tiimimoderaattorioikeudet toiselle tiimiläiselle. Periaatteena on, että kukaan ei voi määritellä kenellekään enempää oikeuksia kuin hänellä itsellään on, jotta tiimin kaappaaminen ei olisi mahdollista.
* **Team owner**: voi edellisten lisäksi poistaa tiimin.
* **Team administrator**: antaa sivuston ylläpitäjille mahdollisuuden moderoida tai auttaa tiimeissä esiintyvissä teknisissä ongelmissa. Tätä tiimiroolia ei myönnetä, vaan ylläpitäjätili voi ottaa sen käyttöönsä tiimissä navigoimalla tiimisivulle.

Tiimirooleista jne. tarkemmin [käyttötapaukset](käyttötapaukset.md)-osiossa.

Tiimin luomista havainnollistava .gif alapuolella:

<a href="https://drive.google.com/uc?export=view&id=1udemUR0z2BRM8J3TXjDoEzcP-2xrSk-F"><img src="https://drive.google.com/uc?export=view&id=1udemUR0z2BRM8J3TXjDoEzcP-2xrSk-F" style="width: 650px; max-width: 100%; height: auto" title="Tiimin luominen"/></a>











### Tiimiin kutsuminen

Tiimiin voi kutsua jäseniä tiimisivun navbarin Invite to team -painikkeesta. Tämän jälkeen aukeaa sivu, johon on listattu kaikki palveluun rekisteröityneet käyttäjät. Kunkin käyttäjän kohdalla on sivun oikeassa reunassa nappi, jonka avulla käyttäjän voi kutsua tiimiinsä.

Tiimiläisten kutsuminen .gif-muodossa

<a href="https://drive.google.com/uc?export=view&id=1alTb_wHLEP_6N8AbGMUnXw6un2-E6Yr9"><img src="https://drive.google.com/uc?export=view&id=1alTb_wHLEP_6N8AbGMUnXw6un2-E6Yr9" style="width: 650px; max-width: 100%; height: auto" title="Tiimin luominen"/></a>

### Tiimin jäsenien tarkastelu ja roolien muuttaminen

Tiimin jäseniä voi tarkastella tiimisivun navbarin Members -painikkeesta. Mikäli olet kirjautuneena moderaattorina, tiimin omistajana tai Admin-käyttäjänä, voit muokata tiimiläisten rooleja painamalla tiimiläisen kohdalla näkyvää Edit team role -painiketta.

Tiimirooliksi voit valita roolin, jolla on korkeintaan yhtä paljon oikeuksia kuin omalla tiimiroolillasi.

Tiimiroolit on toteutettu tietokannassa team_roles-luokassa, jonka yhtenä parametrina on team_permissions-niminen kokonaisluku. Kokonaisluvut muodostuvat eri rooleille seuraavasti:

```python

class TeamPermission:
    CREATE_TASKS = 1
    CLAIM_TASKS = 2
    ASSIGN_TASKS = 4
    MODERATE_TEAM = 8
    TEAM_OWNER = 16
    ADMIN = 32

# TeamRole-luokan insert_role-metodista:
roles = {
            'Team member': [
                TeamPermission.CREATE_TASKS,
                TeamPermission.CLAIM_TASKS
            ],
            'Team member with assign': [
                TeamPermission.CREATE_TASKS,
                TeamPermission.CLAIM_TASKS,
                TeamPermission.ASSIGN_TASKS
            ],
            'Team moderator': [
                TeamPermission.CREATE_TASKS,
                TeamPermission.CLAIM_TASKS,
                TeamPermission.ASSIGN_TASKS,
                TeamPermission.MODERATE_TEAM
            ],
            'Team owner': [
                TeamPermission.CREATE_TASKS,
                TeamPermission.CLAIM_TASKS,
                TeamPermission.ASSIGN_TASKS,
                TeamPermission.MODERATE_TEAM,
                TeamPermission.TEAM_OWNER
            ],
            'Administrator': [
                TeamPermission.CREATE_TASKS,
                TeamPermission.CLAIM_TASKS,
                TeamPermission.ASSIGN_TASKS,
                TeamPermission.MODERATE_TEAM,
                TeamPermission.TEAM_OWNER,
                TeamPermission.ADMIN
            ]
        }
```
Tämä tekee tiimiroolien lisäämisen ja vähentämisen mielestäni melko joustavaksi. 

Roolien muuttaminen sovelluksessa tapahtuu tiimisivuilla näkyvän alemman, taustaväriltään mustan navbarin Members-painikkeen kautta. Kaikki tiimiläiset pääsevät tähän näkymään, mutta vähintään moderaattori-roolin omaavat käyttäjät näkevät sivulla jokaisen tiimiläisen kohdalla napin, jonka kautta rooleja on mahdollista käydä muuttamassa. Saman valikon kautta on myös mahdollista poistaa tiimiläinen.

Tiimiroolien muokkausta havainnollistettu seuraavassa gif:ssä:



<a href="https://drive.google.com/uc?export=view&id=1ScyyYZjLoNyKSihxVpsh079Zafbumbc_"><img src="https://drive.google.com/uc?export=view&id=1ScyyYZjLoNyKSihxVpsh079Zafbumbc_" style="width: 650px; max-width: 100%; height: auto" title="Tiimin luominen"/></a>


## Tiimitehtävien luominen

Tiimitehtäviä on mahdollista luoda ja muokata tiimin Team tasks -sivulla, jonne pääsee tiimisivuilla näkyvän alemman, taustaväriltään mustan navbarin Team tasks -painikkeen kautta. Navbarin alle, keskelle sivua ilmestyvän Create task -painikkeen kautta voi lisätä tehtäviä.

Kaikki tehtävät siirtyvät aluksi Todos-tauluun. Kun tehtävä on luotu, sille on mahdollista määritellä tekijä tai käyttäjä voi itse määrittää ottavansa tehtävän hoitaakseen. Mikäli käyttäjällä ei ole oikeutta määritellä tehtävää jonkun muun tiimiläisen hoidettavaksi (Team member -rooli), hänellä on vaihtoehtoina vain määrittää tiimitehtävä joko omaksi tehtäväkseen tai jättää tekijä määrittämättä.

Tiimitehtävät ovat card-tyyppisiä ja niiden alalaidassa näkyvän kynän kuvan kautta tiimitehtävää pääsee muokkaamaan. Sen oikealla puolella olevan rastin kautta tiimitehtävän voi tuhota. Tiimitehtävän siirtäminen taulujen välillä puolestaan onnistuu vasemmasta ja oikeasta alalaidasta löytyvillä nuolipainikkeilla, joita painamalla tehtävä siirtyy nuolen osoittamaan suuntaan mikäli se on mahdollista, sillä vasemman reunan taulusta tehtävää ei enää voi siirtää vasemmalle eikä oikeasta reunasta oikealle taulujen loppuessa kesken.

Alla havainnollistettu tiimitehtävän luomista:

<a href="https://drive.google.com/uc?export=view&id=1xqoFoAtnzExAXSIlLrcyLzdTY4sT9wcg"><img src="https://drive.google.com/uc?export=view&id=1xqoFoAtnzExAXSIlLrcyLzdTY4sT9wcg" style="width: 650px; max-width: 100%; height: auto" title="Tiimin luominen"/></a>

### Kommentit tiimitehtävissä

Lopuksi vielä toteutin mahdollisuuden lisätä kommentteja tiimitehtäviin, jotta tiimiläiset voisivat halutessaan keskustella keskenään tiimitehtäviin liittyvistä asioista. 


## Ylläpitäjänä toimiminen

Ylläpitäjätileillä on mahdollisuus päästä muokkaamaan kaikkien käyttäjien tietoja sekä tiimejä. Ylläpitäjänä kirjautunut käyttäjä näkee navbarissa punaisen dropdown-valikon, jonka kautta hän pääsee käsiksi sekä sivuston käyttäjiin että tiimeihin.

Halutessaan muokata tiimiä ylläpitäjän on ensin otettava tiimissä käyttöön Admin-oikeutensa, mikä tapahtuu tiimisivun etusivulla näkyvän "Claim admin" -painikkeen kautta. Tämä lisää ylläpitäjän tiimin (piilo)jäseneksi, jota muut eivät näe esimerkiksi Members-listassa, mutta jolla on pääsy kaikkiin tiimin asetuksiin ja valikoihin.