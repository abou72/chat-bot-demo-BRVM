# on va cree un chatbot demo sur la brvm le principe est que le chat est base sur un discours par mot cle

#les pre requis sont la librairie NLTK

from nltk.chat.util import Chat, reflections

#Definir le dialogue
pairs = [
    ["bonjour", ["Bonjour bienvenue, je suis le chatbot de la BRVM et je repond a toutes vos questions! "]],
    ["(Bonjour|Salut|hello)", [" Bonjour comment puis je vous aidez", "Salut bienvenue","bonjour comment puis je vous aidez"] ],
    ["(c'est quoi la BRVM?)",["la BRVM est la bourse regionale commune a 8 pays de l'espace UEMOA"]],
    ["ou se trouve la brvm ?",["Le siège de la BRVM est situé à Abidjan, en Côte d'Ivoire. Avec une representation dans les different pays de l'UEMOA"]],

    ["(Comment investir a la BRVM)", [" Pour investir a la Brvm vous devrez passer par une SGI, la vous pouriez investir soite sur une Action soite sur une Obligation"]],
    ["(C'est quoi une Action?)","Une action représente une part du capital d'une entreprise "],
    ["(C'est quoi une obligation)", "Une obligation "],

    #["(les horaires de cotation), [" la BRVM cote du Lundi au Vendredi de 9h a 15h30"]],
    ["merci",["Je vous en prie !"]],
    ["au revoir",["Au revoir et à bientôt !"]],
    [r"(.*)", ["Désolé, je ne comprends pas votre question."]],

    #["bienvenue, je suis le chatbot de la BRVM et je repond a toutes vos questions! "]
]

chat=Chat(pairs,reflections)
chat.converse()
