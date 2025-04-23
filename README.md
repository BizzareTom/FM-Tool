Dies ist ein kleines Modding-Tool, um das Bearbeiten von Grafiken für den EA Fussballmanager 13/14 zu vereinfachen.
Derweilen sind drei Features nutzbar.
Im Cities-Reiter, kann man ein Stadtbild geben. Dort wird ein zentraler Bildausschnitt gewählt und automatisch im Grafikpfad abgespeichert.
Im Stadiums-Reiter, passiert Gleiches - nur, dass hier direkt alle Größen in einem Schritt gespeichert werden.
Im Badges-Reiter kann man ein Bild einpflegen, mit einem Rahmen das Wappen auf dem Bild wählen und dort wird dann der Hintergrund entfernt, das Bild
nachträglich zentriert und in allen Zielgrößen im Zielordner ausgegebeben.

### Installation

Eine .exe wird bald bereitgestellt, bis dahin ist nur die manuelle Installation mit Python möglich. Hierzu den Code herunterladen, im Terminal öffnen und `pip install .` ausführen.

### Konfiguration

Beim ersten Start der Software legt diese eine Konfigurationsdatei `directories.ini` an und teilt den Speicherort dieser Datei mit. Diese muss anschließend ausgefüllt werden. `fm_main_dir` zeigt dabei auf den Installationsordner des Spiels und `fm_graphics_dir` auf das Grafikverzeichnis in den eigenen Dokumented. Die fertige Datei sieht dann in etwa so aus:

```
[Directories]
fm_main_dir = C:\Programme\EA Games\FIFA Manager 14
fm_graphics_dir = C:\Benutzer\Name\Documents\FM\Graphics
```
