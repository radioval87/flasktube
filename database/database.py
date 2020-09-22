import os
import sqlite3

from models.models import Comment, Post, User

DB_PATH = './database/data.db'

def init_db():
    if os.path.isfile(DB_PATH) and os.path.getsize(DB_PATH) > 100:
        with open(DB_PATH, 'r', encoding="ISO-8859-1") as f:
            header = f.read(100)
            if header.startswith('SQLite format 3'):
                print("SQLite3 database has been detected.")
    else:
        conn = sqlite3.connect(DB_PATH)

        sql_create_users_table = '''
            CREATE TABLE IF NOT EXISTS users
                    (id             VARCHAR(36)    NOT NULL     PRIMARY KEY,
                    fname           VARCHAR(50)    NOT NULL,
                    lname           VARCHAR(50)    NOT NULL,
                    nickname        VARCHAR(50)    NOT NULL     UNIQUE,
                    gender          VARCHAR(10)    NOT NULL,
                    password_hash   VARCHAR(100)   NOT NULL,
                    email           VARCHAR(100)   NOT NULL     UNIQUE);
        '''

        sql_create_posts_table = '''
            CREATE TABLE IF NOT EXISTS posts
                    (post_id        VARCHAR(36)    NOT NULL   PRIMARY KEY,
                    post_text       VARCHAR(150)   NOT NULL,
                    post_date       DATETIME       NOT NULL,
                    author_id       VARCHAR(36)    NOT NULL,
                    author_nickname VARCHAR(50)    NOT NULL,
                    FOREIGN KEY(author_id) REFERENCES users(id) ON DELETE   CASCADE,
                    FOREIGN KEY(author_nickname) REFERENCES users(nickname) ON DELETE   CASCADE);
        '''

        sql_create_comments_table = '''
            CREATE TABLE IF NOT EXISTS comments
                    (post_id        VARCHAR(36)    NOT NULL,
                    comment_text    VARCHAR(150)   NOT NULL,
                    comment_date    DATETIME       NOT NULL,
                    author_id       VARCHAR(36)    NOT NULL,
                    author_nickname VARCHAR(50)    NOT NULL,
                    comment_id      VARCHAR(36)    NOT NULL     PRIMARY KEY,  
                    FOREIGN KEY(author_id) REFERENCES users(id) ON DELETE   CASCADE,
                    FOREIGN KEY(author_nickname) REFERENCES users(nickname) ON DELETE   CASCADE,
                    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE   CASCADE );
        '''

        sql_create_follow_table = '''
            CREATE TABLE IF NOT EXISTS followed
                    (id             VARCHAR(36)    NOT NULL,
                    followed_id     VARCHAR(36)    NOT NULL, 
                    FOREIGN KEY(id) REFERENCES users(id) ON DELETE   CASCADE,
                    FOREIGN KEY(followed_id) REFERENCES users(id) ON DELETE   CASCADE);
        '''

        sql_create_likes_table = '''
            CREATE TABLE IF NOT EXISTS likes
                    (post_id        VARCHAR(36)    NOT NULL,
                    like_date       DATETIME       NOT NULL,
                    user_id         VARCHAR(36)    NOT NULL,
                    user_nickname   VARCHAR(50)    NOT NULL,
                    FOREIGN KEY(post_id) REFERENCES posts(post_id) ON DELETE   CASCADE,
                    FOREIGN KEY(user_nickname) REFERENCES users(nickname) ON DELETE   CASCADE,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE   CASCADE);
        '''

        admin_username = 'admin@admin.com'
        admin_password = 'admin'
        admin = User('1', 'admin', 'admin', 'admin', 'admin', '', '')
        admin.set_password(admin_password)
        admin.set_email(admin_username)
        c = conn.cursor()
        c.execute(sql_create_users_table)
        c.execute(sql_create_posts_table)
        c.execute(sql_create_comments_table)
        c.execute(sql_create_follow_table)
        c.execute(sql_create_likes_table)
        create_user(admin)
        conn.close()
        print('Database has been created')

def add_comment(new_comment):
    comment = (new_comment.post_id, new_comment.comment_text,
               new_comment.comment_date, new_comment.author_id,
               new_comment.author_nickname, new_comment.comment_id)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO 
            comments 
        VALUES 
            (?, ?, ?, ?, ?, ?)
    """, comment)
    conn.commit()
    conn.close()

def add_followed(id_, followed_id):
    ids = (id_, followed_id)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO 
            followed 
        VALUES 
            (?, ?)
    """, ids)
    conn.commit()
    conn.close()

def add_like(new_like):
    new_like = (new_like[0], new_like[1], new_like[2], new_like[3])
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO 
            likes 
        VALUES 
            (?, ?, ?, ?)
    """, new_like)
    conn.commit()
    conn.close()

def add_post(new_post):
    post = (new_post.post_id, new_post.post_text,
            new_post.post_date, new_post.author_id, new_post.author_nickname)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO 
            posts 
        VALUES 
            (?, ?, ?, ?, ?)
    """, post)
    conn.commit()
    conn.close()

def create_user(new_user):
    user = (new_user.id, new_user.fname, new_user.lname, new_user.nickname,
            new_user.gender, new_user.password_hash, new_user.email)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        INSERT INTO 
            users 
        VALUES 
            (?, ?, ?, ?, ?, ?, ?)
    """, user)
    conn.commit()
    conn.close()

def delete_followed(id_, followed_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    delete_query = '''
        DELETE FROM 
            followed 
        WHERE id = ? AND followed_id = ?
        '''
    conn.execute("PRAGMA foreign_keys = 1")
    cursor.execute(delete_query, (id_, followed_id, ))
    conn.commit()
    conn.close()

def delete_like(post_id, user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    delete_query = '''
        DELETE FROM 
            likes 
        WHERE post_id = ? AND user_id = ?
        '''
    conn.execute("PRAGMA foreign_keys = 1")
    cursor.execute(delete_query, (post_id, user_id, ))
    conn.commit()
    conn.close()

def delete_post(post_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    delete_query = '''
        DELETE FROM 
            posts 
        WHERE post_id = ?
        '''
    conn.execute("PRAGMA foreign_keys = 1")
    cursor.execute(delete_query, (post_id, ))
    conn.commit()
    conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    delete_query = """
        DELETE FROM 
            users 
        WHERE 
            id = ?
    """
    try:
        cursor.execute(delete_query, (user_id, ))
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        conn.close()

def fetch_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT 
            * 
        FROM 
            users
    """)
    users_reversed = cursor.fetchall()
    users_iter = reversed(users_reversed)
    users = [User(u[0], u[1], u[2], u[3], u[4], u[5], u[6]) for
             u in users_iter]
    conn.close()
    return users

def get_all_likes_by_posts_ids(posts):
    posts_ids = [post.post_id for post in posts]
    all_likes = {post_id:get_liked_users(post_id) for
                 post_id in posts_ids}
    return all_likes

def get_all_number_of_likes_by_posts_ids(posts):
    posts_ids = [post.post_id for post in posts]
    all_NoL = {post_id:get_number_of_likes(post_id) for
               post_id in posts_ids}
    return all_NoL

def get_all_followed_ids_by_id(id_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            followed_id 
        FROM 
            followed 
        WHERE 
            id = ?
    """
    cursor.execute(select_query, (id_, ))
    results = cursor.fetchall()
    followed_ids = [result[0] for result in results]
    conn.close()
    return followed_ids

def get_all_followed_by_id(id_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            users 
        WHERE 
            id IN 
            (SELECT 
                followed_id 
            FROM 
                followed 
            WHERE 
                id = ?
            ) 
        ORDER BY 
            nickname
    """
    cursor.execute(select_query, (id_, ))
    results = cursor.fetchall()
    users = [User(u[0], u[1], u[2], u[3], u[4], u[5], u[6]) for u in results]
    conn.close()
    return users

def get_all_followed_by_nickname(nickname):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            users 
        WHERE 
            id IN 
            (SELECT 
                followed_id 
            FROM 
                followed 
            WHERE 
                id = 
                (SELECT 
                    id
                FROM
                    users
                WHERE
                    nickname = ?    
                )
            )
        ORDER BY 
            nickname
    """
    cursor.execute(select_query, (nickname, ))
    results = cursor.fetchall()
    users = [User(u[0], u[1], u[2], u[3], u[4], u[5], u[6]) for u in results]
    conn.close()
    return users

def get_all_followers_by_nickname(nickname):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            users 
        WHERE 
            id IN 
            (SELECT 
                id 
            FROM 
                followed 
            WHERE 
                followed_id = 
                (SELECT 
                    id
                FROM
                    users
                WHERE
                    nickname = ?    
                )
            )
        ORDER BY 
            nickname
    """
    cursor.execute(select_query, (nickname, ))
    results = cursor.fetchall()
    users = [User(u[0], u[1], u[2], u[3], u[4], u[5], u[6]) for u in results]
    conn.close()
    return users

def get_all_comments_by_posts_ids(posts):
    posts_ids = [post.post_id for post in posts]
    all_comments = {post_id:get_all_comments_by_post_id(post_id) for
                    post_id in posts_ids}
    return all_comments

def get_all_comments_by_post_id(post_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            comments 
        WHERE 
            post_id = ?
        ORDER BY 
            comment_date DESC;
    """
    cursor.execute(select_query, (post_id, ))
    selected_comments = cursor.fetchall()
    comments = [Comment(c[0], c[1], c[2], c[3], c[4], c[5]) for
                c in selected_comments]
    conn.close()
    return comments

def get_liked_users(post_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            user_nickname
        FROM 
            likes 
        WHERE 
            post_id = ?
        ORDER BY 
            like_date DESC;
    """
    cursor.execute(select_query, (post_id, ))
    results = cursor.fetchall()
    liked_users = [result[0] for result in results]
    conn.close()
    return liked_users

def get_number_of_likes(post_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            COUNT (post_id) AS Number_of_likes 
        FROM 
            likes 
        WHERE 
            post_id = ?
    """
    cursor.execute(select_query, (post_id, ))
    results = cursor.fetchall()
    number_of_likes = [result[0] for result in results]
    conn.close()
    return number_of_likes

def get_news_by_nickname(nickname):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = 1")
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            posts 
        WHERE 
            author_id IN
            (SELECT
                followed_id
            FROM
                followed
            WHERE 
                id = 
                    (SELECT 
                        id
                    FROM
                        users
                    WHERE
                        nickname = ?    
                    )
            )
        ORDER BY 
            post_date DESC;
    """
    cursor.execute(select_query, (nickname, ))
    selected_posts = cursor.fetchall()
    posts = [Post(p[0], p[1], p[2], p[3], p[4]) for p in selected_posts]
    conn.close()
    return posts

def get_all_posts_by_author_id(id_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            posts 
        WHERE 
            author_id = ?
        ORDER BY 
            post_date DESC;
    """
    cursor.execute(select_query, (id_, ))
    selected_posts = cursor.fetchall()
    posts = [Post(p[0], p[1], p[2], p[3], p[4]) for p in selected_posts]
    conn.close()
    return posts

def get_post_by_post_id(post_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            posts 
        WHERE 
            post_id = ?
    """
    cursor.execute(select_query, (post_id, ))
    selected_post = cursor.fetchone()
    post = Post(selected_post[0], selected_post[1],
                selected_post[2], selected_post[3], selected_post[4])
    conn.close()
    return post

def get_user_by_id(id_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            users 
        WHERE 
            id = ?
    """
    cursor.execute(select_query, (id_, ))
    selected_user = cursor.fetchone()
    user = User(selected_user[0], selected_user[1], selected_user[2],
                selected_user[3], selected_user[4],
                selected_user[5], selected_user[6])
    conn.close()
    return user

def get_user_by_email(email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            users 
        WHERE 
            email = ?
    """
    try:
        cursor.execute(select_query, (email, ))
        selected_user = cursor.fetchone()
        user = User(selected_user[0], selected_user[1], selected_user[2],
                    selected_user[3], selected_user[4], selected_user[5],
                    selected_user[6])
        return user
    except TypeError as e:
        print(e)
    finally:
        conn.close()

def get_user_by_nickname(nickname):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    select_query = """
        SELECT 
            * 
        FROM 
            users 
        WHERE 
            nickname = ?
    """
    cursor.execute(select_query, (nickname, ))
    selected_user = cursor.fetchone()
    user = User(selected_user[0], selected_user[1], selected_user[2],
                selected_user[3], selected_user[4], selected_user[5],
                selected_user[6])
    conn.close()
    return user

def update_user(updated_user):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    update_query = """
        UPDATE 
            users 
        SET 
            fname=?, lname=?, nickname=?, gender=? 
        WHERE 
            id = ?
    """
    user_data = (updated_user.fname, updated_user.lname, updated_user.nickname,
                 updated_user.gender, updated_user.id)
    cursor.execute(update_query, user_data)
    conn.commit()
    conn.close()
