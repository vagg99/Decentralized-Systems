>Εκτέλεση του crawler.py

Δημιουργία αρχείων 
- 'scientist_info.txt' 
- 'scientist_info.json' 
- 'failed_entries_scientist_info.txt' 

εντός του φακέλου 'Text-Outputs'

** Το 'scientist_info.txt' χρησιμοποιείται ως input dataset στην εκτέλεση του αλγορίθμου CHORD. 
Η δομή του είναι διαδοχικές γραμμές με πληροφορίες για τον κάθε επιστήμονα. 

------------------------------------------------------------------------
>Ανάλυση 1

    -Επιστήμονας 1
    -Επιστήμονας 2
    - ...
    -Επιστήμονας Ν

με Ν = 494 χρήσιμα entries


------------------------------------------------------------------------
>Ανάλυση 2 (σε λεπτομέρεια γραμμής)

    -Επίθετο 1 
    -Βραβεία 1
    -Εκπαίδευση 1
    -Επίθετο 2 
    -Βραβεία 2
    -Εκπαίδευση 2
    - ...
    -Επίθετο Ν 
    -Βραβεία Ν
    -Εκπαίδευση Ν

ομοίως με Ν = 494 χρήσιμων πληροφοριών, αλλά με τριπλασιασμό των γραμμών (494*3=1482) 
λόγω της δομής {Surname, Awards, Education} που τηρεί ο κάθε επιστήμονας. 


-------------------------------------------------------------------------

>'scientist_info.json'
    
    Το JSON αρχείο προσφέρεται ως εναλλακτική για αξοιοποίηση πιο τυποποιημένης υλοποίησης.
    -> Χαρακτήρες που δεν περιγράφονται στο standard λατινικό αλφάβητο, εμφανίζονται διαφορετικά.
------------------------
>'failed_entries_scientist_info.txt' 

    Για καταγραφή τελικών αποτυχημένων entries, τα οποία με εντατικότερη αναζήτηση - ενδεχομένως - να κατέληγαν ως χρήσιμα entries.
    Στην παρούσα φάση για λόγους ασφάλειας παραλείπονται από το τελικό dataset.