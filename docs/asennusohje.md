
# Asennusohjeet

## Asentaminen Docker-ympäristössä

Sovelluksen käyttäminen paikallisesti Docker-ympäristössä edellyttää Dockerin ja docker-composen asentamista, mihin löydät ohjeet seuraavista linkeistä:

* [Dockerin asentaminen]('https://docs.docker.com/engine/install/')
* [docker-composen]('https://docs.docker.com/compose/install/')

Kun docker ja docker-compose on asennettu, kopioi docker-kansiosta esimerkiksi tiedostot *.env.db*, *.env.dev*, *docker-compose_livereload.yml*, *Dockerfile_livereload_dev_only* sekä *entrypoint.sh* Tasker-kansioon. Näiden avulla voit luoda Docker-ympäristön, jossa ohjelmiston koodiin tekemäsi muutokset näkyvät otetaan välittömästi käyttöön sovelluksen ollessa päällä. Kyseisten tiedostojen määrittämät Docker-asetukset eivät kuitenkaan sovellu esimerkiksi Herokussa hyödynnettäviksi!

* **.env.dev** sisältämät asetukset ovat samat kuin [myöhemmin kuvatut](#-ympäristömuuttujat)
* **.env.db** sisältää Dockeroidun postgres-tietokantaa koskevia ympäristömuuttujia, jotka tarvitaan yhteyden muodostamiseksi tietokantaan.

**.env.db - dockeroidun postgres-tietokannan ympäristömuuttujia**
```
POSTGRES_USER=tietokannan_kayttaja
POSTGRES_PASSWORD=tietokannan_kayttajan_salasana
POSTGRES_DB=tietokannan_nimi
```
### Docker-ympäristön kokoaminen

Mikäli olet asentanut docker-composen ja dockerin sekä siirtänyt em. tiedostot Tasker-kansioon, seuraavien komentojen pitäisi luoda dockeroitu versio Tasker-sovellusksesta. Tasker-kansion sisällä, suorita:

```
docker-compose -f docker-compose_livereload.yml build
```

Tämä muodostaa kuvat Dockerfile_livereload_dev_only ja compose_livereload.yml:n määrittelemällä tavalla sekä containerin postgresia ja Taskerin Python-ympäristöä varten. Mikäli suorituksen aikana ei ilmene ongelmia, pitäisi Tasker-sovelluksen käynnistyä komennolla:

```
docker-compose -f docker-compose_livereload.yml up
```

Tämän jälkeen sivujen pitäisi olla käytettävissä, jos menet selaimellasi osoitteeseen 0.0.0.0:5000 tai 127.0.0.1:5000 

Voit käynnistää sovelluksen taustalla myös komennolla:

```
docker-compose -f docker-compose_livereload.yml up -d
```

Lopettaaksesi sovelluksen, voit joko painaa CTRL+C, mikäli käynnistit sovelluksen ensiksi mainitulla tavalla tai suorittamalla komennon

```
docker-compose -f docker-compose_livereload.yml down
```

Mikäli sovellus antaa virheitä tietokantaan liittyviä virheitä, voit yrittää suorittaa komennon, joka tyhjentää vanhan tietokannan ja luo uuden sen tilalle:

```
docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
```

Lisäksi voit luoda tavallisen testikäyttäjän (käyttäjätunnus: "testi"; salasana: "testi") komennolla:

```
docker-compose -f docker-compose.prod.yml exec web python manage.py seed_db
```
Mikäli haluat kokeilla ylläpitäjäoikeuksien käyttöä, voit muokata seed_db:n käyttäjää luovaa koodia siten, että muutat käyttäjän sähköpostiosoitteen vastaamaan [.env.dev](#-ympäristömuuttujat)-tiedoston ADMIN-ympäristömuuttujaa vastaavaksi sähköpostiosoitteeksi.

### Docker-ympäristön poistaminen

Voit tarkistaa, jäikö Docker-containereita koneellesi vielä sovelluksen sammuttamisen jälkeen komennolla:

```
docker container ls -a
```

Jonka output voi näyttää suunnilleen seuraavalta, jos containereita on vielä järjestelmään tallennettuna:

```
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS         PORTS                    NAMES
978c45979667   tasker_web        "flask run --host=0.…"   10 seconds ago   Up 3 seconds   0.0.0.0:5000->5000/tcp   tasker_web_1
0dfd4ac9896f   postgres:latest   "docker-entrypoint.s…"   11 seconds ago   Up 3 seconds   5432/tcp                 tasker_db_1
```

Jos Status-kohdan alla näkyy "Up x seconds" tms., sammuta ensin containerit aiemmin kuvatulla tavalla. Suorita sitten sama komento uudelleen ja tarkista näkyykö containereita edelleen. Jos näkyy, saat poistettua ne seuraavasti:

```
docker rm <CONTAINER ID-sarakkeen alla näkyvä merkkijono>
```

Docker luo lisäksi "kuvia" containereista, jotka näet komennolla:

```
docker images
```

Mikäli outputissa on Taskeriin viittaavia containereita, esim:

```
REPOSITORY   TAG          IMAGE ID       CREATED       SIZE
tasker_web   latest       7338f0135aa6   2 hours ago   202MB
postgres     latest       1f1bd4302537   11 days ago   314MB
python       3.8.7-slim   4fab6f68e9f0   2 weeks ago   115MB
```

Saat poistettua ne komennolla:

```
docker rmi <IMAGE ID>
```

Voit myös poistaa Dockerin Taskerille luoman volumen eli tallennustilan (tietokantaa varten). Selvitä ensin, minkä niminen Taskerille luotu volume on, jos sitä ei ole jo poistettu:

```docker volume ls```

jonka output voi näyttää esim. tältä:

```
DRIVER    VOLUME NAME
local     tasker_postgres_data
```
Volumen poistaminen onnistuu seuraavasti:

```
docker volume rm tasker_postgres_data
```

## Asentaminen Python-ympäristössä

Vaatimukset:

* Python (>=3.8.1) toimivat ainakin, kehitys tehty versiolla 3.8.7.
    * [Pythonin]('https://www.python.org/downloads/') voit ladata täältä tarvittaessa. (Huomaa kuitenkin, että sovellusta ei ole testattu tuoreimmalla versiolla 3.9.1)

Suosittellaan:

* Pipenv tai virtualenv, jotta voit helposti poistaa sovelluksen edellyttämät paketit järjestelmästäsi.

Virtualenv:n saat helpoiten asennettua seuraavalla komennolla:

```
pip install virtualenv
```
Myös wheel-niminen paketti voi olla tarpeellinen:

```
pip install wheel
```

### Virtualenv-ympäristön luominen

Mene kansioon, johon latasit Taskerin ja suorita siellä komento:

```
python3 -m venv venv
```

Tämän seurauksena kansioon pitäisi ilmestyä venv-niminen kansio, johon kaikki sovelluksen vaatimat python-paketit asennetaan. Poistamalla kyseisen kansion pääset eroon sovelluksen vaatimista python-paketeista.

Ympäristön otetaan käyttöön komennolla:

```
source venv/bin/activate
```

Nyt komentorivin alkuun ilmestyy (venv), mikä tarkoittaa, että virtualenv-ympäristö on käytössä. Kun haluat lopettaa sen käyttämisen, suorita:

```
deactivate
```
### Varsinaisten sovelluksen edellyttämien pakettien asentaminen

Mene ensin komentorivillä kansioon, johon latasit sovelluksen ja suorita seuraava komento:

```
pip install -r requirements.txt
```

Mikäli asentamisen aikana ei tapahdu virheitä, vaaditut python-paketit on nyt asennettu.

## Yleiset asennusohjeet

### Ympäristömuuttujat

Luo Tasker-kansioon .env-niminen tiedosto, johon tallennat sovelluksen käyttämät ympäristömuuttujat. Tämän tiedoston avulla myös säätelet, missä config.py-tiedoston määrittelemistä asetuksista sovellus käynnistyy säätämällä APP_SETTINGS-muuttujan määritystä. Esimerkissä käytössä on sovelluksen kehitystila. Sähköpostia ei välttämättä tarvita, mutta jos kokeilet sovellusta antamatta sovellukselle oikeuksia sähköpostin käyttöön, aseta ympäristömuuttuja ```EMAIL_CONFIGURED=0```, jolloin sovellukseen rekisteröityneiltä käyttäjiltä ei edellytetä sähköpostiosoitteen varmentamista ennen kuin sovelluksen käyttäminen on mahdollista.

Lisäksi jos haluat sovelluksen käyttävän tietokantaa ja tietojen pysyvän tallessa, joudut luomaan sovellukselle tietokannan. Kaikkein helpointa on käyttää sqlite-tietokantaa, jolloin voit korvata DATABASE_URL- ja DEV_DATABASE_URI -muuttujat esimerkiksi "sqlite:///db.db", jolloin sovellus luo application-kansion sisälle db.db-nimisen Sqlite3-tietokannan ja käyttää sitä. Toisaalta, jos et halua säilyttää tietoja myöhempää käyttöä varten, polku sqlite:/// luo väliaikaisen tietokannan tietokannan muistiin, joka poistetaan, kun sovellus lopetetaan.

Vastaavasti, jos haluat käyttää esimerkiksi postgresql-tietokantaa, voit syöttää sen tiedot em. kenttiin. Alla näkyvässä esimerkissä oletetaan, että käytössä olisi paikallinen postgresql-tietokanta:

```
FLASK_ENV=development
APP_SETTINGS=config.DevConfig
# 0 = no email for confirming accounts, 1 = email is used
EMAIL_CONFIGURED=0
FLASK_APP=wsgi.py
DEBUG=True
FLASK_DEBUG=1
DATABASE_URL="postgresql://tietokannan_kayttaja:tietokannan_salasana@localhost:5432/tietokanta"
DEV_DATABASE_URI="postgresql://tietokannan_kayttaja:tietokannan_salasana@localhost:5432/tietokanta"
# For temporary use:
# DATABASE_URL=sqlite:///
# Sqlite database that is saved:
# DATABASE_URL=sqlite:///db.db
SECRET_KEY=salainenmerkkijonojotakaytetaansalasanojensalaamisessajneVAIHDA
# EMAIL Settings (GMail as example):
MAIL_SERVER='smtp.googlemail.com'
MAIL_PORT=465
MAIL_USE_TLS=0
MAIL_USE_SSL=1
MAIL_USERNAME='email_addres@gmail.com'
MAIL_PASSWORD='your_email_password'
# If the site needs to have multiple admins already from startup onwards,
# add more email addresses into this list:
ADMINS=['email_addres@gmail.com']
MAIL_DEFAULT_SENDER = 'email_addres@gmail.com'
ADMIN='email_addres@gmail.com'
MAIL_SUBJECT_RESET="Reset password"
```
### Gmail-sähköpostin käyttäminen

Mikäli sovelluksen haluaa lähettävän salasananpalautusviestejä, uusien tilien varmentamisviestejä jne., on sille annettava käyttöön jokin sähköpostiosoite. Itse käytin Gmail-osoitetta, jonka toimimaan saaminen edellytty "Vähemmän turvallisten sovellusten käyttöoikeuksien" sallimista [Googlen sivuilla](https://myaccount.google.com/lesssecureapps?pli=1&rapt=AEjHL4M_b6ZbBQgTf7w6vflBCGi8NlOyAVEVO89ZDcoFSfU4KCXb5768NLBxGh-R3zSEurQqXpZSO5divb38ls_VnF_-pzQeSw).

Aina tämäkään ei riitä, vaan Google saattaa myös estää sovelluksen toiminnan, mikäli gmail-tiliin kirjaudutaan Googlen mielestä epäilyttävästä sijainnista (esim. Heroku). Jos näin käy, voi joutua hyväksymään sovelluksen käyttämisen uudesta sijainnista osoitteessa: https://accounts.google.com/DisplayUnlockCaptcha . Lisäksi on käytävä [myaccount.google.com](https://myaccount.google.com/) -osoitteessa hyväksymässä viimeaikaiset epäilyttävät tapahtumat.

Suosittelenkin esimerkiksi MailGun-palvelun käyttöä, mikäli sähköpostin haluaa oikeasti toimimaan kohtuullisella toimintavarmuudella.

### Sovelluksen käynnistäminen

Nyt sovelluksen pitäisi olla toimintavalmis.

Voit käynnistää sovelluksen suorittamalla Tasker-kaniossa komennon:

```
python manage.py run
```
Mikäli sovelluksen käynnistyksen yhteydessä esiintyy virheitä esimerkiksi tietokantaan liittyen, voit luoda uuden tietokannan (poistaa tietokannan nyt sisältämät tiedot) komennolla:

```
python manage.py create_db
```

Lisäksi voit luoda testikäyttäjän sovellukseen komennolla

```
python manage.py seed_db
```

Testikäyttäjän tunnnukset ovat käyttäjätunnus: "testi"; salasana: "testi".

Mikäli haluat kokeilla ylläpitäjäoikeuksien käyttöä, voit muokata seed_db:n käyttäjää luovaa koodia siten, että muutat käyttäjän sähköpostiosoitteen vastaamaan .env.dev-tiedoston ADMIN-ympäristömuuttujaa vastaavaksi sähköpostiosoitteeksi.

## Herokussa

Herokussa sovelluksen käyttöönsaaminen onnistuu helpoiten käyttämällä Python buildpackeja. Sovellus tarvitsee Heroku-tietokannan, joten asennettuasi Heroku-clientin, kirjauduttuasi tililesi sekä luotuasi Heroku appin, on suoritettava:

```
heroku addons:create heroku-postgresql:hobby-dev --app app_name
```
Lisäksi Herokuun on lisättävä [ympäristömuuttujat](#-ympäristömuuttujat), jotka mainittiin edellä. Tämän voi tehdä joko komentoriviltä komennolla (esimerkkinä sähköpostivarmennuksen poistava asetus):

```
heroku config:set EMAIL_CONFIGURED=0
```
Tai herokun verkkosivuilta, menemällä appiin ja siellä settings -> Reveal config vars. Ympäristömuuttujan DATABASE_URL pitäisi ilmestyä Herokun ympäristömuuttujiin automaattisesti, kun postgres-tietokanta on otettu käyttöön.

Kun em. asiat on tehty, komennon ```git push heroku master``` pitäisi onnistua puskemaan sovellus Herokuun. Mikäli Herokussa tulee virheitä esimerkiksi tietokantaan liittyen, voi suorittaa vielä komennon:

```
heroku run python manage.py create_db
```
Jos palveluun rekisteröitymisessä on ongelmia johtuen esimerkiksi siitä, että sähköpostivarmennus ei onnistu, onnistuu em. testikäyttäjän luominen edellistä komentoa mukauttamalla:

```
heroku run python manage.py seed_db
```