from database_config import User, Category, Book, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# an Engine, which the Session will use for connection
# resources
engine = create_engine('sqlite:///itemcatalog.db')

# Clear the database
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)

# create a configured "Session" class
Session = sessionmaker(bind=engine)

# create a Session
session = Session()

user_admin = User(name='Andy', email='udacity@bestbooks.com', picture='')

session.add(user_admin)
session.commit()

category1 = Category(name='Science-Fiction',
                     description="""Post your favourite science-fiction books
                     here.""",
                     user_id=1)

session.add(category1)
session.commit()

category2 = Category(name='Thriller',
                     description='What makes a good thriller?',
                     user_id=1)

session.add(category2)
session.commit()

category3 = Category(name='Health and Fitness',
                     description='Get ripped now.',
                     user_id=1)

session.add(category3)
session.commit()

book1 = Book(
    title='Dune',
    author='Frank Herbert',
    description="""The sweeping tale of the desert planet Arrakis, the focus
     of an intricate power struggle in a byzantine interstellar empire.
     Arrakis is the sole source of Melange, necessary for interstellar
     travel and also grants psychic powers and longevity, so whoever
     controls it wields great influence.""",
    category_id=1,
    img=('https://upload.wikimedia.org/wikipedia/en/d/de/'
         'Dune-Frank_Herbert_%281965%29_First_edition.jpg'),
    user_id=1
)

session.add(book1)
session.commit()

book2 = Book(
    title='The Forever War',
    author='Joe Haldeman',
    description="""Private William Mandella is a reluctant hero in an
    interstellar war against an unknowable and unconquerable alien enemy, but
    his greatest test will be when he returns home.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/c/cd/'
         'TheForeverWar%281stEd%29.jpg'),
    user_id=1
)

session.add(book2)
session.commit()

book3 = Book(
    title='Neuromancer',
    author='William Gibson',
    description="""The Matrix unfolds like neon origami beneath clusters and
    constellations of data. Constructs, AIs, live here. Somewhere, concealed
    by ice, Neuromancer is evolving. As entropy goes into reverse, Molly\'s
    surgical implants broadcast trouble from the ferro-concrete geodesic of
    the Sprawl. Maelcum, Rastafarian in space, is her best hope of rescue.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/4/4b/Neuromancer'
         '_%28Book%29.jpg'),
    user_id=1
)

session.add(book3)
session.commit()

book4 = Book(
    title='The Demolished Man',
    author='Alfred Bester',
    description="""In 2301 murder is virtually impossible, but one man is
     about to change that... Ben Reich, a psychopathic business magnate, has
     devised the ultimate scheme to eliminate the competition and destroy the
     order of his society.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/f/fd/'
         'The_Demolished_Man_first_edition.jpg'),
    user_id=1
)

session.add(book4)
session.commit()

book5 = Book(
    title='The Dispossessed',
    author='Ursula Le Guin',
    description="""The Principle of Simultaneity is a scientific breakthrough
     which will revolutionize interstellar civilisation by making possible
     instantaneous communication. It is the life work of Shevek, a brilliant
     physicist from the arid anarchist world of Anarres.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/f/fc/The'
         'Dispossed%281stEdHardcover%29.jpg'),
    user_id=1
)

session.add(book5)
session.commit()

book6 = Book(
    title='Gateway',
    author='Frederik Pohl',
    description="""Humans had discovered this artificial spaceport, full of
    working interstellar ships left behind by the mysterious, vanished Heechee.
     Their destinations are preprogrammed. They are easy to operate, but
     impossible to control.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/6/68/GatewayNovel.JPG'),
    user_id=1
)

session.add(book6)
session.commit()

book7 = Book(
    title='The Man In The High Castle',
    author='Philip K Dick',
    description="""Imagine the world if the Allies had lost the Second World
    War - the African continent virtually wiped out, the Mediterranean drained
    to make farmland, the United States divided between the Japanese and the
    Nazis.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/8/87/Man_in_the_High_'
         'Castle_%281st_Edition%29.png'),
    user_id=1
)

session.add(book7)
session.commit()

book8 = Book(
    title='Childhood\'s End',
    author='Arthur C Clarke',
    description="""Earth has become a Utopia, guided by a strange unseen
    people from outer space whose staggering powers have eradicated war,
    cruelty, poverty and racial inequality. When the \'Overlords\' finally
    reveal themselves, their horrific form makes little impression.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/7/72/Childhoods'
         'End%281stEd%29.jpg'),
    user_id=1
)

session.add(book8)
session.commit()

book9 = Book(
    title='Ubik',
    author='Philip K Dick',
    description="""Death, the final frontier, the one inescapable and
    inevitable fact of that we call life, or is it?""",
    category=category1,
    img='https://upload.wikimedia.org/wikipedia/en/a/af/Ubik%281stEd%29.jpg',
    user_id=1
)

session.add(book9)
session.commit()

book10 = Book(
    title='Timescape',
    author='Gregory Benford',
    description="""1962: A young Californian scientist finds his experiments
    spoiled by mysterious interference.""",
    category=category1,
    img=('https://upload.wikimedia.org/wikipedia/en/b/ba/'
         'Timescape%281stEd%29.jpg'),
    user_id=1
)

session.add(book10)
session.commit()

thriller_book1 = Book(
    title='The Snowman',
    author='Jo Nesbo',
    description="""A young boy wakes to find his mother missing. Outside, he
    sees her favourite scarf wrapped around the neck of a snowman.""",
    category=category2,
    img=('https://upload.wikimedia.org/wikipedia/en/5/5b/The_Snowman_%28Nesb%'
         'C3%B8_novel%29.jpg'),
    user_id=1
)

session.add(thriller_book1)
session.commit()

thriller_book2 = Book(
    title='The Girl With The Dragon Tattoo',
    author='Steig Larsson',
    description="""The first book in the Millennium series featuring Lisbeth
    Salander, the global publishing phenomenon""",
    category=category2,
    img=('https://upload.wikimedia.org/wikipedia/en/b/bc/Thegirlwiththed'
         'ragontattoo.jpg'),
    user_id=1
)

session.add(thriller_book2)
session.commit()

health_book1 = Book(
    title='Gut',
    author='Giulia Enders',
    description="""Our gut is almost as important to us as our brain or our
    heart, yet we know very little about how it works. In Gut, Giulia Enders
    shows that rather than the utilitarian and, let's be honest, somewhat
    embarrassing body part we imagine it to be, it is one of the most complex,
    important, and even miraculous parts of our anatomy.""",
    category=category3,
    img=('https://cdn.waterstones.com/bookjackets/large/9781/9113/'
         '9781911344773.jpg'),
    user_id=1
)

session.add(health_book1)
session.commit()

health_book2 = Book(
    title='LL Cool J\'s Platinum Workout',
    author='LL Cool J',
    description="""LL didn't always have a diesel body. He chiselled it the
    old-fashioned way, with hard work and discipline. Here he shares the
    secrets of his transformation in a uniquely creative, yet no-nonsense
    regimen, enlivened with humour and sheer force of personality, that will
    inspire readers to enjoy working out as never before, while building a body
    they never thought possible.""",
    category=category3,
    img=('https://upload.wikimedia.org/wikipedia/commons/1/16/LL_Cool_J.jpg'),
    user_id=1
)

session.add(health_book2)
session.commit()

print('Books added')
