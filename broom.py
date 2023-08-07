import argparse
import sys
import os.path

# Largeur de la barre de pourcentage
PERCENT_BAR_WIDTH = 30

############## Gestion des arguments ########################
parser = argparse.ArgumentParser()
parser.add_argument('input_file', help='Fichier .rsmi à nettoyer')
parser.add_argument('output_file', help='Fichier .rsmi de sortie, doit être différent du fichier d\'entrée. Si le fichier est non vide, alors par défaut, le résultat est envoyé en fin de fichier. Attention, aucun saut de ligne n\'est effectué en fin de fichier.')
parser.add_argument('-q', '--quiet', help='N\'affiche rien en console, sinon où en est le nettoyage (en pourcentage de réactions traitées), le nombre de réactions déjà traitées et combien ont été conservées, quelle réaction est en cours de traitement.', action='store_true')
parser.add_argument('-f', '--force', help='Si le fichier de sortie existe, écrase le fichier. Si l\'option est désactivée et que le fichier de sortie existe alors rien ne se passe.', action='store_true')
args = parser.parse_args()


############## Vérification des entrées ########################
if not os.path.isfile(args.input_file):
    print("Le fichier d'entrée %s n'existe pas." % args.input_file, file=sys.stderr)
    sys.exit(-1)

if not args.force and os.path.isfile(args.output_file):
    print("Le fichier de sortie %s existe. Utiliser l'option -f pour l'écraser." % args.output_file, file=sys.stderr)
    sys.exit(-1)

if args.input_file == args.output_file:
    print("Fichier d'entrée et de sortie identiques. Impossible de continuer.", file=sys.stderr)
    sys.exit(-1)

############## Préliminaires ########################

if not args.quiet:
    print()
    print()
    print()


# Compte les lignes du fichiers (pour l'affichage uniquement)
total = 0
for line in open(args.input_file, 'rb'):
    total += 1

class Reaction:
    # Classe utile pour stocker des réactions, ie des tuples de réactions et produits

    def __init__(self, reacts, prods):
        self.reacts = reacts
        self.prods = prods

    def __eq__(self, other):
        return self.reacts == other.reacts and self.prods == other.prods

    def __hash__(self):
        return hash((self.reacts, self.prods))

# Ensemble sauvegardant l'ensemble des 
saved = set()
nbsaved = 0

def prt(current_index):
    # Affiche des informations sur l'itération en cours, sauf si quiet est activé.

    if args.quiet:
        return
    
    # Effacter les 3 dernières lignes de la console
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")
    
    # Compter le pourcentage et le pourtrentage
    p100 = int(current_index / (total - 1) * 100)
    p30 = int(current_index / (total - 1) * 30)

    # Afficher les informations relatives.
    print('> Done : %d / %d, %d%% < ' % (current_index + 1, total, p100))
    print('[' + '=' * (p30 - 1) + '>' + ' ' * (30 - p30) + ']')
    print('> Removed : %d / %d < ' % (current_index + 1 - len(saved), current_index + 1))


# Ouverture du fichier d'entrée
with open(args.input_file) as f:
    # Ouverture du fichier de sortie
    with open(args.output_file, 'w') as g:

        # On ignore la première ligne
        f.readline()
        for i, line in enumerate(f):
            # On sépare la réaction du reste de la ligne
            line2 = line.split('\t')[0]
            line2 = line2.split(' ')[0]

            # On sépare les molécules réactifs et produits
            mols = line2.split('>')

            # On sépare chacune des molécules réactives, et de même les produits
            reacts = frozenset(mols[0].split('.'))
            prods = frozenset(mols[-1].split('.'))
            reaction = Reaction(reacts, prods)

            # On essaie de mettre la réaction dans la base
            saved.add(reaction)

            # Si ça a marché, alors on met a jour le fichier de sortie.
            if len(saved) != nbsaved:
                nbsaved += 1
                g.write(line2 + '\n')
                #sys.stdout.flush()

            # Et on affichche les infos de l'itération en cours.
            prt(i)

