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

category1 = Category(name='Science-Fiction', user_id=1)
session.add(category1)
session.commit()

category2 = Category(name='Thriller', user_id=1)
session.add(category2)
session.commit()

category3 = Category(name='Health and Fitness', user_id=1)
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
    img='',
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
    img='',
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
    img='',
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
    img='',
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
    img='',
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
    img='',
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
    img='',
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
    img='',
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
    img='',
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
    img='',
    user_id=1
)

session.add(book10)
session.commit()

thriller_book1 = Book(
    title='The Snowman',
    author='Jo Nesbo',
    description="""Read the latest book in the Harry Hole detective series.""",
    category=category2,
    img='',
    user_id=1
)

session.add(thriller_book1)
session.commit()

thriller_book2 = Book(
    title='The Girl With The Dragon Tattoo',
    author='Steig Larsson',
    description='',
    category=category2,
    img='',
    user_id=1
)

session.add(thriller_book2)
session.commit()

health_book1 = Book(
    title='Gut',
    author='Giulia Enders',
    description='',
    category=category3,
    img='',
    user_id=1
)

session.add(health_book1)
session.commit()

health_book2 = Book(
    title='LL Cool J\'s Platinum Workout',
    author='LL Cool J',
    description='',
    category=category3,
    img='',
    user_id=1
)

session.add(health_book2)
session.commit()

print('that was fun')
