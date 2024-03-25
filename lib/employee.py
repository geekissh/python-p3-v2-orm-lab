from __init__ import CURSOR, CONN
from abc import ABC, abstractmethod
from datetime import datetime

class BaseModel(ABC):

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of instances """
        sql = cls.create_table_sql()
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists instances """
        sql = cls.drop_table_sql()
        CURSOR.execute(sql)
        CONN.commit()

    @abstractmethod
    def save(self):
        """ Save the object to the database """
        pass

    @abstractmethod
    def update(self):
        """ Update the object in the database """
        pass

    @abstractmethod
    def delete(self):
        """ Delete the object from the database """
        pass

    @classmethod
    def create(cls, *args, **kwargs):
        """ Initialize a new instance and save the object to the database """
        instance = cls(*args, **kwargs)
        instance.save()
        return instance

class Review(BaseModel):

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, id, employee_id, year, text):
        self.id = id
        self.employee_id = employee_id
        self.year = year
        self.text = text

    def __repr__(self):
        return f"<Review {self.id}: {self.employee_id}, {self.year}, {self.text}>"

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, year):
        if isinstance(year, int) and 1900 <= year <= datetime.datetime.now().year:
            self._year = year
        else:
            raise ValueError("Year must be a positive integer within 1900-present")

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if isinstance(text, str) and len(text) > 0:
            self._text = text
        else:
            raise ValueError("Review text must be a non-empty string")

    @classmethod
    def create_table_sql(cls):
        """ Return the SQL statement to create the table """
        return """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            employee_id INTEGER,
            year INTEGER,
            text TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """

    @classmethod
    def drop_table_sql(cls):
        """ Return the SQL statement to drop the table """
        return """
            DROP TABLE IF EXISTS reviews;
        """

    def save(self):
        """ Insert a new row with the employee_id, year, and text values of the current Review object.
        Update object id attribute using the primary key value of new row.
        Save the object in local dictionary using table row's PK as dictionary key"""
        sql = """
                INSERT INTO reviews (employee_id, year, text)
                VALUES (?, ?, ?)
        """

        CURSOR.execute(sql, (self.employee_id, self.year, self.text))
        CONN.commit()

        self.id = CURSOR.lastrowid
        type(self).all[self.id] = self

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET employee_id = ?, year = ?, text = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.employee_id, self.year, self.text, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row corresponding to the current Review instance,
        delete the dictionary entry, and reassign id attribute"""

        sql = """
            DELETE FROM reviews
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()

        # Delete the dictionary entry using id as the key
        del type(self).all[self.id]

        # Set the id to None
        self.id = None