#Importere moduler
import csv
import sqlite3
import warnings
from tkinter import PhotoImage
from tkinter import ttk

import customtkinter #pip3 install customtkinter
from CTkMessagebox import CTkMessagebox #pip install CTkMessagebox

#Lager en sqlite database med navnet GamasjerASDatabase
conn = sqlite3.connect('GamasjerASDatabase.db') 
c = conn.cursor() #Definerer C som cursor. 

#Her er funksjonen som lager strukturen på databasen, altså tabellene med kolonnene osv.
def FunkDatabaseStruktur():
    #Her lager jeg en tabell som heter brukerliste, jeg gjør ID om til en Integer og primary key, sånn at alle har en unik ID og at den er tall.
    #Jeg legger til AUTOINCREMENT som gjør at den automatisk lager ID tallene sånn at det går ifra 1 og oppover.
    #Jeg bruker VARCHAR for å begrense antall karakterer i feltet, også bruker jeg UNIQUE sånn at ingen kan ha samme telefonnummer og epost som blir kalt for secondary key. 
    c.execute('''
            CREATE TABLE IF NOT EXISTS Brukerliste (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Fornavn VARCHAR(25),
                Etternavn VARCHAR(30),
                Epost VARCHAR(50) UNIQUE,
                Telefonnummer INTEGER UNIQUE, 
                Postnummer INTEGER
            )
        ''')

    conn.commit()
    #Her gjør jeg det samme men med postnummerlisten, det eneste som skal være unikt i denne listen er postnummerene. 
    c.execute('''
            CREATE TABLE IF NOT EXISTS Postnummerliste (
                Postnummer PRIMARY KEY,
                Poststed,
                Kommunenummer,
                Kommunenavn, 
                Kategori
            )
        ''')

    conn.commit()

#Importere Brukerliste CSV
def FunkImporterCSV():
    conn = sqlite3.connect('GamasjerASDatabase.db') 
    c = conn.cursor()
    try:
        with open('Brukerdatabase.csv', 'r') as csvfil: #Åpner opp csv filen
            lescsv = csv.reader(csvfil) #Bruker csv modulens reader funksjon til å lese csvfilen.
            next(lescsv)  #Hopper over første raden 

            for row in lescsv: #For hver rad i csv filen blir informasjonen settet inn i kollonene under som ligger i brukerliste tabellen.

                c.execute('''
                    INSERT INTO Brukerliste(
                          Fornavn, 
                          Etternavn, 
                          Epost, 
                          Telefonnummer, 
                          Postnummer
                          )
                    VALUES(?, ?, ?, ?, ?)''', row)

            conn.commit() 
        #Gir en melding at det fungerte hvis det har fungert.
        CTkMessagebox(title="Importering fullført", message="Brukerene har blitt importert i databasen.",
                  icon="check", option_1="Fortsett")
    #Hvis det ikke fungerer gir det en melding om at det ikke har fungert, og da blir selve erroren også lagt til i meldingen. 
    except Exception as e:
        CTkMessagebox(title="Feilmelding", message=f"Importering av Brukerliste feilet!: {e}", icon="cancel")
    finally:
        conn.close() #Lukker databasen. 


#Importere Post CSV
def FunkImporterPostCSV():
    conn = sqlite3.connect('GamasjerASDatabase.db') 
    c = conn.cursor()
    #Samme kode her som da vi importerte brukerene, bare forskjellige csv fil og tabell/kolonner.
    try:
        with open('Postnummerregister.csv', 'r') as csvfil: 
            lescsv = csv.reader(csvfil)  
            next(lescsv) 

            for row in lescsv: 
                c.execute('''
                    INSERT INTO Postnummerliste(
                          Postnummer,
                          Poststed,
                          Kommunenummer,
                          Kommunenavn,
                          Kategori
                          )
                    VALUES(?, ?, ?, ?, ?)''', row) 

            conn.commit() 
        CTkMessagebox(title="Importering fullført", message="Postnummere har blitt importert i databasen.",
                  icon="check", option_1="Fortsett")
    except Exception as e:
        CTkMessagebox(title="Feilmelding", message=f"Importering av Postnummerliste feilet!: {e}", icon="cancel")
    finally:
        conn.close()


#Funksjon som sletter brukere
def FunkSlettBrukere():
    conn = sqlite3.connect('GamasjerASDatabase.db') 
    c = conn.cursor()
    try:
        c.execute('''DELETE FROM Brukerliste''') #Sletter alt sammen som ligger inne i brukerliste tabellen.
        c.execute('''DELETE FROM sqlite_sequence''') 
        #Siden jeg har brukt AUTOINCRIMENT, så vil det bli lagret informasjon i tabellen sqlite_sequence, selv om jeg sletter alt ifra brukertabellen vil det fortsatt være info der,
        #Sånn at hvis jeg skal importere brukere vil IDen starte på 201 selv om brukerene har blitt slettet pga infoen i sqlite_sequence. Derfor slettet jeg alt i den også. 
        conn.commit()
        CTkMessagebox(title="Sletting fullført", message="Brukerene har blitt slettet i databasen.",
                  icon="check", option_1="Fortsett") #Her får man opp en melding hvis det fungerer.
    except Exception as e:
        CTkMessagebox(title="Feilmelding", message=f"Sletting av Brukerliste feilet!: {e}", icon="cancel") #Her får man opp en feilmelding hvis det ikke fungerer, og der står også erroren. 
    finally:
        conn.close() #Tilslutt lukker jeg connection.

#Funksjon som sletter posttabellen
def FunkSlettPost():
    conn = sqlite3.connect('GamasjerASDatabase.db') 
    c = conn.cursor()
    #Det her blir akkurat samme kode som forgje, men at det er i postnummerliste tabellen, og at jeg ikke trenger og slette en sqlite_sequence siden jeg ikke har ID på postnummerene.
    try:
        c.execute('''DELETE FROM Postnummerliste''') 
        conn.commit()
        CTkMessagebox(title="Sletting fullført", message="Postnummerene har blitt slettet i databasen.",
                  icon="check", option_1="Fortsett")
    except Exception as e:
        CTkMessagebox(title="Feilmelding", message=f"Sletting av Postnummerliste feilet!: {e}", icon="cancel") 
    finally:
        conn.close() #Lukker connection

#Funksjon som søker opp kunder
def FunkSearchBrukere(id):
    conn = sqlite3.connect('GamasjerASDatabase.db')
    c = conn.cursor()
    try:
        #Her joiner vi sammen postnummere ifra postnummerlisten med postnummerene i brukerlisten. Så velger vi og vise allt sammen bortsett fra postnummerene i postnummerlisten sånn at det ikke postnummerene blir duplikert. 
        #Så velger vi at IDen må matche det man skriver inn når man skal søke opp brukeren. 
        c.execute('''
                SELECT
                    Brukerliste.ID,
                    Brukerliste.Fornavn,
                    Brukerliste.Etternavn,
                    Brukerliste.Epost,
                    Brukerliste.Telefonnummer,
                    Brukerliste.Postnummer,
                    Postnummerliste.Poststed,
                    Postnummerliste.Kommunenummer,
                    Postnummerliste.Kommunenavn,
                    Postnummerliste.Kategori
                FROM Brukerliste 
                JOIN Postnummerliste 
                ON Postnummerliste.Postnummer = Brukerliste.Postnummer
                WHERE Brukerliste.ID = ?
                ''', (id,))
        rows = c.fetchall() #Her fanger den det opp og lagrer det i rows.
        conn.close()
        return rows #Her returner vi rows.
    except Exception as e:
        CTkMessagebox(title="Feilmelding", message=f"Noe gikk galt: {e}", icon="cancel") #Gir feilmelding hvis det ikke fungerer. 


#Main
def main():
    FunkDatabaseStruktur() #Kjører funksjonen som lager database strukturen.
    warnings.filterwarnings("ignore", category=UserWarning, module='customtkinter') #Ignorerer en advarsel som kommer pga bruk av Tkinter Photoimage istedet for customtkinter photoimage.


    window = customtkinter.CTk() #Lager vinduet
    window.title('Gamasjer AS') #Tittel på vinduet
    window.after(0, lambda:window.state('zoomed')) #Vinduet starter maksimert. Dette funket på laptoppen, men ikke når jeg hadde en ekstern skjerm koblet til i laptoppen. Hvis det ikke funker sett vinduet til maksimert når du starter det for best mulig opplevelse. 


    customtkinter.set_appearance_mode("dark") #Setter modusen til dark mode.
    customtkinter.set_default_color_theme("green") #Setter farge temaet til grønn.

    tabview = customtkinter.CTkTabview(window) #Lager en tabview.
    tabview.pack(padx=20, pady=20) #Bruker pack sånn at tabview syntes, definerer størelsen på tabviewen. 

    #Lager de forskjellige tabbene. 
    varTab1 = tabview.add("Startside")  
    varTab2 = tabview.add("Legg til innhold")  
    varTab3= tabview.add("Fjern innhold")  
    varTab4= tabview.add("Søk i kundedatabase")  
    tabview.set("Startside") #Gjør sånn at dette er den første man får opp når man starter programmet. 

    #Lager en overskrift og et paragraf. Velger hvilke tab det skal være i, velger font størrelse, og marginene.
    varVelkommenOverskrift = customtkinter.CTkLabel(varTab1, text="Velkommen til Gamasjer AS sitt database verktøy!", font=("Arial", 20)).pack(pady=5)
    varVelkommenParagrapf = customtkinter.CTkLabel(varTab1, text="Dette programmet er utviklet for å administrere en brukerdatabase med funksjoner, inkludert import av brukere fra CSV-filer, opprette en ren database, slette brukere og søke etter brukere. \n\nDen bruker SQLite for databasebehandling og tilpasset tkinter for det grafiske brukergrensesnittet. Nøkkelfunksjoner inkluderer import av brukere og postnumre, sletting av brukere og postnumre, og søk etter brukere etter ID.", font=("Arial", 12), wraplength=500, justify='left').pack(pady=5)

    #Legger til en logo. Bruker photoimage funksjonen til å dette, ganske enkel kode. 
    varBilde = PhotoImage(file="logo.png")
    varBildeLabel = customtkinter.CTkLabel(varTab1, image=varBilde, text="").pack(pady=15)


    #Ganske enkel kode, her legger jeg til labels, paragraf, og knapper. Jeg linker knappene til de forskjellige funksjonene sånn at man kan kjøre de via knapper. 
    varLeggtilLabel = customtkinter.CTkLabel(varTab2, text="Legg til innhold i databasen", font=("Arial", 20)).pack(pady=5)
    varLeggtilParagraf = customtkinter.CTkLabel(varTab2, text="Her kan du administrere innholdet i databasen din ved å legge til og oppdatere data. Først kan du opprette en ny database ved å klikke på Lag en database - dette vil sette opp strukturen som trengs for å lagre informasjonen din. Deretter kan du bruke Importer brukere i databasen for å legge til nye brukerdata fra en CSV-fil, og Importer postnummer i databasen for å legge til postnummerinformasjon på samme måte.\n\nMed disse verktøyene kan du enkelt administrere og oppdatere innholdet i databasen din for å sikre nøyaktig og oppdatert informasjon.", font=("Arial", 12), wraplength=500, justify='left').pack(pady=5)
    varImporterCSV = customtkinter.CTkButton(varTab2, text="Importer brukere i databasen", font=("Arial", 15), width=250, command=FunkImporterCSV).pack(pady=3)
    varImporterPostCSV = customtkinter.CTkButton(varTab2, text="Importer postnummer i databasen", font=("Arial", 15), width=250,command=FunkImporterPostCSV).pack(pady=3)

    #Samme kode her, definerer fargen sånn at det passer med tanke på at man skal fjerne noe. 
    varFjernLabel = customtkinter.CTkLabel(varTab3, text="Fjern innhold ifra databasen", font=("Arial", 20)).pack(pady=5)
    varFjernParagraf = customtkinter.CTkLabel(varTab3, text="Her kan du fjerne innhold fra databasen ved å slette brukere eller postnummer. Ved å klikke på Slett brukere, vil du kunne fjerne brukerdata fra databasen din. Dette kan være nyttig hvis du for eksempel ønsker å rydde opp i gamle eller unødvendige brukerprofiler. Tilsvarende kan du bruke Slett postnummere for å fjerne postnummerinformasjon som ikke lenger er relevant eller nøyaktig.\n\nDisse verktøyene gir deg kontroll over databasens innhold ved å tillate deg å fjerne unødvendig eller utdatert informasjon med letthet.", font=("Arial", 12), wraplength=500, justify='left').pack(pady=5)
    varSlettBrukere = customtkinter.CTkButton(varTab3, text="Slett brukere", fg_color="red", hover_color="maroon", width=250, command=FunkSlettBrukere).pack(pady=3)
    varSlettPost = customtkinter.CTkButton(varTab3, text="Slett postnummere", fg_color="red", hover_color="maroon", width=250, command=FunkSlettPost).pack(pady=3)

    #En funksjon som oppdaterer tabellen i GUI,det skapte problemer å ha den utenom så da var det lettest og bare ha den inne i main.
    def OppdaterTabell():
        conn = sqlite3.connect('GamasjerASDatabase.db')
        c = conn.cursor()
        for i in tree.get_children(): 
            tree.delete(i) #Sletter alt som ligger i treeview(tabellen)
        try:
            #Joiner sammen alt bortsett fra postnummer ifra postnummer listen sånn at det ikke blir duplikat. Sorterer etter ID sånn at det blir mer ryddig.
            c.execute('''
                SELECT
                    Brukerliste.ID,
                    Brukerliste.Fornavn,
                    Brukerliste.Etternavn,
                    Brukerliste.Epost,
                    Brukerliste.Telefonnummer,
                    Brukerliste.Postnummer,
                    Postnummerliste.Poststed,
                    Postnummerliste.Kommunenummer,
                    Postnummerliste.Kommunenavn,
                    Postnummerliste.Kategori
                FROM Brukerliste 
                JOIN Postnummerliste 
                ON Postnummerliste.Postnummer = Brukerliste.Postnummer
                ORDER BY Brukerliste.ID      
                ''') 
                
            resultat = c.fetchall() #Lagrer det i en variable som heter resultat

            
            for row in resultat:
                tree.insert("", "end", values=row) #Setter inn resultatene i hver rad i treeview.

        except Exception as e:
            CTkMessagebox(title="Feilmelding", message=f"Noe gikk galt: {e}", icon="cancel") #Gir error hvis det ikke fungerer.
        #Kjører funksjonen hvert 10 sekund, det var dette som skapte problemer når jeg skulle integrere den med FunkAddITabell.
        window.after(10000, OppdaterTabell)
    
    #En funksjon som oppdaterer tabellen med resultatet ifra det man skriver inn i search entry sånn at man får opp info om brukeren.
    def FunkSearchOppdatering():
            for i in tree.get_children():
                tree.delete(i) #Sletter det som er i tabellen.
            for row in FunkSearchBrukere(varSearchEntry.get()): 
                tree.insert("", "end", values=row) #Henter det man skriver inn entry feltet, setter inn informasjonen ifra FunkSearchBrukere og setter det inn i hver kolonne.
            rows = FunkSearchBrukere(varSearchEntry.get())
            if not rows: #Hvis man skriver inn en bruker som ikke finnes så får man en advarsel. 
                CTkMessagebox(title="Advarsel", message="Brukeren finnes ikke!!!", icon="warning")
                return

    #KLabels og knapper, og en entry hvor man kan skrive inn bruker ID. Bruker grid sånn at jeg kan ha flere widgets ved siden av hverandre. 
    varSearchLabel = customtkinter.CTkLabel(varTab4, text="Søk i kundedatabasen", font=("Arial", 20)).grid(row=0, column=0, columnspan=2)
    varSearchEntry = customtkinter.CTkEntry(varTab4, width=350, placeholder_text="Skriv in kunde ID...")
    varSearchEntry.grid(row=1, column=0, sticky='e')
    varSearchButton = customtkinter.CTkButton(varTab4, text="Søk", width=20, command=FunkSearchOppdatering)
    varSearchButton.grid(row=1, column=1, sticky='w')

    #Her definerer jeg fargene og font størrelse som jeg skal bruke for å endre på hvordan treeview(tabellen) ser ut. 
    bg_color = window._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"])
    text_color = window._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkLabel"]["text_color"])
    selected_color = window._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
    header_color = window._apply_appearance_mode(customtkinter.ThemeManager.theme["CTkButton"]["fg_color"])
    font_size = 14
    header_font_size = 16

    #Her velger jeg hvordan treeviewet skal se ut og legger til de fargene jeg definerte tidligere.  
    treestyle = ttk.Style()
    treestyle.theme_use('default')
    treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, font=('Helvetica', font_size), borderwidth=0)
    treestyle.configure("Treeview.Heading", background=header_color, foreground=text_color, font=('Helvetica', header_font_size),)
    treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
    window.bind("<<TreeviewSelect>>", lambda event: window.focus_set())

    #Her lager jeg treeviewet, jeg lager de forskjellige kolonnene først, også velger jeg hva headingen på kolonnen skal være, i dette tilfellet valgte jeg at de heter det samme.
    tree = ttk.Treeview(varTab4, columns=("ID", "Fornavn", "Etternavn","Epost", "Telefonnummer", "Postnummer", "Poststed", "Kommunenummer", "Kommunenavn", "Kategori"), show='headings')
    tree.heading("ID", text="ID")
    tree.heading("Fornavn", text="Fornavn")
    tree.heading("Etternavn", text="Etternavn")
    tree.heading("Epost", text="Epost")
    tree.heading("Telefonnummer", text="Telefonnummer")
    tree.heading("Postnummer", text="Postnummer")
    tree.heading("Poststed", text="Poststed")
    tree.heading("Kommunenummer", text="Kommunenummer")
    tree.heading("Kommunenavn", text="Kommunenavn")
    tree.heading("Kategori", text="Kategori")
    
    #Her bruker jeg grid igjen, også bruker width til å endre størrelsen på kolonnene. Disse innstillingene er tilpasset sånn at det er best på laptoppen min. Men man kan også justere kolonne bredde inne på GUIen ved å dra. 
    tree.grid(row=3, column=0, columnspan=2, pady=(25, 0 ))
    tree.column("ID", width=70)
    tree.column("Fornavn", width=120)
    tree.column("Etternavn", width=150)
    tree.column("Epost", width=290)
    tree.column("Telefonnummer", width=170)
    tree.column("Postnummer", width=70)
    tree.column("Poststed", width=100)
    tree.column("Kommunenummer", width=120)
    tree.column("Kommunenavn", width=120)
    tree.column("Kategori", width=70)

    #Her kjører jeg funksjonene som adder informasjonen i tabellen og oppdaterer den.
    OppdaterTabell()

    window.mainloop() #Her kjører jeg GUI vinduet. 
   
if __name__ == "__main__":
    main() #Kjører main