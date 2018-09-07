# Nabla bokskapsystem #

Dette er nablas system for å holde styr på hvem som bruker hvilke skap i
Realfagbygget.


## Pipfile
Dette prosjektet bruker [Pipfile](https://github.com/pypa/pipfile).


## Hvordan komme i gang

1. Installer [pipenv](https://docs.pipenv.org/)
2. Kjør ```pipenv install``` for å installere alle pip-pakkene du trenger.
3. Deretter kan du kjøre ting ved å skrive ```pipenv run "whatever"``` eller bruke ```pipenv shell```

Pipenv vil påse at du bruker riktig python-version.

Kommandoene som følger antar at de blir kjørt etter å ha kjørt ```pipenv shell```.

## Tester
Dette prosjektet har tester. Disse bør kjøres før du committer og/eller pusher.
De kjøres ved hjelp av denne kommandoen i prosjektets rotmappe:

```
./manage.py test
```

Hvis du har lyst til å finne ut hvor mye av kodebasen som blir testet kan du kjøre
```
coverage run ./manage.py test
coverage report
```

## Linting
Det er også kjekt om folk følger kjører pylint for å få hint for å forbedre koden
```
pylint locker
```
