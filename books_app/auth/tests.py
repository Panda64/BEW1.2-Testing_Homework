import os
from unittest import TestCase

from datetime import date
 
from books_app import app, db, bcrypt
from books_app.models import Book, Author, User, Audience

"""
Run these tests with the command:
python -m unittest books_app.main.tests
"""

#################################################
# Setup
#################################################

def create_books():
    a1 = Author(name='Harper Lee')
    b1 = Book(
        title='To Kill a Mockingbird',
        publish_date=date(1960, 7, 11),
        author=a1
    )
    db.session.add(b1)

    a2 = Author(name='Sylvia Plath')
    b2 = Book(title='The Bell Jar', author=a2)
    db.session.add(b2)
    db.session.commit()

def create_user():
    password_hash = bcrypt.generate_password_hash('password').decode('utf-8')
    user = User(username='me1', password=password_hash)
    db.session.add(user)
    db.session.commit()

#################################################
# Tests
#################################################

class AuthTests(TestCase):
    """Tests for authentication (login & signup)."""

    def setUp(self):
        """Executed prior to each test."""
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.drop_all()
        db.create_all()

    def test_signup(self):
        """Test sign up.""" 
        # Make POST request with data
        post_data = {
            'username': 'me2',
            'password': 'testpass',
        }
        self.app.post('/signup', data=post_data)

        # Make sure user was created as we'd expect
        created_user = User.query.filter_by(username='me2').one()
        self.assertIsNotNone(created_user)
        self.assertEqual(created_user.username, 'me2')


    def test_signup_existing_user(self):
        # Set up
        create_user()

        # Make POST request with data
        post_data = {
            'username': 'me1',
            'password': 'password',
        }
        response = self.app.post('/signup', data=post_data)

        # Check that trying to create a user twice results in an error
        response_text = response.get_data(as_text=True)
        self.assertIn('That username is taken. Please choose a different one.', response_text)

    def test_login_correct_password(self):
        # Set up
        create_user()

        # Make POST request with data
        post_data = {
            'username': 'me1',
            'password': 'password',
        }
        self.app.post('/login', data=post_data)

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that "login" button is not displayed on the homepage
        response_text = response.get_data(as_text=True)
        self.assertNotIn('login', response_text)

    def test_login_nonexistent_user(self):
        # Make POST request with data
        post_data = {
            'username': 'me1',
            'password': 'password',
        }
        response = self.app.post('/login', data=post_data)

        # Check that trying to login with a nonexistent user results in an error
        response_text = response.get_data(as_text=True)
        self.assertIn('No user with that username. Please try again.', response_text)

    def test_login_incorrect_password(self):
        # Set up
        create_user()

        # Make POST request with data
        post_data = {
            'username': 'me1',
            'password': 'wrongpassword',
        }
        response = self.app.post('/login', data=post_data)

        # Check that trying to login with an incorrect password results in an error
        response_text = response.get_data(as_text=True)
        self.assertIn('Password doesn&#39;t match. Please try again.', response_text)

    def test_logout(self):
        # Set up
        create_user()

        # Make POST request with data
        post_data = {
            'username': 'me1',
            'password': 'password',
        }
        self.app.post('/login', data=post_data)

        # Make a GET request
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Make a GET request
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Check that the user was succesfully logged out by seeing if the "login" button is displayed on the homepage
        response_text = response.get_data(as_text=True)
        self.assertIn('login', response_text)
