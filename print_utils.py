import re
import math

EMPTY_SLOT = ' '
FULL_SLOT = 'o'

INTERNALSEPARATOR = "─"

GRIDANGLE = '+'
GRIDVERTICAL = '|'
GRIDHORIZONTAL = '-'

ANNIDATE_LEVEL = 0
PAGE_WIDTH = [120]

class bcolors:
    MAGENTA = '\033[95m'
    
    BLUE = '\033[94m'  # GENERIC_POKEMON
    CYAN = '\033[96m'  # SHINY_GENERIC_POKEMON
    GREEN = '\033[92m'  # PRESENT_POKEMON
    YELLOW = '\033[93m'  # SHINY_PRESENT_POKEMON
    RED = '\033[91m'  # ABSENT_POKEMON
    
    RESET = '\033[0m'  # ENDC
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
def insert_substrings(text, insertions, offset=0):
    # Calcola la lunghezza della stringa di testo
    text_len = len(text)
    
    # Filtro le inserzioni per mantenere solo quelle con indici compresi tra offset e offset + lunghezza del testo
    # Questo serve a limitare gli indici validi per l'inserimento delle sottostringhe
    insertions = [(substring, index) for substring, index in insertions if offset <= index < offset + text_len - 1]
    
    # Riduce tutti gli indici di offset. Questo è necessario per "traslare" gli indici
    # rispetto all'offset, così che il nuovo indice sia relativo alla parte di stringa
    # a partire da "offset"
    insertions = [(substring, index - offset) for substring, index in insertions]
    
    # Ordina le coppie (sottostringa, indice) in base all'indice in ordine decrescente.
    # Ordinando in ordine decrescente si evita che l'inserimento di una sottostringa
    # cambi la posizione delle altre sottostringhe da inserire (evitandosi sovrapposizioni)
    insertions.sort(key=lambda x: x[1], reverse=True)
    
    # Ciclo per eseguire gli inserimenti, partendo dalla fine (grazie all'ordinamento decrescente)
    # In questo modo possiamo inserire le sottostringhe senza modificare gli indici
    # delle altre sottostringhe che devono ancora essere inserite
    for substring, index in insertions:
        # Inserisce la sottostringa prima dell'indice specificato
        # text[:index] prende la parte della stringa prima dell'indice
        # text[index:] prende la parte della stringa da quell'indice in poi
        text = text[:index] + substring + text[index:]
    
    return text  # Ritorna la stringa modificata con tutte le sottostringhe inserite

def split_string_in_chunks(text, chunk_size, elipsis=False):
    # Rimuove i codici di colore ANSI (se presenti) dalla stringa di testo
    # Questo è utile per assicurarsi che il testo pulito, senza i codici di colore,
    # venga effettivamente suddiviso in chunk
    clean_text = re.sub(r'\033\[[0-9;]*m', '', text)
    
    # Se la lunghezza del testo è inferiore al chunk_size, restituisce direttamente
    # il testo intero in una lista di un solo elemento (non è necessario suddividere)
    if chunk_size >= len(clean_text):
        return [text]
    else:
        # Trova tutte le occorrenze dei codici di colore ANSI nel testo originale
        matches = re.finditer(r'\033\[[0-9;]*m', text)
        # Salva il codice di colore e la sua posizione nella stringa
        matches = [(x.group(), x.start()) for x in matches]
        
        # Creiamo una nuova lista di "match" con gli offset corretti
        new_matches = []
        cumulative_offset = 0
        for i, x in enumerate(matches):
            # Per ogni "match" calcoliamo un offset cumulativo che tiene conto dei codici
            # di colore precedenti, in modo che gli indici siano corretti
            prev_match = matches[i-1][0] if i > 0 else ''
            cumulative_offset += len(prev_match)
            
            # Regola la posizione tenendo conto dell'offset cumulativo
            new_matches.append((x[0], x[1] - cumulative_offset))
        
        # Suddividi la stringa senza codici di colore in chunk di dimensione `chunk_size`
        splitted = [clean_text[i:i+chunk_size] for i in range(0, len(clean_text), chunk_size)]
        
        if elipsis:
            splitted = [s + '…' for s in splitted]  # Aggiungi "..." alla fine di ogni chunk
            splitted[-1] = splitted[-1][:-1]  # Rimuovi l'ultimo "..." dall'ultimo chunk
            
        # Ora inseriamo i codici di colore nella stringa, usando gli indici corretti
        splitted = [insert_substrings(s, new_matches,  i*chunk_size) for i, s in enumerate(splitted)]
        
        # Lista finale dei chunk, che conterrà i pezzi di testo con i codici di colore ripristinati
        new_splitted = []
        actual_color = None  # Variabile per tenere traccia del colore attivo

        # Per ogni "chunk" separato, gestiamo i codici di colore finali
        for s in splitted:
            # Se c'era un colore precedente, lo riapplichiamo all'inizio del chunk
            if actual_color != None:
                s = actual_color + s
            
            # Trova eventuali codici di colore nel chunk
            matches_2 = re.findall(r'\033\[[0-9;]*m', s)

            if len(matches_2) > 0:
                # Se l'ultimo codice di colore non è "\033[0m", lo aggiungiamo alla fine
                # e aggiorniamo il colore attivo
                if matches_2[-1] != '\033[0m':
                    s = s + '\033[0m'
                    actual_color = matches_2[-1]
                else:
                    actual_color = None  # Nessun colore attivo
                
                # Aggiungiamo il chunk alla lista finale
                new_splitted.append(s)
            else:
                new_splitted.append(s)  # Aggiungiamo il chunk senza modifiche

        # Restituiamo la lista dei chunk con i codici di colore correttamente gestiti
        return new_splitted


def get_page_width(level):
    return PAGE_WIDTH[level]


def add_print_level(width=None): 
    """
    Aggiunge un livello di annidamento nella visualizzazione gerarchica.
    
    Stampa una linea superiore decorativa (╔═══╗) per ogni livello aggiunto 
    e aggiorna la variabile globale ANNIDATE_LEVEL per riflettere il nuovo livello di annidamento.

    Args:
        add_level (int): Numero di livelli da aggiungere (default: 1).
    """
    global ANNIDATE_LEVEL
    global PAGE_WIDTH
    
    # Se widths è una lista valida, aggiorna la larghezza della pagina
    if isinstance(width, int) and width > 0 and width <= PAGE_WIDTH[-1] - 2:
        PAGE_WIDTH.append(width)  # Aggiunge la nuova larghezza alla lista
    else:
        PAGE_WIDTH.append(PAGE_WIDTH[-1] - 2) # Aggiunge la larghezza predefinita
        
    _print_annidate_header("╔" + "═" * get_page_width(ANNIDATE_LEVEL + 1) + "╗") 
    
    ANNIDATE_LEVEL += 1  # Aggiorna il livello attuale  
            
def sub_print_level():
    """
    Riduce il livello di annidamento nella visualizzazione gerarchica.

    Stampa una linea inferiore decorativa (╚═══╝) per ogni livello rimosso 
    e aggiorna la variabile globale ANNIDATE_LEVEL per riflettere il nuovo livello di annidamento.

    Args:
        sub_level (int): Numero di livelli da rimuovere (default: 1).
    """
    global ANNIDATE_LEVEL
    
    ANNIDATE_LEVEL -= 1  # Riduce il livello attuale
    
    _print_annidate_header("╚" + "═" * get_page_width(ANNIDATE_LEVEL + 1) + "╝")
        
    PAGE_WIDTH.pop()

def _print_annidate_header(text):
    
    # Genera il prefisso con le barre verticali (║) per rappresentare il livello di annidamento
    subfix = ''
    prefix = ''
    
    accum_len = len(text)
    for i in range(ANNIDATE_LEVEL, 0, -1):
        subfix += ' ' * math.floor( (get_page_width(i) - accum_len) /2) + "║"
        prefix = "║" + ' ' * math.ceil( (get_page_width(i) - accum_len) /2) + prefix
        
        accum_len += len(' ' * (get_page_width(i) - accum_len)) + 2

    print(prefix + text + subfix)
    
    
def print_annidate(*args):
    """
    Stampa un testo formattato rispettando il livello di annidamento attuale.

    - Se la lunghezza del testo supera la larghezza della pagina, viene troncato con '...'.
    - Viene applicata una cornice con caratteri decorativi in base al livello di annidamento.
    
    Args:
        *args: Testo da stampare (può essere formato da più elementi concatenati).
    """
    to_print = ''.join(map(str, args)).splitlines()  # Converte tutti gli argomenti in stringhe e li divide in righe
    final_to_print = []  # Lista finale per il testo da stampare
    for p in to_print:
        final_to_print += split_string_in_chunks(p, get_page_width(ANNIDATE_LEVEL) - 1, elipsis=True)  # Suddivide il testo in chunk
    
    for item in final_to_print:
        line = str(item)
        clean_text = re.sub(r'\033\[[0-9;]*m', '', line)

        # Genera il prefisso  e suffisso con le barre verticali (║) per rappresentare il livello di annidamento
        subfix = ''
        prefix = ''
        accum_len = len(clean_text)
        for i in range(ANNIDATE_LEVEL, 0, -1):
            subfix += ' ' * math.floor( (get_page_width(i) - accum_len) /2) + "║"
            prefix = "║" + ' ' * math.ceil( (get_page_width(i) - accum_len) /2) + prefix
            
            accum_len = get_page_width(i) + 2
                
        print(prefix + line + subfix)


def print_internal_separator():
    """
    Stampa una linea separatrice interna utilizzando il carattere definito in INTERNALSEPARATOR.
    La lunghezza della linea è determinata dalla larghezza della pagina al livello di annidamento attuale.
    """
    print_annidate(INTERNALSEPARATOR * get_page_width(ANNIDATE_LEVEL))


def color(s, col):
    """
    Applica un colore ANSI a una stringa e la resetta alla fine.

    Args:
        s (str): Il testo da colorare.
        col (str): Il codice ANSI del colore.

    Returns:
        str: Testo colorato.
    """
    return col + s + bcolors.RESET


def get_colored_i(i, col, tot_len):
    """
    Genera un indice numerico colorato, formattandolo con zeri iniziali fino a raggiungere tot_len.

    Args:
        i (int): L'indice numerico.
        col (str): Il codice ANSI del colore.
        tot_len (int): La lunghezza totale desiderata della stringa risultante.

    Returns:
        str: Indice numerico colorato e formattato con zeri iniziali.
    """
    ret = str(i)
    while len(ret) < tot_len:
        ret = '0' + ret  # Aggiunge zeri iniziali per riempire lo spazio
    return color(ret, col)


def print_grid(grid):
    """
    Stampa una griglia di elementi, con bordi e separatori.

    - La griglia è composta da elementi separati da barre verticali (GRIDVERTICAL).
    - La larghezza degli elementi è definita da len_el.
    - Gli elementi vengono stampati in blocchi di dimensione fissa (6x6 di default).
    - Se il numero di elementi è inferiore al numero massimo della griglia, vengono aggiunti spazi vuoti.

    Args:
        grid (list): Lista di stringhe che rappresentano gli elementi della griglia.
        len_el (int): Larghezza massima di ogni elemento.
    """
    
    grid_real_len = [len(re.sub(r'\033\[[0-9;]*m', '', el)) for el in grid]
    len_el = max(1, max(grid_real_len))  # Larghezza massima dell'elemento
    
    list1 = [' '] + [' ' + item + ' ' + GRIDVERTICAL for item in grid]
    length = len(grid)
    iter_ = 6  # Dimensione del blocco (default: 6 elementi per riga)
    
    fallout = (iter_)**2 - length  # Numero di celle vuote da riempire
    if fallout:
        list1 += ['   ' + GRIDVERTICAL] * fallout  # Aggiunge celle vuote

    block = GRIDANGLE + GRIDHORIZONTAL * (len_el + 2)
    
    # Stampa la griglia riga per riga
    for i in range(0, length, iter_):
        print_annidate(block * iter_ + GRIDANGLE)  # Stampa la riga superiore della griglia
        pp = ''.join(list1[i+1:i+iter_+1])  # Stampa gli elementi della riga
        print_annidate(GRIDVERTICAL + pp)
    
    print_annidate(block * iter_ + GRIDANGLE)  # Stampa l'ultima riga della griglia
