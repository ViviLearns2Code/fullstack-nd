from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, LearningItem, Resource

engine = create_engine("sqlite:///tolearn.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# CREATE data
# user
#email = "YOUR GOOGLEMAIL ADDRESS HERE"
#name = "YOUR GOOGLE NAME HERE"

me = User(name=name, email=email)
session.add(me)
session.flush()
# category for user
me = session.query(User).filter_by(name=name).one()
js = Category(user_id=me.id, name="JavaScript")
kotlin = Category(user_id=me.id, name="Kotlin")
session.add(kotlin)
session.add(js)
session.flush()
# item for category
nodejs = LearningItem(
    category_id=js.id,
    name="Introduction to Node.js",
    description="Learn the basics of node by completing the blog series")
angularjs = LearningItem(
    category_id=js.id,
    name="Introduction to AngularJS",
    description="Get started with AngularJS")
kotlinbasics = LearningItem(
    category_id=kotlin.id,
    name="Kotlin Basics",
    description="Learn the basics of Kotlin")
kotlinapp = LearningItem(
    category_id=kotlin.id,
    name="Hello world app",
    description="Build a hello world app with Kotlin in Android Studio")

session.add(angularjs)
session.add(nodejs)
session.add(kotlinbasics)
session.add(kotlinapp)
session.flush()

# learning resources for category
goloroden = Resource(
    item_id=nodejs.id,
    name="Introduction to Node.js (German)",
    url=("""https://www.heise.de/developer/artikel/
        Einfuehrung-in-Node-js-Folge-1-Node-js-installieren-3595787.html"""))
session.add(goloroden)
goloroden = Resource(
    item_id=nodejs.id,
    name="Node.js Web Development by David Herron",
    url="")
session.add(goloroden)
session.commit()
