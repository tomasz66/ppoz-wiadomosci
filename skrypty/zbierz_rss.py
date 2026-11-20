"""Zbiera najnowsze wpisy z kanałów RSS (zrodla.json) do pliku rss.json - bez AI, bez kosztów.

Uruchamiany codziennie przez GitHub Actions (.github/workflows/rss.yml).
Wynik czyta zakładka Wiadomości w aplikacji Inspektor PPOŻ (sekcja „Najnowsze z kanałów”).
"""

import json
import re
import ssl
import urllib.request
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree

GODZIN_WSTECZ = 72
LIMIT_OPISU = 260
LIMIT_WPISOW = 80
NA_ZRODLO = 8
TIMEOUT_S = 25
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
ATOM = "{http://www.w3.org/2005/Atom}"
KATALOG = Path(__file__).resolve().parent.parent

# Pomijane tematy bez wartości dla inspektora (budżety, kadry, reklamy)
POMIJAJ = re.compile(r"budget|budżet|sponsor|giveaway|award|nagrod|contract|przetarg|appoint|black week|sale\b|\bnames\b|\bhires\b|\bVP\b|investor|top workplace|promot|nabory|nabór", re.I)


def pobierz(url):
    zadanie = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        return urllib.request.urlopen(zadanie, timeout=TIMEOUT_S).read()
    except ssl.SSLError:
        # Niektóre uczelnie mają niepełny łańcuch certyfikatów - treść jest publiczna, tylko odczyt
        return urllib.request.urlopen(zadanie, timeout=TIMEOUT_S, context=ssl._create_unverified_context()).read()


def data_wpisu(tekst):
    if not tekst:
        return None
    tekst = tekst.strip()
    try:
        return parsedate_to_datetime(tekst)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(tekst.replace("Z", "+00:00"))
    except ValueError:
        return None


def oczysc(html):
    tekst = re.sub(r"<[^>]+>", " ", html or "")
    tekst = re.sub(r"The post .* appeared first on .*|The post .* first appeared on .*", "", tekst)
    tekst = re.sub(r"\s+", " ", tekst).strip()
    return tekst[:LIMIT_OPISU]


def wpisy(xml):
    # Wycięcie śmieci po zamknięciu dokumentu (zdarza się w niektórych kanałach)
    koniec = max(xml.rfind(b"</rss>"), xml.rfind(b"</feed>"))
    if koniec > 0:
        xml = xml[: koniec + 7]
    korzen = ElementTree.fromstring(xml)
    for el in korzen.iter("item"):
        yield el.findtext("title"), el.findtext("link"), el.findtext("pubDate"), el.findtext("description")
    for el in korzen.iter(f"{ATOM}entry"):
        link = el.find(f"{ATOM}link")
        yield (el.findtext(f"{ATOM}title"), link.get("href") if link is not None else None,
               el.findtext(f"{ATOM}published") or el.findtext(f"{ATOM}updated"), el.findtext(f"{ATOM}summary"))


def main():
    teraz = datetime.now(timezone.utc)
    # Źródła wydawane rzadko (miesięcznik, kwartalnik) mają w zrodla.json dłuższe okno „godzin”
    zrodla = json.loads((KATALOG / "zrodla.json").read_text(encoding="utf-8"))
    wynik, bledy = [], []

    for z in zrodla:
        try:
            lista = list(wpisy(pobierz(z["rss"])))
        except Exception as blad:
            bledy.append(f"{z['nazwa']}: {type(blad).__name__}")
            continue
        nowe = []
        granica = teraz - timedelta(hours=z.get("godzin", GODZIN_WSTECZ))
        for tytul, link, data, opis in lista:
            kiedy = data_wpisu(data)
            if not tytul or not link or kiedy is None or kiedy.tzinfo is None or kiedy < granica or kiedy > teraz + timedelta(hours=1):
                continue
            if POMIJAJ.search(tytul):
                continue
            nowe.append({"zrodlo": z["nazwa"], "kraj": z["kraj"], "typ": z["typ"], "tytul": tytul.strip(),
                         "link": link.strip(), "data": kiedy.astimezone(timezone.utc).isoformat(timespec="minutes"),
                         "opis": oczysc(opis)})
        wynik.extend(nowe[:NA_ZRODLO])

    wynik.sort(key=lambda w: w["data"], reverse=True)
    dane = {"aktualizacja": datetime.now(timezone.utc).isoformat(timespec="minutes"), "wpisy": wynik[:LIMIT_WPISOW], "bledy": bledy}
    (KATALOG / "rss.json").write_text(json.dumps(dane, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Zapisano {len(dane['wpisy'])} wpisów, błędy: {len(bledy)}")


if __name__ == "__main__":
    main()
