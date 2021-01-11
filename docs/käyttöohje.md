# Käyttöohje

## Rekisteröityminen

Palveluun pääsee rekisteröitymään painamalla oikean ylälaidan "Login"-painiketta. Tämän jälkeen aukeavan ikkunan alalaidassa on vaihtoehto rekisteröityä, mikäli käyttäjätunnuksia ei vielä ole. Jos sähköpostivarmennus on päällä, on käyttäjätietoihin syötettävä oikea sähköpostiosoite käyttäjänimen ja salasanan lisäksi. Jos mitään virheitä ei tule vastaan ja rekisteröinti onnistuu, on käyttäjätili luotu.

Sähköpostivarmennuksen ollessa käytössä on tässä vaiheessa hyvä kirjautua ja avata sitten sähköpostiin tullut varmennusviestin linkki (tilin varmentaessaan täytyy olla kirjautunut, jotta sähköpostiosoitteen varmistaminen onnistuu). Kun sähköposti on varmennettu käyttäen sähköpostilinkkiä, on palvelua mahdollista alkaa käyttää.

Jos sähköpostiin tullut varmennuslinkki ehtii vanhentua, on sisäänkirjautumisen jälkeen mahdollista pyytää uuden varmennusviestin lähettämistä. Jos sähköpostien lähettämisessä on vikaa, kannattaa sähköpostivarmenteet ottaa pois päältä lisäämällä ympäristömuuttujatiedostoon .env Tasker-kansiossa asetus ```EMAIL_CONFIGURED=0``` . Ympäristömuuttujista tarkemmin [asennusohjeessa](docs/asennusohje#-ympäristömuuttujat).

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

