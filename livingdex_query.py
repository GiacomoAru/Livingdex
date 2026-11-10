import json
import jellyfish
import math
import pandas as pd
from pathlib import Path
from collections import OrderedDict
import re
 
from utils.print_utils import *


PRESENT_POKEMON = bcolors.BLUE
TARGET_PRESENT_POKEMON = bcolors.GREEN
ABSENT_POKEMON = bcolors.RED
TARGET_ABSENT_POKEMON = bcolors.MAGENTA
SHINY_POKEMON = bcolors.CYAN
TARGET_SHINY_POKEMON = bcolors.YELLOW

ANSWER_WIDTH = 140
SEARCH_LIST_WIDTH = 100
BOX_LIST_WIDTH = 90
BOX_GRID_WIDTH = 35
INFO_WIDTH = 75
SMALL_INFO_WIDTH = 50

PREV_P_SEARCH = None
INDEX_PREV_P_SEARCH = -1

livingdex_location = './data/pokemon_livingdex/livingdex_09042026.csv'
livingdex = pd.read_csv(livingdex_location)
availability_location = './data/availability.csv'
availability = pd.read_csv(availability_location)

BOX_LIST = list(OrderedDict.fromkeys(livingdex['box'].values))

        
#--------------------------------------------------------------------------------------------------------------
# Funzioni utility di ricerca e gestione del Living Dex

def get_box_coord(box_name):
    dummy = BOX_LIST.index(box_name)
    box_page = str(math.trunc(dummy/30) + 1)
    box_page_row = str(math.trunc((dummy%30)/6) + 1)
    box_page_column = str((dummy % 6) + 1)

    return [box_page, box_page_row, box_page_column]

def coord_to_string(coord):
    return '[' + str(coord[0]) + '/' + str(coord[1]) + '/' + str(coord[2]) + ']'

def search_distance(small, long):
    
    # if len(small) > len(long):
    #    small, long = long, small
    
    d_1 = jellyfish.damerau_levenshtein_distance(small,long)/len(small) + (1-jellyfish.jaro_winkler_similarity(small,long))
    
    d_2 = jellyfish.damerau_levenshtein_distance(small,long.replace('-f','').replace('-m',''))/len(small) + (1-jellyfish.jaro_winkler_similarity(small,long.replace('-f','').replace('-m','')))

    d_3 = jellyfish.damerau_levenshtein_distance(small,long.replace('-gigamax','').replace('-m',''))/len(small) + (1-jellyfish.jaro_winkler_similarity(small,long.replace('-gigamax','').replace('-m','')))
    
    ret = min(d_1, d_2*1.1, d_3*1.2)
    
    
    if long.startswith(small):
        ret = ret/2
    elif small in long:
        ret =  ret/2

    return ret

#--------------------------------------------------------------------------------------------------------------
# Funzioni di ricerca e gestione del Living Dex

# funzione che restituisce un dataframe ordinato rispetto alla distanza degli input
def search(name=None, shiny=None, captured=None, gigamax=None, box=None):

    dummy = livingdex.copy()

    if box != None:
        dummy['distance_box'] = dummy['box'].apply(lambda x: search_distance(box, x))
        dummy = dummy.sort_values('distance_box', kind='stable')
    if name != None:
        dummy['distance_id'] = dummy['name'].apply(lambda x: search_distance(name, x))
        dummy = dummy.sort_values('distance_id', kind='stable')


    if shiny != None:
        dummy = dummy.loc[dummy['shiny'] == shiny]
    if captured != None:
        dummy = dummy.loc[dummy['captured'] == captured]
    if gigamax != None:
        dummy = dummy.loc[dummy['gigamax'] == bool(gigamax)]
    
    return dummy

# ricerca visiva di un pokemon
def p(request, save_next=True):
    if save_next:
        global PREV_P_SEARCH
        global INDEX_PREV_P_SEARCH 
        PREV_P_SEARCH = search(request[1])
        INDEX_PREV_P_SEARCH = 0

        find = PREV_P_SEARCH.iloc[0]
    else:
        find = search(request[1]).iloc[0]


    tot_box = livingdex.loc[livingdex['box'] == find['box']]
            

    showed_box = tot_box.drop(['box', 'ref_name', 'variant'], axis=1)
    showed_box.index = range(1, len(showed_box)+1)
    box_string = []
    
    empty_slot_mul = 2 #max(2, math.ceil(math.log10(len(showed_box)+1)))
    for index, values in showed_box.iterrows():
        if values['name'] == find['name']: 
            if values['captured'] and values['shiny']:
                box_string.append(get_colored_i(index, TARGET_SHINY_POKEMON, empty_slot_mul))
            elif values['captured']:
                box_string.append(get_colored_i(index, TARGET_PRESENT_POKEMON, empty_slot_mul))
            else:
                box_string.append(get_colored_i(index, TARGET_ABSENT_POKEMON, empty_slot_mul))
        else:
            if values['captured'] and values['shiny']:
                box_string.append(get_colored_i(index, SHINY_POKEMON, empty_slot_mul))
            elif values['captured']:
                box_string.append(get_colored_i(index, PRESENT_POKEMON, empty_slot_mul))
            else:
                box_string.append(get_colored_i(index, ABSENT_POKEMON, empty_slot_mul))
                
                
    print_annidate('CAPTURED')
    add_print_level(BOX_LIST_WIDTH)
    print_annidate(showed_box.loc[showed_box['captured']])
    sub_print_level()
    
    print_annidate('MISSING')
    add_print_level(BOX_LIST_WIDTH)
    print_annidate(showed_box.loc[showed_box['captured'] == False])
    sub_print_level()
    
    box_string = box_string + [EMPTY_SLOT*empty_slot_mul]*(30-len(box_string))
    print_annidate(f'{find['box'].upper()}  {coord_to_string(get_box_coord(find['box']))}')
    add_print_level(BOX_GRID_WIDTH)
    print_grid(box_string)
    sub_print_level()
    
    add_print_level(INFO_WIDTH)
    
    s1 = f'Pokemon finded: {find['name']}'
    s2 = f'[next pokemon: {PREV_P_SEARCH.iloc[INDEX_PREV_P_SEARCH + 1]['name']}]'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - len(s2) - 2) + s2)

    
    s1 = f'Pokemon captured: {len(showed_box.loc[showed_box['captured']])}'
    s2 = f'[{100*len(showed_box.loc[showed_box['captured']])/len(showed_box):.2f} %]'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - len(s2) - 2) + s2)
    
    s1 = f'Shiny pokemon captured: {len(showed_box.loc[showed_box['shiny']])}'
    s2 = f'[{100*len(showed_box.loc[showed_box['shiny']])/len(showed_box):.2f} %]'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - len(s2) - 2) + s2)
    
    s1 = f'Total Pokemon: {len(showed_box)}'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - 2))
    sub_print_level()

# ridcerca visiva di un box
def b(request):
        
    find = search(box=request[1]).iloc[0] 
    tot_box = livingdex.loc[livingdex['box'] == find['box']].copy()
    
    # captured_box = tot_box.loc[tot_box['captured']]
    # not_captured_box = tot_box.loc[tot_box['captured'] == False]
    
    showed_box = tot_box.drop(['box', 'ref_name', 'variant'], axis=1)
    showed_box.index = range(1, len(showed_box)+1)
    box_string = []

    empty_slot_mul = 2 #max(2, math.ceil(math.log10(len(showed_box)+1)))
    for index, values in showed_box.iterrows():
        if values['captured'] and values['shiny']:
            box_string.append(get_colored_i(index, SHINY_POKEMON, empty_slot_mul))
        elif values['captured']:
            box_string.append(get_colored_i(index, PRESENT_POKEMON, empty_slot_mul))
        else:
            box_string.append(get_colored_i(index, ABSENT_POKEMON, empty_slot_mul))

    
    # showed_box = showed_box.rename(index=dict(zip(showed_box.index,range(1, len(showed_box)+1))))

    print_annidate('CAPTURED')
    add_print_level(BOX_LIST_WIDTH)
    print_annidate(showed_box.loc[showed_box['captured']])
    sub_print_level()
    
    print_annidate('MISSING')
    add_print_level(BOX_LIST_WIDTH)
    print_annidate(showed_box.loc[showed_box['captured'] == False])
    sub_print_level()
    
    box_string = box_string + [EMPTY_SLOT*empty_slot_mul]*(30-len(box_string))
    print_annidate(f'{find['box'].upper()} {coord_to_string(get_box_coord(find['box']))}')
    add_print_level(BOX_GRID_WIDTH)
    print_grid(box_string)
    sub_print_level()
    
    
    add_print_level(INFO_WIDTH)
    
    s1 = f'Pokemon captured: {len(showed_box.loc[showed_box['captured']])}'
    s2 = f'[{100*len(showed_box.loc[showed_box['captured']])/len(showed_box):.2f} %]'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - len(s2) - 2) + s2)
    
    s1 = f'Shiny pokemon captured: {len(showed_box.loc[showed_box['shiny']])}'
    s2 = f'[{100*len(showed_box.loc[showed_box['shiny']])/len(showed_box):.2f} %]'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - len(s2) - 2) + s2)
    
    s1 = f'Total Pokemon: {len(showed_box)}'
    print_annidate(s1 + ' '*(INFO_WIDTH - len(s1) - 2))
    sub_print_level()


# ricerca di pokemon che somigliano agli imput, visualizzazione di search
def f(request, save_next=True):
    
    fin_req = [None]*2
    for i, part in enumerate(request[1:]):
        if part != '.' and part != '*':
            fin_req[i] = part

    searched = search(name=fin_req[0], box=fin_req[1]).head(25)
    if save_next:
        global PREV_P_SEARCH
        global INDEX_PREV_P_SEARCH 
        PREV_P_SEARCH = searched
        INDEX_PREV_P_SEARCH = -1

    searched['box_coord'] = [coord_to_string(get_box_coord(x)) for x in searched['box']]
    searched = searched.drop(['ref_name', 'variant'], axis=1)
    
    #print_annidate(, '\n', searched)
    
    add_print_level(SEARCH_LIST_WIDTH)
    print_annidate(searched)
    sub_print_level()
    
    add_print_level(INFO_WIDTH)
    
    s1 = f'Tot_row: {len(searched)}'
    print_annidate(s1)
    sub_print_level()
    

# aggiungi un pokemon al livingdex
def a(request):

    fin_req = []
    
    if len(request)>1:
        fin_req.append(request[1])
    else:
        fin_req.append(PREV_P_SEARCH.iloc[INDEX_PREV_P_SEARCH]['name'])
        
    if len(request)>2:
        fin_req.append(True)
    else:
        fin_req.append(False)

    searched = search(name=fin_req[0])
    find = searched.iloc[0][['name', 'distance_id']].values
    ind = searched.index[0]

    if find[1] > 0:
        print_annidate('You want to add: ', find[0], ' ?          [shiny:', str(fin_req[1])+']')

        match input():
            case 'y' | 'yes' | 'si' | 's':
                livingdex.loc[ind:ind, 'captured':'shiny'] = True, fin_req[1]
                print_annidate(find[0], ' added')
            case _:
                print_annidate('fiuuuuu...')
    else:
        livingdex.loc[ind:ind, 'captured':'shiny'] = True, fin_req[1]
        print_annidate(find[0], ' added')

# rimuovi un pokemon al livingdex
def d(request):
    fin_req = [request[1]]

    searched = search(name=fin_req[0])
    find = searched.iloc[0][['name', 'distance_id']].values
    ind = searched.index[0]

    if find[1] > 0:
        print_annidate('You want to delete: ', find[0], ' ?')
        match input():
            case 'y' | 'yes' | 'si' | 's':
                livingdex.loc[ind:ind, 'captured':'shiny'] = False, False
                print_annidate(find[0], ' deleted')
            case _:
                print_annidate('fiuuuuu...')
    else:
        livingdex.loc[ind:ind, 'captured':'shiny'] = False, False
        print_annidate(find[0], ' deleted')


# esegui p di next
def np():
    global PREV_P_SEARCH
    global INDEX_PREV_P_SEARCH 

    INDEX_PREV_P_SEARCH += 1
    #print(PREV_SEARCH, INDEX_PREV_SEARCH, PREV_SEARCH.iloc[INDEX_PREV_SEARCH])
    return p([None, PREV_P_SEARCH.iloc[INDEX_PREV_P_SEARCH]['name']], save_next=False)

def stats(request):
    """
    Stampa le statistiche del Living Dex, includendo:
    - Livello 0: Totale Pokémon, Pokémon catturati, percentuale catturati, shiny catturati e percentuale shiny
    - Livello 1: Statistiche per gruppo di box (prefisso o 'forms')
    - Livello 2: Statistiche per singolo box
    
    :param livingdex: DataFrame contenente i dati del Living Dex
    :param level: livello di dettaglio (0, 1, o 2)
    """
    
    if len(request) > 1:
        level = int(request[1])
    else:
        level = 0
    
    tmp_livingdex = livingdex
    
    # Conta Pokémon totali, catturati e shiny catturati
    total_pokemon = len(tmp_livingdex)
    captured_pokemon = tmp_livingdex['captured'].sum()
    shiny_captured = tmp_livingdex[(tmp_livingdex['shiny'] == True) & (tmp_livingdex['captured'] == True)].shape[0]
    
    # Percentuali
    captured_percentage = (captured_pokemon / total_pokemon) * 100 if total_pokemon > 0 else 0
    shiny_percentage = (shiny_captured / total_pokemon) * 100 if total_pokemon > 0 else 0
    
    # Estrai il prefisso del box (prende tutto prima di "_")
    tmp_livingdex['box_prefix'] = tmp_livingdex['box'].apply(lambda x: x.split('_')[0])

    # Unifica i box che finiscono con 'forms' sotto un unico gruppo
    tmp_livingdex['box_group'] = tmp_livingdex['box'].apply(
        lambda x: 'forms' if x.endswith('forms') else x.split('_')[0]
    )

    # Statistiche per ogni gruppo di box (prefisso o 'forms')
    box_prefix_stats = tmp_livingdex.groupby('box_group')['captured'].agg(['sum', 'count'])
    box_prefix_stats.columns = ['Captured', 'Total']

    # Statistiche per ogni box singolo
    box_stats = tmp_livingdex.groupby('box')['captured'].agg(['sum', 'count'])
    box_stats.columns = ['Captured', 'Total']

    # Aggiungere le statistiche per gli shiny catturati
    shiny_per_group = tmp_livingdex.groupby('box_group').agg(shiny_captured=('shiny', lambda x: ((x == True) & (tmp_livingdex.loc[x.index, 'captured'] == True)).sum()))
    shiny_per_box = tmp_livingdex.groupby('box').agg(shiny_captured=('shiny', lambda x: ((x == True) & (tmp_livingdex.loc[x.index, 'captured'] == True)).sum()))

    # Stampa il riepilogo in base al livello di dettaglio
    #print_annidate("=" * 50)
    print_annidate("LIVING DEX STATISTICS")
    #print_annidate("=" * 50)

    if level >= 0:
        add_print_level(SMALL_INFO_WIDTH)
        print_annidate(f"Total Pokémon: {total_pokemon}")
        print_annidate(f"Captured Pokémon: {captured_pokemon} ({captured_percentage:.2f}%)")
        print_annidate(f"Shiny Pokémon Captured: {shiny_captured} ({shiny_percentage:.2f}%)")
        sub_print_level()
        
    if level >= 1:
        print_annidate("\nSTATS PER BOX GROUP")
        add_print_level(BOX_LIST_WIDTH)
        # Aggiungere la percentuale di catturati e shiny per ogni gruppo
        box_prefix_stats['Captured %'] = (box_prefix_stats['Captured'] / box_prefix_stats['Total']) * 100
        box_prefix_stats['Shiny Captured'] = shiny_per_group['shiny_captured']
        box_prefix_stats['Shiny %'] = (box_prefix_stats['Shiny Captured'] / box_prefix_stats['Total']) * 100
        
        # Riordina le colonne
        box_prefix_stats = box_prefix_stats[['Captured', 'Captured %', 'Shiny Captured', 'Shiny %', 'Total']]
        
        # Calcola il totale e aggiungi come ultima riga
        total_row = box_prefix_stats.sum()
        total_row['Captured %'] = (total_row['Captured'] / total_row['Total']) * 100
        total_row['Shiny %'] = (total_row['Shiny Captured'] / total_row['Total']) * 100
        total_row['Shiny Captured'] = shiny_per_group['shiny_captured'].sum()

        # Aggiungi la riga totale
        box_prefix_stats.loc['Total'] = total_row
        
        # Stampa il risultato
        print_annidate(box_prefix_stats.round({'Captured %': 2, 'Shiny %': 2}).to_string())
        sub_print_level()
        
    if level >= 2:
        print_annidate("\nSTATS PER INDVIDUAL BOX")
        add_print_level(BOX_LIST_WIDTH)
        # Aggiungere la percentuale di catturati e shiny per ogni box
        box_stats['Captured %'] = (box_stats['Captured'] / box_stats['Total']) * 100
        box_stats['Shiny Captured'] = shiny_per_box['shiny_captured']
        box_stats['Shiny %'] = (box_stats['Shiny Captured'] / box_stats['Total']) * 100
        
        # Riordina le colonne
        box_stats = box_stats[['Captured', 'Captured %', 'Shiny Captured', 'Shiny %', 'Total']]
        
        # Calcola il totale e aggiungi come ultima riga
        total_row = box_stats.sum()
        total_row['Captured %'] = (total_row['Captured'] / total_row['Total']) * 100
        total_row['Shiny %'] = (total_row['Shiny Captured'] / total_row['Total']) * 100
        total_row['Shiny Captured'] = shiny_per_box['shiny_captured'].sum()

        # Aggiungi la riga totale
        box_stats.loc['Total'] = total_row
        
        # Stampa il risultato
        print_annidate(box_stats.round({'Captured %': 2, 'Shiny %': 2}).to_string())
        sub_print_level()


def g(request):
    # print(request)

    target_req = request[1]
    add_req = None
    
    if len(request) > 2:
        add_req = int(request[2])

    pokemon_games = {
    "I_R": ["Red", "R"],
    "I_G": ["Green", "G"],
    "I_B": ["Blue", "B"],
    "I_Y": ["Yellow", "Y"],
    "II_G": ["Gold", "G"],
    "II_S": ["Silver", "S"],
    "II_C": ["Crystal", "C"],
    "III_R": ["Ruby", "Ru"],
    "III_S": ["Sapphire", "Sa"],
    "III_E": ["Emerald", "E"],
    "III_FR": ["FireRed", "FR"],
    "III_LG": ["LeafGreen", "LG"],
    "Colosseum":["Colosseum"],
    "XD":["XD"],
    "IV_D": ["Diamond", "D"],
    "IV_PR": ["Pearl", "Pr"],
    "IV_PL": ["Platinum", "Pt"],
    "IV_HG": ["HeartGold", "HG"],
    "IV_SS": ["SoulSilver", "SS"],
    "V_B": ["Black", "B"],
    "V_W": ["White", "W"],
    "V_B2": ["Black 2", "B2"],
    "V_W2": ["White 2", "W2"],
    "VI_X": ["X"],
    "VI_Y": ["Y"],
    "VI_OR": ["Omega Ruby", "OR"],
    "VI_AS": ["Alpha Sapphire", "AS"],
    "VII_S": ["Sun", "S"],
    "VII_M": ["Moon", "M"],
    "VII_US": ["Ultra Sun", "US"],
    "VII_UM": ["Ultra Moon", "UM"],
    "VII_LGP": ["Let's Go Pikachu", "LGP"],
    "VII_LGE": ["Let's Go Eevee", "LGE"],
    "VIII_SW": ["Sword", "Sw"],
    "VIII_SH": ["Shield", "Sh"],
    "VIII_BD": ["Brilliant Diamond", "BD"],
    "VIII_SP": ["Shining Pearl", "SP"],
    "VIII_LA": ["Legends: Arceus", "PLA"],
    "IX_SCA": ["Scarlet", "Sca"],
    "IX_VIO": ["Violet", "Vio"],
    }
    
    min_dist = math.inf
    game = None
    for g in pokemon_games:
        for gn in pokemon_games[g]:
            if search_distance(target_req, gn.lower()) < min_dist:
                min_dist = search_distance(target_req, gn.lower())
                game = g

    searched = livingdex.merge(availability[['ref_id', 'ref_name', game]], on='ref_name', how='left')
    searched = searched.dropna(subset=[game])
    searched = searched.loc[searched['captured'] == False]
    
    show = searched.loc[:, ['ref_id', 'name']]
    show['availability'] = searched[game]
    not_available_values = ['PW', 'DR', 'DW', 'ET', 'Ev', 'TE', 'T']
    for val in not_available_values:
        show = show.loc[show['availability'] != val]
    # show = show.sort_values(by='ref_id')
    
    if add_req != None:
        show = show.loc[add_req:]
    show = show.iloc[:50]
    
    add_print_level(SEARCH_LIST_WIDTH)
    print_annidate(show)
    sub_print_level()
    
    box_width = 75
    add_print_level(box_width)
    
    s1 = f'Game: {pokemon_games[game][0]}'
    s2 = f'[{game}]'
    print_annidate(s1 + ' '*(box_width - len(s1) - len(s2) - 2) + s2)
    
    s1 = f'Tot_row: {len(searched)}'
    print_annidate(s1 + ' '*(box_width - len(s1) - 2))
    sub_print_level()

def m(request):

    # Ottieni tutti i Pokémon mancanti
    missing_df = livingdex.loc[livingdex['captured'] == False].copy()
    missing_df['box_coord'] = [coord_to_string(get_box_coord(x)) for x in missing_df['box']]

    # Rimuovi colonne inutili
    missing_df = missing_df.drop(['ref_name', 'variant'], axis=1)

    # Se c'è un argomento numerico, filtra a partire da quell'indice
    start_index = 0
    if len(request) > 1:
        try:
            start_index = int(request[1])
        except ValueError:
            pass  # ignora se non è un numero

    # Applica limite
    limited_df = missing_df.iloc[start_index:start_index + 50]

    # Stampa lista
    add_print_level(SEARCH_LIST_WIDTH)
    print_annidate(limited_df)
    sub_print_level()

    # Stampa conteggio totale mancanti
    add_print_level(INFO_WIDTH)
    s1 = f'Tot_missing: {len(missing_df)}'
    print_annidate(s1)
    sub_print_level()



def reset_index():
    livingdex['id'] = livingdex.index + 1
    
#--------------------------------------------------------------------------------------------------------------
# Inizio esecuzione del programma

# inizio ricezione imput
while True:
    
    try:
        request = str(input('Enter request:\t')).strip().lower()
        
        add_print_level(ANSWER_WIDTH)
        # print_internal_separator()
        request = request.replace('  ',  ' ').split(' ')

        match request[0]:
            case 'h' | 'help':
                width = 54
                print_annidate('COMMANDS')
                add_print_level(84)
                print_annidate(
                    'p, pokemon: Display information about a specific Pokémon.\n',
                    'n, next: Display the next Pokémon based on the previous search result.\n',
                    'b, box: Show the box based on the Pokémon currently present.\n',
                    'f, find: Search for a Pokémon with a similar name.\n',
                    'm, missing: Show the list of missing Pokémon, optionally filtered by name/box.\n',
                    'a, add: Add a new Pokémon to the Living Dex.\n',
                    'd, delete: Remove a Pokémon from the Living Dex.\n',
                    'g, game: Show missing Pokémon obtainable in a specific game.\n',
                    'stats: Display Living Dex statistics.\n',
                    'resetindex: Reset the Pokémon IDs in the Living Dex.\n',
                    'save: Save all updates to the Living Dex.\n',
                    'c, close: Close the Living Dex *without* saving changes.\n'
                )
                sub_print_level()

                
            case 'p' | 'pokemon':
                p(request)

            case 'b' | 'box':
                b(request)
                
            case 'f' | 'find': 
                f(request)

            case 'a' | 'add':
                a(request)

            case 'd' | 'delete':
                d(request)
            
            case 'n' | 'next':
                np()
                
            case 'save':
                print_annidate('salvo tutto!')
                livingdex.to_csv(livingdex_location, index=False)

            case 'stats':
                stats(request)
                # print(livingdex.value_counts().to_frame())
                
            case 'g' | 'game':
                g(request)

            case 'm' | 'missing':
                m(request)
    
            case 'c' | 'close':
                break
            
            case 'resetindex':
                reset_index()
                print_annidate('id reset')
                
            case _: 
                    
                print_annidate('eh?')

    except Exception as e:
        print_annidate(color('Valore non riconosciuto', TARGET_SHINY_POKEMON))
        print_annidate(e)
    
    sub_print_level()

print_annidate('Ciao ciao, addio')
sub_print_level()
# livingdex.to_csv(file_location)