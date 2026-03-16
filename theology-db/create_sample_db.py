#!/usr/bin/env python3
"""
Create Sample Theology Database
Includes representative books and authors for immediate use
Users can run full extraction later for complete library
"""

import sqlite3
import os
import base85
import zstandard as zstd

# Sample Bible verses (LSV) - representative selection
SAMPLE_BIBLE = [
    # Genesis (10 sample verses)
    ("Genesis", "OT", 1, 1, "In the beginning, God created the heavens and the earth."),
    ("Genesis", "OT", 1, 2, "And the earth was without form and void, and darkness was over the face of the deep. And the Spirit of God was hovering over the face of the waters."),
    ("Genesis", "OT", 1, 3, "And God says, 'Let light be;' and light is."),
    ("Genesis", "OT", 1, 26, "And God says, 'Let Us make man in Our image, according to Our likeness; and let them rule over the fish of the sea, and over the birds of the heavens, and over the livestock, and over all the earth, and over every creeping thing that is creeping on the earth.'"),
    ("Genesis", "OT", 1, 27, "And God creates the man in His own image; in the image of God He created him; male and female He created them."),
    ("Genesis", "OT", 3, 15, "And I will put enmity between you and the woman, and between your seed and her Seed; He will bruise your head, and you will bruise His heel."),
    ("Genesis", "OT", 12, 1, "And YHWH says to Abram, 'Go out from your land, and from your relatives, and from the house of your father, to the land that I show you."),
    ("Genesis", "OT", 12, 2, "And I make you into a great nation, and bless you, and make your name great; and you are a blessing."),
    ("Genesis", "OT", 15, 6, "And he [Abram] believes in YHWH, and He counts it to him [for] righteousness."),
    ("Genesis", "OT", 22, 18, "And all the nations of the earth are blessed in your Seed, because you have listened to My voice.'"),
    
    # Exodus (5 sample verses)
    ("Exodus", "OT", 3, 14, "And God says to Moses, 'I AM THAT WHICH I AM;' and He says, 'Thus you say to the sons of Israel: I AM has sent me to you.'"),
    ("Exodus", "OT", 20, 1, "And God speaks all these words, saying..."),
    ("Exodus", "OT", 20, 2, "I [am] YHWH your God, who has brought you out of the land of Egypt, out of a house of servants."),
    ("Exodus", "OT", 20, 3, "You have no other gods before Me."),
    ("Exodus", "OT", 20, 7, "You do not take the Name of YHWH your God in vain, for YHWH does not acquit him who takes His Name in vain."),
    
    # Psalms (10 sample verses)
    ("Psalms", "OT", 1, 1, "Blessed [is] the man who has not walked in the counsel of the wicked, and has not stood in the way of sinners, and has not sat in the seat of scorners."),
    ("Psalms", "OT", 1, 2, "But his delight [is] only in the Law of YHWH, and he meditates in His Law day and night."),
    ("Psalms", "OT", 23, 1, "YHWH [is] my shepherd; I do not lack."),
    ("Psalms", "OT", 23, 4, "Indeed, though I walk in the valley of the shadow of death, I fear no evil, for You [are] with me; Your rod and Your staff—they comfort me."),
    ("Psalms", "OT", 51, 1, "Favor me, O God, according to Your kindness; according to the abundance of Your mercies, blot out my transgressions."),
    ("Psalms", "OT", 51, 10, "Create a clean heart for me, O God, and renew a steadfast spirit within me."),
    ("Psalms", "OT", 110, 1, "A declaration of YHWH to my Lord: 'Sit at My right hand, until I make Your enemies Your footstool.'"),
    ("Psalms", "OT", 119, 105, "Your word [is] a lamp before my feet and a light to my path."),
    ("Psalms", "OT", 139, 23, "Search me, O God, and know my heart; try me, and know my thoughts."),
    ("Psalms", "OT", 139, 24, "And see if a grievous way [is] in me, and lead me in the way continuous!"),
    
    # Isaiah (5 sample verses - Messianic prophecies)
    ("Isaiah", "OT", 7, 14, "Therefore the Lord Himself gives a sign to you: Behold, the virgin is conceiving and bearing a son, and calls his name Immanuel."),
    ("Isaiah", "OT", 9, 6, "For a Child has been born to us; a Son has been given to us; and the government is upon His shoulder; and His name is called Wonderful, Counselor, Mighty God, Father of Continuity, Prince of Peace."),
    ("Isaiah", "OT", 40, 3, "A voice is crying in the wilderness: Prepare the way of YHWH; make straight a highway in the desert for our God."),
    ("Isaiah", "OT", 53, 5, "And he is pierced for our transgressions; he is crushed for our iniquities; the discipline of our peace [is] upon him; and by his stripes healing is given to us."),
    ("Isaiah", "OT", 53, 6, "All of us, like sheep, have wandered; we have each turned to his own way; and YHWH has laid upon him the iniquity of all of us."),
    
    # Matthew (10 sample verses)
    ("Matthew", "NT", 1, 21, "And she will bear a son, and you will call his name Jesus, for he will save his people from their sins."),
    ("Matthew", "NT", 1, 23, "'Behold, the virgin will conceive and will bear a son, and they will call his name Emmanuel,' which is, being interpreted, 'God with us.'"),
    ("Matthew", "NT", 5, 3, "Blessed [are] the poor in spirit—because theirs is the kingdom of the heavens."),
    ("Matthew", "NT", 5, 4, "Blessed [are] those who mourn—because they will be comforted."),
    ("Matthew", "NT", 5, 5, "Blessed [are] the meek—because they will inherit the earth."),
    ("Matthew", "NT", 6, 9, "Therefore pray in this way: 'Our Father who is in the heavens; let Your Name be hallowed;"),
    ("Matthew", "NT", 6, 10, "let Your kingdom come; let Your will be done, as in heaven [so] also on the earth."),
    ("Matthew", "NT", 11, 28, "Come to Me, all you laboring and burdened ones, and I will give you rest."),
    ("Matthew", "NT", 11, 29, "Take up My yoke upon you, and learn from Me, because I am meek and humble in heart, and you will find rest for your souls;"),
    ("Matthew", "NT", 11, 30, "for My yoke [is] easy, and My burden is light."),
    
    # John (10 sample verses)
    ("John", "NT", 1, 1, "In [the] beginning was the Word, and the Word was with God, and the Word was God."),
    ("John", "NT", 1, 14, "And the Word became flesh, and tabernacled among us, and we beheld his glory, glory as of [an] only begotten from [the] Father, full of grace and truth."),
    ("John", "NT", 3, 16, "For God loved the world so much that He gave [His] only begotten Son, that everyone who believes in Him should not perish, but may have continuous life."),
    ("John", "NT", 3, 17, "For God did not send His Son into the world that He might judge the world, but that the world might be saved through Him."),
    ("John", "NT", 8, 12, "Again, therefore, Jesus spoke to them, saying, 'I am the light of the world; he who follows Me will not walk in the darkness, but will have the light of life.'"),
    ("John", "NT", 10, 9, "I am the door; through Me if anyone may enter, he will be saved, and will go in and out, and will find pasture."),
    ("John", "NT", 10, 11, "I am the good shepherd; the good shepherd lays down his life for the sheep."),
    ("John", "NT", 14, 6, "Jesus says to him, 'I am the way, and the truth, and the life; no one comes to the Father, except through Me.'"),
    ("John", "NT", 14, 27, "Peace I leave to you; My peace I give to you; not as the world gives do I give to you. Let not your heart be troubled, nor let it fear."),
    ("John", "NT", 15, 13, "Greater love has no one than this, that someone should lay down his life for his friends."),
    
    # Romans (10 sample verses)
    ("Romans", "NT", 1, 16, "For I am not ashamed of the gospel, for it is [the] power of God for salvation to everyone who believes, to Jew first, and also to Greek;"),
    ("Romans", "NT", 1, 17, "for the righteousness of God in it is revealed from faith to faith, according as it has been written: 'But the righteous will live by faith.'"),
    ("Romans", "NT", 3, 23, "For all have sinned and fall short of the glory of God—"),
    ("Romans", "NT", 3, 24, "being justified freely by His grace through the redemption that [is] in Christ Jesus."),
    ("Romans", "NT", 5, 8, "But God demonstrates His own love toward us, in that while we were still sinners, Christ died for us."),
    ("Romans", "NT", 6, 23, "For the wages of sin [is] death, but the free gift of God [is] continuous life in Christ Jesus our Lord."),
    ("Romans", "NT", 8, 1, "[There is] therefore now no condemnation to [those] in Christ Jesus."),
    ("Romans", "NT", 8, 28, "And we have known that to those loving God all things work together for good, to those who are called according to purpose;"),
    ("Romans", "NT", 10, 9, "Because if you confess with your mouth [that] Jesus [is] Lord, and believe in your heart that God raised Him out of [the] dead, you will be saved;"),
    ("Romans", "NT", 10, 10, "for with [the] heart [one] believes for righteousness, and with [the] mouth [one] confesses for salvation."),
    
    # 1 Corinthians (5 sample verses)
    ("1 Corinthians", "NT", 1, 18, "For the word of the cross is foolishness to those who are perishing, but to us who are being saved it is [the] power of God."),
    ("1 Corinthians", "NT", 13, 4, "Love is patient, love is kind, [it] does not envy, [it] does not boast, [it] is not puffed up,"),
    ("1 Corinthians", "NT", 13, 5, "[it] does not behave indecently, [it] does not seek its own, [it] is not easily provoked, [it] does not reckon evil;"),
    ("1 Corinthians", "NT", 13, 13, "And now there remain faith, hope, love—these three; and the greatest of these [is] love."),
    ("1 Corinthians", "NT", 15, 3, "For I delivered to you first, what I also received: that Christ died for our sins, according to the Scriptures;"),
    ("1 Corinthians", "NT", 15, 4, "and that He was buried, and that He has been raised on the third day, according to the Scriptures;"),
    
    # Revelation (5 sample verses)
    ("Revelation", "NT", 1, 8, "I am the Alpha and the Omega, Beginning and Ending, says the Lord, who is, and who was, and who is coming—the Almighty."),
    ("Revelation", "NT", 3, 20, "Behold, I have stood at the door, and I knock; if anyone may hear My voice and may open the door, I will come in to him, and will dine with him, and he with Me."),
    ("Revelation", "NT", 21, 4, "And God will wipe away every tear from their eyes; and death will be no more, nor mourning, nor crying, nor pain will be anymore, because the first things have gone away."),
    ("Revelation", "NT", 21, 6, "And He said to me, 'It has been done! I am the Alpha and the Omega, the Beginning and the End; I will give freely to him who is thirsty from the fountain of the water of life.'"),
    ("Revelation", "NT", 22, 20, "He who is testifying these things says, 'Yes, I come quickly!' Amen. Come, Lord Jesus!"),
]

# Sample Church Fathers texts
SAMPLE_FATHERS = [
    # Clement of Rome
    ("Clement of Rome", "First Epistle to the Corinthians", "Volume 1", 1, 
     "The Church of God which sojourns in Rome to the Church of God which sojourns in Corinth, to those who are called and sanctified by the will of God through our Lord Jesus Christ."),
    ("Clement of Rome", "First Epistle to the Corinthians", "Volume 1", 2,
     "May grace and peace be multiplied to you from God Almighty through Jesus Christ."),
    
    # Ignatius of Antioch
    ("Ignatius of Antioch", "Epistle to the Ephesians", "Volume 1", 1,
     "Ignatius, who is also called Theophorus, to the Church which is at Ephesus, in Asia, deservedly most happy, being blessed in the greatness and fullness of God the Father."),
    ("Ignatius of Antioch", "Epistle to the Romans", "Volume 1", 1,
     "Ignatius, who is also called Theophorus, to the Church which has obtained mercy, through the majesty of the Most High Father, and Jesus Christ, His only-begotten Son."),
    
    # Polycarp
    ("Polycarp", "Epistle to the Philippians", "Volume 1", 1,
     "Polycarp, and the presbyters with him, to the Church of God sojourning at Philippi."),
    
    # Irenaeus
    ("Irenaeus", "Against Heresies", "Volume 1", 1,
     "Inasmuch as certain men have set the truth aside, and bring in lying words and vain genealogies, which, as the apostle says, minister questions rather than godly edifying in the faith."),
    ("Irenaeus", "Against Heresies", "Volume 1", 2,
     "For the Lord of all gave to His apostles the power of the Gospel, through whom also we have known the truth, that is, the doctrine of the Son of God."),
    
    # Justin Martyr
    ("Justin Martyr", "First Apology", "Volume 1", 1,
     "To the Emperor Titus Aelius Adrianus Antoninus Pius Augustus Caesar, and to his son Verissimus the Philosopher, and to Lucius the Philosopher, the natural son of Caesar."),
    ("Justin Martyr", "First Apology", "Volume 1", 5,
     "But lest we should seem to be dealing unfairly, we demand that the charges against the Christians be investigated, and that, if they are proved to be doing anything that is wrong, they may be punished as their wrong-doing deserves."),
    
    # Athanasius
    ("Athanasius", "On the Incarnation", "Volume 4", 1,
     "In our former book we dealt fully enough with a few of the chief points about the heathen worship of idols, and how those false gods originally came to be so regarded."),
    ("Athanasius", "On the Incarnation", "Volume 4", 54,
     "For He was made man that we might be made God; and He manifested Himself by a body that we might receive the idea of the unseen Father."),
    
    # Chrysostom
    ("Chrysostom", "Homilies on the Gospel of John", "Volume 14", 1,
     "In the beginning was the Word, and the Word was with God. Why, tell me, does he speak of the Word, and not of the Son? Because for the present he wishes to show that He was from the beginning."),
    ("Chrysostom", "Homilies on the Statues", "Volume 9", 1,
     "Once again I address myself to you, and with more confidence than before, as I have by your zeal and earnestness, and our common triumph, been so completely relieved from my former apprehensions."),
    
    # Augustine
    ("Augustine", "Confessions", "Volume 1", 1,
     "Great are You, O Lord, and greatly to be praised; great is Your power, and of Your wisdom there is no end. And man, being a part of Your creation, desires to praise You."),
    ("Augustine", "Confessions", "Volume 1", 2,
     "For You have made us for Yourself, and our heart is restless, until it rests in You."),
    ("Augustine", "City of God", "Volume 2", 1,
     "The glorious city of God is my theme in this work, which you, my dearest son Marcellinus, suggested, and which is due to you by my promise."),
    ("Augustine", "On Christian Doctrine", "Volume 2", 1,
     "There are two things on which all interpretation of Scripture depends: the mode of ascertaining the proper meaning, and the mode of making known the meaning when it is ascertained."),
    ("Augustine", "Homilies on Psalm 119", "Volume 8", 1,
     "Blessed are the undefiled in the way, who walk in the law of the Lord. It is the voice of the saints, who are not so called in a carnal sense, but in a spiritual."),
    
    # Jerome
    ("Jerome", "Letter to Eustochium", "Volume 6", 1,
     "I have been asked to undertake the education of a maiden vowed to Christ, and to instruct her mind in the rudiments of the Christian teaching."),
    ("Jerome", "Against Vigilantius", "Volume 6", 1,
     "Vigilantius has set the whole world crying after me, and has made my name detestable as one who is a heretic and a traitor to my faith."),
    
    # Ambrose
    ("Ambrose", "On the Mysteries", "Volume 10", 1,
     "Having discussed the general doctrine as to the washing of water, we must now speak of the Mysteries, and set forth the reasons and proofs of the things which you have received."),
    ("Ambrose", "On the Holy Spirit", "Volume 10", 1,
     "The Holy Spirit is not a weakling, but is the power of God; for the Holy Spirit is the Spirit of God."),
    
    # Basil the Great
    ("Basil the Great", "On the Holy Spirit", "Volume 8", 1,
     "The question asked is not one of those on which we venture to speak without risk, nor yet, on the other hand, are we so afraid as to be hindered from investigating it."),
    
    # Gregory of Nazianzus
    ("Gregory of Nazianzus", "Theological Orations", "Volume 7", 1,
     "The question has often been raised, and is a subject of constant discussion even now in our own day, whether the terms of the Faith ought to be determined according to Scriptural usage."),
    
    # Leo the Great
    ("Leo the Great", "Sermons", "Volume 12", 1,
     "In this sermon, dearly-beloved, which has to be preached with all the earnestness I possess, I will address myself particularly to the catechumens and the faithful."),
    ("Leo the Great", "Letter to Flavian", "Volume 12", 1,
     "Having read your letter, beloved, at the late arrival of which we are surprised, and having perused the detailed account of the Eutyches case."),
    
    # Gregory the Great
    ("Gregory the Great", "Pastoral Rule", "Volume 12", 1,
     "In the beginning of my conversation with you, dearly beloved, I said that I was not acquainted with the sacred canons, and that my life was not such as to give me authority for teaching others."),
    
    # Cyril of Jerusalem
    ("Cyril of Jerusalem", "Catechetical Lectures", "Volume 7", 1,
     "As a charge has been given me by the Right Reverend and most holy Meletius, to address to you, my brethren, certain short statements concerning the matter of baptism."),
    
    # Cyprian
    ("Cyprian", "On the Unity of the Church", "Volume 5", 1,
     "The Lord says, 'I and the Father are one;' and again it is written of the Father, and of the Son, and of the Holy Spirit, 'And these three are one.'"),
    
    # Origen
    ("Origen", "De Principiis", "Volume 4", 1,
     "All who believe and are assured that grace and truth were obtained through Jesus Christ, and who know Christ to be the truth."),
]

def create_database(db_path: str):
    """Create and populate the theology database with sample texts."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bible_verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            testament TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS church_fathers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            work TEXT NOT NULL,
            volume TEXT,
            section INTEGER NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bible_book ON bible_verses(book)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bible_ref ON bible_verses(book, chapter, verse)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fathers_author ON church_fathers(author)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_fathers_work ON church_fathers(work)')
    
    # Clear existing data
    cursor.execute("DELETE FROM bible_verses")
    cursor.execute("DELETE FROM church_fathers")
    
    # Insert Bible verses
    print("Inserting sample Bible verses...")
    cursor.executemany('''
        INSERT INTO bible_verses (book, testament, chapter, verse, content)
        VALUES (?, ?, ?, ?, ?)
    ''', SAMPLE_BIBLE)
    
    # Insert Fathers texts
    print("Inserting sample Church Fathers texts...")
    cursor.executemany('''
        INSERT INTO church_fathers (author, work, volume, section, content)
        VALUES (?, ?, ?, ?, ?)
    ''', SAMPLE_FATHERS)
    
    conn.commit()
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM bible_verses")
    bible_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM church_fathers")
    fathers_count = cursor.fetchone()[0]
    
    print(f"\n✓ Database created: {db_path}")
    print(f"  Bible verses: {bible_count}")
    print(f"  Fathers sections: {fathers_count}")
    print(f"\n  Note: This is a SAMPLE database for immediate use.")
    print(f"  Run parse_lsv_bible_full.py and parse_fathers_full.py")
    print(f"  with your source texts to populate the complete library.")
    
    conn.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = '/home/workspace/arch-christian-rice/theology-db/theology.db'
    
    create_database(db_path)
