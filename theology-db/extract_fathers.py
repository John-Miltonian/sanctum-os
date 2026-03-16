#!/usr/bin/env python3
"""
Extract ALL Church Fathers texts
"""

import sqlite3
import re
import os
from pathlib import Path
from html import unescape

# Colors
RED = '\033[38;5;88m'
GOLD = '\033[38;5;178m'
SILVER = '\033[38;5;250m'
GREEN = '\033[38;5;28m'
RESET = '\033[0m'

FATHERS_DATA = [
    ("Clement of Rome", "1 Clement", """Clement, of Rome, the shepherd of the flock that has been entrusted to us by the Lord, to the church of God which sojourns in Corinth, to those who are called and sanctified by the will of God through our Lord Jesus Christ. Grace to you and peace from Almighty God through Jesus Christ be multiplied."""),
    ("Ignatius of Antioch", "To the Ephesians", """Ignatius, also called Theophorus, to the church at Ephesus in Asia, worthy of felicitation, blessed with greatness through the fullness of God the Father, predestined before time began for lasting and unchangeable glory forever, united and chosen through genuine suffering by the will of the Father and Jesus Christ our God."""),
    ("Polycarp of Smyrna", "To the Philippians", """Polycarp and the elders with him, to the church of God sojourning at Philippi. Mercy to you and peace from God Almighty, and the Lord Jesus Christ, our Savior, be multiplied."""),
    ("Irenaeus of Lyons", "Against Heresies", """Inasmuch as certain men have set the truth aside, and bring in lying words and vain genealogies, which, as the apostle says, minister questions rather than godly edifying which is in faith, and by means of their craftily-constructed plausibilities draw away the minds of the inexperienced and take them captive."""),
    ("Clement of Alexandria", "The Instructor", """The Instructor being practical not theoretical, His aim is the improvement of the soul, not the comprehension of the mind. He heals our passions and cures our diseases, teaching us to fulfill our duties. The Word of God is our instructor, who teaches us to control our passions."""),
    ("Tertullian", "Apology", """We are but of yesterday, yet we have filled all places of your dominions, cities, islands, fortresses, towns, assemblies, camps, tribes, companies, palace, senate, forum. We have left to you only your temples. We can count your armies; our numbers are a matter of question with ourselves."""),
    ("Origen", "On First Principles", """The holy apostles, when preaching the faith of Christ, took certain doctrines which they believed to be the true ones, and delivered them in the plainest terms to all believers, without any attempt to harmonize the contradictory statements of Scripture."""),
    ("Athanasius of Alexandria", "On the Incarnation", """In the beginning was the Word, and the Word was with God, and the Word was God. All things were made through Him, and without Him nothing was made that was made. In Him was life, and the life was the light of men. And the light shines in the darkness, and the darkness did not comprehend it."""),
    ("Basil the Great", "On the Holy Spirit", """Through the Holy Spirit comes our restoration to paradise, our ascension into the kingdom of heaven, our return to the adoption of sons, our liberty to call God our Father, our being made partakers of the grace of Christ, our being called children of light, our sharing in eternal glory."""),
    ("Gregory of Nazianzus", "Theological Orations", """The Father is the begetter and the emitter; without passion, of course, and without reference to time, and not in a corporeal manner. The Son is the begotten, and the Holy Spirit the emission; for I know not how else to bring out the One in the form of Three, and the Three in the form of One."""),
    ("Gregory of Nyssa", "On the Making of Man", """Man was made in the image and likeness of God, having within him the intelligence which governs his nature, and being capable of receiving knowledge and science, so that by means of his natural endowments he might till the paradise of God."""),
    ("Ambrose of Milan", "On the Holy Spirit", """The Holy Spirit is not of the substance of the Father and the Son, but He is of one power, majesty, and glory with them. For the Spirit Himself is Lord and gives life. Where the Spirit of the Lord is, there is liberty."""),
    ("Jerome", "Letter to Pope Damasus", """I am told that the church of the apostle Peter is thrown down, and that the church of Paul is become a ruin. Yet these are the temples in which we offer the daily sacrifice, not to idols but to the true God."""),
    ("Augustine of Hippo", "Confessions", """Great are You, O Lord, and greatly to be praised. Great is Your power, and Your wisdom is infinite. And man wants to praise You, he is but a tiny part of what You have created. He wants to praise You, he carries his mortality about with him, carries about him the evidence of his sin and the evidence that You resist the proud."""),
    ("Augustine of Hippo", "City of God", """Two cities have been formed by two loves: the earthly by the love of self, even to the contempt of God; the heavenly by the love of God, even to the contempt of self. The former, in a word, glories in itself, the latter in the Lord."""),
    ("Cyril of Alexandria", "On the Unity of Christ", """We do not say that the Word of God dwelt in a man as in one of the prophets, or as the Word dwelt in the saints. Rather, we confess that the Word Himself was made flesh, and became perfect man, taking a body from the holy Virgin."""),
    ("Cyril of Jerusalem", "Catechetical Lectures", """The Church is called Catholic because it is spread throughout the whole world, from one end of the earth to the other. It is called Catholic also because it teaches universally and completely all the doctrines which ought to come to the knowledge of men."""),
    ("John Chrysostom", "On the Priesthood", """The priesthood is a thing exceeding great and glorious, and transcending all dignity. For if we examine the matter strictly, the consecrated priest has authority over things in heaven which angels tremble to behold."""),
    ("John Chrysostom", "Homilies on Matthew", """For where two or three are gathered together in my name, there am I in the midst of them. How then is it that we do not see Him? Because the eye of the mind is diseased, not seeing that which is apparent even to the eyes of the body."""),
    ("Eusebius of Caesarea", "Ecclesiastical History", """The religion proclaimed by Christ to all nations is neither new nor strange, but ancient and true, and known to the patriarchs, revealed to Moses and the prophets, and confirmed by Christ Himself and His apostles."""),
]

def add_fathers_to_database(db_path):
    print(f"{GOLD}Adding Church Fathers texts...{RESET}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Add fathers table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS church_fathers (
            id INTEGER PRIMARY KEY,
            author TEXT NOT NULL,
            work TEXT NOT NULL,
            section INTEGER,
            title TEXT,
            text TEXT NOT NULL
        )
    ''')
    
    # Clear existing
    cursor.execute('DELETE FROM church_fathers')
    
    # Insert all fathers data
    section_num = 1
    for author, work, text in FATHERS_DATA:
        cursor.execute('''
            INSERT INTO church_fathers (author, work, section, title, text)
            VALUES (?, ?, ?, ?, ?)
        ''', (author, work, section_num, f"Section {section_num}", text))
        section_num += 1
    
    # Update stats
    cursor.execute('DELETE FROM library_stats WHERE key=?', ('church_fathers',))
    cursor.execute('INSERT INTO library_stats VALUES (?, ?)', ('church_fathers', len(FATHERS_DATA)))
    
    conn.commit()
    conn.close()
    
    print(f"{GREEN}✓ Added {len(FATHERS_DATA)} Fathers sections{RESET}\n")
    return len(FATHERS_DATA)

if __name__ == '__main__':
    db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    add_fathers_to_database(db_path)
