# Instrukcja automatu - codzienna aktualizacja Wiadomości PPOŻ

Działasz sam, bez kontaktu z odbiorcą. Nie zadawaj pytań - wykonaj wszystko do końca.

## Dla kogo i jak pisać
Tomek - strażak PSP i inspektor ochrony ppoż., prowadzi szkolenia. Chce być stale „w temacie”: ciekawe wydarzenia z branży, wnioski, dobre praktyki, wiedza na przyszłość.
- Pisz po polsku, ciekawie i po ludzku - jak kolega z branży, nie jak rozporządzenie. Krótkie zdania.
- Zawsze krótki myślnik „-”, nigdy długi.
- TYLKO prawdziwe i rzetelne informacje: źródła oficjalne (PSP, KG PSP, komendy, instytuty, raporty, Dz.U., EUR-Lex) albo porządne portale branżowe. Każda informacja z linkiem, który sam otworzyłeś.
- Nie wymyślaj faktów, dat, liczb, przyczyn, przepisów, cytatów ani linków. Gdy nie da się potwierdzić - pomiń.
- Etykiety: MEDIA (informacja prasowa, przyczyna niepotwierdzona), RAPORT, BADANIE, PRODUCENT.
- Zero plotek. Projekt przepisu nigdy jako obowiązujące prawo.

## Krok 0 - odśwież nagłówki RSS (zapas dla GitHub Actions)
Uruchom `python3 skrypty/zbierz_rss.py` - zapisze świeży `rss.json` (bez AI). Dołącz `rss.json` do commita w kroku 3.

## Krok 1 - pobierz kanały RSS (bez AI)
Napisz krótki skrypt w Pythonie (tylko biblioteka standardowa), który pobiera kanały z pliku `zrodla.json` w tym repozytorium (User-Agent zwykłej przeglądarki, timeout 20 s), bierze wpisy z ostatnich 30 godzin (RSS <item> i Atom <entry>) i wypisuje: źródło, data, tytuł, link, 280 znaków opisu. Błąd jednego kanału nie przerywa reszty.
Kanały, które zwróciły błąd (403, SSL, zerwane połączenie, zły XML) - spróbuj jeszcze raz narzędziem WebFetch na adresie kanału.
Jeśli wartościowych wpisów jest mniej niż 6 - poszerz okno do 72 godzin.

## Krok 2 - wybierz i sprawdź
- 3-5 wydarzeń lub publikacji z najlepszymi wnioskami (MINIMUM 3 - jeśli brakuje świeżych, weź z poszerzonego okna) (akcje z problemami, MAYDAY, wypadki strażaków, raporty, badania, nietypowe pożary, czad, baterie). Mieszaj Polskę i świat. Dla każdego OTWÓRZ pełny artykuł (curl z przeglądarkowym User-Agent albo WebFetch). Strona blokuje dostęp - wybierz inny temat.
- Pomijaj: budżety, kadry, sprawy sądowe bez lekcji, reklamy, nagrody, wydarzenia już opisane w `wiadomosci.json` (sprawdź tytuły i linki).
- Gdy w kanałach jest coś do sekcji pobocznych (przepisy, wyroki, nowości, badania, baterie, statystyki PSP) - dodaj tam.

## Krok 3 - zaktualizuj `wiadomosci.json`
Zachowaj strukturę pliku. Zmieniaj tylko to, co opisane niżej. Nie usuwaj kluczy.
1. `aktualizacja` = dzisiejsza data (RRRR-MM-DD, strefa Europe/Warsaw).
2. `wydarzenia` - nowe na POCZĄTEK listy. Każde:
   `{"id":"RRRR-MM-DD-krotka-nazwa","data":"RRRR-MM-DD","kraj":"Polska","etykieta":"MEDIA","naglowek":"KRÓTKI NADTYTUŁ WERSALIKAMI","tytul":"chwytliwy, ale prawdziwy tytuł","zajawka":"1-2 zdania","tresc":["akapit faktów","akapit faktów"],"wniosek":"czego to uczy","praktyka":"co konkretnie robić","tematy":["czad","MAYDAY"],"powiazane":["nazwa hasła z listy niżej"],"zrodla":[["Nazwa","https://..."]]}`
   Opcjonalnie `"analiza":["Nazwa raportu","https://..."]` gdy jest oficjalny raport. Gdy zdarzenie starsze niż artykuł - podaj datę zdarzenia w treści.
   Wydarzenia starsze niż 30 dni PRZENIEŚ (nie usuwaj) na początek listy `wydarzenia` w pliku `archiwum.json` - patrz punkt 11.
   `powiazane` - tylko nazwy z tej listy (hasła z aplikacji): Butle LPG, Czujki i SSP, Drogi pożarowe, Elektryka i PWP, Ewakuacja, Fotowoltaika, Garaże, Gaśnice, Hydranty, IBP, Klasy odporności pożarowej, Strefy pożarowe, Kominy i kotłownie, Kontrole i mandaty, Lasy i żniwa, Materiały budowlane, Obciążenie ogniowe, Obowiązki właściciela, Oddymianie i drzwi ppoż., Odległości, Prace niebezpieczne, Przyczyny pożarów, Rozwiązania zamienne, Spalanie i pożar, Stacje paliw, Strefy Ex i wybuch, Szkolenia, Tryskacze, Woda do gaszenia, Wysokość budynku, ZL i kategorie, Wodór, Tlenek węgla (czad), Gaz ziemny (metan), Propan-butan, Acetylen, Benzyna i ciecze palne, Pyły, Akumulatory i baterie, Znaki i oświetlenie.
3. `pytania` - dodaj 2 nowe na podstawie dzisiejszych wydarzeń: `{"p":"pytanie","o":"krótka odpowiedź","data":"RRRR-MM-DD"}`. Starsze niż 30 dni PRZENIEŚ do `archiwum.json` (lista `pytania`), ale w `wiadomosci.json` zostaw co najmniej 10.
4. `terminy` - minione PRZENIEŚ do `archiwum.json` (lista `terminy`). Dodaj nowy tylko, gdy w źródle jest konkretna data (przepis, nabór, konferencja): `{"data":"RRRR-MM-DD","tytul":"...","opis":"1 zdanie","wiecej":"2-3 zdania po ludzku","zrodla":[[...]]}`.
5. `obserwuje` - gdy w sprawie pojawiło się coś nowego: zaktualizuj `stan` i `ostatnio`. Nowa ważna sprawa w toku - dodaj (najwyżej 8 pozycji).
6. Co 1-2 dni dodaj 1 pozycję do `czywiesz` (`{"tekst":"...","zrodlo":"..."}`) albo `tipy` (`{"tytul":"...","tresc":"...","przepis":"§ ... (tylko pewny)","dla":"inspektor" albo "strażak"}`) - ciekawą i sprawdzoną.
7. `przepisy`, `wyroki`, `nowosci`, `badania`, `baterie`, `faktmit`, `liczby`, `raporty`, `materialy` - dodawaj tylko z pewnych źródeł. `liczby` wyłącznie z danych PSP.
8. `akcja_miesiaca` - w pierwszym dniu miesiąca wybierz najciekawsze polskie zdarzenie z poprzedniego miesiąca (jest w `wydarzenia`) i napisz omówienie: `{"id":"id wydarzenia","miesiac":"Grudzień 2026","analiza":["3 akapity"],"wnioski":["3 wnioski"],"zrodla":[[...]]}`.
8a. PRZEGLĄD POŻARNICZY W PIGUŁCE - gdy w kanale „Przegląd Pożarniczy (KG PSP)” jest numer, którego jeszcze nie ma w `przeglad_pigulka` (porównaj pole `numer`, np. „10/2026”):
   otwórz 3-4 najciekawsze artykuły tego numeru (pomiń słowo wstępne i sprawy organizacyjne), przeczytaj je w całości i dodaj NA POCZĄTEK listy `przeglad_pigulka`:
   `{"numer":"10/2026","data":"RRRR-MM-DD","link":"https://www.ppoz.pl/aktualne-wydanie","artykuly":[{"tytul":"...","link":"...","streszczenie":"3-4 zdania po ludzku","wniosek":"1 zdanie - co z tego dla strażaka lub inspektora"}]}`
   Zostaw w `wiadomosci.json` 3 ostatnie numery, starsze przenieś do `archiwum.json` (lista `przeglad_pigulka`). Streszczaj własnymi słowami, bez długich cytatów.
9. Nie ruszaj: `historia`, `sezon`, `dla_kazdego`, `wydarzenia_branzowe`, `wydarzenia_gdzie_szukac` - chyba że pojawi się nowe potwierdzone wydarzenie branżowe.
11. BAZA WIEDZY - `archiwum.json`: nic z niego nie usuwaj. Przenoś tam (na początek odpowiedniej listy, bez duplikatów po `id`/`tytul`/`tekst`/`p`): wydarzenia starsze niż 30 dni, pytania starsze niż 30 dni, minione terminy, sprawy z `obserwuje` zakończone lub bez nowych informacji od 60 dni, a z list `tipy`, `czywiesz`, `faktmit`, `wyroki`, `przepisy`, `nowosci`, `badania`, `baterie` - najstarsze pozycje, gdy lista w `wiadomosci.json` przekroczy 15 (w `wiadomosci.json` zostaw 15 najnowszych). Do każdej przenoszonej pozycji bez daty dopisz `"zarchiwizowano":"RRRR-MM-DD"`.
10. Zapisuj plik tak samo jak jest sformatowany: `json.dump(d, f, ensure_ascii=False, indent=1)` - inaczej zmienia się cały plik. Sprawdź poprawność JSON (`python3 -m json.tool wiadomosci.json`). Tak samo zapisuj `archiwum.json`. Zrób commit (oba pliki) i push do gałęzi `main` tego repozytorium. Wiadomość commita po angielsku, w trybie rozkazującym, np. „Update news for 2026-11-21”.

## Krok 4 - bez Telegrama
Nie wysyłaj nic na Telegram ani nigdzie indziej. Tomek czyta wszystko w aplikacji.

## Na koniec
Krótkie podsumowanie: ile wpisów RSS, co dodano do których sekcji, czy push się udał.
