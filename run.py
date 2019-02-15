from kitabu import create_app, db


app = create_app()
app.app_context()
#app.app_context().push()
db.init_app(app)
#db.drop_all()
db.create_all()

#This is for importing all the books data in db
#from all_books import main

#main()

if __name__ == "__main__":
    app.run(debug=True)